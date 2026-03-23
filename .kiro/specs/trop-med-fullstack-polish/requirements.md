# Requirements Document

## Introduction

Trop-Med is a clinical platform for tropical medicine, built with a FastAPI backend and a Next.js 16 / React 19 frontend. The platform currently has functional backend routes (auth, patients, clinical, AI, files, surveillance, notifications, GDPR, chat) and basic frontend pages (login, dashboard, patients, chat) that use raw inline styles with no CSS framework, no protected-route middleware, no token-refresh logic, and no documentation. This spec covers the full-stack polish needed to make the platform production-ready: a Tailwind CSS design system, a wired authentication flow, a typed API client with error handling, a versioned MongoDB migration strategy, comprehensive test coverage, and complete documentation.

---

## Glossary

- **App**: The Trop-Med clinical platform as a whole.
- **Frontend**: The Next.js 16 / React 19 application in `frontend/`.
- **Backend**: The FastAPI application in `backend/`.
- **API_Client**: The typed HTTP client in `frontend/src/lib/api.ts` that communicates with the Backend.
- **Auth_Service**: The backend service at `backend/app/services/auth_service.py` that issues and validates JWT tokens.
- **Auth_Hook**: The `useAuth` React hook in `frontend/src/hooks/useAuth.ts`.
- **Middleware**: The Next.js middleware in `frontend/src/middleware.ts` that enforces route protection.
- **Design_System**: The Tailwind CSS configuration, shared component library, and responsive layout primitives used across all Frontend pages.
- **Migration_Runner**: The versioned script system in `backend/migrations/` that applies MongoDB schema changes in order.
- **Token**: A JWT access token issued by the Auth_Service with a 15-minute expiry.
- **Refresh_Token**: A JWT refresh token issued by the Auth_Service with a 7-day expiry.
- **MFA**: Multi-factor authentication via TOTP (time-based one-time password).
- **Role**: One of `admin`, `doctor`, `nurse`, `researcher`, or `patient`, embedded in the Token payload.
- **i18n**: Internationalisation support for French (`fr`) and English (`en`) via `next-intl`.
- **Protected_Route**: Any Frontend page that requires a valid Token to render.
- **Loading_State**: A UI indicator (spinner or skeleton) shown while an async operation is in progress.
- **Error_Boundary**: A React component that catches render errors and displays a fallback UI.

---

## Requirements

### Requirement 1: Design System — Tailwind CSS Installation and Configuration

**User Story:** As a developer, I want Tailwind CSS installed and configured in the frontend, so that all pages can use utility classes instead of inline styles.

#### Acceptance Criteria

1. THE Design_System SHALL include Tailwind CSS v3 (or v4) installed as a dev dependency in `frontend/package.json`.
2. THE Design_System SHALL include a `tailwind.config.ts` that extends the default theme with a `tropmed` colour palette (primary teal, neutral slate, danger red, warning amber).
3. THE Design_System SHALL include a global CSS file imported in the root layout that applies Tailwind's `@tailwind base`, `@tailwind components`, and `@tailwind utilities` directives.
4. WHEN the Frontend is built with `next build`, THE Design_System SHALL produce no Tailwind-related build errors.

---

### Requirement 2: Design System — Shared Component Library

**User Story:** As a developer, I want a set of reusable UI components, so that all pages share a consistent look and feel without duplicating markup.

#### Acceptance Criteria

1. THE Design_System SHALL provide a `Button` component that accepts `variant` (`primary` | `secondary` | `danger`), `size` (`sm` | `md` | `lg`), `loading` (boolean), and `disabled` (boolean) props.
2. THE Design_System SHALL provide an `Input` component that accepts `label`, `error`, `type`, and all standard HTML input attributes.
3. THE Design_System SHALL provide a `Card` component that wraps content in a rounded, shadowed container.
4. THE Design_System SHALL provide a `Spinner` component used as the Loading_State indicator.
5. THE Design_System SHALL provide a `Badge` component that renders a Role label with a colour-coded background.
6. THE Design_System SHALL provide a `Table` component with sortable column headers, a loading skeleton, and an empty-state slot.
7. THE Design_System SHALL provide a `Modal` component with a focus-trap and an accessible close button.
8. WHEN a component receives a `loading` prop set to `true`, THE Design_System SHALL render the Spinner in place of the component's primary action.

---

### Requirement 3: Design System — Responsive Layout

**User Story:** As a clinician using a tablet or mobile device, I want the platform to be usable on any screen size, so that I can access patient data at the bedside.

#### Acceptance Criteria

