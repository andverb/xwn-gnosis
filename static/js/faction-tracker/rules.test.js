// Unit tests for rules.js
// Run: node --test 'static/js/**/*.test.js' (or `make test-js`)
//
// rules.js + constants.js are written as browser IIFEs that attach to
// `window.FactionTracker`. We shim a global window, eval the source, then
// pull the namespace off it.

'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const HERE = __dirname;

function loadModules() {
    const ctx = { window: {}, console };
    vm.createContext(ctx);
    for (const file of ['constants.js', 'rules.js']) {
        const src = fs.readFileSync(path.join(HERE, file), 'utf8');
        vm.runInContext(src, ctx, { filename: file });
    }
    return ctx.window.FactionTracker;
}

const FT = loadModules();
const R = FT.rules;

const HP_TABLE = [
    { rating: 1, hp: 1, xp_cost: 0 },
    { rating: 2, hp: 2, xp_cost: 1 },
    { rating: 3, hp: 4, xp_cost: 2 },
    { rating: 4, hp: 6, xp_cost: 4 },
    { rating: 5, hp: 8, xp_cost: 6 },
    { rating: 6, hp: 12, xp_cost: 8 },
    { rating: 7, hp: 16, xp_cost: 10 },
    { rating: 8, hp: 20, xp_cost: 12 },
];

// ===== HP / attributes =====

test('getHpForRating returns mapped hp', () => {
    assert.equal(R.getHpForRating(3, HP_TABLE), 4);
    assert.equal(R.getHpForRating(8, HP_TABLE), 20);
});

test('getHpForRating falls back to rating when missing', () => {
    assert.equal(R.getHpForRating(99, HP_TABLE), 99);
});

test('calcMaxHp sums per-attribute hp', () => {
    assert.equal(R.calcMaxHp(3, 4, 5, HP_TABLE), 4 + 6 + 8);
});

test('calcMaxHp defaults missing attributes to 1', () => {
    assert.equal(R.calcMaxHp(0, undefined, null, HP_TABLE), 3);
});

test('getXpCostForNext returns next entry cost', () => {
    assert.equal(R.getXpCostForNext(3, HP_TABLE), 4);
});

test('getXpCostForNext returns Infinity at cap', () => {
    assert.equal(R.getXpCostForNext(8, HP_TABLE), Infinity);
});

test('getStartingAssetsGuidance buckets by best attribute', () => {
    assert.equal(R.getStartingAssetsGuidance(2, 3, 4).size, 'Small');
    assert.equal(R.getStartingAssetsGuidance(5, 3, 2).size, 'Medium');
    assert.equal(R.getStartingAssetsGuidance(7, 3, 2).size, 'Large');
});

test('hpPercent / hpBarClass thresholds', () => {
    assert.equal(R.hpPercent(0, 10), 0);
    assert.equal(R.hpPercent(10, 10), 100);
    assert.equal(R.hpBarClass(8, 10), 'hp-high');
    assert.equal(R.hpBarClass(4, 10), 'hp-mid');
    assert.equal(R.hpBarClass(2, 10), 'hp-low');
    assert.equal(R.hpBarClass(0, 0), 'hp-low');
});

// ===== Treasure / upkeep =====

test('calcTreasureIncome rounds up wealth/2 + (force+cunning)/4', () => {
    assert.equal(R.calcTreasureIncome({ force: 3, wealth: 4, cunning: 5 }), 4);
    assert.equal(R.calcTreasureIncome({ force: 2, wealth: 3, cunning: 2 }), 3);
});

test('planUpkeep pays what it can, flags rest', () => {
    const faction = {
        treasure: 3,
        assets: [
            { id: 'a1', assetId: 'cheap', name: 'Cheap' },
            { id: 'a2', assetId: 'pricey', name: 'Pricey' },
            { id: 'a3', assetId: 'free', name: 'Free' },
        ],
    };
    const data = {
        cheap: { upkeep: 1 },
        pricey: { upkeep: 5 },
        free: { upkeep: 0 },
    };
    const plan = R.planUpkeep(faction, (id) => data[id]);
    assert.equal(plan.treasureAfter, 2);
    assert.equal(plan.lines.length, 2);
    assert.equal(plan.lines[0].paid, true);
    assert.equal(plan.lines[1].paid, false);
});

test('countAssetsOfType excludes base-of-influence', () => {
    const faction = {
        assets: [
            { type: 'force', assetId: 'base-of-influence' },
            { type: 'force', assetId: 'thugs' },
            { type: 'force', assetId: 'thugs' },
            { type: 'wealth', assetId: 'smugglers' },
        ],
    };
    assert.equal(R.countAssetsOfType(faction, 'force'), 2);
    assert.equal(R.countAssetsOfType(faction, 'wealth'), 1);
});

test('getExcessAssets reports over-cap attrs', () => {
    const faction = {
        force: 1, wealth: 3, cunning: 2,
        assets: [
            { type: 'force', assetId: 'thugs' },
            { type: 'force', assetId: 'thugs' },
            { type: 'wealth', assetId: 's' },
        ],
    };
    const ex = R.getExcessAssets(faction);
    assert.equal(ex.length, 1);
    assert.equal(ex[0].type, 'force');
    assert.equal(ex[0].excess, 1);
});

// ===== Repair =====

test('calcRepairAmount: faction = ceil((highest+lowest)/2)', () => {
    const faction = { force: 5, wealth: 2, cunning: 3 };
    assert.equal(R.calcRepairAmount('__faction__', faction), 4);
});

