"""
Context processors for the tools app.

These functions add variables to the template context for all requests.
"""

from .nav import get_all_sections


def rules_nav(request):
    """
    Add rules navigation data to template context.

    Provides `rules_nav` dict with sections and pages for the current language.
    """
    # Get language from cookie (matching views.py pattern)
    lang = request.COOKIES.get("lang", "en")

    return {
        "rules_nav": get_all_sections(lang),
    }
