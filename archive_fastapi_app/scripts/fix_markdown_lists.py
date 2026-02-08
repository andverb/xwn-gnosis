"""
Fix markdown list formatting in source files.
Adds blank line before lists when they follow a paragraph.
"""

import re
from pathlib import Path


def fix_list_formatting(content: str) -> str:
    """
    Add blank lines before list items when needed.

    A list item (starting with '-', '*', or digit) needs a blank line before it
    if the previous line is non-empty and isn't already a list item.

    Args:
        content: Markdown content

    Returns:
        Fixed markdown content
    """
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # Check if current line is a list item
        is_list_item = bool(re.match(r"^(\s*)[-*]|\d+\.", line.strip()))

        # Check if we need to add a blank line before this list item
        if is_list_item and i > 0:
            prev_line = lines[i - 1].strip()

            # Need blank line if:
            # - Previous line is not empty
            # - Previous line is not a list item
            # - Previous line is not a header
            # - We haven't already added a blank line
            prev_is_list = bool(re.match(r"^[-*]|\d+\.", prev_line))
            prev_is_header = prev_line.startswith("#")
            prev_is_empty = prev_line == ""

            if prev_line and not prev_is_list and not prev_is_header and not prev_is_empty:
                # Add blank line before list item
                fixed_lines.append("")

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def process_file(input_file: Path, output_file: Path = None):
    """
    Process a markdown file to fix list formatting.

    Args:
        input_file: Path to input markdown file
        output_file: Path to output file (defaults to overwriting input)
    """
    if not input_file.exists():
        print(f"❌ Error: File '{input_file}' not found")
        return

    if output_file is None:
        output_file = input_file

    print(f"\n📝 Processing: {input_file.name}")

    # Read file
    content = input_file.read_text(encoding="utf-8")
    original_lines = len(content.split("\n"))

    # Fix formatting
    fixed_content = fix_list_formatting(content)
    fixed_lines = len(fixed_content.split("\n"))

    # Write output
    output_file.write_text(fixed_content, encoding="utf-8")

    lines_added = fixed_lines - original_lines
    print(f"   ✅ Fixed! Added {lines_added} blank lines")
    print(f"   📊 Before: {original_lines} lines → After: {fixed_lines} lines")


def main():
    """Main entry point"""

    # English
    process_file(Path("data/data_sources/wwn-lite-en.md"))

    # Ukrainian
    process_file(Path("data/data_sources/wwn-lite-uk.md"))


if __name__ == "__main__":
    main()
