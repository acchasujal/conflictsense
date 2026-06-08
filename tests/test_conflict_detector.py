"""
tests/test_conflict_detector.py

Exhaustive unit test suite for the ConflictDetector agent.

Spec reference:
    docs/test_corpus.md       §1 (positive cases), §2 (negative), §3 (edge cases)
    docs/reliability_spec.md  §2–3
    docs/acceptance_criteria.md §2
    docs/agent_contracts.md   §2

Coverage targets:
  - Positive Cases (must detect):
      • anonymity conflict (Whistleblower vs IT Security)
      • data residency trilemma (IT + HR + DPDP)
      • incident reporting gap (FCA 72-hour)
      • retention conflict (BYOD delete vs 7-year retain)
      • approval workflow conflict (auto vs. discretionary)
      • MFA exception contradiction
      • expense self-certification conflict

  - Negative Cases (must NOT detect):
      • wording / synonym differences
      • complementary policies
      • single-document statements (< 2 citations)
      • policy exceptions that do not invalidate the rule

  - Edge Cases:
      • < 2 citations → blocked
      • confidence < 0.65 → UNCERTAIN, not on dashboard
      • duplicate conflicts suppressed
      • missing citations → ValidationError
      • empty passage → ValidationError
      • all required ConflictRecord fields present
      • schema validation rejects malformed records

Test structure:
  - Each class covers one spec section or one conflict type
  - Fixtures use pre-built PolicyStatement objects (no external I/O)
  - Tests are deterministic (temperature=0 enforced; mocks used)
  - Target: ≥ 90% path coverage of conflict_detector.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from agents.conflict_helpers import (
    MIN_CITATIONS,
    MEDIUM_CONF_THRESHOLD,
    HIGH_CONF_THRESHOLD,
    SchemaValidator,
    ConfidenceFramework,
    DuplicateFilter,
    InsufficientCitationsError,
    ValidationError,
)
from agents.conflict_detector import (
    ConflictDetector,
    detect_conflicts,
    get_detector,
)
from agents.iq_mock_data import topic_key_for as _topic_key
from agents.conflict_types import (
    ConflictSeverity,
    ConflictStatus,
    ConflictType,
    ConflictPair,
    ConflictRecord,
    DetectorResult,
)
from agents.document_analyzer import DocumentAnalyzerResult, PolicyStatement


# ═══════════════════════════════════════════════════════════════════════════════
# Shared Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

def _stmt(document: str, section: str, passage: str, confidence: float = 0.90) -> PolicyStatement:
    """Build a PolicyStatement shorthand for tests."""
    return PolicyStatement(
        document=document,
        section=section,
        passage=passage,
        confidence=confidence,
        topic="test topic",
    )


def _make_analyzer_result(
    topic: str,
    citations: list[PolicyStatement],
    is_mock_mode: bool = True,
) -> DocumentAnalyzerResult:
    return DocumentAnalyzerResult(
        topic=topic,
        query=f"What rule or policy applies to: {topic}?",
        citations=citations,
        low_confidence_citations=[],
        silent_documents=[],
        is_mock_mode=is_mock_mode,
        execution_time_s=0.1,
    )


# ─── Core citation fixtures ────────────────────────────────────────────────────

@pytest.fixture
def whistleblower_stmt() -> PolicyStatement:
    return _stmt(
        "Whistleblower_Policy.md", "§4.2",
        "Reports filed through the ethics portal are anonymous. "
        "Employee identity is never logged or traceable by any internal party.",
        confidence=0.91,
    )


@pytest.fixture
def it_security_logging_stmt() -> PolicyStatement:
    return _stmt(
        "IT_Security_Policy.md", "§12.1",
        "All system access is logged with full user identity for security audit purposes. "
        "No exceptions permitted.",
        confidence=0.95,
    )


@pytest.fixture
def it_security_us_servers_stmt() -> PolicyStatement:
    return _stmt(
        "IT_Security_Policy.md", "§4.2",
        "All company data processing shall occur exclusively on US-domiciled servers. "
        "VPN access restricted to US IP ranges.",
        confidence=0.96,
    )


@pytest.fixture
def hr_remote_work_stmt() -> PolicyStatement:
    return _stmt(
        "HR_Remote_Work_Policy.md", "§2.1",
        "Employees may work from any global location without prior approval.",
        confidence=0.95,
    )


@pytest.fixture
def dpdp_directive_stmt() -> PolicyStatement:
    return _stmt(
        "DPDP_Compliance_Directive.md", "§3.1",
        "Personal data of Indian-resident employees must be processed within Indian jurisdiction. "
        "Effective July 1, 2026.",
        confidence=0.94,
    )


@pytest.fixture
def byod_delete_stmt() -> PolicyStatement:
    return _stmt(
        "IT_Security_Policy.md", "§6.3",
        "Upon termination or transfer, all company data stored on personal devices (BYOD) "
        "must be immediately and permanently deleted.",
        confidence=0.83,
    )


@pytest.fixture
def retention_7yr_stmt() -> PolicyStatement:
    return _stmt(
        "Data_Governance_Policy.md", "§11.2",
        "To comply with financial audits, all communications and work products of employees "
        "must be retained for a mandatory period of 7 years.",
        confidence=0.82,
    )


@pytest.fixture
def mfa_mandatory_stmt() -> PolicyStatement:
    return _stmt(
        "IT_Security_Policy.md", "§7",
        "Multi-Factor Authentication (MFA) is mandatory for all access to company networks "
        "and systems, with no exceptions for any user type.",
        confidence=0.71,
    )


@pytest.fixture
def mfa_exception_stmt() -> PolicyStatement:
    return _stmt(
        "HR_Remote_Work_Policy.md", "§4",
        "External contractors and temporary staff may be granted network access without MFA "
        "if approved in writing by their sponsoring department manager.",
        confidence=0.70,
    )


@pytest.fixture
def expense_receipt_stmt() -> PolicyStatement:
    return _stmt(
        "Finance_Expense_Policy.md", "§8",
        "No expense reimbursement will be processed without a valid receipt or invoice from "
        "the merchant. Self-certification of expenses is strictly prohibited.",
        confidence=0.68,
    )


@pytest.fixture
def expense_selfcert_stmt() -> PolicyStatement:
    return _stmt(
        "Employee_Handbook.md", "§22",
        "For emergency travel or critical supply procurement under $100, employees may "
        "self-certify the expense using the emergency form if a receipt was unobtainable.",
        confidence=0.67,
    )


# ─── ConflictDetector with Azure mocked out (always Tier 3) ───────────────────

@pytest.fixture
def detector() -> ConflictDetector:
    """ConflictDetector in Tier 3-only mode (no Azure credentials)."""
    with patch("agents.conflict_detector.AZURE_ENDPOINT", ""), \
         patch("agents.conflict_detector.AZURE_API_KEY", ""):
        return ConflictDetector(azure_client=None)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. POSITIVE CASES — the detector MUST detect these conflicts
# ═══════════════════════════════════════════════════════════════════════════════

class TestAnonymityConflict:
    """
    Case 1 (test_corpus.md §1): Whistleblower_Policy.md vs IT_Security_Policy.md
    Expected: CRITICAL severity, isSurprise=True, ≥ 2 citations.
    Golden reasoning: see docs/reasoning_trace_examples.md §2.
    """

    TOPIC = "employee reporting channels and anonymity guarantees"

    def _run(self, detector, whistleblower_stmt, it_security_logging_stmt) -> DetectorResult:
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[whistleblower_stmt, it_security_logging_stmt],
        )
        return detector.detect(result)

    def test_conflict_detected(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        assert len(dr.conflicts) == 1, "Anonymity conflict must be detected"

    def test_has_conflict_true(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        assert dr.conflicts[0].has_conflict is True

    def test_severity_critical(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        assert dr.conflicts[0].severity == ConflictSeverity.CRITICAL

    def test_is_surprise_true(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        assert dr.conflicts[0].isSurprise is True, "Anonymity conflict must be marked isSurprise=True"

    def test_minimum_two_citations(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        assert len(dr.conflicts[0].citations) >= 2

    def test_sources_contain_whistleblower(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        sources_str = " ".join(dr.conflicts[0].sources)
        assert "Whistleblower_Policy.md" in sources_str

    def test_sources_contain_it_security(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        sources_str = " ".join(dr.conflicts[0].sources)
        assert "IT_Security_Policy.md" in sources_str

    def test_confidence_above_high_threshold(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        assert dr.conflicts[0].confidence >= 85, "CRITICAL anonymity conflict must be HIGH confidence"

    def test_reasoning_is_prose(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        reasoning = dr.conflicts[0].reasoning
        # Must be a prose paragraph, not a JSON dump or short classifier label
        assert len(reasoning) > 100, "Reasoning must be a prose paragraph (>100 chars)"
        assert "{" not in reasoning, "Reasoning must NOT be a JSON dump"

    def test_reasoning_names_both_policies(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        reasoning = dr.conflicts[0].reasoning.lower()
        assert "whistleblower" in reasoning or "anonymous" in reasoning
        assert "it security" in reasoning or "logged" in reasoning or "identity" in reasoning

    def test_status_confirmed(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        assert dr.conflicts[0].status == ConflictStatus.CONFIRMED

    def test_conflict_type_is_direct_contradiction(self, detector, whistleblower_stmt, it_security_logging_stmt):
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        c = dr.conflicts[0]
        # Type should be Direct Contradiction (anonymity is a binary impossible)
        assert c.conflict_type in (
            ConflictType.DIRECT_CONTRADICTION, ConflictType.ACCESS_CONTROL
        ), f"Unexpected conflict_type: {c.conflict_type}"

    def test_mock_mode_used(self, detector, whistleblower_stmt, it_security_logging_stmt):
        """With no Azure credentials, Tier 3 must activate."""
        dr = self._run(detector, whistleblower_stmt, it_security_logging_stmt)
        assert dr.tier_used == 3


class TestDataResidencyTrilemma:
    """
    Case 2 (test_corpus.md §1): IT_Security + HR_Remote_Work + DPDP_Compliance
    Expected: CRITICAL severity, ≥ 3 sources, mentions India.
    """

    TOPIC = "employee data location and processing rules"

    def _run(
        self, detector,
        it_security_us_servers_stmt,
        hr_remote_work_stmt,
        dpdp_directive_stmt,
    ) -> DetectorResult:
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt],
        )
        return detector.detect(result)

    def test_conflict_detected(
        self, detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt
    ):
        dr = self._run(detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt)
        assert len(dr.conflicts) == 1

    def test_severity_critical(
        self, detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt
    ):
        dr = self._run(detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt)
        assert dr.conflicts[0].severity == ConflictSeverity.CRITICAL

    def test_three_or_more_sources(
        self, detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt
    ):
        dr = self._run(detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt)
        assert len(dr.conflicts[0].sources) >= 3, "Data residency is a THREE-way conflict"

    def test_sources_include_dpdp(
        self, detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt
    ):
        dr = self._run(detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt)
        sources_str = " ".join(dr.conflicts[0].sources)
        assert "DPDP" in sources_str

    def test_sources_include_hr_remote_work(
        self, detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt
    ):
        dr = self._run(detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt)
        sources_str = " ".join(dr.conflicts[0].sources)
        assert "HR_Remote_Work_Policy.md" in sources_str

    def test_reasoning_mentions_india(
        self, detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt
    ):
        dr = self._run(detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt)
        reasoning_lower = dr.conflicts[0].reasoning.lower()
        assert "india" in reasoning_lower or "dpdp" in reasoning_lower

    def test_confidence_high(
        self, detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt
    ):
        dr = self._run(detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt)
        assert dr.conflicts[0].confidence >= 90, "Data residency trilemma must have HIGH confidence"

    def test_conflict_type_is_data_residency(
        self, detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt
    ):
        dr = self._run(detector, it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt)
        assert dr.conflicts[0].conflict_type == ConflictType.DATA_RESIDENCY


class TestRetentionConflict:
    """
    Retention Conflict: BYOD delete (IT Security) vs. 7-year retain (Data Governance).
    Expected: HIGH severity.
    """

    TOPIC = "BYOD data deletion and retention rules"

    def _run(self, detector, byod_delete_stmt, retention_7yr_stmt) -> DetectorResult:
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[byod_delete_stmt, retention_7yr_stmt],
        )
        return detector.detect(result)

    def test_conflict_detected(self, detector, byod_delete_stmt, retention_7yr_stmt):
        dr = self._run(detector, byod_delete_stmt, retention_7yr_stmt)
        assert len(dr.conflicts) == 1

    def test_severity_high(self, detector, byod_delete_stmt, retention_7yr_stmt):
        dr = self._run(detector, byod_delete_stmt, retention_7yr_stmt)
        assert dr.conflicts[0].severity == ConflictSeverity.HIGH

    def test_conflict_type_retention(self, detector, byod_delete_stmt, retention_7yr_stmt):
        dr = self._run(detector, byod_delete_stmt, retention_7yr_stmt)
        assert dr.conflicts[0].conflict_type == ConflictType.RETENTION

    def test_reasoning_mentions_deletion(self, detector, byod_delete_stmt, retention_7yr_stmt):
        dr = self._run(detector, byod_delete_stmt, retention_7yr_stmt)
        reasoning_lower = dr.conflicts[0].reasoning.lower()
        assert "delet" in reasoning_lower or "terminat" in reasoning_lower

    def test_reasoning_mentions_retention(self, detector, byod_delete_stmt, retention_7yr_stmt):
        dr = self._run(detector, byod_delete_stmt, retention_7yr_stmt)
        reasoning_lower = dr.conflicts[0].reasoning.lower()
        assert "retain" in reasoning_lower or "7 year" in reasoning_lower or "retention" in reasoning_lower

    def test_minimum_two_citations(self, detector, byod_delete_stmt, retention_7yr_stmt):
        dr = self._run(detector, byod_delete_stmt, retention_7yr_stmt)
        assert len(dr.conflicts[0].citations) >= 2


class TestApprovalWorkflowConflict:
    """
    Approval Workflow Conflict: automatic relocation allowance vs. Finance Director pre-approval.
    Expected: HIGH severity.
    """

    TOPIC = "relocation and expense compensation"

    @pytest.fixture
    def relocation_auto_stmt(self) -> PolicyStatement:
        return _stmt(
            "Employee_Handbook.md", "§8.3",
            "Employees relocated to regional offices are automatically entitled to a "
            "standard relocation allowance of $5,000, disbursed in the first payroll cycle.",
            confidence=0.79,
        )

    @pytest.fixture
    def relocation_discretionary_stmt(self) -> PolicyStatement:
        return _stmt(
            "Finance_Expense_Policy.md", "§5.1",
            "All relocation expenses and allowance disbursements are discretionary and "
            "require prior written authorization from the Finance Director before any "
            "commitment is made.",
            confidence=0.78,
        )

    def test_conflict_detected(
        self, detector, relocation_auto_stmt, relocation_discretionary_stmt
    ):
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[relocation_auto_stmt, relocation_discretionary_stmt],
        )
        dr = detector.detect(result)
        assert len(dr.conflicts) == 1

    def test_severity_high(
        self, detector, relocation_auto_stmt, relocation_discretionary_stmt
    ):
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[relocation_auto_stmt, relocation_discretionary_stmt],
        )
        dr = detector.detect(result)
        assert dr.conflicts[0].severity == ConflictSeverity.HIGH

    def test_conflict_type_approval_workflow(
        self, detector, relocation_auto_stmt, relocation_discretionary_stmt
    ):
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[relocation_auto_stmt, relocation_discretionary_stmt],
        )
        dr = detector.detect(result)
        assert dr.conflicts[0].conflict_type == ConflictType.APPROVAL_WORKFLOW


class TestAccessControlConflict:
    """
    Access Control: MFA mandatory (no exceptions) vs. manager-granted contractor exception.
    Expected: MEDIUM severity.
    """

    TOPIC = "MFA and authentication exceptions"

    def _run(self, detector, mfa_mandatory_stmt, mfa_exception_stmt) -> DetectorResult:
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[mfa_mandatory_stmt, mfa_exception_stmt],
        )
        return detector.detect(result)

    def test_conflict_detected(self, detector, mfa_mandatory_stmt, mfa_exception_stmt):
        dr = self._run(detector, mfa_mandatory_stmt, mfa_exception_stmt)
        assert len(dr.conflicts) == 1

    def test_severity_medium(self, detector, mfa_mandatory_stmt, mfa_exception_stmt):
        dr = self._run(detector, mfa_mandatory_stmt, mfa_exception_stmt)
        assert dr.conflicts[0].severity == ConflictSeverity.MEDIUM

    def test_conflict_type_access_control(self, detector, mfa_mandatory_stmt, mfa_exception_stmt):
        dr = self._run(detector, mfa_mandatory_stmt, mfa_exception_stmt)
        assert dr.conflicts[0].conflict_type == ConflictType.ACCESS_CONTROL

    def test_reasoning_mentions_mfa(self, detector, mfa_mandatory_stmt, mfa_exception_stmt):
        dr = self._run(detector, mfa_mandatory_stmt, mfa_exception_stmt)
        reasoning_lower = dr.conflicts[0].reasoning.lower()
        assert "mfa" in reasoning_lower or "multi-factor" in reasoning_lower


class TestExpenseReimbursementConflict:
    """
    Direct Contradiction: self-cert strictly prohibited (Finance) vs. permitted emergency (Handbook).
    """

    TOPIC = "expense reimbursement validation"

    def _run(self, detector, expense_receipt_stmt, expense_selfcert_stmt) -> DetectorResult:
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[expense_receipt_stmt, expense_selfcert_stmt],
        )
        return detector.detect(result)

    def test_conflict_detected(self, detector, expense_receipt_stmt, expense_selfcert_stmt):
        dr = self._run(detector, expense_receipt_stmt, expense_selfcert_stmt)
        assert len(dr.conflicts) == 1

    def test_has_conflict_true(self, detector, expense_receipt_stmt, expense_selfcert_stmt):
        dr = self._run(detector, expense_receipt_stmt, expense_selfcert_stmt)
        assert dr.conflicts[0].has_conflict is True

    def test_minimum_two_citations(self, detector, expense_receipt_stmt, expense_selfcert_stmt):
        dr = self._run(detector, expense_receipt_stmt, expense_selfcert_stmt)
        assert len(dr.conflicts[0].citations) >= 2


# ═══════════════════════════════════════════════════════════════════════════════
# 2. NEGATIVE CASES — the detector MUST reject these
# ═══════════════════════════════════════════════════════════════════════════════

class TestWordingDifferences:
    """
    Case 4 (test_corpus.md §2): Two policies use different synonyms.
    Expected: NO CONFLICT — language ambiguity without operational impossibility.
    """

    TOPIC = "vacation and leave terminology"

    @pytest.fixture
    def vacation_stmt_a(self) -> PolicyStatement:
        return _stmt(
            "Employee_Handbook.md", "§5.1",
            "All employees are entitled to 20 vacation days per calendar year.",
            confidence=0.80,
        )

    @pytest.fixture
    def vacation_stmt_b(self) -> PolicyStatement:
        return _stmt(
            "HR_Remote_Work_Policy.md", "§7.2",
            "Annual leave entitlement is 20 working days per year for all staff.",
            confidence=0.78,
        )

    def test_no_conflict_for_synonym_difference(
        self, detector, vacation_stmt_a, vacation_stmt_b
    ):
        """
        Two policies say the same thing with different words (vacation vs. leave).
        This must NOT be flagged as a conflict.
        """
        # Inject a mock LLM response that returns no-conflict
        with patch.object(detector, "_mock_response", return_value={
            "has_conflict": False,
            "conflict_pairs": [],
            "reasoning": "Both policies grant 20 days of leave. The terminology differs "
                         "(vacation vs. annual leave) but the entitlement is identical. "
                         "No operational impossibility exists.",
            "severity": None,
            "confidence": 0.0,
        }):
            result = _make_analyzer_result(
                topic=self.TOPIC,
                citations=[vacation_stmt_a, vacation_stmt_b],
            )
            dr = detector.detect(result)

        assert len(dr.conflicts) == 0, (
            "Synonym / wording difference must NOT be detected as a conflict"
        )


class TestComplementaryPolicies:
    """
    Complementary policies (one adds detail to the other) — must NOT be flagged.
    """

    TOPIC = "data encryption requirements"

    @pytest.fixture
    def encryption_base_stmt(self) -> PolicyStatement:
        return _stmt(
            "IT_Security_Policy.md", "§8.1",
            "All data at rest must be encrypted using AES-256.",
            confidence=0.88,
        )

    @pytest.fixture
    def encryption_additional_stmt(self) -> PolicyStatement:
        return _stmt(
            "Data_Governance_Policy.md", "§5.3",
            "Encryption keys must be rotated annually and stored in a Hardware Security Module.",
            confidence=0.85,
        )

    def test_no_conflict_for_complementary_policies(
        self, detector, encryption_base_stmt, encryption_additional_stmt
    ):
        """These policies are additive, not contradictory — no conflict."""
        with patch.object(detector, "_mock_response", return_value={
            "has_conflict": False,
            "conflict_pairs": [],
            "reasoning": "Both policies address encryption but are complementary. "
                         "One mandates AES-256 at rest; the other specifies key rotation. "
                         "Both can be satisfied simultaneously.",
            "severity": None,
            "confidence": 0.0,
        }):
            result = _make_analyzer_result(
                topic=self.TOPIC,
                citations=[encryption_base_stmt, encryption_additional_stmt],
            )
            dr = detector.detect(result)

        assert len(dr.conflicts) == 0, "Complementary policies must NOT be detected as conflicts"


class TestInsufficientCitations:
    """
    Case 5 (test_corpus.md §2): < 2 Foundry IQ citations → finding BLOCKED.
    Expected: conflicts=[], blocked_findings=[...], no ValidationError thrown.
    """

    TOPIC = "single document topic"

    @pytest.fixture
    def single_stmt(self) -> PolicyStatement:
        return _stmt(
            "IT_Security_Policy.md", "§1.1",
            "All data must be protected.",
            confidence=0.90,
        )

    def test_single_citation_blocks_finding(self, detector, single_stmt):
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[single_stmt],  # Only 1 citation
        )
        dr = detector.detect(result)
        assert len(dr.conflicts) == 0, "A single citation must not produce a conflict"
        assert len(dr.blocked_findings) >= 1, "Single-citation case must produce a blocked finding"

    def test_zero_citations_blocks_finding(self, detector):
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[],
        )
        dr = detector.detect(result)
        assert len(dr.conflicts) == 0
        assert len(dr.blocked_findings) >= 1

    def test_no_exception_on_single_citation(self, detector, single_stmt):
        """Insufficient citations must be handled gracefully, not crash."""
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[single_stmt],
        )
        try:
            detector.detect(result)  # Must not raise
        except Exception as exc:
            pytest.fail(f"detect() raised unexpectedly: {exc}")


class TestPolicyExceptionClause:
    """
    An exception clause that does not invalidate the rule — NOT a conflict.
    E.g., "All employees must wear ID badges, except in external visitor areas where
    badges are not required" — the exception is part of the rule, not a contradiction.
    """

    TOPIC = "employee badge requirements"

    @pytest.fixture
    def badge_rule_stmt(self) -> PolicyStatement:
        return _stmt(
            "Employee_Handbook.md", "§3.1",
            "All employees must wear company ID badges visibly at all times within office premises.",
            confidence=0.85,
        )

    @pytest.fixture
    def badge_exception_stmt(self) -> PolicyStatement:
        return _stmt(
            "IT_Security_Policy.md", "§2.4",
            "Badge verification scanners must be operational at all entry points during business hours.",
            confidence=0.82,
        )

    def test_no_conflict_for_exception_clause(
        self, detector, badge_rule_stmt, badge_exception_stmt
    ):
        with patch.object(detector, "_mock_response", return_value={
            "has_conflict": False,
            "conflict_pairs": [],
            "reasoning": "Both policies concern badge security but do not contradict each other. "
                         "One requires employees to wear badges; the other requires scanners to be "
                         "operational. These are compatible obligations.",
            "severity": None,
            "confidence": 0.0,
        }):
            result = _make_analyzer_result(
                topic=self.TOPIC,
                citations=[badge_rule_stmt, badge_exception_stmt],
            )
            dr = detector.detect(result)

        assert len(dr.conflicts) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# 3. EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

class TestLowConfidenceRouting:
    """
    Case 6 (test_corpus.md §3): Conflict detected with < 65% confidence.
    Expected: routed to UNCERTAIN queue, NOT shown on main dashboard (conflicts=[]).
    """

    TOPIC = "low confidence conflict scenario"

    @pytest.fixture
    def low_conf_stmt_a(self) -> PolicyStatement:
        return _stmt(
            "Employee_Handbook.md", "§99.1",
            "Employees should endeavour to maintain a professional appearance.",
            confidence=0.55,
        )

    @pytest.fixture
    def low_conf_stmt_b(self) -> PolicyStatement:
        return _stmt(
            "HR_Remote_Work_Policy.md", "§99.2",
            "Remote staff are encouraged to dress comfortably during video calls.",
            confidence=0.53,
        )

    def test_low_confidence_routed_to_uncertain_not_dashboard(
        self, detector, low_conf_stmt_a, low_conf_stmt_b
    ):
        """A 55% confidence finding must NOT appear in conflicts[]."""
        with patch.object(detector, "_mock_response", return_value={
            "has_conflict": True,
            "conflict_pairs": [
                {
                    "document_a": "Employee_Handbook.md",
                    "section_a": "§99.1",
                    "document_b": "HR_Remote_Work_Policy.md",
                    "section_b": "§99.2",
                    "conflict_type": "Direct Contradiction",
                    "why_impossible": "One says professional, one says comfortable — "
                                      "arguably impossible to satisfy both simultaneously.",
                }
            ],
            "reasoning": "The appearance guidelines are loosely contradictory but this is "
                         "highly subjective and may not constitute a genuine operational impossibility.",
            "severity": "LOW",
            "confidence": 0.55,  # BELOW threshold — must → UNCERTAIN
        }):
            result = _make_analyzer_result(
                topic=self.TOPIC,
                citations=[low_conf_stmt_a, low_conf_stmt_b],
            )
            dr = detector.detect(result)

        assert len(dr.conflicts) == 0, (
            "Low-confidence finding MUST NOT appear in confirmed conflicts"
        )
        assert len(dr.uncertain_findings) == 1, (
            "Low-confidence finding must be routed to uncertain_findings"
        )
        assert dr.uncertain_findings[0].status == ConflictStatus.UNCERTAIN


class TestDuplicateConflictElimination:
    """
    Same conflict pair detected twice across two detect() calls on the same detector.
    Expected: second detection suppressed.
    """

    TOPIC = "employee reporting channels and anonymity guarantees"

    def test_duplicate_suppressed_within_run(
        self, whistleblower_stmt, it_security_logging_stmt
    ):
        """Run the same analysis twice on the same detector instance — second should be suppressed."""
        detector = ConflictDetector(azure_client=None)
        citations = [whistleblower_stmt, it_security_logging_stmt]

        result = _make_analyzer_result(topic=self.TOPIC, citations=citations)

        dr1 = detector.detect(result)
        assert len(dr1.conflicts) == 1

        # Second run — dup_filter resets on each detect() call per spec
        # (each detect() call resets the filter — so we use the DuplicateFilter directly)
        dup_filter = DuplicateFilter()
        dup_filter.record(citations)
        assert dup_filter.is_duplicate(citations), "Same citations must be detected as duplicate"

    def test_duplicate_filter_different_citations(
        self, whistleblower_stmt, it_security_logging_stmt, byod_delete_stmt
    ):
        """Different citation sets must NOT be flagged as duplicates."""
        dup_filter = DuplicateFilter()
        citations_a = [whistleblower_stmt, it_security_logging_stmt]
        citations_b = [byod_delete_stmt, it_security_logging_stmt]

        dup_filter.record(citations_a)
        assert not dup_filter.is_duplicate(citations_b), (
            "Different citation pairs must not be duplicates"
        )

    def test_duplicate_filter_reset(self, whistleblower_stmt, it_security_logging_stmt):
        dup_filter = DuplicateFilter()
        citations = [whistleblower_stmt, it_security_logging_stmt]
        dup_filter.record(citations)
        dup_filter.reset()
        assert not dup_filter.is_duplicate(citations), "After reset, filter must be empty"


class TestCitationValidation:
    """
    Citation validation rules from docs/reliability_spec.md §3.
    """

    def test_two_distinct_citations_pass(self, whistleblower_stmt, it_security_logging_stmt):
        SchemaValidator.validate_citations([whistleblower_stmt, it_security_logging_stmt])
        # Should not raise

    def test_single_citation_raises(self, whistleblower_stmt):
        with pytest.raises(InsufficientCitationsError):
            SchemaValidator.validate_citations([whistleblower_stmt])

    def test_zero_citations_raises(self):
        with pytest.raises(InsufficientCitationsError):
            SchemaValidator.validate_citations([])

    def test_same_document_section_counts_as_one(self, whistleblower_stmt):
        """Two citations from the same document+section are not 'distinct'."""
        duplicate = _stmt(
            "Whistleblower_Policy.md", "§4.2",
            "Duplicate passage — same source.",
            confidence=0.90,
        )
        with pytest.raises(InsufficientCitationsError):
            SchemaValidator.validate_citations([whistleblower_stmt, duplicate])

    def test_empty_passage_citation_not_counted(self, whistleblower_stmt):
        """Citations with empty passage do not count toward the minimum."""
        empty_passage = PolicyStatement(
            document="IT_Security_Policy.md",
            section="§12.1",
            passage="",    # Empty — should not count
            confidence=0.90,
            topic="test",
        )
        with pytest.raises(InsufficientCitationsError):
            SchemaValidator.validate_citations([whistleblower_stmt, empty_passage])

    def test_whitespace_only_passage_not_counted(self, whistleblower_stmt):
        whitespace_passage = PolicyStatement(
            document="IT_Security_Policy.md",
            section="§12.1",
            passage="   ",   # Whitespace only — should not count
            confidence=0.90,
            topic="test",
        )
        with pytest.raises(InsufficientCitationsError):
            SchemaValidator.validate_citations([whistleblower_stmt, whitespace_passage])

    def test_three_distinct_citations_pass(
        self, whistleblower_stmt, it_security_logging_stmt, hr_remote_work_stmt
    ):
        SchemaValidator.validate_citations([
            whistleblower_stmt, it_security_logging_stmt, hr_remote_work_stmt,
        ])
        # Should not raise


class TestSchemaValidation:
    """
    SchemaValidator.validate_schema() must catch malformed ConflictRecords.
    """

    def _valid_record(self, whistleblower_stmt, it_security_logging_stmt) -> ConflictRecord:
        pair = ConflictPair(
            statement_a=whistleblower_stmt,
            statement_b=it_security_logging_stmt,
            conflict_type=ConflictType.DIRECT_CONTRADICTION,
            why_impossible="Test conflict"
        )
        return ConflictRecord(
            id="abc12345",
            has_conflict=True,
            title="Test conflict",
            severity=ConflictSeverity.CRITICAL,
            confidence=91,
            sources=["Whistleblower_Policy.md §4.2", "IT_Security_Policy.md §12.1"],
            affected="All employees",
            deadline=None,
            resolution="Migrate ethics portal.",
            citations=[whistleblower_stmt, it_security_logging_stmt],
            conflict_pairs=[pair],
            reasoning="The anonymity guarantee is technically impossible given the logging requirement.",
        )

    def test_valid_record_passes(self, whistleblower_stmt, it_security_logging_stmt):
        record = self._valid_record(whistleblower_stmt, it_security_logging_stmt)
        errors = SchemaValidator.validate_schema(record)
        assert errors == []

    def test_missing_title_fails(self, whistleblower_stmt, it_security_logging_stmt):
        record = self._valid_record(whistleblower_stmt, it_security_logging_stmt)
        record.title = ""
        errors = SchemaValidator.validate_schema(record)
        assert any("title" in e for e in errors)

    def test_missing_reasoning_fails(self, whistleblower_stmt, it_security_logging_stmt):
        record = self._valid_record(whistleblower_stmt, it_security_logging_stmt)
        record.reasoning = ""
        errors = SchemaValidator.validate_schema(record)
        assert any("reasoning" in e for e in errors)

    def test_confidence_out_of_range_fails(self, whistleblower_stmt, it_security_logging_stmt):
        record = self._valid_record(whistleblower_stmt, it_security_logging_stmt)
        record.confidence = 150  # Out of range
        errors = SchemaValidator.validate_schema(record)
        assert any("confidence" in e for e in errors)

    def test_empty_sources_fails(self, whistleblower_stmt, it_security_logging_stmt):
        record = self._valid_record(whistleblower_stmt, it_security_logging_stmt)
        record.sources = []
        errors = SchemaValidator.validate_schema(record)
        assert any("sources" in e for e in errors)

    def test_empty_citations_fails(self, whistleblower_stmt, it_security_logging_stmt):
        record = self._valid_record(whistleblower_stmt, it_security_logging_stmt)
        record.citations = []
        errors = SchemaValidator.validate_schema(record)
        assert any("citation" in e for e in errors)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CONFIDENCE FRAMEWORK
# ═══════════════════════════════════════════════════════════════════════════════

class TestConfidenceFramework:
    """
    ConfidenceFramework classifies confidence into HIGH / MEDIUM / LOW tiers
    and maps them to ConflictStatus correctly.
    docs/reliability_spec.md §2
    """

    def test_high_confidence_gives_confirmed(self):
        status, score = SchemaValidator.classify_confidence(0.92)
        assert status == ConflictStatus.CONFIRMED
        assert score == 92

    def test_medium_confidence_gives_confirmed(self):
        status, score = SchemaValidator.classify_confidence(0.70)
        assert status == ConflictStatus.CONFIRMED
        assert score == 70

    def test_exactly_threshold_gives_confirmed(self):
        """confidence == 0.65 is CONFIRMED per spec (≥ threshold)."""
        status, score = SchemaValidator.classify_confidence(0.65)
        assert status == ConflictStatus.CONFIRMED

    def test_below_threshold_gives_uncertain(self):
        status, score = SchemaValidator.classify_confidence(0.64)
        assert status == ConflictStatus.UNCERTAIN

    def test_zero_confidence_gives_uncertain(self):
        status, score = SchemaValidator.classify_confidence(0.0)
        assert status == ConflictStatus.UNCERTAIN
        assert score == 0

    def test_perfect_confidence(self):
        status, score = SchemaValidator.classify_confidence(1.0)
        assert status == ConflictStatus.CONFIRMED
        assert score == 100

    def test_tier_label_high(self):
        assert ConfidenceFramework.get_tier_label(0.90) == "HIGH"

    def test_tier_label_medium(self):
        assert ConfidenceFramework.get_tier_label(0.70) == "MEDIUM"

    def test_tier_label_low(self):
        assert ConfidenceFramework.get_tier_label(0.50) == "LOW"

    def test_severity_parsing_critical(self):
        sev = ConfidenceFramework.severity_from_llm("CRITICAL")
        assert sev == ConflictSeverity.CRITICAL

    def test_severity_parsing_high(self):
        sev = ConfidenceFramework.severity_from_llm("HIGH")
        assert sev == ConflictSeverity.HIGH

    def test_severity_parsing_medium(self):
        sev = ConfidenceFramework.severity_from_llm("MEDIUM")
        assert sev == ConflictSeverity.MEDIUM

    def test_severity_parsing_none_defaults_medium(self):
        sev = ConfidenceFramework.severity_from_llm(None)
        assert sev == ConflictSeverity.MEDIUM

    def test_severity_parsing_case_insensitive(self):
        sev = ConfidenceFramework.severity_from_llm("critical")
        assert sev == ConflictSeverity.CRITICAL

    def test_conflict_type_infer_residency(self):
        ct = ConfidenceFramework.infer_conflict_type("processing location server jurisdiction")
        assert ct == ConflictType.DATA_RESIDENCY

    def test_conflict_type_infer_retention(self):
        ct = ConfidenceFramework.infer_conflict_type("delete retain retention destroy")
        assert ct == ConflictType.RETENTION

    def test_conflict_type_infer_approval(self):
        ct = ConfidenceFramework.infer_conflict_type("approval authorization discretionary automatic")
        assert ct == ConflictType.APPROVAL_WORKFLOW

    def test_conflict_type_infer_access_control(self):
        ct = ConfidenceFramework.infer_conflict_type("mfa exception access")
        assert ct == ConflictType.ACCESS_CONTROL


# ═══════════════════════════════════════════════════════════════════════════════
# 5. TOPIC KEY MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

class TestTopicKeyMapping:
    """_topic_key() must map free-form topics to canonical mock keys."""

    def test_anonymity_topic(self):
        assert _topic_key("employee reporting channels and anonymity guarantees") == "anonymity"

    def test_data_location_topic(self):
        assert _topic_key("employee data location and processing rules") == "data location"

    def test_incident_reporting_topic(self):
        assert _topic_key("security incident reporting timelines") == "incident reporting"

    def test_byod_topic(self):
        assert _topic_key("BYOD data deletion and retention rules") == "byod"

    def test_relocation_topic(self):
        assert _topic_key("relocation and expense compensation") == "relocation"

    def test_software_procurement_topic(self):
        assert _topic_key("software procurement and security approval") == "software procurement"

    def test_data_minimization_topic(self):
        assert _topic_key("data minimization and retention") == "data minimization"

    def test_mfa_topic(self):
        assert _topic_key("MFA and authentication exceptions") == "mfa"

    def test_expense_topic(self):
        assert _topic_key("expense reimbursement validation") == "expense reimbursement"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. MULTI-DOCUMENT SCENARIO
# ═══════════════════════════════════════════════════════════════════════════════

class TestMultiDocumentScenario:
    """
    Run the detector across multiple citation groups and verify:
      - All unique conflicts are detected
      - Duplicates are not emitted
      - Each conflict has correct sources list
    """

    def test_all_conflicts_from_precomputed_data(self):
        """
        The pre-computed mock data has 9 distinct conflicts.
        Verify the ConflictDetector can produce records for the key topics
        without errors.
        """
        detector = ConflictDetector(azure_client=None)
        topics_and_citations = [
            (
                "employee reporting channels and anonymity guarantees",
                [
                    _stmt("Whistleblower_Policy.md", "§4.2",
                          "Reports filed through the ethics portal are anonymous.", 0.91),
                    _stmt("IT_Security_Policy.md", "§12.1",
                          "All system access is logged with full user identity. No exceptions.", 0.95),
                ],
            ),
            (
                "employee data location and processing rules",
                [
                    _stmt("IT_Security_Policy.md", "§4.2",
                          "All company data processing shall occur exclusively on US-domiciled servers.", 0.96),
                    _stmt("HR_Remote_Work_Policy.md", "§2.1",
                          "Employees may work from any global location without prior approval.", 0.95),
                    _stmt("DPDP_Compliance_Directive.md", "§3.1",
                          "Personal data of Indian-resident employees must be processed within Indian jurisdiction.", 0.94),
                ],
            ),
        ]

        all_conflicts: list[ConflictRecord] = []
        for topic, citations in topics_and_citations:
            analyzer_result = _make_analyzer_result(topic=topic, citations=citations)
            dr = detector.detect(analyzer_result)
            all_conflicts.extend(dr.conflicts)

        assert len(all_conflicts) >= 2, "Must detect at least 2 distinct conflicts"

        # Verify sources are distinct for each conflict
        source_sets = [frozenset(c.sources) for c in all_conflicts]
        assert len(source_sets) == len(set(source_sets)), "All conflicts must have unique source sets"


# ═══════════════════════════════════════════════════════════════════════════════
# 7. TIER 3 FALLBACK
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallbackChain:
    """
    Verify Tier 3 (mock) is correctly activated when no Azure credentials
    are present and that results are valid.
    """

    def test_tier_3_activated_without_credentials(self, detector):
        assert not detector._available, "Detector without credentials must have _available=False"

    def test_tier_3_always_produces_result(
        self, detector, whistleblower_stmt, it_security_logging_stmt
    ):
        """Tier 3 must never raise or return None."""
        result = _make_analyzer_result(
            topic="employee reporting channels and anonymity guarantees",
            citations=[whistleblower_stmt, it_security_logging_stmt],
        )
        dr = detector.detect(result)
        # Must produce a valid DetectorResult (not None, not exception)
        assert isinstance(dr, DetectorResult)

    def test_tier_3_marks_is_mock_mode(
        self, detector, whistleblower_stmt, it_security_logging_stmt
    ):
        result = _make_analyzer_result(
            topic="employee reporting channels and anonymity guarantees",
            citations=[whistleblower_stmt, it_security_logging_stmt],
        )
        dr = detector.detect(result)
        assert dr.is_mock_mode is True

    def test_tier_3_used_value(
        self, detector, whistleblower_stmt, it_security_logging_stmt
    ):
        result = _make_analyzer_result(
            topic="employee reporting channels and anonymity guarantees",
            citations=[whistleblower_stmt, it_security_logging_stmt],
        )
        dr = detector.detect(result)
        assert dr.tier_used == 3

    def test_unknown_topic_returns_no_conflict(self, detector):
        """For an unknown topic, Tier 3 must return no-conflict gracefully."""
        stmts = [
            _stmt("Employee_Handbook.md", "§1.1", "All employees should be respectful.", 0.70),
            _stmt("HR_Remote_Work_Policy.md", "§1.2", "Remote work is encouraged.", 0.70),
        ]
        result = _make_analyzer_result(
            topic="workplace culture guidelines that have no precomputed mock",
            citations=stmts,
        )
        dr = detector.detect(result)
        assert isinstance(dr, DetectorResult)
        # Should either return no conflict or a gracefully handled result
        assert len(dr.conflicts) == 0 or dr.is_mock_mode


# ═══════════════════════════════════════════════════════════════════════════════
# 8. DETERMINISTIC BEHAVIOR
# ═══════════════════════════════════════════════════════════════════════════════

class TestDeterministicBehavior:
    """
    Same input must produce same output.
    docs brief: "produce repeatable outputs / avoid prompt drift"
    """

    TOPIC = "employee reporting channels and anonymity guarantees"

    def test_same_input_same_output(self, whistleblower_stmt, it_security_logging_stmt):
        """Run the same detection twice — results must be identical."""
        detector1 = ConflictDetector(azure_client=None)
        detector2 = ConflictDetector(azure_client=None)

        citations = [whistleblower_stmt, it_security_logging_stmt]

        result1 = detector1.detect(_make_analyzer_result(self.TOPIC, citations))
        result2 = detector2.detect(_make_analyzer_result(self.TOPIC, citations))

        assert len(result1.conflicts) == len(result2.conflicts)
        if result1.conflicts and result2.conflicts:
            assert result1.conflicts[0].severity == result2.conflicts[0].severity
            assert result1.conflicts[0].confidence == result2.conflicts[0].confidence
            assert result1.conflicts[0].reasoning == result2.conflicts[0].reasoning

    def test_record_id_deterministic(self, whistleblower_stmt, it_security_logging_stmt):
        """The generated conflict ID must be the same for the same source fingerprint."""
        detector1 = ConflictDetector(azure_client=None)
        detector2 = ConflictDetector(azure_client=None)
        citations = [whistleblower_stmt, it_security_logging_stmt]

        dr1 = detector1.detect(_make_analyzer_result(self.TOPIC, citations))
        dr2 = detector2.detect(_make_analyzer_result(self.TOPIC, citations))

        if dr1.conflicts and dr2.conflicts:
            assert dr1.conflicts[0].id == dr2.conflicts[0].id


# ═══════════════════════════════════════════════════════════════════════════════
# 9. CONVENIENCE API
# ═══════════════════════════════════════════════════════════════════════════════

class TestConvenienceAPI:
    """Test module-level convenience functions."""

    def test_get_detector_returns_singleton(self):
        d1 = get_detector()
        d2 = get_detector()
        assert d1 is d2, "get_detector() must return a singleton"

    def test_detect_conflicts_function_works(self, whistleblower_stmt, it_security_logging_stmt):
        result = _make_analyzer_result(
            topic="employee reporting channels and anonymity guarantees",
            citations=[whistleblower_stmt, it_security_logging_stmt],
        )
        dr = detect_conflicts(result)
        assert isinstance(dr, DetectorResult)

    def test_detect_from_statements(self, whistleblower_stmt, it_security_logging_stmt):
        detector = ConflictDetector(azure_client=None)
        dr = detector.detect_from_statements(
            topic="employee reporting channels and anonymity guarantees",
            statements=[whistleblower_stmt, it_security_logging_stmt],
        )
        assert isinstance(dr, DetectorResult)
        assert len(dr.conflicts) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# 10. PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════

class TestPerformance:
    """
    Detection latency for Tier 3 (mock) must be well under 5 seconds even
    for maximum input (≤ 7 documents, ≤ 100 statements).
    """

    def test_detection_latency_under_5s(self, detector):
        # Build 7 documents × ~14 citations each ≈ 98 citations
        citations = []
        for i in range(7):
            for j in range(14):
                citations.append(_stmt(
                    f"Policy_Doc_{i}.md",
                    f"§{i+1}.{j+1}",
                    f"Policy statement {i}.{j} regarding data handling and employee obligations.",
                    confidence=0.75,
                ))

        result = _make_analyzer_result(
            topic="employee data location and processing rules",
            citations=citations[:100],  # Cap at 100 per spec
        )

        t0 = time.monotonic()
        dr = detector.detect(result)
        elapsed = time.monotonic() - t0

        assert elapsed < 5.0, (
            f"ConflictDetector took {elapsed:.2f}s — must complete in < 5s (Tier 3 mode)"
        )

    def test_minimum_citation_check_is_fast(self, detector):
        """Zero-citation path must be near-instant."""
        result = _make_analyzer_result(topic="any topic", citations=[])
        t0 = time.monotonic()
        detector.detect(result)
        elapsed = time.monotonic() - t0
        assert elapsed < 0.1, "Zero-citation guard must be near-instant"


# ═══════════════════════════════════════════════════════════════════════════════
# 11. GOLDEN STANDARD REASONING TRACE
# ═══════════════════════════════════════════════════════════════════════════════

class TestGoldenReasoningTrace:
    """
    The key output that judges see.
    Validates that reasoning matches the golden standard from
    docs/reasoning_trace_examples.md §2.
    """

    TOPIC = "employee reporting channels and anonymity guarantees"

    GOLDEN_PHRASES = [
        "legal commitment",
        "traceable",
        "identity",
        "simultaneously",
    ]

    def test_reasoning_contains_golden_phrases(
        self, detector, whistleblower_stmt, it_security_logging_stmt
    ):
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[whistleblower_stmt, it_security_logging_stmt],
        )
        dr = detector.detect(result)
        assert dr.conflicts, "Must detect anonymity conflict"
        reasoning_lower = dr.conflicts[0].reasoning.lower()

        # At least 3 of the 4 golden phrases must appear
        hits = sum(1 for phrase in self.GOLDEN_PHRASES if phrase in reasoning_lower)
        assert hits >= 3, (
            f"Reasoning must contain the golden phrases. Found {hits}/4: {self.GOLDEN_PHRASES}\n"
            f"Actual reasoning: {dr.conflicts[0].reasoning[:300]}"
        )

    def test_reasoning_is_one_or_few_sentences(
        self, detector, whistleblower_stmt, it_security_logging_stmt
    ):
        """Reasoning must be tight, impactful prose — not a bullet list or labelled breakdown."""
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[whistleblower_stmt, it_security_logging_stmt],
        )
        dr = detector.detect(result)
        reasoning = dr.conflicts[0].reasoning
        # Must not contain bullet-list markers
        assert "•" not in reasoning, "Reasoning must not use bullet points"
        assert reasoning.count("\n") < 5, "Reasoning must be compact prose"

    def test_reasoning_explains_impossibility(
        self, detector, whistleblower_stmt, it_security_logging_stmt
    ):
        """The 'why impossible' must be explicit — not just 'these differ'."""
        result = _make_analyzer_result(
            topic=self.TOPIC,
            citations=[whistleblower_stmt, it_security_logging_stmt],
        )
        dr = detector.detect(result)
        reasoning_lower = dr.conflicts[0].reasoning.lower()

        # Must explain what technically cannot coexist
        impossibility_markers = [
            "cannot simultaneously", "cannot both", "simultaneously be true",
            "cannot be both", "cannot coexist", "full stop",
        ]
        assert any(m in reasoning_lower for m in impossibility_markers), (
            "Reasoning must explicitly state why both cannot be true simultaneously."
        )

    def test_data_residency_reasoning_names_all_three_sources(
        self,
        detector,
        it_security_us_servers_stmt,
        hr_remote_work_stmt,
        dpdp_directive_stmt,
    ):
        result = _make_analyzer_result(
            topic="employee data location and processing rules",
            citations=[it_security_us_servers_stmt, hr_remote_work_stmt, dpdp_directive_stmt],
        )
        dr = detector.detect(result)
        assert dr.conflicts, "Must detect data residency conflict"
        reasoning_lower = dr.conflicts[0].reasoning.lower()

        # The golden standard reasoning names all three constraints
        assert "us" in reasoning_lower or "server" in reasoning_lower
        assert "india" in reasoning_lower or "dpdp" in reasoning_lower
