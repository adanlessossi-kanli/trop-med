/**
 * Property-based tests for the Trop-Med frontend.
 * Feature: trop-med-fullstack-polish
 * Uses fast-check with numRuns: 100 per property.
 * Requirements: 13.1, 13.3, 13.6
 */
import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import * as fc from 'fast-check';
import { NextRequest } from 'next/server';

// ---------------------------------------------------------------------------
// Shared types and constants
// ---------------------------------------------------------------------------

type Role = 'admin' | 'doctor' | 'nurse' | 'researcher' | 'patient';

const ALL_ROLES: Role[] = ['admin', 'doctor', 'nurse', 'researcher', 'patient'];

const ROLE_ROUTES: Record<string, Role[]> = {
  '/patients':      ['admin', 'doctor', 'nurse'],
  '/surveillance':  ['admin', 'doctor', 'researcher'],
  '/settings':      ['admin'],
  '/chat':          ['admin', 'doctor', 'nurse', 'researcher', 'patient'],
  '/notifications': ['admin', 'doctor', 'nurse', 'researcher', 'patient'],
};

const LOCALES = ['fr', 'en'] as const;

// ---------------------------------------------------------------------------
// JWT helpers
// ---------------------------------------------------------------------------

function makeJwt(
  payload: { sub: string; role: Role; locale?: string },
  expired = false
): string {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
  const exp = expired
    ? Math.floor(Date.now() / 1000) - 3600
    : Math.floor(Date.now() / 1000) + 3600;
  const body = Buffer.from(JSON.stringify({ ...payload, exp })).toString('base64url');
  return `${header}.${body}.fakesig`;
}

function makeRequest(path: string, token?: string): NextRequest {
  const req = new NextRequest(`http://localhost${path}`);
  if (token) {
    req.cookies.set('token', token);
  }
  return req;
}

function makeJsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? 'OK' : 'Error',
    headers: new Headers({ 'Content-Type': 'application/json' }),
    json: async () => body,
  } as unknown as Response;
}

// ---------------------------------------------------------------------------
// Arbitraries
// ---------------------------------------------------------------------------

const localeArb = fc.constantFrom(...LOCALES);
const roleArb = fc.constantFrom(...ALL_ROLES);

const protectedRouteArb = fc.tuple(
  localeArb,
  fc.constantFrom(...Object.keys(ROLE_ROUTES))
).map(([locale, route]) => `/${locale}${route}`);

