// Unit tests for static/js/faction-tracker/storage.js
// Run: node --test tests/faction-tracker/storage.test.js

'use strict';

const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const ROOT = path.join(__dirname, '..', '..');

function loadModules() {
    const store = {};
    const localStorage = {
        getItem: (k) => (k in store ? store[k] : null),
        setItem: (k, v) => { store[k] = String(v); },
        removeItem: (k) => { delete store[k]; },
        clear: () => { for (const k of Object.keys(store)) delete store[k]; },
    };
    const ctx = { window: {}, console, localStorage };
    vm.createContext(ctx);
    for (const file of ['constants.js', 'storage.js']) {
        const src = fs.readFileSync(path.join(ROOT, 'static/js/faction-tracker', file), 'utf8');
        vm.runInContext(src, ctx, { filename: file });
    }
    return { FT: ctx.window.FactionTracker, store };
}

test('defaultState shape', () => {
    const { FT } = loadModules();
    const s = FT.storage.defaultState();
    assert.equal(s.version, FT.constants.STATE_VERSION);
    assert.equal(s.campaignName, '');
    assert.equal(s.currentTurn, 0);
    assert.deepEqual(s.factions, []);
    assert.deepEqual(s.log, []);
});

test('validate accepts default state', () => {
    const { FT } = loadModules();
    const r = FT.storage.validate(FT.storage.defaultState());
    assert.equal(r.ok, true);
    assert.deepEqual(r.errors, []);
});

test('validate rejects non-object', () => {
    const { FT } = loadModules();
    assert.equal(FT.storage.validate(null).ok, false);
    assert.equal(FT.storage.validate('string').ok, false);
});

test('validate rejects non-array factions/log', () => {
    const { FT } = loadModules();
    const r = FT.storage.validate({ factions: 'oops', log: [] });
    assert.equal(r.ok, false);
    assert.ok(r.errors.some(e => e.includes('factions')));
});

test('validate rejects non-numeric version', () => {
    const { FT } = loadModules();
    const r = FT.storage.validate({ factions: [], log: [], version: 'one' });
    assert.equal(r.ok, false);
});

test('migrate stamps current version', () => {
    const { FT } = loadModules();
    const m = FT.storage.migrate({ factions: [], log: [], version: 0 });
    assert.equal(m.version, FT.constants.STATE_VERSION);
});

test('save → load round-trip', () => {
    const { FT } = loadModules();
    const state = { ...FT.storage.defaultState(), campaignName: 'Test' };
    FT.storage.save(state);
    const loaded = FT.storage.load();
    assert.equal(loaded.campaignName, 'Test');
});

test('load returns default when storage empty', () => {
    const { FT } = loadModules();
    const loaded = FT.storage.load();
    assert.equal(loaded.campaignName, '');
    assert.deepEqual(loaded.factions, []);
});

test('load falls back to default on invalid stored shape', () => {
    const { FT, store } = loadModules();
    store[FT.constants.STORAGE_KEY] = JSON.stringify({ factions: 'broken' });
    const loaded = FT.storage.load();
    assert.deepEqual(loaded.factions, []);
});

test('load falls back to default on parse error', () => {
    const { FT, store } = loadModules();
    store[FT.constants.STORAGE_KEY] = 'not-json{';
    const loaded = FT.storage.load();
    assert.deepEqual(loaded.factions, []);
});
