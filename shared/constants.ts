export const ROLES = ["admin", "doctor", "nurse", "researcher", "patient"] as const;
export type Role = (typeof ROLES)[number];

export const LOCALES = ["fr", "en"] as const;
export type Locale = (typeof LOCALES)[number];

export const SUPPORTED_FILE_TYPES = [
  "application/pdf",
  "image/png",
  "image/jpeg",
  "image/dicom",
  "text/csv",
] as const;

export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50 MB

export const RATE_LIMITS: Record<string, number> = {
  patient: 60,
  nurse: 300,
  doctor: 300,
  researcher: 300,
  admin: 600,
};

export const AI_CONFIDENCE_THRESHOLD = 0.6;