1. THE Design_System SHALL provide a `Shell` layout component with a collapsible sidebar navigation and a top header bar.
2. WHEN the viewport width is below 768 px, THE Shell SHALL collapse the sidebar into a hamburger-menu drawer.
3. THE Design_System SHALL use Tailwind responsive prefixes (`sm:`, `md:`, `lg:`) consistently across all page layouts.
4. WHEN the viewport width is below 640 px, THE Table component SHALL switch to a card-based stacked layout.
5. THE Design_System SHALL pass Lighthouse mobile usability checks with no critical failures.

---

### Requirement 4: Design System — Free Images via Unsplash/Pexels

**User Story:** As a product owner, I want the login page and dashboard to display high-quality, royalty-free medical images, so that the platform looks professional.

#### Acceptance Criteria

1. THE Design_System SHALL include at least one royalty-free hero image on the login page sourced from Unsplash or Pexels (referenced by URL or downloaded to `frontend/public/images/`).
2. THE Design_System SHALL include at least one royalty-free illustration or photo on the dashboard welcome banner.
3. WHEN an image fails to load, THE Frontend SHALL display an accessible `alt` text fallback.
4. THE Design_System SHALL use `next/image` with explicit `width`, `height`, and `alt` attributes for all images.

---

### Requirement 5: Authentication Flow — Login Page Redesign

**User Story:** As a user, I want a polished, accessible login page that uses the Auth_Hook, so that I can sign in securely.

#### Acceptance Criteria

1. THE Frontend login page SHALL use the Auth_Hook's `login` method instead of calling `api()` directly.
2. WHEN the user submits valid credentials, THE Frontend SHALL store the Token and Refresh_Token via the Auth_Hook and redirect to `/{locale}/dashboard`.
3. WHEN the user submits invalid credentials, THE Frontend SHALL display a localised error message using the `auth.invalidCredentials` i18n key.
4. WHEN the login form is submitting, THE Frontend SHALL disable the submit button and show the Spinner.
5. THE Frontend login page SHALL be fully keyboard-navigable and meet WCAG 2.1 AA colour-contrast requirements.
6. WHERE the user's account has MFA enabled, THE Frontend SHALL display a TOTP code input step after successful password validation.

---

### Requirement 6: Authentication Flow — Token Refresh

**User Story:** As a logged-in user, I want my session to be silently renewed before the access token expires, so that I am not unexpectedly logged out mid-session.

#### Acceptance Criteria

1. THE API_Client SHALL intercept HTTP 401 responses and attempt a token refresh using the stored Refresh_Token before retrying the original request.
2. WHEN the refresh succeeds, THE API_Client SHALL store the new Token and Refresh_Token and retry the original request transparently.
3. WHEN the refresh fails (expired or missing Refresh_Token), THE API_Client SHALL clear stored tokens and redirect the user to `/{locale}/login`.
4. THE API_Client SHALL queue concurrent requests that arrive during a refresh and replay them after the refresh completes, rather than triggering multiple simultaneous refresh calls.
5. WHEN the Token is within 60 seconds of expiry, THE Auth_Hook SHALL proactively call the refresh endpoint before the next API request.

---

### Requirement 7: Authentication Flow — Protected Route Middleware

**User Story:** As a security engineer, I want all non-public routes to require a valid Token, so that unauthenticated users cannot access clinical data.

#### Acceptance Criteria

1. THE Middleware SHALL read the `token` cookie and redirect unauthenticated requests to `/{locale}/login`.
2. WHEN a valid Token is present, THE Middleware SHALL allow the request to proceed to the requested Protected_Route.
3. THE Middleware SHALL treat `/login`, `/register`, `/_next`, `/api`, `/favicon.ico`, and `/health` as public paths exempt from authentication checks.
4. WHEN a Token is present but the user's Role is insufficient for the requested route, THE Middleware SHALL redirect to a `/{locale}/forbidden` page.
5. THE Middleware SHALL preserve the original URL as a `?next=` query parameter on the login redirect so the user is returned there after authentication.

---

### Requirement 8: Backend–Frontend Wiring — Typed API Client

**User Story:** As a frontend developer, I want a typed API client that automatically attaches auth headers and handles errors consistently, so that I don't repeat boilerplate in every page component.

#### Acceptance Criteria

1. THE API_Client SHALL export typed wrapper functions for every Backend route group: `authApi`, `patientsApi`, `clinicalApi`, `aiApi`, `filesApi`, `surveillanceApi`, `notificationsApi`, `gdprApi`.
2. THE API_Client SHALL automatically attach the `Authorization: Bearer <token>` header to every authenticated request using the Token from the Auth_Hook context.
3. WHEN the Backend returns a non-2xx response, THE API_Client SHALL throw a typed `ApiError` with `status`, `code`, and `message` fields.
4. THE API_Client SHALL support request cancellation via `AbortController` for all GET requests.
5. THE API_Client SHALL include a WebSocket factory function `createChatSocket(token)` that returns a typed WebSocket connection for the `/ws/chat` endpoint.

---

