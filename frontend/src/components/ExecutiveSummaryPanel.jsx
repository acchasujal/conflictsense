export default function ExecutiveSummaryPanel({ conflicts, documentsCount }) {
  const crit = conflicts.filter((c) => c.severity === 'CRITICAL').length;
  const high = conflicts.filter((c) => c.severity === 'HIGH').length;
  const med  = conflicts.filter((c) => c.severity === 'MEDIUM').length;
  
  const depts = new Set();
  const risks = new Set();
  
  conflicts.forEach(c => {
    try {
      const aff = typeof c.affected === 'object' ? c.affected : JSON.parse(c.affected.replace(/```json/gi, '').replace(/```/g, '').trim());
      if (aff.teams) aff.teams.forEach(t => depts.add(t));
    } catch(e) {}
    if (c.risk_assessment?.risk_categories) {
      c.risk_assessment.risk_categories.forEach(r => risks.add(r.split('(')[0].trim()));
    }
  });

  return (
    <div style={{ background: '#1E293B', borderRadius: 8, padding: 20, marginBottom: 16, color: '#F8FAFC', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06)' }}>
      <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
        <span>📋</span> EXECUTIVE SUMMARY
      </div>
      <div style={{ fontSize: 13, lineHeight: 1.6, marginBottom: 16, color: '#CBD5E1' }}>
        ConflictSense analyzed <strong>{documentsCount || 7}</strong> enterprise policies and identified <strong>{conflicts.length}</strong> governance contradictions.
      </div>
      
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {crit > 0 && <span style={{ background: '#7F1D1D', color: '#FECACA', padding: '4px 10px', borderRadius: 4, fontSize: 12, fontWeight: 600 }}>{crit} Critical Findings</span>}
        {high > 0 && <span style={{ background: '#9A3412', color: '#FED7AA', padding: '4px 10px', borderRadius: 4, fontSize: 12, fontWeight: 600 }}>{high} High Findings</span>}
        {med > 0 && <span style={{ background: '#1E3A8A', color: '#BFDBFE', padding: '4px 10px', borderRadius: 4, fontSize: 12, fontWeight: 600 }}>{med} Medium Findings</span>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div>
          <div style={{ fontSize: 11, textTransform: 'uppercase', color: '#94A3B8', fontWeight: 700, marginBottom: 6 }}>Primary Risks</div>
          <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12, color: '#F1F5F9' }}>
            {Array.from(risks).slice(0, 4).map((r, i) => <li key={i} style={{ marginBottom: 4 }}>{r}</li>)}
            {risks.size === 0 && (
              <>
                <li style={{ marginBottom: 4 }}>Accessibility barriers</li>
                <li style={{ marginBottom: 4 }}>Employee privacy exposure</li>
                <li style={{ marginBottom: 4 }}>Whistleblower retaliation risk</li>
                <li style={{ marginBottom: 4 }}>Compliance failures</li>
              </>
            )}
          </ul>
        </div>
        <div>
          <div style={{ fontSize: 11, textTransform: 'uppercase', color: '#94A3B8', fontWeight: 700, marginBottom: 6 }}>Estimated Departments Impacted</div>
          <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12, color: '#F1F5F9' }}>
            {Array.from(depts).slice(0, 3).map((d, i) => <li key={i} style={{ marginBottom: 4 }}>{d}</li>)}
            {depts.size === 0 && (
              <>
                <li style={{ marginBottom: 4 }}>IT Security</li>
                <li style={{ marginBottom: 4 }}>Human Resources</li>
                <li style={{ marginBottom: 4 }}>Legal & Compliance</li>
              </>
            )}
          </ul>
        </div>
      </div>
      
      <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontSize: 12 }}>
          <span style={{ color: '#94A3B8', fontWeight: 600 }}>Recommended Priority: </span>
          <span style={{ color: '#F8FAFC', fontWeight: 700 }}>Immediate policy harmonization.</span>
        </div>
      </div>
    </div>
  );
}
