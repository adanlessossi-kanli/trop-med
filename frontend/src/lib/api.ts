const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// ---------------------------------------------------------------------------
// ApiError
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    public message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ---------------------------------------------------------------------------
// TypeScript interfaces for response types
// ---------------------------------------------------------------------------

export interface Patient {
  id: string;
  full_name: string;
  date_of_birth?: string;
  gender?: string;
  nationality?: string;
  contact_info?: Record<string, string>;
  medical_record_number?: string;
  created_at?: string;
  updated_at?: string;
}

export interface PatientCreate {
  full_name: string;
  date_of_birth?: string;
  gender?: string;
  nationality?: string;
  contact_info?: Record<string, string>;
  medical_record_number?: string;
}

export interface PatientListResponse {
  items: Patient[];
  total: number;
  skip: number;
  limit: number;
}

export interface Encounter {
  id: string;
  patient_id: string;
  encounter_date: string;
  chief_complaint?: string;
  diagnosis?: string;
  treatment?: string;
  notes?: string;
  created_by?: string;
  created_at?: string;
}

export interface EncounterCreate {
  patient_id: string;
  encounter_date: string;
  chief_complaint?: string;
  diagnosis?: string;
  treatment?: string;
  notes?: string;
}

export interface EncounterListResponse {
  items: Encounter[];
  total: number;
}

export interface AiQueryResponse {
  answer: string;
  confidence: number;
  sources?: string[];
}

export interface DifferentialResponse {
  differentials: Array<{ diagnosis: string; probability: number; reasoning: string }>;
}

export interface LiteratureResponse {
  results: Array<{ title: string; abstract: string; url?: string; authors?: string[] }>;
}

export interface FileUploadResponse {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  url?: string;
  patient_id?: string;
  uploaded_at?: string;
}

export interface FileListResponse {
  items: FileUploadResponse[];
  total: number;
}

export interface Alert {
  id: string;
  type: string;
  severity: string;
  message: string;
  patient_id?: string;
  created_at?: string;
  resolved?: boolean;
}

export interface AlertListResponse {
  items: Alert[];
  total: number;
}

export interface SurveillanceStats {
  total_alerts: number;
  active_alerts: number;
  resolved_alerts: number;
  by_severity: Record<string, number>;
  by_type: Record<string, number>;
}

export interface Notification {
  id: string;
  type: string;
  message: string;
  read: boolean;
  created_at?: string;
}

export interface NotificationListResponse {
  items: Notification[];
  total: number;
  unread_count: number;
}

export interface GdprExportResponse {
  patient_id: string;
  export_url?: string;
  data?: Record<string, unknown>;
  exported_at: string;
}

// ---------------------------------------------------------------------------
// Base fetch options and apiFetch
// ---------------------------------------------------------------------------

type ApiFetchOptions = {
  method?: string;
  body?: BodyInit | null;
  headers?: Record<string, string>;
  token?: string;
  signal?: AbortSignal;
};

// ---------------------------------------------------------------------------
// Token refresh interceptor
// ---------------------------------------------------------------------------

/** Shared in-flight refresh promise — prevents concurrent 401s from triggering multiple refreshes. */
let refreshInFlight: Promise<string> | null = null;

async function doRefresh(): Promise<string> {
  if (refreshInFlight) return refreshInFlight;

  refreshInFlight = (async () => {
    const storedRefreshToken =
      typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;

    if (!storedRefreshToken) {
      throw new ApiError(401, "NO_REFRESH_TOKEN", "No refresh token available");
    }

    const data = await apiFetch<{ access_token: string; refresh_token: string }>(
      "/auth/refresh",
      { method: "POST", body: JSON.stringify({ refresh_token: storedRefreshToken }) }
    );

    // Store new tokens
    if (typeof window !== "undefined") {
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      document.cookie = `token=${data.access_token}; path=/; SameSite=Lax`;
    }

    return data.access_token;
  })().finally(() => {
    refreshInFlight = null;
  });

  return refreshInFlight;
}

