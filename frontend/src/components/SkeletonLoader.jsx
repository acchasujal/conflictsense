import React from 'react';

const styles = {
  container: {
    padding: '14px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    animation: 'fadeInUp 0.3s ease',
  },
  skeletonText: {
    background: 'linear-gradient(90deg, #E2E8F0 25%, #F1F5F9 50%, #E2E8F0 75%)',
    backgroundSize: '200% 100%',
    animation: 'shimmer 1.5s infinite',
    borderRadius: '4px',
  },
  card: {
    background: '#FFFFFF',
    border: '0.5px solid #E2E8F0',
    borderRadius: '8px',
    padding: '12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  }
};

export default function SkeletonLoader({ type = 'document', count = 3 }) {
  const items = Array.from({ length: count });

  if (type === 'conflict') {
    return (
      <div style={styles.container} aria-hidden="true">
        {items.map((_, i) => (
          <div key={i} style={styles.card}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <div style={{ ...styles.skeletonText, width: '40px', height: '14px' }} />
              <div style={{ ...styles.skeletonText, width: '80px', height: '14px', marginLeft: 'auto' }} />
            </div>
            <div style={{ ...styles.skeletonText, width: '70%', height: '16px' }} />
            <div style={{ ...styles.skeletonText, width: '100%', height: '12px' }} />
            <div style={{ ...styles.skeletonText, width: '80%', height: '12px' }} />
          </div>
        ))}
      </div>
    );
  }

  // default 'document' skeleton
  return (
    <div style={{ display: 'flex', gap: '10px', overflowX: 'hidden', padding: '14px 0' }} aria-hidden="true">
      {items.map((_, i) => (
        <div key={i} style={{ ...styles.card, minWidth: '140px', height: '80px' }}>
          <div style={{ ...styles.skeletonText, width: '80%', height: '14px' }} />
          <div style={{ ...styles.skeletonText, width: '60%', height: '12px', marginTop: 'auto' }} />
        </div>
      ))}
    </div>
  );
}
