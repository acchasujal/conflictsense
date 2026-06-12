/**
 * frontend/src/components/ReasoningTrace.jsx
 *
 * Live Agent Timeline showing reasoning trace steps with Microsoft-style Agent Cards.
 */

import React, { useRef, useEffect, useState } from 'react';
import AgentCard from './AgentCard.jsx';
import SkeletonLoader from './SkeletonLoader.jsx';
import ExecutiveSummaryPanel from './ExecutiveSummaryPanel.jsx';

export default function ReasoningTrace({ steps, phase, isMockMode, isAbstained, executionMode, currentStep, agentStatus, isDebugUI, visibleConflicts = [], documentsCount = 0 }) {
  const traceBodyRef = useRef(null);

  // Auto-scroll to bottom as new steps appear
  useEffect(() => {
    if (traceBodyRef.current) {
      traceBodyRef.current.scrollTop = traceBodyRef.current.scrollHeight;
    }
  }, [currentStep, steps.length]);

  const [startTime, setStartTime] = useState(null);
  const [elapsedMs, setElapsedMs] = useState(0);

  useEffect(() => {
    if (phase === 'scanning') {
      if (steps.length === 0) {
        setStartTime(Date.now());
        setElapsedMs(0);
      } else if (!startTime) {
        setStartTime(Date.now());
      }
    } else if (phase === 'idle') {
      setStartTime(null);
      setElapsedMs(0);
    }
  }, [phase, steps.length, startTime]);

  useEffect(() => {
    let raf;
    const update = () => {
      if (startTime && phase === 'scanning') {
        setElapsedMs(Date.now() - startTime);
        raf = requestAnimationFrame(update);
      }
    };
    if (startTime && phase === 'scanning') {
      raf = requestAnimationFrame(update);
    }
    return () => cancelAnimationFrame(raf);
  }, [startTime, phase]);

  const isRunning = phase === 'scanning';
  const isDone    = phase === 'done';
  const totalSteps = 7;
  const displayStep = Math.min(Math.max(currentStep + 1, 1), totalSteps);
  
  const currentAgent = steps.length > 0 ? steps[steps.length - 1].agent : 'Initializing...';
  const elapsedSec = (elapsedMs / 1000).toFixed(1);
  const estimatedRemaining = currentStep > 0 && isRunning
    ? (((elapsedMs / currentStep) * (totalSteps - currentStep)) / 1000).toFixed(1)
    : '...';

  return (
    <div
      role="region"
      aria-label="Live Agent Timeline"
      style={{
        borderLeft: '1px solid #E2E8F0',
        background: '#FAFAFA',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        width: '45%',
        minWidth: 400,
        maxWidth: 600,
        flexShrink: 0,
      }}
    >
      {/* ── Panel header ───────────────────────────────────────────────── */}
      <div
        style={{
          padding: '16px 20px',
          background: '#FFFFFF',
          borderBottom: '1px solid #E2E8F0',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          flexShrink: 0,
          boxShadow: '0 1px 2px rgba(0,0,0,0.02)',
        }}
      >
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 16, fontWeight: 600, color: '#0F172A' }}>Live Agent Timeline</div>
          <div style={{ fontSize: 12, color: '#64748B', marginTop: 8 }}>
            {isRunning ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 16px', fontSize: 11 }}>
                <div><span style={{ fontWeight: 600 }}>Current Agent:</span> {currentAgent}</div>
                <div><span style={{ fontWeight: 600 }}>Completed:</span> {displayStep - 1} / {totalSteps}</div>
                <div><span style={{ fontWeight: 600 }}>Elapsed:</span> {elapsedSec}s</div>
                <div><span style={{ fontWeight: 600 }}>Est. Remaining:</span> {estimatedRemaining}s</div>
              </div>
            ) : isDone && isAbstained ? (
              <div style={{ display: 'flex', gap: 16 }}>
                <span style={{ color: '#64748B' }}>Analysis Inconclusive</span>
                <span><span style={{ fontWeight: 600 }}>Total Time:</span> {elapsedSec}s</span>
              </div>
            ) : isDone ? (
              <div style={{ display: 'flex', gap: 16 }}>
                <span>Analysis Complete</span>
                <span><span style={{ fontWeight: 600 }}>Total Time:</span> {elapsedSec}s</span>
              </div>
            ) : (
              'Awaiting start'
            )}
          </div>
        </div>

        {isRunning && (
          <div style={{ display: 'flex', gap: 4 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#2563EB', animation: 'pulse 1s infinite' }} />
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#2563EB', animation: 'pulse 1s infinite 0.2s' }} />
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#2563EB', animation: 'pulse 1s infinite 0.4s' }} />
          </div>
        )}
        {isDone && isAbstained && (
          <span style={{ fontSize: 13, fontWeight: 600, color: '#64748B', display: 'flex', alignItems: 'center', gap: 4 }}>
            ⏸ Abstained
          </span>
        )}
        {isDone && !isAbstained && (
          <span style={{ fontSize: 13, fontWeight: 600, color: '#16A34A', display: 'flex', alignItems: 'center', gap: 4 }}>
            ✓ Complete
          </span>
        )}
      </div>

      {/* ── Execution Mode banner ───────────────────────────────────────── */}
      {isDebugUI && executionMode && (
        <div
          style={{
            padding: '8px 20px',
            background: executionMode === 'Evidence Only' ? '#F1F5F9' : executionMode === 'Live Analysis' ? '#EFF6FF' : '#F0FDF4',
            borderBottom: `1px solid ${executionMode === 'Evidence Only' ? '#CBD5E1' : executionMode === 'Live Analysis' ? '#BFDBFE' : '#BBF7D0'}`,
            fontSize: 11,
            color: executionMode === 'Evidence Only' ? '#475569' : executionMode === 'Live Analysis' ? '#1D4ED8' : '#16A34A',
            fontWeight: 500
          }}
        >
          Execution Mode: {executionMode}
          {executionMode === 'Curated Scenario Mode' && ' — deterministic enterprise policy analysis.'}
          {executionMode === 'Live Analysis' && ' — uploaded documents analyzed via live retrieval and provider chain.'}
          {executionMode === 'Evidence Only' && ' — no validated conflicts emitted; confidence 0%.'}
        </div>
      )}

      {isDebugUI && isMockMode && !executionMode && (
        <div
          style={{
            padding: '8px 20px',
            background: '#F0FDF4',
            borderBottom: '1px solid #BBF7D0',
            fontSize: 11,
            color: '#16A34A',
            fontWeight: 500
          }}
        >
          🛡️ Fast Validation Mode: Precomputed reasoning trace engaged for accelerated, deterministic execution.
        </div>
      )}

      {/* ── Trace body ──────────────────────────────────────────────────── */}
      <div
        ref={traceBodyRef}
        aria-live="polite"
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '20px',
        }}
      >
        {phase === 'idle' && (
          <div style={{ textAlign: 'center', paddingTop: 60, color: '#94A3B8' }}>
            <div style={{ fontSize: 40, marginBottom: 16 }}>🤖</div>
            <div style={{ fontSize: 14, fontWeight: 500 }}>Agents ready for deployment</div>
            <div style={{ fontSize: 12, marginTop: 8 }}>Click "Run Analysis" to orchestrate the pipeline</div>
          </div>
        )}

        {/* Rendered agent cards */}
        {steps.map((step, i) => (
          <AgentCard key={i} step={step} isLatest={i === steps.length - 1 && isRunning} />
        ))}

        {isRunning && (
          <div style={{ marginTop: 20 }}>
            {agentStatus && (
              <div style={{
                marginBottom: 12,
                fontSize: 12,
                color: '#64748B',
                fontFamily: 'monospace',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                background: '#F1F5F9',
                padding: '8px 12px',
                borderRadius: 4,
                border: '1px solid #E2E8F0'
              }}>
                <span style={{ fontSize: 14 }}>⚡</span> {agentStatus}
              </div>
            )}
            <SkeletonLoader type="conflict" count={1} />
          </div>
        )}

        {isDone && isAbstained && (
          <div
            style={{
              marginTop: 16,
              padding: '16px',
              background: '#F1F5F9',
              borderRadius: '8px',
              border: '1px solid #CBD5E1',
              animation: 'fadeInUp 0.3s ease',
              textAlign: 'center'
            }}
          >
            <div style={{ fontSize: 14, fontWeight: 600, color: '#475569' }}>Analysis Inconclusive</div>
            <div style={{ fontSize: 12, color: '#64748B', marginTop: 4 }}>
              The system could not gather sufficient validated evidence to determine whether a policy conflict exists.
            </div>
            <div style={{ fontSize: 12, color: '#475569', marginTop: 8, fontWeight: 500 }}>
              Reasoning Confidence: 0% — ABSTAINED
            </div>
          </div>
        )}

        {phase === 'cancelled' && (
          <div
            style={{
              marginTop: 16,
              padding: '16px',
              background: '#FEF2F2',
              borderRadius: '8px',
              border: '1px solid #FECACA',
              animation: 'fadeInUp 0.3s ease',
              textAlign: 'center'
            }}
          >
            <div style={{ fontSize: 14, fontWeight: 600, color: '#991B1B' }}>Analysis Cancelled</div>
            <div style={{ fontSize: 12, color: '#DC2626', marginTop: 4 }}>
              Execution aborted by user.
            </div>
            <div style={{ fontSize: 12, color: '#991B1B', marginTop: 8, fontWeight: 500 }}>
              System safely idled.
            </div>
          </div>
        )}

        {isDone && !isAbstained && visibleConflicts.length > 0 && (
          <div style={{ marginTop: 16, animation: 'fadeInUp 0.4s ease' }}>
            <ExecutiveSummaryPanel conflicts={visibleConflicts} documentsCount={documentsCount} />
          </div>
        )}

        {isDone && !isAbstained && (
          <div
            style={{
              marginTop: 16,
              padding: '16px',
              background: '#F0FDF4',
              borderRadius: '8px',
              border: '1px solid #BBF7D0',
              animation: 'fadeInUp 0.3s ease',
              textAlign: 'center'
            }}
          >
            <div style={{ fontSize: 14, fontWeight: 600, color: '#16A34A' }}>Pipeline Execution Finished</div>
            <div style={{ fontSize: 12, color: '#15803D', marginTop: 4 }}>
              Conflicts detected. Awaiting human review.
            </div>
          </div>
        )}
      </div>

      {/* ── Footer: Foundry IQ attribution ──────────────────────────────── */}
      <div
        style={{
          padding: '12px 20px',
          background: '#FFFFFF',
          borderTop: '1px solid #E2E8F0',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          flexShrink: 0,
        }}
      >
        <span style={{ fontSize: 11, color: '#64748B' }}>Grounded by</span>
        <span style={{ fontSize: 11, fontWeight: 700, color: '#2563EB' }}>Azure AI Search</span>
        <span style={{ fontSize: 11, color: '#94A3B8' }}>• Orchestrated by ConflictSense Multi-Agent Pipeline</span>
      </div>
    </div>
  );
}
