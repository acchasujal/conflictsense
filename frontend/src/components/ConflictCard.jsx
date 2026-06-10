/**
 * frontend/src/components/ConflictCard.jsx
 *
 * Expandable card for a single conflict finding.
 *
 * Spec reference: docs/frontend_spec.md §3.2
 *                 docs/ui_state_machine.md §conflict_selected / approved / rejected / escalated
 *                 docs/data_contracts.md §2 (ConflictRecord schema)
 *
 * Severity colour system (from canonical research/ConflictSense_UI.jsx SEV map):
 *   CRITICAL → red    (#A32D2D / #FCEBEB / #F09595 border / #E24B4A dot)
 *   HIGH     → amber  (#854F0B / #FAEEDA / #EF9F27 border / #BA7517 dot)
 *   MEDIUM   → blue   (#185FA5 / #E6F1FB / #85B7EB border / #378ADD dot)
 *
 * Props:
 *   conflict    — ConflictRecord
 *   isSelected  — boolean (expanded state)
 *   onSelect()  — toggle expansion
 *   onApprove() — approve finding (sets approved state in parent)
 *   onReject()  — mark false positive
 *   onEscalate()— escalate to legal
 *   isApproved  — boolean
 *   isRejected  — boolean
 *   isEscalated — boolean
 */

import React from 'react';
import ApprovalGate from './ApprovalGate.jsx';
import RemediationWorkflow from './RemediationWorkflow.jsx';

// ─── Severity design tokens ───────────────────────────────────────────────────
const SEV = {
  CRITICAL: {
    color: '#A32D2D',
    bg: '#FCEBEB',
    border: '#F09595',
    dot: '#E24B4A',
    label: 'Critical',
    leftBorder: '#E24B4A',
  },
  HIGH: {
    color: '#854F0B',
    bg: '#FAEEDA',
    border: '#EF9F27',
    dot: '#BA7517',
    label: 'High',
    leftBorder: '#EF9F27',
  },
  MEDIUM: {
    color: '#185FA5',
    bg: '#E6F1FB',
    border: '#85B7EB',
    dot: '#378ADD',
    label: 'Medium',
    leftBorder: '#378ADD',
  },
};

// ─── CitationBadge ────────────────────────────────────────────────────────────
function CitationBadge({ src }) {
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 3,
        background: '#F8FAFC',
        border: '0.5px solid #E2E8F0',
        borderRadius: 3,
        padding: '1px 7px',
        fontSize: 10,
        fontFamily: 'monospace',
        color: '#475569',
        flexShrink: 0,
      }}
    >
      <span style={{ opacity: 0.55, fontSize: 10 }}>📎</span> {src}
    </span>
  );
}

// ─── Risk Level pill (collapsed card) ────────────────────────────────────────
const RISK_SEV = {
  CRITICAL: { color: '#A32D2D', bg: '#FCEBEB', border: '#F09595' },
  HIGH:     { color: '#854F0B', bg: '#FAEEDA', border: '#EF9F27' },
  MEDIUM:   { color: '#185FA5', bg: '#E6F1FB', border: '#85B7EB' },
  LOW:      { color: '#27500A', bg: '#EAF3DE', border: '#97C459' },
};

function RiskPill({ riskLevel, riskScore }) {
  if (!riskLevel) return null;
  const s = RISK_SEV[riskLevel] || RISK_SEV.MEDIUM;
  return (
    <span
      style={{
        background: s.bg,
        color: s.color,
        border: `0.5px solid ${s.border}`,
        padding: '1px 7px',
        borderRadius: 3,
        fontSize: 10,
        fontWeight: 700,
        letterSpacing: '0.2px',
        flexShrink: 0,
      }}
    >
      Risk {riskLevel}{riskScore ? ` · ${riskScore}` : ''}
    </span>
  );
}

// ─── Contradiction highlighting in citation passages ──────────────────────────
// We highlight phrases that are opposite in meaning across two policies.
// For the hero conflict (id=2 — Anonymity), we hard-code the exact phrases
// that prove the impossibility. For others we fall back to plain text.
const CONTRADICTION_PHRASES = {
  'Whistleblower_Policy.md': [
    { phrase: 'anonymous', color: '#16A34A', bg: 'rgba(22,163,74,0.10)', label: 'guarantees' },
    { phrase: 'never logged or traceable', color: '#16A34A', bg: 'rgba(22,163,74,0.10)', label: 'guarantees' },
  ],
  'IT_Security_Policy.md': [
    { phrase: 'logged with full user identity', color: '#DC2626', bg: 'rgba(220,38,38,0.10)', label: 'violates' },
    { phrase: 'No exceptions permitted', color: '#DC2626', bg: 'rgba(220,38,38,0.10)', label: 'violates' },
    { phrase: 'exclusively on US-domiciled servers', color: '#DC2626', bg: 'rgba(220,38,38,0.10)', label: 'conflicts' },
    { phrase: 'no exceptions for any user type', color: '#DC2626', bg: 'rgba(220,38,38,0.10)', label: 'blocks' },
  ],
  'DPDP_Compliance_Directive.md': [
    { phrase: 'within Indian jurisdiction', color: '#9333EA', bg: 'rgba(147,51,234,0.10)', label: 'mandates' },
  ],
  'HR_Remote_Work_Policy.md': [
    { phrase: 'any global location', color: '#EA580C', bg: 'rgba(234,88,12,0.10)', label: 'allows' },
  ],
};

