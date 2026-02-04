"""
Django views for GM tools (cheatsheets, combat tracker).

All views are async for better concurrency under load.
"""

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import aiofiles
import markdown
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import TypoSuggestion
from .nav import get_section_pages as get_cached_section_pages

# Path to JSON data files (in static/data/ for offline caching support)
DATA_DIR = Path(settings.BASE_DIR) / "static" / "data"
WEAPONS_FILE = DATA_DIR / "wwn_weapons.json"
SPELLS_FILE = DATA_DIR / "wwn_spells.json"
FOCI_FILE = DATA_DIR / "wwn_foci.json"
EQUIPMENT_FILE = DATA_DIR / "wwn_equipment.json"


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


async def combat_cheatsheet(request):
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


async def encounter_cheatsheet(request):
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
async def calculate_challenge(request):
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

    # Ensure minimum values of 1
    attacks = max(total_attacks, 1)
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


async def combat_tracker(request):
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
            # Raw list for Django template iteration
            "weapons": weapons_data["weapons"],
            # Pre-serialize to JSON for safe embedding in <script> tags
            "weapons_json": json.dumps(weapons_data["weapons"]),
            "weapon_traits_json": json.dumps(weapons_data["traits"]),
        },
    )


async def set_language(request, lang):
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


async def health_check(request):
    """
    Simple health check endpoint for deployment monitoring.

    HttpResponse is the base response class - we return plain text here.
    """
    return HttpResponse("OK", content_type="text/plain")


# ============================================================================
# Entity Browser Views
# ============================================================================


@lru_cache
def get_spells_data() -> dict:
    """Load spells data from JSON file (cached)."""
    if SPELLS_FILE.exists():
        with open(SPELLS_FILE) as f:
            return json.load(f)
    return {"spells": []}


@lru_cache
def get_foci_data() -> dict:
    """Load foci data from JSON file (cached)."""
    if FOCI_FILE.exists():
        with open(FOCI_FILE) as f:
            return json.load(f)
    return {"foci": []}


@lru_cache
def get_equipment_data() -> dict:
    """Load equipment data from JSON file (cached)."""
    if EQUIPMENT_FILE.exists():
        with open(EQUIPMENT_FILE) as f:
            return json.load(f)
    return {"equipment": [], "armor": []}


def get_all_entities(lang: str) -> list[dict]:
    """
    Load and combine all entity types into a single list.

    Each entity is normalized to have consistent fields for display:
    - id, name, type, description, tags
    - Plus type-specific fields (level, tradition, damage, etc.)
    """
    entities = []

    # Load spells
    spells_data = get_spells_data()
    for spell in spells_data.get("spells", []):
        entities.append(
            {
                "id": spell["id"],
                "name": spell["name"].get(lang, spell["name"].get("en", "")),
                "type": "spell",
                "level": spell.get("level", 1),
                "tradition": spell.get("tradition", ""),
                "description": spell["description"].get(lang, spell["description"].get("en", "")),
                "tags": spell.get("tags", []),
            }
        )

    # Load foci
    foci_data = get_foci_data()
    for focus in foci_data.get("foci", []):
        entities.append(
            {
                "id": focus["id"],
                "name": focus["name"].get(lang, focus["name"].get("en", "")),
                "type": "focus",
                "category": focus.get("category", ""),
                "description": focus["description"].get(lang, focus["description"].get("en", "")),
                "tags": focus.get("tags", []),
            }
        )

    # Load weapons
    weapons_data = get_weapons_data()
    for weapon in weapons_data.get("weapons", []):
        shock_str = ""
        if weapon.get("shock"):
            shock_str = f"{weapon['shock']['value']}/{weapon['shock'].get('ac', '-')}"
        entities.append(
            {
                "id": weapon["id"],
                "name": weapon["name"].get(lang, weapon["name"].get("en", "")),
                "type": "weapon",
                "damage": weapon.get("damage", ""),
                "shock": shock_str,
                "range": weapon.get("range", ""),
                "description": "",  # Weapons don't have descriptions in current data
                "tags": weapon.get("traits", []),
            }
        )

    # Load equipment
    equipment_data = get_equipment_data()
    for item in equipment_data.get("equipment", []):
        entities.append(
            {
                "id": item["id"],
                "name": item["name"].get(lang, item["name"].get("en", "")),
                "type": "equipment",
                "cost": item.get("cost", ""),
                "enc": item.get("enc", ""),
                "description": item["description"].get(lang, item["description"].get("en", "")),
                "tags": item.get("tags", []),
            }
        )

    # Load armor
    for armor in equipment_data.get("armor", []):
        entities.append(
            {
                "id": armor["id"],
                "name": armor["name"].get(lang, armor["name"].get("en", "")),
                "type": "armor",
                "ac": armor.get("ac", ""),
                "cost": armor.get("cost", ""),
                "enc": armor.get("enc", ""),
                "description": armor["description"].get(lang, armor["description"].get("en", "")),
                "tags": armor.get("tags", []),
            }
        )

    return entities


