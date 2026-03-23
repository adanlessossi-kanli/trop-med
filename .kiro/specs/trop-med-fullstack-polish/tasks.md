# Implementation Plan: Trop-Med Fullstack Polish

## Overview

Incremental implementation of production-grade infrastructure on top of the existing Trop-Med codebase: Tailwind design system, wired auth flow with token refresh, typed API client, MongoDB migration runner, comprehensive tests, documentation, and Docker Compose local dev environment.

## Tasks

- [ ] 1. Install and configure Tailwind CSS
  - Add `tailwindcss`, `postcss`, and `autoprefixer` as dev dependencies in `frontend/package.json`
  - Create `frontend/tailwind.config.ts` extending the default theme with the `tropmed` colour palette (`primary` teal-600, `neutral` slate-500, `danger` red-600, `warning` amber-600)
  - Create or update `frontend/src/app/globals.css` with `@tailwind base`, `@tailwind components`, `@tailwind utilities` directives
  - Import `globals.css` in `frontend/src/app/layout.tsx` (root layout)
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 2. Build shared UI component library
  - [ ] 2.1 Create `Button` component (`frontend/src/components/ui/Button.tsx`)
    - Accept `variant` (`primary` | `secondary` | `danger`), `size` (`sm` | `md` | `lg`), `loading`, `disabled` props
    - Render `Spinner` in place of children when `loading=true`
    - _Requirements: 2.1, 2.8_

  - [ ] 2.2 Write property test for Button loading prop renders Spinner
    - **Property 1: Button loading prop renders Spinner**
    - **Validates: Requirements 2.1, 2.8**

  - [ ] 2.3 Create `Input` component (`frontend/src/components/ui/Input.tsx`)
    - Accept `label`, `error`, `type`, and all standard HTML input attributes
    - Render accessible label and error text
    - _Requirements: 2.2_

  - [ ] 2.4 Create `Card`, `Spinner`, and `Modal` components (`frontend/src/components/ui/`)
    - `Card`: rounded, shadowed container wrapping children
    - `Spinner`: SVG animate-spin, accepts `size` prop
    - `Modal`: accepts `open`, `onClose`, `children`; implement focus-trap via `focus-trap-react`; accessible close button with `aria-label`
    - _Requirements: 2.3, 2.4, 2.7_

  - [ ] 2.5 Create `Badge` component (`frontend/src/components/ui/Badge.tsx`)
    - Accept `role` prop typed as `Role`; render colour-coded background per role
    - _Requirements: 2.5_

  - [ ] 2.6 Write property test for Badge renders colour class for every valid Role
    - **Property 2: Badge renders a colour class for every valid Role**
    - **Validates: Requirements 2.5**

  - [ ] 2.7 Create `Table` component (`frontend/src/components/ui/Table.tsx`)
    - Accept `columns`, `data`, `loading`, `emptySlot` props
    - Render loading skeleton when `loading=true`, empty-state slot when data is empty, data rows otherwise
    - Switch to card-based stacked layout below 640 px via Tailwind responsive classes
    - _Requirements: 2.6, 3.4_

  - [ ] 2.8 Write property test for Table renders correct state for all data/loading combinations
    - **Property 3: Table renders correct state for all data/loading combinations**
    - **Validates: Requirements 2.6**

  - [ ] 2.9 Create `Shell` layout component (`frontend/src/components/ui/Shell.tsx`)
    - Sidebar navigation + top header bar
    - Collapse sidebar into hamburger-menu drawer below 768 px
    - _Requirements: 3.1, 3.2, 3.3_

