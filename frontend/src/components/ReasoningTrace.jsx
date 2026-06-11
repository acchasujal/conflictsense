/**
 * frontend/src/components/ReasoningTrace.jsx
 *
 * Live Agent Timeline showing reasoning trace steps with Microsoft-style Agent Cards.
 */

import React, { useRef, useEffect } from 'react';
import AgentCard from './AgentCard.jsx';
import SkeletonLoader from './SkeletonLoader.jsx';

export default function ReasoningTrace({ steps, phase, isMockMode, currentStep, agentStatus }) {
  const traceBodyRef = useRef(null);

  // Auto-scroll to bottom as new steps appear
  useEffect(() => {
    if (traceBodyRef.current) {
      traceBodyRef.current.scrollTop = traceBodyRef.current.scrollHeight;
    }
  }, [currentStep, steps.length]);

  const isRunning = phase === 'scanning';
  const isDone    = phase === 'done';
  const totalSteps = 7;
  const displayStep = Math.min(Math.max(currentStep + 1, 1), totalSteps);

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
          <div style={{ fontSize: 12, color: '#64748B', marginTop: 2 }}>
            {isRunning ? `Step ${displayStep}/${totalSteps} • Processing` : isDone ? 'Analysis Complete' : 'Awaiting start'}
          </div>
        </div>

        {isRunning && (
          <div style={{ display: 'flex', gap: 4 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#2563EB', animation: 'pulse 1s infinite' }} />
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#2563EB', animation: 'pulse 1s infinite 0.2s' }} />
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#2563EB', animation: 'pulse 1s infinite 0.4s' }} />
          </div>
        )}
        {isDone && (
          <span style={{ fontSize: 13, fontWeight: 600, color: '#16A34A', display: 'flex', alignItems: 'center', gap: 4 }}>
            ✓ Complete
          </span>
        )}
      </div>

      {/* ── Mock Mode banner ────────────────────────────────────────────── */}
      {isMockMode && (
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
          🛡️ Demo Replay Mode Activated: Using a recorded enterprise scenario to guarantee deterministic results and a consistent demonstration experience.
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

        {isDone && (
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
        <span style={{ fontSize: 11, color: '#64748B' }}>Powered by</span>
        <span style={{ fontSize: 11, fontWeight: 700, color: '#2563EB' }}>Azure AI Foundry</span>
        <span style={{ fontSize: 11, color: '#94A3B8' }}>• Fully Auditable</span>
      </div>
    </div>
  );
}
