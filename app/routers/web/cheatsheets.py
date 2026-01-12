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


@router.get("/cheatsheets/wwn-encounter", response_class=HTMLResponse)
async def encounter_cheatsheet(request: Request, lang: str | None = Cookie(default=None)):
    """Encounter Cheatsheet - morale, instinct, challenge calculator"""
    translations = get_translations(request, lang)
    current_lang = get_language(request, lang)

    template_name = "cheatsheets/wwn_encounter_uk.html" if current_lang == "uk" else "cheatsheets/wwn_encounter.html"

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
    lang: str = Form(default=None),
    language: str | None = Cookie(default=None, alias="lang"),
):
    """Calculate encounter challenge rating"""
    # Determine language from form or cookie
    current_lang = lang or language or "en"

    # Ensure attacks >= HD (minimum 1 attack per HD)
    attacks = max(total_attacks, total_hd, 1)
    hd = max(total_hd, 1)

    foe_score = attacks * hd
    party_score = total_pc_levels * num_pcs

    # Avoid division by zero
    if party_score == 0:
        party_score = 1

    ratio = foe_score / party_score

    # Verdicts in both languages
    verdicts = {
        "en": {
            "rout": "Rout - Excellent tactics or magic needed to survive",
            "deadly": "Deadly - At least 1 PC down, possible TPK",
            "hard": "Hard - Ally might go down, decent chance to win",
            "fair": "Fair - Likely win without Mortally Wounded",
            "easy": "Easy - Probably a walkover",
        },
        "uk": {
            "rout": "Розгром - Щоб вижити, потрібна відмінна тактика або магія",
            "deadly": "Смертельна небезпека - Мінімум 1 персонаж в 0, можливий TPK",
            "hard": "Важко - Хтось із ПГ може впасти в 0, але є шанс на перемогу",
            "fair": "Справедливо - Ймовірна перемога без С. Поранених персонажів",
            "easy": "Легко - Скоріш за все легка прогулянка",
        },
    }

    lang_verdicts = verdicts.get(current_lang, verdicts["en"])

    if ratio > 4:
        verdict = lang_verdicts["rout"]
        verdict_class = "verdict-rout"
    elif ratio >= 2:
        verdict = lang_verdicts["deadly"]
        verdict_class = "verdict-deadly"
    elif ratio > 1:
        verdict = lang_verdicts["hard"]
        verdict_class = "verdict-hard"
    elif ratio > 0.5:
        verdict = lang_verdicts["fair"]
        verdict_class = "verdict-fair"
    else:
        verdict = lang_verdicts["easy"]
        verdict_class = "verdict-easy"

    template_name = (
        "cheatsheets/_challenge_result_uk.html" if current_lang == "uk" else "cheatsheets/_challenge_result.html"
    )

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "foe_score": foe_score,
            "party_score": party_score,
            "verdict": verdict,
            "verdict_class": verdict_class,
        },
    )
