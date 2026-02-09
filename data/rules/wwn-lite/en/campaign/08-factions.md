## Factions

Factions have statistics defining their qualities. Weak/small factions tend to have low ratings even in their focus, while kingdoms may have good ratings even in less important traits due to sheer resources.

### Faction Statistics

**Cunning** (1-8): Guile, subterfuge, and subtlety. Low = straightforward; High = Machiavellian schemers.

**Force** (1-8): Military prowess and martial competence. Low = unused to violence; High = culture of military expertise.

**Wealth** (1-8): Prosperity, material resources, and facility with money. Low = poor or spendthrift; High = rich and skilled at using money as a tool.

**Magic**: Magical resources available to the faction.
- **None** - No meaningful access to magic
- **Low** - A few trained mages or small stores of magical goods
- **Medium** - Established source of magical power (cooperative mages, academy, sorcery tradition)
- **High** - Strong focus on wielding magical power (magical orders)

**Treasure**: Points representing cash and valuable goods. No fixed cash value per point - it represents whatever resources the faction needs.

**Hit Points**: When reduced to zero, the faction collapses. Members may survive, but the faction ceases to exist as a coherent whole.

**Assets**: Important resources (e.g., Smugglers, Infantry). Each has its own stats and HP, and requires certain Force, Wealth, Cunning, and Magic scores to purchase. They represent the faction's most relevant current resources, not everything it controls.

---

### The Faction Turn

Run a faction turn roughly every month (or after every adventure). More often during intense activity, less often when quiet.

**Initiative**: Each faction rolls 1d8; highest goes first. GM resolves ties.

Each faction takes these steps in order:

1. **Earn Treasure** = ½ Wealth + ¼(Force + Cunning), rounded up
2. **Pay Upkeep** for Assets. If unable to pay individual Asset upkeep, those Assets suffer consequences. If unable to pay for excess Assets (more Assets of a type than the attribute score), lose the excess.
3. **Trigger Asset Special Abilities** (movement, special benefits, etc.)
4. **Take One Faction Action** (see below). When an action is chosen, every qualifying Asset may take it (e.g., if Attack is chosen, all valid Assets can Attack).
5. **Check Goal Completion**. If accomplished, collect XP and pick a new goal. May abandon a goal for a new one, but sacrifices next turn's Faction Action and cannot trigger Asset special abilities that round.

---

### Asset Locations & Movement

Every Asset has a location on the campaign map - its center of gravity. Usually a town or settlement, but can be anywhere logical (wilderness, hidden cave, etc.).

Assets move via the **Move Asset** action or special abilities. Per move: ~100 miles for a one-month turn. GM adjusts for terrain and circumstances.

Some Asset abilities affect targets **within one move** (~100 miles).

**Movement Restrictions**: Some Assets can't logically enter certain locations (e.g., Infantry can't walk into an enemy capital). They'd need to move nearby and wait.

**Subtle Assets**: Can move to locations normally prohibited by ruling powers. Must be Attacked to dislodge or moved out by owner.

**Stealthed Assets**: Move freely to any location within reach. Cannot be Attacked until they lose Stealth (by being discovered or by Attacking something).

---

### Attribute Checks

Both attacker and defender roll **1d10 + relevant attribute**. Attacker wins if higher; defender wins on ties.

Some abilities/tags allow rolling more than one die - use the highest result.

---

### Faction Tags

The GM may devise others to suit their needs.

**Antimagical**: Assets requiring Medium+ Magic roll attribute checks twice against this faction during Attack and take the worst roll.

**Concealed**: All purchased Assets enter play with the Stealth quality.

**Imperialist**: Once per turn, can use Expand Influence as a special ability instead of a full action.

**Innovative**: Can purchase Assets as if attributes were 2 points higher. Max 2 such over-complex Assets at any time.

**Machiavellian**: Rolls an extra die for all Cunning checks. Cunning must always be its highest attribute.

**Martial**: Rolls an extra die for all Force checks. Force must always be its highest attribute.

**Massive**: Auto-wins attribute checks if its attribute is more than 2x the opponent's, unless the opponent is also Massive.

**Mobile**: Faction turn movement range is doubled.

**Populist**: Assets costing 5 Treasure or less cost 1 less (minimum 1).

**Rich**: Rolls an extra die for all Wealth checks. Wealth must always be its highest attribute.

---

### Faction Turn Actions

**Attack**: Nominate one or more Assets to attack enemies in their locations. The defender chooses which Asset meets each Attack.

- Attacker makes an attribute check based on the attacking Asset's type (e.g., Infantry rolls Force vs Force).
- **Success**: Defending Asset takes damage = attacker's attack score.
- **Failure**: Attacking Asset takes damage = defender's counterattack score.
- An Asset at 0 HP is destroyed. The same Asset can defend against multiple attacks if it survives.
- Damage to a Base of Influence is also dealt to the faction's HP (no overflow).

**Move Asset**: Move one or more Assets up to one turn's distance. The destination must not forbid the Asset's presence. Subtle and Stealthed Assets ignore this.

