from fastapi import APIRouter, Cookie, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app import models
from app.config import settings
from app.dependencies import DbSession
from app.dependencies.i18n import get_language, get_translations
from app.utils import render_markdown

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["markdown"] = render_markdown


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: DbSession, lang: str | None = Cookie(default=None)):
    translations = get_translations(request, lang)
    current_lang = get_language(request, lang)

    # Fetch all rulesets for system filter dropdown
    stmt = select(models.RuleSet).order_by(models.RuleSet.name)
    result = await db.execute(stmt)
    rulesets = result.scalars().all()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "t": translations, "current_lang": current_lang, "rulesets": rulesets},
    )


@router.get("/rules/{ruleset_slug}/{rule_slug}", response_class=HTMLResponse)
async def rule_card(
    ruleset_slug: str,
    rule_slug: str,
    request: Request,
    db: DbSession,
    query: str = "",
    rule_type: str = Query("", alias="type"),
    lang: str | None = Cookie(default=None),
):
    """Get rule detail card - returns full page or htmx partial"""
    translations = get_translations(request, lang)
    current_lang = get_language(request, lang)

    # Join Rule and RuleSet to find by both slugs
    stmt = (
        select(models.Rule)
        .options(selectinload(models.Rule.ruleset))
        .join(models.RuleSet)
        .where(models.RuleSet.slug == ruleset_slug, models.Rule.slug == rule_slug)
    )
    result = await db.execute(stmt)
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule_data = {
        "id": rule.id,
        "slug": rule.slug,
        "type": rule.type,
        "rule_name": rule.get_name(current_lang),
        "rule_description": rule.get_description(current_lang),
        "ruleset_name": rule.ruleset.name,
        "tags": rule.tags or [],
        "is_official": rule.is_official,
        "changes_description": rule.changes_description,
        "meta_data": rule.meta_data,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at,
        "created_by": rule.created_by,
        "last_update_by": rule.last_update_by,
    }

    # Check if request is from htmx
    is_htmx = request.headers.get("HX-Request") == "true"

    if is_htmx:
        # Return partial for htmx with back links
        return templates.TemplateResponse(
            "rule_card.html",
            {
                "request": request,
                "rule": rule_data,
                "query": query,
                "type": rule_type,
                "show_back_link": True,
                "t": translations,
                "current_lang": current_lang,
            },
        )
    # Return full page for direct access without back links
    return templates.TemplateResponse(
        "rule_detail_page.html",
        {
            "request": request,
            "rule": rule_data,
            "query": query,
            "type": rule_type,
            "show_back_link": False,
            "t": translations,
            "current_lang": current_lang,
        },
    )


@router.get("/set-language/{lang}")
async def set_language(lang: str, request: Request):
    """Set language preference via cookie"""
    if lang not in ["en", "uk"]:
        lang = "en"

    # Redirect back to referrer or home
    referer = request.headers.get("referer", "/")
    response = RedirectResponse(url=referer, status_code=303)

    is_production = settings.environment == "production"
    response.set_cookie(
        key="lang",
        value=lang,
        max_age=31536000,  # 1 year
        httponly=True,
        samesite="lax",
        secure=is_production,
    )
    return response


@router.get("/health")
async def health_check():
    return {"message": "Im OK!"}
