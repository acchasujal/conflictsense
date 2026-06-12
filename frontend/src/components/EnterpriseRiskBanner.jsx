/**
 * frontend/src/components/EnterpriseRiskBanner.jsx
 *
 * Enterprise Risk Summary Banner — top-level panel displayed when at least one
 * conflict has been detected.
 *
 * Purpose: A judge should understand enterprise impact within 3 seconds.
 * This component surfaces the highest-severity conflict's risk level, the total
 * risk score across all findings, and the single most critical consequence —
 * without requiring any card expansion.
 *
 * Spec reference: docs/judging_alignment.md (Enterprise Value visibility)
 *
 * Props:
 *   conflicts — ConflictRecord[] (all currently visible conflicts)
 *   phase     — 'idle'|'scanning'|'done'
 */

import React from 'react';

// ─── Severity design tokens (mirrors ConflictCard.jsx SEV map) ────────────────
const SEV = {
  CRITICAL: { color: '#A32D2D', bg: '#FCEBEB', border: '#F09595', dot: '#E24B4A', label: 'CRITICAL' },
  HIGH:     { color: '#854F0B', bg: '#FAEEDA', border: '#EF9F27', dot: '#BA7517', label: 'HIGH'     },
  MEDIUM:   { color: '#185FA5', bg: '#E6F1FB', border: '#85B7EB', dot: '#378ADD', label: 'MEDIUM'   },
};

// Static consequence map keyed to conflict id — derived from precomputed_conflicts.json
// so there is zero new backend dependency.
const CONSEQUENCE_MAP = {
  '1': 'Systemic DPDP non-compliance: 34 employees unprotected · ₹250Cr fine exposure · July 1 deadline in 24 days',
  '2': 'Anonymity guarantee is legally promised but technically impossible — every whistleblower is traceable',
  '3': 'Security incidents may route to Legal only, bypassing CISO — FCA 72hr window at risk',
  '4': 'BYOD employees simultaneously required to delete AND retain the same data for 7 years',
  '5': 'Employees are entitled by policy to $5,000 relocation payments that Finance will not authorize',
  '6': 'Unsecured SaaS software approved by managers without mandatory IT Security sign-off',
  '7': 'Employee data must be destroyed in 12 months AND retained indefinitely — contradiction in policy',
  '8': 'Contractors may bypass mandatory MFA with a manager email — security control undermined',
  '9': 'Self-certified emergency expenses are both permitted and strictly prohibited in different policies',
};

// Compute an aggregate enterprise risk score from the visible conflicts.
// CRITICAL = 90, HIGH = 70, MEDIUM = 50, weighted average.
function computeEnterpriseRiskScore(conflicts) {
  if (!conflicts.length) return 0;
  const weights = { CRITICAL: 90, HIGH: 70, MEDIUM: 50 };
  const raw = conflicts.reduce((sum, c) => sum + (weights[c.severity] || 50), 0);
  return Math.min(100, Math.round(raw / conflicts.length));
}

// Determine the overall risk level label from the score.
function riskLevelFromScore(score) {
  if (score >= 85) return 'CRITICAL';
  if (score >= 70) return 'HIGH';
  if (score >= 50) return 'MEDIUM';
  return 'LOW';
}

// ─── EnterpriseRiskBanner ─────────────────────────────────────────────────────

export default function EnterpriseRiskBanner({ conflicts, phase }) {
  if (!conflicts || conflicts.length === 0) return null;
  // Only show when there is at least one conflict surfaced.
  if (phase === 'idle') return null;

  // Find highest severity conflict for hero display.
  const sevOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2 };
  const hero = [...conflicts].sort(
    (a, b) => (sevOrder[a.severity] ?? 3) - (sevOrder[b.severity] ?? 3)
  )[0];

  const sev = SEV[hero.severity] || SEV.MEDIUM;
  const riskScore = computeEnterpriseRiskScore(conflicts);
  const riskLevel = riskLevelFromScore(riskScore);
  const riskSev = SEV[riskLevel] || SEV.MEDIUM;
  const consequence = CONSEQUENCE_MAP[hero.id] || hero.affected;

  const critCount = conflicts.filter((c) => c.severity === 'CRITICAL').length;

  return (
    <div
      style={{
        background: '#FFFFFF',
        borderBottom: `2px solid ${sev.border}`,
        borderTop: 'none',
        padding: '10px 16px',
        display: 'flex',
        alignItems: 'stretch',
        gap: 0,
        flexShrink: 0,
        animation: 'slideIn 0.4s ease',
      }}
    >
      {/* ── Left: Critical alert strip ──────────────────────────────────── */}
      <div
        style={{
          background: sev.bg,
          border: `0.5px solid ${sev.border}`,
          borderRadius: 6,
          padding: '8px 14px',
          minWidth: 190,
          flexShrink: 0,
          marginRight: 14,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 3 }}>
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: sev.dot,
              display: 'inline-block',
              flexShrink: 0,
              animation: 'pulse 1.2s infinite',
            }}
          />
          <span
            style={{
              fontSize: 9,
              fontWeight: 700,
              color: sev.color,
              letterSpacing: '0.8px',
              textTransform: 'uppercase',
            }}
          >
            {sev.label} ENTERPRISE RISK
          </span>
        </div>
        <div style={{ fontSize: 12, fontWeight: 600, color: sev.color, lineHeight: 1.35 }}>
          {hero.title}
        </div>
        <div style={{ fontSize: 10, color: sev.color, opacity: 0.75, marginTop: 2 }}>
          {(hero.sources ?? []).slice(0, 2).join(' vs. ')}
        </div>
      </div>

      {/* ── Center: Consequence detail ───────────────────────────────────── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <div
          style={{
            fontSize: 10,
            fontWeight: 600,
            color: '#94A3B8',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: 4,
          }}
        >
          Primary Consequence
        </div>
        <div style={{ fontSize: 12, color: '#0F172A', lineHeight: 1.5, fontWeight: 500 }}>
          {consequence}
        </div>
        {hero.deadline && (
          <div
            style={{
              marginTop: 5,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 5,
              background: '#FAECE7',
              border: '0.5px solid #F8C4B4',
              padding: '2px 9px',
              borderRadius: 4,
              width: 'fit-content',
            }}
          >
            <span style={{ fontSize: 10, color: '#993C1D', fontWeight: 600 }}>
              ⏰ Compliance deadline: {hero.deadline}
            </span>
          </div>
        )}
      </div>

      {/* ── Right: Aggregate risk score ──────────────────────────────────── */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          justifyContent: 'center',
          flexShrink: 0,
          marginLeft: 14,
          gap: 4,
        }}
      >
        <div
          style={{
            fontSize: 9,
            fontWeight: 700,
            color: '#94A3B8',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
        >
          Enterprise Risk Score
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 5 }}>
          <span
            style={{
              fontSize: 28,
              fontWeight: 700,
              color: riskSev.color,
              lineHeight: 1,
              fontFamily: 'monospace',
            }}
          >
            {riskScore}
          </span>
          <span style={{ fontSize: 11, color: '#94A3B8', fontWeight: 500 }}>/100</span>
        </div>
        <span
          style={{
            background: riskSev.bg,
            color: riskSev.color,
            border: `0.5px solid ${riskSev.border}`,
            padding: '1px 8px',
            borderRadius: 4,
            fontSize: 10,
            fontWeight: 700,
            letterSpacing: '0.3px',
          }}
        >
          {riskLevel}
        </span>
        {critCount > 0 && (
          <div style={{ fontSize: 10, color: '#A32D2D', fontWeight: 600, marginTop: 1 }}>
            {critCount} critical finding{critCount > 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}
