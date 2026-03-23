"use client";

import React, { useEffect, useRef } from 'react';
import FocusTrap from 'focus-trap-react';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export function Modal({ open, onClose, children }: ModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  // Close on Escape key
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      role="dialog"
      aria-modal="true"
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
    >
      <FocusTrap>
        <div className="relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 p-6">
          <button
            onClick={onClose}
            aria-label="Close modal"
            className="absolute top-3 right-3 text-slate-400 hover:text-slate-600 focus:outline-none focus:ring-2 focus:ring-[#0d9488] rounded"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          {children}
        </div>
      </FocusTrap>
    </div>
  );
}
