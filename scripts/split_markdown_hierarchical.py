"""
Hierarchical markdown splitter for WWN-Lite.
Splits monolithic markdown file into organized folder structure.
Content preserved verbatim.
"""

import re
from pathlib import Path

# English section to folder/filename mapping
EN_SECTION_MAP = {
    "Basics": ("basics", "index.md"),
    "Healing & Hazards": ("survival", "healing-hazards.md"),
    "Combat": ("combat", "combat-basics.md"),
    "Actions & Common Combat Actions": ("combat", "actions.md"),
    "Armors & Weapons": ("equipment", "armors-weapons.md"),
    "Delving": ("survival", "delving.md"),
    "Overland Travel & Wilderness Survival": ("survival", "overland-travel.md"),
    "Sea Travel": ("survival", "sea-travel.md"),
    "Gear": ("equipment", "gear.md"),
    "Alchemy": ("equipment", "alchemy.md"),
    "Magic and Spells": ("magic", "magic-basics.md"),
    "Magical Items": ("magic", "magical-items.md"),
    "Living Expenses & Services": ("campaign", "living-expenses.md"),
    "Hirelings": ("campaign", "hirelings.md"),
    "Hiring Armies & Mass Combat": ("campaign", "hiring-armies.md"),
    "Land Ownership & Domains": ("campaign", "land-ownership.md"),
    "Building Structures": ("campaign", "building-structures.md"),
    "Building Magical Workings": ("campaign", "magical-workings.md"),
    "Rewards by Patron": ("campaign", "patronage.md"),
    "Renown": ("campaign", "renown.md"),
    "XP, Level Up, & Skill Points (SP)": ("character", "xp-leveling.md"),
    "Downtime Activities": ("campaign", "downtime.md"),
    "Quick-start Character Generation": ("character", "character-creation.md"),
    "Monsters and Encounters": ("reference", "encounter-difficulty.md"),
    "NPC/Monsters Statistics": ("reference", "npc-statistics.md"),
}

# Special handling for TAGS section - split by ### subsections
EN_TAGS_SUBSECTIONS = {
    "Character Tags": ("reference/tags", "character.md"),
    "Community Tags": ("reference/tags", "community.md"),
    "Ruins Tags": ("reference/tags", "ruins.md"),
    "Wilderness Tags": ("reference/tags", "wilderness.md"),
    "Court Tags": ("reference/tags", "court.md"),
}

# Ukrainian section to folder/filename mapping
UK_SECTION_MAP = {
    "Основи": ("basics", "index.md"),
    "Загрози й Зцілення": ("survival", "healing-hazards.md"),
    "Бій": ("combat", "combat-basics.md"),
    "Дії та часті дії в бою": ("combat", "actions.md"),
    "Броня й Зброя": ("equipment", "armors-weapons.md"),
    "Дослідження Підземель": ("survival", "delving.md"),
    "Подорожі та Виживання": ("survival", "overland-travel.md"),
    "Кораблі": ("survival", "sea-travel.md"),
    "Звичайне Спорядження": ("equipment", "gear.md"),
    "Виготовлення Спорядження": ("equipment", "crafting.md"),
    "Модифікації та Обслуговування Спорядження": ("equipment", "modifications.md"),
    "Алхімія": ("equipment", "alchemy.md"),
    "Чари і Заклинання": ("magic", "magic-basics.md"),
    "Магічні Предмети": ("magic", "magical-items.md"),
    "Витрати на Життя та Вартість на Тиждень": ("campaign", "living-expenses.md"),
    "Найманці": ("campaign", "hirelings.md"),
    "Найм Армій та Масовий Бій": ("campaign", "hiring-armies.md"),
    "Земельна Власність та Доходи": ("campaign", "land-ownership.md"),
    "Будівництво Споруд": ("campaign", "building-structures.md"),
    "Створення Магічних Конструкцій": ("campaign", "magical-workings.md"),
    "Винагороди Від Покровителів": ("campaign", "patronage.md"),
    "Опис Власності та Вартість Винагороди": ("campaign", "property-rewards.md"),
    "Річний Дохід та Тип Місцевості": ("campaign", "income-hex-type.md"),
    "Визнання": ("campaign", "renown.md"),
    "Досвід (ОД), Підвищення Рівня та Очки Навичок (ОН)": ("character", "xp-leveling.md"),
    "Деякі Заняття в Період Простою": ("campaign", "downtime.md"),
    "Швидке Створення Персонажа": ("character", "character-creation.md"),
    "Крок #1: Кидок Здібностей": ("character", "step1-abilities.md"),
    "Крок #2: Оберіть Передісторію та Навички": ("character", "step2-background.md"),
    "Навички": ("character", "skills.md"),
    "Крок #3: Оберіть Клас": ("character", "step3-class.md"),
    "Здібності Класів": ("character", "class-abilities.md"),
    "Крок #4 Оберіть Фокуси": ("character", "step4-foci.md"),
    "Фокуси": ("character", "foci.md"),
    "Крок #5: Виберіть Набір Спорядження": ("character", "step5-equipment.md"),
    "Монстри і Сутички": ("reference", "encounter-difficulty.md"),
    "НІПИ (Монстри)": ("reference", "npc-statistics.md"),
}

