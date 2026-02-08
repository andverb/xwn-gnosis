#!/usr/bin/env python3
"""
Script to POST all weapon entries to the Gnosis API with metadata.
"""

import requests

API_URL = "http://localhost:8000/rules/"
API_KEY = "dev-secret-key"
RULESET_ID = 1

# Weapon data: (name, damage, shock, attribute, range, traits, cost, enc, tags, description, trait_descriptions)
weapons = [
    (
        "Hand Axe",
        "1d6",
        "1/AC 15",
        "Str/Dex",
        "10/30",
        "T",
        "10 sp",
        1,
        "weapon, axe, melee, throwable",
        "Axes given here are those fashioned for war; lighter and more agile than their working cousins, though still capable of hacking through a door or hewing a cable if needed.",
        "T (Throwable - While the weapon can be used in melee, it may be thrown out to the listed range as well, albeit it does no Shock in that case. Throwing a weapon while in melee applies a -4 penalty to the hit roll.)",
    ),
    (
        "War Axe",
        "1d10",
        "3/AC 15",
        "Str",
        "-",
        "2H",
        "50 sp",
        2,
        "weapon, axe, melee, two-handed",
        "War axes are big enough to demand two hands for their use.",
        "2H (Two Handed - The weapon requires two hands to use in combat.)",
    ),
    (
        "Blackjack",
        "1d4",
        "None",
        "Str/Dex",
        "-",
        "S, LL",
        "1 sp",
        1,
        "weapon, club, melee, subtle, less-lethal",
        "Blackjacks include not only obvious weapons loaded with sand or iron shot, but any small, stunning fist load. A blackjack or other small fist load is easily concealed as some ornamental component of ordinary clothing.",
        "S (Subtle - Can be easily hidden in clothing or jewelry), LL (Less Lethal - Foes brought to zero hit points by this weapon can always be left alive at the wielder's discretion.)",
    ),
    (
        "Large Bow",
        "1d8",
        "None",
        "Dex",
        "100/600",
        "2H, R, PM",
        "20 sp",
        2,
        "weapon, bow, ranged, two-handed",
        "Bows cover everything from the small self bows of horse archers to the man-tall longbows wielded by foot archers. Larger bows are more cumbersome and impossible to shoot from horseback, but usually have superior strength. An archer with a Readied quiver can load a fresh arrow as a Move action each turn, or as an On Turn action if they have at least Shoot-1 skill.",
        "2H (Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.), R (Reload - The weapon takes a Move action to reload. If the user has at least Shoot-1 skill, they can reload as an On Turn action instead.), PM (Precisely Murderous - When used for an Execution Attack, the weapon applies an additional -1 penalty to the Physical save and does double damage even if it succeeds.)",
    ),
    (
        "Small Bow",
        "1d6",
        "None",
        "Dex",
        "50/300",
        "2H, R, PM",
        "20 sp",
        1,
        "weapon, bow, ranged, two-handed",
        "Bows cover everything from the small self bows of horse archers to the man-tall longbows wielded by foot archers.",
        "2H (Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.), R (Reload - The weapon takes a Move action to reload. If the user has at least Shoot-1 skill, they can reload as an On Turn action instead.), PM (Precisely Murderous - When used for an Execution Attack, the weapon applies an additional -1 penalty to the Physical save and does double damage even if it succeeds.)",
    ),
    (
        "Claw Blades",
        "1d6",
        "2/AC 13",
        "Str/Dex",
        "-",
        "S",
        "10 sp",
        1,
        "weapon, blade, melee, subtle",
        "Claw blades are the sharper kin of fist loads, being small blades or finger talons that are easily concealed or disguised as metal ornaments. While they are vicious weapons, they can't be usefully thrown.",
        "S (Subtle - Can be easily hidden in clothing or jewelry.)",
    ),
    (
        "Club",
        "1d4",
        "None",
        "Str/Dex",
        "10/30",
        "T, LL",
        "-",
        1,
        "weapon, club, melee, throwable, less-lethal",
        "Clubs, staves, and maces are of much the same genus. While fully capable of killing a man, a careful user can usually avoid inflicting lethal injury.",
        "T (Throwable - While the weapon can be used in melee, it may be thrown out to the listed range as well, albeit it does no Shock in that case. Throwing a weapon while in melee applies a -4 penalty to the hit roll.), LL (Less Lethal - Foes brought to zero hit points by this weapon can always be left alive at the wielder's discretion.)",
    ),
    (
        "Great Club",
        "1d10",
        "2/AC 15",
        "Str",
        "-",
        "2H",
        "1 sp",
        2,
        "weapon, club, melee, two-handed",
        "Clubs, staves, and maces are of much the same genus, though great clubs require two hands to wield effectively.",
        "2H (Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.)",
    ),
    (
        "Crossbow",
        "1d10",
        "None",
        "Dex",
        "100/300",
        "2H, SR, PM",
        "10 sp",
        1,
        "weapon, crossbow, ranged, two-handed",
        "Crossbows come in heavier varieties than the one listed, but such slow, bulky arbalests are rarely in the hands of adventurers. Reloading a crossbow of this size takes a full Main Action, but due to the simplicity of their operation, someone without Shoot-0 can still use them at no unskilled hit penalty.",
        "2H (Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.), SR (Slow Reload - It takes a Main Action to reload this weapon.), PM (Precisely Murderous - When used for an Execution Attack, the weapon applies an additional -1 penalty to the Physical save and does double damage even if it succeeds.)",
    ),
    (
        "Dagger",
        "1d4",
        "1/AC 15",
        "Str/Dex",
        "30/60",
        "S, T, PM",
        "3 sp",
        1,
        "weapon, dagger, blade, melee, throwable, subtle",
        "Daggers come in ten thousand varieties, but the listed kind is a common fighting dirk, big enough to push through light armor while remaining small enough to be discreetly hidden.",
        "S (Subtle - Can be easily hidden in clothing or jewelry.), T (Throwable - While the weapon can be used in melee, it may be thrown out to the listed range as well, albeit it does no Shock in that case. Throwing a weapon while in melee applies a -4 penalty to the hit roll.), PM (Precisely Murderous - When used for an Execution Attack, the weapon applies an additional -1 penalty to the Physical save and does double damage even if it succeeds.)",
    ),
    (
        "Halberd",
        "1d10",
        "2/AC 15",
        "Str",
        "-",
        "2H, L",
        "50 sp",
        2,
        "weapon, polearm, melee, two-handed, long",
        "Halberds and other polearms can be somewhat awkward in narrow spaces, but remain popular military weapons in some armies. The statistics given here can also be used for fauchards, bills, voulges, spetums, bardiches, glaives, guisarmes, guisarme-glaives, glaive-guisarme-glaives, and similar weapons.",
        "2H (Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.), L (Long - The weapon is unusually long, allowing melee attacks to be made at targets up to 10 feet distant, even if an ally is in the way. Even so, the wielder still needs to be within five feet of a foe to count as being in melee with them for purposes of forcing Fighting Withdrawals, disrupting large ranged weapons, or similar maneuvers.)",
    ),
    (
        "Great Hammer",
        "1d10",
        "2/AC 18",
        "Str",
        "-",
        "2H",
        "50 sp",
        2,
        "weapon, hammer, melee, two-handed",
        "Hammers listed here are the fighting variety, narrow-headed and made for penetrating or shocking heavy plates of armor.",
        "2H (Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.)",
    ),
    (
        "War Hammer",
        "1d8",
        "1/AC 18",
        "Str",
        "-",
        "",
        "30 sp",
        1,
        "weapon, hammer, melee",
        "Hammers listed here are the fighting variety, narrow-headed and made for penetrating or shocking heavy plates of armor.",
        "",
    ),
    (
        "Great Hurlant",
        "3d10",
        "None",
        "Dex",
        "600/2400",
        "FX, SS, AP",
        "10000 sp",
        15,
        "weapon, hurlant, ranged, fixed",
        "Great hurlants are usually eight feet long and hundreds of pounds in weight, and launch tremendous bolts that can transfix even monstrous targets. Those able to afford their use generally mount them on ships, gun carriages, or on important fortifications.",
        "FX (Fixed - The weapon is too heavy and clumsy to use without a fixed position and at least five minutes to entrench it.), SS (Single Shot - This weapon takes ten rounds to reload, and the reloading effort is spoiled if an enemy melees the wielder.), AP (Armor Piercing - This weapon ignores non-magical hides, armor and shields for purposes of its hit rolls.)",
    ),
    (
        "Hand Hurlant",
        "1d12",
        "None",
        "Dex",
        "30/60",
        "SS, AP",
        "1000 sp",
        1,
        "weapon, hurlant, ranged",
        "Hand hurlants are usually pistol-sized, most often carried by the wealthy as a single-shot opener at the start of hostilities.",
        "SS (Single Shot - This weapon takes ten rounds to reload, and the reloading effort is spoiled if an enemy melees the wielder.), AP (Armor Piercing - This weapon ignores non-magical hides, armor and shields for purposes of its hit rolls.)",
    ),
    (
        "Long Hurlant",
        "2d8",
        "None",
        "Dex",
        "200/600",
        "2H, SS, AP, PM",
        "4000 sp",
        2,
        "weapon, hurlant, ranged, two-handed",
        "Long hurlants are rifle-sized weapons favored by elite snipers and assassins who don't expect a need for a second shot.",
        "2H (Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.), SS (Single Shot - This weapon takes ten rounds to reload, and the reloading effort is spoiled if an enemy melees the wielder.), AP (Armor Piercing - This weapon ignores non-magical hides, armor and shields for purposes of its hit rolls.), PM (Precisely Murderous - When used for an Execution Attack, the weapon applies an additional -1 penalty to the Physical save and does double damage even if it succeeds.)",
    ),
    (
        "Mace",
        "1d6",
        "1/AC 18",
        "Str",
        "-",
        "LL",
        "15 sp",
        1,
        "weapon, mace, melee, less-lethal",
        "Clubs, staves, and maces are of much the same genus, though the latter is usually made of metal. While fully capable of killing a man, a careful user can usually avoid inflicting lethal injury.",
        "LL (Less Lethal - Foes brought to zero hit points by this weapon can always be left alive at the wielder's discretion.)",
    ),
    (
        "Pike",
        "1d8",
        "1/AC 18",
        "Str",
        "-",
        "2H, L",
        "10 sp",
        2,
        "weapon, polearm, melee, two-handed, long",
        "Spears, and their longer cousin the pike, are common military weapons. Heavier two-handed versions penetrate armor well.",
        "2H (Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.), L (Long - The weapon is unusually long, allowing melee attacks to be made at targets up to 10 feet distant, even if an ally is in the way. Even so, the wielder still needs to be within five feet of a foe to count as being in melee with them for purposes of forcing Fighting Withdrawals, disrupting large ranged weapons, or similar maneuvers.)",
    ),
    (
        "Large Shield Bash",
        "1d6",
        "1/AC 13",
        "Str",
        "-",
        "LL",
        "-",
        0,
        "weapon, shield, melee, less-lethal",
        "Shields can be an effective weapon when used to bash or pummel an enemy. If used as a weapon or as part of a dual-wielding attack, a shield grants no AC or Shock protection benefits until the wielder's next turn.",
        "LL (Less Lethal - Foes brought to zero hit points by this weapon can always be left alive at the wielder's discretion.)",
    ),
    (
        "Small Shield Bash",
        "1d4",
        "None",
        "Str/Dex",
        "-",
        "LL",
        "-",
        0,
        "weapon, shield, melee, less-lethal",
        "Shields can be an effective weapon when used to bash or pummel an enemy. If used as a weapon or as part of a dual-wielding attack, a shield grants no AC or Shock protection benefits until the wielder's next turn.",
        "LL (Less Lethal - Foes brought to zero hit points by this weapon can always be left alive at the wielder's discretion.)",
    ),
    (
        "Heavy Spear",
        "1d10",
        "2/AC 15",
        "Str",
        "-",
        "2H",
        "10 sp",
        2,
        "weapon, spear, polearm, melee, two-handed",
        "Spears, and their longer cousin the pike, are common military weapons. Heavier two-handed versions penetrate armor well.",
        "2H (Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.)",
    ),
    (
        "Light Spear",
        "1d6",
        "2/AC 13",
        "Str/Dex",
        "30/60",
        "T",
        "5 sp",
        1,
        "weapon, spear, melee, throwable",
        "Spears are common military weapons. Lighter spears are effective thrown weapons.",
        "T (Throwable - While the weapon can be used in melee, it may be thrown out to the listed range as well, albeit it does no Shock in that case. Throwing a weapon while in melee applies a -4 penalty to the hit roll.)",
    ),
    (
        "Staff",
        "1d6",
        "1/AC 13",
        "Str/Dex",
        "-",
        "2H, LL",
        "1 sp",
        1,
        "weapon, staff, melee, two-handed, less-lethal",
        "Clubs, staves, and maces are of much the same genus. While fully capable of killing a man, a careful user can usually avoid inflicting lethal injury.",
        "2H (Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.), LL (Less Lethal - Foes brought to zero hit points by this weapon can always be left alive at the wielder's discretion.)",
    ),
    (
        "Stiletto",
        "1d4",
        "1/AC 18",
        "Dex",
        "-",
        "S, PM",
        "10 sp",
        1,
        "weapon, dagger, blade, melee, subtle",
        "Stilettos and similar armor-piercing daggers aren't usually effective as thrown weapons.",
        "S (Subtle - Can be easily hidden in clothing or jewelry.), PM (Precisely Murderous - When used for an Execution Attack, the weapon applies an additional -1 penalty to the Physical save and does double damage even if it succeeds.)",
    ),
    (
        "Great Sword",
        "1d12",
        "2/AC 15",
        "Str",
        "-",
        "2H",
        "250 sp",
        2,
        "weapon, sword, blade, melee, two-handed",
        "Swords are common sidearms for the gentry. The expense of forging a large blade makes it a symbol of wealth and status in many cultures.",
        "2H (Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.)",
    ),
    (
        "Long Sword",
        "1d8",
        "2/AC 13",
        "Str/Dex",
        "-",
        "",
        "100 sp",
        1,
        "weapon, sword, blade, melee",
        "Swords are common sidearms for the gentry. The expense of forging a large blade makes it a symbol of wealth and status in many cultures, and its convenience makes it a favored arm for street wear.",
        "",
    ),
    (
        "Short Sword",
        "1d6",
        "2/AC 15",
        "Str/Dex",
        "-",
        "",
        "10 sp",
        1,
        "weapon, sword, blade, melee",
        "Swords are common sidearms for the gentry.",
        "",
    ),
    (
        "Throwing Blade",
        "1d4",
        "None",
        "Dex",
        "30/60",
        "S, T, N",
        "3 sp",
        1,
        "weapon, blade, ranged, throwable, subtle",
        "Throwing blades are small leaves or spikes of steel that are not terribly useful as melee weapons but are easy to carry discreetly in considerable numbers.",
        "S (Subtle - Can be easily hidden in clothing or jewelry.), T (Throwable - While the weapon can be used in melee, it may be thrown out to the listed range as well, albeit it does no Shock in that case. Throwing a weapon while in melee applies a -4 penalty to the hit roll.), N (Numerous - Five of these count as only one Readied item.)",
    ),
    (
        "Unarmed Attack",
        "1d2+Skill",
        "None",
        "Str/Dex",
        "-",
        "",
        "-",
        0,
        "weapon, unarmed, melee",
        "The unarmed attack given here is a common punch or kick, unimproved by a Vowed's arts or a Focus. Unarmed attacks add the assailant's Punch skill to the damage roll as well as the attack roll.",
        "",
    ),
]