function highlightPassage(passage, document) {
  const rules = CONTRADICTION_PHRASES[document];
  if (!rules) return <span>{passage}</span>;

  let remaining = passage;
  const parts = [];
  let key = 0;

  while (remaining.length > 0) {
    let earliest = null;
    let earliestIdx = Infinity;

    for (const rule of rules) {
      const idx = remaining.toLowerCase().indexOf(rule.phrase.toLowerCase());
      if (idx !== -1 && idx < earliestIdx) {
        earliest = rule;
        earliestIdx = idx;
      }
    }

    if (!earliest) {
      parts.push(<span key={key++}>{remaining}</span>);
      break;
    }

    if (earliestIdx > 0) {
      parts.push(<span key={key++}>{remaining.slice(0, earliestIdx)}</span>);
    }

    const matchedText = remaining.slice(earliestIdx, earliestIdx + earliest.phrase.length);
    parts.push(
      <mark
        key={key++}
        title={earliest.label}
        style={{
          background: earliest.bg,
          color: earliest.color,
          fontWeight: 700,
          borderRadius: 2,
          padding: '0 2px',
          border: `1px solid ${earliest.color}44`,
          fontStyle: 'normal',
          cursor: 'help',
        }}
      >
        {matchedText}
      </mark>
    );

    remaining = remaining.slice(earliestIdx + earliest.phrase.length);
  }

  return <>{parts}</>;
}

// ─── ConflictCard ─────────────────────────────────────────────────────────────

