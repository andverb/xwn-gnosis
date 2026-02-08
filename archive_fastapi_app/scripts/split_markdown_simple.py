"""
Simple markdown splitter based on ## (H2) headers.
Splits monolithic markdown file into one file per ## section.
All ### (H3) subsections stay with their parent ##.
Content preserved verbatim.
"""

import re
from pathlib import Path

# English filename mapping
EN_FILENAME_MAP = {
    "BASICS": "basics",
    "HEALING & HAZARDS": "healing-hazards",
    "COMBAT": "combat",
    "ACTIONS & COMMON COMBAT ACTIONS": "actions-common-combat",
    "ARMORS & WEAPONS": "armors-weapons",
    "DELVING": "delving",
    "OVERLAND TRAVEL & WILDERNESS SURVIVAL": "overland-travel",
    "SEA TRAVEL": "sea-travel",
    "GEAR": "gear",
    "ALCHEMY": "alchemy",
    "MAGIC": "magic",
    "ELIXIRS": "elixirs",
    "MAGICAL DEVICES": "magical-devices",
    "LIVING EXPENSES & SERVICES": "living-expenses",
    "HIRELINGS": "hirelings",
    "HIRING ARMIES & MASS COMBAT": "hiring-armies",
    "LAND OWNERSHIP & DOMAINS": "land-ownership",
    "BUILDING STRUCTURES": "building-structures",
    "BUILDING MAGICAL WORKINGS": "building-magical-workings",
    "REWARDS BY PATRON": "rewards-by-patron",
    "RENOWN": "renown",
    "XP, LEVEL UP, & SKILL POINTS (SP)": "xp-leveling",
    "DOWNTIME ACTIVITIES": "downtime",
    "QUICK-START CHARACTER GENERATION": "character-generation",
    "ARCANE TRADITION OF THE HIGH MAGE": "tradition-high-mage",
    "ARCANE TRADITION OF THE DRUID": "tradition-druid",
    "ARCANE TRADITION OF THE ELEMENTALIST": "tradition-elementalist",
    "ARCANE TRADITION OF THE NECROMANCER": "tradition-necromancer",
    "ARCANE TRADITION OF THE BARD (HALF CLASS)": "tradition-bard",
    "ARCANE TRADITION OF THE CLERIC (HALF CLASS)": "tradition-cleric",
    "ARCANE TRADITION OF THE MONK (HALF CLASS)": "tradition-monk",
    "ARCANE TRADITION OF THE BEASTMASTER (HALF CLASS)": "tradition-beastmaster",
    "ARCANE TRADITION OF THE WARLOCK (HALF CLASS)": "tradition-warlock",
    "CHARACTER TAGS": "tags-character",
    "COMMUNITY TAGS": "tags-community",
    "RUINS TAGS": "tags-ruins",
    "WILDERNESS TAGS": "tags-wilderness",
    "COURT TAGS": "tags-court",
    "JUDGING AN ENCOUNTER CHALLENGE": "encounter-difficulty",
    "NPC STATISTICS": "npc-statistics",
}

