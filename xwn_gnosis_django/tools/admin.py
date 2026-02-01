from django.contrib import admin

from .models import TypoSuggestion


@admin.register(TypoSuggestion)
class TypoSuggestionAdmin(admin.ModelAdmin):
    list_display = ["short_text", "section", "page", "reviewed", "created_at"]
    list_filter = ["reviewed", "section", "created_at"]
    search_fields = ["selected_text", "suggested_correction", "section", "page"]
    readonly_fields = ["created_at", "page_url"]
    list_editable = ["reviewed"]
    ordering = ["-created_at"]

    fieldsets = [
        (None, {"fields": ["section", "page", "page_url"]}),
        ("Content", {"fields": ["selected_text", "context", "suggested_correction"]}),
        ("Status", {"fields": ["reviewed", "created_at"]}),
    ]

    def short_text(self, obj):
        return obj.selected_text[:50] + "..." if len(obj.selected_text) > 50 else obj.selected_text

    short_text.short_description = "Selected Text"
