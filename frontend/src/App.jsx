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
import ConflictDashboard    from './components/ConflictDashboard.jsx';
import ReasoningTrace       from './components/ReasoningTrace.jsx';
import EnterpriseRiskBanner from './components/EnterpriseRiskBanner.jsx';
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
    font-family: 'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif;
    background: #FAFAFA;
    color: #242424;
    -webkit-font-smoothing: antialiased;
  }

  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  @keyframes slideIn {
    from { opacity: 0; transform: translateX(10px); }
    to   { opacity: 1; transform: translateX(0); }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.5; }
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.25); }

  /* ─── Accessibility: Focus Indicators ───────────────────────────────── */
  *:focus-visible {
    outline: 3px solid #2563EB;
    outline-offset: 2px;
    border-radius: 3px;
  }

  /* ─── Accessibility: Reduced Motion CSS class ────────────────────────── */
  .reduced-motion *,
  .reduced-motion *::before,
  .reduced-motion *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  @media (prefers-reduced-motion: reduce) {
    * {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
`;

// ─── Severity summary pills ───────────────────────────────────────────────────
function SummaryPills({ visibleConflicts }) {
  const crit = visibleConflicts.filter((c) => c.severity === 'CRITICAL').length;
  const high = visibleConflicts.filter((c) => c.severity === 'HIGH').length;
  const med  = visibleConflicts.filter((c) => c.severity === 'MEDIUM').length;
  if (!visibleConflicts.length) return null;
  return (
    <div style={{ display: 'flex', gap: 6, marginLeft: 10 }} aria-label="Conflict Severity Summary" role="group">
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
      aria-label="Run AI Conflict Analysis"
      aria-busy={isScanning}
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
  const [isAbstained, setIsAbstained]           = useState(false);
  const [executionMode, setExecutionMode]       = useState(null);
  const [agentStatus, setAgentStatus]           = useState(null);
  const [totalConflicts, setTotalConflicts]     = useState(0);

  // New state to fix scenario routing bug
  const [currentScenario, setCurrentScenario]   = useState(null);
  const [liveDocuments, setLiveDocuments]       = useState(MOCK_DOCUMENTS);

  // ── Accessibility state ───────────────────────────────────────────────
  const [reducedMotion, setReducedMotion]       = useState(false);
  const [srMode, setSrMode]                     = useState(false);
  const [announcement, setAnnouncement]         = useState('');

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

  // ── Screen reader announcements ───────────────────────────────────────
  const announce = useCallback((msg) => {
    if (!srMode) return;
    setAnnouncement('');
    setTimeout(() => setAnnouncement(msg), 50);
  }, [srMode]);

  useEffect(() => {
    if (phase === 'scanning') announce('Analysis started. AI agents are reviewing policy documents.');
    if (phase === 'done')     announce(`Analysis complete. ${visibleConflicts.length} conflict${visibleConflicts.length !== 1 ? 's' : ''} detected.`);
  }, [phase]); // eslint-disable-line

  useEffect(() => {
    if (visibleConflicts.length > 0) {
      const last = visibleConflicts[visibleConflicts.length - 1];
      announce(`Conflict detected: ${last.title}. Severity: ${last.severity}.`);
    }
  }, [visibleConflicts.length]); // eslint-disable-line

  useEffect(() => () => cancelAll(), [cancelAll]);

  // ── Tier 3 local fallback ─────────────────────────────────────────────────
  // Called when backend SSE fails. Mirrors the original timer-based simulation.
  const runLocalFallback = useCallback((scenario) => {
    console.warn('[App] Backend unavailable — activating Tier 3 client-side mock mode');
    if (scenario === 'custom_upload') {
      console.error('[App] HARD GUARDRAIL: custom_upload cannot fall back to precomputed client mock mode!');
      setPhase('done');
      setIsAbstained(true);
      return;
    }

    setIsMockMode(true);
    setLiveDocuments(MOCK_DOCUMENTS);
    setTotalConflicts(MOCK_CONFLICTS.length);

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
  const runAnalysis = useCallback((scenario = null) => {
    cancelAll();

    // Fix: Ensure we preserve scenario state across button clicks (which pass MouseEvent)
    let scenarioParam = null;
    if (typeof scenario === 'string') {
      scenarioParam = scenario;
    } else {
      scenarioParam = currentScenario;
    }
    
    setCurrentScenario(scenarioParam);

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
    setIsAbstained(false);
    setExecutionMode(null);
    setAgentStatus("Starting analysis engine. First request may take up to 60 seconds.");
    setLiveDocuments([]); // Clear documents on new analysis run

    if (scenarioParam === 'custom_upload') {
      setExecutionMode('Live Analysis');
    } else if (scenarioParam?.startsWith('scenario_')) {
      setExecutionMode('Demo Scenario Replay');
    }

    let stepIndex = 0;

    const handle = streamAnalysis({
      scenario: scenarioParam,
      onDocumentLoaded: (data) => {
        setLiveDocuments((prev) => {
          if (prev.some((d) => d.name === data.document)) return prev;
          return [...prev, {
            id: data.document,
            name: data.document,
            dept: scenarioParam === "custom_upload" ? "Uploaded Policy" : "Knowledge Base",
            date: new Date().toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
            size: "Live",
            status: data.status,
          }];
        });
      },
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
        setAgentStatus(null);
        if (payload?.status === 'abstained') {
          setIsAbstained(true);
          setExecutionMode('Evidence Only');
        }
        if (payload?.total_conflicts !== undefined) {
          setTotalConflicts(payload.total_conflicts);
        }
        const fallback = payload?._meta?.fallback;
        if (fallback === 'DEMO_SCENARIO_REPLAY') {
          setExecutionMode('Demo Scenario Replay');
        } else if (payload?._meta?.execution_mode) {
          setExecutionMode(payload._meta.execution_mode);
        }
        if (fallback === 'DETERMINISTIC_FALLBACK') {
          setIsMockMode(true);
        }
      },
      
      onAgentStatus: (status) => {
        setAgentStatus(status.message);
      },

      onError: () => {
        // Backend unavailable — fall back to Tier 3 local simulation
        cancelAll();
        runLocalFallback(scenarioParam);
      },
    });

    streamCancelRef.current = handle;
  }, [cancelAll, runLocalFallback, currentScenario]);

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

      <div
        id="conflictsense-root"
        className={reducedMotion ? 'reduced-motion' : ''}
        style={{ fontFamily: "'Inter', system-ui, sans-serif", background: '#F1F5F9', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}
      >

        {/* ── Header ──────────────────────────────────────────────────── */}
        <header aria-label="Application Header" style={{ background: '#FFFFFF', borderBottom: '0.5px solid #E2E8F0', padding: '10px 16px', display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0, flexWrap: 'wrap' }}>
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

          {/* ── Accessibility Toggles ──────────────────────────────── */}
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 6, alignItems: 'center' }} role="group" aria-label="Accessibility Settings">
            <button
              id="btn-reduced-motion"
              onClick={() => setReducedMotion(m => !m)}
              aria-pressed={reducedMotion}
              title="Toggle Reduced Motion"
              style={{
                background: reducedMotion ? '#EFF6FF' : '#F8FAFC',
                border: `1px solid ${reducedMotion ? '#3B82F6' : '#CBD5E1'}`,
                borderRadius: 6, padding: '4px 9px', fontSize: 11,
                fontWeight: 600, cursor: 'pointer', color: reducedMotion ? '#1D4ED8' : '#475569',
                display: 'flex', alignItems: 'center', gap: 4,
              }}
            >
              {reducedMotion ? '🎞 Motion On' : '🎞 Reduce Motion'}
            </button>
            <button
              id="btn-sr-mode"
              onClick={() => setSrMode(m => !m)}
              aria-pressed={srMode}
              title="Toggle Screen Reader Announcements"
              style={{
                background: srMode ? '#EFF6FF' : '#F8FAFC',
                border: `1px solid ${srMode ? '#3B82F6' : '#CBD5E1'}`,
                borderRadius: 6, padding: '4px 9px', fontSize: 11,
                fontWeight: 600, cursor: 'pointer', color: srMode ? '#1D4ED8' : '#475569',
                display: 'flex', alignItems: 'center', gap: 4,
              }}
            >
              {srMode ? '🔊 SR On' : '🔊 Screen Reader Mode'}
            </button>
          </div>
        </header>

        {/* ── Screen Reader Live Region ─────────────────────────────────── */}
        <div
          role="status"
          aria-live="polite"
          aria-atomic="true"
          style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', clip: 'rect(0,0,0,0)', whiteSpace: 'nowrap' }}
        >
          {announcement}
        </div>

        {/* ── Debug Panel ──────────────────────────────────────────────── */}
        {import.meta.env.VITE_DEBUG_MODE === 'true' && (
          <div style={{ background: '#1E293B', color: '#F8FAFC', padding: '4px 16px', fontSize: 10, display: 'flex', gap: 16, borderBottom: '1px solid #0F172A' }}>
            <span style={{ color: '#94A3B8' }}>DEBUG MODE</span>
            <span>Phase: <strong style={{ color: '#38BDF8' }}>{phase}</strong></span>
            <span>Execution Mode: <strong style={{ color: executionMode ? '#38BDF8' : '#64748B' }}>{executionMode || '—'}</strong></span>
            <span>Total Conflicts (Internal): <strong>{totalConflicts}</strong></span>
            <span>Visible Conflicts: <strong>{visibleConflicts.length}</strong></span>
          </div>
        )}

        {/* ── Responsible AI banner ────────────────────────────────────── */}
        <div role="alert" aria-live="polite" style={{ background: '#FAEEDA', borderBottom: '0.5px solid #EF9F27', padding: '5px 16px', fontSize: 10, color: '#633806', display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
          <span>⚠</span>
          <span>ConflictSense uses AI to identify potential policy conflicts. All findings require human review before action. This tool does not constitute legal advice.</span>
        </div>

        {/* ── Enterprise Risk Banner (appears once first conflict is detected) ─── */}
        <EnterpriseRiskBanner conflicts={visibleConflicts} phase={phase} />

        {/* ── Two-panel body ───────────────────────────────────────────── */}
        <main aria-label="Main Application Content" style={{ display: 'flex', flex: 1, minHeight: 0, overflow: 'hidden' }}>

          {/* Left: document grid + conflict list */}
          <ConflictDashboard
            documents={liveDocuments}
            visibleConflicts={visibleConflicts}
            phase={phase}
            totalConflicts={phase === 'done' ? totalConflicts : (isMockMode ? MOCK_CONFLICTS.length : totalConflicts)}
            selectedId={selectedId}
            approvedIds={approvedIds}
            rejectedIds={rejectedIds}
            escalatedIds={escalatedIds}
            onSelect={handleSelect}
            onApprove={handleApprove}
            onReject={handleReject}
            onEscalate={handleEscalate}
            onRunAnalysis={runAnalysis}
            isAbstained={isAbstained && currentScenario === 'custom_upload'}
          />

          {/* Right: reasoning trace terminal */}
          <ReasoningTrace
            steps={visibleSteps}
            phase={phase}
            isMockMode={isMockMode}
            isAbstained={isAbstained && currentScenario === 'custom_upload'}
            executionMode={executionMode}
            currentStep={currentStep}
            agentStatus={agentStatus}
          />
        </main>
      </div>
    </>
  );
}
