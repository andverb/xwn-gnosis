"""
Build search index and navigation structure from markdown files.

Run: python manage.py build_content_index

Generates:
- static/data/search_index_{lang}.json - For lunr.js search
- static/data/nav_{lang}.json - For sidebar navigation
"""

import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

# Rules content directory
RULES_DIR = Path(settings.BASE_DIR).parent / "docs" / "wwn-lite"

# Output directory for generated JSON files
OUTPUT_DIR = Path(settings.BASE_DIR) / "static" / "data"

# Section metadata (matching views.py)
SECTION_META = {
    "basics": {
        "title": {"en": "Basics", "uk": "Основи"},
        "icon": "bi bi-star",
    },
    "survival": {
        "title": {"en": "Survival", "uk": "Виживання"},
        "icon": "bi bi-heart-pulse",
    },
    "combat": {
        "title": {"en": "Combat", "uk": "Бій"},
        "icon": "bi bi-shield",
    },
    "equipment": {
        "title": {"en": "Equipment", "uk": "Спорядження"},
        "icon": "bi bi-backpack",
    },
    "magic": {
        "title": {"en": "Magic", "uk": "Магія"},
        "icon": "bi bi-magic",
    },
    "character": {
        "title": {"en": "Character", "uk": "Персонаж"},
        "icon": "bi bi-person",
    },
    "campaign": {
        "title": {"en": "Campaign", "uk": "Кампанія"},
        "icon": "bi bi-map",
    },
    "reference": {
        "title": {"en": "Reference", "uk": "Довідник"},
        "icon": "bi bi-bookmark",
    },
}

# Order of sections for navigation
SECTION_ORDER = [
    "basics",
    "survival",
    "combat",
    "equipment",
    "magic",
    "character",
    "campaign",
    "reference",
]