function clearAuthAndRedirect(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  document.cookie = "token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  const locale = localStorage.getItem("locale") ?? "fr";
  window.location.href = `/${locale}/login`;
}

export async function apiFetch<T = unknown>(
  path: string,
  opts: ApiFetchOptions = {},
  _isRetry = false
): Promise<T> {
  const { token, headers, signal, body, method } = opts;

  const requestHeaders: Record<string, string> = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...headers,
  };

  // Only set Content-Type for JSON bodies (not FormData)
  if (body && !(body instanceof FormData)) {
    requestHeaders["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_URL}${path}`, {
    method: method ?? "GET",
    headers: requestHeaders,
    body: body ?? undefined,
    signal,
  });

  if (!res.ok) {
    // Intercept 401 for token refresh (but not on the refresh endpoint itself, and not on retry)
    if (res.status === 401 && !_isRetry && !path.includes("/auth/refresh")) {
      try {
        const newToken = await doRefresh();
        // Replay original request with new token
        return apiFetch<T>(path, { ...opts, token: newToken }, true);
      } catch {
        clearAuthAndRedirect();
        throw new ApiError(401, "SESSION_EXPIRED", "Session expired. Please log in again.");
      }
    }

    let code = "UNKNOWN_ERROR";
    let message = res.statusText;
    try {
      const errBody = await res.json();
      code = errBody?.error?.code ?? code;
      message = errBody?.error?.message ?? message;
    } catch {
      // fallback to statusText already set
    }
    throw new ApiError(res.status, code, message);
  }

  // 204 No Content or void responses
  const contentType = res.headers.get("content-type");
  if (res.status === 204 || !contentType?.includes("application/json")) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Backward-compatible `api` export (used by useAuth.ts)
// ---------------------------------------------------------------------------

type FetchOptions = RequestInit & { token?: string };

export async function api<T = unknown>(path: string, opts: FetchOptions = {}): Promise<T> {
  const { token, headers, signal, body, method, ...rest } = opts;
  return apiFetch<T>(path, {
    method: method as string | undefined,
    body: body as BodyInit | null | undefined,
    headers: headers as Record<string, string> | undefined,
    token,
    signal: signal ?? undefined,
    ...rest,
  });
}

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------

export const authApi = {
  login: (body: { email: string; password: string }, token?: string) =>
    apiFetch<
      | { access_token: string; refresh_token: string }
      | { mfa_required: true; user_id: string }
    >("/auth/login", { method: "POST", body: JSON.stringify(body), token }),

  register: (body: { email: string; password: string; full_name: string }, token?: string) =>
    apiFetch<{ access_token: string; refresh_token: string }>(
      "/auth/register",
      { method: "POST", body: JSON.stringify(body), token }
    ),

  refresh: (refreshToken: string) =>
    apiFetch<{ access_token: string; refresh_token: string }>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),

  logout: (token: string) =>
    apiFetch<void>("/auth/logout", { method: "POST", token }),

  setupMfa: (token: string) =>
    apiFetch<{ secret: string; qr_code: string }>("/auth/mfa/setup", {
      method: "POST",
      token,
    }),

  verifyMfa: (body: { user_id: string; code: string }) =>
    apiFetch<{ access_token: string; refresh_token: string }>("/auth/mfa/verify", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};

// ---------------------------------------------------------------------------
// Patients API
// ---------------------------------------------------------------------------

export const patientsApi = {
  list: (
    params: { search?: string; skip?: number; limit?: number },
    token: string,
    signal?: AbortSignal
  ) => {
    const qs = new URLSearchParams();
    if (params.search) qs.set("search", params.search);
    if (params.skip !== undefined) qs.set("skip", String(params.skip));
    if (params.limit !== undefined) qs.set("limit", String(params.limit));
    const query = qs.toString();
    return apiFetch<PatientListResponse>(`/patients${query ? `?${query}` : ""}`, {
      token,
      signal,
    });
  },

  get: (id: string, token: string, signal?: AbortSignal) =>
    apiFetch<Patient>(`/patients/${id}`, { token, signal }),

  create: (body: PatientCreate, token: string) =>
    apiFetch<Patient>("/patients", { method: "POST", body: JSON.stringify(body), token }),

  update: (id: string, body: Partial<PatientCreate>, token: string) =>
    apiFetch<Patient>(`/patients/${id}`, {
      method: "PUT",
      body: JSON.stringify(body),
      token,
    }),

  delete: (id: string, token: string) =>
    apiFetch<void>(`/patients/${id}`, { method: "DELETE", token }),
};

