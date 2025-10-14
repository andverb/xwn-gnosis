from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.admin import create_admin
from app.config import settings
from app.db import engine
from app.routers.api import rules as api_rules
from app.routers.api import rulesets as api_rulesets
from app.routers.api import search as api_search
from app.routers.web import pages
from app.routers.web import search as web_search

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
    yield
    # Shutdown: properly dispose of database engine and close all connections
    await engine.dispose()


app = FastAPI(
    title="Gnosis - database of rules for xWN family of TRPG systems",
    version="0.1.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    # Don't cache admin interface or API write endpoints
    if request.method == "GET" and not request.url.path.startswith("/admin"):
        # Cache for 10 minutes
        response.headers["Cache-Control"] = "public, max-age=600"
    return response


# API routers (JSON responses)
app.include_router(api_rules.router)
app.include_router(api_rulesets.router)
app.include_router(api_search.router)

# Web routers (HTML responses)
app.include_router(pages.router)
app.include_router(web_search.router)

create_admin(app)
