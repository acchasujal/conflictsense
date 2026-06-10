import React from 'react';

export default function CopilotExperience() {
  return (
    <div
      style={{
        background: 'linear-gradient(135deg, #F3F4F6 0%, #FFFFFF 100%)',
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
      <style>
        {`
          @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
          }
        `}
      </style>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 8,
          background: '#EEF2FF', display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#3730A3', fontSize: 20
        }}>
          ✨
        </div>
        <div>
          <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: '#0F172A', letterSpacing: '-0.3px' }}>
            Designed for Microsoft 365 Copilot
          </h2>
          <div style={{ fontSize: 12, color: '#64748B', marginTop: 2 }}>
            Enterprise Governance Agent Companion
          </div>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 12
      }}>
        <PromptCard role="Compliance Officer" prompt="Do any of our policies conflict?" color="#185FA5" bg="#E6F1FB" border="#85B7EB" />
        <PromptCard role="HR Director" prompt="Will this new policy create governance risk?" color="#854F0B" bg="#FAEEDA" border="#EF9F27" />
        <PromptCard role="Security Team" prompt="Does this policy violate existing controls?" color="#A32D2D" bg="#FCEBEB" border="#F09595" />
        <PromptCard role="Legal Team" prompt="What policies must be updated before rollout?" color="#3730A3" bg="#EEF2FF" border="#A5B4FC" />
      </div>
    </div>
  );
}

function PromptCard({ role, prompt, color, bg, border }) {
  return (
    <div style={{
      background: '#FFFFFF',
      border: '1px solid #E2E8F0',
      borderRadius: 8,
      padding: '12px 14px',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      boxShadow: '0 1px 2px rgba(0,0,0,0.02)',
      display: 'flex',
      flexDirection: 'column',
      gap: 6
    }}>
      <div style={{
        fontSize: 10,
        fontWeight: 600,
        color: color,
        background: bg,
        padding: '2px 8px',
        borderRadius: 4,
        alignSelf: 'flex-start',
        border: `0.5px solid ${border}`
      }}>
        {role}
      </div>
      <div style={{
        fontSize: 13,
        color: '#334155',
        fontWeight: 500,
        lineHeight: 1.4
      }}>
        "{prompt}"
      </div>
      <div style={{
        marginTop: 'auto',
        fontSize: 10,
        color: '#94A3B8',
        display: 'flex',
        alignItems: 'center',
        gap: 4
      }}>
        <span>Ask Copilot</span> <span style={{fontSize: 12}}>→</span>
      </div>
    </div>
  );
}
