import React from 'react';
import { CheckCircle2, CircleDashed, ShieldAlert, FileSearch, Sparkles } from 'lucide-react';

const AGENT_META = {
  'Document Analysis': { icon: FileSearch, purpose: 'Extracting and structuring policy clauses' },
  'Azure Search Grounding': { icon: Sparkles, purpose: 'Retrieving grounded evidence context' },
  'Conflict Detection': { icon: ShieldAlert, purpose: 'Identifying structural contradictions' },
  'Conflict Validation': { icon: CheckCircle2, purpose: 'Verifying contradiction validity' },
  'Impact Assessment': { icon: ShieldAlert, purpose: 'Evaluating blast radius' },
  'Risk Quantification': { icon: Sparkles, purpose: 'Quantifying business exposure' },
  'Resolution Generation': { icon: Sparkles, purpose: 'Drafting remediation pathways' }
};

export default function AgentCard({ step, isLatest }) {
  const meta = AGENT_META[step.agent] || { icon: Sparkles, purpose: 'Reasoning process' };
  const Icon = meta.icon;
  const isRunning = isLatest && !step.conclusion; // simple heuristic
  const isCritical = step.severity === 'CRITICAL';

  let summary = step.conclusion;
  let details = null;
  if (step.conclusion) {
    const match = step.conclusion.match(/^([^.!?]+[.!?])\s+(.*)$/s);
    if (match) {
      summary = match[1];
      details = match[2];
    }
  }

  return (
    <div style={{
      background: '#FFFFFF',
      border: '1px solid #E2E8F0',
      borderRadius: '8px',
      padding: '16px',
      marginBottom: '16px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.02)',
      animation: 'fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Decorative top border for critical findings */}
      {isCritical && <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: '#DC2626' }} />}
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
        <div style={{
          width: 32, height: 32, borderRadius: '6px',
          background: isRunning ? '#EFF6FF' : '#F0FDF4',
          color: isRunning ? '#2563EB' : '#16A34A',
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          {isRunning ? <CircleDashed size={18} style={{ animation: 'spin 2s linear infinite' }} /> : <Icon size={18} />}
        </div>
        
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: '#0F172A' }}>{step.agent}</div>
            {step.confidence && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: 11, color: '#64748B' }}>Confidence</span>
                <span style={{
                  fontSize: 12, fontWeight: 700,
                  color: step.confidence >= 90 ? '#16A34A' : '#D97706'
                }}>
                  {step.confidence}%
                </span>
              </div>
            )}
          </div>
          <div style={{ fontSize: 12, color: '#64748B', marginTop: 2 }}>{meta.purpose}</div>
        </div>
      </div>

      {/* Citations if any */}
      {step.citations && step.citations.length > 0 && (
        <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid #F1F5F9' }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: '#475569', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 }}>
            Grounded Evidence
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {step.citations.map((cit, idx) => (
              <div key={idx} style={{
                background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: 4, padding: '8px 10px'
              }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: '#0F172A', marginBottom: 4 }}>
                  {cit.document} <span style={{ color: '#94A3B8', fontWeight: 400 }}>{cit.section}</span>
                </div>
                <div style={{ fontSize: 12, color: '#475569', fontStyle: 'italic' }}>"{cit.passage}"</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conclusion */}
      {step.conclusion && (
        <div style={{
          marginTop: 14,
          padding: '10px 12px',
          background: isCritical ? '#FEF2F2' : '#F8FAFC',
          borderLeft: `3px solid ${isCritical ? '#DC2626' : '#94A3B8'}`,
          borderRadius: 4,
          fontSize: 13,
          color: '#334155',
          lineHeight: 1.6
        }}>
          {isCritical && (
            <div style={{ fontSize: 11, fontWeight: 700, color: '#DC2626', marginBottom: 4, textTransform: 'uppercase' }}>
              Conflict Detected
            </div>
          )}
          <div style={{ fontWeight: details ? 600 : 400 }}>{summary}</div>
          {details && (
            <details style={{ marginTop: 8 }}>
              <summary style={{ fontSize: 11, color: '#64748B', cursor: 'pointer', outline: 'none', userSelect: 'none' }}>View detailed reasoning trace</summary>
              <div style={{ marginTop: 6, paddingTop: 6, borderTop: '1px dashed #CBD5E1', fontSize: 12, color: '#475569' }}>
                {details}
              </div>
            </details>
          )}
        </div>
      )}

      <style>{`
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
