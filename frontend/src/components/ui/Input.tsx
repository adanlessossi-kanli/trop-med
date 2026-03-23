import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, id, className = '', ...props }: InputProps) {
  const inputId = id ?? (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label
          htmlFor={inputId}
          className="text-sm font-medium text-[#64748b]"
        >
          {label}
        </label>
      )}
      <input
        id={inputId}
        className={[
          'rounded-md border px-3 py-2 text-sm',
          'focus:outline-none focus:ring-2 focus:ring-[#0d9488] focus:border-transparent',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          error
            ? 'border-[#dc2626] focus:ring-[#dc2626]'
            : 'border-slate-300',
          className,
        ].join(' ')}
        aria-invalid={!!error}
        aria-describedby={error ? `${inputId}-error` : undefined}
        {...props}
      />
      {error && (
        <p id={`${inputId}-error`} className="text-xs text-[#dc2626]" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
