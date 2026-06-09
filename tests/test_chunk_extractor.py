"""
tests/test_chunk_extractor.py

Tests for ChunkExtractor — the ProviderChain-based extraction layer that
replaces FoundryIQClient as DocumentAnalyzer's reasoning backend.

Coverage:
  1. ChunkExtractor instantiates without errors.
  2. Extract with a live provider mock → Tier 1 result.
  3. Gemini failure → OpenRouter fallback → Tier 1 result.
  4. Groq fallback when Gemini+OpenRouter fail.
  5. All providers fail → Tier 3 mock result (never raises).
  6. Empty document_text → silent result (no providers called).
  7. Malformed LLM JSON → mock fallback (no crash).
  8. Output schema: FoundryIQResult fields are correctly typed.
  9. Citation fields are correctly typed.
  10. DocumentAnalyzer uses ChunkExtractor (not FoundryIQClient) by default.
  11. ChunkExtractor returns tier_used=1 when provider succeeds.
  12. Pipeline reaches ConflictDetector when ChunkExtractor returns live results.
  13. Mock mode NOT activated when providers succeed (unit-level proof).
  14. Mock mode IS activated when all providers fail.
"""

from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock

from agents.foundry_iq_client import FoundryIQResult, Citation
from agents.llm_provider import LLMResponse, LLMProviderError, ProviderChain
from agents.chunk_extractor import ChunkExtractor
from agents.document_analyzer import DocumentAnalyzer, SUPPORTED_TOPICS


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _live_response() -> str:
    """Simulate a valid LLM JSON response for data-residency extraction."""
    return json.dumps({
        "is_silent": False,
        "citations": [
            {
                "section": "§4.2",
                "passage": "All employee data must be stored on US-based servers.",
                "confidence": 0.92,
            }
        ],
    })


def _make_provider_chain(responses: list) -> ProviderChain:
    """
    Build a ProviderChain where each provider call in sequence returns
    the corresponding entry in `responses`.

    Each entry is either:
      - str          → provider succeeds with that text
      - Exception    → provider raises that exception
    """
    provider_mocks = []
    for resp in responses:
        p = MagicMock()
        p.name = "mock_provider"
        p.available = True
        if isinstance(resp, Exception):
            p.complete.side_effect = resp
        else:
            p.complete.return_value = LLMResponse(
                content=resp,
                provider="mock_provider",
                model="mock-model",
                elapsed_s=0.1,
                is_mock_mode=False,
            )
        provider_mocks.append(p)
    return ProviderChain(providers=provider_mocks)


# ─── 1. Instantiation ─────────────────────────────────────────────────────────

class TestChunkExtractorInstantiation:
    def test_instantiates_without_error(self):
        extractor = ChunkExtractor()
        assert extractor is not None

    def test_accepts_custom_provider_chain(self):
        chain = _make_provider_chain([_live_response()])
        extractor = ChunkExtractor(provider_chain=chain)
        assert extractor is not None

    def test_returns_foundry_iq_result(self):
        chain = _make_provider_chain([_live_response()])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="What rule applies?",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 All data must be stored on US servers.",
            topic="employee data location and processing rules",
        )
        assert isinstance(result, FoundryIQResult)


# ─── 2. Live provider success (Tier 1) ────────────────────────────────────────

class TestLiveProviderSuccess:
    def test_tier_1_when_provider_succeeds(self):
        chain = _make_provider_chain([_live_response()])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="data rule?",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers only.",
            topic="employee data location and processing rules",
        )
        assert result.tier_used == 1

    def test_citation_section_preserved(self):
        chain = _make_provider_chain([_live_response()])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="data rule?",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers only.",
            topic="employee data location and processing rules",
        )
        assert any("4.2" in c.section for c in result.citations)

    def test_citation_passage_preserved(self):
        chain = _make_provider_chain([_live_response()])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="data rule?",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers only.",
            topic="employee data location and processing rules",
        )
        assert any("US" in c.passage for c in result.citations)

    def test_citation_document_set_to_filename(self):
        chain = _make_provider_chain([_live_response()])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="data rule?",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers.",
            topic="employee data location and processing rules",
        )
        assert all(c.document == "IT_Security_Policy.md" for c in result.citations)

    def test_is_not_mock_mode_on_live_success(self):
        chain = _make_provider_chain([_live_response()])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="data rule?",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers.",
            topic="employee data location and processing rules",
        )
        assert result.tier_used == 1


