import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.admin import create_admin
from app.config import settings
from app.db import engine
from app.logging_config import add_request_context, clear_request_context, get_logger, setup_logging
from app.routers.api import rules as api_rules
from app.routers.api import rulesets as api_rulesets
from app.routers.api import search as api_search
from app.routers.web import pages
from app.routers.web import search as web_search

# Initialize structured logging
setup_logging(log_level=settings.log_level, json_logs=settings.log_json)
logger = get_logger(__name__)

tags_metadata = [
    {
        "name": "rules-api",
        "description": "API: Operations with rules. Individual game mechanics and content.",
    },
    {
        "name": "rulesets-api",
        "description": "API: Operations with rulesets. Collections of rules for different game systems.",
    },
    {
        "name": "search-api",
        "description": "API: Search rules and rulesets.",
    },
    {
        "name": "search-web",
        "description": "Web: Search interface (HTML)",
    },
    {
        "name": "pages",
        "description": "Web: Frontend pages (HTML)",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan: startup and shutdown events."""
    # Startup: resources are already initialized at module import
    logger.info(
        "application_startup",
        environment=settings.environment,
        log_level=settings.log_level,
        database_configured=bool(settings.database_url),
    )
    yield
    # Shutdown: properly dispose of database engine and close all connections
    logger.info("application_shutdown", message="Closing database connections")
    await engine.dispose()
    logger.info("application_shutdown_complete")


app = FastAPI(
    title="Gnosis - database of rules for xWN family of TRPG systems",
    version="0.1.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Force HTTPS scheme in production (for admin static files)
@app.middleware("http")
async def force_https_scheme(request: Request, call_next):
    # In production, trust proxy headers to set correct scheme
    if settings.environment != "development":
        if request.headers.get("x-forwarded-proto") == "https":
            request.scope["scheme"] = "https"
    return await call_next(request)


@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    # Don't cache admin interface or API write endpoints
    if request.method == "GET" and not request.url.path.startswith("/admin"):
        # Cache for 10 minutes, but vary by Cookie so different languages are cached separately
        response.headers["Cache-Control"] = "public, max-age=600"
        response.headers["Vary"] = "Cookie"
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing and request ID tracking."""
    # Generate unique request ID
    request_id = str(uuid.uuid4())

    # Add request context for all logs in this request
    add_request_context(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_host=request.client.host if request.client else None,
    )

    # Log request start
    start_time = time.time()
    logger.info("request_started", url=str(request.url))

    try:
        # Process request
        response = await call_next(request)

        # Calculate request duration
        duration_ms = (time.time() - start_time) * 1000

        # Log request completion
        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        # Add request ID to response headers for tracing
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception as e:
        # Log request failure
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "request_failed",
            error=str(e),
            error_type=type(e).__name__,
            duration_ms=round(duration_ms, 2),
            exc_info=True,
        )
        raise

    finally:
        # Clear request context
        clear_request_context()


# API routers (JSON responses)
app.include_router(api_rules.router)
app.include_router(api_rulesets.router)
app.include_router(api_search.router)

# Web routers (HTML responses)
app.include_router(pages.router)
app.include_router(web_search.router)

# Mount MkDocs static sites for rulesets
# site-uk and site-en now contain clean paths (basics/, combat/, etc.)
# because we set docs_dir to point directly to language-specific folders (docs/wwn-lite/uk, docs/wwn-lite/en)
# This follows MkDocs best practices for multilingual sites
SITE_UK_DIR = Path(__file__).parent.parent / "site-uk"
SITE_EN_DIR = Path(__file__).parent.parent / "site-en"

if SITE_UK_DIR.exists():
    app.mount("/rulesets/wwn-lite/uk", StaticFiles(directory=str(SITE_UK_DIR), html=True), name="rulesets-uk")

if SITE_EN_DIR.exists():
    app.mount("/rulesets/wwn-lite/en", StaticFiles(directory=str(SITE_EN_DIR), html=True), name="rulesets-en")

create_admin(app)
