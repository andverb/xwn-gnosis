// Faction Tracker — Alpine.js component factory.
// Depends on (load order): constants.js, rules.js, storage.js
// Reads static asset data from <script type="application/json" id="faction-asset-data">.
(function () {
    'use strict';

    const C = window.FactionTracker.constants;
    const R = window.FactionTracker.rules;
    const S = window.FactionTracker.storage;
    const A = window.FactionTracker.actions;

    function readAssetData() {
        const el = document.getElementById('faction-asset-data');
        if (!el) {
            console.error('Faction Tracker: missing <script id="faction-asset-data">.');
            return { assets: [], goals: [], tags: [], hp_table: [] };
        }
        try {
            return JSON.parse(el.textContent);
        } catch (err) {
            console.error('Faction Tracker: failed to parse asset data.', err);
            return { assets: [], goals: [], tags: [], hp_table: [] };
        }
    }

    function debounce(fn, wait) {
        let t;
        return function (...args) {
            clearTimeout(t);
            t = setTimeout(() => fn.apply(this, args), wait);
        };
    }

    function factionTracker() {
        const ASSET_DATA = readAssetData();
        const HP_TABLE = ASSET_DATA.hp_table || [];

        return {
            // ===== Static Data =====
            ASSET_DATA,
            HP_TABLE,
            QUALITY_DESCRIPTIONS: C.QUALITY_DESCRIPTIONS,
            ACTION_LIST: A.list,

            // ===== Persistent State (auto-saved via $watch) =====
            state: S.defaultState(),

            // ===== UI State =====
            expandedAsset: null,
            showAddFaction: false,
            editingFaction: null,
            showManualEntry: false,

            // Faction form
            factionForm: { name: '', force: 3, wealth: 3, cunning: 3, magic: 'none', treasure: 4, hp: 0, tags: [], goalType: '', headquarters: '' },

            // Add asset
            addAssetFaction: null,
            addAssetForm: { assetId: '', location: '' },

            // Delete confirmation
            deleteConfirmText: '',
            deleteCallback: null,

            // Manual entry
            manualEntryForm: { factionId: '', text: '' },

            // ===== Turn Execution State =====
            runningTurn: false,
            turnPhase: '',
            turnInitiative: [],
            currentFactionIdx: 0,
            currentAction: null,
            currentFactionNote: '',
            currentAutoTreasure: 0,
            currentUpkeepResults: [],
            currentExcess: [],
            currentAbilities: [],
            currentTurnEntries: [],
            factionHpRepairedThisTurn: false,
            repairsThisTurn: 0,
            actionSuppressed: false,
            abilitiesSuppressed: false,
            lastActionSnapshot: null,

            // Per-action sub-flow state piles (kept for Phase 1; flattened in Phase 2)
            attackState: { attackerAssetId: '', targetFactionId: '', defenderAssetId: '', step: 1, rolled: false, hit: false, rollText: '', damageText: '', manualAtk: null, manualDef: null, moreAttacks: false },
            moveState: { assetId: '', destination: '', movedCount: 0 },
            createState: { assetId: '', location: '', lastCreated: '' },
            repairState: { assetId: '' },
            expandState: { location: '', baseHp: 1, baseCreated: false, rivalChecks: [], rivalFactionId: '' },
            simpleActionState: { assetId: '' },

            // All turn entries for the full turn being constructed
            fullTurnEntries: [],

            // ===== Init =====
            init() {
                this.state = S.load();

                const debouncedSave = debounce(() => S.save(this.state), 250);
                this.$watch('state', () => debouncedSave());

                this.$watch('showAddFaction', (val) => {
                    if (val) {
                        this.editingFaction = null;
                        this.resetFactionForm();
                        this.openModal('factionModal');
                        this.showAddFaction = false;
                    }
                });
                this.$watch('showManualEntry', (val) => {
                    if (val) {
                        this.manualEntryForm = { factionId: '', text: '' };
                        this.openModal('manualEntryModal');
                        this.showManualEntry = false;
                    }
                });
            },

            // ===== Storage / Export / Import =====
            // save() retained as a no-op alias for backward compat in case anything still calls it.
            save() { /* state is auto-saved via $watch */ },

            exportJSON() { S.exportToFile(this.state); },

            async importJSON(event) {
                const file = event.target.files && event.target.files[0];
                event.target.value = '';
                if (!file) return;
                try {
                    const data = await S.importFromFile(file);
                    this.state = { ...this.state, ...data };
                } catch (err) {
                    alert('Invalid JSON file: ' + (err.message || err));
                }
            },

            // ===== Helpers =====
            uuid() { return crypto.randomUUID(); },

            capitalize(str) {
                if (!str) return '';
                return str.charAt(0).toUpperCase() + str.slice(1);
            },

            openModal(refName) {
                this.$nextTick(() => {
                    const el = this.$refs[refName];
                    if (el) bootstrap.Modal.getOrCreateInstance(el).show();
                });
            },

            closeModal(refName) {
                const el = this.$refs[refName];
                if (el) {
                    const modal = bootstrap.Modal.getInstance(el);
                    if (modal) modal.hide();
                }
            },

            // ===== HP Calculations (delegates to rules.js) =====
            getHpForRating(rating) { return R.getHpForRating(rating, this.HP_TABLE); },
            getMaxHp(faction) { return R.getMaxHpFromFaction(faction, this.HP_TABLE); },
            calcMaxHp(f, w, c) { return R.calcMaxHp(f, w, c, this.HP_TABLE); },
            getXpCostForNext(currentRating) { return R.getXpCostForNext(currentRating, this.HP_TABLE); },
            getStartingAssetsGuidance(f, w, c) { return R.getStartingAssetsGuidance(f, w, c); },
            hpPercent(current, max) { return R.hpPercent(current, max); },
            hpBarClass(current, max) { return R.hpBarClass(current, max); },

            // ===== Faction CRUD =====
            resetFactionForm() {
                this.factionForm = { name: '', force: 3, wealth: 3, cunning: 3, magic: 'none', treasure: 4, hp: 0, tags: [], goalType: '', headquarters: '' };
            },

            editFaction(faction) {
                this.editingFaction = faction.id;
                this.factionForm = {
                    name: faction.name,
                    force: faction.force,
                    wealth: faction.wealth,
                    cunning: faction.cunning,
                    magic: faction.magic,
                    treasure: faction.treasure,
                    hp: faction.hp,
                    tags: [...faction.tags],
                    goalType: faction.goal.type,
                    headquarters: '',
                };
                this.openModal('factionModal');
            },

            toggleTag(tagId) {
                const idx = this.factionForm.tags.indexOf(tagId);
                if (idx >= 0) this.factionForm.tags.splice(idx, 1);
                else this.factionForm.tags.push(tagId);
            },

            saveFaction() {
                if (this.editingFaction) {
                    const faction = this.state.factions.find(f => f.id === this.editingFaction);
                    if (faction) {
                        faction.name = this.factionForm.name;
                        faction.force = this.factionForm.force;
                        faction.wealth = this.factionForm.wealth;
                        faction.cunning = this.factionForm.cunning;
                        faction.magic = this.factionForm.magic;
                        faction.treasure = this.factionForm.treasure;
                        faction.hp = this.factionForm.hp || this.getMaxHp(faction);
                        faction.tags = [...this.factionForm.tags];
                        faction.goal = { type: this.factionForm.goalType, progress: faction.goal?.progress || 0, target: faction.goal?.target || 0 };
                    }
                } else {
                    const newFaction = {
                        id: this.uuid(),
                        name: this.factionForm.name,
                        color: this.state.factions.length % C.FACTION_COLORS,
                        force: this.factionForm.force,
                        wealth: this.factionForm.wealth,
                        cunning: this.factionForm.cunning,
                        magic: this.factionForm.magic,
                        hp: this.factionForm.hp || R.calcMaxHp(this.factionForm.force, this.factionForm.wealth, this.factionForm.cunning, this.HP_TABLE),
                        treasure: this.factionForm.treasure,
                        xp: 0,
                        tags: [...this.factionForm.tags],
                        goal: { type: this.factionForm.goalType, progress: 0, target: 0 },
                        assets: [],
                    };
                    this.state.factions.push(newFaction);

                    const hqLocation = this.factionForm.headquarters || newFaction.name + ' HQ';
                    const hqMaxHp = this.getMaxHp(newFaction);
                    newFaction.assets.push({
                        id: this.uuid(),
                        assetId: 'base-of-influence',
                        name: 'Base of Influence',
                        type: 'special',
                        hp: hqMaxHp,
                        maxHp: hqMaxHp,
                        location: hqLocation,
                        qualities: [],
                        stealth: false,
                        notes: '',
                        isHQ: true,
                    });
                }
                this.closeModal('factionModal');
            },

            confirmDeleteFaction(faction) {
                this.deleteConfirmText = `Delete faction "${faction.name}" and all its assets?`;
                this.deleteCallback = () => {
                    this.state.factions = this.state.factions.filter(f => f.id !== faction.id);
                };
                this.openModal('deleteConfirmModal');
            },

            confirmDeleteAsset(faction, asset) {
                this.deleteConfirmText = `Remove "${asset.name}" from ${faction.name}?`;
                this.deleteCallback = () => {
                    faction.assets = faction.assets.filter(a => a.id !== asset.id);
                };
                this.openModal('deleteConfirmModal');
            },

            confirmClearAll() {
                this.deleteConfirmText = 'Clear all factions, assets, and turn history? This cannot be undone.';
                this.deleteCallback = () => {
                    this.state = S.defaultState();
                    this.runningTurn = false;
                    this.turnPhase = '';
                    this.turnInitiative = [];
                    this.currentFactionIdx = 0;
                    this.currentAction = null;
                    this.currentTurnEntries = [];
                    this.fullTurnEntries = [];
                };
                this.openModal('deleteConfirmModal');
            },

            executeDelete() {
                if (this.deleteCallback) {
                    this.deleteCallback();
                    this.deleteCallback = null;
                }
                this.closeModal('deleteConfirmModal');
            },

            // ===== Asset Helpers =====
            getAssetStaticData(assetId) {
                return this.ASSET_DATA.assets?.find(a => a.id === assetId) || null;
            },

            getAssetDescription(assetId) {
                const data = this.getAssetStaticData(assetId);
                return data?.description?.en || '';
            },

            getAssetQualities(asset) {
                const data = this.getAssetStaticData(asset.assetId);
                const baseQualities = data?.qualities || [];
                const extra = asset.qualities || [];
                const all = [...new Set([...baseQualities, ...extra])];
                return all.map(q => this.capitalize(q));
            },

            formatAttack(attack) {
                if (!attack) return 'None';
                const atk = attack.atk_attr === 'special' ? 'Special' : attack.atk_attr.charAt(0).toUpperCase();
                const def = attack.def_attr === 'special' ? 'Special' : attack.def_attr.charAt(0).toUpperCase();
                const dmg = attack.damage === 'special' ? 'Special' : attack.damage;
                return `${atk} v. ${def} / ${dmg}`;
            },

            toggleAsset(assetId) {
                this.expandedAsset = this.expandedAsset === assetId ? null : assetId;
            },

            updateAssetLocation(factionId, assetId, location) {
                const faction = this.state.factions.find(f => f.id === factionId);
                if (faction) {
                    const asset = faction.assets.find(a => a.id === assetId);
                    if (asset) asset.location = location;
                }
            },

            // ===== Asset CRUD =====
            openAddAsset(faction) {
                this.addAssetFaction = faction;
                this.addAssetForm = { assetId: '', location: '' };
                this.openModal('addAssetModal');
            },

            countAssetsOfType(faction, type) {
                return R.countAssetsOfType(faction, type);
            },

            getEligibleAssets(faction) {
                return R.eligibleAssetsToBuy(faction, this.ASSET_DATA.assets);
            },

            getEligibleAssetsByType(faction, type) {
                return this.getEligibleAssets(faction).filter(a => a.type === type);
            },

            confirmAddAsset() {
                if (!this.addAssetFaction || !this.addAssetForm.assetId) return;
                const assetData = this.getAssetStaticData(this.addAssetForm.assetId);
                if (!assetData) return;

                this.addAssetFaction.assets.push({
                    id: this.uuid(),
                    assetId: this.addAssetForm.assetId,
                    name: assetData.name.en,
                    type: assetData.type,
                    hp: assetData.hp,
                    maxHp: assetData.hp,
                    location: this.addAssetForm.location,
                    qualities: [],
                    stealth: false,
                    notes: '',
                });
                this.closeModal('addAssetModal');
            },

            // ===== Reference Data Helpers =====
            getQualityTooltip(quality, assetId) {
                if (quality === 'Special') return this.getAssetDescription(assetId);
                return C.QUALITY_DESCRIPTIONS[quality] || '';
            },

            getGoalName(goalId) {
                if (!goalId) return '';
                const goal = this.ASSET_DATA.goals?.find(g => g.id === goalId);
                return goal?.name?.en || goalId;
            },

            getGoalDescription(goalId) {
                if (!goalId) return '';
                const goal = this.ASSET_DATA.goals?.find(g => g.id === goalId);
                if (!goal) return '';
                return `${goal.description?.en || ''} (Difficulty: ${goal.difficulty})`;
            },

            getTagDescription(tagId) {
                const tag = this.ASSET_DATA.tags?.find(t => t.id === tagId);
                return tag?.description?.en || '';
            },

            getFaction(factionId) {
                return this.state.factions.find(f => f.id === factionId);
            },

            // ===== Turn Execution =====
            startTurn() {
                this.runningTurn = true;
                this.turnPhase = C.TURN_PHASE.INITIATIVE;
                this.fullTurnEntries = [];
                this.currentFactionIdx = 0;

                this.turnInitiative = this.state.factions.map(f => ({
                    factionId: f.id,
                    roll: R.rollInitiative(),
                }));
                this.sortInitiative();
            },

            sortInitiative() {
                this.turnInitiative.sort((a, b) => b.roll - a.roll);
            },

            rerollInitiative(init) {
                init.roll = R.rollInitiative();
                this.sortInitiative();
            },

            proceedToFactionTurns() {
                this.turnPhase = C.TURN_PHASE.FACTION;
                this.currentFactionIdx = 0;
                this.setupCurrentFactionTurn();
            },

            currentTurnFaction() {
                if (this.turnInitiative.length === 0) return this.state.factions[0];
                const init = this.turnInitiative[this.currentFactionIdx];
                return this.getFaction(init?.factionId) || this.state.factions[0];
            },

            setupCurrentFactionTurn() {
                const faction = this.currentTurnFaction();
                this.currentAction = null;
                this.currentFactionNote = '';
                this.currentTurnEntries = [];
                this.lastActionSnapshot = null;

                this.attackState = { attackerAssetId: '', targetFactionId: '', defenderAssetId: '', step: 1, rolled: false, hit: false, rollText: '', damageText: '', manualAtk: null, manualDef: null, moreAttacks: false };
                this.moveState = { assetId: '', destination: '', movedCount: 0 };
                this.createState = { assetId: '', location: '', lastCreated: '' };
                this.repairState = { assetId: '' };
                this.factionHpRepairedThisTurn = false;
                this.repairsThisTurn = 0;
                this.expandState = { location: '', baseHp: 1, baseCreated: false, rivalChecks: [], rivalFactionId: '' };
                this.simpleActionState = { assetId: '' };

                // Auto-calc treasure
                const treasureEarned = R.calcTreasureIncome(faction);
                faction.treasure += treasureEarned;
                this.currentAutoTreasure = treasureEarned;
                this.currentTurnEntries.push({
                    factionId: faction.id,
                    type: C.ENTRY.AUTO,
                    text: `Earned ${treasureEarned} Treasure → now ${faction.treasure}`,
                });

                // Pay upkeep (per-asset)
                this.currentUpkeepResults = [];
                const plan = R.planUpkeep(faction, (id) => this.getAssetStaticData(id));
                faction.treasure = plan.treasureAfter;
                for (const line of plan.lines) {
                    if (line.paid) {
                        this.currentUpkeepResults.push({
                            assetId: line.assetId,
                            text: `Upkeep: −${line.upkeep} ${line.name} → now ${faction.treasure}`,
                        });
                        this.currentTurnEntries.push({
                            factionId: faction.id,
                            type: C.ENTRY.AUTO,
                            text: `Upkeep: −${line.upkeep} (${line.name})`,
                        });
                    } else {
                        this.currentUpkeepResults.push({
                            assetId: line.assetId,
                            text: `⚠ Cannot pay upkeep for ${line.name} (needs ${line.upkeep}, has ${faction.treasure})`,
                        });
                        this.currentTurnEntries.push({
                            factionId: faction.id,
                            type: C.ENTRY.AUTO,
                            text: `⚠ Cannot pay upkeep for ${line.name}!`,
                        });
                    }
                }

                // Asset cap excess check (per attr; resolve via Pay or Remove in UI)
                this.currentExcess = R.getExcessAssets(faction).map(ex => ({
                    type: ex.type,
                    count: ex.count,
                    cap: ex.cap,
                    excess: ex.excess,
                    resolved: false,
                }));
                for (const ex of this.currentExcess) {
                    const label = this.capitalize(ex.type);
                    this.currentTurnEntries.push({
                        factionId: faction.id,
                        type: C.ENTRY.AUTO,
                        text: `⚠ Excess ${label} assets (${ex.count}/${ex.cap}) — pay ${ex.excess}T or remove ${ex.excess}`,
                    });
                }

                // Apply (and clear) goal-abandonment penalty from previous turn
                const penalty = faction.nextTurnPenalty || { suppressAction: false, suppressAbilities: false };
                this.actionSuppressed = !!penalty.suppressAction;
                this.abilitiesSuppressed = !!penalty.suppressAbilities;
                if (penalty.suppressAction || penalty.suppressAbilities) {
                    this.currentTurnEntries.push({
                        factionId: faction.id,
                        type: C.ENTRY.AUTO,
                        text: '⚠ Goal-abandonment penalty: no action and no asset special abilities this turn',
                    });
                }
                faction.nextTurnPenalty = { suppressAction: false, suppressAbilities: false };

                // Identify special abilities (informational)
                this.currentAbilities = [];
                if (!this.abilitiesSuppressed) {
                    for (const asset of faction.assets) {
                        const data = this.getAssetStaticData(asset.assetId);
                        if (data && data.qualities?.includes(C.QUALITY.SPECIAL)) {
                            this.currentAbilities.push({
                                assetId: asset.id,
                                assetName: asset.name,
                                location: asset.location || '—',
                                description: data.description?.en || '',
                                resolved: false,
                                used: false,
                            });
                        }
                    }
                }
            },

            resolveAbility(ability, used) {
                ability.resolved = true;
                ability.used = used;
                if (used) {
                    this.currentTurnEntries.push({
                        factionId: this.currentTurnFaction().id,
                        type: C.ENTRY.ABILITY,
                        text: `Ability: ${ability.assetName} — used`,
                    });
                }
            },

            // ===== Action Execution =====
            startAction(action) { this.currentAction = action; },

            // Snapshot all factions + per-turn ephemeral counters before any executeX
            // mutates them. Allows one-step undo of the just-executed action.
            captureUndoSnapshot() {
                this.lastActionSnapshot = {
                    factions: JSON.parse(JSON.stringify(this.state.factions)),
                    currentTurnEntriesLen: this.currentTurnEntries.length,
                    repairsThisTurn: this.repairsThisTurn,
                    factionHpRepairedThisTurn: this.factionHpRepairedThisTurn,
                    currentAbilities: JSON.parse(JSON.stringify(this.currentAbilities)),
                };
            },

            canUndoLastAction() { return !!this.lastActionSnapshot; },

            undoLastAction() {
                const snap = this.lastActionSnapshot;
                if (!snap) return;
                this.state.factions = snap.factions;
                this.currentTurnEntries = this.currentTurnEntries.slice(0, snap.currentTurnEntriesLen);
                this.repairsThisTurn = snap.repairsThisTurn;
                this.factionHpRepairedThisTurn = snap.factionHpRepairedThisTurn;
                this.currentAbilities = snap.currentAbilities;
                this.lastActionSnapshot = null;
                this.cancelAction();
            },

            cancelAction() {
                this.currentAction = null;
                this.attackState = { attackerAssetId: '', targetFactionId: '', defenderAssetId: '', step: 1, rolled: false, hit: false, rollText: '', damageText: '', manualAtk: null, manualDef: null, moreAttacks: false };
                this.moveState = { assetId: '', destination: '', movedCount: 0 };
                this.createState = { assetId: '', location: '', lastCreated: '' };
                this.repairState = { assetId: '' };
                this.expandState = { location: '', baseHp: 1, baseCreated: false, rivalChecks: [], rivalFactionId: '' };
                this.simpleActionState = { assetId: '' };
            },

            getAttackableAssets(faction) {
                return faction.assets.filter(a => {
                    const data = this.getAssetStaticData(a.assetId);
                    return data?.attack != null;
                });
            },

            getEnemyFactions() {
                const currentId = this.currentTurnFaction().id;
                return this.state.factions.filter(f => f.id !== currentId);
            },

            getDefendableAssets(factionId, attackerAssetId) {
                const faction = this.getFaction(factionId);
                return faction ? faction.assets : [];
            },

            getAttackNotation() {
                const attacker = this.currentTurnFaction().assets.find(a => a.id === this.attackState.attackerAssetId);
                if (!attacker) return '';
                const data = this.getAssetStaticData(attacker.assetId);
                if (!data?.attack) return '';
                return `${this.capitalize(data.attack.atk_attr)} vs ${this.capitalize(data.attack.def_attr)}`;
            },

            executeAttack() {
                this.captureUndoSnapshot();
                const faction = this.currentTurnFaction();
                const attacker = faction.assets.find(a => a.id === this.attackState.attackerAssetId);
                const targetFaction = this.getFaction(this.attackState.targetFactionId);
                const defender = targetFaction?.assets.find(a => a.id === this.attackState.defenderAssetId);
                if (!attacker || !targetFaction || !defender) return;

                const atkData = this.getAssetStaticData(attacker.assetId);
                const defData = this.getAssetStaticData(defender.assetId);
                if (!atkData?.attack) return;

                const atkAttr = faction[atkData.attack.atk_attr] || 0;
                const defAttr = targetFaction[atkData.attack.def_attr] || 0;
                const result = R.rollAttack({ atkAttr, defAttr });

                this.attackState.rolled = true;
                this.attackState.hit = result.hit;
                this.attackState.rollText = `1d10+${atkAttr} vs 1d10+${defAttr} → [${result.atkRoll}]+${atkAttr}=${result.atkTotal} vs [${result.defRoll}]+${defAttr}=${result.defTotal}`;

                Alpine.store('dice').displayResult(
                    `${attacker.name} → ${defender.name}`,
                    '1d10', [result.atkRoll], atkAttr, result.atkTotal,
                    result.hit ? 'success' : 'fail'
                );

                if (result.hit && atkData.attack.damage && atkData.attack.damage !== 'special') {
                    const dmg = R.rollDamage(atkData.attack.damage, Alpine.store('dice'));
                    if (dmg) {
                        const delta = R.applyDamageDelta(defender, dmg.total, targetFaction);
                        defender.hp = delta.targetHpAfter;
                        targetFaction.hp = delta.factionHpAfter;
                        let dmgText = `Damage: ${atkData.attack.damage} → [${dmg.rolls.join(',')}] = ${dmg.total}`;
                        if (delta.factionDmg > 0) dmgText += ` (Faction HP: −${delta.factionDmg} → ${targetFaction.hp})`;
                        dmgText += delta.destroyed ? ' — DESTROYED!' : ` → HP: ${defender.hp}/${defender.maxHp}`;
                        this.attackState.damageText = dmgText;
                        if (delta.destroyed) {
                            targetFaction.assets = targetFaction.assets.filter(a => a.id !== defender.id);
                        }
                    }
                } else if (!result.hit && defData?.counter) {
                    const ctr = R.rollDamage(defData.counter.damage, Alpine.store('dice'));
                    if (ctr) {
                        const delta = R.applyDamageDelta(attacker, ctr.total, faction);
                        attacker.hp = delta.targetHpAfter;
                        faction.hp = delta.factionHpAfter;
                        this.attackState.damageText = `Counterattack: ${defData.counter.damage} → [${ctr.rolls.join(',')}] = ${ctr.total}${delta.destroyed ? ' — DESTROYED!' : ' → HP: ' + attacker.hp + '/' + attacker.maxHp}`;
                        if (delta.destroyed) {
                            faction.assets = faction.assets.filter(a => a.id !== attacker.id);
                        }
                    }
                } else if (result.hit && atkData.attack.damage === 'special') {
                    this.attackState.damageText = 'Special effect — resolve manually';
                }
            },

            executeAttackManual() {
                const atk = this.attackState.manualAtk;
                const def = this.attackState.manualDef;
                if (atk == null || def == null) return;

                const hit = atk > def;
                this.attackState.rolled = true;
                this.attackState.hit = hit;
                this.attackState.rollText = `Manual: ${atk} vs ${def}`;
                this.attackState.damageText = hit ? 'Hit — resolve damage manually' : 'Miss — resolve counterattack manually';
            },

            confirmAttackResult() {
                const attacker = this.currentTurnFaction().assets.find(a => a.id === this.attackState.attackerAssetId);
                const targetFaction = this.getFaction(this.attackState.targetFactionId);
                const defenderName = this.attackState.defenderAssetId
                    ? (targetFaction?.assets.find(a => a.id === this.attackState.defenderAssetId)?.name || 'asset')
                    : 'asset';

                this.currentTurnEntries.push({
                    factionId: this.currentTurnFaction().id,
                    type: C.ENTRY.ACTION,
                    action: C.ACTION.ATTACK,
                    text: `Attack: ${attacker?.name || 'asset'} → ${targetFaction?.name}'s ${defenderName}`,
                    rollText: this.attackState.rollText,
                    damageText: this.attackState.damageText,
                    roll: true,
                });

                if (this.attackState.moreAttacks) this.resetAttackForMore();
            },

            resetAttackForMore() {
                this.attackState = { ...this.attackState, attackerAssetId: '', targetFactionId: '', defenderAssetId: '', step: 1, rolled: false, hit: false, rollText: '', damageText: '', manualAtk: null, manualDef: null, moreAttacks: false };
            },

            executeMove() {
                this.captureUndoSnapshot();
                const faction = this.currentTurnFaction();
                const asset = faction.assets.find(a => a.id === this.moveState.assetId);
                if (!asset) return;
                const from = asset.location || 'unknown';
                asset.location = this.moveState.destination;

                this.currentTurnEntries.push({
                    factionId: faction.id,
                    type: C.ENTRY.ACTION,
                    action: C.ACTION.MOVE,
                    text: `Move: ${asset.name} from ${from} → ${this.moveState.destination}`,
                });
                this.moveState.movedCount++;
                this.moveState.assetId = '';
                this.moveState.destination = '';
            },

            executeCreate() {
                this.captureUndoSnapshot();
                const faction = this.currentTurnFaction();
                const assetData = this.getAssetStaticData(this.createState.assetId);
                if (!assetData) return;

                if (faction.treasure < assetData.cost) {
                    alert('Not enough Treasure!');
                    return;
                }

                const capCount = R.countAssetsOfType(faction, assetData.type);
                if (capCount >= faction[assetData.type]) {
                    alert(`Attribute cap reached: you have ${capCount}/${faction[assetData.type]} ${assetData.type} assets. Raise your ${assetData.type} attribute to purchase more.`);
                    return;
                }

                if (!R.magicLevelMet(faction.magic, assetData.magic_req)) {
                    alert('Magic level insufficient for this asset.');
                    return;
                }

                faction.treasure -= assetData.cost;
                faction.assets.push({
                    id: this.uuid(),
                    assetId: this.createState.assetId,
                    name: assetData.name.en,
                    type: assetData.type,
                    hp: assetData.hp,
                    maxHp: assetData.hp,
                    location: this.createState.location,
                    qualities: [],
                    stealth: false,
                    notes: '',
                });

                this.currentTurnEntries.push({
                    factionId: faction.id,
                    type: C.ENTRY.ACTION,
                    action: C.ACTION.CREATE,
                    text: `Create: ${assetData.name.en} at ${this.createState.location} (−${assetData.cost} Treasure)`,
                });

                this.createState.lastCreated = `${assetData.name.en} at ${this.createState.location}`;
                this.createState.assetId = '';
            },

            getDamagedAssets(faction) {
                return faction.assets.filter(a => a.hp < a.maxHp);
            },

            // Per-attribute assets to choose for excess removal (excludes BoI).
            getExcessCandidates(type) {
                const faction = this.currentTurnFaction();
                return (faction.assets || []).filter(a => a.type === type && a.assetId !== 'base-of-influence');
            },

            payExcessUpkeep(ex) {
                const faction = this.currentTurnFaction();
                if (faction.treasure < ex.excess) {
                    alert(`Not enough Treasure (need ${ex.excess}, have ${faction.treasure}).`);
                    return;
                }
                faction.treasure -= ex.excess;
                ex.resolved = true;
                this.currentTurnEntries.push({
                    factionId: faction.id,
                    type: C.ENTRY.AUTO,
                    text: `Paid ${ex.excess}T excess upkeep for ${this.capitalize(ex.type)} → now ${faction.treasure}`,
                });
            },

            removeExcessAsset(ex, assetId) {
                if (!assetId) return;
                const faction = this.currentTurnFaction();
                const asset = faction.assets.find(a => a.id === assetId);
                if (!asset) return;
                faction.assets = faction.assets.filter(a => a.id !== assetId);
                this.currentTurnEntries.push({
                    factionId: faction.id,
                    type: C.ENTRY.AUTO,
                    text: `Removed excess ${this.capitalize(ex.type)} asset: ${asset.name}`,
                });
                // Recompute excess for this type and clear if at/under cap.
                const remainingCount = R.countAssetsOfType(faction, ex.type);
                ex.count = remainingCount;
                ex.excess = Math.max(0, remainingCount - ex.cap);
                if (ex.excess === 0) ex.resolved = true;
            },

            getRepairAmount(assetId) {
                const faction = this.currentTurnFaction();
                if (assetId === '__faction__') return R.calcRepairAmount('__faction__', faction);
                const asset = faction.assets.find(a => a.id === assetId);
                return asset ? R.calcRepairAmount(asset, faction) : 0;
            },

            getRepairCost() {
                return R.calcRepairCost(this.repairsThisTurn || 0);
            },

            executeRepair() {
                this.captureUndoSnapshot();
                const faction = this.currentTurnFaction();
                const cost = this.getRepairCost();
                if (faction.treasure < cost) {
                    alert(`Not enough Treasure! Repair #${(this.repairsThisTurn || 0) + 1} costs ${cost}.`);
                    return;
                }

                const heal = this.getRepairAmount(this.repairState.assetId);
                faction.treasure -= cost;
                this.repairsThisTurn = (this.repairsThisTurn || 0) + 1;

                if (this.repairState.assetId === '__faction__') {
                    const max = this.getMaxHp(faction);
                    faction.hp = Math.min(max, faction.hp + heal);
                    this.factionHpRepairedThisTurn = true;
                    this.currentTurnEntries.push({
                        factionId: faction.id,
                        type: C.ENTRY.ACTION,
                        action: C.ACTION.REPAIR,
                        text: `Repair: Faction HP +${heal} (−${cost} Treasure) → ${faction.hp}/${max}`,
                    });
                } else {
                    const asset = faction.assets.find(a => a.id === this.repairState.assetId);
                    if (asset) {
                        asset.hp = Math.min(asset.maxHp, asset.hp + heal);
                        this.currentTurnEntries.push({
                            factionId: faction.id,
                            type: C.ENTRY.ACTION,
                            action: C.ACTION.REPAIR,
                            text: `Repair: ${asset.name} +${heal} HP (−${cost} Treasure) → ${asset.hp}/${asset.maxHp}`,
                        });
                    }
                }
            },

            executeHide() {
                this.captureUndoSnapshot();
                const faction = this.currentTurnFaction();
                const asset = faction.assets.find(a => a.id === this.simpleActionState.assetId);
                if (!asset || faction.cunning < 3 || faction.treasure < 2) return;

                faction.treasure -= 2;
                asset.stealth = true;

                this.currentTurnEntries.push({
                    factionId: faction.id,
                    type: C.ENTRY.ACTION,
                    action: C.ACTION.HIDE,
                    text: `Hide: ${asset.name} gains Stealth (−2 Treasure)`,
                });
            },

            getSellValue(asset) {
                return R.calcSellValue(asset, (id) => this.getAssetStaticData(id));
            },

            executeSell() {
                this.captureUndoSnapshot();
                const faction = this.currentTurnFaction();
                const asset = faction.assets.find(a => a.id === this.simpleActionState.assetId);
                if (!asset) return;

                const refund = this.getSellValue(asset);
                faction.treasure += refund;
                faction.assets = faction.assets.filter(a => a.id !== asset.id);

                this.currentTurnEntries.push({
                    factionId: faction.id,
                    type: C.ENTRY.ACTION,
                    action: C.ACTION.SELL,
                    text: `Sell: ${asset.name} (+${refund} Treasure)`,
                });
            },

            executeExpand() {
                this.captureUndoSnapshot();
                const faction = this.currentTurnFaction();
                if (faction.treasure < this.expandState.baseHp) return;

                faction.treasure -= this.expandState.baseHp;
                faction.assets.push({
                    id: this.uuid(),
                    assetId: 'base-of-influence',
                    name: 'Base of Influence',
                    type: 'special',
                    hp: this.expandState.baseHp,
                    maxHp: this.expandState.baseHp,
                    location: this.expandState.location,
                    qualities: [],
                    stealth: false,
                    notes: '',
                });

                this.currentTurnEntries.push({
                    factionId: faction.id,
                    type: C.ENTRY.ACTION,
                    action: C.ACTION.EXPAND,
                    text: `Expand Influence: New Base at ${this.expandState.location} (HP: ${this.expandState.baseHp}, −${this.expandState.baseHp} Treasure)`,
                });
                this.expandState.baseCreated = true;
                this.expandState.rivalChecks = [];
                this.expandState.rivalFactionId = '';
            },

            executeExpandRivalCheck(factionId) {
                const myFaction = this.currentTurnFaction();
                const rival = this.getFaction(factionId);
                if (!rival) return;

                const result = R.rollAttack({ atkAttr: myFaction.cunning, defAttr: rival.cunning });
                const rivalWins = !result.hit;
                this.expandState.rivalChecks.push({
                    factionId,
                    rivalName: rival.name,
                    myTotal: result.atkTotal,
                    rivTotal: result.defTotal,
                    rivalWins,
                });
                this.currentTurnEntries.push({
                    factionId: myFaction.id,
                    type: C.ENTRY.AUTO,
                    text: `Expand check vs ${rival.name}: You ${result.atkTotal} (${result.atkRoll}+${myFaction.cunning}) vs ${rival.name} ${result.defTotal} (${result.defRoll}+${rival.cunning}) — ${rivalWins ? '⚠ Rival wins — may Attack immediately' : '✓ Rival fails'}`,
                });
            },

            completeGoal() {
                const faction = this.currentTurnFaction();
                const goal = this.ASSET_DATA.goals?.find(g => g.id === faction.goal.type);
                const xp = goal ? parseInt(goal.difficulty) || 1 : 1;
                faction.xp += xp;

                this.currentTurnEntries.push({
                    factionId: faction.id,
                    type: C.ENTRY.GOAL,
                    text: `Goal Complete: ${this.getGoalName(faction.goal.type)} (+${xp} XP)`,
                });

                faction.goal = { type: '', progress: 0, target: 0 };
            },

            setGoal(goalId) {
                if (!goalId) return;
                const faction = this.currentTurnFaction();
                if (faction.goal?.type) {
                    faction.nextTurnPenalty = { suppressAction: true, suppressAbilities: true };
                    this.currentTurnEntries.push({
                        factionId: faction.id,
                        type: C.ENTRY.AUTO,
                        text: `⚠ Goal abandoned (${this.getGoalName(faction.goal.type)}) — forfeits next turn's action and asset special abilities`,
                    });
                }
                faction.goal = { type: goalId, progress: 0, target: 0 };
                this.currentTurnEntries.push({
                    factionId: faction.id,
                    type: C.ENTRY.AUTO,
                    text: `New Goal: ${this.getGoalName(goalId)}`,
                });
            },

            raiseAttribute(attrName) {
                const faction = this.currentTurnFaction();
                const oldVal = faction[attrName];
                const cost = this.getXpCostForNext(oldVal);
                if (oldVal >= 8 || faction.xp < cost) return;

                const oldMaxHp = this.getMaxHp(faction);
                faction.xp -= cost;
                faction[attrName] = oldVal + 1;
                const newMaxHp = this.getMaxHp(faction);
                const hpDiff = newMaxHp - oldMaxHp;

                faction.hp += hpDiff;

                const hqBase = faction.assets.find(a => a.isHQ === true);
                if (hqBase) {
                    hqBase.maxHp = newMaxHp;
                    hqBase.hp += hpDiff;
                }

                this.currentTurnEntries.push({
                    factionId: faction.id,
                    type: C.ENTRY.XP,
                    text: `Raised ${this.capitalize(attrName)} ${oldVal} → ${oldVal + 1} (−${cost} XP)`,
                });
            },

            // ===== Finish Faction Turn =====
            finishFactionTurn() {
                if (this.currentAction === C.ACTION.NONE) {
                    this.currentTurnEntries.push({
                        factionId: this.currentTurnFaction().id,
                        type: C.ENTRY.ACTION,
                        action: C.ACTION.NONE,
                        text: 'No action taken',
                    });
                }

                if (this.currentFactionNote.trim()) {
                    this.currentTurnEntries.push({
                        factionId: this.currentTurnFaction().id,
                        type: C.ENTRY.MANUAL,
                        text: '',
                        note: this.currentFactionNote.trim(),
                    });
                }

                this.fullTurnEntries = this.fullTurnEntries.concat(
                    this.currentTurnEntries.map(e => ({ ...e }))
                );

                if (this.currentFactionIdx < this.turnInitiative.length - 1) {
                    this.currentFactionIdx++;
                    this.setupCurrentFactionTurn();
                } else {
                    this.completeTurn();
                }
            },

            completeTurn() {
                this.state.currentTurn++;
                this.state.log.push({
                    turn: this.state.currentTurn,
                    title: '',
                    initiative: [...this.turnInitiative],
                    entries: [...this.fullTurnEntries],
                });
                this.runningTurn = false;
                this.turnPhase = '';
                this.fullTurnEntries = [];
            },

            // ===== Turn Log =====
            updateTurnTitle(turnNum, title) {
                const turn = this.state.log.find(t => t.turn === turnNum);
                if (turn) turn.title = title;
            },

            addManualEntry() {
                if (!this.manualEntryForm.text) return;

                if (this.state.log.length === 0) {
                    this.state.log.push({
                        turn: 0,
                        title: 'Pre-game',
                        initiative: [],
                        entries: [],
                    });
                }

                const lastTurn = this.state.log[this.state.log.length - 1];
                lastTurn.entries.push({
                    factionId: this.manualEntryForm.factionId || null,
                    type: C.ENTRY.MANUAL,
                    text: this.manualEntryForm.text,
                    note: null,
                });

                this.closeModal('manualEntryModal');
            },
        };
    }

    window.factionTracker = factionTracker;

    // Reusable manual-override widget. Usage:
    //   <span x-data="autoValue({ get: () => faction.treasure, set: (v) => faction.treasure = v })">
    //       <template x-if="!edit"><span x-text="value()"></span></template>
    //       <template x-if="edit"><input x-model.number="draft" @keydown.enter="commit()" @blur="commit()"></template>
    //       <button class="auto-value-edit-btn" @click="start()" x-show="!edit"><i class="bi bi-pencil"></i></button>
    //   </span>
    document.addEventListener('alpine:init', () => {
        if (typeof Alpine === 'undefined') return;
        Alpine.data('autoValue', ({ get, set }) => ({
            edit: false,
            draft: 0,
            value() { return get(); },
            start() { this.draft = get(); this.edit = true; },
            commit() {
                if (!this.edit) return;
                if (typeof this.draft === 'number' && !Number.isNaN(this.draft)) set(this.draft);
                this.edit = false;
            },
            cancel() { this.edit = false; },
        }));
    });
})();
