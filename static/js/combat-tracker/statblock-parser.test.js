// Run with: node --test static/js/combat-tracker/statblock-parser.test.js
const test = require('node:test');
const assert = require('node:assert/strict');

const {
    parseStatblock,
    parseDamage,
    parseShock,
    parseSpacedStatblock,
    parseSingleSpaceStatblock,
    parseCompactStatblock
} = require('./statblock-parser.js');

test('parseDamage: weapon damage with bonus', () => {
    assert.deepEqual(parseDamage('Wpn+2'), { damageMode: 'weapon', dmgBonus: 2 });
});

test('parseDamage: weapon damage without bonus', () => {
    assert.deepEqual(parseDamage('Wpn'), { damageMode: 'weapon', dmgBonus: 0 });
});

test('parseDamage: dice notation with bonus', () => {
    assert.deepEqual(parseDamage('2d6+5'), {
        damageMode: 'dice', diceCount: 2, diceType: 6, dmgBonus: 5
    });
});

test('parseDamage: dice notation without bonus', () => {
    assert.deepEqual(parseDamage('1d8'), {
        damageMode: 'dice', diceCount: 1, diceType: 8, dmgBonus: 0
    });
});

test('parseShock: dash means no shock', () => {
    assert.deepEqual(parseShock('-'), { shockValue: 0, shockAC: '-' });
});

test('parseShock: "none" means no shock', () => {
    assert.deepEqual(parseShock('none'), { shockValue: 0, shockAC: '-' });
});

test('parseShock: numeric N/AC', () => {
    assert.deepEqual(parseShock('2/15'), { shockValue: 2, shockAC: '15' });
});

test('parseShock: numeric with - AC (any AC)', () => {
    assert.deepEqual(parseShock('5/-'), { shockValue: 5, shockAC: '-' });
});

test('parseShock: Wpn means weapon shock, no override', () => {
    assert.deepEqual(parseShock('Wpn'), { shockOverride: false });
});

test('parseShock: Wpn/- means override (shock against any AC)', () => {
    assert.deepEqual(parseShock('Wpn+2/-'), { shockOverride: true });
});

// Helper: unwrap the result envelope, asserting ok:true.
function ok(input) {
    const r = parseStatblock(input);
    assert.equal(r.ok, true, 'expected ok:true, got error: ' + (r.error && r.error.message));
    return r.data;
}

// Helper: unwrap a failure, returning the error object.
function fail(input) {
    const r = parseStatblock(input);
    assert.equal(r.ok, false, 'expected ok:false, got data');
    return r.error;
}

test('SPACED format: villager statblock', () => {
    const r = ok("Villager  1  10  +0  Wpn  Wpn  30'  7  5  +1  15+");
    assert.equal(r.name, 'Villager');
    assert.equal(r.hd, 1);
    assert.equal(r.ac, 10);
    assert.equal(r.bab, 0);
    assert.equal(r.attacks, 1);
    assert.equal(r.damageMode, 'weapon');
    assert.equal(r.mv, "30'");
    assert.equal(r.ml, 7);
    assert.equal(r.inst, 5);
    assert.equal(r.skl, 1);
    assert.equal(r.sv, 15);
});

test('SPACED format: armored knight with attack count', () => {
    const r = ok("Warlord  8  16a  +10 x2  Wpn+4  Wpn+4/-  30'  10  3  +2  11+");
    assert.equal(r.name, 'Warlord');
    assert.equal(r.hd, 8);
    assert.equal(r.ac, 16);
    assert.equal(r.hasArmor, true);
    assert.equal(r.bab, 10);
    assert.equal(r.attacks, 2);
    assert.equal(r.damageMode, 'weapon');
    assert.equal(r.dmgBonus, 4);
    assert.equal(r.shockOverride, true);
});

test('SPACED format: dice damage with shock value', () => {
    const r = ok("Skeleton  1  13  +1  1d6  -  30'  12  5  +0  15+");
    assert.equal(r.name, 'Skeleton');
    assert.equal(r.damageMode, 'dice');
    assert.equal(r.diceCount, 1);
    assert.equal(r.diceType, 6);
    assert.equal(r.shockValue, 0);
    assert.equal(r.shockAC, '-');
});

