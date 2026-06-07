/**
 * frontend/src/components/ApprovalGate.jsx
 *
 * Human Approval Gate — the three action buttons inside an expanded ConflictCard.
 *
 * Spec reference: docs/prd.md §2.3, docs/frontend_spec.md §3.2,
 *                 docs/ui_state_machine.md §conflict_selected / approved / rejected / escalated
 *
 * No autonomous action is permitted — this component is the enforcement point.
 * All state changes are reported up to parent via callbacks (no side-effects here).
 *
 * Props:
 *   onApprove()   — user confirms the finding, starts resolution workflow (local only)
 *   onReject()    — user marks as false positive (local only)
 *   onEscalate()  — user escalates to legal team (UI-only in v1)
 */

import React from 'react';

const styles = {
  container: {
    display: 'flex',
    gap: 6,
    flexWrap: 'wrap',
    marginTop: 2,
  },
  btn: {
    borderRadius: 5,
    padding: '5px 13px',
    fontSize: 11,
    fontWeight: 500,
    cursor: 'pointer',
    border: 'none',
    transition: 'filter 0.15s, transform 0.1s',
    fontFamily: 'inherit',
    lineHeight: 1.5,
  },
};

export default function ApprovalGate({ onApprove, onReject, onEscalate }) {
  const handleMouseEnter = (e) => {
    e.currentTarget.style.filter = 'brightness(1.08)';
  };
  const handleMouseLeave = (e) => {
    e.currentTarget.style.filter = '';
  };
  const handleMouseDown = (e) => {
    e.currentTarget.style.transform = 'scale(0.97)';
  };
  const handleMouseUp = (e) => {
    e.currentTarget.style.transform = '';
  };

  return (
    <div style={styles.container}>
      {/* Approve finding */}
      <button
        id="btn-approve-finding"
        style={{
          ...styles.btn,
          background: '#EAF3DE',
          color: '#3B6D11',
          border: '0.5px solid #97C459',
        }}
        onClick={(e) => {
          e.stopPropagation();
          onApprove();
        }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        title="Approve this conflict finding and enter resolution workflow"
      >
        ✓ Approve finding
      </button>

      {/* Mark false positive */}
      <button
        id="btn-false-positive"
        style={{
          ...styles.btn,
          background: '#F8FAFC',
          color: '#64748B',
          border: '0.5px solid #CBD5E1',
        }}
        onClick={(e) => {
          e.stopPropagation();
          onReject();
        }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        title="Mark this finding as a false positive"
      >
        Mark false positive
      </button>

      {/* Escalate to legal */}
      <button
        id="btn-escalate-legal"
        style={{
          ...styles.btn,
          background: '#E6F1FB',
          color: '#0C447C',
          border: '0.5px solid #85B7EB',
        }}
        onClick={(e) => {
          e.stopPropagation();
          onEscalate();
        }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        title="Escalate this conflict to the legal team for review"
      >
        Escalate to legal ↗
      </button>
    </div>
  );
}
