/**
 * frontend/src/components/ConflictDashboard.jsx
 *
 * Left panel: document grid + conflict list.
 *
 * Spec reference: docs/frontend_spec.md §2 (Left Panel)
 *                 docs/ui_state_machine.md (idle / scanning / done states)
 *
 * Renders:
 *   - DocumentGrid — 7 tiles, always visible
 *   - Idle CTA     — shown only in "idle" phase
 *   - Conflict list — progressive reveal during scanning; fully visible in "done"
 */

import React from 'react';
import DocumentGrid from './DocumentGrid.jsx';
import ConflictCard from './ConflictCard.jsx';
import ExecutiveDashboard from './ExecutiveDashboard.jsx';
import CopilotExperience from './CopilotExperience.jsx';

const styles = {
  panel: {
    padding: '14px 14px 14px 16px',
    display: 'flex',
    flexDirection: 'column',
    gap: 14,
    overflow: 'auto',
    flex: 1,
  },
  idleCta: {
    textAlign: 'center',
    padding: '40px 20px',
    borderRadius: 10,
    border: '0.5px dashed #CBD5E1',
    color: '#94A3B8',
    animation: 'fadeInUp 0.3s ease',
  },
  idleEmoji: {
    fontSize: 28,
    marginBottom: 10,
    display: 'block',
  },
  idleHeading: {
    fontSize: 13,
    fontWeight: 500,
    color: '#64748B',
    marginBottom: 6,
  },
  idleBody: {
    fontSize: 12,
    maxWidth: 320,
    margin: '0 auto',
    lineHeight: 1.75,
    color: '#94A3B8',
  },
  deadlineAlert: {
    marginTop: 14,
    fontSize: 11,
    color: '#854F0B',
    background: '#FAEEDA',
    border: '0.5px solid #FAC775',
    padding: '6px 14px',
    borderRadius: 6,
    display: 'inline-block',
  },
  conflictsSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: 0,
  },
  conflictsSectionLabel: {
    fontSize: 10,
    fontWeight: 600,
    color: '#94A3B8',
    textTransform: 'uppercase',
    letterSpacing: '0.6px',
    marginBottom: 8,
    display: 'flex',
    alignItems: 'center',
    gap: 6,
  },
  conflictsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
  },
  summaryRow: {
    display: 'flex',
    gap: 6,
    flexWrap: 'wrap',
    marginTop: 10,
    paddingTop: 10,
    borderTop: '0.5px solid #E2E8F0',
  },
  summaryPill: (bg, color, border) => ({
    background: bg,
    color,
    border: `0.5px solid ${border}`,
    padding: '2px 9px',
    borderRadius: 4,
    fontSize: 11,
    fontWeight: 600,
  }),
};

// Severity summary counts
function SeveritySummary({ conflicts }) {
  const crit = conflicts.filter((c) => c.severity === 'CRITICAL').length;
  const high = conflicts.filter((c) => c.severity === 'HIGH').length;
  const med  = conflicts.filter((c) => c.severity === 'MEDIUM').length;
  if (!conflicts.length) return null;
  return (
    <div style={styles.summaryRow}>
      {crit > 0 && (
        <span style={styles.summaryPill('#FCEBEB', '#A32D2D', '#F09595')}>
          {crit} Critical
        </span>
      )}
      {high > 0 && (
        <span style={styles.summaryPill('#FAEEDA', '#854F0B', '#EF9F27')}>
          {high} High
        </span>
      )}
      {med > 0 && (
        <span style={styles.summaryPill('#E6F1FB', '#185FA5', '#85B7EB')}>
          {med} Medium
        </span>
      )}
    </div>
  );
}

/**
 * @param {{
 *   documents: object[],
 *   visibleConflicts: object[],
 *   phase: 'idle'|'scanning'|'done',
 *   totalConflicts: number,
 *   selectedId: string|null,
 *   approvedIds: Set<string>,
 *   rejectedIds: Set<string>,
 *   escalatedIds: Set<string>,
 *   onSelect: (id: string) => void,
 *   onApprove: (id: string) => void,
 *   onReject: (id: string) => void,
 *   onEscalate: (id: string) => void,
 *   onRunAnalysis: () => void,
 *   isAbstained: boolean,
 * }} props
 */