// ---------------------------------------------------------------------------
// Clinical API
// ---------------------------------------------------------------------------

export const clinicalApi = {
  getEncounters: (patientId: string, token: string, signal?: AbortSignal) =>
    apiFetch<EncounterListResponse>(
      `/clinical/encounters?patient_id=${encodeURIComponent(patientId)}`,
      { token, signal }
    ),

  createEncounter: (body: EncounterCreate, token: string) =>
    apiFetch<Encounter>("/clinical/encounters", {
      method: "POST",
      body: JSON.stringify(body),
      token,
    }),
};

// ---------------------------------------------------------------------------
// AI API
// ---------------------------------------------------------------------------

export const aiApi = {
  query: (body: { question: string; patient_id?: string }, token: string) =>
    apiFetch<AiQueryResponse>("/ai/query", {
      method: "POST",
      body: JSON.stringify(body),
      token,
    }),

  differential: (body: { symptoms: string[]; patient_id?: string }, token: string) =>
    apiFetch<DifferentialResponse>("/ai/differential", {
      method: "POST",
      body: JSON.stringify(body),
      token,
    }),

  literature: (query: string, token: string, signal?: AbortSignal) =>
    apiFetch<LiteratureResponse>(
      `/ai/literature?q=${encodeURIComponent(query)}`,
      { token, signal }
    ),
};

// ---------------------------------------------------------------------------
// Files API
// ---------------------------------------------------------------------------

export const filesApi = {
  upload: (formData: FormData, token: string) =>
    apiFetch<FileUploadResponse>("/files/upload", {
      method: "POST",
      body: formData,
      token,
    }),

  list: (patientId: string, token: string, signal?: AbortSignal) =>
    apiFetch<FileListResponse>(
      `/files?patient_id=${encodeURIComponent(patientId)}`,
      { token, signal }
    ),
};

// ---------------------------------------------------------------------------
// Surveillance API
// ---------------------------------------------------------------------------

export const surveillanceApi = {
  getAlerts: (token: string, signal?: AbortSignal) =>
    apiFetch<AlertListResponse>("/surveillance/alerts", { token, signal }),

  getStats: (token: string, signal?: AbortSignal) =>
    apiFetch<SurveillanceStats>("/surveillance/stats", { token, signal }),
};

// ---------------------------------------------------------------------------
// Notifications API
// ---------------------------------------------------------------------------

export const notificationsApi = {
  list: (token: string, signal?: AbortSignal) =>
    apiFetch<NotificationListResponse>("/notifications", { token, signal }),

  markRead: (id: string, token: string) =>
    apiFetch<void>(`/notifications/${id}/read`, { method: "POST", token }),

  markAllRead: (token: string) =>
    apiFetch<void>("/notifications/read-all", { method: "POST", token }),
};

// ---------------------------------------------------------------------------
// GDPR API
// ---------------------------------------------------------------------------

export const gdprApi = {
  exportData: (patientId: string, token: string) =>
    apiFetch<GdprExportResponse>(`/gdpr/export/${encodeURIComponent(patientId)}`, { token }),

  deleteData: (patientId: string, token: string) =>
    apiFetch<void>(`/gdpr/delete/${encodeURIComponent(patientId)}`, {
      method: "DELETE",
      token,
    }),
};

// ---------------------------------------------------------------------------
// WebSocket factory
// ---------------------------------------------------------------------------

export function createChatSocket(token: string): WebSocket {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
  return new WebSocket(`${wsUrl}/chat?token=${encodeURIComponent(token)}`);
}
