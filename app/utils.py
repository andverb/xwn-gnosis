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

    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)
