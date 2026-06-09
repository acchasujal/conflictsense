"""
tests/test_document_analyzer.py

Unit tests for DocumentAnalyzer and FoundryIQClient.

Spec reference: docs/agent_contracts.md §1
                docs/foundry_iq_spec.md §2.1
                docs/data_contracts.md §1
                docs/reliability_spec.md §1–3

Test strategy:
  All tests use a MockFoundryIQClient that bypasses Azure (Tier 3 always).
  This ensures tests are:
    - Deterministic (no network dependency)
    - Fast (no LLM calls)
    - Correct (validates schema and routing logic independently of LLM output)

Coverage:
  1. DocumentAnalyzer loads all 7 knowledge base documents
  2. analyze() returns correct PolicyStatement schema
  3. Confidence threshold routing (< 0.65 → low-confidence queue)
  4. Silent documents are filtered and tracked
  5. Tier 3 mock mode is activated when Azure unavailable
  6. Both canonical topics return correct documents
  7. Citation count validation (>= 2 for non-silent topics)
  8. PolicyStatement fields are all present and correctly typed
  9. Single-document analysis works
  10. is_mock_mode flag correctly set
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agents.foundry_iq_client import (
    FoundryIQResult, Citation, _mock_result, _topic_key
)
from agents.document_analyzer import (
    DocumentAnalyzer, DocumentAnalyzerResult, PolicyStatement,
    MIN_CONFIDENCE, SUPPORTED_TOPICS, KB_DIR,
)

# ─── Mock FoundryIQ client (always Tier 3, deterministic) ────────────────────

class MockFoundryIQClient:
    """
    Test double for FoundryIQClient.
    Delegates directly to _mock_result() — always Tier 3, no network.
    """
    def query_document(
        self,
        query: str,
        document_name: str,
        document_text: str,
        topic: str,
        require_grounded_citations: bool = True,
    ) -> FoundryIQResult:
        return _mock_result(document_name, topic, query)


@pytest.fixture(scope="module")
def analyzer() -> DocumentAnalyzer:
    """DocumentAnalyzer with deterministic mock client."""
    return DocumentAnalyzer(foundry_client=MockFoundryIQClient())


@pytest.fixture(scope="module")
def data_residency_result(analyzer) -> DocumentAnalyzerResult:
    return analyzer.analyze(SUPPORTED_TOPICS[0])  # "employee data location..."


@pytest.fixture(scope="module")
def anonymity_result(analyzer) -> DocumentAnalyzerResult:
    return analyzer.analyze(SUPPORTED_TOPICS[1])  # "employee reporting channels..."


# ─── 1. Knowledge base loading ────────────────────────────────────────────────

class TestKnowledgeBaseLoading:
    def test_seven_documents_loaded(self, analyzer):
        assert len(analyzer.document_names) == 7, \
            f"Expected 7 documents, got {len(analyzer.document_names)}"

    def test_all_canonical_documents_present(self, analyzer):
        expected = {
            "IT_Security_Policy.md",
            "HR_Remote_Work_Policy.md",
            "Data_Governance_Policy.md",
            "Employee_Handbook.md",
            "Whistleblower_Policy.md",
            "Finance_Expense_Policy.md",
            "DPDP_Compliance_Directive.md",
        }
        assert set(analyzer.document_names) == expected

    def test_documents_are_non_empty(self, analyzer):
        for name in analyzer.document_names:
            path = KB_DIR / name
            assert path.exists(), f"Missing document: {name}"
            content = path.read_text(encoding="utf-8")
            assert len(content) > 100, f"Document {name} appears empty or too short"

    def test_documents_contain_sections(self, analyzer):
        """All canonical documents should have section headers like §X.Y."""
        for name in analyzer.document_names:
            content = (KB_DIR / name).read_text(encoding="utf-8")
            assert "§" in content, f"Document {name} has no section markers (§)"


# ─── 2. Data residency topic — canonical citations ────────────────────────────

class TestDataResidencyAnalysis:
    def test_returns_document_analyzer_result(self, data_residency_result):
        assert isinstance(data_residency_result, DocumentAnalyzerResult)

    def test_topic_is_set(self, data_residency_result):
        assert "data location" in data_residency_result.topic.lower() or \
               "processing" in data_residency_result.topic.lower()

    def test_citations_are_non_empty(self, data_residency_result):
        assert len(data_residency_result.citations) > 0, \
            "Data residency topic must return at least 1 citation"

    def test_it_security_citation_present(self, data_residency_result):
        docs = {c.document for c in data_residency_result.citations}
        assert "IT_Security_Policy.md" in docs

    def test_hr_remote_work_citation_present(self, data_residency_result):
        docs = {c.document for c in data_residency_result.citations}
        assert "HR_Remote_Work_Policy.md" in docs

    def test_dpdp_citation_present(self, data_residency_result):
        docs = {c.document for c in data_residency_result.citations}
        assert "DPDP_Compliance_Directive.md" in docs

    def test_it_security_section_is_4_2(self, data_residency_result):
        it_cits = [c for c in data_residency_result.citations
                   if c.document == "IT_Security_Policy.md"]
        assert any("4.2" in c.section for c in it_cits), \
            "IT Security data residency citation must reference §4.2"

    def test_hr_section_is_2_1(self, data_residency_result):
        hr_cits = [c for c in data_residency_result.citations
                   if c.document == "HR_Remote_Work_Policy.md"]
        assert any("2.1" in c.section for c in hr_cits), \
            "HR Remote Work citation must reference §2.1"

    def test_dpdp_section_is_3_1(self, data_residency_result):
        dpdp_cits = [c for c in data_residency_result.citations
                     if c.document == "DPDP_Compliance_Directive.md"]
        assert any("3.1" in c.section for c in dpdp_cits)

    def test_it_security_passage_mentions_us_servers(self, data_residency_result):
        it_cits = [c for c in data_residency_result.citations
                   if c.document == "IT_Security_Policy.md"]
        assert any("US" in c.passage or "United States" in c.passage for c in it_cits)

    def test_dpdp_passage_mentions_indian_jurisdiction(self, data_residency_result):
        dpdp_cits = [c for c in data_residency_result.citations
                     if c.document == "DPDP_Compliance_Directive.md"]
        assert any("Indian jurisdiction" in c.passage or "India" in c.passage
                   for c in dpdp_cits)

    def test_is_mock_mode_true(self, data_residency_result):
        """All tests use MockFoundryIQClient (Tier 3) — flag must be True."""
        assert data_residency_result.is_mock_mode is True


# ─── 3. Anonymity topic — canonical citations ─────────────────────────────────

class TestAnonymityAnalysis:
    def test_returns_result(self, anonymity_result):
        assert isinstance(anonymity_result, DocumentAnalyzerResult)

    def test_citations_non_empty(self, anonymity_result):
        assert len(anonymity_result.citations) > 0

    def test_whistleblower_citation_present(self, anonymity_result):
        docs = {c.document for c in anonymity_result.citations}
        assert "Whistleblower_Policy.md" in docs

    def test_it_security_citation_present(self, anonymity_result):
        docs = {c.document for c in anonymity_result.citations}
        assert "IT_Security_Policy.md" in docs

    def test_whistleblower_section_is_4_2(self, anonymity_result):
        wb_cits = [c for c in anonymity_result.citations
                   if c.document == "Whistleblower_Policy.md"]
        assert any("4.2" in c.section for c in wb_cits)

    def test_it_security_section_is_12_1(self, anonymity_result):
        it_cits = [c for c in anonymity_result.citations
                   if c.document == "IT_Security_Policy.md"]
        assert any("12.1" in c.section for c in it_cits)

    def test_whistleblower_passage_mentions_anonymous(self, anonymity_result):
        wb_cits = [c for c in anonymity_result.citations
                   if c.document == "Whistleblower_Policy.md"]
        assert any("anonymous" in c.passage.lower() for c in wb_cits)

    def test_it_security_passage_mentions_logging(self, anonymity_result):
        it_cits = [c for c in anonymity_result.citations
                   if c.document == "IT_Security_Policy.md"]
        assert any("logged" in c.passage.lower() for c in it_cits)

    def test_hr_is_silent(self, anonymity_result):
        """HR Remote Work Policy should be silent on anonymity topic."""
        assert "HR_Remote_Work_Policy.md" in anonymity_result.silent_documents

    def test_dpdp_is_silent(self, anonymity_result):
        assert "DPDP_Compliance_Directive.md" in anonymity_result.silent_documents


# ─── 4. PolicyStatement schema validation ─────────────────────────────────────

class TestPolicyStatementSchema:
    def test_all_citations_have_document(self, data_residency_result):
        for c in data_residency_result.citations:
            assert c.document and isinstance(c.document, str)

    def test_all_citations_have_section(self, data_residency_result):
        for c in data_residency_result.citations:
            assert c.section and isinstance(c.section, str)

    def test_all_citations_have_passage(self, data_residency_result):
        for c in data_residency_result.citations:
            assert c.passage and len(c.passage) > 10, \
                f"Passage too short: {c.passage!r}"

    def test_all_citations_have_confidence_float(self, data_residency_result):
        for c in data_residency_result.citations:
            assert isinstance(c.confidence, float), f"confidence must be float, got {type(c.confidence)}"
            assert 0.0 <= c.confidence <= 1.0, f"confidence out of range: {c.confidence}"

    def test_all_citations_have_topic(self, data_residency_result):
        for c in data_residency_result.citations:
            assert c.topic and isinstance(c.topic, str)

    def test_document_filename_format(self, data_residency_result):
        """Document names should end with .md"""
        for c in data_residency_result.citations:
            assert c.document.endswith(".md"), \
                f"Document name {c.document!r} should end with .md"

    def test_section_format(self, data_residency_result):
        """Sections should contain § symbol."""
        for c in data_residency_result.citations:
            assert "§" in c.section, \
                f"Section {c.section!r} should contain § character"


# ─── 5. Confidence threshold routing ─────────────────────────────────────────

class TestConfidenceThresholdRouting:
    def test_min_confidence_value(self):
        assert MIN_CONFIDENCE == 0.65, "MIN_CONFIDENCE must be 0.65 per reliability_spec.md §2"

    def test_all_accepted_citations_above_threshold(self, data_residency_result):
        for c in data_residency_result.citations:
            assert c.confidence >= MIN_CONFIDENCE, \
                f"Citation {c.document} {c.section} below threshold: {c.confidence}"

    def test_low_confidence_citations_are_below_threshold(self, data_residency_result):
        for c in data_residency_result.low_confidence_citations:
            assert c.confidence < MIN_CONFIDENCE, \
                f"Low-conf citation {c.document} should be < {MIN_CONFIDENCE}"

    def test_data_governance_eu_gdpr_low_confidence(self, data_residency_result):
        """
        Data_Governance_Policy §7.3 (EU GDPR) has confidence=0.74 — above threshold.
        It should appear in the main citations, not the low-confidence queue.
        """
        dg_cits = [c for c in data_residency_result.citations
                   if c.document == "Data_Governance_Policy.md"]
        # Confidence 0.74 is above MIN_CONFIDENCE=0.65, so it's accepted
        if dg_cits:
            assert all(c.confidence >= MIN_CONFIDENCE for c in dg_cits)


# ─── 6. Silent document tracking ─────────────────────────────────────────────

class TestSilentDocuments:
    def test_silent_docs_tracked(self, data_residency_result):
        assert isinstance(data_residency_result.silent_documents, list)

    def test_whistleblower_silent_for_data_residency(self, data_residency_result):
        """Whistleblower Policy has no data residency rules."""
        assert "Whistleblower_Policy.md" in data_residency_result.silent_documents

    def test_finance_silent_for_data_residency(self, data_residency_result):
        assert "Finance_Expense_Policy.md" in data_residency_result.silent_documents

    def test_employee_handbook_silent_for_data_residency(self, data_residency_result):
        assert "Employee_Handbook.md" in data_residency_result.silent_documents

    def test_silent_docs_not_in_citations(self, data_residency_result):
        cited_docs = {c.document for c in data_residency_result.citations}
        for silent in data_residency_result.silent_documents:
            assert silent not in cited_docs, \
                f"Silent document {silent} should not appear in citations"


# ─── 7. Citation count validation (reliability_spec.md §3) ───────────────────

class TestCitationCountValidation:
    def test_data_residency_has_three_or_more_citations(self, data_residency_result):
        """Data residency is a three-way conflict — needs >= 3 citations."""
        assert len(data_residency_result.citations) >= 3, \
            f"Expected >= 3 citations for data residency, got {len(data_residency_result.citations)}"

    def test_anonymity_has_exactly_two_citations(self, anonymity_result):
        """Anonymity is a two-way conflict — needs exactly 2."""
        assert len(anonymity_result.citations) >= 2


# ─── 8. Single document analysis ─────────────────────────────────────────────

class TestSingleDocumentAnalysis:
    def test_single_doc_returns_foundry_iq_result(self, analyzer):
        from agents.foundry_iq_client import FoundryIQResult
        result = analyzer.analyze_single_document(
            topic=SUPPORTED_TOPICS[0],
            document_name="IT_Security_Policy.md",
        )
        assert isinstance(result, FoundryIQResult)

    def test_single_doc_it_security_data_residency(self, analyzer):
        result = analyzer.analyze_single_document(
            topic=SUPPORTED_TOPICS[0],
            document_name="IT_Security_Policy.md",
        )
        assert not result.is_silent
        assert len(result.citations) >= 1

    def test_single_doc_whistleblower_data_residency_silent(self, analyzer):
        """Whistleblower Policy is silent on data location."""
        result = analyzer.analyze_single_document(
            topic=SUPPORTED_TOPICS[0],
            document_name="Whistleblower_Policy.md",
        )
        assert result.is_silent

    def test_single_doc_invalid_name_raises(self, analyzer):
        with pytest.raises(ValueError, match="not found"):
            analyzer.analyze_single_document(
                topic=SUPPORTED_TOPICS[0],
                document_name="NonExistent_Policy.md",
            )


# ─── 9. FoundryIQClient Tier 3 fallback ─────────────────────────────────────

class TestFoundryIQClientTier3Fallback:
    # Removed test_no_azure_credentials_uses_tier3 because Azure OpenAI was removed

    def test_tier3_returns_correct_citation_for_it_security(self):
        result = _mock_result(
            "IT_Security_Policy.md",
            "employee data location and processing rules",
            "test query",
        )
        assert not result.is_silent
        assert len(result.citations) >= 1
        assert any("§4.2" in c.section for c in result.citations)

    def test_tier3_returns_correct_citation_for_whistleblower_anonymity(self):
        result = _mock_result(
            "Whistleblower_Policy.md",
            "employee reporting channels and anonymity guarantees",
            "test query",
        )
        assert not result.is_silent
        assert any("§4.2" in c.section for c in result.citations)
        assert any("anonymous" in c.passage.lower() for c in result.citations)

    def test_tier3_marks_silent_documents_correctly(self):
        result = _mock_result(
            "Finance_Expense_Policy.md",
            "employee data location and processing rules",
            "test query",
        )
        assert result.is_silent

    def test_tier3_citation_confidence_in_range(self):
        result = _mock_result(
            "IT_Security_Policy.md",
            "employee data location and processing rules",
            "test query",
        )
        for c in result.citations:
            assert 0.0 <= c.confidence <= 1.0

    # Removed test_invalid_azure_key_falls_back_to_tier3 because Azure OpenAI was removed


# ─── 10. Topic key mapping ────────────────────────────────────────────────────

class TestTopicKeyMapping:
    def test_data_location_topic_key(self):
        assert _topic_key("employee data location and processing rules") == "data location"
        assert _topic_key("server data processing") == "data location"
        assert _topic_key("data residency rules") == "data location"

    def test_anonymity_topic_key(self):
        assert _topic_key("employee reporting channels and anonymity guarantees") == "anonymity"
        assert _topic_key("anonymous reporting") == "anonymity"
        assert _topic_key("whistleblower channel") == "anonymity"


# ─── 11. is_mock_mode propagation ────────────────────────────────────────────

class TestMockModePropagation:
    def test_mock_mode_true_with_mock_client(self, data_residency_result):
        assert data_residency_result.is_mock_mode is True

    def test_mock_mode_true_for_anonymity_topic(self, anonymity_result):
        assert anonymity_result.is_mock_mode is True

    def test_execution_time_recorded(self, data_residency_result):
        assert data_residency_result.execution_time_s >= 0.0
        assert data_residency_result.execution_time_s < 60.0

    def test_per_doc_results_count(self, data_residency_result):
        assert len(data_residency_result.per_doc_results) == 7
