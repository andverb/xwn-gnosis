"""
Convert bold all-caps items with colons to #### headers.
Targets ONLY: Combat actions, spells, arts, magical weapon/armor properties, elixirs, cursed items, Foci.
Only processes content within specific sections.
"""

import re
from pathlib import Path

# Define target sections where we want to convert bold items to #### headers
TARGET_SECTIONS = {
    # Combat actions
    "Actions & Common Combat Actions",
    # Foci
    "Quick-start Character Generation",  # Contains Foci list
    # Magic traditions (arts and spells)
    "Arcane Tradition of the High Mage",
    "Arcane Tradition of the Druid",
    "Arcane Tradition of the Elementalist",
    "Arcane Tradition of the Necromancer",
    "Arcane Tradition of the Bard (Half Class)",
    "Arcane Tradition of the Cleric (Half Class)",
    "Arcane Tradition of the Monk (Half Class)",
    "Arcane Tradition of the Beastmaster (Half Class)",
    "Arcane Tradition of the Warlock (Half Class)",
    # Equipment with magical properties
    "Armors & Weapons",
    # Elixirs
    "Elixirs",
    # Magical devices (includes cursed items)
    "Magical Devices",
}


def is_in_target_section(section_name: str) -> bool:
    """Check if we're in a section that should be converted."""
    return section_name in TARGET_SECTIONS


def convert_bold_to_h4_in_sections(content: str) -> str:
    """
    Convert bold items to #### headers only in specific sections.

    Patterns handled:
    1. **ALL CAPS TEXT**: content -> #### ALL CAPS TEXT\ncontent
    2. **ALL CAPS (Text)**: content -> #### ALL CAPS (Text)\ncontent
    3. **Title Case Text**: content -> #### Title Case Text\ncontent (for elixirs)
    4. **SPELL NAME LEVEL X**: content -> #### SPELL NAME LEVEL X\ncontent

    Args:
        content: Markdown file content

    Returns:
        Content with #### headers added in target sections
    """
    lines = content.split("\n")
    converted_lines = []
    current_section = None
    in_target_section = False

    for line in lines:
        # Track which ## section we're in
        h2_match = re.match(r"^## (.+)$", line)
        if h2_match:
            current_section = h2_match.group(1).strip()
            in_target_section = is_in_target_section(current_section)
            converted_lines.append(line)
            continue

        # Only process bold items if we're in a target section
        if in_target_section:
            # Pattern 1: Bold all-caps with optional parens (Combat Actions, Arts)
            # **MAKE AN ATTACK (Main Action)**: content
            match1 = re.match(r"^\*\*([A-Z][A-Z\s,&()/-]+)\*\*:\s*(.+)$", line)

            # Pattern 2: Bold title case (Elixirs, Foci)
            # **Anchoring Draught**: content
            match2 = re.match(r"^\*\*([A-Z][a-zA-Z\s,&()/-]+)\*\*:\s*(.+)$", line)

            # Pattern 3: Bold with LEVEL (Spells)
            # **SPELL NAME LEVEL 1**: content
            match3 = re.match(r"^\*\*([A-Z][A-Z\s,&()/-]+LEVEL\s+\d+)\*\*:\s*(.+)$", line)

            if match1 or match2 or match3:
                match = match1 or match2 or match3
                header_text = match.group(1).strip()
                content_text = match.group(2).strip()

                # Convert to #### header
                converted_lines.append(f"#### {header_text}")
                converted_lines.append(content_text)
            else:
                converted_lines.append(line)
        else:
            converted_lines.append(line)

    return "\n".join(converted_lines)


def process_file(input_file: Path):
    """
    Process a markdown file to convert bold items to #### headers in target sections.

    Args:
        input_file: Path to markdown file
    """
    if not input_file.exists():
        print(f"❌ Error: File '{input_file}' not found")
        return

    print(f"\n📝 Processing: {input_file.name}")

    # Read file
    content = input_file.read_text(encoding="utf-8")

    # Convert
    converted_content = convert_bold_to_h4_in_sections(content)

    # Count how many #### headers we added
    original_h4_count = len(re.findall(r"^#### ", content, re.MULTILINE))
    new_h4_count = len(re.findall(r"^#### ", converted_content, re.MULTILINE))
    added_count = new_h4_count - original_h4_count

    # Write back
    input_file.write_text(converted_content, encoding="utf-8")

    print(f"   ✅ Converted {added_count} bold items to #### headers")
    print(f"   📊 Total #### headers in file: {new_h4_count}")


def main():
    """Main entry point"""

    # English
    process_file(Path("data/data_sources/wwn-lite-en.md"))

    # Ukrainian
    process_file(Path("data/data_sources/wwn-lite-uk.md"))

    print("\n✨ Done! Bold items converted to #### headers in target sections.")


if __name__ == "__main__":
    main()
