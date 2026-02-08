"""
Split monolithic markdown files into MkDocs-compatible structure.

This script parses large markdown files and splits them into logical chapters
while combining related sections for better navigation.
"""

import argparse
import re
from collections import defaultdict
from pathlib import Path

# Define section-to-file mapping for Ukrainian
UK_SECTION_MAPPING = {
    # basics/
    "СКОРОЧЕННЯ": "index",  # Landing page for Ukrainian
    "ЗДІБНОСТІ (АТРИБУТИ)": "basics/core-mechanics",
    "НАВИЧКИ (УМІННЯ)": "basics/core-mechanics",
    "ПЕРЕВІРКИ НАВИЧОК": "basics/core-mechanics",
    "РЯТІВНІ КИДКИ (РЯТКИДКИ, ПОРЯТУНКИ)": "basics/core-mechanics",
    "МОВИ": "basics/core-mechanics",
    # survival/
    "ЗАГРОЗИ Й ЗЦІЛЕННЯ": "survival/threats-healing",
    "ДОСЛІДЖЕННЯ ПІДЗЕМЕЛЬ": "survival/exploration",
    "ПОДОРОЖІ ТА ВИЖИВАННЯ": "survival/travel-ships",
    "КОРАБЛІ": "survival/travel-ships",
    # combat/
    "Бій": "combat/combat-basics",
    "Дії та часті дії в бою": "combat/actions",
    # equipment/
    "Броня й Зброя": "equipment/armors-weapons",
    "Спорядження": "equipment/gear",
    "Виготовлення Спорядження": "equipment/gear",
    "Модифікації та Обслуговування Спорядження": "equipment/gear",
    "Алхімія": "equipment/alchemy",
    # magic/
    "ЧАРИ": "magic/magic-basics",
    "ЕЛІКСИРИ": "magic/items",
    "МАГІЧНІ ПРИСТРОЇ": "magic/items",
    "АРКАННА ТРАДИЦІЯ ВИЩИХ МАГІВ": "magic/traditions",
    "АРКАННА ТРАДИЦІЯ ДРУЇДА": "magic/traditions",
    "АРКАННА ТРАДИЦІЯ ЕЛЕМЕНТАЛІСТА": "magic/traditions",
    "АРКАННА ТРАДИЦІЯ НЕКРОМАНТА": "magic/traditions",
    "АРКАННА ТРАДИЦІЯ БАРДА (НАПІВКЛАС)": "magic/traditions",
    "АРКАННА ТРАДИЦІЯ КЛІРИКА (НАПІВКЛАС)": "magic/traditions",
    "АРКАННА ТРАДИЦІЯ МОНАХА (НАПІВКЛАС)": "magic/traditions",
    "АРКАННА ТРАДИЦІЯ ПРИБОРКУВАЧА ЗВІРІВ (НАПІВКЛАС)": "magic/traditions",
    "АРКАННА ТРАДИЦІЯ ЧАКЛУНА (НАПІВКЛАС)": "magic/traditions",
    # character/
    "ШВИДКЕ СТВОРЕННЯ ПЕРСОНАЖА": "character/creation",
    "КРОК #1: КИДОК ЗДІБНОСТЕЙ": "character/creation",
    "КРОК #2: ОБЕРІТЬ ПЕРЕДІСТОРІЮ ТА НАВИЧКИ": "character/creation",
    "НАВИЧКИ": "character/creation",  # Duplicate section in character creation
    "КРОК #3: ОБЕРІТЬ КЛАС": "character/creation",
    "ЗДІБНОСТІ КЛАСІВ": "character/options",
    "КРОК #4 ОБЕРІТЬ ФОКУСИ": "character/creation",
    "ФОКУСИ": "character/options",
    "КРОК #5: ВИБЕРІТЬ НАБІР СПОРЯДЖЕННЯ": "character/creation",
    "КРОК #6: МАГИ ОБИРАЮТЬ СВОЮ ТРАДИЦІЮ ТА ЗАКЛИНАННЯ": "character/creation",
    "ДОСВІД (ОД), ПІДВИЩЕННЯ РІВНЯ ТА ОЧКИ НАВИЧОК (ОН)": "character/options",
    # campaign/
    "ВИТРАТИ НА ЖИТТЯ ТА ВАРТІСТЬ НА ТИЖДЕНЬ": "campaign/domain-management",
    "НАЙМАНЦІ": "campaign/domain-management",
    "НАЙМ АРМІЙ ТА МАСОВИЙ БІЙ": "campaign/domain-management",
    "ЗЕМЕЛЬНА ВЛАСНІСТЬ ТА ДОХОДИ": "campaign/domain-management",
    "БУДІВНИЦТВО СПОРУД": "campaign/domain-management",
    "СТВОРЕННЯ МАГІЧНИХ КОНСТРУКЦІЙ": "campaign/domain-management",
    "Винагороди від Покровителів": "campaign/domain-management",
    "Опис Власності та Вартість Винагороди": "campaign/domain-management",
    "Річний Дохід та Тип Гексу": "campaign/domain-management",
    "Визнання": "campaign/domain-management",
    "ДЕЯКІ ЗАНЯТТЯ В ПЕРІОД ПРОСТОЮ": "campaign/downtime",
    "ОЦІНКА СКЛАДНОСТІ СУТИЧКИ": "campaign/downtime",
    # reference/
    "Теги Персонажа": "reference/tags",
    "Теги Спільнот": "reference/tags",
    "Теги Руїн": "reference/tags",
    "Теги Дикої Місцевості": "reference/tags",
    "Теги Двору": "reference/tags",
}

