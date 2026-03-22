"""Simple in-memory IP-based rate limiter middleware."""

import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("app.ratelimit")

# Only rate-limit the heavy AI endpoints
RATE_LIMITED_PATHS = {"/api/writing/process", "/api/writing/stream"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter per client IP.

    Args:
        app: ASGI application
        max_requests: maximum requests per window (default 10)
        window_seconds: window size in seconds (default 60)
    """

    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        # ip -> list of timestamps
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _cleanup(self, ip: str, now: float):
        cutoff = now - self.window
        timestamps = self._hits[ip]
        self._hits[ip] = [t for t in timestamps if t > cutoff]

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS" or request.url.path not in RATE_LIMITED_PATHS:
            return await call_next(request)

        ip = self._client_ip(request)
        now = time.time()
        self._cleanup(ip, now)

        if len(self._hits[ip]) >= self.max_requests:
            logger.warning("Rate limit exceeded for %s on %s", ip, request.url.path)
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"},
            )

        self._hits[ip].append(now)
        return await call_next(request)
