#!/usr/bin/env python3
"""
One-time script to format spell/art entries in markdown files.

Transforms entries like:
    **Spell Name (Рівень 1)**
    Діапазон: 100 футів.
    Description text...

Into:
    #### Spell Name (Рівень 1)
    **Діапазон:** 100 футів.
    Description text...

Also handles arts format:
    **Art Name:**
    Зусилля: Сцена.
    Description text...

Into:
    #### Art Name
    **Зусилля:** Сцена.
    Description text...
"""

import re
import sys
from pathlib import Path

# Known property prefixes (Ukrainian)
PROPERTY_PREFIXES = [
    "Діапазон",
    "Область ефекту",
    "Зона дії",
    "Зона ефекту",
    "Тривалість",
    "Вимагає",
    "Вимога",
    "Впливає на",
    "Ціль",
    "КХ",
    "Обмеження",
    "Зусилля",
    "Дія на Ходу",
    "Основна дія",
    "Миттєва Дія",
    # English equivalents
    "Range",
    "Area",
    "Duration",
    "Requires",
    "Affects",
    "Target",
    "HD",
    "Effort",
    "Restriction",
    "Move Action",
    "Main Action",
    "Instant Action",
]


def is_property_line(line: str) -> bool:
    """Check if line starts with a known property prefix."""
    stripped = line.strip()
    for prefix in PROPERTY_PREFIXES:
        if stripped.startswith(prefix + ":") or stripped.startswith(prefix + "."):
            return True
    # Also match patterns like "Ціль: ..." or single-word properties
    if re.match(r"^[А-ЯA-Z][а-яa-z\s]+:\s", stripped):
        return True
    return False


def format_property_line(line: str) -> str:
    """Format a property line with bold label."""
    stripped = line.strip()
    # Match "Property: value" or "Property. value"
    match = re.match(r"^([А-ЯA-Za-zа-яіїєґІЇЄҐ\s\-]+)([:.])(\s*.*)$", stripped)
    if match:
        label = match.group(1).strip()
        separator = match.group(2)
        value = match.group(3).strip()
        # Use colon always in output
        if value:
            return f"**{label}:** {value}  "
        return f"**{label}.**  "
    return line


def process_spell_block(name: str, content_lines: list[str]) -> list[str]:
    """Process a spell/art block and return formatted lines."""
    result = []

    # Add h4 header
    result.append(f"#### {name}")

    # Process content lines
    in_properties = True

    for line in content_lines:
        stripped = line.strip()

        if not stripped:
            # Empty line - might be transitioning from properties to description
            in_properties = False
            result.append("")
            continue

        if in_properties and is_property_line(stripped):
            # Format as bold property
            result.append(format_property_line(stripped))
        else:
            # Regular description line
            in_properties = False
            result.append(line.rstrip())

    return result


def process_file(filepath: Path) -> str:
    """Process the markdown file and return formatted content."""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for spell pattern: **Name (Рівень X)** or **Name (Level X)**
        spell_match = re.match(r"^\*\*(.+?)\s*\((Рівень|Level)\s*(\d+)\)\*\*\s*$", line.strip())

        # Check for art pattern: **Name:** or **Name (Known Art):**
        art_match = re.match(r"^\*\*(.+?)(?:\s*\([^)]+\))?:\*\*\s*$", line.strip())

        if spell_match:
            # Extract spell name and level
            name = spell_match.group(1).strip()
            level_word = spell_match.group(2)
            level_num = spell_match.group(3)
            full_name = f"{name} ({level_word} {level_num})"

            # Collect content until next heading or spell/art
            i += 1
            content_lines = []
            while i < len(lines):
                next_line = lines[i]
                # Stop at next heading, spell, or art definition
                if (
                    next_line.strip().startswith("#")
                    or re.match(r"^\*\*(.+?)\s*\((Рівень|Level)\s*\d+\)\*\*\s*$", next_line.strip())
                    or re.match(r"^\*\*(.+?)(?:\s*\([^)]+\))?:\*\*\s*$", next_line.strip())
                ):
                    break
                content_lines.append(next_line)
                i += 1

            # Remove trailing empty lines from content
            while content_lines and not content_lines[-1].strip():
                content_lines.pop()

            # Process and add the spell block
            formatted = process_spell_block(full_name, content_lines)
            result.extend(formatted)
            result.append("")  # Add blank line after spell

        elif art_match:
            # Extract art name (remove any parenthetical like "Відоме Мистецтво")
            raw_name = art_match.group(0)
            # Get the full name including parenthetical but without ** and :
            name_match = re.match(r"^\*\*(.+?)\*\*:?\s*$", raw_name.replace(":**", "**"))
            if name_match:
                name = name_match.group(1).strip()
                # Remove trailing colon if present
                name = name.rstrip(":")
            else:
                name = art_match.group(1).strip()

            # Collect content until next heading or spell/art
            i += 1
            content_lines = []
            while i < len(lines):
                next_line = lines[i]
                # Stop at next heading, spell, or art definition
                if (
                    next_line.strip().startswith("#")
                    or re.match(r"^\*\*(.+?)\s*\((Рівень|Level)\s*\d+\)\*\*\s*$", next_line.strip())
                    or re.match(r"^\*\*(.+?)(?:\s*\([^)]+\))?:\*\*\s*$", next_line.strip())
                ):
                    break
                content_lines.append(next_line)
                i += 1

            # Remove trailing empty lines from content
            while content_lines and not content_lines[-1].strip():
                content_lines.pop()

            # Process and add the art block
            formatted = process_spell_block(name, content_lines)
            result.extend(formatted)
            result.append("")  # Add blank line after art

        else:
            # Regular line, keep as-is
            result.append(line)
            i += 1

    # Remove multiple consecutive blank lines
    final_result = []
    prev_blank = False
    for line in result:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        final_result.append(line)
        prev_blank = is_blank

    return "\n".join(final_result)


def main():
    if len(sys.argv) < 2:
        print("Usage: python format_spells.py <input_file> [output_file]")
        print("If output_file is not specified, will modify input file in place.")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    print(f"Processing: {input_path}")

    # Process the file
    formatted_content = process_file(input_path)

    # Write output
    output_path.write_text(formatted_content, encoding="utf-8")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
