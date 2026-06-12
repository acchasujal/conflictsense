"""Verification tests for custom_upload routing and mock guardrails."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import patch

import pytest

from agents.document_analyzer import DocumentAnalyzer, UPLOADS_DIR, KB_DIR
from backend.pipeline import run_analysis_pipeline, run_live_pipeline


@pytest.fixture
def upload_docs(tmp_path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    (upload_dir / "Policy_A.md").write_text("## §1\nAll data stays in EU.\n", encoding="utf-8")
    (upload_dir / "Policy_B.md").write_text("## §1\nAll data must be stored in US.\n", encoding="utf-8")
    monkeypatch.setattr("agents.document_analyzer.UPLOADS_DIR", upload_dir)
    monkeypatch.setattr("backend.pipeline.UPLOADS_DIR", upload_dir)
    return upload_dir


def test_document_analyzer_custom_upload_uses_uploads_dir(upload_docs):
    analyzer = DocumentAnalyzer(scenario="custom_upload")
    assert analyzer.strict_live is True
    assert set(analyzer.document_names) == {"Policy_A.md", "Policy_B.md"}
    assert analyzer._doc_dir == upload_docs
    assert analyzer._retriever.kb_dir == upload_docs
    assert analyzer._retriever.kb_dir != KB_DIR


@pytest.mark.anyio
async def test_custom_upload_abstains_when_no_documents(monkeypatch, tmp_path):
    empty_uploads = tmp_path / "empty_uploads"
    empty_uploads.mkdir()
    monkeypatch.setattr("backend.pipeline.UPLOADS_DIR", empty_uploads)
    monkeypatch.setattr("agents.document_analyzer.UPLOADS_DIR", empty_uploads)

    events = []

    def emit(event: str, data: dict) -> None:
        events.append((event, data))

    await run_analysis_pipeline(emit, "custom_upload")

    complete = [d for e, d in events if e == "complete"]
    assert len(complete) == 1
    assert complete[0]["status"] == "abstained"
    assert complete[0]["_meta"]["fallback"] == "ABSTAINED"
    assert complete[0]["_meta"]["execution_mode"] == "Evidence Only"


@pytest.mark.anyio
async def test_custom_upload_never_emits_precomputed(upload_docs):
    events = []

    def emit(event: str, data: dict) -> None:
        events.append((event, data))

    with patch("agents.chunk_extractor.ChunkExtractor.extract") as mock_extract:
        from agents.foundry_iq_client import FoundryIQResult
        mock_extract.return_value = FoundryIQResult(
            query="q", document_id="Policy_A.md", citations=[], is_silent=True, tier_used=1,
        )
        await run_live_pipeline(emit, "custom_upload")

    doc_loaded = [d for e, d in events if e == "document_loaded"]
    assert all("Policy_" in d["document"] for d in doc_loaded)
    assert all(str(upload_docs) in d.get("source_dir", "") for d in doc_loaded)
    complete = [d for e, d in events if e == "complete"]
    assert complete
    assert complete[0]["_meta"]["execution_mode"] == "Live Analysis"


def test_demo_scenario_files_are_distinct():
    root = Path(__file__).parent.parent / "data" / "precomputed"
    scenarios = [
        "scenario_1_data_residency",
        "scenario_2_anonymous_reporting",
        "scenario_3_cross_border",
        "scenario_4_vendor_compliance",
    ]
    topics = []
    conflict_ids = []
    for name in scenarios:
        import json
        data = json.loads((root / f"{name}.json").read_text(encoding="utf-8"))
        evidence = next(ev["data"]["topic"] for ev in data if ev["event"] == "evidence_retrieved")
        conflict = next(ev["data"]["id"] for ev in data if ev["event"] == "conflict_emitted")
        topics.append(evidence)
        conflict_ids.append(conflict)
    assert len(set(topics)) == len(scenarios)
    assert len(set(conflict_ids)) == len(scenarios)
