from fastapi import FastAPI

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


app = FastAPI(
    title="Gnosis - database of rules for xWN family of TRPG systems",
    version="0.1.0",
    openapi_tags=tags_metadata,
)

# API routers (JSON responses)
app.include_router(api_rules.router)
app.include_router(api_rulesets.router)
app.include_router(api_search.router)

# Web routers (HTML responses)
app.include_router(pages.router)
app.include_router(web_search.router)
