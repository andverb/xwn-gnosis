#!/usr/bin/env python3
"""
Monster and NPC stat blocks for WWN.
"""

import sys

import requests

# Format: (name, category, HD, AC, Atk, Dmg, Shock, Move, ML, Inst, Skill, Save, description)
MONSTERS = [
    # Normal Humans
    (
        "Peaceful Human",
        "Normal Human",
        1,
        10,
        "+0",
        "Wpn",
        "Wpn",
        "30'",
        7,
        5,
        "+1",
        "15+",
        "An ordinary civilian with no combat training or martial experience.",
    ),
    (
        "Thug or Militia",
        "Normal Human",
        1,
        "13a",
        "+1",
        "Wpn",
        "Wpn",
        "30'",
        8,
        4,
        "+1",
        "15+",
        "A street tough or local militia member with basic combat training and simple armor.",
    ),
    (
        "Barbarian Fighter",
        "Normal Human",
        1,
        "13a",
        "+2",
        "Wpn+1",
        "Wpn+1",
        "30'",
        8,
        5,
        "+1",
        "15+",
        "A tribal warrior or barbarian fighter, fierce in combat and experienced in battle.",
    ),
    (
        "Veteran Soldier",
        "Normal Human",
        1,
        "13a",
        "+2",
        "Wpn+1",
        "Wpn+1",
        "30'",
        8,
        3,
        "+1",
        "15+",
        "A seasoned military veteran with combat experience and disciplined training.",
    ),
    (
        "Skilled Veteran",
        "Normal Human",
        2,
        15,
        "+3",
        "Wpn+1",
        "Wpn+1",
        "30'",
        9,
        2,
        "+1",
        "14+",
        "A highly skilled veteran warrior with extensive combat experience and better armor.",
    ),
    (
        "Elites or Special Guards",
        "Normal Human",
        3,
        18,
        "+4",
        "Wpn+2",
        "Wpn+2",
        "30'",
        10,
        2,
        "+2",
        "14+",
        "Elite guards or special forces, equipped with the finest armor and extensive training.",
    ),
    (
        "Knight or Minor Hero",
        "Normal Human",
        4,
        18,
        "+6",
        "Wpn+2",
        "Wpn+2",
        "30'",
        10,
        1,
        "+2",
        "13+",
        "A knight or minor hero, a warrior of exceptional skill and renown.",
    ),
    (
        "Warrior Baron",
        "Normal Human",
        6,
        18,
        "+8",
        "Wpn+3",
        "Wpn+3",
        "30'",
        9,
        1,
        "+2",
        "12+",
        "A warrior baron or lord, a military leader of great prowess and authority.",
    ),
    (
        "Barbarian Warlord",
        "Normal Human",
        8,
        16,
        "+10 x2",
        "Wpn+4",
        "Wpn+4/-",
        "30'",
        10,
        3,
        "+2",
        "11+",
        "A legendary barbarian warlord, making two attacks per round with devastating force.",
    ),
    (
        "Mighty General",
        "Normal Human",
        8,
        18,
        "+10",
        "Wpn+4",
        "Wpn+4/-",
        "30'",
        10,
        1,
        "+3",
        "11+",
        "A mighty general, a master tactician and warrior who commands armies.",
    ),
    (
        "Major Hero",
        "Normal Human",
        10,
        18,
        "+12 x2",
        "Wpn+5",
        "Wpn+5/-",
        "30'",
        10,
        2,
        "+3",
        "10+",
        "A major hero of legend, making two attacks per round with unmatched martial skill.",
    ),
    (
        "Great Warrior King",
        "Normal Human",
        12,
        18,
        "+14 x2",
        "Wpn+5",
        "Wpn+5/-",
        "30'",
        10,
        1,
        "+3",
        "9+",
        "A great warrior king, the pinnacle of martial prowess and leadership, making two attacks per round.",
    ),
    # Spellcasters
    (
        "Petty Mage",
        "Spellcaster",
        2,
        10,
        "+1",
        "Wpn",
        "Wpn",
        "30'",
        8,
        4,
        "+1",
        "14+",
        "A minor spellcaster with limited magical training. Mages generally have the spellcasting and Arts of an appropriate mage tradition at a level equal to their hit dice and Effort equal to their skill bonus plus two.",
    ),
    (
        "Tribal Shaman",
        "Spellcaster",
        4,
        10,
        "+3",
        "Wpn+1",
        "Wpn+1",
        "30'",
        9,
        4,
        "+1",
        "13+",
        "A tribal shaman who serves their people with spiritual magic and guidance. Mages generally have the spellcasting and Arts of an appropriate mage tradition at a level equal to their hit dice and Effort equal to their skill bonus plus two.",
    ),
    (
        "Skilled Sorcerer",
        "Spellcaster",
        5,
        10,
        "+1",
        "Wpn",
        "Wpn",
        "30'",
        9,
        4,
        "+2",
        "13+",
        "A skilled sorcerer with significant magical power and arcane knowledge. Mages generally have the spellcasting and Arts of an appropriate mage tradition at a level equal to their hit dice and Effort equal to their skill bonus plus two.",
    ),
    (
        "Master Wizard",
        "Spellcaster",
        8,
        13,
        "+1",
        "Wpn",
        "Wpn",
        "30'",
        9,
        3,
        "+2",
        "11+",
        "A master wizard of considerable power and learning. Mages generally have the spellcasting and Arts of an appropriate mage tradition at a level equal to their hit dice and Effort equal to their skill bonus plus two.",
    ),
    (
        "Famous Arch-Mage",
        "Spellcaster",
        10,
        13,
        "+2",
        "Wpn",
        "Wpn",
        "30'",
        9,
        2,
        "+3",
        "10+",
        "A famous arch-mage of legendary power and knowledge. Mages generally have the spellcasting and Arts of an appropriate mage tradition at a level equal to their hit dice and Effort equal to their skill bonus plus two.",
    ),
    # Normal Animals
    (
        "Small Pack Predator",
        "Normal Animal",
        1,
        12,
        "+2",
        "1d4",
        "1/13",
        "40'",
        7,
        6,
        "+1",
        "15+",
        "A wolf, wild dog, or similar small pack-hunting predator.",
    ),
    (
        "Large Solitary Predator",
        "Normal Animal",
        5,
        13,
        "+6",
        "1d8",
        "2/13",
        "30'",
        8,
        6,
        "+1",
        "13+",
        "A bear, great cat, or other large predator that hunts alone.",
    ),
    (
        "Apex Predator",
        "Normal Animal",
        6,
        13,
        "+6 x2",
        "1d8",
        "2/13",
        "40'",
        8,
        6,
        "+2",
        "12+",
        "A saber-tooth tiger, dire wolf, or other apex predator making two attacks per round.",
    ),
    (
        "Herd Beast",
        "Normal Animal",
        2,
        11,
        "+2",
        "1d4",
        "None",
        "40'",
        7,
        6,
        "+1",
        "14+",
        "A deer, antelope, or similar herd animal with no Shock damage.",
    ),
    (
        "Vicious Large Herbivore",
        "Normal Animal",
        4,
        13,
        "+5",
        "1d10",
        "1/13",
        "40'",
        9,
        6,
        "+1",
        "13+",
        "A wild boar, aggressive bull, or similar dangerous herbivore.",
    ),
    (
        "Elephantine Grazer",
        "Normal Animal",
        6,
        13,
        "+5",
        "2d8",
        "None",
        "40'",
        7,
        6,
        "+1",
        "12+",
        "An elephant, mammoth, or similar massive grazing beast with no Shock damage.",
    ),
    # Unnatural Entities
    (
        "Automaton, Humanlike",
        "Unnatural Entity",
        2,
        13,
        "+2",
        "Wpn",
        "Wpn",
        "30'",
        12,
        3,
        "+1",
        "14+",
        "A mechanical construct resembling a human, capable of wielding weapons.",
    ),
    (
        "Automaton, Laborer",
        "Unnatural Entity",
        2,
        15,
        "+2",
        "1d6",
        "1/13",
        "30'",
        12,
        3,
        "+1",
        "14+",
        "A mechanical construct built for heavy labor and physical work.",
    ),
    (
        "Automaton, Military",
        "Unnatural Entity",
        4,
        18,
        "+5",
        "1d10+2",
        "4/15",
        "30'",
        12,
        3,
        "+1",
        "13+",
        "A mechanical construct designed for warfare, heavily armored and dangerous.",
    ),
    (
        "Automaton, Warbot",
        "Unnatural Entity",
        10,
        20,
        "+12 x3",
        "1d12+5",
        "7/-",
        "40'",
        12,
        2,
        "+2",
        "10+",
        "A massive mechanical war machine making three attacks per round with devastating power.",
    ),
    (
        "Slime or Ooze",
        "Unnatural Entity",
        6,
        10,
        "+6 x2",
        "1d8",
        "1/-",
        "20'",
        12,
        5,
        "+1",
        "12+",
        "An amorphous ooze or slime making two attacks per round, applying Shock regardless of AC.",
    ),
    (
        "Predator, Small Vicious",
        "Unnatural Entity",
        1,
        14,
        "+1",
        "1d4",
        "1/13",
        "30'",
        7,
        5,
        "+1",
        "15+",
        "A small but vicious supernatural predator, more dangerous than its size suggests.",
    ),
    (
        "Predator, Large Vicious",
        "Unnatural Entity",
        6,
        13,
        "+7 x2",
        "2d6",
        "2/15",
        "40'",
        9,
        5,
        "+2",
        "13+",
        "A large supernatural predator making two attacks per round with terrifying ferocity.",
    ),
    (
        "Predator, Hulking",
        "Unnatural Entity",
        10,
        15,
        "+12 x2",
        "2d6+3",
        "6/15",
        "30'",
        10,
        4,
        "+1",
        "10+",
        "A hulking supernatural predator making two attacks per round with immense strength.",
    ),
    (
        "Predator, Hellbeast",
        "Unnatural Entity",
        10,
        18,
        "+12 x4",
        "1d10+5",
        "6/-",
        "60'",
        11,
        4,
        "+3",
        "10+",
        "A hellish beast from nightmare, making four attacks per round at terrifying speed.",
    ),
    (
        "Unnatural Swarm",
        "Unnatural Entity",
        4,
        10,
        "+6 x3",
        "1d6",
        "1/-",
        "30'",
        10,
        5,
        "+1",
        "13+",
        "A swarm of unnatural creatures making three attacks per round, applying Shock regardless of AC.",
    ),
    (
        "Terrible Warbeast",
        "Unnatural Entity",
        8,
        15,
        "+10 x2",
        "2d6+4",
        "7/15",
        "40'",
        9,
        4,
        "+2",
        "11+",
        "A terrible warbeast of supernatural origin, making two attacks per round with devastating power.",
    ),
    (
        "Legendary God-Titan",
        "Unnatural Entity",
        20,
        22,
        "+20 x3",
        "2d10+5",
        "10/-",
        "40'",
        10,
        3,
        "+3",
        "2+",
        "A legendary god-titan of immense power, making three attacks per round and applying massive Shock regardless of AC.",
    ),
]


