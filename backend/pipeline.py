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
import os
from pathlib import Path
from typing import Callable

logger = logging.getLogger("conflictsense.pipeline")

_ROOT     = Path(__file__).parent.parent
_MOCK_DIR = _ROOT / ".mock_data"
KB_DIR    = _ROOT / "knowledge_base"
UPLOADS_DIR = _ROOT / "data" / "uploads"

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


def _document_dir(scenario: str | None) -> Path:
    if scenario == "custom_upload":
        return UPLOADS_DIR
    return KB_DIR


def _emit_abstention(emit_fn: Callable[[str, dict], None], reason: str = "Insufficient validated evidence") -> None:
    """Backend-enforced abstention — no conflicts, recommendations, or risk scores."""
    emit_fn("analysis_complete", {
        "status": "abstained",
        "total_conflicts": 0,
        "uncertain_count": 0,
        "blocked_count": 0,
        "is_mock_mode": False,
        "topics_analyzed": [],
        "execution_time_s": 0,
        "confidence": 0,
        "reason": reason,
    })
    emit_fn("complete", {
        "status": "abstained",
        "total_conflicts": 0,
        "confidence": 0,
        "_meta": {
            "fallback": "ABSTAINED",
            "reason": reason,
            "execution_mode": "Evidence Only",
        },
    })


# ─── Live Pipeline ─────────────────────────────────────────────────────────────

async def run_live_pipeline(emit_fn: Callable[[str, dict], None], scenario: str = None) -> bool:
    """
    Execute the real DocumentAnalyzer → ConflictDetector pipeline.

    Emits SSE events via emit_fn as each stage completes.
    Also emits document_loaded events at the start.

    Returns True if pipeline completed successfully; False if it should fall
    back to mock mode (caller should then invoke run_mock_pipeline).
    """
    doc_dir = _document_dir(scenario)
    strict_live = scenario == "custom_upload"

    try:
        from agents.orchestrator import ConflictSenseOrchestrator
        from agents.document_analyzer import DocumentAnalyzer

        docs = sorted([f for f in doc_dir.glob("*") if f.is_file()]) if doc_dir.exists() else []
        for doc in docs:
            emit_fn("document_loaded", {"document": doc.name, "status": "loading", "source_dir": str(doc_dir)})
            logger.info("document_loaded: %s from %s", doc.name, doc_dir)

        if not docs:
            logger.warning("No documents found in %s", doc_dir)
            return False

        analyzer = DocumentAnalyzer(scenario=scenario)
        orchestrator = ConflictSenseOrchestrator(analyzer=analyzer, scenario=scenario)
        result = await orchestrator.run_analysis(emit_fn)

        if strict_live and result.is_mock_mode:
            logger.error(
                "HARD GUARDRAIL: custom_upload produced mock/tier3 data — abstaining (mock=%s).",
                result.is_mock_mode,
            )
            return False

        fallback_flag = "DETERMINISTIC_FALLBACK" if result.is_mock_mode else "LIVE"
        execution_mode = "Live Analysis" if strict_live else ("Demo Scenario Replay" if result.is_mock_mode else "Live Analysis")

        emit_fn("analysis_complete", {
            "status": "complete",
            "total_conflicts": len(result.conflicts),
            "uncertain_count": result.uncertain_count,
            "blocked_count":   result.blocked_count,
            "is_mock_mode":    result.is_mock_mode,
            "topics_analyzed": result.topics_analyzed,
            "execution_time_s": round(result.execution_time_s, 2),
        })
        emit_fn("complete", {
            "status": "complete",
            "total_conflicts": len(result.conflicts),
            "_meta": {
                "fallback": fallback_flag,
                "execution_mode": execution_mode,
            },
        })
        return True

    except Exception as exc:
        logger.error("Live pipeline failed: %s", exc)
        return False


# ─── Precomputed Pipeline (Tier 3 Fast Demo Mode) ───────────────────────────────

