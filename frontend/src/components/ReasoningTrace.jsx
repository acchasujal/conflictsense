/**
 * frontend/src/components/ReasoningTrace.jsx
 *
 * Right panel: scrollable dark terminal showing reasoning trace steps.
 *
 * Spec reference: docs/frontend_spec.md §3.3, docs/ui_state_machine.md,
 *                 docs/reasoning_trace_examples.md
 *
 * Critical rules:
 *   - Each step's "conclusion" MUST render as a prose paragraph.
 *     NOT JSON. NOT timestamped function labels.
 *   - DocumentAnalyzer steps with citations show them with Foundry IQ attribution.
 *   - ConflictDetector steps with a conflict show the severity header before prose.
 *   - [MOCK MODE] banner displayed if isMockMode=true (docs/reliability_spec.md §1).
 *   - "powered by Azure Foundry IQ" footer attribution always visible.
 *
 * Props:
 *   steps        — TraceStep[]  (the subset visible so far)
 *   phase        — 'idle'|'scanning'|'done'
 *   isMockMode   — boolean
 *   currentStep  — number  (index of the last step currently being shown)
 */

import React, { useRef, useEffect } from 'react';

// ─── Citation row inside a DocumentAnalyzer step ──────────────────────────────
function CitationRow({ citation }) {
  const confPct = Math.round(citation.confidence * 100);
  const confLabel = confPct >= 85 ? 'high' : confPct >= 65 ? 'medium' : 'low';
  const shortPassage =
    citation.passage.length > 90
      ? citation.passage.slice(0, 90) + '…'
      : citation.passage;

  return (
    <div style={{ marginLeft: 14, marginBottom: 5 }}>
      <div
        style={{
          color: '#FAC775',
          fontSize: 10,
          fontFamily: 'monospace',
          lineHeight: 1.4,
        }}
      >
        ┌ {citation.document} {citation.section}{' '}
        <span style={{ color: 'rgba(255,255,255,0.28)' }}>
          [Foundry IQ · {confLabel} confidence]
        </span>
      </div>
      <div
        style={{
          color: 'rgba(255,255,255,0.48)',
          marginLeft: 10,
          fontSize: 10,
          fontFamily: 'monospace',
          fontStyle: 'italic',
          lineHeight: 1.5,
        }}
      >
        └ "{shortPassage}"
      </div>
    </div>
  );
}