def generate_monster_tables_markdown():
    """Generate markdown tables for all monster categories."""
    output = []

    output.append("\n## Monster and NPC Statistics Tables\n")
    output.append("**Type:** reference")
    output.append("**Tags:** reference, monsters, npcs, statistics, game-mastering\n")

    # Normal Humans table
    output.append("### Normal Humans\n")
    output.append("| HD | AC | Atk. | Dmg. | Shock | Move | ML | Inst. | Skill | Save |")
    output.append("|----|----|------|------|-------|------|-------|-------|-------|------|")
    for name, category, hd, ac, atk, dmg, shock, move, ml, inst, skill, save, _ in MONSTERS:
        if category == "Normal Human":
            output.append(
                f"| **{name}** | {hd} | {ac} | {atk} | {dmg} | {shock} | {move} | {ml} | {inst} | {skill} | {save} |"
            )

    # Spellcasters table
    output.append("\n### Spellcasters\n")
    output.append("| HD | AC | Atk. | Dmg. | Shock | Move | ML | Inst. | Skill | Save |")
    output.append("|----|----|------|------|-------|------|-------|-------|-------|------|")
    for name, category, hd, ac, atk, dmg, shock, move, ml, inst, skill, save, _ in MONSTERS:
        if category == "Spellcaster":
            output.append(
                f"| **{name}** | {hd} | {ac} | {atk} | {dmg} | {shock} | {move} | {ml} | {inst} | {skill} | {save} |"
            )
    output.append(
        "\nMages generally have the spellcasting and Arts of an appropriate mage tradition at a level equal to their hit dice and Effort equal to their skill bonus plus two.\n"
    )

    # Normal Animals table
    output.append("### Normal Animals\n")
    output.append("| HD | AC | Atk. | Dmg. | Shock | Move | ML | Inst. | Skill | Save |")
    output.append("|----|----|------|------|-------|------|-------|-------|-------|------|")
    for name, category, hd, ac, atk, dmg, shock, move, ml, inst, skill, save, _ in MONSTERS:
        if category == "Normal Animal":
            output.append(
                f"| **{name}** | {hd} | {ac} | {atk} | {dmg} | {shock} | {move} | {ml} | {inst} | {skill} | {save} |"
            )

    # Unnatural Entities table
    output.append("\n### Unnatural Entities\n")
    output.append("| HD | AC | Atk. | Dmg. | Shock | Move | ML | Inst. | Skill | Save |")
    output.append("|----|----|------|------|-------|------|-------|-------|-------|------|")
    for name, category, hd, ac, atk, dmg, shock, move, ml, inst, skill, save, _ in MONSTERS:
        if category == "Unnatural Entity":
            output.append(
                f"| **{name}** | {hd} | {ac} | {atk} | {dmg} | {shock} | {move} | {ml} | {inst} | {skill} | {save} |"
            )

    return "\n".join(output)


