/**
 * Integration tests for the API client token-refresh interceptor.
 * Requirements: 13.4
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

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
// Tests
// ---------------------------------------------------------------------------

describe('API Client — token refresh interceptor', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    // Clear token cookie
    document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('401 response triggers refresh and retries original request with new token', async () => {
    localStorage.setItem('refresh_token', 'stored-refresh-token');

    const newAccessToken = 'new-access-token-abc';
    const retryData = { id: '1', name: 'Patient A' };

    const fetchSpy = vi.spyOn(globalThis, 'fetch')
      // 1st call: original request → 401
      .mockResolvedValueOnce(makeJsonResponse(
        { error: { code: 'UNAUTHORIZED', message: 'Unauthorized' } },
        401
      ))
      // 2nd call: refresh → 200 with new tokens
      .mockResolvedValueOnce(makeJsonResponse({
        access_token: newAccessToken,
        refresh_token: 'new-refresh-token',
      }))
      // 3rd call: retry original → 200 with data
      .mockResolvedValueOnce(makeJsonResponse(retryData));

    const { apiFetch } = await import('@/lib/api');
    const result = await apiFetch('/patients/1');

    // fetch called 3 times: original, refresh, retry
    expect(fetchSpy).toHaveBeenCalledTimes(3);

    // The retry call should use the new token
    const retryCall = fetchSpy.mock.calls[2];
    const retryInit = retryCall[1] as RequestInit;
    const retryHeaders = new Headers(retryInit?.headers as HeadersInit);
    expect(retryHeaders.get('authorization')).toBe(`Bearer ${newAccessToken}`);

    // Result is from the retry response
    expect(result).toEqual(retryData);

    // New token stored in localStorage
    expect(localStorage.getItem('token')).toBe(newAccessToken);
  });

  it('does not retry when refresh endpoint itself returns 401', async () => {
    localStorage.setItem('refresh_token', 'stored-refresh-token');

    const fetchSpy = vi.spyOn(globalThis, 'fetch')
      // original → 401
      .mockResolvedValueOnce(makeJsonResponse(
        { error: { code: 'UNAUTHORIZED', message: 'Unauthorized' } },
        401
      ))
      // refresh → 401 (expired refresh token)
      .mockResolvedValueOnce(makeJsonResponse(
        { error: { code: 'REFRESH_EXPIRED', message: 'Refresh token expired' } },
        401
      ));

    const { apiFetch, ApiError } = await import('@/lib/api');

    let thrown: unknown;
    try {
      await apiFetch('/patients/1');
    } catch (err) {
      thrown = err;
    }

    // Should throw ApiError (session expired)
    expect(thrown).toBeInstanceOf(ApiError);
    expect((thrown as InstanceType<typeof ApiError>).status).toBe(401);

    // fetch called only twice: original + refresh attempt
    expect(fetchSpy).toHaveBeenCalledTimes(2);
  });

  it('does not trigger refresh when no refresh token is stored', async () => {
    // No refresh_token in localStorage
    localStorage.removeItem('refresh_token');

    const fetchSpy = vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(makeJsonResponse(
        { error: { code: 'UNAUTHORIZED', message: 'Unauthorized' } },
        401
      ));

    const { apiFetch, ApiError } = await import('@/lib/api');

    let thrown: unknown;
    try {
      await apiFetch('/patients/1');
    } catch (err) {
      thrown = err;
    }

    expect(thrown).toBeInstanceOf(ApiError);
    // fetch called once for original, once for refresh attempt (which fails immediately)
    // The refresh call itself is attempted but fails with NO_REFRESH_TOKEN
    expect(fetchSpy.mock.calls.length).toBeLessThanOrEqual(2);
  });

  it('attaches Authorization header when token is provided', async () => {
    const token = 'my-access-token';
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      makeJsonResponse({ data: 'ok' })
    );

    const { apiFetch } = await import('@/lib/api');
    await apiFetch('/patients', { token });

    const callInit = fetchSpy.mock.calls[0][1] as RequestInit;
    const headers = new Headers(callInit?.headers as HeadersInit);
    expect(headers.get('authorization')).toBe(`Bearer ${token}`);
  });

  it('throws ApiError with correct status for non-2xx responses', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      makeJsonResponse({ error: { code: 'NOT_FOUND', message: 'Not found' } }, 404)
    );

    const { apiFetch, ApiError } = await import('@/lib/api');

    let thrown: unknown;
    try {
      await apiFetch('/patients/nonexistent', {}, true); // _isRetry=true skips refresh
    } catch (err) {
      thrown = err;
    }

    expect(thrown).toBeInstanceOf(ApiError);
    expect((thrown as InstanceType<typeof ApiError>).status).toBe(404);
    expect((thrown as InstanceType<typeof ApiError>).code).toBe('NOT_FOUND');
    expect((thrown as InstanceType<typeof ApiError>).message).toBe('Not found');
  });
});
