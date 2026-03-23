"use client";

import { useCallback, useState } from "react";
import { api } from "@/lib/api";

interface User {
  sub: string;
  role: string;
  locale: string;
}

function parseToken(t: string | null): User | null {
  if (!t) return null;
  try {
    const payload = JSON.parse(atob(t.split(".")[1]));
    return { sub: payload.sub, role: payload.role, locale: payload.locale };
  } catch {
    return null;
  }
}

export function useAuth() {
  const [token, setToken] = useState<string | null>(() =>
    typeof window !== "undefined" ? localStorage.getItem("token") : null
  );
  const [user, setUser] = useState<User | null>(() =>
    typeof window !== "undefined" ? parseToken(localStorage.getItem("token")) : null
  );

  const login = useCallback(async (email: string, password: string) => {
    const data = await api<{ access_token: string; refresh_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    document.cookie = `token=${data.access_token}; path=/`;
    setToken(data.access_token);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    document.cookie = "token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    setToken(null);
    setUser(null);
    window.location.href = "/fr/login";
  }, []);

  return { token, user, login, logout, isAuthenticated: !!token };
}
