"""CDF SigTrace — FastAPI application entry point."""
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.analysis import router as analysis_router
from app.api.anchors import router as anchors_router
from app.api.public import router as public_router
from app.api.pulse import router as pulse_router
from app.api.monitor import router as monitor_router
from app.api.auth import router as auth_router
from app.api.contracts import router as contracts_router
from app.api.ingestion import router as ingestion_router
from app.core.config import settings
from app.core.rate_limit import limiter

log = structlog.get_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Rate limiter state + middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

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


# --- Routers ---
app.include_router(auth_router, prefix="/api/v1")       # INC-001
app.include_router(ingestion_router, prefix="/api/v1")  # INC-002
app.include_router(contracts_router, prefix="/api/v1")  # INC-005
app.include_router(analysis_router, prefix="/api/v1")   # INC-005
app.include_router(anchors_router, prefix="/api/v1")    # INC-006
app.include_router(public_router, prefix="/api/v1")     # INC-007
app.include_router(pulse_router, prefix="/api/v1")      # INC-010
app.include_router(monitor_router, prefix="/api/v1")    # INC-015


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.error("unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "Internal server error"}},
    )
