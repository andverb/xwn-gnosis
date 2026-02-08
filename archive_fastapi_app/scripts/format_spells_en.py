#!/usr/bin/env python3
"""
One-time script to format spell entries in English markdown files.

Transforms entries like:
    **SEE MAGIC LEVEL 1**: Lasts 15 mins x Caster level. Description...

Into:
    #### See Magic (Level 1)
    **Duration:** 15 mins × Caster level.
    Description...

Also handles arts that are already h4 but need content split:
    #### COUNTER MAGIC:
    Effort: Day. Instant Action. Description...

Into:
    #### Counter Magic
    **Effort:** Day.
    **Instant Action.**
    Description...
"""

import re
import sys
from pathlib import Path


def title_case_spell(name: str) -> str:
    """Convert SPELL NAME to Title Case Spell Name."""
    # Handle special abbreviations
    words = name.split()
    result = []
    for word in words:
        # Keep certain words lowercase (unless first word)
        lower_words = {"of", "the", "a", "an", "and", "or", "for", "to", "in", "on", "at", "by", "vs"}
        if word.lower() in lower_words and result:
            result.append(word.lower())
        else:
            result.append(word.capitalize())
    return " ".join(result)


def extract_properties_from_description(text: str) -> tuple[list[str], str]:
    """
    Extract property-like prefixes from description text.
    Returns (property_lines, remaining_description)
    """
    # Known property patterns at start of description
    property_patterns = [
        r"^(Lasts?\s+[^.]+\.)\s*",
        r"^(Range:\s*[^.]+\.)\s*",
        r"^(AoE:\s*[^.]+\.)\s*",
        r"^(Requires?\s+[^.]+\.)\s*",
        r"^(Affects?\s+[^.]+\.)\s*",
        r"^(Duration:\s*[^.]+\.)\s*",
        r"^(Limit:\s*[^.]+\.)\s*",
        r"^(Effort:\s*[^.]+\.)\s*",
        r"^(Instant Action\.)\s*",
        r"^(On Turn Action\.)\s*",
        r"^(Main Action\.)\s*",
    ]

    properties = []
    remaining = text.strip()

    # Keep extracting properties from the start
    found = True
    while found and remaining:
        found = False
        for pattern in property_patterns:
            match = re.match(pattern, remaining, re.IGNORECASE)
            if match:
                prop = match.group(1).strip()
                properties.append(prop)
                remaining = remaining[match.end() :].strip()
                found = True
                break

    return properties, remaining


def format_property(prop: str) -> str:
    """Format a property string with bold label and trailing spaces for md newline."""
    # Handle "Lasts X" -> "**Duration:** X  " (two trailing spaces for md newline)
    if prop.lower().startswith("lasts "):
        value = prop[6:].rstrip(".")
        return f"**Duration:** {value}  "

    # Handle "Property: value" patterns
    match = re.match(r"^([A-Za-z\s]+):\s*(.+)$", prop)
    if match:
        label = match.group(1).strip()
        value = match.group(2).strip().rstrip(".")
        return f"**{label}:** {value}  "

    # Handle standalone actions like "Instant Action."
    if prop.rstrip(".") in ["Instant Action", "On Turn Action", "Main Action"]:
        return f"**{prop.rstrip('.')}**  "

    # Handle "Requires X" -> "**Requires:** X"
    if prop.lower().startswith("requires "):
        value = prop[9:].rstrip(".")
        return f"**Requires:** {value}  "

    if prop.lower().startswith("affects "):
        value = prop[8:].rstrip(".")
        return f"**Affects:** {value}  "

    return prop


def process_spell_line(line: str) -> list[str]:
    """
    Process a spell line like:
    **SEE MAGIC LEVEL 1**: Description...

    Returns formatted lines.
    """
    # Match pattern: **SPELL NAME LEVEL X**: description
    match = re.match(r"^\*\*([A-Z][A-Z\s\']+?)\s+LEVEL\s+(\d+)\*\*:\s*(.+)$", line.strip())
    if not match:
        return [line]

    spell_name = match.group(1).strip()
    level = match.group(2)
    description = match.group(3).strip()

    # Convert to title case
    formatted_name = title_case_spell(spell_name)

    # Extract properties from description
    properties, remaining_desc = extract_properties_from_description(description)

    # Build output
    result = [f"#### {formatted_name} (Level {level})"]

    for prop in properties:
        result.append(format_property(prop))

    if remaining_desc:
        result.append(remaining_desc)

    return result


def process_art_header(current_line: str, next_line: str | None) -> tuple[list[str], bool]:
    """
    Process an art header like:
    #### COUNTER MAGIC:
    Effort: Day. Instant Action. Description...

    Returns (formatted_lines, consumed_next_line)
    """
    # Check if it's an h4 with content on next line
    header_match = re.match(r"^####\s+([A-Z][A-Z\s\']+):?\s*$", current_line.strip())
    if not header_match:
        return [current_line], False

    art_name = header_match.group(1).strip().rstrip(":")
    formatted_name = title_case_spell(art_name)

    result = [f"#### {formatted_name}"]

    # Check if next line has content
    if next_line and next_line.strip() and not next_line.strip().startswith("#"):
        # Extract properties from the content line
        properties, remaining_desc = extract_properties_from_description(next_line.strip())

        for prop in properties:
            result.append(format_property(prop))

        if remaining_desc:
            result.append(remaining_desc)

        return result, True

    return result, False


