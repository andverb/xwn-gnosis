#!/usr/bin/env python3
"""
Elementalism spell data for WWN.
Each spell: (name, level, description)
"""

import sys

import requests

ELEMENTALISM_SPELLS = [
    (
        "Aqueous Harmony",
        1,
        "The elementalist and up to a dozen allies are charmed with powers of water-breathing, a tolerance for the pressure and cold of the deeps, and the ability to see through water as if it were well-lit air. Ensorceled beings may move freely while in the water at their usual movement rate and their attacks and projectile weapons are not hindered by the medium, nor are their possessions soaked or damaged. The spell lasts for one hour per caster level, but will not naturally end so long as a subject is still at least partially submerged. Only the caster or magical dispelling can stop it under those circumstances.",
    ),
    (
        "Boreal Wings",
        2,
        "The elementalist chooses a visible ally within one hundred feet; the target becomes capable of swift and easy aerial travel, flying at twice their usual movement rate. If the spell ends or is dispelled while aloft, the target descends gently to the earth. This spell lasts for one scene, though casters of fifth level or more can make it last an hour, and those of eighth level or more can make it last until dawn or dusk, whichever comes next.",
    ),
    (
        "The Burrower Below",
        2,
        "A passage is carved through natural stone or earth, forming a tunnel up to twenty feet long per caster level and up to ten feet wide and tall. The caster can cause the earth to compress and pack itself so as to stabilize the tunnel even in very sandy or burdened soil, or they can allow it to collapse naturally if burdened by some large structure or unstable surroundings. This spell can function against worked stone, but the length of the tunnel is much shorter, being only two feet per level. Magical stone or earth cannot be altered by this spell. The caster has basic control over the direction and interior features of the tunnel, and can form stairs or other simple structures within it.",
    ),
    (
        "Calcifying Scourge",
        4,
        "A visible target within one hundred feet must make a Physical saving throw or be turned to stone. Any size of living creature may be so transmuted, though inanimate objects larger than a cart cannot. Objects being held or worn by someone else get a Physical saving throw made by their user. The calcification remains until dispelled or the caster undoes the magic, but if the object or creature is damaged in the meanwhile, it may end up being harmed or killed on its restoration. If the Physical saving throw is made successfully by a creature, the target is temporarily slowed, losing its Move action for the next 1d6 rounds.",
    ),
    (
        "Elemental Favor",
        1,
        "The elementalist makes a direct appeal to a non-magical mass of earth, stone, water, flame, or air no larger than a ten-foot cube. At the end of the round, the mass will move or reshape itself within that space as the elementalist requests, maintaining its new form until the end of the scene. If its new shape is one that is stable without magical help, it can be told to remain in it after the spell is finished.",
    ),
    (
        "Elemental Guardian",
        4,
        "The elementalist imbues a human-sized mass of earth, water, fire, or air with a crude awareness and an eagerness to defend them. Whatever the substance used, it now has 4 HD, AC 15, a Move of 40'/action, a +1 skill bonus, saves of 13+, Instinct 0, Morale 12, and a melee attack of +6/1d10 with no Shock. If called from earth, it has 6 hit dice, albeit its other stats don't change. If called from fire, it does 5/- Shock damage. If summoned from water, it has an AC of 18, and if called from air, it can fly at its usual movement rate. It has a human degree of intelligence, can communicate with others and manipulate objects, and serves with suicidal devotion. Only one elemental guardian can be summoned at any one time, and if destroyed, a new one cannot be called that same scene. A guardian persists until destroyed or until the dawn after they have been summoned.",
    ),
    (
        "Elemental Spy",
        1,
        "The elementalist enchants a stone, ounce of liquid, flame no smaller than a candleflame, or a particular plume of smoke or incense. For one day per level, so long as the charmed object is not destroyed, dispersed, or consumed, they can as a Main Action see and listen to anything around the object as if they were standing there.",
    ),
    (
        "Elemental Vallation",
        3,
        "A wall of a chosen churning elemental force can be called up by the elementalist. The barrier is ten feet long per character level, with a height of ten feet and a thickness of one foot. The barrier must rest on solid ground but may be bent or shaped as desired so long as no part of it is more than two hundred feet from the caster. Earthen walls are impervious to anything but mining-appropriate tools or rock-shattering strength, taking 20 HP of damage to knock a man-sized hole in them. Fire walls inflict 3d6 damage plus the elementalist's level on anyone who passes through them. Water walls spin and hurl creatures of ox-size or less who pass through them, ejecting them at a random point on the far side of the wall and doing 2d6 damage from the buffeting. Air walls are invisible, inaudible, and twenty feet in height; those who cross them suffer 1d6 plus the elementalist's level in electrical damage. The walls vanish at the end of the scene.",
    ),
    (
        "Flame Scrying",
        1,
        "The elementalist becomes aware of the approximate locations of all open flames within thirty feet per caster level. They may choose one of those flames as a focus for the scrying, allowing them to see and hear everything around the flame as if they were present. The spell's duration lasts for as long as the elementalist remains motionlessly focused on it; during this duration, they may switch their focus between the various flames in range as they wish.",
    ),
    (
        "Flame Without End",
        2,
        "A sample of flame no larger than the caster is made effectively eternal. It no longer consumes the object it burns, though it can still be used to burn or heat other things, and it resists all extinguishing save being buried or wholly immersed in water. The elementalist can temporarily extinguish it at will. A number of such flames can be created equal to the elementalist's level; beyond that, special ingredients and fuels are needed that cost 500 silver pieces per flame. If used as a weapon, it adds +2 damage to a successful hit, albeit nothing to Shock. The flame lasts until dispelled, extinguished, or the elementalist releases it.",
    ),
    (
        "Fury of the Elements",
        5,
        "A combination of molten rock, searing pyroclastic winds, and superheated steam erupts forth to ravage a chosen target point within two hundred feet per caster level. The cataclysmic ruin smites everything within thirty feet of the target point for 10d6 damage, destroying all conventional structures. The zone of devastation then moves 1d6x10 feet in a random direction at the start of the next round, blasting everything in its path. The zone will continue to wander in this fashion for 1d6 rounds in total before dying out. The molten remnants of the spell remain after this duration, a hazard for whomever enters the area for the rest of the day.",
    ),
    (
        "Like the Stones",
        3,
        "The elementalist charges their physical shape with the qualities of a chosen element for the rest of the scene. In all cases, they need not breathe and become immune to poisons and diseases not already present in them. If stone, they automatically stabilize at zero hit points and ignore the first three points of damage from any source of harm. If water, they can pass through any aperture a mouse could get through. If air, they can fly at their usual movement rate and gain a +4 Armor Class bonus against ranged attacks. If fire, they inflict 1d6 damage to all creatures in melee range at the start of their turn each round and become immune to heat damage.",
    ),
    (
        "Pact of Stone and Sea",
        2,
        "The elementalist chooses earth, water, fire, or wind when casting this spell and selects a visible target to be affected. For the rest of the scene, the target is immune to injury caused by mundane manifestations of that substance; stone weapons don't harm them, water doesn't drown them, fire doesn't burn them, and wind doesn't topple them. This affects secondary effects of the material as well; a fire-pacted mage couldn't be boiled in a pot, and an earth-pacted one won't be suffocated if buried alive.",
    ),
    (
        "Tremors of the Depths",
        5,
        "The elementalist calls up a deep, rolling tremor from within the earth, centering it on a visible point and affecting all structures in a radius of up to five hundred feet. This spell's effects build slowly, requiring five minutes to fully manifest, but they can successfully topple or destroy any structures, tunnels, or caves within the affected area unless such structures are magically reinforced. The effects are negated if the spell is dispelled within a minute after it was cast; after that, it's too late to stop the effect.",
    ),
    (
        "Wind Walking",
        3,
        "A visible target creature and their possessions are briefly transformed into a misty, insubstantial cloud. Only sources of harm that could conceivably disrupt a cloud of mist can harm them, and until the spell's end they may pass freely into any area that a vapor could reach. They may move freely in all three dimensions at their normal movement rate, though they cannot physically manipulate objects. The spell lasts until the end of the scene or until the target or the caster choose to end it.",
    ),
]


