import React, { useEffect } from 'react';

export default function Toast({ message, isVisible, onClose }) {
  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        onClose();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [isVisible, onClose]);

  if (!isVisible) return null;

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        background: '#0F172A',
        color: '#FFFFFF',
        padding: '12px 24px',
        borderRadius: 8,
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        zIndex: 9999,
        animation: 'slideUp 0.3s ease-out',
        fontSize: 14,
        fontWeight: 500,
      }}
    >
      <span style={{ color: '#4ADE80' }}>✓</span>
      {message}
    </div>
  );
}