async def entity_browse(request):
    """
    Entity Browser main page.

    Displays a searchable/filterable grid of game entities (spells, foci, weapons, etc.).
    """
    current_lang = get_language(request)

    return render(
        request,
        "tools/entities/browse.html",
        {
            "current_lang": current_lang,
            "other_lang": get_other_lang(current_lang),
        },
    )


async def entity_search(request):
    """
    htmx endpoint for entity search/filter.

    Returns HTML fragment with filtered entity cards.
    Supports query string filtering by:
    - q: search text (matches name and description)
    - type: entity type filter (spell, focus, weapon, armor, equipment)
    """
    current_lang = get_language(request)
    query = request.GET.get("q", "").strip().lower()
    entity_type = request.GET.get("type", "").strip().lower()

    # Get all entities
    entities = get_all_entities(current_lang)

    # Filter by type
    if entity_type:
        entities = [e for e in entities if e["type"] == entity_type]

    # Filter by search query
    if query:
        filtered = []
        for entity in entities:
            # Search in name, description, and tags
            name_match = query in entity["name"].lower()
            desc_match = query in entity.get("description", "").lower()
            tag_match = any(query in tag.lower() for tag in entity.get("tags", []))

            if name_match or desc_match or tag_match:
                filtered.append(entity)
        entities = filtered

    # Sort by type, then name
    type_order = {"spell": 0, "focus": 1, "weapon": 2, "armor": 3, "equipment": 4}
    entities.sort(key=lambda e: (type_order.get(e["type"], 99), e["name"]))

    return render(
        request,
        "tools/entities/_entity_list.html",
        {
            "entities": entities,
            "current_lang": current_lang,
        },
    )


# ============================================================================
# Rules Views
# ============================================================================

# Rules content is stored in docs/wwn-lite/{lang}/{section}/{page}.md
RULES_DIR = Path(settings.BASE_DIR).parent / "docs" / "wwn-lite"

