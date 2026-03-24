"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

export type Role = "admin" | "doctor" | "nurse" | "researcher" | "patient";

export interface User {
  sub: string;
  role: Role;
  locale: string;
  exp: number;
}

export type LoginResult =
  | { type: "success" }
  | { type: "mfa_required"; userId: string };

export interface AuthContextValue {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  login(email: string, password: string): Promise<LoginResult>;
  logout(): void;
  refresh(): Promise<void>;
  isAuthenticated: boolean;
}

/** Decode a JWT payload without verifying the signature. */
function parseToken(t: string | null): User | null {
  if (!t) return null;
  try {
    const payload = JSON.parse(atob(t.split(".")[1]));
    return {
      sub: payload.sub,
      role: payload.role as Role,
      locale: payload.locale ?? "fr",
      exp: payload.exp ?? 0,
    };
  } catch {
    return null;
  }
}

/** Returns true when the token expires within `thresholdSeconds` seconds. */
function isExpiringSoon(user: User | null, thresholdSeconds = 60): boolean {
  if (!user || !user.exp) return false;
  const nowSeconds = Math.floor(Date.now() / 1000);
  return user.exp - nowSeconds <= thresholdSeconds;
}

/** Write the access token to the `token` cookie so Next.js Middleware can read it. */
function setTokenCookie(token: string): void {
  if (typeof document === "undefined") return;
  document.cookie = `token=${token}; path=/; SameSite=Lax`;
}

/** Clear the `token` cookie. */
function clearTokenCookie(): void {
  if (typeof document === "undefined") return;
  document.cookie = "token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
}

export function useAuth(): AuthContextValue {
  const [token, setToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  // Hydrate from localStorage after mount to avoid SSR/client mismatch
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedRefresh = localStorage.getItem("refresh_token");
    setToken(storedToken);
    setRefreshToken(storedRefresh);
    setUser(parseToken(storedToken));
  }, []);

  // In-flight refresh promise — shared so concurrent callers don't trigger multiple refreshes.
  const refreshPromiseRef = useRef<Promise<void> | null>(null);

  /** Persist tokens to localStorage and mirror access token to cookie. */
  const storeTokens = useCallback((accessToken: string, newRefreshToken: string) => {
    localStorage.setItem("token", accessToken);
    localStorage.setItem("refresh_token", newRefreshToken);
    setTokenCookie(accessToken);
    const parsed = parseToken(accessToken);
    setToken(accessToken);
    setRefreshToken(newRefreshToken);
    setUser(parsed);
  }, []);

  /** Call /auth/refresh and update stored tokens. */
  const refresh = useCallback(async (): Promise<void> => {
    // Reuse an in-flight refresh if one is already running.
    if (refreshPromiseRef.current) {
      return refreshPromiseRef.current;
    }

    const storedRefreshToken =
      typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;

    if (!storedRefreshToken) {
      throw new Error("No refresh token available");
    }

    const promise = api<{ access_token: string; refresh_token: string }>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: storedRefreshToken }),
    })
      .then((data) => {
        storeTokens(data.access_token, data.refresh_token);
      })
      .finally(() => {
        refreshPromiseRef.current = null;
      });

    refreshPromiseRef.current = promise;
    return promise;
  }, [storeTokens]);

  /**
   * Proactively refresh if the current token is within 60 s of expiry.
   * Called by the API client before each request.
   */
  const refreshIfExpiringSoon = useCallback(async (): Promise<void> => {
    const currentUser =
      typeof window !== "undefined" ? parseToken(localStorage.getItem("token")) : null;
    if (isExpiringSoon(currentUser)) {
      await refresh();
    }
  }, [refresh]);

  const login = useCallback(
    async (email: string, password: string): Promise<LoginResult> => {
      const data = await api<
        | { access_token: string; refresh_token: string }
        | { mfa_required: true; user_id: string }
      >("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      if ("mfa_required" in data && data.mfa_required) {
        return { type: "mfa_required", userId: data.user_id };
      }

      const tokenData = data as { access_token: string; refresh_token: string };
      storeTokens(tokenData.access_token, tokenData.refresh_token);
      return { type: "success" };
    },
    [storeTokens]
  );

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    clearTokenCookie();
    setToken(null);
    setRefreshToken(null);
    setUser(null);
    window.location.href = "/fr/login";
  }, []);

  return {
    token,
    refreshToken,
    user,
    login,
    logout,
    refresh,
    isAuthenticated: !!token,
    // Expose for API client use (not part of the public interface but useful internally)
    ...(typeof window !== "undefined" ? { refreshIfExpiringSoon } : {}),
  } as AuthContextValue & { refreshIfExpiringSoon?: () => Promise<void> };
}
