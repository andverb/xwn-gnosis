from django.db import models


class TypoSuggestion(models.Model):
    """User-submitted typo/correction suggestions for compendium pages."""

    section = models.CharField(max_length=100)
    page = models.CharField(max_length=100)
    selected_text = models.TextField()
    context = models.TextField(blank=True, help_text="Surrounding text for context (~50 chars)")
    suggested_correction = models.TextField(blank=True)
    page_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Typo in {self.section}/{self.page}: {self.selected_text[:50]}..."
