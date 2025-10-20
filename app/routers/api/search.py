from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app import models, schemas
from app.dependencies import DbSession
from app.search_service import build_fuzzy_search_query

router = APIRouter(prefix="/api/search", tags=["search-api"])


@router.get("/rules", response_model=list[schemas.RuleSearchResult])
async def search_rules(
    db: DbSession,
    q: str = Query(..., min_length=2, description="Search query"),
    ruleset: str | None = Query(None, description="Filter by ruleset name"),
    limit: int = Query(20, le=100, description="Max results"),
    min_similarity: float = Query(0.1, ge=0.0, le=1.0, description="Minimum similarity threshold (0.0-1.0)"),
):
    """
    Search rules using fuzzy matching with PostgreSQL trigram similarity.

    Searches both names and descriptions in English and Ukrainian.
    For multi-word queries (e.g., "vowed arts"), searches each word and sums scores.
    Returns results ordered by relevance score (best matches first).
    """
    # Build fuzzy search conditions using the search service
    similarity_score, where_condition = build_fuzzy_search_query(q, min_similarity)

    # Construct the main query
    stmt = (
        select(models.Rule, similarity_score)
        .options(selectinload(models.Rule.ruleset))
        .join(models.RuleSet)
        .where(where_condition)
    )

    # Add ruleset filter if provided
    if ruleset:
        stmt = stmt.where(models.RuleSet.name.ilike(f"%{ruleset}%"))

    # Order by similarity score (best matches first) and limit results
    stmt = stmt.order_by(similarity_score.desc()).limit(limit)

    result = await db.execute(stmt)
    rows = result.all()

    # Process results and extract rule objects with their similarity scores
    rules_populated = []
    for rule, similarity_score in rows:
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
