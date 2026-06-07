/**
 * frontend/src/App.jsx
 *
 * Root component — assembles the two-panel ConflictSense dashboard.
 *
 * Spec reference: docs/frontend_spec.md §2, docs/ui_state_machine.md
 *
 * Data flow (backend-driven):
 *   1. User clicks "Run Analysis"
 *   2. App calls api.streamAnalysis() → opens EventSource to GET /analyze/stream
 *   3. trace_step events     → advance ReasoningTrace
 *   4. conflict_detected events → append to ConflictDashboard
 *   5. complete event        → set phase="done", detect MOCK_MODE flag
 *
 * Fallback (Tier 3 client-side):
 *   If the EventSource connection fails (backend not running), App
 *   automatically falls back to local timer-based simulation using the
 *   pre-computed mock data. isMockMode is set to true in both paths.
 *
 * Approval Gate:
 *   onApprove → POST /approve via api.approveConflict()  (optimistic local update)
 *   onReject  → POST /reject  via api.rejectConflict()   (optimistic local update)
 *   State updates are applied immediately; backend call is fire-and-forget.
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import ConflictDashboard from './components/ConflictDashboard.jsx';
import ReasoningTrace    from './components/ReasoningTrace.jsx';
import { streamAnalysis, approveConflict, rejectConflict } from './lib/api.js';
import {
  MOCK_DOCUMENTS,
  MOCK_TRACE_STEPS,
  MOCK_CONFLICTS,
  STEP_INTERVAL_MS,
  STEP_OFFSET_MS,
  CONFLICT_REVEAL_MAP,
} from './lib/mockData.js';

// ─── Global CSS ───────────────────────────────────────────────────────────────
const GLOBAL_CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  *, *::before, *::after { box-sizing: border-box; }

  body {
    margin: 0;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    background: #F1F5F9;
    color: #0F172A;
    -webkit-font-smoothing: antialiased;
  }

  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(5px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  @keyframes slideIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.45; }
  }

  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 2px; }
`;

// ─── Severity summary pills ───────────────────────────────────────────────────
function SummaryPills({ visibleConflicts }) {
  const crit = visibleConflicts.filter((c) => c.severity === 'CRITICAL').length;
  const high = visibleConflicts.filter((c) => c.severity === 'HIGH').length;
  const med  = visibleConflicts.filter((c) => c.severity === 'MEDIUM').length;
  if (!visibleConflicts.length) return null;
  return (
    <div style={{ display: 'flex', gap: 6, marginLeft: 10 }}>
      {crit > 0 && (
        <span style={{ background: '#FCEBEB', color: '#A32D2D', border: '0.5px solid #F09595', padding: '2px 9px', borderRadius: 4, fontSize: 11, fontWeight: 600, animation: 'slideIn 0.25s ease' }}>
          {crit} Critical
        </span>
      )}
      {high > 0 && (
        <span style={{ background: '#FAEEDA', color: '#854F0B', border: '0.5px solid #EF9F27', padding: '2px 9px', borderRadius: 4, fontSize: 11, fontWeight: 600, animation: 'slideIn 0.25s ease' }}>
          {high} High
        </span>
      )}
      {med > 0 && (
        <span style={{ background: '#E6F1FB', color: '#185FA5', border: '0.5px solid #85B7EB', padding: '2px 9px', borderRadius: 4, fontSize: 11, fontWeight: 600, animation: 'slideIn 0.25s ease' }}>
          {med} Medium
        </span>
      )}
    </div>
  );
}

// ─── Run Analysis Button ──────────────────────────────────────────────────────
function RunButton({ phase, onClick }) {
  const isScanning = phase === 'scanning';
  const isDone     = phase === 'done';
  const label = isScanning ? 'Analyzing…' : isDone ? 'Re-run Analysis' : 'Run Analysis';
  return (
    <button
      id="btn-run-analysis"
      onClick={onClick}
      disabled={isScanning}
      style={{
        marginLeft: 'auto',
        background: isScanning ? '#E2E8F0' : '#185FA5',
        color: isScanning ? '#94A3B8' : '#FFFFFF',
        border: 'none', borderRadius: 6, padding: '7px 16px',
        fontSize: 12, fontWeight: 500,
        cursor: isScanning ? 'not-allowed' : 'pointer',
        transition: 'all 0.2s',
        display: 'flex', alignItems: 'center', gap: 7,
        fontFamily: 'inherit',
      }}
    >
      {isScanning && (
        <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#85B7EB', display: 'inline-block', animation: 'pulse 1s infinite' }} />
      )}
      {label}
    </button>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [phase, setPhase]                       = useState('idle');
  const [visibleSteps, setVisibleSteps]         = useState([]);
  const [currentStep, setCurrentStep]           = useState(-1);
  const [visibleConflicts, setVisibleConflicts] = useState([]);
  const [selectedId, setSelectedId]             = useState(null);
  const [approvedIds, setApprovedIds]           = useState(new Set());
  const [rejectedIds, setRejectedIds]           = useState(new Set());
  const [escalatedIds, setEscalatedIds]         = useState(new Set());
  const [isMockMode, setIsMockMode]             = useState(false);

  // Refs for cleanup
  const streamCancelRef = useRef(null);
  const timersRef       = useRef([]);

  // ── Cleanup helper ────────────────────────────────────────────────────────
  const cancelAll = useCallback(() => {
    if (streamCancelRef.current) {
      streamCancelRef.current.cancel();
      streamCancelRef.current = null;
    }
    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];
  }, []);

  useEffect(() => () => cancelAll(), [cancelAll]);

  // ── Tier 3 local fallback ─────────────────────────────────────────────────
  // Called when backend SSE fails. Mirrors the original timer-based simulation.
  const runLocalFallback = useCallback(() => {
    console.warn('[App] Backend unavailable — activating Tier 3 client-side mock mode');
    setIsMockMode(true);

    MOCK_TRACE_STEPS.forEach((step, stepIdx) => {
      const tid = setTimeout(() => {
        setVisibleSteps((prev) => [...prev, step]);
        setCurrentStep(stepIdx);

        const conflictIndexes = CONFLICT_REVEAL_MAP[stepIdx];
        if (conflictIndexes) {
          setVisibleConflicts((prev) => {
            const existingIds = new Set(prev.map((c) => c.id));
            const fresh = conflictIndexes
              .map((ci) => MOCK_CONFLICTS[ci])
              .filter(Boolean)
              .filter((c) => !existingIds.has(c.id));
            return fresh.length ? [...prev, ...fresh] : prev;
          });
        }

        if (stepIdx === MOCK_TRACE_STEPS.length - 1) {
          setPhase('done');
        }
      }, stepIdx * STEP_INTERVAL_MS + STEP_OFFSET_MS);

      timersRef.current.push(tid);
    });
  }, []);

  // ── runAnalysis — backend SSE path ────────────────────────────────────────
  const runAnalysis = useCallback(() => {
    cancelAll();

    // Reset state
    setPhase('scanning');
    setVisibleSteps([]);
    setCurrentStep(-1);
    setVisibleConflicts([]);
    setApprovedIds(new Set());
    setRejectedIds(new Set());
    setEscalatedIds(new Set());
    setSelectedId(null);
    setIsMockMode(false);

    let stepIndex = 0;

    const handle = streamAnalysis({
      onTraceStep: (step) => {
        setVisibleSteps((prev) => [...prev, step]);
        setCurrentStep((prev) => prev + 1);
        stepIndex++;
      },

      onConflictDetected: (conflict) => {
        setVisibleConflicts((prev) => {
          const exists = prev.some((c) => c.id === conflict.id);
          return exists ? prev : [...prev, conflict];
        });
      },

      onComplete: (payload) => {
        setPhase('done');
        // Set MOCK_MODE if backend signals it
        if (payload?._meta?.fallback === 'MOCK_MODE') {
          setIsMockMode(true);
        }
      },

      onError: () => {
        // Backend unavailable — fall back to Tier 3 local simulation
        cancelAll();
        runLocalFallback();
      },
    });

    streamCancelRef.current = handle;
  }, [cancelAll, runLocalFallback]);

  // ── Approval Gate handlers ────────────────────────────────────────────────
  const handleSelect = useCallback((id) => {
    setSelectedId((prev) => (prev === id ? null : id));
  }, []);

  const handleApprove = useCallback(async (id) => {
    // Optimistic local update first
    setApprovedIds((prev) => new Set([...prev, id]));
    // Fire-and-forget backend call
    try {
      await approveConflict(id);
    } catch (err) {
      console.warn('[App] /approve call failed (mock mode OK):', err.message);
    }
  }, []);

  const handleReject = useCallback(async (id) => {
    setRejectedIds((prev) => new Set([...prev, id]));
    try {
      await rejectConflict(id);
    } catch (err) {
      console.warn('[App] /reject call failed (mock mode OK):', err.message);
    }
  }, []);

  const handleEscalate = useCallback((id) => {
    setEscalatedIds((prev) => new Set([...prev, id]));
  }, []);

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <>
      <style>{GLOBAL_CSS}</style>

      <div style={{ fontFamily: "'Inter', system-ui, sans-serif", background: '#F1F5F9', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

        {/* ── Header ──────────────────────────────────────────────────── */}
        <div style={{ background: '#FFFFFF', borderBottom: '0.5px solid #E2E8F0', padding: '10px 16px', display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0, flexWrap: 'wrap' }}>
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: '-0.3px', color: '#0F172A', display: 'flex', alignItems: 'center', gap: 7 }}>
              <span style={{ color: '#185FA5', fontSize: 16 }}>◈</span>
              ConflictSense
            </div>
            <div style={{ fontSize: 10, color: '#94A3B8', marginTop: 1 }}>
              Knowledge Conflict Intelligence · Nexora Technologies
            </div>
          </div>

          <SummaryPills visibleConflicts={visibleConflicts} />
          <RunButton phase={phase} onClick={runAnalysis} />
        </div>

        {/* ── Responsible AI banner ────────────────────────────────────── */}
        <div style={{ background: '#FAEEDA', borderBottom: '0.5px solid #EF9F27', padding: '5px 16px', fontSize: 10, color: '#633806', display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
          <span>⚠</span>
          <span>ConflictSense uses AI to identify potential policy conflicts. All findings require human review before action. This tool does not constitute legal advice.</span>
        </div>

        {/* ── Two-panel body ───────────────────────────────────────────── */}
        <div style={{ display: 'flex', flex: 1, minHeight: 0, overflow: 'hidden' }}>

          {/* Left: document grid + conflict list */}
          <ConflictDashboard
            documents={MOCK_DOCUMENTS}
            visibleConflicts={visibleConflicts}
            phase={phase}
            totalConflicts={MOCK_CONFLICTS.length}
            selectedId={selectedId}
            approvedIds={approvedIds}
            rejectedIds={rejectedIds}
            escalatedIds={escalatedIds}
            onSelect={handleSelect}
            onApprove={handleApprove}
            onReject={handleReject}
            onEscalate={handleEscalate}
          />

          {/* Right: reasoning trace terminal */}
          <ReasoningTrace
            steps={visibleSteps}
            phase={phase}
            isMockMode={isMockMode}
            currentStep={currentStep}
          />
        </div>
      </div>
    </>
  );
}
