# Faction Tracker — Design & Implementation Plan

## Overview

A GM tool for running WWN faction turns. Tracks faction state (attributes, HP, treasure, assets, goals), automates bookkeeping (treasure income, upkeep), and maintains a turn-by-turn log with GM commentary. Purpose: generate background events and adventure hooks so the game world feels alive.

**URL**: `/wwn/tools/faction-tracker/`

---

## Page Layout

Two sections, top to bottom:

1. **Faction Dashboard** — color-coded faction cards showing current state
2. **Turn Log / Timeline** — reverse-chronological turn history

Between them: `[▶ Run Faction Turn]` and `[+ Add Manual Entry]` buttons.

Top-right area: `[Export JSON]` `[Import JSON]` buttons, campaign name (editable).

---

## Faction Cards

Responsive grid (2 columns large, 1 column mobile). Each faction gets a card with a colored left border from a 6-color palette. Max 6 factions.

### Card contents:

```
┌─ [Red] IRON CIRCLE ──────────────────── [Edit] [×] ─┐
│  F: 4  W: 3  C: 5    Magic: Low    Tags: Machiavellian│
│  HP: ██████████░░ 10/15    Treasure: 7                 │
│  Goal: Blood the Enemy (2 XP) — 12/15 dmg dealt        │
│                                                         │
│  Assets:                                                │
│  ▸ Smugglers      ████ 4/4   Westmark   Subtle,Action  │
│  ▸ Infantry       ███░ 3/6   Eastkeep                  │
│  ▸ Hired Friends  ████ 4/4   Westmark   Subtle,Special │
└─────────────────────────────────────────────────────────┘
```

- **Asset rows**: compact — name, HP bar, location, qualities
- **"Special" quality**: Bootstrap tooltip on hover showing full ability text (from static JSON)
- **Expandable assets**: click row to reveal attack/counter/damage, type, cost, description
- **Edit button**: opens modal to edit faction attributes, tags, magic, goal
- **Add Asset**: button inside card, dropdown filtered by faction's attribute scores + magic level
- **Add Faction**: button below all cards, modal with name, F/W/C, magic, tags, starting goal

---

## Turn Log / Timeline

Reverse-chronological (newest on top). Each turn is a Bootstrap accordion item.

```
═══════════════════════════════════════════════════════
 TURN 3 — Month of the Red Moon          [Collapse ▾]
 Initiative: Iron Circle (7) → Silver Hand (5) → Rats Below (2)
═══════════════════════════════════════════════════════

 [Red] IRON CIRCLE                              +3 Treasure earned
 ├─ Upkeep: −1 (Free Company)                   −1 Treasure
 ├─ Action: ATTACK — Infantry → Silver Hand's Informers
 │   Roll: 1d10+4 vs 1d10+5 → [8]+4=12 vs [3]+5=8 ✓ Hit
 │   Damage: 1d8 → [6] — Informers destroyed!
 │   📝 "Iron Circle flexing muscle after the border dispute.
 │       Players might hear rumors of guild crackdowns."
 ├─ Goal: Blood the Enemy — 12/15 → 18/15 ✓ COMPLETE (+2 XP)
 │
 [Blue] SILVER HAND                             +2 Treasure earned
 ├─ Upkeep: paid (0)
 ├─ Ability: Smugglers moved Hired Friends to Eastkeep
 ├─ Action: CREATE ASSET — Petty Seers at Westmark (−2 Treasure)
 │
 [Green] RATS BELOW                             +1 Treasure earned
 ├─ Upkeep: paid (0)
 ├─ Action: MOVE ASSET — Thugs → Westmark
 └─ Goal: Inside Enemy Territory — 1/3 stealthed
```

- **Turn title**: editable (GM can name months, or leave as "Turn N")
- **Faction names**: color-coded matching cards
- **Automated entries** (treasure, upkeep): muted/secondary text
- **Rolls**: full breakdown with dice notation, individual results in brackets, total, pass/fail
- **GM comments**: inline, click to add/edit per action
- **Older turns**: collapsed to header only

---

## Run Turn Flow

Clicking `[▶ Run Faction Turn]`:

### Step 1 — Initiative
Auto-rolls 1d8 per faction, displays results, sorts by initiative. GM can re-roll or manually adjust order.

### Step 2 — Per Faction (in initiative order)

A focused panel appears for each faction:

