"""
Convert bold all-caps items with colons to #### headers.
Targets: Combat actions, spells, arts, magical weapon properties, elixirs, cursed items.
"""

import re
from pathlib import Path


def convert_bold_to_h4(content: str) -> str:
    """
    Convert bold all-caps items to #### headers.

    Pattern: **ALL CAPS TEXT**: content
    Result:  #### Title Case Text\ncontent

    Args:
        content: Markdown file content

    Returns:
        Content with #### headers added
    """
    lines = content.split("\n")
    converted_lines = []

    for line in lines:
        # Match bold all-caps items with colons
        # Pattern: **SOME TEXT (with parens, slashes, etc.)**: rest of content
        match = re.match(r"^\*\*([A-Z][A-Z\s,&()/-]+)\*\*:\s*(.+)$", line)

        if match:
            header_text = match.group(1).strip()
            content_text = match.group(2).strip()

            # Convert to #### header
            converted_lines.append(f"#### {header_text}")
            converted_lines.append(content_text)
        else:
            converted_lines.append(line)

    return "\n".join(converted_lines)


def process_file(input_file: Path):
    """
    Process a markdown file to convert bold items to #### headers.

    Args:
        input_file: Path to markdown file
    """
    if not input_file.exists():
        print(f"❌ Error: File '{input_file}' not found")
        return

    print(f"\n📝 Processing: {input_file.name}")

    # Read file
    content = input_file.read_text(encoding="utf-8")

    # Count conversions
    bold_items = len(re.findall(r"^\*\*([A-Z][A-Z\s,&()/-]+)\*\*:", content, re.MULTILINE))

    # Convert
    converted_content = convert_bold_to_h4(content)

    # Write back
    input_file.write_text(converted_content, encoding="utf-8")

    print(f"   ✅ Converted {bold_items} bold items to #### headers")


def main():
    """Main entry point"""

    # English
    process_file(Path("data/data_sources/wwn-lite-en.md"))

    # Ukrainian
    process_file(Path("data/data_sources/wwn-lite-uk.md"))

    print("\n✨ Done! Bold items converted to #### headers.")


if __name__ == "__main__":
    main()
