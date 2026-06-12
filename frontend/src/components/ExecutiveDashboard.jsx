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

export default function ExecutiveDashboard({ phase }) {
  const isDone = phase === 'done';
  const isScanning = phase === 'scanning';

  const chartData = [
    { name: 'Legal', risk: isDone ? 85 : 10 },
    { name: 'IT', risk: isDone ? 95 : 15 },
    { name: 'HR', risk: isDone ? 45 : 10 },
    { name: 'Finance', risk: isDone ? 30 : 5 },
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
            <span style={{ color: '#2563EB', fontSize: 18 }}>📊</span>
            Enterprise Governance Exposure
          </div>
          <div style={{ fontSize: 12, color: '#64748B', marginTop: 2 }}>
            Real-time multi-agent policy compliance monitoring
          </div>
        </div>
        <div style={{ fontSize: 11, color: '#475569', fontWeight: 600, background: '#F8FAFC', padding: '4px 10px', borderRadius: 12, border: '1px solid #E2E8F0' }}>
          Confidential • VP Level View
        </div>
      </div>
      
      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12, flex: 2, minWidth: 300 }}>
          <MetricCard label="Est. Exposure" value={isDone ? '$2.4M' : '$0'} color={isDone ? '#DC2626' : '#16A34A'} subLabel="Potential regulatory fines" />
          <MetricCard label="Compliance Health" value={isDone ? '58%' : '98%'} color={isDone ? '#D97706' : '#16A34A'} subLabel="Across 7 policies" />
          <MetricCard label="Depts Affected" value={isDone ? 'IT, Legal' : 'None'} color="#3B82F6" subLabel="Cross-functional risk" />
          <MetricCard label="Pending Conflicts" value={isDone ? '9' : (isScanning ? '...' : '0')} color={isDone ? '#D97706' : '#94A3B8'} subLabel="Require human review" />
        </div>

        {/* Dynamic Impact Graph */}
        <div style={{ flex: 1, minWidth: 200, height: 160, background: '#FAFAFA', border: '1px solid #E2E8F0', borderRadius: 6, padding: '12px' }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: '#475569', marginBottom: 8, textAlign: 'center' }}>Departmental Risk Index</div>
          <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
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
  );
}
