"""
agents/foundry_iq_client.py

Azure AI Foundry IQ client wrapper.

Spec reference: docs/foundry_iq_spec.md §1–3

Responsibilities:
  - Wrap the Azure OpenAI SDK for per-document grounded citation retrieval.
  - Implement the 3-tier fallback chain (docs/reliability_spec.md §1):
      Tier 1: Azure Foundry IQ gpt-4o  (timeout 10s)
      Tier 2: Azure Foundry IQ gpt-4o-mini  (timeout 15s)
      Tier 3: Pre-computed mock responses  (never fails)
  - Return FoundryIQResult with citations, passages, and confidence scores.

Mock data (Tier 3) lives in agents/iq_mock_data.py — not here.
This file is responsible only for the Azure client and parsing logic.

Configuration (from environment variables / .env):
  AZURE_OPENAI_ENDPOINT        — e.g. https://<resource>.openai.azure.com/
  AZURE_OPENAI_API_KEY         — Azure API key
  AZURE_OPENAI_DEPLOYMENT_4O   — deployment name for gpt-4o (Tier 1)
  AZURE_OPENAI_DEPLOYMENT_MINI — deployment name for gpt-4o-mini (Tier 2)
  AZURE_API_VERSION            — e.g. 2025-01-01-preview"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("conflictsense.foundry_iq")

# ─── Config ───────────────────────────────────────────────────────────────────

AZURE_ENDPOINT   = os.getenv("AZURE_FOUNDRY_ENDPOINT", "")
AZURE_API_KEY    = os.getenv("AZURE_API_KEY", "")
DEPLOYMENT_4O    = os.getenv("AZURE_OPENAI_DEPLOYMENT_4O", "gpt-4o")
DEPLOYMENT_MINI  = os.getenv("AZURE_OPENAI_DEPLOYMENT_MINI", "gpt-4o-mini")
API_VERSION      = os.getenv("AZURE_API_VERSION", "2025-01-01-preview")

TIER1_TIMEOUT = 10   # seconds
TIER2_TIMEOUT = 15   # seconds

# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class Citation:
    """One grounded citation from a document, matching PolicyStatement schema."""
    document: str
    section: str
    passage: str
    confidence: float
    topic: str


@dataclass
class FoundryIQResult:
    """
    Result of a Foundry IQ grounded query.
    Mirrors what the real Foundry IQ SDK would return.
    """
    query: str
    document_id: str        # Filename of the source document
    citations: list[Citation]
    is_silent: bool         # True if document has no relevant content on the topic
    tier_used: int          # 1, 2, or 3 (for MOCK_MODE detection)
    raw_response: Optional[str] = None


# ─── System prompt (DocumentAnalyzer — docs/prompt_registry.md §1) ────────────

_SYSTEM_PROMPT = """You are a policy document analyst. You receive the full text of a single enterprise policy document and a query topic. Your task: extract the specific rule or constraint that applies to the given topic.

Return ONLY the exact claim made by this document — do not infer, extrapolate, or summarise. Quote the exact policy text where possible. If the document is silent on the topic, say so explicitly.

You MUST return a JSON object with this exact structure:
{
  "is_silent": boolean,
  "citations": [
    {
      "section": "§X.Y",
      "passage": "exact quoted text from the document",
      "confidence": 0.0 to 1.0
    }
  ]
}

Rules:
- "is_silent" is true only if the document contains no relevant rule on the topic.
- "citations" must contain at least 1 item if is_silent is false.
- "section" must be the actual section identifier from the document (e.g. "§4.2").
- "passage" must be a verbatim quote from the document — never paraphrased.
- "confidence" reflects how directly and unambiguously this passage answers the query (0.0–1.0).
- Do NOT add any text outside the JSON object.
"""

_USER_PROMPT_TEMPLATE = """Document: {document_name}

Topic: {topic}

Document content:
---
{document_text}
---

