"""
URL configuration for the Django project.

include() is used to reference app-specific URL configurations.
This keeps the project modular - each app defines its own URLs.

The empty string "" means these URLs are at the root level (no prefix).
If you used path("tools/", include(...)), URLs would be /tools/cheatsheets/...
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin interface
    path("admin/", admin.site.urls),
    # Include all URLs from the tools app at the root level
    # This means /cheatsheets/wwn-combat, not /tools/cheatsheets/wwn-combat
    path("", include("tools.urls")),
]