def generate_spell_markdown(name, level, description):
    """Generate markdown for a single spell entry."""
    return f"""
## Spell: {name}
**Type:** spell
**Tags:** spell, elementalism, level-{level}

### {name}
**Level:** {level}

{description}
"""


def generate_all_spells_markdown():
    """Generate markdown for all Elementalism spells."""
    output = []
    for name, level, description in ELEMENTALISM_SPELLS:
        output.append(generate_spell_markdown(name, level, description))
    return "\n".join(output)


def post_spell_to_api(name, level, description, api_url, api_key, ruleset_id):
    """POST a single spell to the API."""

    payload = {
        "ruleset_id": ruleset_id,
        "type": "spell",
        "tags": ["spell", "elementalism", f"level-{level}"],
        "meta_data": {"school": "Elementalism", "spell_level": level},
        "translations": {"en": {"name": name, "description": description}},
    }

    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(f"{api_url}/rules/", json=payload, headers=headers)
        response.raise_for_status()
        print(f"✓ Posted: {name} (Level {level})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to post {name}: {e}")
        return False


def post_all_spells(api_url="http://localhost:8000", api_key="dev-secret-key", ruleset_id=1):
    """POST all Elementalism spells to the API."""
    success_count = 0
    fail_count = 0

    for name, level, description in ELEMENTALISM_SPELLS:
        if post_spell_to_api(name, level, description, api_url, api_key, ruleset_id):
            success_count += 1
        else:
            fail_count += 1

    print("\n--- Summary ---")
    print(f"Successfully posted: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total spells: {len(ELEMENTALISM_SPELLS)}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        post_all_spells()
    else:
        print(generate_all_spells_markdown())
