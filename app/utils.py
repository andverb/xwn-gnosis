import re
from dataclasses import dataclass
from pathlib import Path

import bleach
import markdown
from slugify import slugify


def generate_slug(text: str, max_length: int = 150) -> str:
    return slugify(text, max_length=max_length)


def render_markdown(text: str) -> str:
    """Convert markdown to safe HTML - optimized for tables and lists"""
    if not text:
        return ""

    # Render markdown with essential extensions
    html = markdown.markdown(
        text,
        extensions=[
            "tables",  # GitHub-style tables
            "nl2br",  # Convert newlines to <br>
            "sane_lists",  # Better list handling
        ],
    )

    # Sanitize HTML to prevent XSS attacks
    allowed_tags = [
        "p",
        "br",
        "strong",
        "em",
        "u",
        "s",
        "code",
        "pre",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "ul",
        "ol",
        "li",
        "blockquote",
        "hr",
        "table",
        "thead",
        "tbody",
        "tr",
        "th",
        "td",
        "a",
        "div",
        "span",
    ]

    allowed_attrs = {
        "*": ["class"],
        "a": ["href", "title"],
        "th": ["align"],
        "td": ["align"],
    }
    html = re.sub(r"<table>", '<table role="grid">', html)

    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)


# Compendium markdown parsing utilities


@dataclass
class Chapter:
    """Represents a chapter in the compendium."""

    id: str  # URL-safe slug
    title: str  # Original title
    level: int  # Header level (1 or 2)
    content: str  # Markdown content
    html: str  # Rendered HTML
    order: int  # Position in document


@dataclass
class Compendium:
    """Represents a parsed compendium document."""

    title: str
    chapters: list[Chapter]
    toc: list[dict]  # Hierarchical table of contents


def slugify_chapter(text: str) -> str:
    """Convert text to URL-safe slug for chapters."""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip("-")


def parse_markdown_compendium(file_path: Path) -> Compendium:
    """
    Parse a markdown file into chapters based on H2 headers.

    Args:
        file_path: Path to markdown file

    Returns:
        Compendium object with parsed chapters
    """
    content = file_path.read_text(encoding="utf-8")

    # Extract title (first H1)
    title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Compendium"

    # Split by H2 headers
    # Pattern: ## TITLE followed by content until next ## or end
    chapter_pattern = r"^## (.+?)$\n((?:(?!^##? ).*\n?)*)"
    matches = re.finditer(chapter_pattern, content, re.MULTILINE)

    chapters = []
    md = markdown.Markdown(extensions=["tables", "nl2br", "fenced_code"])

    for order, match in enumerate(matches):
        chapter_title = match.group(1).strip()
        chapter_content = match.group(2).strip()
        chapter_id = slugify_chapter(chapter_title)

        # Render content to HTML
        html = md.convert(chapter_content)
        md.reset()  # Reset for next chapter

        chapters.append(
            Chapter(
                id=chapter_id,
                title=chapter_title,
                level=2,
                content=chapter_content,
                html=html,
                order=order,
            )
        )

    # Build table of contents
    toc = [{"id": ch.id, "title": ch.title, "level": ch.level} for ch in chapters]

    return Compendium(title=title, chapters=chapters, toc=toc)


def get_chapter_by_id(compendium: Compendium, chapter_id: str) -> Chapter | None:
    """Get a chapter by its ID."""
    return next((ch for ch in compendium.chapters if ch.id == chapter_id), None)


def get_navigation_info(compendium: Compendium, current_id: str) -> dict:
    """
    Get previous/next chapter info for navigation.

    Returns:
        Dict with 'prev' and 'next' Chapter objects (or None)
    """
    current_chapter = get_chapter_by_id(compendium, current_id)
    if not current_chapter:
        return {"prev": None, "next": None}

    current_order = current_chapter.order
    prev_chapter = next((ch for ch in compendium.chapters if ch.order == current_order - 1), None)
    next_chapter = next((ch for ch in compendium.chapters if ch.order == current_order + 1), None)

    return {"prev": prev_chapter, "next": next_chapter}