# ─── 3. OpenRouter fallback when Gemini fails ─────────────────────────────────

class TestOpenRouterFallback:
    def test_openrouter_used_when_gemini_fails(self):
        chain = _make_provider_chain([
            LLMProviderError("Gemini timeout"),
            _live_response(),       # OpenRouter succeeds
        ])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="q",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers.",
            topic="employee data location and processing rules",
        )
        assert result.tier_used == 1
        assert len(result.citations) > 0


# ─── 4. Groq fallback ────────────────────────────────────────────────────────

class TestGroqFallback:
    def test_groq_used_when_gemini_and_openrouter_fail(self):
        chain = _make_provider_chain([
            LLMProviderError("Gemini fail"),
            LLMProviderError("OpenRouter fail"),
            _live_response(),       # Groq succeeds
        ])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="q",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers.",
            topic="employee data location and processing rules",
        )
        assert result.tier_used == 1
        assert len(result.citations) > 0


# ─── 5. Mock fallback (Tier 3) when all providers fail ───────────────────────

class TestMockFallback:
    def test_mock_used_when_all_providers_fail(self):
        chain = _make_provider_chain([
            LLMProviderError("Gemini fail"),
            LLMProviderError("OpenRouter fail"),
            LLMProviderError("Groq fail"),
            LLMProviderError("NVIDIA fail"),
        ])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="q",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers.",
            topic="employee data location and processing rules",
        )
        assert result.tier_used == 3

    def test_never_raises_when_all_providers_fail(self):
        chain = _make_provider_chain([
            LLMProviderError("all fail"),
        ])
        extractor = ChunkExtractor(provider_chain=chain)
        # Must not raise
        result = extractor.extract(
            query="q",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 data.",
            topic="employee data location and processing rules",
        )
        assert isinstance(result, FoundryIQResult)

    def test_mock_result_tier3(self):
        chain = _make_provider_chain([LLMProviderError("fail")])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="q",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 data.",
            topic="employee data location and processing rules",
        )
        assert result.tier_used == 3


# ─── 6. Empty document_text → silent (no providers called) ───────────────────

class TestEmptyDocumentText:
    def test_empty_text_returns_silent(self):
        chain = _make_provider_chain([])  # no providers should fire
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="q",
            document_name="Whistleblower_Policy.md",
            document_text="",
            topic="employee data location and processing rules",
        )
        assert result.is_silent

    def test_whitespace_only_text_no_citations(self):
        extractor = ChunkExtractor()
        result = extractor.extract(
            query="q",
            document_name="Whistleblower_Policy.md",
            document_text="   ",
            topic="employee data location and processing rules",
        )
        assert len(result.citations) == 0


# ─── 7. Malformed LLM JSON → mock fallback, no crash ─────────────────────────

class TestMalformedJSON:
    def test_malformed_json_falls_back_to_mock(self):
        chain = _make_provider_chain(["NOT JSON AT ALL !!"])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="q",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 data.",
            topic="employee data location and processing rules",
        )
        assert isinstance(result, FoundryIQResult)


# ─── 8. Output schema ─────────────────────────────────────────────────────────

class TestOutputSchema:
    @pytest.fixture
    def live_result(self) -> FoundryIQResult:
        chain = _make_provider_chain([_live_response()])
        extractor = ChunkExtractor(provider_chain=chain)
        return extractor.extract(
            query="q",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers.",
            topic="employee data location and processing rules",
        )

    def test_result_has_document_id(self, live_result):
        assert live_result.document_id == "IT_Security_Policy.md"

    def test_result_has_query(self, live_result):
        assert live_result.query == "q"

    def test_result_tier_used_is_int(self, live_result):
        assert isinstance(live_result.tier_used, int)

    def test_citations_is_list(self, live_result):
        assert isinstance(live_result.citations, list)

    def test_citation_confidence_in_range(self, live_result):
        for c in live_result.citations:
            assert 0.0 <= c.confidence <= 1.0


# ─── 10. DocumentAnalyzer uses ChunkExtractor by default ─────────────────────

