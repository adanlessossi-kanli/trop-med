"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";

interface User {
  sub: string;
  role: string;
  locale: string;
}

export function useAuth() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const t = localStorage.getItem("token");
    if (t) {
      setToken(t);
      try {
        const payload = JSON.parse(atob(t.split(".")[1]));
        setUser({ sub: payload.sub, role: payload.role, locale: payload.locale });
      } catch {
        setUser(null);
      }
    }
  }, []);

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