# Section metadata (icon, description)
SECTION_META = {
    "basics": {
        "title": {"en": "Basics", "uk": "Основи"},
        "icon": "bi bi-star",
        "description": {
            "en": "Core mechanics, attribute checks, skill checks, and saving throws.",
            "uk": "Основні механіки, перевірки атрибутів, навичок та рятівні кидки.",
        },
    },
    "survival": {
        "title": {"en": "Survival", "uk": "Виживання"},
        "icon": "bi bi-heart-pulse",
        "description": {
            "en": "Hit points, healing, environmental perils, and travel.",
            "uk": "Хіти, лікування, небезпеки середовища та подорожі.",
        },
    },
    "combat": {
        "title": {"en": "Combat", "uk": "Бій"},
        "icon": "bi bi-shield",
        "description": {
            "en": "Combat basics, actions, attack rolls, damage, and shock.",
            "uk": "Основи бою, дії, кидки атаки, пошкодження та шок.",
        },
    },
    "equipment": {
        "title": {"en": "Equipment", "uk": "Спорядження"},
        "icon": "bi bi-backpack",
        "description": {
            "en": "Weapons, armor, gear, and encumbrance rules.",
            "uk": "Зброя, обладунки, спорядження та правила обтяжливості.",
        },
    },
    "magic": {
        "title": {"en": "Magic", "uk": "Магія"},
        "icon": "bi bi-magic",
        "description": {
            "en": "Magic basics, spells, and magical items.",
            "uk": "Основи магії, закляття та магічні предмети.",
        },
    },
    "character": {
        "title": {"en": "Character", "uk": "Персонаж"},
        "icon": "bi bi-person",
        "description": {
            "en": "Character creation, XP, and leveling.",
            "uk": "Створення персонажа, досвід та підвищення рівня.",
        },
    },
    "campaign": {
        "title": {"en": "Campaign", "uk": "Кампанія"},
        "icon": "bi bi-map",
        "description": {
            "en": "Downtime activities, hirelings, and renown.",
            "uk": "Відпочинок, наймити та репутація.",
        },
    },
    "reference": {
        "title": {"en": "Reference", "uk": "Довідник"},
        "icon": "bi bi-bookmark",
        "description": {
            "en": "NPC statistics, encounter difficulty, and quick reference tables.",
            "uk": "Статистика НІПів, складність зустрічей та довідкові таблиці.",
        },
    },
}


def get_section_pages(section: str, lang: str) -> list[dict]:
    """
    Get list of pages in a rules section.

    Uses cached navigation from pre-built JSON files.
    Falls back to file scanning if cache is not available.
    """
    pages = get_cached_section_pages(section, lang)
    if pages:
        return pages

    # Fallback: scan files directly (for development without build step)
    section_dir = RULES_DIR / lang / section
    fallback_pages = []

    if section_dir.exists():
        for md_file in sorted(section_dir.glob("*.md")):
            slug = md_file.stem
            # Read first line to get title
            with open(md_file, encoding="utf-8") as f:
                first_line = f.readline().strip()
                title = first_line.lstrip("#").strip() if first_line.startswith("#") else slug.replace("-", " ").title()
            fallback_pages.append({"slug": slug, "title": title})

    return fallback_pages


def render_markdown(content: str) -> tuple[str, str, list]:
    """
    Render markdown to HTML with linkable headings.

    Returns:
        tuple: (html_content, toc_html, toc_tokens)
            - html_content: The rendered HTML
            - toc_html: HTML for table of contents
            - toc_tokens: List of heading dicts for programmatic use
    """
    md = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "toc",
        ],
        extension_configs={
            "toc": {
                # Add IDs to all headings
                "slugify": lambda value, separator: slugify_heading(value),
                # Add permalink anchor after each heading (link icon)
                "permalink": "",  # Empty string, we'll use CSS for the icon
                "permalink_class": "heading-anchor",
                "permalink_title": "Copy link",
                # Generate TOC tokens for programmatic access
                "toc_depth": "2-4",  # Include H2, H3, H4 in TOC
            },
        },
    )
    html_content = md.convert(content)
    # md.toc is the generated TOC HTML
    # md.toc_tokens is a list of heading dicts with 'level', 'id', 'name', 'children'
    return html_content, md.toc, getattr(md, "toc_tokens", [])


def slugify_heading(value: str) -> str:
    """Convert heading text to URL-safe slug."""
    # Normalize unicode characters
    value = unicodedata.normalize("NFKD", value)
    # Convert to lowercase
    value = value.lower()
    # Remove non-alphanumeric characters (keep spaces and hyphens)
    value = re.sub(r"[^\w\s-]", "", value)
    # Replace spaces with hyphens
    value = re.sub(r"[\s_]+", "-", value)
    # Remove multiple hyphens
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


