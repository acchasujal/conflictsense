import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function MetricCard({ label, value, color, subLabel }) {
  return (
    <div style={{ flex: 1, minWidth: 120, background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: 6, padding: 12, boxShadow: '0 1px 2px rgba(0,0,0,0.02)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
        <div style={{ width: 4, height: 12, background: color, borderRadius: 2 }} />
        <div style={{ fontSize: 11, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
          {label}
        </div>
      </div>
      <div style={{ fontSize: 24, fontWeight: 700, color: '#0F172A', lineHeight: 1 }}>
        {value}
      </div>
      {subLabel && (
        <div style={{ fontSize: 11, color: '#94A3B8', marginTop: 4 }}>{subLabel}</div>
      )}
    </div>
  );
}

export default function ExecutiveDashboard({ phase, visibleConflicts = [], traceId }) {
  const isDone = phase === 'done';
  const isScanning = phase === 'scanning';

  const exportReport = () => {
    let report = `# ConflictSense Enterprise Policy Audit\n\n`;
    report += `**Trace ID:** ${traceId || 'N/A'}\n`;
    report += `**Timestamp:** ${new Date().toISOString()}\n\n`;
    report += `## Executive Summary\n`;
    report += `System processed documents and identified ${visibleConflicts.length} active conflicts.\n\n`;
    
    visibleConflicts.forEach((c, idx) => {
      report += `### ${idx + 1}. ${c.title}\n`;
      report += `- **Severity:** ${c.severity}\n`;
      report += `- **Affected:** ${typeof c.affected === 'object' ? JSON.stringify(c.affected) : c.affected}\n`;
      report += `- **Deadline:** ${c.deadline || 'None'}\n\n`;
      if (c.resolution) {
        report += `**Recommended Resolution:**\n${typeof c.resolution === 'object' ? JSON.stringify(c.resolution) : c.resolution}\n\n`;
      }
    });

    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ConflictSense_Report_${traceId || 'audit'}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const crit = visibleConflicts.filter((c) => c.severity === 'CRITICAL').length;
  const high = visibleConflicts.filter((c) => c.severity === 'HIGH').length;
  const med  = visibleConflicts.filter((c) => c.severity === 'MEDIUM').length;

  const exposureAmount = (crit * 1.2 + high * 0.5 + med * 0.1).toFixed(1);
  const exposureStr = (isScanning && visibleConflicts.length === 0) || (!isDone && visibleConflicts.length === 0) ? '$0' : `$${exposureAmount}M`;

  const healthScore = Math.max(0, 100 - (crit * 20 + high * 10 + med * 5));
  const healthStr = (isScanning && visibleConflicts.length === 0) || (!isDone && visibleConflicts.length === 0) ? '98%' : `${healthScore}%`;

  const depts = new Set();
  visibleConflicts.forEach(c => {
    try {
      const aff = typeof c.affected === 'object' ? c.affected : JSON.parse(c.affected.replace(/```json/gi, '').replace(/```/g, '').trim());
      if (aff.teams) aff.teams.forEach(t => depts.add(t));
    } catch(e) {}
  });
  let deptsStr = 'None';
  if (depts.size > 0) {
    deptsStr = Array.from(depts).slice(0, 2).join(', ');
    if (depts.size > 2) deptsStr += '...';
  } else if (visibleConflicts.length > 0) {
    deptsStr = 'Multiple';
  }

  const pendingStr = (isDone || visibleConflicts.length > 0) ? visibleConflicts.length.toString() : (isScanning ? '...' : '0');

  const chartData = [
    { name: 'Legal', risk: isDone ? Math.min(100, crit * 30 + 10) : 10 },
    { name: 'IT', risk: isDone ? Math.min(100, high * 25 + 15) : 15 },
    { name: 'HR', risk: isDone ? Math.min(100, med * 20 + 10) : 10 },
    { name: 'Finance', risk: isDone ? Math.min(100, crit * 10 + 5) : 5 },
  ];

  return (
    <div style={{
      background: '#FFFFFF',
      border: '1px solid #E2E8F0',
      borderRadius: 12,
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      gap: 20,
      boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: 16, fontWeight: 700, color: '#0F172A', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ color: '#2563EB', fontSize: 18 }}>🛡️</span>
            Human-Centered Policy Governance
          </div>
          <div style={{ fontSize: 12, color: '#64748B', marginTop: 2 }}>
            Protecting employees from systemic policy contradictions
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {isDone && visibleConflicts.length > 0 && (
            <button 
              onClick={exportReport}
              style={{
                background: '#FFFFFF',
                color: '#0F172A',
                border: '1px solid #CBD5E1',
                padding: '6px 12px',
                borderRadius: 6,
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
              }}
            >
              <span>📥</span> Export Report
            </button>
          )}
          <div style={{ fontSize: 11, color: '#475569', fontWeight: 600, background: '#F8FAFC', padding: '4px 10px', borderRadius: 12, border: '1px solid #E2E8F0' }}>
            Confidential • VP Level View
          </div>
        </div>
      </div>
      
      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12, flex: 2, minWidth: 300 }}>
          <MetricCard label="Compliance Health" value={healthStr} color={healthScore < 80 ? '#D97706' : '#16A34A'} subLabel="Across 7 policies" />
          <div style={{ flex: 2, minWidth: 200, background: '#EFF6FF', border: '1px solid #BFDBFE', borderRadius: 6, padding: 12, boxShadow: '0 1px 2px rgba(0,0,0,0.02)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
              <div style={{ width: 4, height: 12, background: '#3B82F6', borderRadius: 2 }} />
              <div style={{ fontSize: 11, color: '#1E3A8A', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
                People Protected
              </div>
            </div>
            <div style={{ fontSize: 11, color: '#1E40AF', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span>✅</span> Whistleblower retaliation risk</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span>✅</span> Accessibility barriers</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span>✅</span> Employee privacy risks</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span>✅</span> Safety risks</div>
            </div>
          </div>
        </div>

        {/* Dynamic Impact Graph */}
        <div style={{ flex: 1, minWidth: 200, height: 160, background: '#FAFAFA', border: '1px solid #E2E8F0', borderRadius: 6, padding: '12px' }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: '#475569', marginBottom: 8, textAlign: 'center' }}>Departmental Risk Index</div>
          <div style={{ height: 120, width: '100%', minWidth: 0, minHeight: 120 }}>
            <ResponsiveContainer width="100%" height={120}>
              <BarChart data={chartData} margin={{ top: 0, right: 0, left: -25, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748B' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: '#64748B' }} axisLine={false} tickLine={false} domain={[0, 100]} />
                <Tooltip cursor={{ fill: '#F1F5F9' }} contentStyle={{ fontSize: 12, borderRadius: 4, border: 'none', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }} />
                <Bar dataKey="risk" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.risk > 80 ? '#DC2626' : entry.risk > 40 ? '#D97706' : '#2563EB'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