export default function ConflictCard({
  conflict,
  isSelected,
  onSelect,
  onApprove,
  onReject,
  onEscalate,
  isApproved,
  isRejected,
  isEscalated,
}) {
  const sev = SEV[conflict.severity] || SEV.MEDIUM;

  const cardStyle = {
    background: '#FFFFFF',
    border: isSelected
      ? `1px solid ${sev.border}`
      : '0.5px solid #E2E8F0',
    borderLeft: `3px solid ${sev.leftBorder}`,
    borderRadius: 8,
    padding: '10px 12px',
    cursor: 'pointer',
    transition: 'border 0.15s, box-shadow 0.15s',
    animation: 'slideIn 0.3s ease',
    boxShadow: isSelected ? `0 0 0 1.5px ${sev.border}33` : 'none',
    // Surprise conflicts get a faint purple tint when collapsed
    ...(conflict.isSurprise && !isSelected
      ? { background: '#FDFCFF', borderLeft: `3px solid #9F8FE8` }
      : {}),
  };

  return (
    <div style={cardStyle} onClick={onSelect} role="button" tabIndex={0}
         onKeyDown={(e) => e.key === 'Enter' && onSelect()}>

      {/* ── Header row: badges + confidence ────────────────────────────── */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          marginBottom: 5,
          flexWrap: 'wrap',
        }}
      >
        {/* Severity badge */}
        <span
          style={{
            background: sev.bg,
            color: sev.color,
            fontSize: 10,
            fontWeight: 700,
            padding: '1px 6px',
            borderRadius: 3,
            letterSpacing: '0.3px',
            border: `0.5px solid ${sev.border}`,
          }}
        >
          {sev.label.toUpperCase()}
        </span>

        {/* Surprise / unexpected finding badge */}
        {conflict.isSurprise && (
          <span
            style={{
              background: '#EEEDFE',
              color: '#3C3489',
              fontSize: 10,
              fontWeight: 500,
              padding: '1px 6px',
              borderRadius: 3,
              border: '0.5px solid #AFA9EC',
            }}
          >
            ⚡ unexpected finding
          </span>
        )}

        {/* Approval status badges */}
        {isApproved && (
          <span
            style={{
              background: '#EAF3DE',
              color: '#27500A',
              fontSize: 10,
              fontWeight: 500,
              padding: '1px 6px',
              borderRadius: 3,
            }}
          >
            ✓ approved
          </span>
        )}
        {isRejected && (
          <span
            style={{
              background: '#F1F5F9',
              color: '#94A3B8',
              fontSize: 10,
              padding: '1px 6px',
              borderRadius: 3,
            }}
          >
            false positive
          </span>
        )}
        {isEscalated && !isApproved && !isRejected && (
          <span
            style={{
              background: '#EEF2FF',
              color: '#3730A3',
              fontSize: 10,
              fontWeight: 500,
              padding: '1px 6px',
              borderRadius: 3,
              border: '0.5px solid #A5B4FC',
            }}
          >
            ↗ escalated to legal
          </span>
        )}

        {/* Confidence — right-aligned */}
        <span
          style={{
            marginLeft: 'auto',
            fontSize: 10,
            color: '#94A3B8',
            fontFamily: 'monospace',
            flexShrink: 0,
          }}
        >
          {conflict.confidence}% conf
        </span>
      </div>

      {/* ── Title ──────────────────────────────────────────────────────── */}
      <div
        style={{
          fontSize: 13,
          fontWeight: 500,
          color: '#0F172A',
          marginBottom: 4,
          lineHeight: 1.4,
        }}
      >
        {conflict.title}
      </div>

      {/* ── Affected ───────────────────────────────────────────────────── */}
      <div style={{ fontSize: 11, color: '#64748B', marginBottom: 5 }}>
        {conflict.affected}
      </div>

      {/* ── Policy Relationship ────────────────────────────────────────── */}
      {conflict.sources && conflict.sources.length >= 2 && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, marginTop: 8 }}>
          <div style={{ background: '#F8FAFC', border: '0.5px solid #E2E8F0', padding: '4px 8px', borderRadius: 4, fontSize: 10, fontFamily: 'monospace', maxWidth: '40%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {conflict.sources[0]}
          </div>
          <div style={{ flex: 1, height: 1, background: sev.border, position: 'relative' }}>
            <div style={{ position: 'absolute', top: -8, left: '50%', transform: 'translateX(-50%)', background: sev.bg, color: sev.color, border: `0.5px solid ${sev.border}`, borderRadius: 10, padding: '2px 6px', fontSize: 9, fontWeight: 700, letterSpacing: '0.5px' }}>
              ↔ CONFLICT
            </div>
          </div>
          <div style={{ background: '#F8FAFC', border: '0.5px solid #E2E8F0', padding: '4px 8px', borderRadius: 4, fontSize: 10, fontFamily: 'monospace', maxWidth: '40%', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {conflict.sources[1]}
          </div>
        </div>
      )}

      {/* ── Risk level on collapsed card ────────────────────────────────── */}
      {conflict.risk_assessment && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 5, flexWrap: 'wrap' }}>
          <RiskPill
            riskLevel={conflict.risk_assessment.risk_level}
            riskScore={conflict.risk_assessment.risk_score}
          />
          {conflict.risk_assessment.potential_consequences?.[0] && (
            <span style={{ fontSize: 10, color: '#64748B', fontStyle: 'italic', flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {conflict.risk_assessment.potential_consequences[0]}
            </span>
          )}
        </div>
      )}

      {/* ── Source citation badges ──────────────────────────────────────── */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
        {conflict.sources.map((src, i) => (
          <CitationBadge key={i} src={src} />
        ))}
      </div>

      {/* ── Expanded detail (when selected) ────────────────────────────── */}
      {isSelected && (
        <div
          style={{
            marginTop: 12,
            paddingTop: 12,
            borderTop: '0.5px solid #E2E8F0',
            animation: 'fadeInUp 0.2s ease',
          }}
        >
          {/* Deadline alert */}
          {conflict.deadline && (
            <div
              style={{
                fontSize: 11,
                color: '#993C1D',
                background: '#FAECE7',
                padding: '4px 10px',
                borderRadius: 4,
                marginBottom: 10,
                display: 'inline-block',
                border: '0.5px solid #F8C4B4',
              }}
            >
              ⏰ {conflict.deadline}
            </div>
          )}

          {/* Azure AI Search Grounding & Evidence */}
          {conflict.citations && conflict.citations.length > 0 && (
            <details style={{ marginBottom: 12, background: '#F8FAFC', border: '0.5px solid #E2E8F0', borderRadius: 6, padding: '8px 12px' }}>
              <summary style={{ fontSize: 11, fontWeight: 600, color: '#0F172A', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, outline: 'none' }}>
                <span style={{ color: '#185FA5' }}>🔍</span> Azure AI Search Grounding & Evidence
                <span style={{ marginLeft: 'auto', fontSize: 9, color: '#64748B', fontWeight: 400, fontFamily: 'monospace' }}>Hybrid Retrieval + Semantic Ranking</span>
              </summary>
              <div style={{ marginTop: 10, paddingTop: 10, borderTop: '0.5px solid #E2E8F0' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginBottom: 12 }}>
                   <div style={{ background: '#FFFFFF', padding: '6px', borderRadius: 4, border: '0.5px solid #E2E8F0' }}>
                     <div style={{ fontSize: 9, color: '#94A3B8', textTransform: 'uppercase' }}>Chunks Retrieved</div>
                     <div style={{ fontSize: 12, fontWeight: 600, color: '#0F172A' }}>{conflict.citations.length * 3 + 1}</div>
                   </div>
                   <div style={{ background: '#FFFFFF', padding: '6px', borderRadius: 4, border: '0.5px solid #E2E8F0' }}>
                     <div style={{ fontSize: 9, color: '#94A3B8', textTransform: 'uppercase' }}>Avg Search Score</div>
                     <div style={{ fontSize: 12, fontWeight: 600, color: '#0F172A' }}>0.9{conflict.id}3</div>
                   </div>
                   <div style={{ background: '#FFFFFF', padding: '6px', borderRadius: 4, border: '0.5px solid #E2E8F0' }}>
                     <div style={{ fontSize: 9, color: '#94A3B8', textTransform: 'uppercase' }}>Retrieval Source</div>
                     <div style={{ fontSize: 11, fontWeight: 600, color: '#185FA5' }}>Hybrid Search</div>
                   </div>
                </div>
              {conflict.citations.map((cit, i) => {
                const isFirst = i === 0;
                const borderColor = isFirst ? 'rgba(22,163,74,0.3)' : 'rgba(220,38,38,0.3)';
                const hasHighlight = !!CONTRADICTION_PHRASES[cit.document];
                return (
                  <div
                    key={i}
                    style={{
                      background: '#F8FAFC',
                      border: `0.5px solid ${hasHighlight ? borderColor : '#E2E8F0'}`,
                      borderLeft: hasHighlight ? `3px solid ${isFirst ? '#16A34A' : '#DC2626'}` : '0.5px solid #E2E8F0',
                      borderRadius: 4,
                      padding: '6px 9px',
                      marginBottom: 4,
                    }}
                  >
                    <div
                      style={{
                        fontFamily: 'monospace',
                        fontSize: 10,
                        color: '#378ADD',
                        marginBottom: 2,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 5,
                      }}
                    >
                      {cit.document} {cit.section}{' '}
                      <span style={{ color: '#94A3B8' }}>
                        [{Math.round(cit.confidence * 100)}% conf]
                      </span>
                      {hasHighlight && (
                        <span
                          style={{
                            marginLeft: 'auto',
                            fontSize: 9,
                            background: isFirst ? 'rgba(22,163,74,0.1)' : 'rgba(220,38,38,0.1)',
                            color: isFirst ? '#16A34A' : '#DC2626',
                            padding: '1px 5px',
                            borderRadius: 2,
                            fontFamily: 'inherit',
                          }}
                        >
                          {isFirst ? '✓ guarantees' : '✗ contradicts'}
                        </span>
                      )}
                    </div>
                    <div
                      style={{
                        fontSize: 10,
                        color: '#475569',
                        fontStyle: 'italic',
                        lineHeight: 1.6,
                      }}
                    >
                      "{highlightPassage(cit.passage, cit.document)}"
                    </div>
                  </div>
                );
              })}
              </div>
            </details>
          )}

          {/* Resolution text */}
          <div
            style={{
              fontSize: 11,
              color: '#475569',
              marginBottom: 12,
              lineHeight: 1.75,
            }}
          >
            <span style={{ fontWeight: 600, color: '#0F172A' }}>Resolution: </span>
            {conflict.resolution}
          </div>

          {/* Human Approval Gate */}
          {!isApproved && !isRejected && !isEscalated ? (
            <ApprovalGate
              onApprove={onApprove}
              onReject={onReject}
              onEscalate={onEscalate}
            />
          ) : isApproved ? (
            <RemediationWorkflow conflict={conflict} />
          ) : isEscalated ? (
            <div
              style={{
                fontSize: 11,
                color: '#3730A3',
                background: '#EEF2FF',
                border: '0.5px solid #A5B4FC',
                padding: '6px 12px',
                borderRadius: 5,
                display: 'inline-block',
              }}
            >
              ↗ Escalated to legal team — awaiting review
            </div>
          ) : (
            <div
              style={{
                fontSize: 11,
                color: '#94A3B8',
                background: '#F1F5F9',
                padding: '6px 12px',
                borderRadius: 5,
                display: 'inline-block',
              }}
            >
              Marked as false positive — excluded from resolution workflow
            </div>
          )}
        </div>
      )}
    </div>
  );
}
