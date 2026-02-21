"""
URL configuration for tools app.

Django URL patterns explained:
- path("url-pattern/", view_function, name="name")
- The 'name' is used in templates: {% url 'app_name:name' %}
- <str:lang> captures a string from URL and passes to view as 'lang' parameter
- app_name creates a namespace to avoid conflicts between apps

URL hierarchy:
- /<system>/          → system-specific content (rules, cheatsheets)
- /tools/             → shared tools (combat tracker, entities)
- /                   → global (home, language, health)
"""

from django.urls import path

from . import views

# Namespace for this app - use in templates as {% url 'tools:view_name' %}
app_name = "tools"

urlpatterns = [
    # Home page
    path("", views.rules_index, name="home"),
    # --- WWN system-specific ---
    # Rules
    path("wwn/rules/", views.rules_index, name="rules_index"),
    path("wwn/rules/suggest-typo/", views.suggest_typo, name="suggest_typo"),
    path("wwn/rules/<str:section>/", views.rules_section, name="rules_section"),
    path("wwn/rules/<str:section>/<str:page>/", views.rules_page, name="rules_page"),
    # Cheatsheets
    path("wwn/cheatsheets/combat-actions/", views.combat_actions, name="combat_actions"),
    path("wwn/cheatsheets/site-exploration/", views.site_exploration, name="site_exploration"),
    # WIP
    # path("wwn/cheatsheets/wilderness-exploration/", views.wilderness_exploration, name="wilderness_exploration"),
    path("wwn/cheatsheets/calculate-challenge/", views.calculate_challenge, name="calculate_challenge"),
    # --- Shared tools ---
    path("tools/combat-tracker/", views.combat_tracker, name="combat_tracker"),
    path("tools/entities/", views.entity_browse, name="entity_browse"),
    path("tools/entities/search/", views.entity_search, name="entity_search"),
    # --- Global ---
    path("set-language/<str:lang>", views.set_language, name="set_language"),
    path("health", views.health_check, name="health_check"),
]
