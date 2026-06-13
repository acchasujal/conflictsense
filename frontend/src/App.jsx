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

  // Modals & Toasts
  const [activeModal, setActiveModal]           = useState(null);
  const [toastMessage, setToastMessage]         = useState(null);
  const [legalReason, setLegalReason]           = useState("Potential compliance exposure requires legal assessment.");

  // ── Accessibility state ───────────────────────────────────────────────
  const [reducedMotion, setReducedMotion]       = useState(false);
  const [srMode, setSrMode]                     = useState(false);
  const [announcement, setAnnouncement]         = useState('');
  const [showShortcuts, setShowShortcuts]       = useState(false);

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

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ignore if typing in an input/textarea
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === '?') {
        setShowShortcuts(prev => !prev);
      }
      if (e.key === 'Escape') {
        setShowShortcuts(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

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

  const handleApprove = useCallback((id) => {
    setActiveModal({ type: 'APPROVE', conflictId: id });
  }, []);

  const handleReject = useCallback((id) => {
    setActiveModal({ type: 'LEGAL', conflictId: id });
  }, []);

  const handleEscalate = useCallback((id) => {
    setActiveModal({ type: 'ESCALATE', conflictId: id });
  }, []);

  const confirmAction = () => {
    if (!activeModal) return;
    const { type, conflictId } = activeModal;
    
    let newStep = {
      event: "trace_step",
      data: {
        time: "0.2s",
        confidence: 100,
        citations: []
      }
    };

    if (type === 'APPROVE') {
      setApprovedIds((prev) => new Set([...prev, conflictId]));
      setToastMessage("Remediation plan approved.");
      newStep.data.agent = "GovernanceApprovalAgent";
      newStep.data.agentColor = "#16A34A";
      newStep.data.conclusion = "Remediation plan approved by reviewer.";
    } else if (type === 'LEGAL') {
      setRejectedIds((prev) => new Set([...prev, conflictId]));
      setToastMessage("Legal review requested.");
      newStep.data.agent = "LegalReviewAgent";
      newStep.data.agentColor = "#9333EA";
      newStep.data.conclusion = "Conflict escalated for legal assessment. Reason: " + legalReason;
    } else if (type === 'ESCALATE') {
      setEscalatedIds((prev) => new Set([...prev, conflictId]));
      setToastMessage("Conflict escalated to Governance Board.");
      newStep.data.agent = "GovernanceBoardAgent";
      newStep.data.agentColor = "#DC2626";
      newStep.data.conclusion = "Critical conflict escalated for executive review.";
    }

    setVisibleSteps(prev => [...prev, newStep]);
    setActiveModal(null);
  };

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
              onClick={() => { setSrMode(true); setReducedMotion(true); setShowShortcuts(true); }}
              title="Launch Accessibility Demo"
              style={{
                background: '#4ADE80',
                border: '1px solid #22C55E',
                borderRadius: 6, padding: '4px 9px', fontSize: 11,
                fontWeight: 700, cursor: 'pointer', color: '#064E3B',
                display: 'flex', alignItems: 'center', gap: 4, marginRight: 8,
                boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
              }}
            >
              Accessibility Demo
            </button>
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

        {/* ── Keyboard Shortcuts Overlay ────────────────────────────────── */}
        {showShortcuts && (
          <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(15,23,42,0.4)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={() => setShowShortcuts(false)}>
            <div style={{ background: '#FFFFFF', borderRadius: 12, padding: '24px 32px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)', minWidth: 320 }} onClick={e => e.stopPropagation()}>
              <div style={{ fontSize: 18, fontWeight: 700, color: '#0F172A', marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                Keyboard Shortcuts
                <button onClick={() => setShowShortcuts(false)} style={{ background: 'none', border: 'none', fontSize: 18, cursor: 'pointer', color: '#94A3B8' }}>×</button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 13, color: '#475569' }}>Navigate</span>
                  <kbd style={{ background: '#F1F5F9', border: '1px solid #CBD5E1', borderRadius: 4, padding: '2px 8px', fontSize: 12, fontFamily: 'monospace', fontWeight: 600 }}>Tab</kbd>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 13, color: '#475569' }}>Open / Activate</span>
                  <kbd style={{ background: '#F1F5F9', border: '1px solid #CBD5E1', borderRadius: 4, padding: '2px 8px', fontSize: 12, fontFamily: 'monospace', fontWeight: 600 }}>Enter</kbd>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 13, color: '#475569' }}>Expand Card</span>
                  <kbd style={{ background: '#F1F5F9', border: '1px solid #CBD5E1', borderRadius: 4, padding: '2px 8px', fontSize: 12, fontFamily: 'monospace', fontWeight: 600 }}>Space</kbd>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 13, color: '#475569' }}>Close Overlay</span>
                  <kbd style={{ background: '#F1F5F9', border: '1px solid #CBD5E1', borderRadius: 4, padding: '2px 8px', fontSize: 12, fontFamily: 'monospace', fontWeight: 600 }}>Esc</kbd>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: 13, color: '#475569' }}>Show Shortcuts</span>
                  <kbd style={{ background: '#F1F5F9', border: '1px solid #CBD5E1', borderRadius: 4, padding: '2px 8px', fontSize: 12, fontFamily: 'monospace', fontWeight: 600 }}>?</kbd>
                </div>
              </div>
            </div>
          </div>
        )}

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
            visibleConflicts={visibleConflicts}
            documentsCount={liveDocuments.length}
          />
        </main>
      </div>

      {/* ── Modals & Toasts ────────────────────────────────────────── */}
      <Modal 
        isOpen={activeModal?.type === 'APPROVE'} 
        onClose={() => setActiveModal(null)} 
        title="Approve Remediation Plan?"
      >
        <div style={{ fontSize: 14, color: '#334155', marginBottom: 24 }}>
          This will mark the conflict as approved for remediation and update governance status.
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
          <button onClick={() => setActiveModal(null)} style={{ padding: '8px 16px', borderRadius: 4, border: '1px solid #CBD5E1', background: '#FFFFFF', cursor: 'pointer' }}>Cancel</button>
          <button onClick={confirmAction} style={{ padding: '8px 16px', borderRadius: 4, border: 'none', background: '#3B82F6', color: '#FFFFFF', fontWeight: 600, cursor: 'pointer' }}>Confirm</button>
        </div>
      </Modal>

      <Modal 
        isOpen={activeModal?.type === 'LEGAL'} 
        onClose={() => setActiveModal(null)} 
        title="Request Legal Review"
      >
        <div style={{ fontSize: 14, color: '#334155', marginBottom: 16 }}>
          {activeModal && visibleConflicts.find(c => c.id === activeModal.conflictId) && (
            <div style={{ background: '#F8FAFC', padding: 12, borderRadius: 6, marginBottom: 16, border: '1px solid #E2E8F0' }}>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>{visibleConflicts.find(c => c.id === activeModal.conflictId).title}</div>
              <div style={{ fontSize: 12, color: '#64748B' }}>Severity: {visibleConflicts.find(c => c.id === activeModal.conflictId).severity}</div>
            </div>
          )}
          <label style={{ display: 'block', fontWeight: 600, marginBottom: 8 }}>Reason</label>
          <textarea 
            value={legalReason} 
            onChange={(e) => setLegalReason(e.target.value)}
            style={{ width: '100%', padding: 12, borderRadius: 4, border: '1px solid #CBD5E1', minHeight: 80, fontFamily: 'inherit', boxSizing: 'border-box' }}
          />
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
          <button onClick={() => setActiveModal(null)} style={{ padding: '8px 16px', borderRadius: 4, border: '1px solid #CBD5E1', background: '#FFFFFF', cursor: 'pointer' }}>Cancel</button>
          <button onClick={confirmAction} style={{ padding: '8px 16px', borderRadius: 4, border: 'none', background: '#9333EA', color: '#FFFFFF', fontWeight: 600, cursor: 'pointer' }}>Submit</button>
        </div>
      </Modal>

      <Modal 
        isOpen={activeModal?.type === 'ESCALATE'} 
        onClose={() => setActiveModal(null)} 
        title="Escalate to Governance Board"
      >
        <div style={{ fontSize: 14, color: '#334155', marginBottom: 24 }}>
          This conflict will be escalated to the Governance Board due to enterprise impact.
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
          <button onClick={() => setActiveModal(null)} style={{ padding: '8px 16px', borderRadius: 4, border: '1px solid #CBD5E1', background: '#FFFFFF', cursor: 'pointer' }}>Cancel</button>
          <button onClick={confirmAction} style={{ padding: '8px 16px', borderRadius: 4, border: 'none', background: '#DC2626', color: '#FFFFFF', fontWeight: 600, cursor: 'pointer' }}>Escalate</button>
        </div>
      </Modal>

      <Toast 
        isVisible={!!toastMessage} 
        message={toastMessage} 
        onClose={() => setToastMessage(null)} 
      />
    </>
  );
}
