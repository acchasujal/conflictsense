"""
agents/document_analyzer.py

DocumentAnalyzer agent — per-document grounded retrieval from Foundry IQ.

Spec reference: docs/agent_contracts.md §1
                docs/foundry_iq_spec.md §2.1
                docs/prompt_registry.md §1
                docs/data_contracts.md §1 (PolicyStatement schema)

Responsibilities:
  - Load every document from knowledge_base/
  - For each document, call FoundryIQClient.query_document() with:
        query  = "What rule or policy applies to: {topic}?"
        knowledge_source_ids = [single_doc]    (per-document strategy)
        require_grounded_citations = True
  - Filter out documents that are silent on the topic (is_silent=True)
  - Return a DocumentAnalyzerResult containing:
        citations   — list[PolicyStatement]   (docs/data_contracts.md §1)
        is_mock_mode — bool                   (True if any Tier 3 was used)
        metadata    — per-document trace info

Constraints:
  - Do NOT infer, extrapolate, or summarise (agent_contracts.md §1)
  - Do NOT return documents that are silent on the topic
  - Confidence threshold: only pass citations with confidence >= 0.65
    (docs/reliability_spec.md §2)
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from agents.foundry_iq_client import FoundryIQClient, FoundryIQResult, Citation

logger = logging.getLogger("conflictsense.document_analyzer")

# ─── Knowledge base path ──────────────────────────────────────────────────────
KB_DIR = Path(__file__).parent.parent / "knowledge_base"

# ─── Confidence threshold (docs/reliability_spec.md §2) ──────────────────────
MIN_CONFIDENCE: float = 0.65

# ─── Supported topics (docs/agent_contracts.md §1, foundry_iq_spec.md §2.1) ──
SUPPORTED_TOPICS: list[str] = [
    "employee data location and processing rules",
    "employee reporting channels and anonymity guarantees",
]

# ─── Output data classes ─────────────────────────────────────────────────────

@dataclass
class PolicyStatement:
    """
    A single grounded citation returned by DocumentAnalyzer.
    Exactly matches docs/data_contracts.md §1 PolicyStatement interface.
    """
    document: str        # e.g. "IT_Security_Policy.md"
    section: str         # e.g. "§4.2"
    passage: str         # Exact verbatim text from the document
    confidence: float    # Foundry IQ retrieval confidence 0.0–1.0
    topic: str           # The query topic


@dataclass
class DocumentAnalyzerResult:
    """
    Complete output of a DocumentAnalyzer run across all 7 knowledge base docs.
    Returned to the orchestrator / backend for the next pipeline stage.
    """
    topic: str
    query: str
    citations: list[PolicyStatement]          # Non-silent, >= MIN_CONFIDENCE
    low_confidence_citations: list[PolicyStatement]  # Routed to review queue
    silent_documents: list[str]               # Docs with no relevant content
    is_mock_mode: bool                        # True if any Tier 3 was used
    execution_time_s: float                   # Total wall-clock time
    per_doc_results: list[dict] = field(default_factory=list)  # Debug metadata


# ─── DocumentAnalyzer ────────────────────────────────────────────────────────

class DocumentAnalyzer:
    """
    Policy document analyst agent.

    Implements the per-document Foundry IQ query strategy:
      - One FoundryIQ call per document (prevents context overflow)
      - Section-level attribution preserved
      - Grounded citations only (require_grounded_citations=True)

    Usage:
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze(topic="employee data location and processing rules")

        for citation in result.citations:
            print(f"{citation.document} {citation.section}: {citation.passage[:80]}...")
    """

    def __init__(self, foundry_client: Optional[FoundryIQClient] = None):
        """
        Args:
            foundry_client: Optional pre-built FoundryIQClient (injected for testing).
                           If None, creates one using environment credentials.
        """
        self._client = foundry_client or FoundryIQClient()
        self._documents = self._load_documents()
        logger.info(
            "DocumentAnalyzer initialised. %d documents loaded from %s.",
            len(self._documents), KB_DIR,
        )

    # ── Public interface ──────────────────────────────────────────────────────

    def analyze(self, topic: str) -> DocumentAnalyzerResult:
        """
        Run the full per-document analysis for the given topic.

        For each document in knowledge_base/:
          1. Build the Foundry IQ query
          2. Call FoundryIQClient.query_document()
          3. Filter by confidence threshold and silence flag
          4. Collect results into DocumentAnalyzerResult

        Args:
            topic: The policy topic to investigate.
                   Should be one of SUPPORTED_TOPICS but any string is accepted.

        Returns:
            DocumentAnalyzerResult with all grounded citations.
        """
        t0 = time.monotonic()
        query = f"What rule or policy applies to: {topic}?"
        logger.info("DocumentAnalyzer.analyze() — topic: %r", topic)

        citations: list[PolicyStatement] = []
        low_conf:  list[PolicyStatement] = []
        silent_docs: list[str]           = []
        per_doc_meta: list[dict]         = []
        mock_mode_triggered              = False

        # Prepare concurrent tasks
        futures = {}
        with ThreadPoolExecutor(max_workers=len(self._documents)) as executor:
            for doc_name, doc_text in self._documents.items():
                future = executor.submit(
                    self._analyze_document,
                    query=query,
                    document_name=doc_name,
                    document_text=doc_text,
                    topic=topic,
                )
                futures[future] = doc_name

            for future in as_completed(futures):
                doc_name = futures[future]
                # If an exception occurs, let it bubble up to the orchestrator to trigger mock fallback
                doc_result = future.result()

                if doc_result.tier_used == 3:
                    mock_mode_triggered = True

                meta = {
                    "document": doc_name,
                    "tier_used": doc_result.tier_used,
                    "is_silent": doc_result.is_silent,
                    "citations_found": len(doc_result.citations),
                }

                if doc_result.is_silent or not doc_result.citations:
                    silent_docs.append(doc_name)
                    logger.debug("Silent: %s (no relevant content for topic).", doc_name)
                else:
                    for cit in doc_result.citations:
                        stmt = PolicyStatement(
                            document=cit.document,
                            section=cit.section,
                            passage=cit.passage,
                            confidence=cit.confidence,
                            topic=cit.topic,
                        )
                        if cit.confidence >= MIN_CONFIDENCE:
                            citations.append(stmt)
                            logger.info(
                                "Citation accepted: %s %s (conf=%.2f)",
                                doc_name, cit.section, cit.confidence,
                            )
                        else:
                            low_conf.append(stmt)
                            logger.info(
                                "Citation routed to review queue (low conf=%.2f): %s %s",
                                cit.confidence, doc_name, cit.section,
                            )
                    meta["citations_accepted"] = len([c for c in doc_result.citations
                                                       if c.confidence >= MIN_CONFIDENCE])

                per_doc_meta.append(meta)

        elapsed = time.monotonic() - t0
        logger.info(
            "DocumentAnalyzer complete in %.2fs — %d citations from %d docs (%d silent, %d low-conf).",
            elapsed, len(citations), len(self._documents),
            len(silent_docs), len(low_conf),
        )

        return DocumentAnalyzerResult(
            topic=topic,
            query=query,
            citations=citations,
            low_confidence_citations=low_conf,
            silent_documents=silent_docs,
            is_mock_mode=mock_mode_triggered,
            execution_time_s=elapsed,
            per_doc_results=per_doc_meta,
        )

    def analyze_single_document(
        self,
        topic: str,
        document_name: str,
    ) -> FoundryIQResult:
        """
        Analyze a single named document. Useful for targeted retrieval.

        Args:
            topic:         The query topic.
            document_name: Filename e.g. "IT_Security_Policy.md"

        Returns:
            Raw FoundryIQResult (caller handles filtering).
        """
        doc_text = self._documents.get(document_name)
        if doc_text is None:
            raise ValueError(f"Document {document_name!r} not found in knowledge_base/")
        query = f"What rule or policy applies to: {topic}?"
        return self._analyze_document(
            query=query,
            document_name=document_name,
            document_text=doc_text,
            topic=topic,
        )

    @property
    def document_names(self) -> list[str]:
        """Names of all loaded knowledge base documents."""
        return list(self._documents.keys())

    # ── Private helpers ───────────────────────────────────────────────────────

    def _analyze_document(
        self,
        query: str,
        document_name: str,
        document_text: str,
        topic: str,
    ) -> FoundryIQResult:
        """
        Call the Foundry IQ client for one document. Wraps error handling.
        """
        # Removed try-except block to allow Azure errors to bubble up to Orchestrator
        return self._client.query_document(
            query=query,
            document_name=document_name,
            document_text=document_text,
            topic=topic,
            require_grounded_citations=True,
        )

    @staticmethod
    def _load_documents() -> dict[str, str]:
        """
        Load all 7 policy documents from knowledge_base/.
        Returns a dict of { filename: full_text }.
        """
        docs: dict[str, str] = {}
        if not KB_DIR.exists():
            logger.error("knowledge_base/ directory not found at %s", KB_DIR)
            return docs

        for path in sorted(KB_DIR.glob("*.md")):
            try:
                text = path.read_text(encoding="utf-8")
                docs[path.name] = text
                logger.debug("Loaded document: %s (%d chars)", path.name, len(text))
            except OSError as e:
                logger.error("Failed to load %s: %s", path.name, e)

        return docs


# ─── Convenience function for the backend / tests ────────────────────────────

_default_analyzer: Optional[DocumentAnalyzer] = None


def get_analyzer() -> DocumentAnalyzer:
    """Return the module-level singleton DocumentAnalyzer instance."""
    global _default_analyzer
    if _default_analyzer is None:
        _default_analyzer = DocumentAnalyzer()
    return _default_analyzer


def run_analysis(topic: str) -> DocumentAnalyzerResult:
    """
    Top-level convenience function.

    Args:
        topic: One of SUPPORTED_TOPICS (or any free-form policy topic).

    Returns:
        DocumentAnalyzerResult with all grounded citations.
    """
    return get_analyzer().analyze(topic)
