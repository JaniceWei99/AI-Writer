"""Middleware for request/response logging."""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            logger.error("%s %s -> 500 (%.0fms) %s", method, path, elapsed, exc)
            raise

        elapsed = (time.perf_counter() - start) * 1000
        status = response.status_code

        if status >= 500:
            logger.error("%s %s -> %d (%.0fms)", method, path, status, elapsed)
        elif status >= 400:
            logger.warning("%s %s -> %d (%.0fms)", method, path, status, elapsed)
        else:
            logger.info("%s %s -> %d (%.0fms)", method, path, status, elapsed)

        return response
