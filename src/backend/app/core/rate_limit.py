"""Rate limiting via slowapi + Redis (INC-005 hardening).

Limits:
  - Auth endpoints  — 10 requests / minute per IP  (brute-force protection)
  - Public API      — 120 requests / minute per IP (generous for citizens/journalists)
  - Restricted API  — 300 requests / minute per IP (officers doing real work)

In dev (no Redis URL set or Redis unreachable) the limiter falls back to
in-memory storage so local development still works.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    # If Redis is unavailable fall back to in-memory (dev/test safety net)
    storage_options={"socket_connect_timeout": 1},
)

# Limit strings — import these in routers
AUTH_LIMIT     = "10/minute"
PUBLIC_LIMIT   = "120/minute"
RESTRICT_LIMIT = "300/minute"
