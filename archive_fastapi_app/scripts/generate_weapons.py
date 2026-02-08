weapons_data = [
    (
        "Small Bow",
        "weapon, bow, ranged, two-handed",
        "Bows cover everything from the small self bows of horse archers to the man-tall longbows wielded by foot archers.",
        "2H, R, PM",
    ),
    (
        "Claw Blades",
        "weapon, blade, melee, subtle",
        "Claw blades are the sharper kin of fist loads, being small blades or finger talons that are easily concealed or disguised as metal ornaments. While they are vicious weapons, they can't be usefully thrown.",
        "S",
    ),
    (
        "Club",
        "weapon, club, melee, throwable, less-lethal",
        "Clubs, staves, and maces are of much the same genus. While fully capable of killing a man, a careful user can usually avoid inflicting lethal injury.",
        "T, LL",
    ),
    (
        "Great Club",
        "weapon, club, melee, two-handed",
        "Clubs, staves, and maces are of much the same genus, though great clubs require two hands to wield effectively.",
        "2H",
    ),
    (
        "Crossbow",
        "weapon, crossbow, ranged, two-handed",
        "Crossbows come in heavier varieties than the one listed, but such slow, bulky arbalests are rarely in the hands of adventurers. Reloading a crossbow of this size takes a full Main Action, but due to the simplicity of their operation, someone without Shoot-0 can still use them at no unskilled hit penalty.",
        "2H, SR, PM",
    ),
    (
        "Dagger",
        "weapon, dagger, blade, melee, throwable, subtle",
        "Daggers come in ten thousand varieties, but the listed kind is a common fighting dirk, big enough to push through light armor while remaining small enough to be discreetly hidden.",
        "S, T, PM",
    ),
    (
        "Halberd",
        "weapon, polearm, melee, two-handed, long",
        "Halberds and other polearms can be somewhat awkward in narrow spaces, but remain popular military weapons in some armies. The statistics given here can also be used for fauchards, bills, voulges, spetums, bardiches, glaives, guisarmes, guisarme-glaives, glaive-guisarme-glaives, and similar weapons.",
        "2H, L",
    ),
    (
        "Great Hammer",
        "weapon, hammer, melee, two-handed",
        "Hammers listed here are the fighting variety, narrow-headed and made for penetrating or shocking heavy plates of armor.",
        "2H",
    ),
    (
        "War Hammer",
        "weapon, hammer, melee",
        "Hammers listed here are the fighting variety, narrow-headed and made for penetrating or shocking heavy plates of armor.",
        "",
    ),
    (
        "Great Hurlant",
        "weapon, hurlant, ranged, fixed",
        "Great hurlants are usually eight feet long and hundreds of pounds in weight, and launch tremendous bolts that can transfix even monstrous targets. Those able to afford their use generally mount them on ships, gun carriages, or on important fortifications.",
        "FX, SS, AP",
    ),
    (
        "Hand Hurlant",
        "weapon, hurlant, ranged",
        "Hand hurlants are usually pistol-sized, most often carried by the wealthy as a single-shot opener at the start of hostilities.",
        "SS, AP",
    ),
    (
        "Long Hurlant",
        "weapon, hurlant, ranged, two-handed",
        "Long hurlants are rifle-sized weapons favored by elite snipers and assassins who don't expect a need for a second shot.",
        "2H, SS, AP, PM",
    ),
    (
        "Mace",
        "weapon, mace, melee, less-lethal",
        "Clubs, staves, and maces are of much the same genus, though the latter is usually made of metal. While fully capable of killing a man, a careful user can usually avoid inflicting lethal injury.",
        "LL",
    ),
    (
        "Pike",
        "weapon, polearm, melee, two-handed, long",
        "Spears, and their longer cousin the pike, are common military weapons. Heavier two-handed versions penetrate armor well.",
        "2H, L",
    ),
    (
        "Large Shield Bash",
        "weapon, shield, melee, less-lethal",
        "Shields can be an effective weapon when used to bash or pummel an enemy. If used as a weapon or as part of a dual-wielding attack, a shield grants no AC or Shock protection benefits until the wielder's next turn.",
        "LL",
    ),
    (
        "Small Shield Bash",
        "weapon, shield, melee, less-lethal",
        "Shields can be an effective weapon when used to bash or pummel an enemy. If used as a weapon or as part of a dual-wielding attack, a shield grants no AC or Shock protection benefits until the wielder's next turn.",
        "LL",
    ),
    (
        "Heavy Spear",
        "weapon, spear, polearm, melee, two-handed",
        "Spears, and their longer cousin the pike, are common military weapons. Heavier two-handed versions penetrate armor well.",
        "2H",
    ),
    (
        "Light Spear",
        "weapon, spear, melee, throwable",
        "Spears are common military weapons. Lighter spears are effective thrown weapons.",
        "T",
    ),
    (
        "Staff",
        "weapon, staff, melee, two-handed, less-lethal",
        "Clubs, staves, and maces are of much the same genus. While fully capable of killing a man, a careful user can usually avoid inflicting lethal injury.",
        "2H, LL",
    ),
    (
        "Stiletto",
        "weapon, dagger, blade, melee, subtle",
        "Stilettos and similar armor-piercing daggers aren't usually effective as thrown weapons.",
        "S, PM",
    ),
    (
        "Great Sword",
        "weapon, sword, blade, melee, two-handed",
        "Swords are common sidearms for the gentry. The expense of forging a large blade makes it a symbol of wealth and status in many cultures.",
        "2H",
    ),
    (
        "Long Sword",
        "weapon, sword, blade, melee",
        "Swords are common sidearms for the gentry. The expense of forging a large blade makes it a symbol of wealth and status in many cultures, and its convenience makes it a favored arm for street wear.",
        "",
    ),
    ("Short Sword", "weapon, sword, blade, melee", "Swords are common sidearms for the gentry.", ""),
    (
        "Throwing Blade",
        "weapon, blade, ranged, throwable, subtle",
        "Throwing blades are small leaves or spikes of steel that are not terribly useful as melee weapons but are easy to carry discreetly in considerable numbers.",
        "S, T, N",
    ),
    (
        "Unarmed Attack",
        "weapon, unarmed, melee",
        "The unarmed attack given here is a common punch or kick, unimproved by a Vowed's arts or a Focus. Unarmed attacks add the assailant's Punch skill to the damage roll as well as the attack roll.",
        "",
    ),
]

