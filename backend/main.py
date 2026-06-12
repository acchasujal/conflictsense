"""
backend/main.py
FastAPI application — ConflictSense backend.

Spec reference: docs/api_contracts.md, docs/system_architecture.md,
                docs/reliability_spec.md §1

Endpoints:
  GET  /analyze/stream  — SSE stream: trace_step / conflict_detected / complete
  POST /approve         — Human Approval Gate: approve a conflict finding
  POST /reject          — Human Approval Gate: mark finding as false positive

Architecture notes:
  - This backend serves pre-computed mock data from mock_data/ (Tier 3).
  - No agents, no Foundry IQ, no LLM calls.
  - Events are streamed with realistic timing delays to drive the demo animation.
  - The _meta.fallback = "MOCK_MODE" flag is set when live LLM providers fail.
  - CORS is open to localhost:5173 (Vite dev server).
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from backend.models import (
    ApproveRequest,
    RejectRequest,
    ActionResponse,
    TraceStep,
    ConflictRecord,
)
from backend.pipeline import run_analysis_pipeline
import os

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("conflictsense")

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ConflictSense API",
    description="Policy Conflict Intelligence — Knowledge Conflict Detection for Enterprise Documents",
    version="0.1.0",
)

# CORS — allow the Vite dev server and any local origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "https://conflictsense.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Load pre-computed mock data (Tier 3) ─────────────────────────────────────
# Resolved relative to the project root, not this file's location.
_ROOT = Path(__file__).parent.parent
_MOCK_DIR = _ROOT / "mock_data"


def _load_json(filename: str) -> list:
    path = _MOCK_DIR / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


MOCK_TRACE_STEPS: list[dict] = _load_json("precomputed_trace.json")
MOCK_CONFLICTS: list[dict]   = _load_json("precomputed_conflicts.json")

# Timing between SSE events (mirrors frontend STEP_INTERVAL_MS)
STEP_INTERVAL_S: float = 0.95

# Map: trace-step index → list of conflict indexes to emit after that step
# Mirrors frontend/src/lib/mockData.js CONFLICT_REVEAL_MAP exactly
CONFLICT_REVEAL_MAP: dict[int, list[int]] = {
    1: [0],           # After ConflictDetector (data residency) → conflict 0
    5: [1, 2],        # After ConflictDetector (anonymity) → conflicts 1, 2
    6: [3, 4, 5, 6, 7, 8],  # ResolutionRecommender → remaining 6
}


# ─── SSE helpers ──────────────────────────────────────────────────────────────

def _sse_event(event: str, data: dict) -> dict:
    """Return a dict in the format sse_starlette expects."""
    return {"event": event, "data": json.dumps(data, ensure_ascii=False)}


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
async def root_check():
    """Root healthcheck endpoint."""
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    """Healthcheck endpoint for Render deployment."""
    return {"status": "healthy"}

@app.get("/analyze/stream")
async def analyze_stream(scenario: str = None):
    """
    GET /analyze/stream

    Server-Sent Events stream that drives the Reasoning Trace UI.

    Event sequence per docs/api_contracts.md §1:
      1. For each trace step:
         a. Emit event=trace_step  with the TraceStep payload
         b. If this step triggers conflicts, emit event=conflict_detected for each
      2. After all steps: emit event=complete with summary + _meta.fallback flag
    """
    async def _generate() -> AsyncGenerator[dict, None]:
        logger.info("Starting analysis stream using run_analysis_pipeline")
        queue = asyncio.Queue()

        def emit(event: str, data: dict) -> None:
            queue.put_nowait(_sse_event(event, data))

        async def pipeline_runner():
            try:
                await run_analysis_pipeline(emit, scenario)
            except Exception as exc:
                logger.error("Error in pipeline runner: %s", exc)
            finally:
                await queue.put(None)
                
        async def heartbeat_runner():
            status_messages = [
                "Initializing multi-agent pipeline...",
                "Vectorizing documents via Azure AI Search...",
                "Running structural impossibility checks...",
                "Evaluating cross-policy references...",
                "Validating compliance directives...",
                "Performing multi-agent consensus...",
                "Compiling executive summary..."
            ]
            idx = 0
            while True:
                emit("agent_status", {"message": status_messages[idx % len(status_messages)]})
                idx += 1
                await asyncio.sleep(4)

        # Run pipeline and heartbeat in background tasks
        runner_task = asyncio.create_task(pipeline_runner())
        heartbeat_task = asyncio.create_task(heartbeat_runner())

        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                yield item
        finally:
            if not heartbeat_task.done():
                heartbeat_task.cancel()
            # Ensure task is not leaked if client disconnects early
            if not runner_task.done():
                runner_task.cancel()
                try:
                    await runner_task
                except asyncio.CancelledError:
                    pass

    return EventSourceResponse(
        _generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

@app.post("/upload")
async def upload_policies(files: list[UploadFile] = File(...)):
    """
    POST /upload
    Save custom policies for live analysis.
    """
    upload_dir = _ROOT / "data" / "uploads"
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    for file in files:
        if not file.filename:
            continue
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)
        
    if not saved_files:
        raise HTTPException(status_code=400, detail="No valid files uploaded.")
        
    return {"status": "ok", "files_loaded": len(saved_files)}


@app.post("/approve", response_model=ActionResponse)
async def approve_conflict(body: ApproveRequest):
    """
    POST /approve

    Human Approval Gate — approve a conflict finding.
    Marks the finding as entering the resolution workflow.
    No autonomous action is taken. Per docs/prd.md §2.3.
    """
    logger.info("Conflict approved: %s", body.conflict_id)
    return ActionResponse(status="approved", conflict_id=body.conflict_id)


@app.post("/reject", response_model=ActionResponse)
async def reject_conflict(body: RejectRequest):
    """
    POST /reject

    Human Approval Gate — mark a conflict finding as false positive.
    Removes the finding from the active resolution queue.
    No autonomous action is taken. Per docs/prd.md §2.3.
    """
    logger.info("Conflict rejected (false positive): %s", body.conflict_id)
    return ActionResponse(status="rejected", conflict_id=body.conflict_id)




# ─── Dev entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