Return the JSON extraction as specified."""

# ─── Mock responses (Tier 3) ─────────────────────────────────────────────────
# Mock data lives in agents/iq_mock_data.py (single responsibility).
# This module only imports what it needs for the _mock_result factory.

from agents.iq_mock_data import MOCK_CITATIONS, SILENT_DOCS_BY_TOPIC, topic_key_for, topic_key_for as _topic_key


def _mock_result(doc_name: str, topic: str, query: str) -> FoundryIQResult:
    """Return a pre-computed Tier 3 result for the given document and topic."""
    tkey = topic_key_for(topic)
    raw_cits = MOCK_CITATIONS.get((doc_name, tkey), [])

    silent_docs = SILENT_DOCS_BY_TOPIC.get(tkey, set())
    is_silent = (doc_name in silent_docs) and not raw_cits

    citations = [
        Citation(
            document=doc_name,
            section=c["section"],
            passage=c["passage"],
            confidence=c["confidence"],
            topic=topic,
        )
        for c in raw_cits
    ]

    return FoundryIQResult(
        query=query,
        document_id=doc_name,
        citations=citations,
        is_silent=is_silent or len(citations) == 0,
        tier_used=3,
    )


# ─── FoundryIQClient ──────────────────────────────────────────────────────────

class FoundryIQClient:
    """
    Grounded citation retrieval client.

    Implements docs/foundry_iq_spec.md §2.1 query pattern and
    docs/reliability_spec.md §1 three-tier fallback chain.

    Usage:
        client = FoundryIQClient()
        result = client.query_document(
            query="What rule applies to: employee data location?",
            document_name="IT_Security_Policy.md",
            document_text="<full policy text>",
            topic="employee data location and processing rules",
        )
    """

    def __init__(self):
        self._azure_client = None
        self._available = False

        if AZURE_ENDPOINT and AZURE_API_KEY:
            try:
                from openai import AzureOpenAI
                self._azure_client = AzureOpenAI(
                    azure_endpoint=AZURE_ENDPOINT,
                    api_key=AZURE_API_KEY,
                    api_version=API_VERSION,
                )
                self._available = True
                logger.info("FoundryIQClient: Azure OpenAI connection configured.")
            except ImportError:
                logger.warning("FoundryIQClient: openai package not available — Tier 3 only.")
            except Exception as e:
                logger.warning("FoundryIQClient: Azure init failed (%s) — Tier 3 only.", e)
        else:
            logger.info("FoundryIQClient: No Azure credentials — Tier 3 mock mode active.")

    def query_document(
        self,
        query: str,
        document_name: str,
        document_text: str,
        topic: str,
        require_grounded_citations: bool = True,
    ) -> FoundryIQResult:
        """
        Query a single document for grounded citations on a topic.
        Implements the per-document query pattern from foundry_iq_spec.md §2.1.
        Falls back through Tier 1 → Tier 2 → Tier 3 automatically.

        Args:
            query:                      Free-form query string
            document_name:              Filename e.g. "IT_Security_Policy.md"
            document_text:              Full text of the policy document
            topic:                      The query topic (for Citation.topic field)
            require_grounded_citations: Always True per spec — enforced via prompt
        """
        # Tier 1: Azure gpt-4o
        if self._available:
            result = self._call_azure(
                query=query,
                document_name=document_name,
                document_text=document_text,
                topic=topic,
                deployment=DEPLOYMENT_4O,
                timeout=TIER1_TIMEOUT,
                tier=1,
            )
            if result is not None:
                return result

            # Tier 2: Azure gpt-4o-mini
            logger.warning("Tier 1 failed for %s — trying Tier 2.", document_name)
            result = self._call_azure(
                query=query,
                document_name=document_name,
                document_text=document_text,
                topic=topic,
                deployment=DEPLOYMENT_MINI,
                timeout=TIER2_TIMEOUT,
                tier=2,
            )
            if result is not None:
                return result
            logger.error("Foundry IQ retrieval failed for %s — using Tier 3 mock citations.", document_name)
            return _mock_result(document_name, topic, query)

        # No Foundry IQ credentials or live retrieval unavailable.
        return _mock_result(document_name, topic, query)

    def _call_azure(
        self,
        query: str,
        document_name: str,
        document_text: str,
        topic: str,
        deployment: str,
        timeout: int,
        tier: int,
    ) -> Optional[FoundryIQResult]:
        """
        Make a single Azure OpenAI call with a timeout.
        Returns None on any error (triggers next tier).
        """
        if self._azure_client is None:
            return None

        user_prompt = _USER_PROMPT_TEMPLATE.format(
            document_name=document_name,
            topic=topic,
            document_text=document_text[:12000],  # safety cap for context window
        )

        try:
            t0 = time.monotonic()
            response = self._azure_client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=1024,
                timeout=timeout,
                response_format={"type": "json_object"},
            )
            elapsed = time.monotonic() - t0

            raw_text = response.choices[0].message.content or ""
            logger.debug(
                "Tier %d (%s) responded for %s in %.2fs",
                tier, deployment, document_name, elapsed,
            )
            return self._parse_response(
                raw_text=raw_text,
                document_name=document_name,
                topic=topic,
                query=query,
                tier=tier,
            )

        except Exception as e:
            logger.warning("Tier %d (%s) error for %s: %s", tier, deployment, document_name, e)
            return None

    def _parse_response(
        self,
        raw_text: str,
        document_name: str,
        topic: str,
        query: str,
        tier: int,
    ) -> Optional[FoundryIQResult]:
        """
        Parse the LLM JSON response into a FoundryIQResult.
        Returns None if parsing fails (triggers next tier).
        """
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            # Try to extract JSON block from mixed-text responses
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if not match:
                logger.warning("Could not parse JSON from %s Tier %d response.", document_name, tier)
                return None
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return None

        is_silent = bool(data.get("is_silent", False))
        raw_cits  = data.get("citations", [])

        citations: list[Citation] = []
        for c in raw_cits:
            section  = str(c.get("section", "")).strip()
            passage  = str(c.get("passage", "")).strip()
            conf_raw = c.get("confidence", 0.5)
            try:
                confidence = max(0.0, min(1.0, float(conf_raw)))
            except (TypeError, ValueError):
                confidence = 0.5

            if passage and section:
                citations.append(Citation(
                    document=document_name,
                    section=section,
                    passage=passage,
                    confidence=confidence,
                    topic=topic,
                ))

        return FoundryIQResult(
            query=query,
            document_id=document_name,
            citations=citations,
            is_silent=is_silent or len(citations) == 0,
            tier_used=tier,
            raw_response=raw_text,
        )