class Command(BaseCommand):
    help = "Build search index and navigation from markdown files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--lang",
            type=str,
            help="Build for specific language only (en or uk)",
        )

    def handle(self, *args, **options):
        languages = [options["lang"]] if options.get("lang") else ["en", "uk"]

        # Ensure output directory exists
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        for lang in languages:
            self.stdout.write(f"Building index for {lang}...")

            search_docs, nav_structure = self.scan_content(lang)

            # Write search index (MkDocs format)
            search_file = OUTPUT_DIR / f"search_index_{lang}.json"
            self.write_json(
                search_file,
                {
                    "config": {"lang": [lang], "separator": r"[\s\-]+"},
                    "docs": search_docs,
                },
            )
            self.stdout.write(self.style.SUCCESS(f"  -> {search_file.name}: {len(search_docs)} documents"))

            # Write navigation structure
            nav_file = OUTPUT_DIR / f"nav_{lang}.json"
            self.write_json(nav_file, nav_structure)
            total_pages = sum(len(s.get("pages", [])) for s in nav_structure.get("sections", {}).values())
            self.stdout.write(self.style.SUCCESS(f"  -> {nav_file.name}: {total_pages} pages"))

        self.stdout.write(self.style.SUCCESS("Done!"))

    def write_json(self, path: Path, data: dict):
        """Write JSON file with pretty formatting."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def scan_content(self, lang: str) -> tuple[list[dict], dict]:
        """
        Scan markdown files and build search documents + navigation.

        Returns:
            (search_docs, nav_structure)
        """
        search_docs = []
        nav_structure = {"sections": {}}

        lang_dir = RULES_DIR / lang
        if not lang_dir.exists():
            self.stdout.write(self.style.WARNING(f"  Directory not found: {lang_dir}"))
            return search_docs, nav_structure

        # Process each section in order
        for section in SECTION_ORDER:
            section_dir = lang_dir / section
            if not section_dir.exists():
                continue

            section_meta = SECTION_META.get(section, {})
            section_title = section_meta.get("title", {}).get(lang, section.title())
            section_icon = section_meta.get("icon", "bi bi-folder")

            nav_structure["sections"][section] = {
                "title": section_title,
                "icon": section_icon,
                "pages": [],
            }

            # Process all markdown files in section
            for md_file in sorted(section_dir.glob("*.md")):
                slug = md_file.stem
                content = md_file.read_text(encoding="utf-8")

                # Extract page title from first H1 or H3
                page_title = self.extract_title(content, slug)

                # Add to navigation
                nav_structure["sections"][section]["pages"].append({"slug": slug, "title": page_title})

                # Add page-level search document
                location = f"{section}/{slug}"
                text = self.clean_text(content)
                search_docs.append(
                    {
                        "location": location,
                        "title": page_title,
                        "text": text[:5000],  # Limit text length for index size
                    }
                )

                # Index individual headings for precise search results
                heading_docs = self.extract_headings(content, location)
                search_docs.extend(heading_docs)

        return search_docs, nav_structure

    def extract_title(self, content: str, fallback_slug: str) -> str:
        """
        Extract page title from markdown content.

        Only uses H1 (# Title) as page title. Falls back to humanized filename
        if no H1 is found, since many pages start with H2/H3 content headings.
        """
        lines = content.split("\n")
        for line in lines[:10]:  # Check first 10 lines
            stripped = line.strip()
            # Only match H1 (single #) as page title
            if stripped.startswith("# ") and not stripped.startswith("## "):
                return stripped[2:].strip()
        # Fallback to humanized slug (delving -> Delving, healing-hazards -> Healing Hazards)
        return fallback_slug.replace("-", " ").title()

    def clean_text(self, content: str) -> str:
        """Remove markdown formatting for search indexing."""
        text = content

        # Remove code blocks
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"`[^`]+`", "", text)

        # Remove markdown formatting
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # Bold
        text = re.sub(r"\*([^*]+)\*", r"\1", text)  # Italic
        text = re.sub(r"__([^_]+)__", r"\1", text)  # Bold
        text = re.sub(r"_([^_]+)_", r"\1", text)  # Italic

        # Remove links, keep text
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

        # Remove headers markers
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)

        # Remove table formatting
        text = re.sub(r"\|", " ", text)
        text = re.sub(r"-{3,}", "", text)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def extract_headings(self, content: str, base_location: str) -> list[dict]:
        """
        Extract H2, H3, H4 headings as separate search documents.

        This allows searching for specific sections within a page.
        """
        docs = []

        # Split content by headings
        lines = content.split("\n")
        current_heading = None
        current_text = []

        for line in lines:
            # Match ## or ### or #### headings
            heading_match = re.match(r"^(#{2,4})\s+(.+)$", line.strip())

            if heading_match:
                # Save previous heading's text
                if current_heading:
                    text = self.clean_text("\n".join(current_text))
                    if text:  # Only add if there's content
                        docs.append(
                            {
                                "location": f"{base_location}#{self.slugify(current_heading)}",
                                "title": current_heading,
                                "text": text[:2000],  # Limit section text
                            }
                        )

                # Start new heading
                current_heading = heading_match.group(2).strip()
                current_text = []
            elif current_heading:
                current_text.append(line)

        # Don't forget the last heading
        if current_heading and current_text:
            text = self.clean_text("\n".join(current_text))
            if text:
                docs.append(
                    {
                        "location": f"{base_location}#{self.slugify(current_heading)}",
                        "title": current_heading,
                        "text": text[:2000],
                    }
                )

        return docs

    def slugify(self, text: str) -> str:
        """Convert heading text to URL-safe slug."""
        # Lowercase and replace spaces
        slug = text.lower().strip()
        # Remove special characters, keep alphanumeric, spaces, and hyphens
        slug = re.sub(r"[^\w\s-]", "", slug)
        # Replace spaces with hyphens
        slug = re.sub(r"[\s_]+", "-", slug)
        # Remove multiple hyphens
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")
