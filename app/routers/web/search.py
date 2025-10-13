from fastapi import APIRouter, Cookie, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app import models
from app.dependencies import DbSession
from app.dependencies.i18n import get_language, get_translations
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
    lang: str | None = Cookie(default=None),
):
    translations = get_translations(request, lang)
    current_lang = get_language(request, lang)

    # Allow empty query if type filter is set OR if "all" is selected
    has_valid_type = rule_type and rule_type.strip() and rule_type != ""
    if (not q or len(q) < 2) and not has_valid_type:  # noqa
        return templates.TemplateResponse(
            "search_results.html",
            {"request": request, "results": [], "query": q, "t": translations, "current_lang": current_lang},
        )

    # Reuse the same search logic
    stmt = select(models.Rule).options(selectinload(models.Rule.ruleset)).join(models.RuleSet)

    # Add search filter if query provided
    if q and len(q) >= 2:  # noqa
        search_term = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                models.Rule.translations["en"]["name"].astext.ilike(search_term),
                # models.Rule.tags.cast(String).ilike(search_term),  # dont search tags for now
                models.Rule.type.ilike(search_term),
            )
        )

    if ruleset:
        stmt = stmt.where(models.RuleSet.name.ilike(f"%{ruleset}%"))

    if rule_type and rule_type.strip() and rule_type != "all":
        stmt = stmt.where(models.Rule.type == rule_type)

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
                "type": rule.type,
                "rule_name": en_content.get("name", f"Rule {rule.id}"),
                "rule_description": en_content.get("description", ""),
                "ruleset_name": rule.ruleset.name,
                "ruleset_abbreviation": rule.ruleset.abbreviation,
                "tags": rule.tags or [],
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