def post_weapon(name, damage, shock, attribute, range_str, traits, cost, enc, tags, description, trait_desc):
    """POST a weapon entry to the API with metadata."""

    # Build metadata
    metadata = {
        "damage": damage,
        "shock": shock,
        "attribute": attribute,
        "cost": cost,
        "encumbrance": enc,
    }

    if range_str and range_str != "-":
        metadata["range"] = range_str

    if traits:
        metadata["traits"] = traits

    # Build description with trait descriptions
    full_desc = f"### {name}\n\n{description}"
    if trait_desc:
        full_desc += f"\n\n**Traits:** {trait_desc}"

    payload = {
        "ruleset_id": RULESET_ID,
        "type": "weapon",
        "tags": tags.split(", "),
        "meta_data": metadata,
        "translations": {"en": {"name": name, "description": full_desc}},
    }

    headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        print(f"✓ Created #{result['id']}: {name}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to create {name}: {e}")
        return None


def main():
    print(f"Posting {len(weapons)} weapons to API...")
    print()

    success_count = 0
    for weapon_data in weapons:
        result = post_weapon(*weapon_data)
        if result:
            success_count += 1

    print()
    print(f"Complete! Posted {success_count}/{len(weapons)} weapons successfully.")


if __name__ == "__main__":
    main()