def post_monster_to_api(
    name, category, hd, ac, atk, dmg, shock, move, ml, inst, skill, save, description, api_url, api_key, ruleset_id
):
    """POST a single monster to the API."""

    payload = {
        "ruleset_id": ruleset_id,
        "type": "monster",
        "tags": ["monster", category.lower().replace(" ", "-")],
        "meta_data": {
            "monster_type": category,
            "HD": hd,
            "AC": ac,
            "Atk": atk,
            "Dmg": dmg,
            "Shock": shock,
            "Move": move,
            "ML": ml,
            "Inst": inst,
            "Skill": skill,
            "Save": save,
        },
        "translations": {"en": {"name": name, "description": description}},
    }

    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(f"{api_url}/rules/", json=payload, headers=headers)
        response.raise_for_status()
        print(f"✓ Posted: {name} ({category})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to post {name}: {e}")
        return False


def post_all_monsters(api_url="http://localhost:8000", api_key="dev-secret-key", ruleset_id=1):
    """POST all monsters to the API."""
    success_count = 0
    fail_count = 0

    for name, category, hd, ac, atk, dmg, shock, move, ml, inst, skill, save, description in MONSTERS:
        if post_monster_to_api(
            name,
            category,
            hd,
            ac,
            atk,
            dmg,
            shock,
            move,
            ml,
            inst,
            skill,
            save,
            description,
            api_url,
            api_key,
            ruleset_id,
        ):
            success_count += 1
        else:
            fail_count += 1

    print("\n--- Summary ---")
    print(f"Successfully posted: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total monsters: {len(MONSTERS)}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        post_all_monsters()
    else:
        print(generate_monster_tables_markdown())
