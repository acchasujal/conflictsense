import React from 'react';

export default function CopilotExperience({ onRunAnalysis }) {
  return (
    <div
      style={{
        background: '#FFFFFF',
        border: '1px solid #E2E8F0',
        borderRadius: 12,
        padding: '20px 24px',
        marginBottom: 16,
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <div style={{
        position: 'absolute',
        top: 0, left: 0, width: '100%', height: '4px',
        background: 'linear-gradient(90deg, #185FA5, #378ADD, #9F8FE8, #185FA5)',
        backgroundSize: '200% 100%',
        animation: 'gradientShift 5s ease infinite'
      }} />

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 8,
          background: '#EEF2FF', display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#3730A3', fontSize: 20
        }}>
          🎯
        </div>
        <div>
          <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: '#0F172A', letterSpacing: '-0.3px' }}>
            Try Enterprise Scenarios
          </h2>
          <div style={{ fontSize: 12, color: '#64748B', marginTop: 2 }}>
            Click a scenario below to launch the multi-agent detection pipeline
          </div>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 12
      }}>
        <ScenarioCard 
          title="Data Residency Conflict" 
          desc="Test cross-border IT policies vs HR flexibility." 
          onClick={onRunAnalysis} 
        />
        <ScenarioCard 
          title="Anonymous Reporting Conflict" 
          desc="Test whistleblower protection vs IT identity logging." 
          onClick={onRunAnalysis} 
        />
        <ScenarioCard 
          title="Cross-Border Access Conflict" 
          desc="Test VPN access vs export control rules." 
          onClick={onRunAnalysis} 
        />
        <ScenarioCard 
          title="Vendor Compliance Conflict" 
          desc="Test third-party software SLAs vs internal security audits." 
          onClick={onRunAnalysis} 
        />
      </div>
    </div>
  );
}

function ScenarioCard({ title, desc, onClick }) {
  const [hover, setHover] = React.useState(false);
  return (
    <div 
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        background: hover ? '#F8FAFC' : '#FFFFFF',
        border: `1px solid ${hover ? '#CBD5E1' : '#E2E8F0'}`,
        borderRadius: 8,
        padding: '12px 14px',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        display: 'flex',
        flexDirection: 'column',
        gap: 6,
        boxShadow: hover ? '0 2px 4px rgba(0,0,0,0.02)' : 'none',
      }}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter') onClick(); }}
      aria-label={`Run scenario: ${title}`}
    >
      <div style={{
        fontSize: 13,
        color: '#0F172A',
        fontWeight: 600,
      }}>
        {title}
      </div>
      <div style={{
        fontSize: 11,
        color: '#64748B',
        lineHeight: 1.4
      }}>
        {desc}
      </div>
      <div style={{
        marginTop: 'auto',
        fontSize: 11,
        color: '#2563EB',
        fontWeight: 600,
        display: 'flex',
        alignItems: 'center',
        gap: 4
      }}>
        Run Analysis ➔
      </div>
    </div>
  );
}

function TelemetryCard({ label, value, status, color }) {
  return (
    <div style={{
      background: '#F8FAFC',
      border: '1px solid #E2E8F0',
      borderRadius: 8,
      padding: '12px 14px',
      display: 'flex',
      flexDirection: 'column',
      gap: 6
    }}>
      <div style={{
        fontSize: 10,
        fontWeight: 600,
        color: '#64748B',
        textTransform: 'uppercase',
        letterSpacing: 0.5
      }}>
        {label}
      </div>
      <div style={{
        fontSize: 13,
        color: '#0F172A',
        fontWeight: 600,
      }}>
        {value}
      </div>
      <div style={{
        marginTop: 'auto',
        fontSize: 11,
        color: color,
        fontWeight: 600,
        display: 'flex',
        alignItems: 'center',
        gap: 4
      }}>
        <span style={{ width: 6, height: 6, borderRadius: '50%', background: color }} />
        {status}
      </div>
    </div>
  );
}
