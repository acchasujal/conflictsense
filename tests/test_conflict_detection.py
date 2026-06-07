"""
tests/test_conflict_detection.py

Unit tests: verify the 3 positive benchmark conflict records are present
and correctly structured in the pre-computed mock data.

Spec reference: docs/test_corpus.md §1, docs/acceptance_criteria.md §1
                docs/data_contracts.md §2

These tests validate that:
  - The mock data contains all 3 required CRITICAL conflicts
  - Each has has_conflict=True, correct severity, ≥2 citations
  - The anonymity conflict has isSurprise=True
  - The data residency conflict has the correct deadline
"""

import json
import pytest
from pathlib import Path

# ─── Load pre-computed data ───────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
CONFLICTS_PATH = ROOT / "mock_data" / "precomputed_conflicts.json"


@pytest.fixture(scope="module")
def conflicts() -> list[dict]:
    with open(CONFLICTS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _find(conflicts: list[dict], conflict_id: str) -> dict:
    """Return the conflict with the given id, or raise."""
    for c in conflicts:
        if c["id"] == conflict_id:
            return c
    raise AssertionError(f"Conflict id={conflict_id!r} not found in mock data")


# ─── Case 1: Anonymity Conflict ───────────────────────────────────────────────
# Sources: Whistleblower_Policy.md vs IT_Security_Policy.md
# Expected: has_conflict=True, severity=CRITICAL, isSurprise=True

class TestAnonymityConflict:
    def test_exists(self, conflicts):
        c = _find(conflicts, "2")
        assert c is not None

    def test_has_conflict_true(self, conflicts):
        c = _find(conflicts, "2")
        assert c["has_conflict"] is True

    def test_severity_critical(self, conflicts):
        c = _find(conflicts, "2")
        assert c["severity"] == "CRITICAL"

    def test_is_surprise(self, conflicts):
        c = _find(conflicts, "2")
        assert c.get("isSurprise") is True, "Anonymity conflict must have isSurprise=True"

    def test_has_two_or_more_citations(self, conflicts):
        c = _find(conflicts, "2")
        assert len(c["citations"]) >= 2, "Must have ≥2 Foundry IQ citations"

    def test_sources_include_whistleblower(self, conflicts):
        c = _find(conflicts, "2")
        sources_str = " ".join(c["sources"])
        assert "Whistleblower_Policy.md" in sources_str

    def test_sources_include_it_security(self, conflicts):
        c = _find(conflicts, "2")
        sources_str = " ".join(c["sources"])
        assert "IT_Security_Policy.md" in sources_str

    def test_confidence_above_threshold(self, conflicts):
        c = _find(conflicts, "2")
        # Per docs/reliability_spec.md §2: HIGH = 85-100%
        assert c["confidence"] >= 85


# ─── Case 2: Data Residency Trilemma ─────────────────────────────────────────
# Sources: IT_Security_Policy.md + HR_Remote_Work_Policy.md + DPDP_Compliance_Directive.md
# Expected: has_conflict=True, severity=CRITICAL, affects 34 India-based employees

class TestDataResidencyTrilemma:
    def test_exists(self, conflicts):
        c = _find(conflicts, "1")
        assert c is not None

    def test_has_conflict_true(self, conflicts):
        c = _find(conflicts, "1")
        assert c["has_conflict"] is True

    def test_severity_critical(self, conflicts):
        c = _find(conflicts, "1")
        assert c["severity"] == "CRITICAL"

    def test_has_three_sources(self, conflicts):
        c = _find(conflicts, "1")
        assert len(c["sources"]) >= 3, "Data residency is a THREE-way conflict"

    def test_sources_include_dpdp(self, conflicts):
        c = _find(conflicts, "1")
        sources_str = " ".join(c["sources"])
        assert "DPDP" in sources_str

    def test_sources_include_hr_remote_work(self, conflicts):
        c = _find(conflicts, "1")
        sources_str = " ".join(c["sources"])
        assert "HR_Remote_Work_Policy.md" in sources_str

    def test_has_deadline(self, conflicts):
        c = _find(conflicts, "1")
        assert c["deadline"] is not None, "Data residency conflict must have a deadline"
        assert "2026" in c["deadline"]

    def test_affected_mentions_india(self, conflicts):
        c = _find(conflicts, "1")
        assert "India" in c["affected"] or "india" in c["affected"].lower()

    def test_has_two_or_more_citations(self, conflicts):
        c = _find(conflicts, "1")
        assert len(c["citations"]) >= 2


# ─── Case 3: Incident Reporting Gap ──────────────────────────────────────────
# Sources: IT_Security_Policy.md §9.1 vs Whistleblower_Policy.md
# Expected: has_conflict=True, severity=CRITICAL, deadline relates to FCA

class TestIncidentReportingGap:
    def test_exists(self, conflicts):
        c = _find(conflicts, "3")
        assert c is not None

    def test_has_conflict_true(self, conflicts):
        c = _find(conflicts, "3")
        assert c["has_conflict"] is True

    def test_severity_critical(self, conflicts):
        c = _find(conflicts, "3")
        assert c["severity"] == "CRITICAL"

    def test_has_two_or_more_citations(self, conflicts):
        c = _find(conflicts, "3")
        assert len(c["citations"]) >= 2

    def test_deadline_mentions_fca(self, conflicts):
        c = _find(conflicts, "3")
        assert c["deadline"] is not None
        assert "FCA" in c["deadline"] or "72" in c["deadline"]


# ─── General schema validation ────────────────────────────────────────────────

class TestConflictSchema:
    REQUIRED_FIELDS = ["id", "has_conflict", "title", "severity", "confidence",
                       "sources", "affected", "resolution", "citations"]
    VALID_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM"}

    def test_total_conflict_count(self, conflicts):
        assert len(conflicts) == 9, "Must have exactly 9 conflicts"

    def test_all_have_required_fields(self, conflicts):
        for c in conflicts:
            for field in self.REQUIRED_FIELDS:
                assert field in c, f"Conflict id={c.get('id')} missing field {field!r}"

    def test_all_severity_valid(self, conflicts):
        for c in conflicts:
            assert c["severity"] in self.VALID_SEVERITIES, \
                f"Conflict id={c.get('id')} has invalid severity {c['severity']!r}"

    def test_all_has_conflict_true(self, conflicts):
        for c in conflicts:
            assert c["has_conflict"] is True, \
                f"Conflict id={c.get('id')} has has_conflict=False — pre-computed conflicts must be True"

    def test_confidence_in_range(self, conflicts):
        for c in conflicts:
            assert 0 <= c["confidence"] <= 100, \
                f"Conflict id={c.get('id')} confidence={c['confidence']} out of range"

    def test_citation_confidence_float(self, conflicts):
        for c in conflicts:
            for cit in c["citations"]:
                assert 0.0 <= cit["confidence"] <= 1.0, \
                    f"Citation confidence must be 0.0–1.0 float, got {cit['confidence']}"

    def test_severity_order(self, conflicts):
        """Critical conflicts must have higher confidence than Medium ones (generally)."""
        crits = [c["confidence"] for c in conflicts if c["severity"] == "CRITICAL"]
        meds  = [c["confidence"] for c in conflicts if c["severity"] == "MEDIUM"]
        if crits and meds:
            assert min(crits) > max(meds) - 30, \
                "CRITICAL confidences should be substantially above MEDIUM"
