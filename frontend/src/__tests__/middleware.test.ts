/**
 * Unit tests for Next.js middleware route protection.
 * Requirements: 13.5
 */
import { describe, it, expect } from 'vitest';
import { NextRequest } from 'next/server';
import { middleware } from '@/middleware';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Build a minimal JWT with the given payload (no real signature). */
function makeJwt(
  payload: { sub: string; role: string; locale?: string },
  expired = false
): string {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
  const exp = expired
    ? Math.floor(Date.now() / 1000) - 3600
    : Math.floor(Date.now() / 1000) + 3600;
  const body = Buffer.from(JSON.stringify({ ...payload, exp })).toString('base64url');
  return `${header}.${body}.fakesig`;
}

/** Build a NextRequest for the given path, optionally with a token cookie. */
function makeRequest(path: string, token?: string): NextRequest {
  const req = new NextRequest(`http://localhost${path}`);
  if (token) {
    req.cookies.set('token', token);
  }
  return req;
}

// ---------------------------------------------------------------------------
// Unauthenticated requests → redirect to /login?next=<url>
// ---------------------------------------------------------------------------
describe('Middleware — unauthenticated requests', () => {
  it('redirects to /{locale}/login when no token cookie is present', () => {
    const req = makeRequest('/fr/patients');
    const res = middleware(req);
    expect(res.status).toBe(307);
    const location = res.headers.get('location') ?? '';
    expect(location).toContain('/fr/login');
  });

  it('includes ?next= query param with the original URL', () => {
    const req = makeRequest('/fr/patients');
    const res = middleware(req);
    const location = res.headers.get('location') ?? '';
    expect(location).toContain('next=');
    expect(location).toContain(encodeURIComponent('/fr/patients'));
  });

  it('redirects to /en/login for English locale paths', () => {
    const req = makeRequest('/en/settings');
    const res = middleware(req);
    const location = res.headers.get('location') ?? '';
    expect(location).toContain('/en/login');
  });

  it('redirects when token is expired', () => {
    const expiredToken = makeJwt({ sub: 'u1', role: 'admin', locale: 'fr' }, true);
    const req = makeRequest('/fr/patients', expiredToken);
    const res = middleware(req);
    expect(res.status).toBe(307);
    const location = res.headers.get('location') ?? '';
    expect(location).toContain('/login');
  });
});

// ---------------------------------------------------------------------------
// Authenticated requests → pass through
// ---------------------------------------------------------------------------
describe('Middleware — authenticated requests', () => {
  it('allows admin through to /fr/patients', () => {
    const token = makeJwt({ sub: 'u1', role: 'admin', locale: 'fr' });
    const req = makeRequest('/fr/patients', token);
    const res = middleware(req);
    expect(res.status).not.toBe(307);
    const location = res.headers.get('location') ?? '';
    expect(location).not.toContain('/login');
    expect(location).not.toContain('/forbidden');
  });

  it('allows doctor through to /fr/patients', () => {
    const token = makeJwt({ sub: 'u1', role: 'doctor', locale: 'fr' });
    const req = makeRequest('/fr/patients', token);
    const res = middleware(req);
    const location = res.headers.get('location') ?? '';
    expect(location).not.toContain('/login');
    expect(location).not.toContain('/forbidden');
  });

  it('allows any authenticated role through to /fr/chat', () => {
    const roles = ['admin', 'doctor', 'nurse', 'researcher', 'patient'];
    for (const role of roles) {
      const token = makeJwt({ sub: 'u1', role, locale: 'fr' });
      const req = makeRequest('/fr/chat', token);
      const res = middleware(req);
      const location = res.headers.get('location') ?? '';
      expect(location).not.toContain('/login');
      expect(location).not.toContain('/forbidden');
    }
  });
});

// ---------------------------------------------------------------------------
// Insufficient role → redirect to /forbidden
// ---------------------------------------------------------------------------
describe('Middleware — insufficient role', () => {
  it('redirects patient to /fr/forbidden when accessing /fr/patients', () => {
    const token = makeJwt({ sub: 'u1', role: 'patient', locale: 'fr' });
    const req = makeRequest('/fr/patients', token);
    const res = middleware(req);
    expect(res.status).toBe(307);
    const location = res.headers.get('location') ?? '';
    expect(location).toContain('/fr/forbidden');
  });

  it('redirects patient to /fr/forbidden when accessing /fr/surveillance', () => {
    const token = makeJwt({ sub: 'u1', role: 'patient', locale: 'fr' });
    const req = makeRequest('/fr/surveillance', token);
    const res = middleware(req);
    expect(res.status).toBe(307);
    const location = res.headers.get('location') ?? '';
    expect(location).toContain('/fr/forbidden');
  });

  it('redirects nurse to /fr/forbidden when accessing /fr/settings', () => {
    const token = makeJwt({ sub: 'u1', role: 'nurse', locale: 'fr' });
    const req = makeRequest('/fr/settings', token);
    const res = middleware(req);
    expect(res.status).toBe(307);
    const location = res.headers.get('location') ?? '';
    expect(location).toContain('/fr/forbidden');
  });

  it('redirects researcher to /fr/forbidden when accessing /fr/patients', () => {
    const token = makeJwt({ sub: 'u1', role: 'researcher', locale: 'fr' });
    const req = makeRequest('/fr/patients', token);
    const res = middleware(req);
    expect(res.status).toBe(307);
    const location = res.headers.get('location') ?? '';
    expect(location).toContain('/fr/forbidden');
  });
});

// ---------------------------------------------------------------------------
// Public paths → bypass auth entirely
// ---------------------------------------------------------------------------
describe('Middleware — public paths', () => {
  it('allows /fr/login through without a token', () => {
    const req = makeRequest('/fr/login');
    const res = middleware(req);
    expect(res.status).not.toBe(307);
  });

  it('allows /fr/register through without a token', () => {
    const req = makeRequest('/fr/register');
    const res = middleware(req);
    expect(res.status).not.toBe(307);
  });

  it('allows /_next/static/... through without a token', () => {
    const req = makeRequest('/_next/static/chunks/main.js');
    const res = middleware(req);
    expect(res.status).not.toBe(307);
  });

  it('allows /api/... through without a token', () => {
    const req = makeRequest('/api/auth/session');
    const res = middleware(req);
    expect(res.status).not.toBe(307);
  });

  it('allows /favicon.ico through without a token', () => {
    const req = makeRequest('/favicon.ico');
    const res = middleware(req);
    expect(res.status).not.toBe(307);
  });

  it('allows /health through without a token', () => {
    const req = makeRequest('/health');
    const res = middleware(req);
    expect(res.status).not.toBe(307);
  });

  it('allows /fr/forbidden through without a token', () => {
    const req = makeRequest('/fr/forbidden');
    const res = middleware(req);
    expect(res.status).not.toBe(307);
  });
});
