/**
 * frontend/src/lib/api.js
 *
 * API client for the ConflictSense backend.
 * Spec reference: docs/api_contracts.md
 *
 * Functions:
 *   streamAnalysis(callbacks)  — Opens EventSource to GET /analyze/stream
 *                                Routes SSE events to appropriate callbacks
 *                                Returns a cancel() function
 *
 *   approveConflict(id)        — POST /approve { conflict_id }
 *   rejectConflict(id)         — POST /reject  { conflict_id }
 *
 * Fallback behaviour:
 *   If the EventSource connection fails or the backend returns an error,
 *   the onError callback is called. App.jsx then falls back to local
 *   mock-data simulation (Tier 3 client-side fallback).
 */

const BASE_URL = "";   // Empty = same-origin via Vite proxy → http://localhost:8000

// ─── streamAnalysis ───────────────────────────────────────────────────────────

/**
 * Open an SSE stream to GET /analyze/stream and route events.
 *
 * @param {{
 *   onTraceStep:        (step: object) => void,
 *   onConflictDetected: (conflict: object) => void,
 *   onComplete:         (payload: object) => void,
 *   onError:            (err: Event|Error) => void,
 *   onAgentStatus:      (status: object) => void,
 * }} callbacks
 *
 * @returns {{ cancel: () => void }}   Call cancel() to close the stream early.
 */
export function streamAnalysis({ onTraceStep, onConflictDetected, onComplete, onError, onAgentStatus }) {
  const url = `${BASE_URL}/analyze/stream`;
  const es = new EventSource(url);

  es.addEventListener("trace_step", (e) => {
    try {
      const step = JSON.parse(e.data);
      onTraceStep(step);
    } catch (err) {
      console.error("[api] Failed to parse trace_step event:", err, e.data);
    }
  });

  es.addEventListener("agent_status", (e) => {
    try {
      if (onAgentStatus) {
        const status = JSON.parse(e.data);
        onAgentStatus(status);
      }
    } catch (err) {
      console.error("[api] Failed to parse agent_status event:", err, e.data);
    }
  });

  es.addEventListener("conflict_detected", (e) => {
    try {
      const conflict = JSON.parse(e.data);
      onConflictDetected(conflict);
    } catch (err) {
      console.error("[api] Failed to parse conflict_detected event:", err, e.data);
    }
  });

  es.addEventListener("complete", (e) => {
    try {
      const payload = JSON.parse(e.data);
      onComplete(payload);
    } catch (err) {
      console.error("[api] Failed to parse complete event:", err, e.data);
    }
    es.close();
  });

  es.onerror = (err) => {
    console.error("[api] EventSource error:", err);
    es.close();
    onError(err);
  };

  return {
    cancel: () => {
      es.close();
    },
  };
}

// ─── approveConflict ──────────────────────────────────────────────────────────

/**
 * POST /approve — Human Approval Gate: approve a conflict finding.
 * @param {string} conflictId
 * @returns {Promise<{ status: string, conflict_id: string }>}
 */
export async function approveConflict(conflictId) {
  const res = await fetch(`${BASE_URL}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conflict_id: conflictId }),
  });
  if (!res.ok) throw new Error(`/approve failed: ${res.status}`);
  return res.json();
}

// ─── rejectConflict ───────────────────────────────────────────────────────────

/**
 * POST /reject — Human Approval Gate: mark conflict as false positive.
 * @param {string} conflictId
 * @returns {Promise<{ status: string, conflict_id: string }>}
 */
export async function rejectConflict(conflictId) {
  const res = await fetch(`${BASE_URL}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conflict_id: conflictId }),
  });
  if (!res.ok) throw new Error(`/reject failed: ${res.status}`);
  return res.json();
}
