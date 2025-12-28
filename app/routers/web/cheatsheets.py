from fastapi import APIRouter, Cookie, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies.i18n import get_language, get_translations
from app.utils import render_markdown

router = APIRouter(tags=["cheatsheets"])
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["markdown"] = render_markdown


@router.get("/cheatsheets/wwn-combat", response_class=HTMLResponse)
async def wwn_combat_cheatsheet(request: Request, lang: str | None = Cookie(default=None)):
    """WWN Combat Cheatsheet - quick reference for combat rules"""
    translations = get_translations(request, lang)
    current_lang = get_language(request, lang)

    # Select template based on language
    template_name = "cheatsheets/wwn_combat_uk.html" if current_lang == "uk" else "cheatsheets/wwn_combat.html"

    return templates.TemplateResponse(
        template_name,
        {"request": request, "t": translations, "current_lang": current_lang},
    )
