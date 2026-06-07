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
      <div style={{ fontSize: 11, color: '#64748B', marginBottom: 6 }}>
        {conflict.affected}
      </div>

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

          {/* Foundry IQ citation details */}
          {conflict.citations && conflict.citations.length > 0 && (
            <div style={{ marginBottom: 10 }}>
              <div
                style={{
                  fontSize: 10,
                  fontWeight: 600,
                  color: '#94A3B8',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  marginBottom: 5,
                }}
              >
                Foundry IQ Citations
              </div>
              {conflict.citations.map((cit, i) => (
                <div
                  key={i}
                  style={{
                    background: '#F8FAFC',
                    border: '0.5px solid #E2E8F0',
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
                    }}
                  >
                    {cit.document} {cit.section}{' '}
                    <span style={{ color: '#94A3B8' }}>
                      [{Math.round(cit.confidence * 100)}% conf]
                    </span>
                  </div>
                  <div
                    style={{
                      fontSize: 10,
                      color: '#475569',
                      fontStyle: 'italic',
                      lineHeight: 1.5,
                    }}
                  >
                    "{cit.passage}"
                  </div>
                </div>
              ))}
            </div>
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
            <div
              style={{
                fontSize: 11,
                color: '#27500A',
                background: '#EAF3DE',
                border: '0.5px solid #97C459',
                padding: '6px 12px',
                borderRadius: 5,
                display: 'inline-block',
              }}
            >
              ✓ Finding approved — entering resolution workflow
            </div>
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
