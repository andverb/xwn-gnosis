from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models
from app.db import get_db
from app.utils import render_markdown

router = APIRouter(tags=["utility"])
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["markdown"] = render_markdown


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/rules/{rule_id}/card", response_class=HTMLResponse)
async def rule_card(rule_id: int, request: Request, query: str = "", db: AsyncSession = Depends(get_db)):
    """Get rule detail card for htmx"""
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
        "rule_name": en_content.get("name", f"Rule {rule.id}"),
        "rule_description": en_content.get("description", ""),
        "ruleset_name": rule.ruleset.name,
        "tags": rule.tags or [],
        "is_official": rule.is_official,
        "changes_description": rule.changes_description,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at,
        "created_by": rule.created_by,
        "last_update_by": rule.last_update_by,
    }

    return templates.TemplateResponse("rule_card.html", {"request": request, "rule": rule_data, "query": query})


@router.get("/health")
async def health_check():
    return {"message": "Im OK!"}