### Requirement 9: Backend–Frontend Wiring — Loading States and Error Handling

**User Story:** As a user, I want clear feedback when data is loading or an error occurs, so that I understand the state of the application.

#### Acceptance Criteria

1. WHEN an API request is in flight, THE Frontend SHALL display the Spinner or a skeleton Loading_State in the relevant UI region.
2. WHEN an API request fails, THE Frontend SHALL display a localised error toast or inline error message using the `common.error` i18n key.
3. THE Frontend SHALL wrap each page in an Error_Boundary that catches unhandled render errors and displays a fallback UI with a "Reload" button.
4. WHEN a network error occurs (no response), THE Frontend SHALL display a `common.networkError` message and offer a retry button.
5. THE Frontend patients page SHALL display a Loading_State skeleton while the patient list is fetching and an empty-state message when the list is empty.

---

### Requirement 10: Backend–Frontend Wiring — Dashboard and Navigation

**User Story:** As a clinician, I want a functional dashboard with working navigation links, so that I can reach all platform sections quickly.

#### Acceptance Criteria

1. THE Frontend dashboard page SHALL use the Shell layout component with the sidebar navigation wired to all available routes: patients, chat, surveillance, notifications, settings.
2. THE Frontend dashboard page SHALL display the authenticated user's full name and Role Badge in the header.
3. WHEN the user clicks "Logout" in the header, THE Frontend SHALL call the Auth_Hook's `logout` method and redirect to `/{locale}/login`.
4. THE Frontend SHALL use Next.js `<Link>` components for all internal navigation instead of raw `<a>` tags.
5. THE Frontend SHALL display a notification badge count in the sidebar navigation item when unread notifications exist.

---

### Requirement 11: Database Migration Strategy

**User Story:** As a backend developer, I want a versioned migration system for MongoDB, so that schema changes are applied consistently across all environments.

#### Acceptance Criteria

1. THE Migration_Runner SHALL store each migration as a numbered Python script in `backend/migrations/` (e.g., `0001_initial_indexes.py`, `0002_add_audit_ttl.py`).
2. THE Migration_Runner SHALL record applied migrations in a `_migrations` MongoDB collection with fields `version`, `name`, `applied_at`.
3. WHEN the Migration_Runner is invoked, THE Migration_Runner SHALL apply only migrations whose `version` is not present in the `_migrations` collection, in ascending version order.
4. IF a migration script raises an exception, THEN THE Migration_Runner SHALL halt execution, log the error, and leave the `_migrations` collection unchanged for that version.
5. THE Migration_Runner SHALL be invokable as a standalone CLI command: `python -m backend.migrations.runner`.
6. THE Migration_Runner SHALL be invoked automatically during the Backend lifespan startup after index creation.
7. THE Migration_Runner SHALL include a migration `0001` that creates all indexes currently defined inline in `main.py` and a migration `0002` that adds a TTL index on `audit_logs.timestamp` (90-day expiry).

---

### Requirement 12: Test Coverage — Backend

**User Story:** As a developer, I want comprehensive backend tests, so that regressions are caught before deployment.

#### Acceptance Criteria

1. THE Backend test suite SHALL cover all auth endpoints: register, login (valid), login (invalid credentials), login (inactive account), refresh (valid), refresh (expired), logout, MFA setup, MFA verify (valid code), MFA verify (invalid code).
2. THE Backend test suite SHALL cover patient CRUD: create, list (with search query), get by ID (found), get by ID (not found), update, delete (admin only), delete (nurse forbidden).
3. THE Backend test suite SHALL cover role-based access: each Role's access to `/patients`, `/clinical`, `/ai/differential`, `/surveillance`, `/gdpr`.
4. THE Backend test suite SHALL cover the AI endpoints: query (high confidence), query (low confidence warning), differential (doctor allowed), differential (patient forbidden), literature search.
5. THE Backend test suite SHALL achieve a minimum line coverage of 80% across `app/api/routes/` and `app/services/`.
6. WHEN `pytest` is run from the `backend/` directory, THE Backend test suite SHALL pass with zero failures.

---

### Requirement 13: Test Coverage — Frontend

**User Story:** As a developer, I want frontend component and integration tests, so that UI regressions are caught before deployment.

#### Acceptance Criteria

1. THE Frontend test suite SHALL use Vitest and React Testing Library.
2. THE Frontend test suite SHALL include unit tests for the `Button`, `Input`, `Card`, and `Table` components covering rendering, props, and accessibility attributes.
3. THE Frontend test suite SHALL include an integration test for the login flow: successful login redirects to dashboard, failed login shows error message, MFA step renders when required.
4. THE Frontend test suite SHALL include a test for the API_Client's token-refresh interceptor: verifies that a 401 response triggers a refresh and retries the original request.
5. THE Frontend test suite SHALL include a test for the Middleware: verifies that unauthenticated requests to Protected_Routes are redirected to `/login`.
6. WHEN `vitest --run` is executed from the `frontend/` directory, THE Frontend test suite SHALL pass with zero failures.