export default function ConflictDashboard({
  documents,
  visibleConflicts,
  phase,
  totalConflicts,
  selectedId,
  approvedIds,
  rejectedIds,
  escalatedIds,
  onSelect,
  onApprove,
  onReject,
  onEscalate,
  onRunAnalysis,
  isAbstained,
}) {
  return (
    <div style={styles.panel}>
      {/* Copilot Experience Panel */}
      <CopilotExperience onRunAnalysis={onRunAnalysis} />

      {/* Executive Dashboard */}
      <ExecutiveDashboard phase={phase} />

      {/* Document grid — always visible */}
      <DocumentGrid documents={documents} />

      {/* Idle CTA — shown only before analysis starts */}
      {phase === 'idle' && (
        <div style={styles.idleCta}>
          <span style={styles.idleEmoji}>🔍</span>
          <div style={styles.idleHeading}>
            {documents.length} policy documents loaded
          </div>
          <div style={styles.idleBody}>
            ConflictSense will interrogate each document simultaneously,
            comparing what they say about the same topics — and listening to
            how they disagree.
          </div>
          <div style={styles.deadlineAlert}>
            ⏰ DPDP compliance deadline: July 1, 2026 — 24 days
          </div>
        </div>
      )}

      {/* Evidence-Only Mode for Abstained state */}
      {phase === 'done' && isAbstained && (
        <div style={{
          background: '#F8FAFC',
          border: '1px solid #CBD5E1',
          borderRadius: 8,
          padding: '20px',
          marginTop: 16,
          animation: 'fadeInUp 0.3s ease'
        }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: '#334155', marginBottom: 12 }}>
            📄 Evidence-Only Mode
          </div>
          <div style={{ fontSize: 12, color: '#475569', lineHeight: 1.6, marginBottom: 12 }}>
            <span style={{ fontWeight: 600 }}>Status:</span> Evidence gathered but conflict not validated.<br/>
            <span style={{ fontWeight: 600 }}>Confidence:</span> Insufficient for conclusion.
          </div>
          <div style={{ fontSize: 12, color: '#475569', lineHeight: 1.6 }}>
            Successfully parsed {documents.length} uploaded policies. Conflict validation could not be completed because the required reasoning providers were unavailable or the extracted text lacked determinative evidence. The system abstained rather than generating an unsupported conclusion.
          </div>
        </div>
      )}

      {/* Conflict cards — revealed progressively during scanning, all shown in done */}
      {visibleConflicts.length > 0 && (
        <div style={styles.conflictsSection}>
          <div style={styles.conflictsSectionLabel}>
            <span
              style={{
                width: 5,
                height: 5,
                borderRadius: '50%',
                background: '#E24B4A',
                display: 'inline-block',
                flexShrink: 0,
                animation: phase === 'scanning' ? 'pulse 1s infinite' : 'none',
              }}
            />
            Conflicts detected — {visibleConflicts.length} of{' '}
            {phase === 'done' ? totalConflicts : '…'} — click to review
          </div>

          {/* Severity summary pills */}
          <SeveritySummary conflicts={visibleConflicts} />

          <div style={{ ...styles.conflictsList, marginTop: 8 }}>
            {visibleConflicts.map((conflict) => (
              <ConflictCard
                key={conflict.id}
                conflict={conflict}
                isSelected={selectedId === conflict.id}
                onSelect={() => onSelect(conflict.id)}
                onApprove={() => onApprove(conflict.id)}
                onReject={() => onReject(conflict.id)}
                onEscalate={() => onEscalate(conflict.id)}
                isApproved={approvedIds.has(conflict.id)}
                isRejected={rejectedIds.has(conflict.id)}
                isEscalated={escalatedIds.has(conflict.id)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
