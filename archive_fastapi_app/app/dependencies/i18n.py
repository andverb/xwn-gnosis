"""
i18n dependencies for FastAPI routes.
"""

from fastapi import Cookie, Request

from app.i18n import get_translations_for_lang


def get_language(request: Request, lang: str | None = Cookie(default=None)) -> str:
    """
    Determine the user's preferred language.

    Priority:
    1. Cookie value
    2. Accept-Language header
    3. Default to "en"

    Args:
        request: FastAPI request object
        lang: Language from cookie

    Returns:
        Language code ("en" or "uk")
    """
    # Check cookie first
    if lang in ["en", "uk"]:
        return lang

    # Check Accept-Language header
    accept_language = request.headers.get("Accept-Language", "")
    if "uk" in accept_language.lower() or "ua" in accept_language.lower():
        return "uk"

    # Default to English
    return "en"


def get_translations(request: Request, lang: str | None = Cookie(default=None)) -> dict[str, str]:
    """
    Get all translations for the user's preferred language.

    Args:
        request: FastAPI request object
        lang: Language from cookie

    Returns:
        Dictionary of translations
    """
    user_lang = get_language(request, lang)
    return get_translations_for_lang(user_lang)
