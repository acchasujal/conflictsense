"""
agents/chunk_extractor.py

Per-document citation extraction using the multi-provider ProviderChain.

Replaces FoundryIQClient's hard Azure OpenAI dependency with the
existing fallback stack (Gemini → OpenRouter → Groq → NVIDIA → Mock).

Returns the same FoundryIQResult / Citation schema that DocumentAnalyzer
already consumes, so no downstream changes are required.

Responsibilities:
  - Accept retrieved chunks assembled into a document_text block.
  - Build the extraction prompt (same spec as foundry_iq_client §1).
  - Call ProviderChain.complete_json() — no Azure OpenAI required.
  - Parse the JSON response into FoundryIQResult + Citation objects.
  - Fall back to pre-computed mock data when all providers fail.

Provider priority order (inherited from llm_provider.py):
  1. Gemini
  2. OpenRouter
  3. Groq
  4. NVIDIA NIM
  5. Mock (iq_mock_data.py — never fails)
"""

from __future__ import annotations

import logging
from typing import Optional

from agents.foundry_iq_client import FoundryIQResult, Citation, _mock_result
from agents.llm_provider import ProviderChain, get_provider_chain

logger = logging.getLogger("conflictsense.chunk_extractor")

# ─── Extraction prompt (mirrors foundry_iq_client._SYSTEM_PROMPT verbatim) ────

_EXTRACTION_SYSTEM_PROMPT = """\
You are a policy document analyst. Extract the specific rule or constraint that applies to the given topic from the provided document.

Return ONLY verbatim text from the document. Do not infer, extrapolate, or summarise.

Return JSON:
{"is_silent": boolean, "citations": [{"section": "§X.Y", "passage": "exact quoted text", "confidence": 0.0-1.0}]}

Rules: is_silent=true if no relevant rule exists. section must be the actual document identifier. passage must be verbatim. Do not add text outside the JSON.
"""

_EXTRACTION_USER_TEMPLATE = """\
Document: {document_name}

Topic: {topic}

Document content:
---
{document_text}
---

Return the JSON extraction as specified.\
"""


class ChunkExtractor:
    """
    Extracts PolicyStatement-compatible citations from retrieved chunks
    using ProviderChain (Gemini → OpenRouter → Groq → NVIDIA → Mock).

    Public interface is intentionally identical to FoundryIQClient so
    DocumentAnalyzer can swap the two without any downstream schema changes.

    Usage:
        extractor = ChunkExtractor()
        result = extractor.extract(
            query="What rule applies to: employee data location?",
            document_name="IT_Security_Policy.md",
            document_text="<retrieved chunk text>",
            topic="employee data location and processing rules",
        )
        # result.citations  → list[Citation]
        # result.is_silent  → bool
        # result.tier_used  → 1 (live provider) or 3 (mock fallback)
    """

    def __init__(self, provider_chain: Optional[ProviderChain] = None, allow_mock: bool = True) -> None:
        self._chain = provider_chain or get_provider_chain()
        self._allow_mock = allow_mock
        logger.info(
            "ChunkExtractor initialised (ProviderChain, allow_mock=%s).",
            allow_mock,
        )

    # ── Public interface (matches FoundryIQClient.query_document signature) ────

    def extract(
        self,
        query: str,
        document_name: str,
        document_text: str,
        topic: str,
    ) -> FoundryIQResult:
        """
        Extract citations from retrieved chunk text for a given document and topic.

        Falls back through: Gemini → OpenRouter → Groq → NVIDIA → Mock.
        Never raises — worst case returns a Tier 3 mock result.

        Args:
            query:         Free-form query string (for logging).
            document_name: Filename e.g. "IT_Security_Policy.md".
            document_text: Assembled chunk text (already retrieved from Azure Search).
            topic:         Policy topic for Citation.topic field.

        Returns:
            FoundryIQResult with tier_used=1 (live) or tier_used=3 (mock).
        """
        if not document_text.strip():
            # No chunks retrieved for this document on this topic → silent
            logger.debug("ChunkExtractor: no chunks for %s on topic %r → silent.", document_name, topic)
            return FoundryIQResult(
                query=query,
                document_id=document_name,
                citations=[],
                is_silent=True,
                tier_used=1,
            )

        user_prompt = _EXTRACTION_USER_TEMPLATE.format(
            document_name=document_name,
            topic=topic,
            document_text=document_text[:12000],  # safety cap matching foundry_iq_client
        )

        def _mock_factory() -> dict:
            r = _mock_result(document_name, topic, query)
            return {
                "is_silent": r.is_silent,
                "citations": [
                    {
                        "section": c.section,
                        "passage": c.passage,
                        "confidence": c.confidence,
                    }
                    for c in r.citations
                ],
            }

        try:
            data, response = self._chain.complete_json(
                _EXTRACTION_SYSTEM_PROMPT,
                user_prompt,
                mock_factory=_mock_factory,
                allow_mock=self._allow_mock,
            )
        except Exception as exc:
            if not self._allow_mock:
                logger.error(
                    "ChunkExtractor: strict live mode — provider chain failed for %s: %s",
                    document_name, exc,
                )
                raise
            logger.warning(
                "ChunkExtractor: provider chain raised unexpectedly for %s: %s — using mock.",
                document_name, exc,
            )
            return _mock_result(document_name, topic, query)

        tier = 3 if response.is_mock_mode else 1
        provider = response.provider

        if response.is_mock_mode:
            logger.info(
                "ChunkExtractor: %s → Tier 3 mock (all providers exhausted).", document_name
            )
        else:
            logger.info(
                "ChunkExtractor: %s → provider=%s model=%s tier=1.",
                document_name, provider, response.model,
            )

        return self._parse(data, document_name, topic, query, tier)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _parse(
        self,
        data: dict,
        document_name: str,
        topic: str,
        query: str,
        tier: int,
    ) -> FoundryIQResult:
        """Parse the JSON dict from ProviderChain into a FoundryIQResult."""
        is_silent = bool(data.get("is_silent", False))
        raw_cits = data.get("citations", [])

        citations: list[Citation] = []
        for c in raw_cits:
            section = str(c.get("section", "")).strip()
            passage = str(c.get("passage", "")).strip()
            try:
                confidence = max(0.0, min(1.0, float(c.get("confidence", 0.5))))
            except (TypeError, ValueError):
                confidence = 0.5

            if section and passage:
                citations.append(
                    Citation(
                        document=document_name,
                        section=section,
                        passage=passage,
                        confidence=confidence,
                        topic=topic,
                    )
                )

        if not citations and not is_silent:
            # Provider returned no parseable citations — treat as silent
            logger.warning(
                "ChunkExtractor: %s returned is_silent=False but no valid citations — forcing silent.",
                document_name,
            )
            is_silent = True

        return FoundryIQResult(
            query=query,
            document_id=document_name,
            citations=citations,
            is_silent=is_silent or not citations,
            tier_used=tier,
        )
