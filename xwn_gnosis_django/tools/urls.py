"""
URL configuration for tools app.

Django URL patterns explained:
- path("url-pattern/", view_function, name="name")
- The 'name' is used in templates: {% url 'app_name:name' %}
- <str:lang> captures a string from URL and passes to view as 'lang' parameter
- app_name creates a namespace to avoid conflicts between apps
"""

from django.urls import path

from . import views

# Namespace for this app - use in templates as {% url 'tools:view_name' %}
app_name = "tools"

urlpatterns = [
    # Home page - defaults to combat cheatsheet
    path("", views.combat_cheatsheet, name="home"),
    # Cheatsheets
    path("cheatsheets/wwn-combat", views.combat_cheatsheet, name="combat_cheatsheet"),
    path("cheatsheets/wwn-encounter", views.encounter_cheatsheet, name="encounter_cheatsheet"),
    # htmx endpoint for challenge calculator (POST only)
    path("cheatsheets/calculate-challenge", views.calculate_challenge, name="calculate_challenge"),
    # Combat tracker
    path("combat-tracker", views.combat_tracker, name="combat_tracker"),
    # Entity browser
    path("entities/", views.entity_browse, name="entity_browse"),
    path("entities/search/", views.entity_search, name="entity_search"),
    # Compendium
    path("compendium/", views.compendium_index, name="compendium_index"),
    path("compendium/suggest-typo/", views.suggest_typo, name="suggest_typo"),
    path("compendium/<str:section>/", views.compendium_section, name="compendium_section"),
    path("compendium/<str:section>/<str:page>/", views.compendium_page, name="compendium_page"),
    # Language switcher - <str:lang> captures "en" or "uk" from URL
    path("set-language/<str:lang>", views.set_language, name="set_language"),
    # Health check for deployment monitoring
    path("health", views.health_check, name="health_check"),
]
