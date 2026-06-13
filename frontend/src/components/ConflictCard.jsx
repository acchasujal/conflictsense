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

function parseStructuredText(text) {
  if (typeof text === 'object') return text;
  try {
    const cleaned = text.replace(/```json/gi, '').replace(/```/g, '').trim();
    return JSON.parse(cleaned);
  } catch (e) {
    return { summary: text };
  }
}

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
  let rules = CONTRADICTION_PHRASES[document];
  if (!rules) {
    rules = [
      { phrase: 'must', color: '#EA580C', bg: 'rgba(234,88,12,0.10)', label: 'modal' },
      { phrase: 'shall', color: '#EA580C', bg: 'rgba(234,88,12,0.10)', label: 'modal' },
      { phrase: 'prohibited', color: '#DC2626', bg: 'rgba(220,38,38,0.10)', label: 'violates' },
      { phrase: 'always', color: '#9333EA', bg: 'rgba(147,51,234,0.10)', label: 'mandates' },
      { phrase: 'never', color: '#DC2626', bg: 'rgba(220,38,38,0.10)', label: 'blocks' },
      { phrase: 'required', color: '#16A34A', bg: 'rgba(22,163,74,0.10)', label: 'mandates' },
      { phrase: 'no exceptions', color: '#DC2626', bg: 'rgba(220,38,38,0.10)', label: 'blocks' },
    ];
  }

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
  traceId,
}) {
  const sev = SEV[conflict.severity] || SEV.MEDIUM;

  const cardStyle = {
    background: '#FFFFFF',
    border: isSelected ? `1px solid ${sev.border}` : '0.5px solid #E2E8F0',
    borderLeft: `3px solid ${sev.leftBorder}`,
    borderRadius: 8,
    padding: '16px',
    cursor: 'pointer',
    transition: 'border 0.15s, box-shadow 0.15s',
    animation: 'slideIn 0.3s ease',
    boxShadow: isSelected ? `0 0 0 1.5px ${sev.border}33` : 'none',
    ...(conflict.isSurprise && !isSelected
      ? { background: '#FDFCFF', borderLeft: `3px solid #9F8FE8` }
      : {}),
  };

  const policyA = conflict.citations && conflict.citations[0] ? conflict.citations[0] : null;
  const policyB = conflict.citations && conflict.citations[1] ? conflict.citations[1] : null;

  const resultText = conflict.risk_assessment?.reasoning || conflict.affected;
  const affectedEntities = conflict.risk_assessment?.affected_entities?.join(', ') || "Unknown";
  const riskText = conflict.human_impact || "Not specified";

  return (
    <div style={cardStyle} onClick={onSelect} role="button" tabIndex={0}
         aria-expanded={isSelected} aria-label={`Conflict finding: ${conflict.title}`}>

      {/* Hero Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 16 }}>🚨</span>
          <span style={{ fontSize: 12, fontWeight: 800, color: sev.color, letterSpacing: '0.5px', textTransform: 'uppercase' }}>
            {conflict.severity} POLICY CONTRADICTION
          </span>
          {isApproved && <span style={{ background: '#EAF3DE', color: '#27500A', fontSize: 10, fontWeight: 500, padding: '1px 6px', borderRadius: 3 }}>✓ approved</span>}
          {isRejected && <span style={{ background: '#F1F5F9', color: '#94A3B8', fontSize: 10, padding: '1px 6px', borderRadius: 3 }}>false positive</span>}
        </div>
        <span style={{ fontSize: 11, color: '#94A3B8', fontFamily: 'monospace' }}>{conflict.confidence}% conf</span>
      </div>

      <div style={{ fontSize: 15, fontWeight: 600, color: '#0F172A', marginBottom: 16 }}>
        {conflict.title}
      </div>

      {/* Visual Policy A vs B Contradiction */}
      {policyA && policyB && (
        <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: 6, padding: '12px', marginBottom: 16 }}>
          {/* Policy A */}
          <div style={{ padding: '8px', background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: 4 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#334155', marginBottom: 4 }}>
              {policyA.document} {policyA.section}
            </div>
            <div style={{ fontSize: 13, color: '#475569', fontStyle: 'italic', lineHeight: 1.5 }}>
              "{highlightPassage(policyA.passage, policyA.document)}"
            </div>
          </div>

          {/* Arrow / Conflict indicator */}
          <div style={{ display: 'flex', justifyContent: 'center', margin: '8px 0', position: 'relative' }}>
            <div style={{ position: 'absolute', top: '50%', left: 0, right: 0, height: 1, background: '#CBD5E1', zIndex: 0 }} />
            <div style={{ background: '#F8FAFC', padding: '0 8px', zIndex: 1 }}>
              <span style={{ background: sev.bg, color: sev.color, border: `1px solid ${sev.border}`, borderRadius: 12, padding: '2px 8px', fontSize: 10, fontWeight: 700, letterSpacing: '0.5px', display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ fontSize: 12 }}>⚠</span> CONFLICT
              </span>
            </div>
          </div>

          {/* Policy B */}
          <div style={{ padding: '8px', background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: 4 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#334155', marginBottom: 4 }}>
              {policyB.document} {policyB.section}
            </div>
            <div style={{ fontSize: 13, color: '#475569', fontStyle: 'italic', lineHeight: 1.5 }}>
              "{highlightPassage(policyB.passage, policyB.document)}"
            </div>
          </div>
        </div>
      )}

      {/* Consequence Summaries */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
        <div style={{ fontSize: 13, lineHeight: 1.5 }}>
          <span style={{ fontWeight: 700, color: '#0F172A' }}>Result: </span>
          <span style={{ color: '#475569' }}>{resultText}</span>
        </div>
        <div style={{ fontSize: 13, lineHeight: 1.5 }}>
          <span style={{ fontWeight: 700, color: '#0F172A' }}>Affected: </span>
          <span style={{ color: '#475569' }}>{affectedEntities}</span>
        </div>
        <div style={{ fontSize: 13, lineHeight: 1.5 }}>
          <span style={{ fontWeight: 700, color: '#0F172A' }}>Risk: </span>
          <span style={{ color: '#475569' }}>{riskText}</span>
        </div>
      </div>

      {/* Expand/Collapse Toggle */}
      <div style={{ borderTop: '1px solid #E2E8F0', paddingTop: 12, display: 'flex', justifyContent: 'center' }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: '#2563EB' }}>
          {isSelected ? 'Hide Reasoning ▲' : '[Expand Reasoning] ▼'}
        </span>
      </div>

      {/* ── Expanded detail (when selected) ────────────────────────────── */}
      {isSelected && (
        <div
          style={{
            marginTop: 12,
            paddingTop: 16,
            borderTop: '0.5px solid #E2E8F0',
            animation: 'fadeInDown 0.3s ease',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Detailed Reasoning section */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#0F172A', marginBottom: 8, textTransform: 'uppercase' }}>
              System Reasoning
            </div>
            <div style={{ fontSize: 13, color: '#334155', lineHeight: 1.6, background: '#F8FAFC', padding: 12, borderRadius: 6, border: '1px solid #E2E8F0' }}>
              {conflict.risk_assessment?.reasoning || conflict.affected}
            </div>
          </div>

          {/* Remediation */}
          <RemediationWorkflow conflict={conflict} />

          {/* Approval Gate */}
          <ApprovalGate
            isApproved={isApproved}
            isRejected={isRejected}
            isEscalated={isEscalated}
            onApprove={onApprove}
            onReject={onReject}
            onEscalate={onEscalate}
            traceId={traceId}
          />
        </div>
      )}
    </div>
  );
}