- [ ] 3. Checkpoint — Ensure all UI component tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement authentication flow
  - [ ] 4.1 Extend `useAuth` hook (`frontend/src/hooks/useAuth.ts`)
    - Expose `refresh()` method callable externally
    - Store tokens in `localStorage` and mirror access token to `token` cookie
    - Proactively refresh when token is within 60 s of expiry (checked on each API call)
    - _Requirements: 6.2, 6.5_

  - [ ] 4.2 Rewrite Next.js Middleware (`frontend/src/middleware.ts`)
    - Decode `token` cookie (JWT, no network call)
    - Allow public paths: `/login`, `/register`, `/_next`, `/api`, `/favicon.ico`, `/health`
    - Redirect unauthenticated requests to `/{locale}/login?next=<original-url>`
    - Redirect insufficient-role requests to `/{locale}/forbidden`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ] 4.3 Write property test for middleware gates protected routes based on token presence
    - **Property 8: Middleware gates protected routes based on token presence**
    - **Validates: Requirements 7.1, 7.2**

  - [ ] 4.4 Write property test for public paths bypass middleware authentication check
    - **Property 9: Public paths bypass middleware authentication check**
    - **Validates: Requirements 7.3**

  - [ ] 4.5 Write property test for insufficient role redirects to forbidden page
    - **Property 10: Insufficient role redirects to forbidden page**
    - **Validates: Requirements 7.4**

  - [ ] 4.6 Redesign login page (`frontend/src/app/[locale]/login/page.tsx`)
    - Use `useAuth().login()` instead of direct `api()` calls
    - Show `Spinner` and disable submit button while submitting
    - Display `auth.invalidCredentials` i18n error on failure
    - Render TOTP input step when `login()` returns `{ type: 'mfa_required' }`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6_

  - [ ] 4.7 Write unit tests for login flow integration
    - Test: successful login → tokens stored → redirect to dashboard
    - Test: failed login → `auth.invalidCredentials` error shown
    - Test: MFA step renders when `mfa_required` returned
    - _Requirements: 5.2, 5.3, 5.6_

  - [ ] 4.8 Write property test for successful login stores tokens and redirects
    - **Property 5: Successful login stores tokens and redirects**
    - **Validates: Requirements 5.2**

- [ ] 5. Build typed API client
  - [ ] 5.1 Rewrite `frontend/src/lib/api.ts`
    - Export typed namespace functions: `authApi`, `patientsApi`, `clinicalApi`, `aiApi`, `filesApi`, `surveillanceApi`, `notificationsApi`, `gdprApi`
    - Attach `Authorization: Bearer <token>` header from `AuthContext`
    - Throw typed `ApiError(status, code, message)` on non-2xx responses
    - Support `AbortController` signal on GET requests
    - Export `createChatSocket(token)` returning a typed `WebSocket`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ] 5.2 Write property test for API Client attaches Authorization header
    - **Property 11: API Client attaches Authorization header to authenticated requests**
    - **Validates: Requirements 8.2**

  - [ ] 5.3 Write property test for non-2xx responses throw a typed ApiError
    - **Property 12: Non-2xx responses throw a typed ApiError**
    - **Validates: Requirements 8.3**

  - [ ] 5.4 Implement refresh-queue interceptor in `api.ts`
    - On 401, call `/auth/refresh` exactly once (shared in-flight promise for concurrent requests)
    - Store new tokens and replay original request on success
    - Clear tokens and redirect to `/{locale}/login` on refresh failure
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ] 5.5 Write property test for HTTP 401 responses trigger token refresh and request retry
    - **Property 6: HTTP 401 responses trigger token refresh and request retry**
    - **Validates: Requirements 6.1, 6.2**

  - [ ] 5.6 Write property test for concurrent 401 responses trigger only one refresh call
    - **Property 7: Concurrent 401 responses trigger only one refresh call**
    - **Validates: Requirements 6.4**