```
┌─ [Red] IRON CIRCLE's Turn ──────────────────────────┐
│                                                       │
│  ✅ Earned 3 Treasure (½×3 + ¼(4+5) = 4) → now 10   │
│  ✅ Upkeep: −1 Free Company → now 9                   │
│                                                       │
│  Special Abilities:                                   │
│  ┌──────────────────────────────────────────────┐     │
│  │ Smugglers (Westmark): Move a W/C asset?      │     │
│  │           [Use Ability]  [Skip]              │     │
│  └──────────────────────────────────────────────┘     │
│                                                       │
│  Choose Action:                                       │
│  [Attack] [Move] [Repair] [Expand] [Create] [Hide]   │
│  [Sell] [No Action]                                   │
│                                                       │
│  GM Notes for this turn: [________________________]   │
│                                                       │
│                          [Finish Iron Circle's Turn →] │
└───────────────────────────────────────────────────────┘
```

**Auto-resolved** (steps 1-2 of faction turn):
- Earn Treasure = ½ Wealth + ¼(Force + Cunning), rounded up
- Pay Upkeep — deduct costs, flag if insufficient

**GM resolves** (steps 3-5):
- **Abilities**: only assets with free-action abilities are shown. [Use] or [Skip] each.
- **Action**: GM picks from buttons. Sub-flows:
  - **Attack**: pick attacking asset(s) → pick target faction → target picks defender → [Roll F vs F] button → auto-roll damage on hit → HP auto-updated
  - **Move**: pick asset → text input for destination
  - **Create**: dropdown of eligible assets (filtered by attributes + magic + treasure) → pick location with Base of Influence
  - **Repair**: pick asset → shows cost and healing amount → confirm
  - **Expand Influence**: pick location → set HP → pay treasure → Cunning vs Cunning checks
  - **Hide**: pick asset (needs Cunning 3+) → pay 2 treasure
  - **Sell**: pick asset → gain half cost (if undamaged)
- **Goal check**: prompt after action if relevant. "Complete? [Yes] [Not yet]"
- **GM Notes**: text area, always visible

**"Finish Turn"** commits to log, moves to next faction. After all factions: full turn entry appears in timeline, cards update.

### Manual Entry

`[+ Add Manual Entry]` — for offline rolls or narrative events outside formal turns. Faction selector + free text. Appears in log.

---

## Data Model

```javascript
{
  version: 1,
  campaignName: "Sunward Marches",
  currentTurn: 3,

  factions: [
    {
      id: "uuid",
      name: "Iron Circle",
      color: 0,                // index into 6-color palette
      force: 4, wealth: 3, cunning: 5,
      magic: "low",            // none|low|medium|high
      hp: 10,
      // maxHp auto-calculated from attributes
      treasure: 9,
      xp: 0,
      tags: ["machiavellian"],
      goal: { type: "blood_the_enemy", progress: 18, target: 15 },
      assets: [
        {
          id: "uuid",
          assetId: "infantry",  // references static asset data
          name: "Infantry",     // display name (GM can rename)
          type: "force",        // force|wealth|cunning
          hp: 3, maxHp: 6,
          location: "Eastkeep",
          qualities: [],        // acquired qualities beyond defaults
          stealth: false,
          notes: ""
        }
      ]
    }
  ],

  log: [
    {
      turn: 3,
      title: "Month of the Red Moon",
      initiative: [
        { factionId: "uuid", roll: 7 }
      ],
      entries: [
        {
          factionId: "uuid",
          type: "auto",          // auto|action|ability|goal|manual
          text: "Earned 3 Treasure",
          treasureChange: +3
        },
        {
          factionId: "uuid",
          type: "action",
          action: "attack",
          attacker: { assetId: "uuid", name: "Infantry" },
          defender: { assetId: "uuid", name: "Informers", factionId: "uuid" },
          roll: {
            atkAttr: "force", defAttr: "force",
            atkDice: "1d10+4", defDice: "1d10+5",
            atkResult: 12, defResult: 8,
            hit: true
          },
          damage: { dice: "1d8", result: 6 },
          note: "Iron Circle flexing muscle after the border dispute."
        },
        {
          factionId: "uuid",
          type: "goal",
          text: "Blood the Enemy — COMPLETE",
          xpGained: 2
        }
      ]
    }
  ]
}
```