test('SINGLE-SPACE format: multi-word name', () => {
    const r = ok("Lesser Anak Warrior 1 13a +1 Wpn+1 Wpn+1 20' 7 4 +1 15+");
    assert.equal(r.name, 'Lesser Anak Warrior');
    assert.equal(r.hd, 1);
    assert.equal(r.ac, 13);
    assert.equal(r.hasArmor, true);
    assert.equal(r.bab, 1);
    assert.equal(r.dmgBonus, 1);
    assert.equal(r.mv, "20'");
});

test('SINGLE-SPACE format: rejects when BAB token absent', () => {
    const e = fail('Just a sentence with no statblock');
    assert.equal(e.code, 'parse_failed');
});

test('COMPACT format: Lesser Anak Warrior', () => {
    const r = ok('Lesser Anak Warrior113a+1Wpn+1Wpn+120\'74+115+');
    assert.equal(r.name, 'Lesser Anak Warrior');
    assert.equal(r.hd, 1);
    assert.equal(r.ac, 13);
    assert.equal(r.hasArmor, true);
    assert.equal(r.bab, 1);
    assert.equal(r.damageMode, 'weapon');
    assert.equal(r.dmgBonus, 1);
    assert.equal(r.mv, "20'");
    assert.equal(r.ml, 7);
    assert.equal(r.inst, 4);
    assert.equal(r.skl, 1);
    assert.equal(r.sv, 15);
});

test('COMPACT format: dice damage and shock', () => {
    const r = ok('Undead Mage810+101d82/-30\'94+211+');
    assert.equal(r.name, 'Undead Mage');
    assert.equal(r.hd, 8);
    assert.equal(r.ac, 10);
    assert.equal(r.bab, 10);
    assert.equal(r.damageMode, 'dice');
    assert.equal(r.diceCount, 1);
    assert.equal(r.diceType, 8);
    assert.equal(r.shockValue, 2);
    assert.equal(r.shockAC, '-');
});

test('COMPACT format: fly flag detected', () => {
    const r = ok('Ancient Warbot1420+15 x32d6+510/-60\' fly122+28+');
    assert.equal(r.name, 'Ancient Warbot');
    assert.equal(r.hd, 14);
    assert.equal(r.ac, 20);
    assert.equal(r.attacks, 3);
    assert.equal(r.hasFly, true);
    assert.equal(r.hasSwim, false);
    assert.equal(r.shockValue, 10);
    assert.equal(r.shockAC, '-');
});

test('parseStatblock: empty input returns ok:false with code "empty"', () => {
    assert.equal(fail('').code, 'empty');
    assert.equal(fail('   ').code, 'empty');
    assert.equal(fail(null).code, 'empty');
});

test('parseStatblock: completely garbage input returns parse_failed', () => {
    const e = fail('this is not a statblock at all');
    assert.equal(e.code, 'parse_failed');
    assert.ok(e.message.length > 0);
    assert.ok(['spaced', 'single-space', 'compact'].includes(e.format));
});

test('parseStatblock: error includes detected format', () => {
    // Single-space heuristic triggers (has " +1" but rest is too short).
    const e = fail('Foo 1 10 +1 Wpn');
    assert.equal(e.code, 'parse_failed');
    assert.equal(e.format, 'single-space');
});

test('format detection: pilcrow forces compact path', () => {
    // Pilcrow-marked compact format (ability markers stripped)
    const r = ok('Skeleton ¶113+11d6-30\'125+015+');
    assert.equal(r.name, 'Skeleton');
});

test('format detection: double-space wins over single-space', () => {
    // Stray double space between fields should still be parsed as SPACED
    const r = ok("Villager  1  10  +0  Wpn  Wpn  30'  7  5  +1  15+");
    assert.equal(r.name, 'Villager');
});

test('parseStatblock: result envelope includes format on success', () => {
    const r = parseStatblock("Villager  1  10  +0  Wpn  Wpn  30'  7  5  +1  15+");
    assert.equal(r.ok, true);
    assert.equal(r.format, 'spaced');
});
