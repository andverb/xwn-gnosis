from fastapi import APIRouter, Cookie, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app import models
from app.dependencies import DbSession
from app.dependencies.i18n import get_language, get_translations
from app.utils import render_markdown

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["markdown"] = render_markdown


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, lang: str | None = Cookie(default=None)):
    translations = get_translations(request, lang)
    current_lang = get_language(request, lang)
    return templates.TemplateResponse(
        "index.html", {"request": request, "t": translations, "current_lang": current_lang}
    )


@router.get("/rules/{rule_id}/card", response_class=HTMLResponse)
async def rule_card(
    rule_id: int,
    request: Request,
    db: DbSession,
    query: str = "",
    rule_type: str = Query("", alias="type"),
    lang: str | None = Cookie(default=None),
):
    """Get rule detail card for htmx"""
    translations = get_translations(request, lang)
    current_lang = get_language(request, lang)

    stmt = select(models.Rule).options(selectinload(models.Rule.ruleset)).where(models.Rule.id == rule_id)
    result = await db.execute(stmt)
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Extract English content
    en_content = rule.translations.get("en", {})
    rule_data = {
        "id": rule.id,
        "slug": rule.slug,
        "type": rule.type,
        "rule_name": en_content.get("name", f"Rule {rule.id}"),
        "rule_description": en_content.get("description", ""),
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

    return templates.TemplateResponse(
        "rule_card.html",
        {
            "request": request,
            "rule": rule_data,
            "query": query,
            "type": rule_type,
            "t": translations,
            "current_lang": current_lang,
        },
    )


@router.get("/set-language/{lang}")
async def set_language(lang: str):
    """Set language preference via cookie"""
    if lang not in ["en", "uk"]:
        lang = "en"

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="lang", value=lang, max_age=31536000, httponly=True, samesite="lax")  # 1 year
    return response


@router.get("/health")
async def health_check():
    return {"message": "Im OK!"}
