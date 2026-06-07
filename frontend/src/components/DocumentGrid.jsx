/**
 * frontend/src/components/DocumentGrid.jsx
 *
 * Grid of DocTile components showing the 7 loaded Nexora policy documents.
 *
 * Spec reference: docs/frontend_spec.md §3.1, docs/synthetic_enterprise_spec.md §2
 *
 * Always visible in all three UI phases (idle / scanning / done).
 * DPDP_Compliance_Directive.md must show a "NEW" badge.
 */

import React from 'react';

// ─── Design tokens ───────────────────────────────────────────────────────────
const styles = {
  section: {
    marginBottom: 0,
  },
  sectionLabel: {
    fontSize: 10,
    fontWeight: 600,
    color: 'rgba(100,116,139,1)',
    textTransform: 'uppercase',
    letterSpacing: '0.6px',
    marginBottom: 8,
    display: 'flex',
    alignItems: 'center',
    gap: 6,
  },
  labelDot: {
    width: 5,
    height: 5,
    borderRadius: '50%',
    background: '#378ADD',
    display: 'inline-block',
    flexShrink: 0,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(148px, 1fr))',
    gap: 6,
  },
  tile: {
    background: '#FFFFFF',
    border: '0.5px solid #E2E8F0',
    borderRadius: 8,
    padding: '9px 11px',
    position: 'relative',
    transition: 'border-color 0.2s, box-shadow 0.2s',
    cursor: 'default',
  },
  tileNew: {
    border: '0.5px solid #85B7EB',
    boxShadow: '0 0 0 1.5px rgba(133,183,235,0.2)',
  },
  tileName: {
    fontSize: 10,
    fontFamily: 'monospace',
    fontWeight: 600,
    color: '#0F172A',
    marginBottom: 3,
    wordBreak: 'break-all',
    lineHeight: 1.35,
  },
  tileDept: {
    fontSize: 10,
    color: '#64748B',
  },
  tileMeta: {
    fontSize: 10,
    color: '#94A3B8',
    marginTop: 2,
  },
  newBadge: {
    position: 'absolute',
    top: 6,
    right: 6,
    background: '#E6F1FB',
    color: '#0C447C',
    fontSize: 9,
    fontWeight: 700,
    padding: '1px 5px',
    borderRadius: 3,
    letterSpacing: '0.4px',
    lineHeight: '14px',
  },
};

// ─── DocTile ─────────────────────────────────────────────────────────────────

function DocTile({ doc }) {
  const tileStyle = {
    ...styles.tile,
    ...(doc.isNew ? styles.tileNew : {}),
  };

  return (
    <div style={tileStyle}>
      {doc.isNew && <div style={styles.newBadge}>NEW</div>}
      <div style={{ ...styles.tileName, paddingRight: doc.isNew ? 30 : 0 }}>
        {doc.name}
      </div>
      <div style={styles.tileDept}>{doc.dept}</div>
      <div style={styles.tileMeta}>
        Updated {doc.date} · {doc.size}
      </div>
    </div>
  );
}

// ─── DocumentGrid ─────────────────────────────────────────────────────────────

/**
 * @param {{ documents: import('../lib/mockData').Document[] }} props
 */
export default function DocumentGrid({ documents }) {
  return (
    <div style={styles.section}>
      <div style={styles.sectionLabel}>
        <span style={styles.labelDot} />
        Document corpus — {documents.length} policies loaded
      </div>
      <div style={styles.grid}>
        {documents.map((doc) => (
          <DocTile key={doc.id} doc={doc} />
        ))}
      </div>
    </div>
  );
}