---

## Static Asset Data

File: `static/data/wwn_faction_assets.json`

Extracted from the 3 asset markdown files. Structure:

```javascript
{
  "assets": [
    {
      "id": "infantry",
      "name": { "en": "Infantry", "uk": "Піхота" },
      "type": "force",
      "attribute_req": 3,
      "cost": 6,
      "hp": 6,
      "magic_req": "none",
      "attack": { "atk_attr": "force", "def_attr": "force", "damage": "1d8" },
      "counter": { "damage": "1d6" },
      "qualities": [],
      "upkeep": 0,
      "description": {
        "en": "Common foot soldiers organized and armed by the faction.",
        "uk": "..."
      }
    }
  ]
}
```

Bilingual from day one so Ukrainian localization of the tracker UI can use it later.

---

## V1 Automation (Pareto)

Auto-calculated:
- Treasure income: ½W + ¼(F+C) rounded up
- Upkeep deduction
- Initiative rolls (1d8)
- Max HP from attribute table
- Asset eligibility filtering (attribute + magic requirements)
- Attack rolls (1d10 + attribute vs 1d10 + attribute)
- Damage rolls on hit, HP auto-deduction
- Counterattack damage on miss

GM resolves manually:
- Which action to take
- Which assets attack / defend
- Special ability usage (text shown, GM decides)
- Goal completion (GM marks done)
- Locations (free text)
- Narrative notes

---

## Deferred to V2+

- Goal progress auto-tracking (too varied per goal type)
- Asset special ability automation (too many unique effects)
- Location/map system (text input for now)
- Multi-campaign support (Patreon accounts)
- Backend persistence (Django models + API)
- Ukrainian localization of tracker UI (asset data is bilingual already)
- Undo/redo
- Faction turn AI suggestions

---

## Tech Stack

Same patterns as combat tracker:
- **Alpine.js** component for all reactive state
- **$store.dice** for rolls (already global in base.html)
- **Bootstrap 5** cards, accordion, modals, tooltips, badges
- **localStorage** for persistence
- **JSON file download/upload** for export/import
- **One Django view** serving the template
- **One static JSON file** for asset data

---

## Implementation Steps

### Phase 1: Data Foundation ✅ COMPLETE
1. ✅ Create `static/data/wwn_faction_assets.json` — 81 assets, 10 tags, 10 goals, HP table
2. ✅ Include faction tags and goals as reference data in the same file
3. ✅ Add Django view + URL at `/wwn/tools/faction-tracker/`
4. ✅ Create base template extending `tools/base.html`

### Phase 2: Faction Dashboard ✅ COMPLETE (built into template)
5. ✅ Alpine.js component with faction state management
6. ✅ localStorage save/load
7. ✅ Faction CRUD — add/edit/remove factions (modal forms)
8. ✅ Faction cards with attribute display, HP bar, treasure, goal, tags
9. ✅ Asset list with compact rows, expandable detail, tooltips for Special
10. ✅ Asset CRUD — add (filtered dropdown) / remove / edit (rename, location, notes)

### Phase 3: Turn Flow ✅ COMPLETE (built into template)
11. ✅ "Run Turn" button + initiative phase (auto-roll 1d8, display order, allow manual adjust)
12. ✅ Per-faction turn panel — auto-calc treasure income + upkeep
13. ✅ Action selection UI (buttons for each action type)
14. ✅ Attack sub-flow: pick attacker → pick target faction + defender → roll → damage → HP update
15. ✅ Other action sub-flows (move, create, repair, expand, hide, sell)
16. ✅ Special abilities display with Use/Skip
17. ✅ Goal check prompt
18. ✅ GM notes text area per faction turn

### Phase 4: Turn Log ✅ COMPLETE (built into template)
19. ✅ Turn log data structure + rendering (accordion, color-coded)
20. ✅ Log entry generation from turn flow (auto-entries + action entries)
21. ✅ Editable turn titles
22. ✅ Inline GM comment editing on log entries
23. ✅ Manual entry button (free-form log addition)

### Phase 5: Polish ✅ COMPLETE (built into template)
24. ✅ Export/Import JSON (file download + file upload)
25. ✅ Campaign name field
26. ✅ Add nav link in base.html
27. Responsive layout testing — NEEDS MANUAL TESTING
28. Edge cases — NEEDS MANUAL TESTING
