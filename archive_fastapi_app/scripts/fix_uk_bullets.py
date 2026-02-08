"""
Fix Ukrainian markdown bullet points.
Replace • (bullet character) with - (markdown dash) for proper list rendering.
"""

from pathlib import Path


def fix_bullets(content: str) -> str:
    """
    Replace bullet character (•) with markdown dash (-).

    Args:
        content: Markdown file content

    Returns:
        Content with fixed bullet points
    """
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Replace leading bullet character with dash
        if line.startswith("•"):
            # Replace • with - and preserve spacing
            fixed_line = "-" + line[1:]
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)

    return "\n".join(fixed_lines)


def main():
    """Main entry point"""

    input_file = Path("data/data_sources/wwn-lite-uk.md")

    if not input_file.exists():
        print(f"❌ Error: File '{input_file}' not found")
        return

    print(f"📝 Processing: {input_file.name}")

    # Read file
    content = input_file.read_text(encoding="utf-8")

    # Count bullets
    bullet_count = content.count("\n•")

    # Fix bullets
    fixed_content = fix_bullets(content)

    # Write back
    input_file.write_text(fixed_content, encoding="utf-8")

    print(f"   ✅ Fixed {bullet_count} bullet points (• → -)")
    print("\n✨ Done!")


if __name__ == "__main__":
    main()