# Define section-to-file mapping for English
EN_SECTION_MAPPING = {
    # basics/
    "SHORTHAND": "index",
    "ATTRIBUTES": "basics/core-mechanics",
    "SKILLS": "basics/core-mechanics",
    "SKILL CHECKS": "basics/core-mechanics",
    "SAVING THROWS": "basics/core-mechanics",
    "LANGUAGE": "basics/core-mechanics",
    # survival/
    "HEALING & HAZARDS": "survival/threats-healing",
    "DELVING": "survival/exploration",
    "OVERLAND TRAVEL & WILDERNESS SURVIVAL": "survival/travel-ships",
    "SEA TRAVEL": "survival/travel-ships",
    # combat/
    "COMBAT": "combat/combat",
    "ACTIONS & COMMON COMBAT ACTIONS": "combat/combat",
    "ARMORS & WEAPONS": "combat/combat",
    # equipment/
    "GEAR": "equipment/equipment",
    "ALCHEMY": "equipment/alchemy",
    # magic/
    "MAGIC": "magic/magic-basics",
    "ELIXIRS": "magic/items",
    "MAGICAL DEVICES": "magic/items",
    "ARCANE TRADITION OF THE HIGH MAGE": "magic/traditions",
    "ARCANE TRADITION OF THE DRUID": "magic/traditions",
    "ARCANE TRADITION OF THE ELEMENTALIST": "magic/traditions",
    "ARCANE TRADITION OF THE NECROMANCER": "magic/traditions",
    "ARCANE TRADITION OF THE BARD (HALF CLASS)": "magic/traditions",
    "ARCANE TRADITION OF THE CLERIC (HALF CLASS)": "magic/traditions",
    "ARCANE TRADITION OF THE MONK (HALF CLASS)": "magic/traditions",
    "ARCANE TRADITION OF THE BEASTMASTER (HALF CLASS)": "magic/traditions",
    "ARCANE TRADITION OF THE WARLOCK (HALF CLASS)": "magic/traditions",
    # character/
    "QUICK-START CHARACTER GENERATION": "character/creation",
    "XP, LEVEL UP, & SKILL POINTS (SP)": "character/options",
    # campaign/
    "LIVING EXPENSES & SERVICES": "campaign/domain-management",
    "HIRELINGS": "campaign/domain-management",
    "HIRING ARMIES & MASS COMBAT": "campaign/domain-management",
    "LAND OWNERSHIP & DOMAINS": "campaign/domain-management",
    "BUILDING STRUCTURES": "campaign/domain-management",
    "BUILDING MAGICAL WORKINGS": "campaign/domain-management",
    "REWARDS BY PATRON": "campaign/domain-management",
    "RENOWN": "campaign/domain-management",
    "DOWNTIME ACTIVITIES": "campaign/downtime",
    "JUDGING AN ENCOUNTER CHALLENGE": "campaign/downtime",
    # reference/
    "CHARACTER TAGS": "reference/tags",
    "COMMUNITY TAGS": "reference/tags",
    "RUINS TAGS": "reference/tags",
    "WILDERNESS TAGS": "reference/tags",
    "COURT TAGS": "reference/tags",
    "NPC STATISTICS": "reference/tags",
}