async def rules_index(request):
    """Rules main index page."""
    current_lang = get_language(request)

    return render(
        request,
        "tools/rules/index.html",
        {
            "current_lang": current_lang,
            "other_lang": get_other_lang(current_lang),
        },
    )


async def rules_section(request, section: str):
    """Rules section landing page."""
    current_lang = get_language(request)

    # Get section metadata
    meta = SECTION_META.get(section, {})
    section_title = meta.get("title", {}).get(current_lang, section.title())
    section_icon = meta.get("icon", "bi bi-folder")
    section_description = meta.get("description", {}).get(current_lang, "")

    # Get pages in this section (cached from nav.json)
    pages = get_section_pages(section, current_lang)

    return render(
        request,
        "tools/rules/section.html",
        {
            "current_lang": current_lang,
            "other_lang": get_other_lang(current_lang),
            "section": section,
            "section_title": section_title,
            "section_icon": section_icon,
            "section_description": section_description,
            "pages": pages,
        },
    )


async def rules_page(request, section: str, page: str):
    """Rules content page - renders markdown file."""
    current_lang = get_language(request)

    # Get section metadata
    meta = SECTION_META.get(section, {})
    section_title = meta.get("title", {}).get(current_lang, section.title())

    # Load markdown file
    md_file = RULES_DIR / current_lang / section / f"{page}.md"

    toc_html = ""
    toc_tokens = []

    if md_file.exists():
        async with aiofiles.open(md_file, encoding="utf-8") as f:
            md_content = await f.read()

        # Extract title from first line
        lines = md_content.split("\n")
        page_title = (
            lines[0].lstrip("#").strip() if lines and lines[0].startswith("#") else page.replace("-", " ").title()
        )

        # Render markdown to HTML (returns content, toc_html, toc_tokens)
        content, toc_html, toc_tokens = render_markdown(md_content)
    else:
        page_title = page.replace("-", " ").title()
        content = f"<p class='text-body-secondary'>Content not found: {section}/{page}</p>"

    # Count headings to decide if TOC should be shown (show if > 5 headings)
    def count_headings(tokens):
        count = len(tokens)
        for token in tokens:
            count += count_headings(token.get("children", []))
        return count

    show_toc = count_headings(toc_tokens) > 5

    # Get pages for prev/next navigation (cached from nav.json)
    pages = get_section_pages(section, current_lang)
    current_idx = next((i for i, p in enumerate(pages) if p["slug"] == page), -1)

    prev_page = pages[current_idx - 1] if current_idx > 0 else None
    next_page = pages[current_idx + 1] if current_idx >= 0 and current_idx < len(pages) - 1 else None

    return render(
        request,
        "tools/rules/page.html",
        {
            "current_lang": current_lang,
            "other_lang": get_other_lang(current_lang),
            "section": section,
            "section_title": section_title,
            "page": page,
            "page_title": page_title,
            "content": content,
            "prev_page": prev_page,
            "next_page": next_page,
            "toc_html": toc_html,
            "toc_tokens": toc_tokens,
            "show_toc": show_toc,
        },
    )


@require_POST
async def suggest_typo(request):
    """
    Handle typo suggestion submissions from rules pages.

    This is an htmx endpoint that receives POST data from the typo suggestion
    modal and creates a TypoSuggestion record. Returns an HTML fragment for
    success feedback.
    """
    section = request.POST.get("section", "")
    page = request.POST.get("page", "")
    selected_text = request.POST.get("selected_text", "")
    context = request.POST.get("context", "")
    suggested_correction = request.POST.get("suggested_correction", "")
    page_url = request.POST.get("page_url", "")

    # Create the suggestion record (using async ORM)
    await TypoSuggestion.objects.acreate(
        section=section,
        page=page,
        selected_text=selected_text,
        context=context,
        suggested_correction=suggested_correction,
        page_url=page_url,
    )

    current_lang = get_language(request)
    return render(
        request,
        "tools/rules/_typo_success.html",
        {"current_lang": current_lang},
    )
