# Legacy compatibility layer
# Azure OpenAI dependency removed
# Retained for backward compatibility

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from agents.iq_mock_data import MOCK_CITATIONS, SILENT_DOCS_BY_TOPIC, topic_key_for, topic_key_for as _topic_key

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
    Result of a grounded document query.
    Preserved for backward compatibility with DocumentAnalyzer and tests.
    """
    query: str
    document_id: str        # Filename of the source document
    citations: list[Citation]
    is_silent: bool         # True if document has no relevant content on the topic
    tier_used: int          # 1, 2, or 3 (for MOCK_MODE detection)
    raw_response: Optional[str] = None


# ─── Mock responses (Tier 3) ─────────────────────────────────────────────────

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