- [ ] 6. Checkpoint — Ensure all auth and API client tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Wire dashboard, navigation, and loading/error states
  - [ ] 7.1 Update dashboard page (`frontend/src/app/[locale]/dashboard/page.tsx`)
    - Use `Shell` layout with sidebar wired to all routes (patients, chat, surveillance, notifications, settings)
    - Display authenticated user's name and `Badge` in header
    - Wire logout button to `useAuth().logout()` → redirect to `/{locale}/login`
    - Use `<Link>` for all internal navigation
    - Display notification badge count when unread notifications exist
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ] 7.2 Add loading states and error handling to page components
    - Wrap each page in an `ErrorBoundary` component with a "Reload" fallback
    - Show `Spinner` or skeleton while API requests are in flight
    - Display `common.error` i18n message on `ApiError`; display `common.networkError` with retry button on network failure
    - Update patients page to show skeleton while fetching and empty-state when list is empty
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ] 7.3 Write property test for loading state shown during in-flight API requests
    - **Property 13: Loading state is shown during in-flight API requests**
    - **Validates: Requirements 9.1**

  - [ ] 7.4 Write property test for error message shown on API failure
    - **Property 14: Error message is shown on API failure**
    - **Validates: Requirements 9.2, 9.4**

  - [ ] 7.5 Add royalty-free images to login page and dashboard
    - Add hero image on login page (Unsplash/Pexels URL or downloaded to `frontend/public/images/`)
    - Add welcome banner image on dashboard
    - Use `next/image` with explicit `width`, `height`, and `alt` for all images
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ] 7.6 Write property test for next/image usages have required accessibility attributes
    - **Property 4: All next/image usages have required accessibility attributes**
    - **Validates: Requirements 4.3, 4.4**

- [ ] 8. Implement MongoDB migration runner
  - [ ] 8.1 Create migration runner (`backend/migrations/runner.py`)
    - Implement `async def run_migrations(db: AsyncIOMotorDatabase) -> None`
    - Apply only migrations whose `version` is absent from `_migrations`, in ascending order
    - On exception: log traceback, halt, leave `_migrations` unchanged for that version
    - Expose CLI entry point: `python -m backend.migrations.runner`
    - _Requirements: 11.1, 11.3, 11.4, 11.5_

  - [ ] 8.2 Create migration scripts
    - `backend/migrations/0001_initial_indexes.py`: move all inline index creation from `main.py` into `up()`
    - `backend/migrations/0002_add_audit_ttl.py`: add TTL index on `audit_logs.timestamp` (90-day expiry)
    - Each module exports `VERSION: int`, `NAME: str`, `async def up(db) -> None`
    - _Requirements: 11.1, 11.7_

  - [ ] 8.3 Wire migration runner into Backend lifespan startup
    - Call `run_migrations(db)` in the FastAPI lifespan after index creation
    - After migrations, check if `_migrations` collection was empty before first run; if so, call `python -m app.scripts.seed`
    - _Requirements: 11.6, 17.7_

  - [ ] 8.4 Write property test for migration runner writes correct records to _migrations
    - **Property 15: Migration runner writes correct records to _migrations**
    - **Validates: Requirements 11.2**

  - [ ] 8.5 Write property test for migration runner is idempotent
    - **Property 16: Migration runner is idempotent**
    - **Validates: Requirements 11.3**

- [ ] 9. Checkpoint — Ensure migration runner tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Write backend test suite
  - [ ] 10.1 Write auth endpoint tests (`backend/tests/test_auth.py`)
    - Cover: register, login (valid), login (invalid credentials), login (inactive account), refresh (valid), refresh (expired), logout, MFA setup, MFA verify (valid code), MFA verify (invalid code)
    - _Requirements: 12.1_

  - [ ] 10.2 Write patient CRUD tests (`backend/tests/test_patients.py`)
    - Cover: create, list with search, get by ID (found/not found), update, delete (admin allowed), delete (nurse forbidden)
    - _Requirements: 12.2_

  - [ ] 10.3 Write role-based access and AI endpoint tests (`backend/tests/test_roles.py`, `backend/tests/test_ai.py`)
    - Role tests: each Role against `/patients`, `/clinical`, `/ai/differential`, `/surveillance`, `/gdpr`
    - AI tests: query (high confidence), query (low confidence warning), differential (doctor allowed), differential (patient forbidden), literature search
    - _Requirements: 12.3, 12.4_

  - [ ] 10.4 Verify 80% line coverage gate
    - Run `pytest --cov=app --cov-fail-under=80` from `backend/`; fix any gaps to meet the threshold
    - _Requirements: 12.5, 12.6_

