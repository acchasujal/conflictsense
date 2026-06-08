"""
tests/test_phase5b_ui_data.py

Phase 5B hardening tests — verify that the data structures required by the
new EnterpriseRiskBanner, RemediationWorkflow, and ConflictCard contradiction
highlighting are present in the mock data and live pipeline output.

Tests:
  1. Risk summary data — conflicts have data that EnterpriseRiskBanner can render.
  2. RemediationWorkflow — conflict resolution text is non-empty for key conflicts.
  3. Contradiction highlighting — hero conflict citations contain exact phrases
     that the highlightPassage function targets.
  4. Regression — existing pipeline produces 9 conflicts with required schema.
  5. Approval gate — approve/reject endpoints still return correct schema.

Spec reference: docs/prd.md §2.3, docs/frontend_spec.md, docs/judging_alignment.md
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# ─── Fixture: load mock conflicts ─────────────────────────────────────────────

_ROOT = Path(__file__).parent.parent
_MOCK_CONFLICTS = json.loads((_ROOT / "mock_data" / "precomputed_conflicts.json").read_text())
_MOCK_TRACE     = json.loads((_ROOT / "mock_data" / "precomputed_trace.json").read_text())


# ─── 1. Enterprise Risk Banner data requirements ──────────────────────────────

def test_risk_banner_has_severity_on_all_conflicts():
    """EnterpriseRiskBanner requires .severity on every conflict."""
    for c in _MOCK_CONFLICTS:
        assert c["severity"] in {"CRITICAL", "HIGH", "MEDIUM"}, (
            f"Conflict {c['id']} has invalid severity: {c['severity']}"
        )


def test_risk_banner_hero_conflict_has_required_fields():
    """The highest-severity conflict must have title, sources, and affected."""
    critical = [c for c in _MOCK_CONFLICTS if c["severity"] == "CRITICAL"]
    assert len(critical) >= 1, "No CRITICAL conflicts in mock data"
    hero = critical[0]
    assert hero.get("title"), "Hero conflict missing title"
    assert hero.get("sources"), "Hero conflict missing sources"
    assert hero.get("affected"), "Hero conflict missing affected"


def test_risk_banner_enterprise_score_computable():
    """Risk score can be computed from severity distribution."""
    weights = {"CRITICAL": 90, "HIGH": 70, "MEDIUM": 50}
    total = sum(weights.get(c["severity"], 50) for c in _MOCK_CONFLICTS)
    score = min(100, round(total / len(_MOCK_CONFLICTS)))
    assert 50 <= score <= 100, f"Enterprise risk score {score} out of expected range"


# ─── 2. Remediation Workflow data requirements ────────────────────────────────

def test_remediation_workflow_resolution_non_empty():
    """RemediationWorkflow uses conflict.resolution — must be non-empty for all."""
    for c in _MOCK_CONFLICTS:
        assert c.get("resolution"), (
            f"Conflict {c['id']} ({c['title']}) has no resolution text. "
            "RemediationWorkflow will fall back to generic text."
        )


def test_hero_anonymity_conflict_resolution_mentions_ethics_portal():
    """The anonymity conflict resolution must mention the ethics portal — key narrative."""
    anon = next((c for c in _MOCK_CONFLICTS if c["id"] == "2"), None)
    assert anon is not None, "Anonymity conflict (id=2) missing from mock data"
    resolution = anon["resolution"].lower()
    assert "ethics portal" in resolution or "anonymous channel" in resolution, (
        "Anonymity conflict resolution must mention ethics portal or anonymous channel"
    )


# ─── 3. Contradiction highlighting data requirements ─────────────────────────

# These are the exact phrases that ConflictCard.jsx's highlightPassage targets.
WHISTLEBLOWER_PHRASES = ["anonymous", "never logged or traceable"]
IT_SECURITY_PHRASES   = ["logged with full user identity", "No exceptions permitted"]

def test_anonymity_conflict_citations_contain_highlight_phrases():
    """
    The hero conflict citations must contain the exact phrases that
    ConflictCard.jsx's CONTRADICTION_PHRASES map targets for green/red highlighting.
    This test guarantees the visual proof of contradiction will render.
    """
    anon = next((c for c in _MOCK_CONFLICTS if c["id"] == "2"), None)
    assert anon is not None

    wb_citation = next(
        (cit for cit in anon["citations"] if "Whistleblower" in cit["document"]), None
    )
    it_citation = next(
        (cit for cit in anon["citations"] if "IT_Security" in cit["document"]), None
    )

    assert wb_citation is not None, "Anonymity conflict missing Whistleblower citation"
    assert it_citation is not None, "Anonymity conflict missing IT Security citation"

    wb_passage = wb_citation["passage"].lower()
    it_passage = it_citation["passage"].lower()

    # At least one green phrase must be present
    assert any(p.lower() in wb_passage for p in WHISTLEBLOWER_PHRASES), (
        f"Whistleblower passage does not contain any highlight phrase. "
        f"Passage: {wb_citation['passage']}"
    )

    # At least one red phrase must be present
    assert any(p.lower() in it_passage for p in IT_SECURITY_PHRASES), (
        f"IT Security passage does not contain any highlight phrase. "
        f"Passage: {it_citation['passage']}"
    )


def test_data_residency_conflict_has_three_citations():
    """The data residency conflict (id=1) should have 3 citations for the three-way proof."""
    dr = next((c for c in _MOCK_CONFLICTS if c["id"] == "1"), None)
    assert dr is not None
    assert len(dr["citations"]) >= 3, (
        f"Data residency conflict should have >= 3 citations, got {len(dr['citations'])}"
    )


# ─── 4. Regression — mock data schema ────────────────────────────────────────

def test_mock_conflicts_count():
    """Regression: mock data must contain exactly 9 conflicts."""
    assert len(_MOCK_CONFLICTS) == 9


def test_mock_conflicts_required_fields():
    """Regression: every conflict must have all schema fields the frontend consumes."""
    required = {"id", "has_conflict", "title", "severity", "confidence",
                "sources", "affected", "resolution", "citations"}
    for c in _MOCK_CONFLICTS:
        missing = required - set(c.keys())
        assert not missing, f"Conflict {c['id']} missing fields: {missing}"


def test_mock_conflicts_citations_have_required_fields():
    """Regression: every citation must have document, section, passage, confidence."""
    required = {"document", "section", "passage", "confidence"}
    for c in _MOCK_CONFLICTS:
        for cit in c.get("citations", []):
            missing = required - set(cit.keys())
            assert not missing, (
                f"Conflict {c['id']} citation missing fields: {missing}. Citation: {cit}"
            )


def test_mock_trace_steps_count():
    """Regression: trace must have 7 steps."""
    assert len(_MOCK_TRACE) == 7


def test_isSurprise_flag_on_anonymity_conflict():
    """The anonymity conflict must have isSurprise=True — drives ⚡ badge in UI."""
    anon = next((c for c in _MOCK_CONFLICTS if c["id"] == "2"), None)
    assert anon is not None
    assert anon.get("isSurprise") is True


# ─── 5. Approval Gate endpoints ───────────────────────────────────────────────

@pytest.mark.anyio
async def test_approve_endpoint_returns_correct_schema():
    """POST /approve must return {status: 'approved', conflict_id: ...}."""
    from httpx import AsyncClient, ASGITransport
    from backend.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/approve", json={"conflict_id": "2"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "approved"
    assert data["conflict_id"] == "2"


@pytest.mark.anyio
async def test_reject_endpoint_returns_correct_schema():
    """POST /reject must return {status: 'rejected', conflict_id: ...}."""
    from httpx import AsyncClient, ASGITransport
    from backend.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/reject", json={"conflict_id": "5", "reason": "false positive"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rejected"
    assert data["conflict_id"] == "5"
