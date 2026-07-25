"""Rate limiting middleware and dependency for FastAPI."""

import time
from collections import defaultdict
from typing import Dict, List

from fastapi import Request, HTTPException, status


class RateLimiter:
    """Simple in-memory sliding-window rate limiter."""

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._store: Dict[str, List[float]] = defaultdict(list)

    def _clean(self, key: str, now: float) -> None:
        cutoff = now - self.window_seconds
        self._store[key] = [t for t in self._store[key] if t > cutoff]

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self._clean(key, now)
        if len(self._store[key]) >= self.max_requests:
            return False
        self._store[key].append(now)
        return True


# Default: 30 requests per 60 seconds for AI endpoints
ai_limiter = RateLimiter(max_requests=30, window_seconds=60)
# General: 100 requests per 60 seconds
general_limiter = RateLimiter(max_requests=100, window_seconds=60)


async def rate_limit_middleware(request: Request, call_next):
    """Apply general rate limiting to all requests."""
    client_ip = request.client.host if request.client else "unknown"
    if not general_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后再试",
        )
    response = await call_next(request)
    return response


async def ai_rate_limit(request: Request) -> None:
    """Dependency: rate-limit AI-heavy endpoints per client IP."""
    client_ip = request.client.host if request.client else "unknown"
    if not ai_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI 请求过于频繁，请稍后再试",
        )
