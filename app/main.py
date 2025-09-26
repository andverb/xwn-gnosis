from fastapi import FastAPI

from app.routers import rules, rulesets

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
    title="Gnosis - database of rules for xWN family of TRPG systems", version="0.1.0", openapi_tags=tags_metadata
)
app.include_router(rules.router)
app.include_router(rulesets.router)


@app.get("/")
async def health_check():
    return {"message": "Im OK!"}
