import { NextRequest, NextResponse } from "next/server";

type Role = "admin" | "doctor" | "nurse" | "researcher" | "patient";

/** Routes that require specific roles. All other authenticated routes are open to any role. */
const ROLE_ROUTES: Record<string, Role[]> = {
  "/patients": ["admin", "doctor", "nurse"],
  "/surveillance": ["admin", "doctor", "researcher"],
  "/settings": ["admin"],
  "/chat": ["admin", "doctor", "nurse", "researcher", "patient"],
  "/notifications": ["admin", "doctor", "nurse", "researcher", "patient"],
};

/** Public path prefixes — bypass auth entirely. */
const PUBLIC_PREFIXES = ["/_next", "/api", "/favicon.ico", "/health"];

/** Public path suffixes/exact matches (locale-prefixed). */
const PUBLIC_PATHS = ["/login", "/register", "/forbidden"];

const DEFAULT_LOCALE = "fr";

/** Decode a JWT payload without verifying the signature. Returns null on any failure. */
function decodeJwtPayload(token: string): { sub: string; role: Role; locale?: string; exp?: number } | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    // Base64url → Base64 → JSON
    const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = Buffer.from(base64, "base64").toString("utf-8");
    const payload = JSON.parse(json);
    if (!payload.sub || !payload.role) return null;
    return payload as { sub: string; role: Role; locale?: string; exp?: number };
  } catch {
    return null;
  }
}

/** Extract the locale from the URL path (first segment). Falls back to DEFAULT_LOCALE. */
function extractLocale(pathname: string): string {
  const segment = pathname.split("/")[1];
  return segment === "fr" || segment === "en" ? segment : DEFAULT_LOCALE;
}

/** Check whether the token is expired. */
function isExpired(exp: number | undefined): boolean {
  if (!exp) return false;
  return Math.floor(Date.now() / 1000) >= exp;
}

export function middleware(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;

  // 1. Allow public prefixes through unconditionally.
  for (const prefix of PUBLIC_PREFIXES) {
    if (pathname.startsWith(prefix)) {
      return NextResponse.next();
    }
  }

  // 2. Extract locale and the path without the locale prefix.
  const locale = extractLocale(pathname);
  const pathWithoutLocale = pathname.replace(/^\/(fr|en)/, "") || "/";

  // 3. Allow public paths (login, register, forbidden) through unconditionally.
  for (const pub of PUBLIC_PATHS) {
    if (pathWithoutLocale === pub || pathWithoutLocale.startsWith(pub + "/")) {
      return NextResponse.next();
    }
  }

  // 4. Read and decode the token cookie.
  const tokenCookie = request.cookies.get("token")?.value ?? null;
  const payload = tokenCookie ? decodeJwtPayload(tokenCookie) : null;
  const isAuthenticated = payload !== null && !isExpired(payload.exp);

  // 5. Unauthenticated → redirect to /{locale}/login?next=<original-url>
  if (!isAuthenticated) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = `/${locale}/login`;
    loginUrl.search = `?next=${encodeURIComponent(request.nextUrl.pathname + request.nextUrl.search)}`;
    return NextResponse.redirect(loginUrl);
  }

  // 6. Role check for restricted routes.
  for (const [route, allowedRoles] of Object.entries(ROLE_ROUTES)) {
    if (pathWithoutLocale === route || pathWithoutLocale.startsWith(route + "/")) {
      if (!allowedRoles.includes(payload!.role)) {
        const forbiddenUrl = request.nextUrl.clone();
        forbiddenUrl.pathname = `/${locale}/forbidden`;
        forbiddenUrl.search = "";
        return NextResponse.redirect(forbiddenUrl);
      }
      break;
    }
  }

  // 7. Authenticated with sufficient role — allow through.
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next|api|favicon\\.ico|health).*)"],
};