- If an Asset loses Subtle/Stealth in a hostile location, it must retreat within one turn or take half its max HP in damage (rounded up) at the start of the next turn.

**Repair Asset**: Spend 1 Treasure per Asset to heal half the relevant attribute value in HP (rounded up). E.g., fixing a Force Asset heals ½ the faction's Force, rounded up. Additional repairs on the same Asset cost +1 Treasure each (2nd costs 2, 3rd costs 3, etc.).

- Can also repair the faction itself: spend 1 Treasure to heal (highest + lowest attribute) / 2, rounded up. E.g., Force 5, Wealth 2, Cunning 4 heals (5+2)/2 = 4 HP. Only once per turn.

**Expand Influence**: Establish a new Base of Influence. Requires at least one Asset already at the location. Cost: 1 Treasure per HP the new Base will have.

- After creation, make a Cunning vs Cunning check against every faction with Assets there. If the rival wins, they may immediately Attack the new Base. The creator can defend with other Assets present.
- If it survives, it operates normally and allows purchasing Assets via Create Asset.

**Create Asset**: Buy one Asset at a location with a Base of Influence. Must meet minimum attribute & Magic requirements and pay the Treasure cost. One Asset per turn.

- A faction can't have more Assets of a particular attribute than their score in that attribute (Force 3 = max 3 Force Assets). Excess costs 1 Treasure per excess Asset each turn, or lose them.

**Hide Asset**: Requires Cunning 3+. Spend 2 Treasure to give one Asset the Stealth quality. Can't hide Assets in a location with another faction's Base of Influence. No refund if Stealth is later lost.

**Sell Asset**: Voluntarily decommission an Asset. Gain half its purchase cost in Treasure (rounded down). No Treasure gained if the Asset is damaged.

---

### Faction Goals

Goal difficulty = XP earned on completion.

**Blood the Enemy** (Difficulty 2): Inflict HP damage on enemy assets/bases equal to your total Force + Cunning + Wealth.

**Destroy the Foe** (Difficulty 2 + avg of target's attributes): Destroy a rival faction.

**Eliminate Target** (Difficulty 1): Choose an undamaged rival Asset. Destroy it within 3 turns. On failure, pick a new goal without the usual turn of paralysis.

**Expand Influence** (Difficulty 1, +1 if contested): Plant a Base of Influence at a new location.

**Inside Enemy Territory** (Difficulty 2): Have Stealthed assets in rival Base locations equal to your Cunning score. Already-Stealthed units when this goal is adopted don't count.

**Invincible Valor** (Difficulty 2): Destroy a Force asset with a minimum purchase rating higher than your Force.

**Peaceable Kingdom** (Difficulty 1): Don't take an Attack action for 4 turns.

**Root Out the Enemy** (Difficulty = ½ avg of ruling faction's attributes, rounded up): Destroy a rival's Base of Influence in a specific location.

**Sphere Dominance** (Difficulty = 1 per 2 destroyed, rounded up): Choose Wealth, Force, or Cunning. Destroy rival assets of that type equal to your score.

**Wealth of Kingdoms** (Difficulty 2): Spend Treasure = 4x your Wealth rating on bribes. Money is lost, goal accomplished. Must increase Wealth before selecting again.

---

### Creating Factions

Keep to 3-4 active factions (max 6). Run turns only for the most active/relevant ones.

Decide size: **small** (petty cult, small city, minor academy), **medium** (baron's government, province-wide faith), or **large** (kingdom, major province). It's fine to model only the relevant branch of a larger institution.

All factions get a Base of Influence at HQ with HP = faction's max HP. Magic rating is whatever the GM thinks suitable.

| Size | Best Attribute | Second | Worst | Assets |
|--------|---------------|--------|-------|--------|
| Small | 3-4 | 2-3 | 1-2 | - |
| Medium | 5-6 | 4-5 | 2-3 | 2 primary + 2 others |
| Large | 7-8 | 6-7 | 3-4 | 4 primary + 4 others |

For large factions, remember it's harder to concentrate effective magical resources across a whole province/nation than in a single city-state or magical institution.

Give the faction a goal from the list above (or one chosen by the GM) to start play.

### Hit Points by Attribute Rating

| Rating | HP Value | XP Cost to Purchase |
|--------|----------|---------------------|
| 1 | 1 | - |
| 2 | 2 | 2 |
| 3 | 4 | 4 |
| 4 | 6 | 6 |
| 5 | 9 | 9 |
| 6 | 12 | 12 |
| 7 | 16 | 16 |
| 8 | 20 | 20 |

A faction's max HP = sum of HP Values for all three attributes (Force + Wealth + Cunning). E.g., Force 3, Wealth 5, Cunning 2 = 4 + 9 + 2 = 15 HP.

The Base of Influence at HQ always has max HP equal to the faction's max HP.

XP costs are cumulative - raising Force from 5 to 7 costs 9 XP (to 6) + 12 XP (to 7) = 21 XP total.
