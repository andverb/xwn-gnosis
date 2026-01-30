"""
Django views for GM tools (cheatsheets, combat tracker).
"""

import json
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST  # Decorator to restrict to POST only

# Path to weapons JSON data (in static/data/ for offline caching support)
WEAPONS_FILE = Path(settings.BASE_DIR) / "static" / "data" / "wwn_weapons.json"


def get_language(request):
    """
    Get language preference from cookie.

    In Django, cookies are accessed via request.COOKIES dictionary.
    .get("key", "default") returns the value or default if not found.
    """
    return request.COOKIES.get("lang", "en")


def get_other_lang(current_lang):
    """Get the opposite language for the language switcher button."""
    return "uk" if current_lang == "en" else "en"


@lru_cache  # Python's built-in caching - loads JSON once, reuses on subsequent calls
def get_weapons_data() -> dict:
    """Load weapons data from JSON file (cached for performance)."""
    with open(WEAPONS_FILE) as f:
        return json.load(f)


def combat_cheatsheet(request):
    """
    WWN Combat Cheatsheet view.

    Django's render() function:
    1. Takes the request object (required by Django)
    2. Template path (relative to app's templates/ folder)
    3. Context dictionary - variables available in the template

    Template selection based on language is simple: different templates for each language.
    """
    current_lang = get_language(request)

    # Select template based on language (templates organized by system: wwn/)
    template = "tools/wwn/combat_cheatsheet_uk.html" if current_lang == "uk" else "tools/wwn/combat_cheatsheet_en.html"

    # Context dict - these become template variables: {{ current_lang }}, {{ other_lang }}
    return render(
        request,
        template,
        {
            "current_lang": current_lang,
            "other_lang": get_other_lang(current_lang),
        },
    )


def encounter_cheatsheet(request):
    """Encounter Cheatsheet - morale, instinct, challenge calculator."""
    current_lang = get_language(request)
    template = (
        "tools/wwn/encounter_cheatsheet_uk.html" if current_lang == "uk" else "tools/wwn/encounter_cheatsheet_en.html"
    )
    return render(
        request,
        template,
        {
            "current_lang": current_lang,
            "other_lang": get_other_lang(current_lang),
        },
    )


@require_POST  # This view ONLY accepts POST requests (htmx form submission)
def calculate_challenge(request):
    """
    Calculate encounter challenge rating.

    This is an htmx endpoint - it returns an HTML fragment, not a full page.
    htmx will insert this fragment into the page without full reload.

    request.POST is a dictionary-like object containing form data.
    request.POST.get("key", default) - safely gets value or default.
    """
    # Get form values, convert to int with defaults
    total_hd = int(request.POST.get("total_hd", 1))
    total_attacks = int(request.POST.get("total_attacks", 1))
    num_pcs = int(request.POST.get("num_pcs", 4))
    total_pc_levels = int(request.POST.get("total_pc_levels", 4))
    lang = request.POST.get("lang")  # Hidden form field for language

    # Language from form takes precedence, then cookie
    current_lang = lang or get_language(request)

    # Game logic: ensure attacks >= HD
    attacks = max(total_attacks, total_hd, 1)
    hd = max(total_hd, 1)

    foe_score = attacks * hd
    party_score = total_pc_levels * num_pcs

    # Avoid division by zero
    if party_score == 0:
        party_score = 1

    ratio = foe_score / party_score

    # Bilingual verdicts dictionary
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

    # Determine verdict based on ratio
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

    # Return partial template (HTML fragment for htmx)
    template_name = (
        "tools/wwn/partials/_challenge_result_uk.html"
        if current_lang == "uk"
        else "tools/wwn/partials/_challenge_result_en.html"
    )

    return render(
        request,
        template_name,
        {
            "foe_score": foe_score,
            "party_score": party_score,
            "verdict": verdict,
            "verdict_class": verdict_class,
        },
    )


def combat_tracker(request):
    """
    WWN Combat Tracker - initiative and HP tracking.

    This view passes weapons data to the template for the combat tracker's
    weapon selection dropdown. The data is cached via @lru_cache.

    Note: We serialize to JSON here because Django templates don't have
    Jinja2's |tojson filter. We use |safe in the template to output it.
    """
    current_lang = get_language(request)
    weapons_data = get_weapons_data()

    return render(
        request,
        "tools/wwn/combat_tracker.html",
        {
            "current_lang": current_lang,
            "other_lang": get_other_lang(current_lang),
            # Pre-serialize to JSON for safe embedding in <script> tags
            "weapons_json": json.dumps(weapons_data["weapons"]),
            "weapon_traits_json": json.dumps(weapons_data["traits"]),
        },
    )


def set_language(request, lang):
    """
    Set language cookie and redirect back.

    Django's redirect() returns an HttpResponseRedirect.
    response.set_cookie() sets a cookie on the response.

    HTTP_REFERER header contains the page the user came from.
    """
    # Get the page user came from, or default to home
    referer = request.META.get("HTTP_REFERER", "/")
    response = redirect(referer)

    # Set cookie: name, value, max_age in seconds (1 year)
    response.set_cookie("lang", lang, max_age=365 * 24 * 60 * 60)
    return response


def health_check(request):
    """
    Simple health check endpoint for deployment monitoring.

    HttpResponse is the base response class - we return plain text here.
    """
    return HttpResponse("OK", content_type="text/plain")