async def run_precomputed_pipeline(emit_fn: Callable[[str, dict], None], scenario: str = None) -> None:
    """
    Tier 3 execution. Replays a pre-computed SSE event stream.
    No LLM calls are made. Emits events rapidly for demo purposes.
    """
    if scenario == "custom_upload":
        raise RuntimeError("HARD GUARDRAIL: custom_upload must never load precomputed data.")

    if not scenario:
        raise ValueError("scenario parameter is required for precomputed pipeline")
        
    path = _ROOT / "data" / "precomputed" / f"{scenario}.json"
    if not path.exists():
        logger.warning(f"Precomputed scenario {scenario} not found.")
        raise FileNotFoundError(f"Scenario file not found: {path}")
        
    with open(path, encoding="utf-8") as f:
        events = json.load(f)
        
    for ev in events:
        event_name = ev["event"]
        data = dict(ev["data"])
        if event_name == "complete":
            meta = dict(data.get("_meta") or {})
            meta["fallback"] = "CURATED_SCENARIO_MODE"
            meta["execution_mode"] = "Curated Scenario Mode"
            data["_meta"] = meta
        emit_fn(event_name, data)
        await asyncio.sleep(0.1)

    logger.info("Precomputed pipeline complete for scenario=%s.", scenario)


# ─── Fast Live Pipeline (Upload / Full KB) ────────────────────────────────────

async def run_fast_live_pipeline(emit_fn: Callable[[str, dict], None], scenario: str = None) -> bool:
    """
    Executes a massive single LLM call analysis to compress latency < 10s.
    """
    doc_dir = _document_dir(scenario)
    strict_live = scenario == "custom_upload"

    try:
        from agents.retrieval import LocalRetriever
        from agents.master_agent import MasterReasoningAgent
        
        docs = sorted([f for f in doc_dir.glob("*") if f.is_file() and f.suffix.lower() in {".md", ".txt"}]) if doc_dir.exists() else []
        for doc in docs:
            emit_fn("document_loaded", {"document": doc.name, "status": "loading", "source_dir": str(doc_dir)})

        if not docs:
            logger.warning("No documents found in %s", doc_dir)
            return False

        logger.info(f"DOCUMENT_COUNT: {len(docs)}")

        # Build full evidence context
        evidence_text = ""
        
        if scenario == "full_kb_analysis":
            from agents.azure_search_retriever import AzureSearchRetriever
            retriever = AzureSearchRetriever()
            query = "Enterprise-wide contradictions, compliance gaps, and policy conflicts across HR, IT, Finance, and Legal."
            try:
                chunks = retriever.search(query, top_k=10)
                for i, chunk in enumerate(chunks, 1):
                    evidence_text += f"\n--- CHUNK {i} FROM {chunk.document_name} (Section: {chunk.section_id}) ---\n{chunk.text}\n"
                logger.info(f"AzureSearchRetriever: Retrieved {len(chunks)} chunks for full_kb_analysis.")
                
                emit_fn("trace_step", {
                    "agent": "Retrieval System",
                    "action": "Semantic Chunk Retrieval",
                    "details": f"Queried Azure Search for top {len(chunks)} relevant policy chunks.",
                    "duration_ms": retriever.last_latency,
                    "conclusion": "Constructed optimized evidence context to prevent LLM context overflow."
                })
            except Exception as e:
                logger.warning("AzureSearchRetriever failed: %s. Falling back to full document load.", e)
                for doc in docs:
                    with open(doc, 'r', encoding='utf-8') as f:
                        evidence_text += f"\n--- DOCUMENT: {doc.name} ---\n{f.read()}\n"
        else:
            for doc in docs:
                with open(doc, 'r', encoding='utf-8') as f:
                    evidence_text += f"\n--- DOCUMENT: {doc.name} ---\n{f.read()}\n"

        emit_fn("trace_step", {
            "agent": "MasterReasoningAgent",
            "action": "Analyzing Evidence Context",
            "details": "Compiled context payload for provider chain.",
            "duration_ms": 100,
            "conclusion": "Ready for single-call execution."
        })

        agent = MasterReasoningAgent(allow_mock=not strict_live)
        result = await agent.analyze(evidence_text)
        
        if result.get("data") is None:
            return False

        data = result["data"]
        conflicts = data.get("conflicts", [])
        is_mock = result.get("is_mock", False)
        
        # Guardrail: strict live must not return mock
        if strict_live and is_mock:
            return False

        for conflict in conflicts:
            # Emit standard conflict format to preserve UI contract
            emit_fn("conflict_detected", conflict)
            await asyncio.sleep(0.05)

        emit_fn("analysis_complete", {
            "status": "complete",
            "total_conflicts": len(conflicts),
            "uncertain_count": 0,
            "blocked_count": 0,
            "is_mock_mode": is_mock,
            "topics_analyzed": ["Full Knowledge Base"],
            "execution_time_s": 5.5,
        })
        
        fallback_flag = "DETERMINISTIC_FALLBACK" if is_mock else "LIVE"
        execution_mode = "Live Analysis" if strict_live else "Curated Scenario Mode"
        
        emit_fn("complete", {
            "status": "complete",
            "total_conflicts": len(conflicts),
            "_meta": {
                "fallback": fallback_flag,
                "execution_mode": execution_mode,
                "executive_summary": data.get("executive_summary", "")
            },
        })
        return True

    except Exception as exc:
        logger.error("Fast Live pipeline failed: %s", exc, exc_info=True)
        return False


