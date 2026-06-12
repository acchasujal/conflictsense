/**
 * frontend/src/components/ApprovalGate.jsx
 *
 * Human Approval Gate — Teams Adaptive Card style.
 *
 * No autonomous action is permitted — this component is the enforcement point.
 * All state changes are reported up to parent via callbacks (no side-effects here).
 */

import React from 'react';

const styles = {
  card: {
    background: '#FFFFFF',
    border: '1px solid #E2E8F0',
    borderRadius: 4,
    padding: '12px 16px',
    marginTop: 12,
    boxShadow: '0 2px 4px rgba(0,0,0,0.04)',
    fontFamily: '"Segoe UI", system-ui, sans-serif',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
    borderBottom: '1px solid #F1F5F9',
    paddingBottom: 8,
  },
  headerIcon: {
    width: 20,
    height: 20,
    background: '#5B5FC7', // Teams purple
    borderRadius: 4,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  headerText: {
    fontSize: 12,
    fontWeight: 600,
    color: '#242424',
  },
  bodyText: {
    fontSize: 12,
    color: '#424242',
    marginBottom: 12,
    lineHeight: 1.5,
  },
  actions: {
    display: 'flex',
    gap: 8,
    flexWrap: 'wrap',
  },
  btnPrimary: {
    background: '#5B5FC7',
    color: '#FFFFFF',
    border: '1px solid #5B5FC7',
    borderRadius: 4,
    padding: '6px 16px',
    fontSize: 12,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
  btnSecondary: {
    background: '#FFFFFF',
    color: '#242424',
    border: '1px solid #D1D1D1',
    borderRadius: 4,
    padding: '6px 16px',
    fontSize: 12,
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
};

export default function ApprovalGate({ onApprove, onReject, onEscalate, conflictId, traceId }) {
  const exportPackage = (e) => {
    e.stopPropagation();
    let pkg = `# Conflict Review Package\n\n`;
    pkg += `**Conflict ID:** ${conflictId}\n`;
    pkg += `**Trace ID:** ${traceId || 'N/A'}\n`;
    pkg += `**Generated:** ${new Date().toISOString()}\n\n`;
    pkg += `Please review the findings and coordinate with the governance board.\n`;
    const blob = new Blob([pkg], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ReviewPackage_${conflictId}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <div style={styles.headerIcon}>T</div>
        <div style={styles.headerText}>ConflictSense via Microsoft Teams</div>
      </div>
      
      <div style={styles.bodyText}>
        <strong>Approval Required:</strong> Please review the recommended resolution for this policy conflict. This action will update enterprise governance records.
      </div>

      <div style={styles.actions}>
        <button
          style={styles.btnPrimary}
          onClick={(e) => { e.stopPropagation(); onApprove(); }}
          onMouseOver={(e) => e.target.style.background = '#4F52B2'}
          onMouseOut={(e) => e.target.style.background = '#5B5FC7'}
        >
          Approve Remediation Plan
        </button>

        <button
          style={styles.btnSecondary}
          onClick={(e) => { e.stopPropagation(); onReject(); }}
          onMouseOver={(e) => e.target.style.background = '#F5F5F5'}
          onMouseOut={(e) => e.target.style.background = '#FFFFFF'}
        >
          Request Legal Review
        </button>

        <button
          style={styles.btnSecondary}
          onClick={(e) => { e.stopPropagation(); onEscalate(); }}
          onMouseOver={(e) => e.target.style.background = '#F5F5F5'}
          onMouseOut={(e) => e.target.style.background = '#FFFFFF'}
        >
          Escalate to Governance Board
        </button>

        <button
          style={{ ...styles.btnSecondary, background: '#F8FAFC' }}
          onClick={exportPackage}
          onMouseOver={(e) => e.target.style.background = '#F1F5F9'}
          onMouseOut={(e) => e.target.style.background = '#F8FAFC'}
        >
          📥 Export Review Package
        </button>
      </div>
    </div>
  );
}