# Ukrainian filename mapping
UK_FILENAME_MAP = {
    "BASICS": "basics",
    "ЗАГРОЗИ Й ЗЦІЛЕННЯ": "threats-healing",
    "БІЙ": "combat",
    "БРОНЯ Й ЗБРОЯ": "armor-weapons",
    "ДОСЛІДЖЕННЯ ПІДЗЕМЕЛЬ": "delving",
    "ПОДОРОЖІ ТА ВИЖИВАННЯ": "overland-travel",
    "КОРАБЛІ": "sea-travel",
    "ЗВИЧАЙНЕ СПОРЯДЖЕННЯ": "gear",
    "ВИГОТОВЛЕННЯ СПОРЯДЖЕННЯ": "gear-crafting",
    "МОДИФІКАЦІЇ ТА ОБСЛУГОВУВАННЯ СПОРЯДЖЕННЯ": "gear-modifications",
    "АЛХІМІЯ": "alchemy",
    "ЧАРИ": "magic",
    "ЕЛІКСИРИ": "elixirs",
    "МАГІЧНІ ПРИСТРОЇ": "magical-devices",
    "ВИТРАТИ НА ЖИТТЯ ТА ВАРТІСТЬ НА ТИЖДЕНЬ": "living-expenses",
    "НАЙМАНЦІ": "hirelings",
    "НАЙМ АРМІЙ ТА МАСОВИЙ БІЙ": "hiring-armies",
    "ЗЕМЕЛЬНА ВЛАСНІСТЬ ТА ДОХОДИ": "land-ownership",
    "БУДІВНИЦТВО СПОРУД": "building-structures",
    "СТВОРЕННЯ МАГІЧНИХ КОНСТРУКЦІЙ": "building-magical-workings",
    "Винагороди від Покровителів": "rewards-by-patron",
    "Опис Власності та Вартість Винагороди": "property-description",
    "Річний Дохід та Тип Гексу": "income-hex-type",
    "Визнання": "recognition",
    "ДОСВІД (ОД), ПІДВИЩЕННЯ РІВНЯ ТА ОЧКИ НАВИЧОК (ОН)": "xp-leveling",
    "ДЕЯКІ ЗАНЯТТЯ В ПЕРІОД ПРОСТОЮ": "downtime",
    "ШВИДКЕ СТВОРЕННЯ ПЕРСОНАЖА": "character-generation",
    "ОЦІНКА СКЛАДНОСТІ СУТИЧКИ": "encounter-difficulty",
    "АРКАННА ТРАДИЦІЯ ВИЩИХ МАГІВ": "tradition-high-mage",
    "АРКАННА ТРАДИЦІЯ ДРУЇДА": "tradition-druid",
    "АРКАННА ТРАДИЦІЯ ЕЛЕМЕНТАЛІСТА": "tradition-elementalist",
    "АРКАННА ТРАДИЦІЯ НЕКРОМАНТА": "tradition-necromancer",
    "АРКАННА ТРАДИЦІЯ БАРДА (НАПІВКЛАС)": "tradition-bard",
    "АРКАННА ТРАДИЦІЯ КЛІРИКА (НАПІВКЛАС)": "tradition-cleric",
    "АРКАННА ТРАДИЦІЯ МОНАХА (НАПІВКЛАС)": "tradition-monk",
    "АРКАННА ТРАДИЦІЯ ПРИБОРКУВАЧА ЗВІРІВ (НАПІВКЛАС)": "tradition-beastmaster",
    "АРКАННА ТРАДИЦІЯ ЧАКЛУНА (НАПІВКЛАС)": "tradition-warlock",
    "Теги Персонажа": "tags-character",
    "Теги Спільнот": "tags-community",
    "Теги Руїн": "tags-ruins",
    "Теги Дикої Місцевості": "tags-wilderness",
    "Теги Двору": "tags-court",
    "НІП (282CR)": "npc-statistics",
}


def split_markdown(input_file: Path, output_dir: Path, filename_map: dict[str, str], lang: str = "en"):
    """
    Split markdown file based on ## headers.
    Each ## section becomes its own file.
    All ### subsections stay with their parent ##.
    Content preserved verbatim.
    """

    if not input_file.exists():
        print(f"❌ Error: Input file '{input_file}' not found")
        return

    content = input_file.read_text(encoding="utf-8")

    # Find all ## headers
    h2_pattern = r"^## (.+)$"
    matches = list(re.finditer(h2_pattern, content, re.MULTILINE))

    print(f"\n📖 Processing {lang.upper()}: {input_file.name}")
    print(f"   Found {len(matches)} ## sections")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, match in enumerate(matches):
        section_name = match.group(1).strip()
        start_pos = match.start()

        # Get content until next ## or EOF
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)

        # Extract section content (verbatim)
        section_content = content[start_pos:end_pos].strip()

        # Get filename from mapping
        filename = filename_map.get(section_name)
        if not filename:
            print(f"   ⚠️  No mapping for: '{section_name}'")
            continue

        output_file = output_dir / f"{filename}.md"
        output_file.write_text(section_content, encoding="utf-8")
        print(f"   ✅ {filename}.md")

    print(f"   ✨ Done! Split {len(matches)} sections into {output_dir}")


def main():
    """Main entry point"""

    # English
    split_markdown(Path("data/data_sources/wwn-lite-en.md"), Path("docs/wwn-lite/en"), EN_FILENAME_MAP, lang="en")

    # Ukrainian
    split_markdown(Path("data/data_sources/wwn-lite-uk.md"), Path("docs/wwn-lite/uk"), UK_FILENAME_MAP, lang="uk")


if __name__ == "__main__":
    main()
