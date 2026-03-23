const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

type FetchOptions = RequestInit & { token?: string };

export async function api<T = unknown>(path: string, opts: FetchOptions = {}): Promise<T> {
  const { token, headers, ...rest } = opts;
  const res = await fetch(`${API_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    ...rest,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.error?.message || res.statusText);
  }
  return res.json();
}