# Chapter index content templates
CHAPTER_INDEX_TEMPLATES = {
    "uk": {
        "basics": {
            "title": "Основи",
            "description": "Базові правила гри: здібності, навички, перевірки та рятівні кидки.",
        },
        "survival": {"title": "Виживання", "description": "Загрози, зцілення, дослідження підземель та подорожі."},
        "combat": {"title": "Бій", "description": "Правила бою, зброя та броня."},
        "equipment": {"title": "Спорядження", "description": "Обладнання, виготовлення предметів та алхімія."},
        "magic": {"title": "Магія", "description": "Чари, арканні традиції та магічні предмети."},
        "character": {"title": "Персонаж", "description": "Створення персонажа, класи, фокуси та розвиток."},
        "campaign": {
            "title": "Кампанія",
            "description": "Управління володіннями, найманці та заняття в період простою.",
        },
        "reference": {"title": "Довідник", "description": "Теги та довідкові таблиці."},
    },
    "en": {
        "basics": {"title": "Basics", "description": "Core game rules: attributes, skills, checks, and saving throws."},
        "survival": {"title": "Survival", "description": "Threats, healing, dungeoneering, and travel."},
        "combat": {"title": "Combat", "description": "Combat rules, weapons, and armor."},
        "equipment": {"title": "Equipment", "description": "Gear, crafting, and alchemy."},
        "magic": {"title": "Magic", "description": "Spellcasting, arcane traditions, and magical items."},
        "character": {"title": "Character", "description": "Character creation, classes, foci, and advancement."},
        "campaign": {"title": "Campaign", "description": "Domain management, hirelings, and downtime activities."},
        "reference": {"title": "Reference", "description": "Tags and reference tables."},
    },
}


def parse_markdown(file_path: Path) -> list[tuple[str, str]]:
    """
    Parse markdown file and return list of (section_name, content) tuples.

    Each section starts with ## (H2) header and includes all content
    until the next ## header.
    """
    content = file_path.read_text(encoding="utf-8")
    sections = []

    # Split on H2 headers (##)
    # Pattern matches: ## SECTION_NAME (captures section name)
    pattern = r"^## (.+)$"

    # Find all H2 headers and their positions
    matches = list(re.finditer(pattern, content, re.MULTILINE))

    # Skip the first H1 header (# WWN-Lite Правила / # WWN-Lite Rules)
    for i, match in enumerate(matches):
        section_name = match.group(1).strip()
        start_pos = match.start()

        # Get content until next section or EOF
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)

        section_content = content[start_pos:end_pos].strip()
        sections.append((section_name, section_content))

    return sections


def group_sections(sections: list[tuple[str, str]], mapping: dict[str, str]) -> dict[str, list[tuple[str, str]]]:
    """
    Group sections by their target file based on mapping.

    Returns: Dict[file_path, List[(section_name, content)]]
    """
    grouped = defaultdict(list)

    for section_name, content in sections:
        target_file = mapping.get(section_name)

        if target_file:
            grouped[target_file].append((section_name, content))
        else:
            print(f"⚠️  Warning: Section '{section_name}' not in mapping, skipping")

    return grouped


def write_files(output_dir: Path, grouped_sections: dict[str, list[tuple[str, str]]]):
    """Write grouped sections to markdown files."""
    for file_path, sections in grouped_sections.items():
        target_file = output_dir / f"{file_path}.md"
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Combine all section content
        combined_content = "\n\n".join([content for _, content in sections])

        target_file.write_text(combined_content, encoding="utf-8")
        print(f"✅ Created: {target_file.relative_to(output_dir.parent.parent)}")


def create_chapter_index_files(output_dir: Path, lang: str):
    """Create index.md files for each chapter folder."""
    templates = CHAPTER_INDEX_TEMPLATES.get(lang, CHAPTER_INDEX_TEMPLATES["en"])

    for chapter, template in templates.items():
        index_file = output_dir / chapter / "index.md"

        if not index_file.exists():
            content = f"# {template['title']}\n\n{template['description']}\n"
            index_file.write_text(content, encoding="utf-8")
            print(f"✅ Created index: {index_file.relative_to(output_dir.parent.parent)}")


def main():
    parser = argparse.ArgumentParser(description="Split monolithic markdown into MkDocs structure")
    parser.add_argument(
        "--input", type=Path, required=True, help="Input markdown file (e.g., data/data_sources/wwn-lite-uk.md)"
    )
    parser.add_argument("--output", type=Path, required=True, help="Output directory (e.g., docs/wwn-lite/uk)")
    parser.add_argument("--lang", choices=["uk", "en"], required=True, help="Language code (uk or en)")

    args = parser.parse_args()

    # Validate input file exists
    if not args.input.exists():
        print(f"❌ Error: Input file '{args.input}' not found")
        return 1

    # Select appropriate mapping
    mapping = UK_SECTION_MAPPING if args.lang == "uk" else EN_SECTION_MAPPING

    print(f"\n📖 Parsing: {args.input}")
    sections = parse_markdown(args.input)
    print(f"   Found {len(sections)} sections")

    print("\n🗂️  Grouping sections...")
    grouped = group_sections(sections, mapping)
    print(f"   Grouped into {len(grouped)} files")

    print(f"\n📝 Writing files to: {args.output}")
    write_files(args.output, grouped)

    print("\n📑 Creating chapter index files...")
    create_chapter_index_files(args.output, args.lang)

    print(f"\n✨ Done! Split {len(sections)} sections into {len(grouped)} files")
    return 0


if __name__ == "__main__":
    exit(main())
