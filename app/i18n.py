"""
Internationalization (i18n) module for Gnosis.
Simple dictionary-based translations for English and Ukrainian.
"""

# Translation dictionaries
TRANSLATIONS = {
    "en": {
        # Navigation & Header
        "app_title": "Gnosis - xWN Rules Database",
        "welcome": "Gnosis",
        "subtitle": "Database of rules for xWN systems",
        "info_tooltip": "Made by John from DMK | xWN systems by Kevin Crawford",
        "rulesets_tooltip": "Browse rulesets",
        "rulesets_title": "Rulesets - Choose Language",
        "rulesets_subtitle": "Choose your language to view the complete rules documentation",
        "rulesets_wwn_lite_desc": "A simplified version of Worlds Without Number,"
        " perfect for newcomers to the xWN system.",
        "toggle_theme": "Toggle theme",
        "toggle_language": "Змінити мову на Українську",
        # Search Interface
        "search_placeholder": "Search rules, classes, spells...",
        "filter_type_label": "Type",
        "filter_system_label": "System",
        "filter_all": "All",
        "filter_rules": "Rules",
        "filter_backgrounds": "Backgrounds",
        "filter_classes": "Classes",
        "filter_foci": "Foci",
        "filter_arts": "Arts",
        "filter_spells": "Spells",
        "filter_weapons": "Weapons",
        "filter_armor": "Armor",
        "filter_combat_actions": "Combat Actions",
        "filter_skills": "Skills",
        # Rule Card
        "back_to_search": "Back to search",
        "rule_type": "Type",
        "tags": "Tags",
        "created_at": "Created",
        "updated_at": "Updated",
        "created_by": "Created by",
        "last_updated_by": "Last updated by",
        "changes": "Changes from base rule",
        "changes_from_base": "Changes from Base Rule:",
        "no_description": "No description available.",
        # Common
        "loading": "Loading...",
        "no_results": "No results found",
        "error": "An error occurred",
    },
    "uk": {  # Ukrainian
        # Navigation & Header
        "app_title": "Гнозіс - База правил xWN",
        "welcome": "Гнозіс",
        "subtitle": "База правил для систем xWN",
        "info_tooltip": "Створено Джоном з DMK | Системи xWN від Кевіна Кроуфорда",
        "rulesets_tooltip": "Переглянути збірки правил",
        "rulesets_title": "Збірки Правил - Оберіть Мову",
        "rulesets_subtitle": "Оберіть мову для перегляду повної документації правил",
        "rulesets_wwn_lite_desc": "Спрощена версія Worlds Without Number, ідеальна для новачків у системі xWN.",
        "toggle_theme": "Змінити тему",
        "toggle_language": "Switch to English",
        # Search Interface
        "search_placeholder": "Шукати правила, класи, закляття...",
        "filter_type_label": "Тип",
        "filter_system_label": "Система",
        "filter_all": "Всі",
        "filter_rules": "Правила",
        "filter_backgrounds": "Передісторії",
        "filter_classes": "Класи",
        "filter_foci": "Фокуси",
        "filter_arts": "Мистецтва",
        "filter_spells": "Закляття",
        "filter_weapons": "Зброя",
        "filter_armor": "Обладунки",
        "filter_combat_actions": "Бойові дії",
        "filter_skills": "Навички",
        # Rule Card
        "back_to_search": "Назад до пошуку",
        "rule_type": "Тип",
        "tags": "Теги",
        "created_at": "Створено",
        "updated_at": "Оновлено",
        "created_by": "Створив",
        "last_updated_by": "Останнє оновлення",
        "official": "Офіційне",
        "homebrew": "Homebrew",
        "changes": "Зміни від базового правила",
        "changes_from_base": "Зміни від базового правила:",
        "no_description": "Опис відсутній.",
        # Common
        "loading": "Завантаження...",
        "no_results": "Результатів не знайдено",
        "error": "Сталася помилка",
    },
}


def get_translation(key: str, lang: str = "en") -> str:
    """
    Get translation for a given key and language.

    Args:
        key: Translation key (e.g., "welcome")
        lang: Language code ("en" or "uk")

    Returns:
        Translated string, or the key itself if translation not found
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


def get_translations_for_lang(lang: str = "en") -> dict[str, str]:
    """
    Get all translations for a specific language.

    Args:
        lang: Language code ("en" or "uk")

    Returns:
        Dictionary of all translations for the language
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])