trait_desc = {
    "AP": "Armor Piercing - This weapon ignores non-magical hides, armor and shields for purposes of its hit rolls.",
    "FX": "Fixed - The weapon is too heavy and clumsy to use without a fixed position and at least five minutes to entrench it.",
    "L": "Long - The weapon is unusually long, allowing melee attacks to be made at targets up to 10 feet distant, even if an ally is in the way. Even so, the wielder still needs to be within five feet of a foe to count as being in melee with them for purposes of forcing Fighting Withdrawals, disrupting large ranged weapons, or similar maneuvers.",
    "LL": "Less Lethal - Foes brought to zero hit points by this weapon can always be left alive at the wielder's discretion.",
    "N": "Numerous - Five of these count as only one Readied item.",
    "PM": "Precisely Murderous - When used for an Execution Attack, the weapon applies an additional -1 penalty to the Physical save and does double damage even if it succeeds.",
    "R": "Reload - The weapon takes a Move action to reload. If the user has at least Shoot-1 skill, they can reload as an On Turn action instead.",
    "S": "Subtle - Can be easily hidden in clothing or jewelry.",
    "SR": "Slow Reload - It takes a Main Action to reload this weapon.",
    "SS": "Single Shot - This weapon takes ten rounds to reload, and the reloading effort is spoiled if an enemy melees the wielder.",
    "T": "Throwable - While the weapon can be used in melee, it may be thrown out to the listed range as well, albeit it does no Shock in that case. Throwing a weapon while in melee applies a -4 penalty to the hit roll.",
    "2H": "Two Handed - The weapon requires two hands to use in combat. Ranged two-handed weapons cannot be fired effectively while an enemy is within melee range.",
}

for name, tags, desc, traits in weapons_data:
    print(f"\n## Weapon: {name}")
    print("**Type:** weapon")
    print(f"**Tags:** {tags}")
    print(f"\n### {name}")
    print(f"\n{desc}")
    if traits:
        trait_list = [t.strip() for t in traits.split(",")]
        trait_explanations = [f"{t} ({trait_desc[t]})" for t in trait_list if t in trait_desc]
        if trait_explanations:
            print(f"\n**Traits:** {', '.join(trait_explanations)}")
    print()
