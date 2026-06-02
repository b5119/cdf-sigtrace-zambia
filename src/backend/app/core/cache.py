"""Simple Redis response cache for public read endpoints (INC-005 hardening).

Usage in a router:
    from app.core.cache import cache_response, invalidate

    @router.get("/public/overview")
    @cache_response(ttl=120)
    async def overview(request: Request): ...

The decorator stores the JSON-serialised response in Redis under a key derived
from the full request URL. The TTL is configurable per endpoint.

Falls back gracefully when Redis is unavailable — the endpoint runs normally,
the result just isn't cached.
"""
import json
import logging
from functools import wraps
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

log = logging.getLogger(__name__)

# Lazy Redis client — imported at first use so tests without Redis don't fail at import time
_redis = None


def _get_redis():
    global _redis
    if _redis is None:
        try:
            import redis.asyncio as aioredis
            from app.core.config import settings
            _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1)
        except Exception as e:
            log.warning("Redis unavailable for caching: %s", e)
    return _redis


def cache_response(ttl: int = 60, key_prefix: str = "cache"):
    """Decorator that caches a route handler's JSONResponse in Redis."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            redis = _get_redis()
            cache_key = f"{key_prefix}:{request.url}"

            if redis:
                try:
                    cached = await redis.get(cache_key)
                    if cached:
                        return JSONResponse(content=json.loads(cached))
                except Exception as e:
                    log.warning("Cache read error: %s", e)

            response = await func(request, *args, **kwargs)

            if redis and isinstance(response, (dict, JSONResponse)):
                try:
                    data = response.body if isinstance(response, JSONResponse) else json.dumps(response)
                    if isinstance(data, bytes):
                        data = data.decode()
                    await redis.setex(cache_key, ttl, data)
                except Exception as e:
                    log.warning("Cache write error: %s", e)

            return response
        return wrapper
    return decorator


async def invalidate_pattern(pattern: str) -> int:
    """Delete all Redis cache keys matching a pattern. Returns count deleted."""
    redis = _get_redis()
    if not redis:
        return 0
    try:
        keys = await redis.keys(pattern)
        if keys:
            return await redis.delete(*keys)
    except Exception as e:
        log.warning("Cache invalidation error: %s", e)
    return 0
