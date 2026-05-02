// Faction Tracker — pure game-logic functions.
// All functions are deterministic given their inputs (with one exception:
// rollAttack/rollDamage are explicit RNG entry points). No DOM, no Alpine.
(function () {
    'use strict';

    const C = window.FactionTracker.constants;

    // ===== HP / attribute helpers =====

    function getHpForRating(rating, hpTable) {
        const entry = (hpTable || []).find(e => e.rating === rating);
        return entry ? entry.hp : rating;
    }

    function calcMaxHp(force, wealth, cunning, hpTable) {
        return (
            getHpForRating(force || 1, hpTable) +
            getHpForRating(wealth || 1, hpTable) +
            getHpForRating(cunning || 1, hpTable)
        );
    }

    function getMaxHpFromFaction(faction, hpTable) {
        return calcMaxHp(faction.force, faction.wealth, faction.cunning, hpTable);
    }

    function getXpCostForNext(currentRating, hpTable) {
        const entry = (hpTable || []).find(e => e.rating === currentRating + 1);
        return entry ? entry.xp_cost : Infinity;
    }

    function getStartingAssetsGuidance(force, wealth, cunning) {
        const best = Math.max(force || 1, wealth || 1, cunning || 1);
        if (best <= 4) return { size: 'Small', text: 'No starting assets' };
        if (best <= 6) return { size: 'Medium', text: '4 assets (2 from highest attribute + 2 from others)' };
        return { size: 'Large', text: '8 assets (4 from highest attribute + 4 from others)' };
    }

    function hpPercent(current, max) {
        if (max <= 0) return 0;
        return Math.min(100, Math.max(0, (current / max) * 100));
    }

    function hpBarClass(current, max) {
        const pct = hpPercent(current, max);
        if (pct > 60) return 'hp-high';
        if (pct > 25) return 'hp-mid';
        return 'hp-low';
    }

    // ===== Treasure / upkeep =====

    // RAW: ½ Wealth + ¼ (Force + Cunning), rounded up.
    function calcTreasureIncome(faction) {
        return Math.ceil(faction.wealth / 2 + (faction.force + faction.cunning) / 4);
    }

    // Returns plan-style results so the caller can decide how to apply them.
    // getAssetStaticData(assetId) → asset definition with upkeep field.
    function planUpkeep(faction, getAssetStaticData) {
        let treasure = faction.treasure;
        const lines = []; // { assetId, name, upkeep, paid: bool }
        for (const asset of faction.assets || []) {
            const data = getAssetStaticData(asset.assetId);
            if (data && data.upkeep > 0) {
                if (treasure >= data.upkeep) {
                    treasure -= data.upkeep;
                    lines.push({ assetId: asset.id, name: asset.name, upkeep: data.upkeep, paid: true });
                } else {
                    lines.push({ assetId: asset.id, name: asset.name, upkeep: data.upkeep, paid: false });
                }
            }
        }
        return { treasureAfter: treasure, lines };
    }

    function countAssetsOfType(faction, type) {
        return (faction.assets || []).filter(a => a.type === type && a.assetId !== 'base-of-influence').length;
    }

    // Returns array of { type, count, cap, excess } for any over-cap attribute.
    function getExcessAssets(faction) {
        const out = [];
        for (const type of ['force', 'wealth', 'cunning']) {
            const count = countAssetsOfType(faction, type);
            const cap = faction[type] || 0;
            if (count > cap) out.push({ type, count, cap, excess: count - cap });
        }
        return out;
    }

    // ===== Repair =====

    // Repair heals ½ matching attribute (rounded up), or for faction HP:
    // (highest + lowest attribute) / 2, rounded up.
    function calcRepairAmount(target, faction) {
        if (target === '__faction__') {
            const highest = Math.max(faction.force, faction.wealth, faction.cunning);
            const lowest = Math.min(faction.force, faction.wealth, faction.cunning);
            return Math.ceil((highest + lowest) / 2);
        }
        // target is an asset
        if (!target) return 0;
        return Math.ceil((faction[target.type] || 0) / 2);
    }

    // Per RAW: 1st repair this turn = 1T, 2nd = 2T, 3rd = 3T, etc.
    function calcRepairCost(repairsThisTurn) {
        return Math.max(1, (repairsThisTurn || 0) + 1);
    }

    // ===== Asset eligibility =====

    function eligibleAssetsToBuy(faction, allAssets) {
        if (!faction) return [];
        const order = C.MAGIC_ORDER;
        const factionMagicIdx = order.indexOf(faction.magic || 'none');
        return (allAssets || []).filter(a => {
            const attrVal = faction[a.type] || 0;
            if (a.attribute_req > attrVal) return false;
            if (order.indexOf(a.magic_req) > factionMagicIdx) return false;
            if (countAssetsOfType(faction, a.type) >= faction[a.type]) return false;
            return true;
        });
    }

    // ===== Combat =====

    // Rolls 1d10 + atk vs 1d10 + def. Attacker wins on strict greater (ties → defender).
    // diceStore is optional; if provided, uses its roll() for consistency / observability.
    function rollAttack({ atkAttr, defAttr, diceStore }) {
        const r10 = () => (diceStore ? diceStore.roll('1d10').rolls[0] : Math.floor(Math.random() * 10) + 1);
        const atkRoll = r10();
        const defRoll = r10();
        const atkTotal = atkRoll + atkAttr;
        const defTotal = defRoll + defAttr;
        return { atkRoll, defRoll, atkTotal, defTotal, hit: atkTotal > defTotal };
    }

    // Returns { rolls: number[], total: number }, or null if notation invalid.
    function rollDamage(notation, diceStore) {
        if (!notation || notation === 'special') return null;
        if (diceStore) return diceStore.roll(notation);
        const match = String(notation).match(/^(\d+)?d(\d+)([+-]\d+)?$/i);
        if (!match) return null;
        const count = parseInt(match[1]) || 1;
        const sides = parseInt(match[2]);
        const modifier = parseInt(match[3]) || 0;
        const rolls = [];
        for (let i = 0; i < count; i++) rolls.push(Math.floor(Math.random() * sides) + 1);
        return { rolls, modifier, total: rolls.reduce((a, b) => a + b, 0) + modifier };
    }

    // Pure: returns the deltas/results, caller applies mutations.
    // - target: asset object with hp + assetId
    // - amount: damage to apply
    // - faction: target's owning faction (used for BoI → faction HP linkage)
    // Returns { targetHpAfter, destroyed, factionHpAfter, factionDmg }
    function applyDamageDelta(target, amount, faction) {
        const targetHpAfter = Math.max(0, (target.hp || 0) - amount);
        const destroyed = targetHpAfter <= 0;
        let factionHpAfter = faction.hp;
        let factionDmg = 0;
        if (target.assetId === 'base-of-influence') {
            factionDmg = Math.min(amount, faction.hp);
            factionHpAfter = Math.max(0, faction.hp - factionDmg);
        }
        return { targetHpAfter, destroyed, factionHpAfter, factionDmg };
    }

    // ===== Sell =====

    // No refund if damaged; otherwise half cost (rounded down).
    function calcSellValue(asset, getAssetStaticData) {
        const data = getAssetStaticData(asset.assetId);
        if (!data) return 0;
        if (asset.hp < asset.maxHp) return 0;
        return Math.floor(data.cost / 2);
    }

    // ===== Initiative =====

    function rollInitiative(diceStore) {
        if (diceStore) return diceStore.roll('1d8').rolls[0];
        return Math.floor(Math.random() * 8) + 1;
    }

    // ===== Magic level =====

    function magicLevelMet(factionMagic, requiredMagic) {
        const order = C.MAGIC_ORDER;
        return order.indexOf(requiredMagic || 'none') <= order.indexOf(factionMagic || 'none');
    }

    window.FactionTracker = window.FactionTracker || {};
    window.FactionTracker.rules = {
        getHpForRating,
        calcMaxHp,
        getMaxHpFromFaction,
        getXpCostForNext,
        getStartingAssetsGuidance,
        hpPercent,
        hpBarClass,
        calcTreasureIncome,
        planUpkeep,
        countAssetsOfType,
        getExcessAssets,
        calcRepairAmount,
        calcRepairCost,
        eligibleAssetsToBuy,
        rollAttack,
        rollDamage,
        applyDamageDelta,
        calcSellValue,
        rollInitiative,
        magicLevelMet,
    };
})();
