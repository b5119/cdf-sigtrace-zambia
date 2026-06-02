"""CDF SigTrace — FastAPI application entry point."""
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.core.config import settings

log = structlog.get_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    # Lock down OpenAPI in production
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- System / health ---

@app.get("/healthz", tags=["system"])
async def liveness():
    return {"status": "ok"}


@app.get("/readyz", tags=["system"])
async def readiness():
    # TODO(INC-017): probe DB, Redis, Fabric, Polygon, IPFS
    return {"status": "ok"}


# --- Routers (INC-001) ---
app.include_router(auth_router, prefix="/api/v1")

# Later increments will mount additional routers here:
# app.include_router(public_router, prefix="/api/v1")
# app.include_router(contracts_router, prefix="/api/v1")
# etc.


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "Internal server error"}},
    )