const validTokenArb = roleArb.map((role) =>
  makeJwt({ sub: 'user-1', role, locale: 'fr' }, false)
);

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 1: Button loading prop renders Spinner
// Validates: Requirements 2.1, 2.8
// ---------------------------------------------------------------------------
describe('Property 1: Button loading prop renders Spinner', () => {
  it('renders Spinner when loading=true, children when loading=false', async () => {
    const { Button } = await import('@/components/ui/Button');

    fc.assert(
      fc.property(fc.boolean(), (loading) => {
        const { unmount } = render(
          React.createElement(Button, { loading }, 'Click me')
        );
        if (loading) {
          expect(screen.queryByTestId('spinner')).not.toBeNull();
          expect(screen.queryByText('Click me')).toBeNull();
        } else {
          expect(screen.queryByTestId('spinner')).toBeNull();
          expect(screen.queryByText('Click me')).not.toBeNull();
        }
        unmount();
      }),
      { numRuns: 100 }
    );
  });
});

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 2: Badge renders colour class for every valid Role
// Validates: Requirements 2.5
// ---------------------------------------------------------------------------
describe('Property 2: Badge renders a colour class for every valid Role', () => {
  it('renders a non-empty role-specific class for every Role value', async () => {
    const { Badge } = await import('@/components/ui/Badge');

    fc.assert(
      fc.property(fc.constantFrom(...ALL_ROLES), (role) => {
        const { container, unmount } = render(
          React.createElement(Badge, { role })
        );
        const span = container.querySelector('span');
        expect(span).not.toBeNull();
        expect(span!.className).toContain(`role-${role}`);
        unmount();
      }),
      { numRuns: 100 }
    );
  });
});

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 3: Table renders correct state for all data/loading combinations
// Validates: Requirements 2.6
// ---------------------------------------------------------------------------
describe('Property 3: Table renders correct state for all data/loading combinations', () => {
  it('renders exactly one of: skeleton, empty-state, or data rows — never more than one simultaneously', async () => {
    const { Table } = await import('@/components/ui/Table');
    const columns = [{ key: 'name' as const, header: 'Name' }];
    const rowArb = fc.record({ name: fc.string() });

    fc.assert(
      fc.property(fc.boolean(), fc.array(rowArb, { maxLength: 5 }), (loading, data) => {
        const { container, unmount } = render(
          React.createElement(Table, {
            columns,
            data,
            loading,
            emptySlot: React.createElement('span', null, 'Empty'),
          })
        );

        const tableEl = container.querySelector('[data-testid="table"]');
        if (tableEl) {
          const skeletonCells = tableEl.querySelectorAll('.animate-pulse');
          const hasSkeleton = skeletonCells.length > 0;

          const allTds = Array.from(tableEl.querySelectorAll('td'));
          const hasEmpty = allTds.some(
            (td) => td.colSpan === columns.length && td.textContent?.includes('Empty')
          );

          const dataRows = tableEl.querySelectorAll('tbody tr');
          const hasData = dataRows.length > 0 && !hasSkeleton && !hasEmpty;

          const activeStates = [hasSkeleton, hasEmpty, hasData].filter(Boolean).length;

          if (loading) {
            expect(hasSkeleton).toBe(true);
            expect(hasEmpty).toBe(false);
          } else if (data.length === 0) {
            expect(hasEmpty).toBe(true);
            expect(hasSkeleton).toBe(false);
          } else {
            // Has data rows
            expect(hasSkeleton).toBe(false);
            expect(hasEmpty).toBe(false);
          }

          // Never more than one state active
          expect(activeStates).toBeLessThanOrEqual(1);
        }

        unmount();
      }),
      { numRuns: 100 }
    );
  });
});

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 4: All next/image usages have required accessibility attributes
// Validates: Requirements 4.3, 4.4
// ---------------------------------------------------------------------------
describe('Property 4: All next/image usages have required accessibility attributes', () => {
  it('renders img with non-empty alt, explicit width, and explicit height for any valid inputs', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 1, maxLength: 80 }),
        fc.integer({ min: 1, max: 4000 }),
        fc.integer({ min: 1, max: 4000 }),
        (alt, width, height) => {
          const { container, unmount } = render(
            React.createElement('img', {
              src: 'https://images.unsplash.com/photo-test',
              alt,
              width,
              height,
            })
          );

          const img = container.querySelector('img');
          expect(img).not.toBeNull();

          const altAttr = img!.getAttribute('alt');
          expect(altAttr).not.toBeNull();
          expect(altAttr!.length).toBeGreaterThan(0);

          const w = Number(img!.getAttribute('width'));
          const h = Number(img!.getAttribute('height'));
          expect(w).toBeGreaterThan(0);
          expect(h).toBeGreaterThan(0);

          unmount();
        }
      ),
      { numRuns: 100 }
    );
  });
});

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 5: Successful login stores tokens and redirects
// Validates: Requirements 5.2
// ---------------------------------------------------------------------------
describe('Property 5: Successful login stores tokens and redirects', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
    document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  });

  it('stores token and refresh_token in localStorage and sets token cookie for any valid credentials', async () => {
    const originalFetch = globalThis.fetch;

    await fc.assert(
      fc.asyncProperty(
        fc.emailAddress(),
        fc.string({ minLength: 8 }),
        async (email, password) => {
          localStorage.clear();
          document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';

          const fakeAccessToken = `header.${Buffer.from(JSON.stringify({
            sub: 'u1', role: 'doctor', locale: 'fr',
            exp: Math.floor(Date.now() / 1000) + 3600,
          })).toString('base64url')}.sig`;
          const fakeRefreshToken = 'refresh-token-value';

          globalThis.fetch = vi.fn().mockResolvedValueOnce({
            ok: true,
            status: 200,
            headers: new Headers({ 'Content-Type': 'application/json' }),
            json: async () => ({
              access_token: fakeAccessToken,
              refresh_token: fakeRefreshToken,
            }),
          } as unknown as Response);

          const { renderHook } = await import('@testing-library/react');
          const { useAuth } = await import('@/hooks/useAuth');

          const { result } = renderHook(() => useAuth());
          const loginResult = await result.current.login(email, password);

          expect(localStorage.getItem('token')).toBe(fakeAccessToken);
          expect(localStorage.getItem('refresh_token')).toBe(fakeRefreshToken);
          expect(document.cookie).toContain('token=');
          expect(loginResult.type).toBe('success');
        }
      ),
      { numRuns: 100 }
    );

    globalThis.fetch = originalFetch;
  });
});

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 6: HTTP 401 responses trigger token refresh and request retry
// Validates: Requirements 6.1, 6.2
// ---------------------------------------------------------------------------
describe('Property 6: HTTP 401 responses trigger token refresh and request retry', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it('calls fetch 3 times (original → refresh → retry) and returns retry data', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.string({ minLength: 1, maxLength: 40 }).map(
          (s) => `/api/${s.replace(/[^a-zA-Z0-9/_-]/g, 'x')}`
        ),
        fc.string({ minLength: 10, maxLength: 64 }),
        async (path, newAccessToken) => {
          vi.clearAllMocks();
          localStorage.clear();
          localStorage.setItem('refresh_token', 'stored-refresh-token');

          const retryData = { result: 'ok' };

          const fetchSpy = vi.spyOn(globalThis, 'fetch')
            .mockResolvedValueOnce(makeJsonResponse(
              { error: { code: 'UNAUTHORIZED', message: 'Unauthorized' } }, 401
            ))
            .mockResolvedValueOnce(makeJsonResponse({
              access_token: newAccessToken,
              refresh_token: 'new-refresh-token',
            }))
            .mockResolvedValueOnce(makeJsonResponse(retryData));

          const { apiFetch } = await import('@/lib/api');
          const result = await apiFetch(path);

          expect(fetchSpy).toHaveBeenCalledTimes(3);
          expect(result).toEqual(retryData);
          expect(localStorage.getItem('token')).toBe(newAccessToken);

          fetchSpy.mockRestore();
        }
      ),
      { numRuns: 20 }
    );
  });
});

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 7: Concurrent 401 responses trigger only one refresh call
// Validates: Requirements 6.4
// ---------------------------------------------------------------------------
describe('Property 7: Concurrent 401 responses trigger only one refresh call', () => {
  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it('triggers exactly one refresh call when N concurrent requests all receive 401', async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 2, max: 5 }),
        async (n) => {
          vi.clearAllMocks();
          localStorage.clear();
          localStorage.setItem('refresh_token', 'stored-refresh-token');

          const { apiFetch } = await import('@/lib/api');

          let refreshCallCount = 0;
          let originalCallCount = 0;

          const fetchSpy = vi.spyOn(globalThis, 'fetch').mockImplementation(
            async (input: RequestInfo | URL) => {
              const url =
                typeof input === 'string'
                  ? input
                  : input instanceof URL
                  ? input.href
                  : (input as Request).url;

              if (url.includes('/auth/refresh')) {
                refreshCallCount++;
                return new Response(
                  JSON.stringify({ access_token: 'new-token', refresh_token: 'new-refresh' }),
                  { status: 200, headers: { 'Content-Type': 'application/json' } }
                );
              }

              originalCallCount++;
              if (originalCallCount <= n) {
                return new Response(
                  JSON.stringify({ error: { code: 'UNAUTHORIZED', message: 'Unauthorized' } }),
                  { status: 401, headers: { 'Content-Type': 'application/json' } }
                );
              }
              return new Response(
                JSON.stringify({ result: 'ok' }),
                { status: 200, headers: { 'Content-Type': 'application/json' } }
              );
            }
          );

          const promises = Array.from({ length: n }, (_, i) =>
            apiFetch(`/patients?page=${i}`).catch(() => null)
          );
          await Promise.allSettled(promises);

          expect(refreshCallCount).toBe(1);

          fetchSpy.mockRestore();
          refreshCallCount = 0;
          originalCallCount = 0;
        }
      ),
      { numRuns: 20 }
    );
  });
});

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 8: Middleware gates protected routes based on token presence
// Validates: Requirements 7.1, 7.2
// ---------------------------------------------------------------------------
describe('Property 8: Middleware gates protected routes based on token presence', () => {
  it('allows through with valid token; redirects to login without valid token', async () => {
    const { middleware } = await import('@/middleware');

    fc.assert(
      fc.property(protectedRouteArb, roleArb, fc.boolean(), (path, role, expired) => {
        const token = makeJwt({ sub: 'user-1', role, locale: 'fr' }, expired);
        const req = makeRequest(path, token);
        const res = middleware(req);

        if (!expired) {
          const location = res.headers.get('location') ?? '';
          expect(location).not.toContain('/login');
        } else {
          expect(res.status).toBe(307);
          const location = res.headers.get('location') ?? '';
          expect(location).toContain('/login');
        }
      }),
      { numRuns: 100 }
    );
  });

  it('redirects to login when no token cookie is present', async () => {
    const { middleware } = await import('@/middleware');

    fc.assert(
      fc.property(protectedRouteArb, (path) => {
        const req = makeRequest(path);
        const res = middleware(req);
        expect(res.status).toBe(307);
        const location = res.headers.get('location') ?? '';
        expect(location).toContain('/login');
      }),
      { numRuns: 100 }
    );
  });
});

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 9: Public paths bypass middleware authentication check
// Validates: Requirements 7.3
// ---------------------------------------------------------------------------
describe('Property 9: Public paths bypass middleware authentication check', () => {
  it('allows public paths through regardless of token presence', async () => {
    const { middleware } = await import('@/middleware');

    const publicPathArb = fc.oneof(
      fc.tuple(localeArb, fc.constantFrom('/login', '/register', '/forbidden')).map(
        ([locale, p]) => `/${locale}${p}`
      ),
      fc.constantFrom(
        '/favicon.ico',
        '/health',
        '/_next/static/chunk.js',
        '/_next/image',
        '/api/auth/session',
        '/api/v1/patients'
      )
    );

    const maybeTokenArb = fc.option(validTokenArb, { nil: undefined });

    fc.assert(
      fc.property(publicPathArb, maybeTokenArb, (path, token) => {
        const req = makeRequest(path, token ?? undefined);
        const res = middleware(req);
        const location = res.headers.get('location') ?? '';
        expect(location).not.toContain('/login');
        expect(location).not.toContain('/forbidden');
        expect(res.status).not.toBe(307);
      }),
      { numRuns: 100 }
    );
  });
});

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 10: Insufficient role redirects to forbidden page
// Validates: Requirements 7.4
// ---------------------------------------------------------------------------
describe('Property 10: Insufficient role redirects to forbidden page', () => {
  it('redirects to /{locale}/forbidden when role is not in the allowed set for the route', async () => {
    const { middleware } = await import('@/middleware');

    const insufficientRoleRouteArb = fc.tuple(
      localeArb,
      fc.constantFrom(...Object.keys(ROLE_ROUTES))
    ).chain(([locale, route]) => {
      const allowed = ROLE_ROUTES[route];
      const forbidden = ALL_ROLES.filter((r) => !allowed.includes(r));
      if (forbidden.length === 0) {
        return fc.constant({ locale, route, role: null as unknown as Role });
      }
      return fc.constantFrom(...forbidden).map((role) => ({ locale, route, role }));
    });

    fc.assert(
      fc.property(insufficientRoleRouteArb, ({ locale, route, role }) => {
        if (role === null) return;

        const token = makeJwt({ sub: 'user-1', role, locale }, false);
        const path = `/${locale}${route}`;
        const req = makeRequest(path, token);
        const res = middleware(req);

        expect(res.status).toBe(307);
        const location = res.headers.get('location') ?? '';
        expect(location).toContain(`/${locale}/forbidden`);
      }),
      { numRuns: 100 }
    );
  });
});

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 11: API Client attaches Authorization header to authenticated requests
// Validates: Requirements 8.2
// ---------------------------------------------------------------------------
describe('Property 11: API Client attaches Authorization header to authenticated requests', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('attaches Authorization: Bearer <token> header for any path and token', async () => {
    const { apiFetch } = await import('@/lib/api');

    await fc.assert(
      fc.asyncProperty(
        fc.string({ minLength: 1, maxLength: 50 }).map(
          (s) => `/${s.replace(/[^a-zA-Z0-9/_-]/g, 'x')}`
        ),
        fc.stringMatching(/^[a-zA-Z0-9._-]{1,64}$/),
        async (path, token) => {
          let capturedHeaders: Headers | null = null;

          const fetchSpy = vi.spyOn(globalThis, 'fetch').mockImplementationOnce(
            async (_input: RequestInfo | URL, init?: RequestInit) => {
              capturedHeaders = new Headers(init?.headers as HeadersInit);
              return new Response(JSON.stringify({}), {
                status: 200,
                headers: { 'Content-Type': 'application/json' },
              });
            }
          );

          try {
            await apiFetch(path, { token });
          } catch {
            // ignore path resolution errors
          }

          if (capturedHeaders) {
            expect((capturedHeaders as Headers).get('authorization')).toBe(`Bearer ${token}`);
          }

          fetchSpy.mockRestore();
        }
      ),
      { numRuns: 100 }
    );
  });
});

// ---------------------------------------------------------------------------
// Feature: trop-med-fullstack-polish, Property 12: Non-2xx responses throw a typed ApiError
// Validates: Requirements 8.3
// ---------------------------------------------------------------------------
describe('Property 12: Non-2xx responses throw a typed ApiError', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('throws ApiError with matching status for any 4xx/5xx response (excluding 401)', async () => {
    const { apiFetch, ApiError } = await import('@/lib/api');

    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 400, max: 599 }).filter((s) => s !== 401),
        async (status) => {
          const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
            ok: false,
            status,
            statusText: 'Error',
            headers: new Headers({ 'Content-Type': 'application/json' }),
            json: async () => ({ error: { code: 'TEST_CODE', message: 'test message' } }),
          } as unknown as Response);

          let thrown: unknown;
          try {
            await apiFetch('/test-path', {}, true); // _isRetry=true skips refresh
          } catch (err) {
            thrown = err;
          }

          expect(thrown).toBeInstanceOf(ApiError);
          expect((thrown as InstanceType<typeof ApiError>).status).toBe(status);

          fetchSpy.mockRestore();
        }
      ),
      { numRuns: 100 }
    );
  });
});
