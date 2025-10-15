from fastapi import APIRouter, Query
from sqlalchemy import String, or_, select
from sqlalchemy.orm import selectinload

from app import models, schemas
from app.dependencies import DbSession

router = APIRouter(prefix="/api/search", tags=["search-api"])


@router.get("/rules", response_model=list[schemas.RuleSearchResult])
async def search_rules(
    db: DbSession,
    q: str = Query(..., min_length=2, description="Search query"),
    ruleset: str | None = Query(None, description="Filter by ruleset name"),
    limit: int = Query(20, le=100, description="Max results"),
):
    search_term = f"%{q.lower()}%"
    stmt = (
        select(models.Rule)
        .options(selectinload(models.Rule.ruleset))
        .join(models.RuleSet)
        .where(
            or_(
                models.Rule.name_en.ilike(search_term),
                models.Rule.tags.cast(String).ilike(search_term),
                models.Rule.type.ilike(search_term),
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
        rules_populated.append(
            schemas.RuleSearchResult(
                id=rule.id,
                type=rule.type,
                slug=rule.slug,
                ruleset_id=rule.ruleset_id,
                ruleset_name=rule.ruleset.name,
                rule_name=rule.name_en,
                rule_description=rule.description_en,
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