// ─── Single trace step ────────────────────────────────────────────────────────
function TraceStepRow({ step, isLatest }) {
  const isCritical = step.severity === 'CRITICAL';
  const isConflictStep = !!step.severity;

  return (
    <div
      style={{
        marginBottom: 14,
        animation: 'fadeInUp 0.35s ease',
      }}
    >
      {/* Agent header row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          marginBottom: 5,
          flexWrap: 'wrap',
        }}
      >
        <span
          style={{
            color: 'rgba(255,255,255,0.3)',
            fontSize: 10,
            fontFamily: 'monospace',
          }}
        >
          [{step.time}]
        </span>
        <span
          style={{
            color: step.agentColor,
            fontWeight: 700,
            fontSize: 11,
            fontFamily: 'monospace',
          }}
        >
          {step.agent}
        </span>
        {step.query && (
          <span
            style={{
              color: 'rgba(255,255,255,0.32)',
              fontSize: 10,
              fontFamily: 'monospace',
            }}
          >
            → querying: "{step.query}"
          </span>
        )}
      </div>

      {/* Citations (DocumentAnalyzer steps) */}
      {step.citations &&
        step.citations.map((cit, i) => (
          <CitationRow key={i} citation={cit} />
        ))}

      {/* Prose conclusion (ConflictDetector, ImpactAssessor, etc.) */}
      {step.conclusion && (
        <div style={{ marginLeft: 14 }}>
          {/* Severity header — only for conflict-detection steps */}
          {isConflictStep && (
            <div
              style={{
                fontFamily: 'monospace',
                fontSize: 10,
                fontWeight: 700,
                marginBottom: 5,
                color: isCritical ? '#F09595' : '#FAC775',
                letterSpacing: '0.4px',
              }}
            >
              →{step.isSurprise ? ' UNEXPECTED' : ''} CONFLICT DETECTED [{step.severity}] —{' '}
              {step.confidence}% confidence
            </div>
          )}

          {/* Prose paragraph — NEVER JSON, NEVER timestamps */}
          <div
            style={{
              color: 'rgba(255,255,255,0.72)',
              fontSize: 11,
              lineHeight: 1.85,
              fontFamily: 'monospace',
              background: step.isSurprise
                ? 'rgba(242,102,102,0.08)'
                : isCritical
                ? 'rgba(255,255,255,0.04)'
                : 'rgba(255,255,255,0.03)',
              padding: '8px 10px',
              borderRadius: 4,
              borderLeft: step.isSurprise
                ? '2px solid #F09595'
                : isCritical
                ? '2px solid rgba(242,75,74,0.45)'
                : isConflictStep
                ? '2px solid rgba(250,199,117,0.5)'
                : '2px solid rgba(255,255,255,0.1)',
              whiteSpace: 'pre-wrap',
            }}
          >
            {step.conclusion}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── ReasoningTrace ───────────────────────────────────────────────────────────

/**
 * @param {{
 *   steps: object[],
 *   phase: 'idle'|'scanning'|'done',
 *   isMockMode: boolean,
 *   currentStep: number,
 * }} props
 */
export default function ReasoningTrace({ steps, phase, isMockMode, currentStep }) {
  const traceBodyRef = useRef(null);

  // Auto-scroll to bottom as new steps appear
  useEffect(() => {
    if (traceBodyRef.current) {
      traceBodyRef.current.scrollTop = traceBodyRef.current.scrollHeight;
    }
  }, [currentStep]);

  const isRunning = phase === 'scanning';
  const isDone    = phase === 'done';

  return (
    <div
      style={{
        borderLeft: '0.5px solid rgba(255,255,255,0.07)',
        background: '#18181B',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        width: 340,
        flexShrink: 0,
      }}
    >
      {/* ── Panel header ───────────────────────────────────────────────── */}
      <div
        style={{
          padding: '10px 14px',
          borderBottom: '0.5px solid rgba(255,255,255,0.07)',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          flexShrink: 0,
        }}
      >
        {/* Status dot */}
        <div
          style={{
            width: 7,
            height: 7,
            borderRadius: '50%',
            background: isRunning ? '#EF9F27' : isDone ? '#639922' : '#444441',
            transition: 'background 0.4s',
            animation: isRunning ? 'pulse 1s infinite' : 'none',
            flexShrink: 0,
          }}
        />
        <span
          style={{
            fontFamily: 'monospace',
            fontSize: 10,
            fontWeight: 600,
            color: 'rgba(255,255,255,0.45)',
            letterSpacing: '0.6px',
          }}
        >
          REASONING TRACE
        </span>

        {/* Running / Complete label */}
        {isDone && (
          <span
            style={{
              marginLeft: 'auto',
              fontFamily: 'monospace',
              fontSize: 10,
              color: '#97C459',
            }}
          >
            ✓ COMPLETE
          </span>
        )}
        {isRunning && (
          <span
            style={{
              marginLeft: 'auto',
              fontFamily: 'monospace',
              fontSize: 10,
              color: '#EF9F27',
            }}
          >
            ● RUNNING
          </span>
        )}
      </div>

      {/* ── Mock Mode banner ────────────────────────────────────────────── */}
      {isMockMode && (
        <div
          style={{
            padding: '4px 14px',
            background: 'rgba(250,199,117,0.12)',
            borderBottom: '0.5px solid rgba(250,199,117,0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          <span style={{ fontFamily: 'monospace', fontSize: 9, color: '#FAC775' }}>
            ⚠ [MOCK MODE] — Live API unavailable. Displaying pre-computed responses.
          </span>
        </div>
      )}

      {/* ── Trace body ──────────────────────────────────────────────────── */}
      <div
        ref={traceBodyRef}
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '12px 14px',
        }}
      >
        {/* Idle placeholder */}
        {phase === 'idle' && (
          <div
            style={{
              textAlign: 'center',
              paddingTop: 40,
              fontFamily: 'monospace',
              fontSize: 11,
              color: 'rgba(255,255,255,0.18)',
              lineHeight: 1.8,
            }}
          >
            reasoning trace will appear here
            <br />
            during analysis
          </div>
        )}

        {/* Rendered trace steps */}
        {steps.map((step, i) => (
          <React.Fragment key={i}>
            <TraceStepRow step={step} isLatest={i === currentStep} />
            {/* Divider between steps (not after last) */}
            {i < steps.length - 1 && (
              <div
                style={{
                  borderTop: '0.5px solid rgba(255,255,255,0.05)',
                  marginBottom: 12,
                }}
              />
            )}
          </React.Fragment>
        ))}

        {/* Analysis complete footer message */}
        {isDone && (
          <div
            style={{
              marginTop: 10,
              padding: '8px 10px',
              background: 'rgba(99,153,34,0.1)',
              borderRadius: 4,
              borderLeft: '2px solid #639922',
              animation: 'fadeInUp 0.3s ease',
            }}
          >
            <span
              style={{
                fontFamily: 'monospace',
                color: '#97C459',
                fontSize: 10,
              }}
            >
              analysis complete · 9 conflicts · all pending human review · no autonomous action taken
            </span>
          </div>
        )}
      </div>

      {/* ── Footer: Foundry IQ attribution ──────────────────────────────── */}
      <div
        style={{
          padding: '8px 14px',
          borderTop: '0.5px solid rgba(255,255,255,0.07)',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          flexShrink: 0,
        }}
      >
        <span
          style={{
            fontFamily: 'monospace',
            fontSize: 9,
            color: 'rgba(255,255,255,0.25)',
          }}
        >
          powered by
        </span>
        <span
          style={{
            fontFamily: 'monospace',
            fontSize: 9,
            fontWeight: 700,
            color: '#378ADD',
          }}
        >
          Azure Foundry IQ
        </span>
        <span
          style={{
            fontFamily: 'monospace',
            fontSize: 9,
            color: 'rgba(255,255,255,0.2)',
          }}
        >
          · every citation grounded · auditable
        </span>
      </div>
    </div>
  );
}
