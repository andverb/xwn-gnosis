from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import String, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/search", tags=["search"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/rules", response_model=list[schemas.RuleSearchResult])
async def search_rules(
    q: str = Query(..., min_length=2, description="Search query"),
    ruleset: str | None = Query(None, description="Filter by ruleset name"),
    limit: int = Query(20, le=100, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    search_term = f"%{q.lower()}%"
    stmt = (
        select(models.Rule)
        .options(selectinload(models.Rule.ruleset))
        .join(models.RuleSet)
        .where(
            or_(
                models.Rule.translations["en"]["name"].astext.ilike(search_term),
                models.Rule.tags.cast(String).ilike(search_term),
            )
        )
    )

    # Add ruleset filter if provided
    if ruleset:
        stmt = stmt.where(models.RuleSet.name.ilike(f"%{ruleset}%"))
    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    rules = result.scalars().all()

    rules_populated = []
    for rule in rules:
        # Extract English content or fallback
        en_content = rule.translations.get("en", {})

        rules_populated.append(
            schemas.RuleSearchResult(
                id=rule.id,
                slug=rule.slug,
                ruleset_id=rule.ruleset_id,
                ruleset_name=rule.ruleset.name,
                rule_name=en_content.get("name", f"Rule {rule.id}"),
                rule_description=en_content.get("description", ""),
                tags=rule.tags,
                changes_description=rule.changes_description,
                is_official=rule.is_official,
                created_at=rule.created_at,
                updated_at=rule.updated_at,
                created_by=rule.created_by,
                last_update_by=rule.last_update_by,
            )
        )
    return rules_populated


@router.get("/rules/html", response_class=HTMLResponse, include_in_schema=False)
async def search_rules_html(
    request: Request,
    q: str = Query("", description="Search query"),
    ruleset: str | None = Query(None, description="Filter by ruleset name"),
    limit: int = Query(20, le=100, description="Max results"),
    db: AsyncSession = Depends(get_db),
):
    if not q or len(q) < 2:  # noqa
        return templates.TemplateResponse("search_results.html", {"request": request, "results": [], "query": q})

    # Reuse the same search logic
    search_term = f"%{q.lower()}%"
    stmt = (
        select(models.Rule)
        .options(selectinload(models.Rule.ruleset))
        .join(models.RuleSet)
        .where(
            or_(
                models.Rule.translations["en"]["name"].astext.ilike(search_term),
                models.Rule.tags.cast(String).ilike(search_term),
            )
        )
    )

    if ruleset:
        stmt = stmt.where(models.RuleSet.name.ilike(f"%{ruleset}%"))

    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    rules = result.scalars().all()

    # Convert to simple dict for template
    results = []
    for rule in rules:
        en_content = rule.translations.get("en", {})
        results.append(
            {
                "id": rule.id,
                "rule_name": en_content.get("name", f"Rule {rule.id}"),
                "rule_description": en_content.get("description", ""),
                "ruleset_name": rule.ruleset.name,
                "tags": rule.tags or [],
                "is_official": rule.is_official,
            }
        )

    return templates.TemplateResponse("search_results.html", {"request": request, "results": results, "query": q})
