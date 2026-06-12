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

function tryParseJSONSummary(text) {
  if (typeof text !== 'string') return text;
  try {
    const obj = JSON.parse(text);
    return obj;
  } catch (e) {
    return text;
  }
}

function RenderValue({ val }) {
  if (typeof val === 'string') return <span>{val}</span>;
  if (Array.isArray(val)) return <span>{val.join(', ')}</span>;
  if (typeof val === 'object' && val !== null) {
    return (
      <ul style={{ margin: '4px 0', paddingLeft: 16 }}>
        {Object.entries(val).map(([k, v]) => (
          <li key={k}><strong>{k}:</strong> <RenderValue val={v} /></li>
        ))}
      </ul>
    );
  }
  return <span>{String(val)}</span>;
}

export default function AgentCard({ step, isLatest }) {
  const meta = AGENT_META[step.agent] || { icon: Sparkles, purpose: 'Reasoning process' };
  const Icon = meta.icon;
  const isRunning = isLatest && !step.conclusion; // simple heuristic
  const isCritical = step.severity === 'CRITICAL';

  let rawConclusion = step.conclusion;
  let parsed = tryParseJSONSummary(rawConclusion);
  let summary = null;
  let details = null;
  
  if (typeof parsed === 'object' && parsed !== null) {
    summary = parsed.summary || parsed.recommendation || "Detailed finding extracted.";
    details = <RenderValue val={parsed} />;
  } else if (typeof parsed === 'string') {
    const match = parsed.match(/^([^.!?]+[.!?])\s+(.*)$/s);
    if (match) {
      summary = match[1];
      details = match[2];
    } else {
      summary = parsed;
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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: '#0F172A' }}>{step.agent}</div>
            <div style={{ fontSize: 11, fontWeight: 600, color: isRunning ? '#2563EB' : '#16A34A', display: 'flex', alignItems: 'center', gap: 4 }}>
              {isRunning ? 'Processing...' : '✓ Complete'}
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 11, color: '#64748B', flexWrap: 'wrap' }}>
            {step.time && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ fontWeight: 600 }}>Duration:</span> {step.time}
              </div>
            )}
            {step.confidence && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ fontWeight: 600 }}>Confidence:</span> 
                <span style={{ color: step.confidence >= 90 ? '#16A34A' : '#D97706', fontWeight: 700 }}>
                  {step.confidence}%
                </span>
              </div>
            )}
          </div>
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
          <div style={{ fontWeight: 500 }}>{summary}</div>
          {details && (
            <details style={{ marginTop: 8 }}>
              <summary style={{ fontSize: 11, color: '#64748B', cursor: 'pointer', outline: 'none', userSelect: 'none' }}>Expand Details</summary>
              <div style={{ marginTop: 6, paddingTop: 6, borderTop: '1px dashed #CBD5E1', fontSize: 11, color: '#475569', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
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
