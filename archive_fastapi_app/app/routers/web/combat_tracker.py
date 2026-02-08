import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Cookie, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies.i18n import get_language, get_translations
from app.utils import render_markdown

router = APIRouter(tags=["combat-tracker"])
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["markdown"] = render_markdown

WEAPONS_FILE = Path("data/wwn_weapons.json")


@lru_cache
def get_weapons_data() -> dict:
    """Load weapons data from JSON file (cached)"""
    with open(WEAPONS_FILE) as f:
        return json.load(f)


@router.get("/combat-tracker", response_class=HTMLResponse)
async def combat_tracker(request: Request, lang: str | None = Cookie(default=None)):
    """WWN Combat Tracker - initiative and HP tracking"""
    translations = get_translations(request, lang)
    current_lang = get_language(request, lang)
    weapons_data = get_weapons_data()

    # For now, use English template for both languages (will add Ukrainian later)
    template_name = "combat_tracker/tracker.html"

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "t": translations,
            "current_lang": current_lang,
            "weapons": weapons_data["weapons"],
            "weapon_traits": weapons_data["traits"],
        },
    )
