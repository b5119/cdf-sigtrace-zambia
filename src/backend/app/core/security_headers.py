"""Security headers middleware (INC-019).

Adds defence-in-depth HTTP security headers to every response:
- HSTS (force HTTPS), CSP (no inline scripts), X-Frame-Options (no clickjacking),
  X-Content-Type-Options (no MIME sniffing), Referrer-Policy, Permissions-Policy.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(self), camera=(self), microphone=()"
        # CSP — API serves JSON; the SPAs set their own CSP. This is a safe default.
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        )
        return response