def process_bold_art_line(line: str) -> list[str]:
    """
    Process an art line like:
    **Arboreal Agility**: You can climb trees... Effort: Day. On Turn action. Description...

    Returns formatted lines.
    """
    # Match pattern: **Art Name**: description
    match = re.match(r"^\*\*([^*]+)\*\*:\s*(.+)$", line.strip())
    if not match:
        return [line]

    art_name = match.group(1).strip()
    description = match.group(2).strip()

    # Convert to title case if needed
    formatted_name = title_case_spell(art_name) if art_name.isupper() else art_name

    # Extract properties from description - they can appear anywhere in the text
    # For arts, properties like "Effort: X" can be in the middle of text
    properties = []
    remaining_parts = []

    # Split by sentences and identify properties
    # Look for patterns like "Effort: Day." or "Range: Melee." anywhere
    sentences = re.split(r"(?<=[.!?])\s+", description)

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # Check if this sentence is a property
        is_property = False

        # Handle "Also, Effort: X." pattern - extract Effort and keep "Also," with remaining
        also_effort_match = re.match(r"^Also,?\s*Effort:\s*([^.]+)\.?$", sentence, re.IGNORECASE)
        if also_effort_match:
            properties.append(f"**Effort:** {also_effort_match.group(1).rstrip('.')}  ")
            is_property = True
            continue

        # Effort pattern
        effort_match = re.match(r"^Effort:\s*([^.]+)\.?$", sentence, re.IGNORECASE)
        if effort_match:
            properties.append(f"**Effort:** {effort_match.group(1).rstrip('.')}  ")
            is_property = True
            continue

        # Range pattern
        range_match = re.match(r"^Range:\s*([^.]+)\.?$", sentence, re.IGNORECASE)
        if range_match:
            properties.append(f"**Range:** {range_match.group(1).rstrip('.')}  ")
            is_property = True
            continue

        # Lasts/Duration pattern
        lasts_match = re.match(r"^Lasts?\s+([^.]+)\.?$", sentence, re.IGNORECASE)
        if lasts_match:
            properties.append(f"**Duration:** {lasts_match.group(1).rstrip('.')}  ")
            is_property = True
            continue

        # Limit pattern
        limit_match = re.match(r"^Limit:\s*([^.]+)\.?$", sentence, re.IGNORECASE)
        if limit_match:
            properties.append(f"**Limit:** {limit_match.group(1).rstrip('.')}  ")
            is_property = True
            continue

        # Action type patterns
        action_patterns = ["On Turn Action", "On Turn action", "Main Action", "Instant Action"]
        for action in action_patterns:
            if sentence.rstrip(".").lower() == action.lower():
                properties.append(f"**{action.title()}**  ")
                is_property = True
                break

        if not is_property:
            remaining_parts.append(sentence)

    # Build output
    result = [f"#### {formatted_name}"]
    result.extend(properties)

    if remaining_parts:
        result.append(" ".join(remaining_parts))

    return result


def process_file(filepath: Path) -> str:
    """Process the markdown file and return formatted content."""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    result = []
    i = 0

    # Track if we're in a spell section
    in_spell_section = False

    while i < len(lines):
        line = lines[i]
        next_line = lines[i + 1] if i + 1 < len(lines) else None

        # Check for spell section headers
        if re.match(r"^###\s+Spells\s+of", line, re.IGNORECASE):
            in_spell_section = True
            result.append(line)
            i += 1
            continue

        # Check for other h3 headers (exit spell section)
        if line.strip().startswith("### ") and not re.match(r"^###\s+Spells\s+of", line, re.IGNORECASE):
            in_spell_section = False

        # Check for spell pattern: **SPELL NAME LEVEL X**: description
        spell_match = re.match(r"^\*\*([A-Z][A-Z\s\']+?)\s+LEVEL\s+(\d+)\*\*:\s*(.+)$", line.strip())
        if spell_match:
            formatted = process_spell_line(line)
            result.extend(formatted)
            result.append("")  # Add blank line after spell
            i += 1
            continue

        # Check for art h4 headers (ALL CAPS with optional colon)
        art_match = re.match(r"^####\s+([A-Z][A-Z\s\']+):?\s*$", line.strip())
        if art_match:
            formatted, consumed = process_art_header(line, next_line)
            result.extend(formatted)
            result.append("")  # Add blank line after art
            if consumed:
                i += 2
            else:
                i += 1
            continue

        # Check for bold art pattern: **Art Name**: description (not a spell with LEVEL in name)
        bold_art_match = re.match(r"^\*\*([^*]+)\*\*:\s*(.+)$", line.strip())
        if bold_art_match and "LEVEL" not in bold_art_match.group(1).upper():
            formatted = process_bold_art_line(line)
            result.extend(formatted)
            result.append("")  # Add blank line after art
            i += 1
            continue

        # Regular line
        result.append(line)
        i += 1

    # Clean up multiple consecutive blank lines
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
        print("Usage: python format_spells_en.py <input_file> [output_file]")
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
