"""
Revert #### headers back to bold format with colons.
Reverses the changes made by add_h4_headers.py
"""

import re
from pathlib import Path


def revert_h4_to_bold(content: str) -> str:
    """
    Convert #### headers back to bold all-caps format with colons.

    Pattern: #### HEADER TEXT
             content on next line
    Result:  **HEADER TEXT**: content on same line

    Args:
        content: Markdown file content

    Returns:
        Content with #### headers reverted to bold format
    """
    lines = content.split("\n")
    reverted_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Match #### headers
        match = re.match(r"^#### (.+)$", line)

        if match:
            header_text = match.group(1).strip()

            # Check if next line exists and is not empty
            if i + 1 < len(lines) and lines[i + 1].strip():
                content_text = lines[i + 1].strip()
                # Combine into bold format
                reverted_lines.append(f"**{header_text}**: {content_text}")
                i += 2  # Skip the next line since we consumed it
                continue
            # No content on next line, just convert header
            reverted_lines.append(f"**{header_text}**:")
            i += 1
            continue

        reverted_lines.append(line)
        i += 1

    return "\n".join(reverted_lines)


def process_file(input_file: Path):
    """
    Process a markdown file to revert #### headers to bold format.

    Args:
        input_file: Path to markdown file
    """
    if not input_file.exists():
        print(f"❌ Error: File '{input_file}' not found")
        return

    print(f"\n📝 Processing: {input_file.name}")

    # Read file
    content = input_file.read_text(encoding="utf-8")

    # Count #### headers
    h4_count = len(re.findall(r"^#### ", content, re.MULTILINE))

    # Revert
    reverted_content = revert_h4_to_bold(content)

    # Write back
    input_file.write_text(reverted_content, encoding="utf-8")

    print(f"   ✅ Reverted {h4_count} #### headers to bold format")


def main():
    """Main entry point"""

    # English
    process_file(Path("data/data_sources/wwn-lite-en.md"))

    # Ukrainian
    process_file(Path("data/data_sources/wwn-lite-uk.md"))

    print("\n✨ Done! #### headers reverted to bold format.")


if __name__ == "__main__":
    main()
