"""
GST Billing Application — FastAPI entry point.

This module creates and configures the FastAPI application,
including CORS, static files, templates, exception handlers,
and API route registration.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import get_settings
from app.utils.exceptions import AppException
from app.utils.responses import error_response
from app.routes import pages

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
# Resolve project root (two levels up from this file: app/main.py -> backend/ -> HawlMark/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
TEMPLATES_DIR = FRONTEND_DIR / "templates"

# Ensure directories exist so the app can start even before frontend files land
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle known application exceptions with structured JSON responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=exc.error_code,
            message=exc.message,
            details=exc.details,
        ),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions."""
    import logging, traceback
    logging.error("Unhandled exception on %s %s:\n%s", request.method, request.url, traceback.format_exc())
    details = {"error": str(exc), "trace": traceback.format_exc()} if settings.DEBUG else {}
    return JSONResponse(
        status_code=500,
        content=error_response(
            code="INTERNAL_SERVER_ERROR",
            message=str(exc) if settings.DEBUG else "An unexpected error occurred.",
            details=details,
        ),
    )

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["health"])
async def health_check() -> dict:
    """Liveness / readiness probe."""
    return {"status": "healthy", "version": "1.0.0"}

# ---------------------------------------------------------------------------
# Page routes (HTML templates served by Jinja2)
# ---------------------------------------------------------------------------
app.include_router(pages.router)

# ---------------------------------------------------------------------------
# API routers (will be registered as phases are implemented)
# ---------------------------------------------------------------------------
from app.routes import auth, business, customers, products, gst, invoices, dashboard, audit_logs, users
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(business.router, prefix="/api", tags=["business"])
app.include_router(customers.router, prefix="/api", tags=["customers"])
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(invoices.router, prefix="/api", tags=["invoices"])
app.include_router(gst.router, prefix="/api", tags=["gst"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(audit_logs.router, prefix="/api", tags=["audit-logs"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
