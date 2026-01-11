from fastapi import APIRouter, Cookie, Form, Request
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


@router.get("/cheatsheets/wwn-dm-encounter", response_class=HTMLResponse)
async def wwn_dm_encounter_cheatsheet(request: Request, lang: str | None = Cookie(default=None)):
    """WWN DM Encounter Cheatsheet - morale, instinct, challenge calculator"""
    translations = get_translations(request, lang)
    current_lang = get_language(request, lang)

    # Select template based on language
    template_name = (
        "cheatsheets/wwn_dm_encounter_uk.html" if current_lang == "uk" else "cheatsheets/wwn_dm_encounter.html"
    )

    return templates.TemplateResponse(
        template_name,
        {"request": request, "t": translations, "current_lang": current_lang},
    )


@router.post("/cheatsheets/calculate-challenge", response_class=HTMLResponse)
async def calculate_challenge(
    request: Request,
    total_hd: int = Form(default=1),
    total_attacks: int = Form(default=1),
    num_pcs: int = Form(default=4),
    total_pc_levels: int = Form(default=4),
):
    """Calculate encounter challenge rating"""
    # Ensure attacks >= HD (minimum 1 attack per HD)
    attacks = max(total_attacks, total_hd, 1)
    hd = max(total_hd, 1)

    foe_score = attacks * hd
    party_score = total_pc_levels * num_pcs

    # Avoid division by zero
    if party_score == 0:
        party_score = 1

    ratio = foe_score / party_score

    if ratio > 4:
        verdict = "Rout - Excellent tactics or magic needed"
        verdict_class = "verdict-rout"
    elif ratio >= 2:
        verdict = "Deadly - At least 1 PC down, possible TPK"
        verdict_class = "verdict-deadly"
    elif ratio > 1:
        verdict = "Hard - Ally might go down, decent chance"
        verdict_class = "verdict-hard"
    elif ratio > 0.5:
        verdict = "Fair - Likely win without Mortally Wounded"
        verdict_class = "verdict-fair"
    else:
        verdict = "Easy - Probably a walkover"
        verdict_class = "verdict-easy"

    return templates.TemplateResponse(
        "cheatsheets/_challenge_result.html",
        {
            "request": request,
            "foe_score": foe_score,
            "party_score": party_score,
            "verdict": verdict,
            "verdict_class": verdict_class,
        },
    )
