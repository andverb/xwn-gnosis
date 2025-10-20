from fastapi import APIRouter, Cookie, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app import models
from app.dependencies import DbSession
from app.dependencies.i18n import get_language, get_translations
from app.search_service import build_fuzzy_search_query
from app.utils import render_markdown

router = APIRouter(prefix="/search", tags=["search-web"])
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["markdown"] = render_markdown


@router.get("/rules/html", response_class=HTMLResponse, include_in_schema=False)
async def search_rules_html(
    request: Request,
    db: DbSession,
    q: str = Query("", description="Search query"),
    rule_type: str | None = Query(None, alias="type", description="Filter by rule type"),
    ruleset: str | None = Query(None, description="Filter by ruleset name"),
    limit: int = Query(50, le=100, description="Max results"),
    min_similarity: float = Query(0.1, ge=0.0, le=1.0, description="Minimum similarity threshold"),
    lang: str | None = Cookie(default=None),
):
    """
    Search rules using fuzzy matching with PostgreSQL trigram similarity.

    Searches both names and descriptions in English and Ukrainian.
    Returns results ordered by relevance score (best matches first).
    """
    translations = get_translations(request, lang)
    current_lang = get_language(request, lang)

    # Allow empty query if type or ruleset filter is set
    has_valid_type = rule_type and rule_type.strip() and rule_type != ""
    has_valid_ruleset = ruleset and ruleset.strip() and ruleset not in ["", "all"]
    if (not q or len(q) < 2) and not has_valid_type and not has_valid_ruleset:  # noqa
        return templates.TemplateResponse(
            "search_results.html",
            {"request": request, "results": [], "query": q, "t": translations, "current_lang": current_lang},
        )

    # Build fuzzy search query
    stmt = select(models.Rule).options(selectinload(models.Rule.ruleset)).join(models.RuleSet)

    # Add fuzzy search filter if query provided
    if q and len(q) >= 2:  # noqa
        # Build fuzzy search conditions using the search service
        similarity_score, where_condition = build_fuzzy_search_query(q, min_similarity)

        # Add similarity score to select
        stmt = select(models.Rule, similarity_score).options(selectinload(models.Rule.ruleset)).join(models.RuleSet)

        stmt = stmt.where(where_condition)

        # Order by similarity score (best matches first)
        stmt = stmt.order_by(similarity_score.desc())

    if ruleset and ruleset.strip() and ruleset != "all":
        stmt = stmt.where(models.RuleSet.abbreviation == ruleset)

    if rule_type and rule_type.strip() and rule_type != "all":
        stmt = stmt.where(models.Rule.type == rule_type)

    stmt = stmt.limit(limit)
    result = await db.execute(stmt)

    # Handle results based on whether we have similarity scoring
    if q and len(q) >= 2:  # noqa
        rows = result.all()
        rules = [row[0] for row in rows]  # Extract rule objects from (rule, similarity_score) tuples
    else:
        rules = result.scalars().all()

    # Convert to simple dict for template
    results = []
    for rule in rules:
        results.append(
            {
                "id": rule.id,
                "type": rule.type,
                "rule_name": rule.get_name(current_lang),
                "rule_description": rule.get_description(current_lang),
                "rule_slug": rule.slug,
                "ruleset_name": rule.ruleset.name,
                "ruleset_slug": rule.ruleset.slug,
                "ruleset_abbreviation": rule.ruleset.abbreviation,
                "tags": rule.tags or [],
                "meta_data": rule.meta_data or {},
                "is_official": rule.is_official,
            }
        )

    return templates.TemplateResponse(
        "search_results.html",
        {
            "request": request,
            "results": results,
            "query": q,
            "type_filter": rule_type,
            "t": translations,
            "current_lang": current_lang,
        },
    )
