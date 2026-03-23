/**
 * Unit tests for the login page flow integration.
 * Requirements: 5.2, 5.3, 5.6
 */
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

const mockPush = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
  useParams: () => ({ locale: 'fr' }),
}));

vi.mock('next-intl', () => ({
  useTranslations: () => (key: string) => key,
}));

const mockLogin = vi.fn();

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({ login: mockLogin }),
}));

// Stub UI components so we don't need full Tailwind rendering
vi.mock('@/components/ui/Button', () => ({
  Button: ({ children, loading, disabled, type, ...rest }: React.ButtonHTMLAttributes<HTMLButtonElement> & { loading?: boolean }) => (
    <button type={type} disabled={disabled || loading} {...rest}>
      {loading ? <span data-testid="spinner" /> : children}
    </button>
  ),
}));

vi.mock('@/components/ui/Input', () => ({
  Input: ({ label, error, onChange, value, type, required, autoComplete, autoFocus, inputMode, pattern, maxLength, placeholder }: {
    label?: string;
    error?: string;
    onChange?: React.ChangeEventHandler<HTMLInputElement>;
    value?: string;
    type?: string;
    required?: boolean;
    autoComplete?: string;
    autoFocus?: boolean;
    inputMode?: React.HTMLAttributes<HTMLInputElement>['inputMode'];
    pattern?: string;
    maxLength?: number;
    placeholder?: string;
  }) => (
    <div>
      {label && <label>{label}</label>}
      <input
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        autoComplete={autoComplete}
        autoFocus={autoFocus}
        inputMode={inputMode}
        pattern={pattern}
        maxLength={maxLength}
        placeholder={placeholder}
        aria-label={label}
      />
      {error && <span role="alert">{error}</span>}
    </div>
  ),
}));

vi.mock('@/components/ui/Card', () => ({
  Card: ({ children, className }: { children: React.ReactNode; className?: string }) => (
    <div className={className}>{children}</div>
  ),
}));

// ---------------------------------------------------------------------------
// Import the component under test AFTER mocks are set up
// ---------------------------------------------------------------------------
import LoginPage from '@/app/[locale]/login/page';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderLogin() {
  return render(<LoginPage />);
}

function fillCredentials(email = 'user@example.com', password = 'secret123') {
  const emailInput = screen.getByRole('textbox', { name: /email/i });
  const passwordInput = document.querySelector('input[type="password"]') as HTMLInputElement;
  fireEvent.change(emailInput, { target: { value: email } });
  fireEvent.change(passwordInput, { target: { value: password } });
}

function submitForm() {
  const form = document.querySelector('form') as HTMLFormElement;
  fireEvent.submit(form);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('Login page — unit tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // -------------------------------------------------------------------------
  // Test: successful login → tokens stored → redirect to dashboard
  // -------------------------------------------------------------------------
  it('successful login redirects to /{locale}/dashboard', async () => {
    mockLogin.mockResolvedValueOnce({ type: 'success' });

    renderLogin();
    fillCredentials();
    submitForm();

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('user@example.com', 'secret123');
      expect(mockPush).toHaveBeenCalledWith('/fr/dashboard');
    });
  });

  // -------------------------------------------------------------------------
  // Test: failed login → auth.invalidCredentials error shown
  // -------------------------------------------------------------------------
  it('failed login shows auth.invalidCredentials error', async () => {
    mockLogin.mockRejectedValueOnce(new Error('Invalid credentials'));

    renderLogin();
    fillCredentials('bad@example.com', 'wrongpass');
    submitForm();

    await waitFor(() => {
      // useTranslations returns the key itself in our mock
      expect(screen.getByRole('alert')).toHaveTextContent('invalidCredentials');
    });
    expect(mockPush).not.toHaveBeenCalled();
  });

  // -------------------------------------------------------------------------
  // Test: MFA step renders when mfa_required returned
  // -------------------------------------------------------------------------
  it('renders MFA TOTP input step when login returns mfa_required', async () => {
    mockLogin.mockResolvedValueOnce({ type: 'mfa_required', userId: 'user-42' });

    renderLogin();
    fillCredentials();
    submitForm();

    await waitFor(() => {
      // The MFA title should be visible (key returned by mock translator)
      expect(screen.getByText('mfaTitle')).toBeInTheDocument();
    });

    // The TOTP input should be present
    const totpInput = document.querySelector('input[inputmode="numeric"]') as HTMLInputElement;
    expect(totpInput).not.toBeNull();

    // The original email/password form should no longer be visible
    expect(screen.queryByRole('textbox', { name: /email/i })).toBeNull();
  });
});
