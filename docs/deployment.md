# Deployment

## Local Development (Docker Compose)

### Prerequisites

- Docker ≥ 24 with Compose v2
- Git

### Setup

1. Copy the environment file:
   ```bash
   cp backend/.env.example docker/.env
   ```

2. Start all services from the repo root:

   **Unix / macOS:**
   ```bash
   ./start.sh
   ```

   **Windows:**
   ```bat
   start.bat
   ```

   Or directly:
   ```bash
   cd docker && docker compose --env-file .env up
   ```

3. To stop:
   ```bash
   ./stop.sh   # Unix/macOS
   stop.bat    # Windows
   ```

### Services

| Service | Port | Description |
|---|---|---|
| `frontend` | 3000 | Next.js dev server with HMR |
| `backend` | 8000 | FastAPI with uvicorn `--reload` |
| `mongodb` | 27017 | MongoDB 7 |
| `redis` | 6379 | Redis 7 |
| `localstack` | 4566 | AWS S3/SQS/SNS emulation |
| `ai-mock` | 8080 | AI inference mock service |

### First Boot

On first startup the backend:
1. Runs all pending database migrations
2. Detects an empty `_migrations` collection and seeds a default admin user via `python -m app.scripts.seed`

No manual database setup is required.

### Hot Reload

- Backend: Python source changes in `backend/` are reflected immediately (uvicorn `--reload` + volume mount)
- Frontend: TypeScript/CSS changes trigger hot-module replacement (Next.js dev mode + volume mount)

---

## Environment Variables

All variables are defined in `docker/.env` (bootstrapped from `backend/.env.example`).

### Backend

| Variable | Required | Default | Description |
|---|---|---|---|
| `MONGODB_URI` | yes | `mongodb://mongodb:27017/tropmed` | MongoDB connection string |
| `REDIS_URL` | yes | `redis://redis:6379` | Redis connection string |
| `JWT_SECRET` | yes | `dev-secret-change-in-prod` | JWT signing secret — **must be changed in production** |
| `AWS_S3_BUCKET` | yes | `tropmed-files-local` | S3 bucket for file uploads |
| `AWS_REGION` | yes | `us-east-1` | AWS region |
| `AWS_ENDPOINT_URL` | no | `http://localstack:4566` | Override for LocalStack; omit in production |
| `AWS_ACCESS_KEY_ID` | yes | `test` | AWS access key (use real credentials in production) |
| `AWS_SECRET_ACCESS_KEY` | yes | `test` | AWS secret key (use real credentials in production) |
| `AI_INFERENCE_URL` | yes | `http://ai-mock:8080` | AI inference service endpoint |
| `APP_LOCALE` | no | `fr` | Default locale (`fr` or `en`) |

### Frontend

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | yes | API base URL for client-side browser requests (e.g. `http://localhost:8000/api/v1`) |
| `API_URL` | yes | API base URL for server-side Next.js requests (e.g. `http://backend:8000/api/v1` inside Docker) |
| `NEXT_PUBLIC_WS_URL` | yes | WebSocket base URL for browser connections (e.g. `ws://localhost:8000/ws`) |

If any required backend variable is missing at startup, the application logs a descriptive error identifying the missing variable and exits with a non-zero status code.

---

## Production Deployment

### Security Checklist

- [ ] Set `JWT_SECRET` to a cryptographically random value (≥ 32 bytes): `openssl rand -hex 32`
- [ ] Replace LocalStack with real AWS credentials and remove `AWS_ENDPOINT_URL`
- [ ] Use a managed MongoDB service (Atlas, DocumentDB) and update `MONGODB_URI` with authentication
- [ ] Use a managed Redis service (ElastiCache, Upstash) and update `REDIS_URL`
- [ ] Enable TLS on all service endpoints
- [ ] Set `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_WS_URL` to your production domain
- [ ] Remove the `ai-mock` service and point `AI_INFERENCE_URL` at your real AI inference endpoint
- [ ] Restrict CORS origins in `backend/app/main.py` to your production frontend domain

### Building Production Images

```bash
# Backend
docker build -t tropmed-backend:latest ./backend

# Frontend
docker build -t tropmed-frontend:latest ./frontend
```

The frontend Dockerfile runs `next build` and serves the output with `next start`. The backend Dockerfile runs uvicorn without `--reload`.

### Scaling Considerations

- The backend is stateless (tokens validated via JWT signature, sessions in Redis) — scale horizontally behind a load balancer
- MongoDB should be deployed as a replica set for high availability
- Redis is used for rate limiting and WebSocket pub/sub — use Redis Cluster or a managed service for production scale
- File uploads go directly to S3 — no backend storage state to manage
- WebSocket connections are sticky per-user; use a load balancer with session affinity or route all WebSocket traffic to a dedicated service

### Database Migrations in Production

Run migrations before deploying a new backend version:

```bash
docker run --rm \
  -e MONGODB_URI=<production-uri> \
  tropmed-backend:latest \
  python -m backend.migrations.runner
```

Migrations are idempotent — safe to run multiple times. The runner halts on the first failure and leaves the database unchanged for that version, so a failed migration does not corrupt previously-applied state.

### Health Checks

- Backend: `GET /health` — returns `{ "status": "ok" }` when the service is ready
- MongoDB: Docker healthcheck via `mongosh --eval "db.runCommand({ping:1}).ok"`

Use these endpoints in your load balancer and orchestration platform (ECS, Kubernetes) health check configuration.
