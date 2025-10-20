"""Compendium web routes for reading rulesets as organized documents."""

from pathlib import Path

from fastapi import APIRouter, Cookie, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.dependencies.i18n import get_translations
from app.utils import (
    get_chapter_by_id,
    get_navigation_info,
    parse_markdown_compendium,
    render_markdown,
)

router = APIRouter(tags=["web"])
settings = get_settings()
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["markdown"] = render_markdown

# Cache parsed compendia
_compendium_cache = {}


def get_compendium_path(ruleset_slug: str, lang: str) -> Path:
    """Get path to compendium markdown file."""
    # Map ruleset slugs to file names
    file_map = {
        "wwn-lite": {
            "en": "wwn-lite-en.md",
            "uk": "wwn-lite-uk.md",  # When available
        }
    }

    if ruleset_slug not in file_map:
        raise HTTPException(status_code=404, detail="Ruleset not found")

    filename = file_map[ruleset_slug].get(lang)
    if not filename:
        # Fallback to English if translation not available
        filename = file_map[ruleset_slug].get("en")

    if not filename:
        raise HTTPException(status_code=404, detail="Compendium not found")

    file_path = Path("data/data_sources") / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Compendium file not found")

    return file_path


def load_compendium(ruleset_slug: str, lang: str):
    """Load and cache compendium."""
    cache_key = f"{ruleset_slug}:{lang}"

    if cache_key not in _compendium_cache:
        file_path = get_compendium_path(ruleset_slug, lang)
        _compendium_cache[cache_key] = parse_markdown_compendium(file_path)

    return _compendium_cache[cache_key]


@router.get("/ruleset/{ruleset_slug}", response_class=HTMLResponse)
async def view_ruleset_index(request: Request, ruleset_slug: str, lang: str | None = Cookie(default=None)):
    """Display ruleset compendium with first chapter."""
    translations = get_translations(request, lang)
    compendium = load_compendium(ruleset_slug, lang or "en")

    # Show first chapter by default
    first_chapter = compendium.chapters[0] if compendium.chapters else None

    return templates.TemplateResponse(
        "compendium.html",
        {
            "request": request,
            "compendium": compendium,
            "current_chapter": first_chapter,
            "nav": get_navigation_info(compendium, first_chapter.id) if first_chapter else {"prev": None, "next": None},
            "ruleset_slug": ruleset_slug,
            "t": translations,
        },
    )


@router.get("/ruleset/{ruleset_slug}/{chapter_id}", response_class=HTMLResponse)
async def view_ruleset_chapter(
    request: Request, ruleset_slug: str, chapter_id: str, lang: str | None = Cookie(default=None)
):
    """Display specific chapter."""
    translations = get_translations(request, lang)
    compendium = load_compendium(ruleset_slug, lang or "en")

    chapter = get_chapter_by_id(compendium, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    nav = get_navigation_info(compendium, chapter_id)

    return templates.TemplateResponse(
        "compendium.html",
        {
            "request": request,
            "compendium": compendium,
            "current_chapter": chapter,
            "nav": nav,
            "ruleset_slug": ruleset_slug,
            "t": translations,
        },
    )


@router.get("/ruleset/{ruleset_slug}/{chapter_id}/content", response_class=HTMLResponse)
async def view_chapter_content(
    request: Request, ruleset_slug: str, chapter_id: str, lang: str | None = Cookie(default=None)
):
    """
    Return just the chapter content for htmx partial updates.
    This allows navigation without full page reload.
    """
    translations = get_translations(request, lang)
    compendium = load_compendium(ruleset_slug, lang or "en")

    chapter = get_chapter_by_id(compendium, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    nav = get_navigation_info(compendium, chapter_id)

    return templates.TemplateResponse(
        "compendium_content.html",
        {
            "request": request,
            "current_chapter": chapter,
            "nav": nav,
            "ruleset_slug": ruleset_slug,
            "t": translations,
        },
    )
