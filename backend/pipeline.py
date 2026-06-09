"""
backend/pipeline.py

Reasoning pipeline execution — live and mock modes.

Single responsibility: run the ConflictSense reasoning pipeline and stream
SSE events via a callback. All SSE framing (EventSourceResponse) stays in
main.py; all agent coordination stays in orchestrator.py.

Two modes:
  run_live_pipeline(emit_fn)  — DocumentAnalyzer → ConflictDetector → SSE
  run_mock_pipeline(emit_fn)  — Streams precomputed mock data (Tier 3)

Spec reference: docs/reliability_spec.md §1 (3-tier fallback)
                docs/system_architecture.md §3

The emit_fn signature is:
    emit_fn(event_name: str, data: dict) -> None
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import AsyncGenerator, Callable

logger = logging.getLogger("conflictsense.pipeline")

_ROOT     = Path(__file__).parent.parent
_MOCK_DIR = _ROOT / "mock_data"

# Timing between mock events (preserves animation feel in Tier 3 demo)
MOCK_STEP_INTERVAL_S: float = 0.95

# Conflict reveal map: trace step index → list of conflict indexes to emit
# Matches frontend/src/lib/mockData.js CONFLICT_REVEAL_MAP exactly
_CONFLICT_REVEAL_MAP: dict[int, list[int]] = {
    1: [0],
    5: [1, 2],
    6: [3, 4, 5, 6, 7, 8],
}


def _load_mock_json(filename: str) -> list:
    path = _MOCK_DIR / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ─── Live Pipeline ─────────────────────────────────────────────────────────────

async def run_live_pipeline(emit_fn: Callable[[str, dict], None]) -> bool:
    """
    Execute the real DocumentAnalyzer → ConflictDetector pipeline.

    Emits SSE events via emit_fn as each stage completes.
    Also emits document_loaded events at the start.

    Returns True if pipeline completed successfully; False if it should fall
    back to mock mode (caller should then invoke run_mock_pipeline).
    """
    try:
        # Import here to isolate import errors (agent modules unavailable = fallback)
        from agents.orchestrator import ConflictSenseOrchestrator
        from agents.document_analyzer import SUPPORTED_TOPICS
        from pathlib import Path as _Path

        # ── Emit document_loaded events ───────────────────────────────────────
        kb_dir = _Path(__file__).parent.parent / "knowledge_base"
        docs = sorted(kb_dir.glob("*.md")) if kb_dir.exists() else []
        for doc in docs:
            emit_fn("document_loaded", {"document": doc.name, "status": "loading"})
            logger.info("document_loaded: %s", doc.name)

        if not docs:
            logger.warning("No documents found in knowledge_base/ — falling back to mock")
            return False

        # ── Run orchestrator ──────────────────────────────────────────────────
        orchestrator = ConflictSenseOrchestrator()
        result = await orchestrator.run_analysis(emit_fn)

        # ── Final events ──────────────────────────────────────────────────────
        fallback_flag = "MOCK_MODE" if result.is_mock_mode else "LIVE"

        emit_fn("analysis_complete", {
            "status": "complete",
            "total_conflicts": len(result.conflicts),
            "uncertain_count": result.uncertain_count,
            "blocked_count":   result.blocked_count,
            "is_mock_mode":    result.is_mock_mode,
            "topics_analyzed": result.topics_analyzed,
            "execution_time_s": round(result.execution_time_s, 2),
        })
        # Backwards-compat alias for frontend
        emit_fn("complete", {
            "status": "complete",
            "total_conflicts": len(result.conflicts),
            "_meta": {"fallback": fallback_flag},
        })
        return True

    except Exception as exc:
        logger.error("Live pipeline failed: %s — falling back to mock", exc)
        return False


# ─── Mock Pipeline (Tier 3) ───────────────────────────────────────────────────

async def run_mock_pipeline(emit_fn: Callable[[str, dict], None]) -> None:
    """
    Stream dynamically generated mock data using real document chunks.

    This is Tier 3 — guaranteed to succeed. Called when the live pipeline
    fails or when Azure credentials are unavailable.
    """
    from agents.retrieval import LocalRetriever
    import hashlib

    # Emit document_loaded events (Tier 3 still announces doc loading)
    kb_dir = _ROOT / "knowledge_base"
    docs = sorted(kb_dir.glob("*.md")) if kb_dir.exists() else []
    for doc in docs:
        emit_fn("document_loaded", {"document": doc.name, "status": "loaded", "is_mock": True})

    retriever = LocalRetriever()
    topics = ["data location", "anonymity", "byod", "vacation policy", "incident reporting"]
    conflicts_emitted = 0

    for topic in topics:
        emit_fn("trace_step", {
            "agent": "DocumentAnalyzer",
            "action": f"Analyzing corpus for: {topic}",
            "is_mock": True,
            "topic": topic
        })
        await asyncio.sleep(MOCK_STEP_INTERVAL_S)

        chunks_by_doc = {}
        for doc in docs:
            top_chunks = retriever.retrieve_for_document(topic, doc.name, top_k=1)
            if top_chunks:
                chunks_by_doc[doc.name] = top_chunks[0]

        if len(chunks_by_doc) >= 2:
            doc_names = list(chunks_by_doc.keys())
            doc_a = doc_names[0]
            doc_b = doc_names[1]
            chunk_a = chunks_by_doc[doc_a]
            chunk_b = chunks_by_doc[doc_b]

            conflict_id = hashlib.md5(f"{doc_a}{doc_b}{topic}".encode()).hexdigest()[:8]

            emit_fn("trace_step", {
                "agent": "ConflictDetector",
                "action": f"Cross-referencing {doc_a} and {doc_b}",
                "is_mock": True,
                "topic": topic
            })
            await asyncio.sleep(MOCK_STEP_INTERVAL_S)

            conflict_data = {
                "id": conflict_id,
                "title": f"MOCK: Structural impossibility in {topic}",
                "severity": "CRITICAL",
                "confidence": 95,
                "sources": [f"{doc_a} {chunk_a.section_id}", f"{doc_b} {chunk_b.section_id}"],
                "reasoning": f"Mock Conflict: {doc_a} {chunk_a.section_id} states '{chunk_a.text[:60]}...' while {doc_b} {chunk_b.section_id} states '{chunk_b.text[:60]}...'. These represent a deterministic structural impossibility based on actual document chunks.",
                "status": "UNRESOLVED",
                "conflict_type": "Direct Contradiction",
                "is_mock_mode": True,
                "citations": [
                    {
                        "document": doc_a,
                        "section": chunk_a.section_id,
                        "passage": chunk_a.text,
                        "confidence": 0.95,
                        "topic": topic
                    },
                    {
                        "document": doc_b,
                        "section": chunk_b.section_id,
                        "passage": chunk_b.text,
                        "confidence": 0.95,
                        "topic": topic
                    }
                ],
                "conflict_pairs": [
                    {
                        "statement_a": {"document": doc_a, "section": chunk_a.section_id},
                        "statement_b": {"document": doc_b, "section": chunk_b.section_id},
                        "conflict_type": "Direct Contradiction",
                        "why_impossible": "Deterministic mock pairing based on retrieved chunks."
                    }
                ]
            }

            emit_fn("conflict_detected", conflict_data)
            emit_fn("conflict_emitted", conflict_data)
            logger.info("Mock pipeline: conflict_detected id=%s", conflict_id)
            conflicts_emitted += 1
            await asyncio.sleep(MOCK_STEP_INTERVAL_S)

    emit_fn("analysis_complete", {
        "status": "complete",
        "total_conflicts": conflicts_emitted,
        "is_mock_mode": True,
    })
    emit_fn("complete", {
        "status": "complete",
        "total_conflicts": conflicts_emitted,
        "_meta": {"fallback": "MOCK_MODE"},
    })
    logger.info("Mock pipeline complete. %d conflicts emitted.", conflicts_emitted)


# ─── Router ───────────────────────────────────────────────────────────────────

async def run_analysis_pipeline(
    emit_fn: Callable[[str, dict], None],
) -> None:
    """
    Entry point for main.py.

    Attempts live pipeline first; falls back to mock on any failure.
    Guaranteed to complete — the demo never fails.
    """
    try:
        live_succeeded = await run_live_pipeline(emit_fn)
    except Exception as exc:
        logger.error("Live pipeline error: %s — falling back to mock", exc)
        live_succeeded = False

    if not live_succeeded:
        logger.info("Activating Tier 3 mock pipeline.")
        await run_mock_pipeline(emit_fn)