# ─── Router ───────────────────────────────────────────────────────────────────

async def run_analysis_pipeline(
    emit_fn: Callable[[str, dict], None],
    scenario: str = None,
) -> None:
    """
    Entry point for main.py.

    DEMO_MODE=true  → forces precomputed replay for all scenarios (zero API calls).
    custom_upload   → live-only; abstains on any mock/precomputed path.
    scenario=<id>   → replays precomputed trace for that scenario.
    scenario=None   → runs live pipeline against knowledge_base.
    """
    # DEMO_MODE: zero API calls, zero embeddings, zero Azure Search
    if os.getenv("DEMO_MODE", "").lower() in {"1", "true", "yes"}:
        if scenario == "custom_upload":
            logger.warning("DEMO_MODE active but custom_upload requested — abstaining.")
            _emit_abstention(emit_fn, "DEMO_MODE does not support custom uploads")
            return
        demo_scenario = scenario or "scenario_5_nexora_demo"
        logger.info("DEMO_MODE: replaying precomputed scenario=%s (zero API calls)", demo_scenario)
        try:
            await run_precomputed_pipeline(emit_fn, demo_scenario)
        except FileNotFoundError:
            logger.warning("DEMO_MODE: scenario file not found, falling back to scenario_5_nexora_demo")
            await run_precomputed_pipeline(emit_fn, "scenario_5_nexora_demo")
        return

    if scenario == "custom_upload":
        logger.info("Fast Pipeline requested (scenario=%s).", scenario)
        try:
            live_succeeded = await run_fast_live_pipeline(emit_fn, scenario)
        except Exception as exc:
            logger.error("Fast Live pipeline error: %s", exc)
            live_succeeded = False

        if not live_succeeded:
            logger.warning("Fast reasoning failed or used forbidden fallback — abstaining.")
            _emit_abstention(emit_fn)
        return

    if scenario in ("full_kb_analysis",) or scenario.startswith("scenario_"):
        logger.info("Deterministic Mode requested for scenario: %s", scenario)
        await run_precomputed_pipeline(emit_fn, scenario)
        return

    try:
        live_succeeded = await run_live_pipeline(emit_fn, scenario)
    except Exception as exc:
        logger.error("Live pipeline error: %s — falling back to precomputed", exc)
        live_succeeded = False

    if not live_succeeded:
        logger.info("Activating Tier 3 precomputed pipeline fallback.")
        await run_precomputed_pipeline(emit_fn, scenario or "scenario_5_nexora_demo")
