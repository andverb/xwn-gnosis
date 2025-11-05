"""
Tests for utility functions.

This module tests utility functions in app/utils.py.
"""

from app import utils


class TestGenerateSlug:
    """Test slug generation utility."""

    def test_basic_slug_generation(self):
        """Test basic slug generation from text."""
        assert utils.generate_slug("Test Rule") == "test-rule"
        assert utils.generate_slug("Fireball Spell") == "fireball-spell"

    def test_slug_handles_special_characters(self):
        """Test that special characters are removed or converted."""
        assert utils.generate_slug("Test & Rule") == "test-rule"
        assert utils.generate_slug("Test@Rule#123") == "test-rule-123"

    def test_slug_handles_unicode(self):
        """Test that Unicode characters are transliterated."""
        # Cyrillic should be transliterated
        slug = utils.generate_slug("Куля вогню")
        assert slug  # Should produce some slug
        assert " " not in slug
        assert slug.islower()

    def test_slug_handles_multiple_spaces(self):
        """Test that multiple spaces are collapsed."""
        assert utils.generate_slug("Test    Rule    Name") == "test-rule-name"

    def test_slug_handles_leading_trailing_spaces(self):
        """Test that leading/trailing spaces are removed."""
        assert utils.generate_slug("  Test Rule  ") == "test-rule"

    def test_slug_empty_string(self):
        """Test slug generation with empty string."""
        result = utils.generate_slug("")
        assert result == "" or result is None


class TestRenderMarkdown:
    """Test markdown rendering utility."""

    def test_basic_markdown_rendering(self):
        """Test basic markdown to HTML conversion."""
        html = utils.render_markdown("**Bold text**")
        assert "<strong>Bold text</strong>" in html

    def test_markdown_paragraph_tags(self):
        """Test that paragraphs are wrapped in <p> tags."""
        html = utils.render_markdown("Test paragraph")
        assert "<p>" in html
        assert "</p>" in html

    def test_markdown_links(self):
        """Test markdown link rendering."""
        html = utils.render_markdown("[Link text](https://example.com)")
        assert '<a href="https://example.com"' in html
        assert "Link text" in html

    def test_markdown_lists(self):
        """Test markdown list rendering."""
        markdown = """
- Item 1
- Item 2
- Item 3
"""
        html = utils.render_markdown(markdown)
        assert "<ul>" in html
        assert "<li>Item 1</li>" in html
        assert "<li>Item 2</li>" in html

    def test_markdown_tables(self):
        """Test markdown table rendering with tables extension."""
        markdown = """
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
"""
        html = utils.render_markdown(markdown)
        assert "<table>" in html
        assert "<thead>" in html
        assert "<tbody>" in html

    def test_markdown_code_blocks(self):
        """Test code block rendering."""
        markdown = "```\ncode here\n```"
        html = utils.render_markdown(markdown)
        assert "<code>" in html

    def test_markdown_sanitization(self):
        """Test that dangerous HTML is sanitized."""
        # Script tags should be removed (bleach strips them)
        html = utils.render_markdown("<script>alert('xss')</script>")
        assert "<script>" not in html.lower()
        assert "</script>" not in html.lower()
        # The content may remain, but the dangerous tags are gone

    def test_markdown_allows_safe_tags(self):
        """Test that safe HTML tags are preserved."""
        # Strong and em should be allowed
        html = utils.render_markdown("<strong>Bold</strong> and <em>italic</em>")
        assert "<strong>" in html
        assert "<em>" in html

    def test_markdown_empty_string(self):
        """Test rendering empty markdown."""
        html = utils.render_markdown("")
        assert html == "" or html.strip() == ""

    def test_markdown_none_value(self):
        """Test rendering None value."""
        # Should handle None gracefully
        html = utils.render_markdown(None)
        assert html == "" or html is None
