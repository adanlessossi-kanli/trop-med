import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis
from app.core.config import get_settings

ROLE_LIMITS = {
    "patient": 60,
    "nurse": 300,
    "doctor": 300,
    "researcher": 300,
    "admin": 600,
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._redis: aioredis.Redis | None = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = aioredis.from_url(get_settings().redis_url)
        return self._redis

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health and auth endpoints
        if request.url.path in ("/health", "/api/v1/auth/login", "/api/v1/auth/register"):
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return await call_next(request)

        try:
            from app.core.security import decode_token
            token = auth_header.split(" ", 1)[1]
            payload = decode_token(token, get_settings())
            role = payload.get("role", "patient")
            user_id = payload.get("sub", "anon")
        except Exception:
            return await call_next(request)

        limit = ROLE_LIMITS.get(role, 60)
        window = 60
        key = f"rate:{user_id}:{int(time.time()) // window}"

        try:
            r = await self._get_redis()
            count = await r.incr(key)
            if count == 1:
                await r.expire(key, window)
            if count > limit:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
        except HTTPException:
            raise
        except Exception:
            pass  # If Redis is down, allow the request through

        return await call_next(request)