---

### Requirement 14: Documentation — README

**User Story:** As a new contributor, I want a comprehensive README, so that I can set up and run the project locally without asking for help.

#### Acceptance Criteria

1. THE App README at the repository root SHALL include: project overview, architecture diagram (ASCII or Mermaid), prerequisites, local setup steps (Docker Compose), environment variable reference, and links to further docs.
2. THE App README SHALL include a "Running Tests" section with exact commands for both backend (`pytest`) and frontend (`vitest --run`) test suites.
3. THE App README SHALL include a "Database Migrations" section explaining how to run the Migration_Runner.
4. WHEN a developer follows the README setup steps on a clean machine with Docker installed, THE App SHALL start successfully with `docker compose up`.

---

### Requirement 15: Documentation — API Reference

**User Story:** As a frontend developer or API consumer, I want auto-generated API documentation, so that I can explore and test endpoints without reading source code.

#### Acceptance Criteria

1. THE Backend SHALL expose a Swagger UI at `/docs` and a ReDoc UI at `/redoc` via FastAPI's built-in OpenAPI support.
2. THE Backend SHALL include `summary`, `description`, and `response_model` annotations on every router endpoint.
3. THE Backend SHALL include an `openapi.json` export script that writes the schema to `docs/api/openapi.json`.
4. WHEN the Backend is running, THE Backend SHALL serve the OpenAPI schema at `/openapi.json`.

---

### Requirement 16: Documentation — Architecture Document

**User Story:** As a technical lead, I want an architecture document, so that I can understand the system's components and their interactions.

#### Acceptance Criteria

1. THE App SHALL include a `docs/architecture.md` file describing: system components (Frontend, Backend, MongoDB, Redis, S3/LocalStack, AI mock), data flow for a typical clinical encounter, authentication sequence (login → token → refresh → logout), and WebSocket chat flow.
2. THE `docs/architecture.md` SHALL include a Mermaid sequence diagram for the authentication flow.
3. THE `docs/architecture.md` SHALL include a Mermaid component diagram showing the service dependencies.
4. THE App SHALL include a `docs/deployment.md` file describing the Docker Compose setup, environment variables, and production deployment considerations.

---

### Requirement 17: Local Development Environment

**User Story:** As a new contributor, I want to start the entire application stack with a single command, so that I can run and develop the app locally without manual configuration.

#### Acceptance Criteria

1. WHEN a developer runs `docker compose up` from the `docker/` directory (or from the repo root via `start.sh` / `start.bat`), THE App SHALL start all services — Backend, Frontend, MongoDB, Redis, LocalStack, and AI mock — without requiring any manual configuration steps beyond copying `.env.example`.
2. THE App SHALL provide a `docker/.env` file (bootstrapped from `backend/.env.example` with Docker-internal service names) so that `docker compose up` works out of the box on a clean clone; the `.env.example` SHALL document every variable with a safe default value.
3. WHEN all services are running, THE Frontend SHALL be reachable at `http://localhost:3000` and THE Backend SHALL be reachable at `http://localhost:8000`.
4. WHILE running inside the Docker network, THE Backend SHALL resolve MongoDB at `mongodb:27017`, Redis at `redis:6379`, LocalStack at `localstack:4566`, and the AI mock at `ai-mock:8080` using Docker service names.
5. THE Frontend Docker service SHALL set `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1` for client-side browser requests and SHALL set `API_URL=http://backend:8000/api/v1` for server-side Next.js requests, so that both rendering contexts resolve the Backend correctly.
6. THE Frontend Docker service SHALL set `NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws` so that WebSocket connections from the browser resolve correctly.
7. WHEN the Backend container starts for the first time (i.e., the `_migrations` collection is empty), THE Backend SHALL automatically run `python -m app.scripts.seed` to create a default admin user, making the app immediately usable without manual database setup.
8. WHILE running in development mode, THE Backend container SHALL start uvicorn with `--reload` so that Python source changes are reflected without restarting the container.
9. WHILE running in development mode, THE Frontend container SHALL start with `next dev` so that TypeScript/CSS source changes trigger hot-module replacement without restarting the container.
10. THE `start.sh` script at the repo root SHALL change into the `docker/` directory and invoke `docker compose --env-file .env up` so that developers can start the stack from the repo root on Unix/macOS.
11. THE `start.bat` script at the repo root SHALL change into the `docker/` directory and invoke `docker compose --env-file .env up` so that developers can start the stack from the repo root on Windows.
12. IF any required environment variable is missing from the Docker environment at Backend startup, THEN THE Backend SHALL log a descriptive error message identifying the missing variable and exit with a non-zero status code.
