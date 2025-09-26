from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.admin import admin
from app.routers import misc, rules, rulesets


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    await admin.initialize()
    yield


tags_metadata = [
    {
        "name": "rules",
        "description": "Operations with rules. Individual game mechanics and content.",
    },
    {
        "name": "rulesets",
        "description": "Operations with rulesets. Collections of rules for different game systems.",
    },
]


app = FastAPI(
    title="Gnosis - database of rules for xWN family of TRPG systems",
    lifespan=lifespan,
    version="0.1.0",
    openapi_tags=tags_metadata,
)
app.include_router(rules.router)
app.include_router(rulesets.router)
app.include_router(misc.router)

app.mount("/admin", admin.app)