test('calcRepairAmount: asset = ceil(matching attr / 2)', () => {
    const faction = { force: 5, wealth: 4, cunning: 3 };
    assert.equal(R.calcRepairAmount({ type: 'force' }, faction), 3);
    assert.equal(R.calcRepairAmount({ type: 'wealth' }, faction), 2);
    assert.equal(R.calcRepairAmount({ type: 'cunning' }, faction), 2);
});

test('calcRepairCost: 1st=1T, 2nd=2T, 3rd=3T (escalation)', () => {
    assert.equal(R.calcRepairCost(0), 1);
    assert.equal(R.calcRepairCost(1), 2);
    assert.equal(R.calcRepairCost(2), 3);
    assert.equal(R.calcRepairCost(undefined), 1);
});

// ===== Eligibility =====

test('eligibleAssetsToBuy filters by attribute, magic, cap', () => {
    const faction = {
        force: 2, wealth: 1, cunning: 1, magic: 'low',
        assets: [
            { type: 'force', assetId: 'thugs' },
            { type: 'force', assetId: 'thugs' },
        ],
    };
    const all = [
        { type: 'force', attribute_req: 1, magic_req: 'none', name: 'A' },
        { type: 'wealth', attribute_req: 2, magic_req: 'none', name: 'B' },
        { type: 'cunning', attribute_req: 1, magic_req: 'none', name: 'C' },
        { type: 'cunning', attribute_req: 1, magic_req: 'high', name: 'D' },
        { type: 'cunning', attribute_req: 1, magic_req: 'low', name: 'E' },
    ];
    const ok = R.eligibleAssetsToBuy(faction, all);
    const names = ok.map(a => a.name).sort();
    assert.deepEqual(names, ['C', 'E']);
});

// ===== Combat =====

test('rollAttack: hit on strict greater', () => {
    let i = 0;
    const seq = [10, 1];
    const dice = { roll: () => ({ rolls: [seq[i++]] }) };
    const r = R.rollAttack({ atkAttr: 0, defAttr: 0, diceStore: dice });
    assert.equal(r.atkRoll, 10);
    assert.equal(r.defRoll, 1);
    assert.equal(r.hit, true);
});

test('rollAttack: tie goes to defender', () => {
    let i = 0;
    const seq = [5, 5];
    const dice = { roll: () => ({ rolls: [seq[i++]] }) };
    const r = R.rollAttack({ atkAttr: 2, defAttr: 2, diceStore: dice });
    assert.equal(r.atkTotal, 7);
    assert.equal(r.defTotal, 7);
    assert.equal(r.hit, false);
});

test('rollDamage parses notation via fallback path', () => {
    const out = R.rollDamage('1d6');
    assert.ok(out.total >= 1 && out.total <= 6);
    assert.equal(out.rolls.length, 1);
});

test('rollDamage: special / null returns null', () => {
    assert.equal(R.rollDamage('special'), null);
    assert.equal(R.rollDamage(null), null);
    assert.equal(R.rollDamage('garbage'), null);
});

test('rollDamage: respects diceStore', () => {
    const dice = { roll: (n) => ({ rolls: [3, 4], total: 7, modifier: 0, notation: n }) };
    const out = R.rollDamage('2d6', dice);
    assert.equal(out.total, 7);
});

// ===== Damage application =====

test('applyDamageDelta: ordinary asset', () => {
    const target = { hp: 5, assetId: 'thugs' };
    const faction = { hp: 10 };
    const r = R.applyDamageDelta(target, 3, faction);
    assert.equal(r.targetHpAfter, 2);
    assert.equal(r.destroyed, false);
    assert.equal(r.factionHpAfter, 10);
    assert.equal(r.factionDmg, 0);
});

test('applyDamageDelta: lethal damage destroys', () => {
    const target = { hp: 2, assetId: 'thugs' };
    const faction = { hp: 10 };
    const r = R.applyDamageDelta(target, 5, faction);
    assert.equal(r.targetHpAfter, 0);
    assert.equal(r.destroyed, true);
    assert.equal(r.factionHpAfter, 10);
});

test('applyDamageDelta: BoI propagates damage to faction (clamped)', () => {
    const target = { hp: 4, assetId: 'base-of-influence' };
    const faction = { hp: 10 };
    const r = R.applyDamageDelta(target, 7, faction);
    assert.equal(r.targetHpAfter, 0);
    assert.equal(r.destroyed, true);
    assert.equal(r.factionDmg, 7);
    assert.equal(r.factionHpAfter, 3);
});

test('applyDamageDelta: BoI faction dmg clamped to faction hp', () => {
    const target = { hp: 4, assetId: 'base-of-influence' };
    const faction = { hp: 5 };
    const r = R.applyDamageDelta(target, 100, faction);
    assert.equal(r.factionDmg, 5);
    assert.equal(r.factionHpAfter, 0);
});

// ===== Sell =====

test('calcSellValue: damaged asset = 0', () => {
    const data = { thugs: { cost: 4 } };
    const asset = { assetId: 'thugs', hp: 1, maxHp: 4 };
    assert.equal(R.calcSellValue(asset, (id) => data[id]), 0);
});

test('calcSellValue: undamaged = floor(cost/2)', () => {
    const data = { thugs: { cost: 5 } };
    const asset = { assetId: 'thugs', hp: 4, maxHp: 4 };
    assert.equal(R.calcSellValue(asset, (id) => data[id]), 2);
});

// ===== Magic =====

test('magicLevelMet: order none < low < medium < high', () => {
    assert.equal(R.magicLevelMet('high', 'low'), true);
    assert.equal(R.magicLevelMet('low', 'high'), false);
    assert.equal(R.magicLevelMet('low', 'low'), true);
    assert.equal(R.magicLevelMet(undefined, 'low'), false);
    assert.equal(R.magicLevelMet('low', undefined), true);
});