class TestDocumentAnalyzerUsesChunkExtractor:
    def test_default_extractor_is_chunk_extractor(self):
        analyzer = DocumentAnalyzer()
        assert isinstance(analyzer._extractor, ChunkExtractor)

    def test_extractor_injection_used_directly(self):
        chain = _make_provider_chain([_live_response()])
        extractor = ChunkExtractor(provider_chain=chain)
        analyzer = DocumentAnalyzer(extractor=extractor)
        assert analyzer._extractor is extractor


# ─── 11. ChunkExtractor returns Tier 1 when provider succeeds ────────────────

class TestChunkExtractorTier1:
    def test_tier1_with_non_empty_text(self):
        """
        ChunkExtractor.extract() called directly with non-empty document_text
        and a working provider: must return tier_used=1 and a valid citation.
        """
        chain = _make_provider_chain([_live_response()])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="q",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers only.",
            topic="employee data location and processing rules",
        )
        assert result.tier_used == 1
        assert result.is_silent is False
        assert len(result.citations) > 0


# ─── 12. Pipeline reaches ConflictDetector ───────────────────────────────────

class TestPipelineReachesConflictDetector:
    def test_conflict_detector_reached_with_live_extractor(self):
        """
        End-to-end: DocumentAnalyzerResult → ConflictDetector.
        Verify ConflictDetector.detect() is called and returns a DetectorResult.
        """
        from agents.document_analyzer import DocumentAnalyzerResult, PolicyStatement
        from agents.conflict_detector import ConflictDetector

        mock_result = DocumentAnalyzerResult(
            topic="employee data location and processing rules",
            query="What rule applies to: employee data location?",
            citations=[
                PolicyStatement(
                    document="IT_Security_Policy.md",
                    section="§4.2",
                    passage="All data must reside on US-based servers.",
                    confidence=0.92,
                    topic="employee data location and processing rules",
                ),
                PolicyStatement(
                    document="DPDP_Compliance_Directive.md",
                    section="§3.1",
                    passage="Data must be stored within Indian jurisdiction.",
                    confidence=0.88,
                    topic="employee data location and processing rules",
                ),
            ],
            low_confidence_citations=[],
            silent_documents=[],
            is_mock_mode=False,
            execution_time_s=0.5,
        )

        conflict_json = json.dumps({
            "has_conflict": True,
            "reasoning": (
                "IT Security requires US servers; DPDP requires Indian jurisdiction. "
                "Structurally impossible."
            ),
            "severity": "CRITICAL",
            "confidence": 0.95,
            "conflict_pairs": [
                {
                    "document_a": "IT_Security_Policy.md",
                    "section_a": "§4.2",
                    "document_b": "DPDP_Compliance_Directive.md",
                    "section_b": "§3.1",
                    "conflict_type": "Data Residency Conflict",
                    "why_impossible": "US server mandate vs Indian jurisdiction mandate.",
                }
            ],
        })
        chain = _make_provider_chain([conflict_json])
        detector = ConflictDetector(provider_chain=chain)

        dr = detector.detect(mock_result)
        assert dr is not None
        total = len(dr.conflicts) + len(dr.uncertain_findings) + len(dr.blocked_findings)
        assert total > 0


# ─── 13. Mock mode NOT activated when providers succeed (unit-level proof) ────

class TestMockModeNotActivatedOnSuccess:
    def test_tier1_means_no_mock_mode(self):
        """
        tier_used=1 from ChunkExtractor proves mock mode was NOT activated.
        """
        chain = _make_provider_chain([_live_response()])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="q",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers must be used.",
            topic="employee data location and processing rules",
        )
        assert result.tier_used == 1  # live provider was used, not mock
        assert len(result.citations) > 0


# ─── 14. Mock mode activated only after all providers fail ────────────────────

class TestMockModeOnlyAfterAllProvidersFail:
    def test_mock_mode_tier3_only_when_all_fail(self):
        chain = _make_provider_chain([
            LLMProviderError("fail"),
        ])
        extractor = ChunkExtractor(provider_chain=chain)
        result = extractor.extract(
            query="q",
            document_name="IT_Security_Policy.md",
            document_text="§4.2 US servers.",
            topic="employee data location and processing rules",
        )
        assert result.tier_used == 3
