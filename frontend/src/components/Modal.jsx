import React, { useEffect, useRef } from 'react';

export default function Modal({ isOpen, onClose, title, children }) {
  const dialogRef = useRef(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (isOpen) {
      if (!dialog.open) dialog.showModal();
    } else {
      if (dialog.open) dialog.close();
    }
  }, [isOpen]);

  useEffect(() => {
    const dialog = dialogRef.current;
    const handleCancel = (e) => {
      e.preventDefault();
      onClose();
    };
    dialog.addEventListener('cancel', handleCancel);
    return () => dialog.removeEventListener('cancel', handleCancel);
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <dialog
      ref={dialogRef}
      style={{
        padding: 0,
        border: 'none',
        borderRadius: 8,
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        width: '100%',
        maxWidth: 500,
        background: '#FFFFFF',
      }}
      aria-modal="true"
      role="dialog"
    >
      <div style={{ padding: '20px 24px', borderBottom: '1px solid #E2E8F0' }}>
        <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: '#0F172A' }}>{title}</h2>
      </div>
      <div style={{ padding: '24px' }}>
        {children}
      </div>
    </dialog>
  );
}