# Ukrainian tags subsections
UK_TAGS_SUBSECTIONS = {
    "Теги Персонажа": ("reference/tags", "character.md"),
    "Теги Спільнот": ("reference/tags", "community.md"),
    "Теги Руїн": ("reference/tags", "ruins.md"),
    "Теги Дикої Місцевості": ("reference/tags", "wilderness.md"),
    "Теги Двору": ("reference/tags", "court.md"),
}


def extract_tags_subsections(content: str, start_pos: int, end_pos: int) -> dict[str, str]:
    """
    Extract ### subsections from the TAGS section.

    Args:
        content: Full markdown content
        start_pos: Start position of ## TAGS section
        end_pos: End position of ## TAGS section

    Returns:
        Dictionary mapping subsection name to its content
    """
    tags_content = content[start_pos:end_pos]

    # Find all ### headers within TAGS section
    h3_pattern = r"^### (.+)$"
    matches = list(re.finditer(h3_pattern, tags_content, re.MULTILINE))

    subsections = {}
    for i, match in enumerate(matches):
        subsection_name = match.group(1).strip()
        subsection_start = match.start()

        # Get content until next ### or end of TAGS section
        if i + 1 < len(matches):
            subsection_end = matches[i + 1].start()
        else:
            subsection_end = len(tags_content)

        subsection_content = tags_content[subsection_start:subsection_end].strip()
        subsections[subsection_name] = subsection_content

    return subsections


def split_markdown_hierarchical(
    input_file: Path,
    output_dir: Path,
    section_map: dict[str, tuple[str, str]],
    tags_subsections: dict[str, tuple[str, str]],
    lang: str = "en",
):
    """
    Split markdown file into hierarchical folder structure.

    Args:
        input_file: Path to source markdown file
        output_dir: Base output directory
        section_map: Mapping of section names to (folder, filename) tuples
        tags_subsections: Mapping of tag subsection names to (folder, filename) tuples
        lang: Language code
    """
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found")
        return

    content = input_file.read_text(encoding="utf-8")

    # Find all ## headers
    h2_pattern = r"^## (.+)$"
    matches = list(re.finditer(h2_pattern, content, re.MULTILINE))

    print(f"\nProcessing {lang.upper()}: {input_file.name}")
    print(f"   Found {len(matches)} ## sections")

    sections_processed = 0
    sections_skipped = 0

    for i, match in enumerate(matches):
        section_name = match.group(1).strip()
        start_pos = match.start()

        # Get content until next ## or EOF
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)

        # Special handling for TAGS section (English: "Tags", Ukrainian: "Теги")
        if section_name in {"Tags", "Теги"}:
            print("   Processing Tags section (splitting into subsections)...")
            subsections = extract_tags_subsections(content, start_pos, end_pos)

            for subsection_name, subsection_content in subsections.items():
                if subsection_name in tags_subsections:
                    folder, filename = tags_subsections[subsection_name]
                    output_path = output_dir / folder
                    output_path.mkdir(parents=True, exist_ok=True)

                    output_file = output_path / filename
                    output_file.write_text(subsection_content, encoding="utf-8")
                    sections_processed += 1
                    print(f"      OK {folder}/{filename}")
                else:
                    print(f"      WARNING: No mapping for subsection: '{subsection_name}'")
                    sections_skipped += 1
            continue

        # Regular section handling
        if section_name not in section_map:
            print(f"   WARNING: No mapping for: '{section_name}'")
            sections_skipped += 1
            continue

        folder, filename = section_map[section_name]

        # Extract section content (verbatim)
        section_content = content[start_pos:end_pos].strip()

        # Strip the ## header line to avoid duplication with MkDocs page title
        # MkDocs nav provides the page title, so we only need ### and below
        lines = section_content.split("\n")
        if lines and lines[0].startswith("## "):
            # Remove first line (the ## header) and rejoin
            section_content = "\n".join(lines[1:]).strip()

        # Create output directory
        output_path = output_dir / folder
        output_path.mkdir(parents=True, exist_ok=True)

        # Write file
        output_file = output_path / filename
        output_file.write_text(section_content, encoding="utf-8")
        sections_processed += 1
        print(f"   OK {folder}/{filename}")

    print("\n   Done!")
    print(f"   Processed: {sections_processed} sections")
    if sections_skipped > 0:
        print(f"   Skipped: {sections_skipped} sections")


def main():
    """Main entry point"""

    # English
    split_markdown_hierarchical(
        Path("data/data_sources/wwn-lite-en.md"),
        Path("docs/wwn-lite/en"),
        EN_SECTION_MAP,
        EN_TAGS_SUBSECTIONS,
        lang="en",
    )

    # Ukrainian
    split_markdown_hierarchical(
        Path("data/data_sources/wwn-lite-uk.md"),
        Path("docs/wwn-lite/uk"),
        UK_SECTION_MAP,
        UK_TAGS_SUBSECTIONS,
        lang="uk",
    )


if __name__ == "__main__":
    main()