- [ ] 11. Write frontend test suite
  - [ ] 11.1 Write unit tests for UI components (`frontend/src/__tests__/components.test.tsx`)
    - `Button`: each variant/size, loading spinner, disabled state
    - `Input`: label render, error text, HTML attribute forwarding
    - `Card`: children rendered inside container
    - `Table`: loading skeleton, empty state, data rows
    - `Badge`: correct class for each Role
    - `Modal`: close button `aria-label`, focus trap
    - _Requirements: 13.1, 13.2_

  - [ ] 11.2 Write API client and middleware integration tests (`frontend/src/__tests__/api.test.ts`, `frontend/src/__tests__/middleware.test.ts`)
    - API client: 401 → refresh → retry original request
    - Middleware: unauthenticated → redirect to `/login?next=`, authenticated → pass through, insufficient role → forbidden
    - _Requirements: 13.4, 13.5_

  - [ ] 11.3 Write all frontend property tests (`frontend/src/__tests__/properties.test.ts`)
    - Implement Properties 1–12 using `fast-check` with `numRuns: 100` each
    - Annotate each with `// Feature: trop-med-fullstack-polish, Property N: <title>`
    - _Requirements: 13.1, 13.3, 13.6_

- [ ] 12. Add backend OpenAPI annotations and export script
  - Add `summary`, `description`, and `response_model` to every router endpoint across all route files in `backend/app/api/routes/`
  - Create `backend/app/scripts/export_openapi.py` that writes the schema to `docs/api/openapi.json`
  - _Requirements: 15.1, 15.2, 15.3, 15.4_

- [ ] 13. Set up Docker Compose local dev environment
  - [ ] 13.1 Create or update `docker/docker-compose.yml`
    - Define services: `backend` (uvicorn --reload), `frontend` (next dev), `mongodb`, `redis`, `localstack`, `ai-mock`
    - Set `NEXT_PUBLIC_API_URL`, `API_URL`, `NEXT_PUBLIC_WS_URL` on the frontend service
    - Wire backend to resolve `mongodb:27017`, `redis:6379`, `localstack:4566`, `ai-mock:8080`
    - _Requirements: 17.1, 17.3, 17.4, 17.5, 17.6, 17.8, 17.9_

  - [ ] 13.2 Create `docker/.env` bootstrapped from `backend/.env.example`
    - Pre-fill Docker-internal service hostnames
    - Document every variable with a safe default value
    - _Requirements: 17.2_

  - [ ] 13.3 Create `start.sh` and `start.bat` at repo root
    - Both scripts: `cd docker/ && docker compose --env-file .env up`
    - _Requirements: 17.10, 17.11_

- [ ] 14. Write documentation
  - [ ] 14.1 Write `README.md` at repo root
    - Include: project overview, Mermaid architecture diagram, prerequisites, Docker Compose setup steps, environment variable reference, "Running Tests" section (exact `pytest` and `vitest --run` commands), "Database Migrations" section
    - _Requirements: 14.1, 14.2, 14.3, 14.4_

  - [ ] 14.2 Write `docs/architecture.md`
    - Include: component diagram (Mermaid), auth sequence diagram (Mermaid), WebSocket chat flow, data flow for a typical clinical encounter
    - _Requirements: 16.1, 16.2, 16.3_

  - [ ] 14.3 Write `docs/deployment.md`
    - Include: Docker Compose setup, environment variables, production deployment considerations
    - _Requirements: 16.4_

- [ ] 15. Final checkpoint — Ensure all tests pass
  - Run `pytest` from `backend/` and `vitest --run` from `frontend/`; ensure zero failures and ≥ 80% backend coverage.
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests use `fast-check` (frontend) and `hypothesis` (backend) with at least 100 iterations each
- Checkpoints ensure incremental validation before moving to the next phase
