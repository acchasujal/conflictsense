import React from 'react';

function MetricCard({ label, value, color }) {
  return (
    <div style={{ flex: 1, minWidth: 120, borderLeft: `2px solid ${color}`, paddingLeft: 10 }}>
      <div style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ fontSize: 20, fontWeight: 700, color: '#0F172A' }}>
        {value}
      </div>
    </div>
  );
}

export default function ExecutiveDashboard({ phase }) {
  return (
    <div style={{
      background: '#FFFFFF',
      border: '0.5px solid #E2E8F0',
      borderRadius: 8,
      padding: '16px 20px',
      display: 'flex',
      flexDirection: 'column',
      gap: 16,
      boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: '#0F172A', display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ color: '#185FA5' }}>📊</span>
          Enterprise Governance & Risk
        </div>
        <div style={{ fontSize: 10, color: '#64748B', fontWeight: 500, background: '#F8FAFC', padding: '2px 8px', borderRadius: 12, border: '0.5px solid #E2E8F0' }}>
          Real-Time + Historical
        </div>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '16px 12px' }}>
        <MetricCard label="Policies Analyzed" value="7" color="#185FA5" />
        <MetricCard label="Governance Status" value={phase === 'done' ? 'AT RISK' : 'ACTIVE'} color={phase === 'done' ? '#A32D2D' : '#3B6D11'} />
        <MetricCard label="Compliance Health" value={phase === 'done' ? '58%' : '98%'} color={phase === 'done' ? '#854F0B' : '#3B6D11'} />
        <MetricCard label="Conflicts Detected" value={phase === 'done' ? '9' : (phase === 'scanning' ? '...' : '0')} color="#854F0B" />
        <MetricCard label="Critical Risks" value={phase === 'done' ? '3' : '0'} color="#A32D2D" />
        <MetricCard label="Pending Approvals" value={phase === 'done' ? '9' : '0'} color="#EF9F27" />
        <MetricCard label="Est. Compliance Exposure" value={phase === 'done' ? '$4.2M' : '$0'} color="#A32D2D" />
        <MetricCard label="Resolution Success Rate" value="100%" color="#3B6D11" />
      </div>
    </div>
  );
}
