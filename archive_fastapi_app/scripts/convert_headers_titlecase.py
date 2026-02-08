"""
Convert markdown headers to Title Case while preserving acronyms.
Processes ## and ### headers in WWN-Lite source files.
"""

import re
from pathlib import Path

# Common acronyms to keep uppercase
ACRONYMS = {
    "HP",
    "SP",
    "DC",
    "NPC",
    "XP",
    "HD",
    "ML",
    "LOS",
    "AC",
    "PC",
    "PCS",
    "NPCS",
    "CR",
    "GM",
    "DM",
    "WWN",
    "DMG",
    "STR",
    "DEX",
    "CON",
    "INT",
    "WIS",
    "CHA",
    "ОД",
    "ОН",
    "НІП",
    "НІПИ",  # Ukrainian acronyms
}

# Words to keep lowercase (articles, prepositions, conjunctions)
LOWERCASE_WORDS = {
    "a",
    "an",
    "the",
    "and",
    "but",
    "or",
    "for",
    "nor",
    "on",
    "at",
    "to",
    "from",
    "by",
    "of",
    "in",
    "with",
    "without",
    "via",
    "per",
    "vs",
    "w/",
    "w/o",
    "&",
    "x",
    "то",
    "та",
    "й",
    "і",
    "в",
    "на",
    "з",
    "для",  # Ukrainian
}


def to_title_case_smart(text: str) -> str:
    """
    Convert text to title case while preserving acronyms and keeping
    certain words lowercase.

    Args:
        text: Header text to convert

    Returns:
        Title-cased text with smart handling
    """
    # Split on spaces and slashes to handle multi-word headers
    words = re.split(r"(\s+|/)", text)
    result = []

    for i, word in enumerate(words):
        # Keep whitespace and separators as-is
        if word.isspace() or word == "/":
            result.append(word)
            continue

        # Remove punctuation for checking
        word_clean = word.strip(".,;:!?()[]{}\"'")

        # Check if it's an acronym (uppercase)
        if word_clean.upper() in ACRONYMS:
            result.append(word)
            continue

        # First word and words after colons/dashes should be capitalized
        is_first = i == 0 or (i > 0 and words[i - 1] in [":", "-", "—"])

        # Keep certain words lowercase unless they're first
        if not is_first and word_clean.lower() in LOWERCASE_WORDS:
            result.append(word.lower())
            continue

        # Handle parenthetical content
        if "(" in word or ")" in word:
            # Preserve case inside parentheses for acronyms
            parts = re.split(r"([()])", word)
            converted_parts = []
            for part in parts:
                if part in "()":
                    converted_parts.append(part)
                elif part.upper() in ACRONYMS:
                    converted_parts.append(part.upper())
                else:
                    converted_parts.append(part.capitalize())
            result.append("".join(converted_parts))
            continue

        # Default: capitalize first letter, lowercase rest
        result.append(word.capitalize())

    return "".join(result)


def convert_headers(content: str) -> str:
    """
    Convert ## and ### headers to title case.

    Args:
        content: Markdown file content

    Returns:
        Content with title-cased headers
    """
    lines = content.split("\n")
    converted_lines = []

    for line in lines:
        # Match ## or ### headers
        header_match = re.match(r"^(#{2,3})\s+(.+)$", line)

        if header_match:
            prefix = header_match.group(1)  # ## or ###
            header_text = header_match.group(2).strip()

            # Convert to title case
            title_cased = to_title_case_smart(header_text)

            converted_lines.append(f"{prefix} {title_cased}")
        else:
            converted_lines.append(line)

    return "\n".join(converted_lines)


def process_file(input_file: Path):
    """
    Process a markdown file to convert headers to title case.

    Args:
        input_file: Path to markdown file
    """
    if not input_file.exists():
        print(f"❌ Error: File '{input_file}' not found")
        return

    print(f"\n📝 Processing: {input_file.name}")

    # Read file
    content = input_file.read_text(encoding="utf-8")

    # Count headers before conversion
    h2_count = len(re.findall(r"^## ", content, re.MULTILINE))
    h3_count = len(re.findall(r"^### ", content, re.MULTILINE))

    # Convert headers
    converted_content = convert_headers(content)

    # Write back
    input_file.write_text(converted_content, encoding="utf-8")

    print(f"   ✅ Converted {h2_count} H2 headers and {h3_count} H3 headers to title case")


def main():
    """Main entry point"""

    # English
    process_file(Path("data/data_sources/wwn-lite-en.md"))

    # Ukrainian
    process_file(Path("data/data_sources/wwn-lite-uk.md"))

    print("\n✨ Done! Headers converted to title case with acronyms preserved.")


if __name__ == "__main__":
    main()
