import time
import uuid
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import logger
from app.core.database import Base, engine
import app.models  # ensure all models are imported
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.reports import router as reports_router
from app.api.v1.audit import router as audit_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensures production database schema matches Alembic migration state safely."""
    try:
        from app.core.migration import run_safe_migration
        run_safe_migration()
    except Exception as e:
        logger.error(f"Safe migration verification on startup encountered an error: {e}", exc_info=True)
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="MMI AI Analytics — Intelligent ERP Analytics & Reporting",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS Middleware (Section 26 & 37)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Observability Middleware (Section 36)
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()

    response = await call_next(request)
    
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-MS"] = str(duration_ms)

    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} in {duration_ms}ms",
        extra={"request_id": request_id, "execution_time_ms": duration_ms}
    )
    return response

# Safe Global Exception Handler (Section 25)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    headers = {}
    origin = request.headers.get("origin")
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Access-Control-Allow-Methods"] = "*"
        headers["Access-Control-Allow-Headers"] = "*"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing the request.",
            "request_id": getattr(request.state, "request_id", None),
        },
        headers=headers,
    )

# Routers
app.include_router(health_router, prefix="/api")
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")

@app.get("/health", tags=["Liveness"])
def liveness():
    """Lightweight liveness probe for container orchestrators (returns 200 immediately without database queries)."""
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs",
        "health": "/health",
    }
