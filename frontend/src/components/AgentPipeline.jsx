import React from 'react';

const AGENTS = [
  { id: 'DocumentAnalyzer', label: 'Analyzer' },
  { id: 'AzureSearch', label: 'Retrieval' },
  { id: 'ConflictDetector', label: 'Detector' },
  { id: 'ConflictValidator', label: 'Validator' },
  { id: 'ImpactAssessor', label: 'Assessor' },
  { id: 'RiskQuantifier', label: 'Quantifier' },
  { id: 'ResolutionRecommender', label: 'Recommender' },
  { id: 'ApprovalGate', label: 'Approval Gate' }
];

// Map trace agent names to pipeline index
const getActiveIndex = (phase, currentAgent) => {
  if (phase === 'idle') return -1;
  if (phase === 'done') return AGENTS.length - 1; // Ends at Approval Gate waiting
  
  switch (currentAgent) {
    case 'DocumentAnalyzer': return 0;
    // Azure search is implied after DocumentAnalyzer
    case 'ConflictDetector': return 2;
    case 'ConflictValidator': return 3;
    case 'ImpactAssessor': return 4;
    case 'RiskQuantifier': return 5;
    case 'ResolutionRecommender': return 6;
    default: return 0; // Default to Analyzer if unknown
  }
};

export default function AgentPipeline({ phase, currentAgent }) {
  const activeIndex = getActiveIndex(phase, currentAgent);

  return (
    <div style={{
      padding: '12px 14px',
      background: '#111111', // Slightly darker than trace background
      borderBottom: '0.5px solid rgba(255,255,255,0.07)',
      display: 'flex',
      flexDirection: 'column',
      gap: 10,
    }}>
      <div style={{ fontSize: 9, fontFamily: 'monospace', color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
        Live Agent Pipeline
      </div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative' }}>
        {/* Background connector line */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: 10,
          right: 10,
          height: 1,
          background: 'rgba(255,255,255,0.1)',
          zIndex: 0,
        }} />
        
        {AGENTS.map((agent, i) => {
          const isDone = i < activeIndex;
          const isActive = i === activeIndex;
          const isPending = i > activeIndex;
          
          let bgColor = 'rgba(255,255,255,0.05)';
          let borderColor = 'rgba(255,255,255,0.1)';
          let textColor = 'rgba(255,255,255,0.3)';
          let dotColor = 'rgba(255,255,255,0.1)';

          if (isDone) {
            bgColor = 'rgba(99,153,34,0.15)';
            borderColor = 'rgba(99,153,34,0.4)';
            textColor = '#97C459';
            dotColor = '#97C459';
          } else if (isActive) {
            bgColor = 'rgba(55,138,221,0.15)';
            borderColor = '#378ADD';
            textColor = '#378ADD';
            dotColor = '#378ADD';
          }

          return (
            <div key={agent.id} style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 4,
              zIndex: 1,
              position: 'relative'
            }}>
              <div style={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                background: '#111111',
                border: `1.5px solid ${borderColor}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: isActive ? '0 0 8px rgba(55,138,221,0.6)' : 'none',
              }}>
                <div style={{
                  width: 4,
                  height: 4,
                  borderRadius: '50%',
                  background: dotColor,
                  animation: isActive ? 'pulse 1s infinite' : 'none'
                }} />
              </div>
              <div style={{
                fontSize: 8,
                fontFamily: 'monospace',
                color: textColor,
                position: 'absolute',
                top: 16,
                whiteSpace: 'nowrap',
                fontWeight: isActive ? 700 : 400,
                transform: 'rotate(-45deg) translateX(-10px) translateY(5px)',
                transformOrigin: 'top left'
              }}>
                {agent.label}
              </div>
            </div>
          );
        })}
      </div>
      {/* Spacer to account for rotated text */}
      <div style={{ height: 25 }} /> 
    </div>
  );
}
