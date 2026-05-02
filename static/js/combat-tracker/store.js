(function() {
    const weaponsDataEl = document.getElementById('combat-tracker-weapons');
    const weaponTraitsEl = document.getElementById('combat-tracker-weapon-traits');
    const weaponsData = weaponsDataEl ? JSON.parse(weaponsDataEl.textContent) : [];
    const weaponTraitsData = weaponTraitsEl ? JSON.parse(weaponTraitsEl.textContent) : {};

    const groupColors = [
        '#dc3545', '#fd7e14', '#6f42c1', '#0dcaf0',
        '#d63384', '#20c997', '#ffc107', '#6610f2',
    ];

    const NPC_TEMPLATES_URL = '/static/data/wwn_npc_templates.json';

    function combatTracker() {
        return {
            // State
            round: 1,
            roundFlash: false,
            currentTurnId: null,
            openTooltipId: null,
            expandedAbilitiesId: null,  // Combatant ID with expanded abilities
            combatants: [],  // NPCs have stats embedded, PCs reference pcs array
            pcs: [],

            // Modals
            addModalOpen: false,
            hpModalOpen: false,
            hpModalTarget: null,
            hpModalAmount: 0,
            formTab: 'npc',
            npcInputMode: 'template',  // 'template' or 'paste'
            statblockPaste: '',
            parseError: '',

            // NPC Form
            npcForm: {
                name: 'Monster',
                group: '',
                count: 1,
                hd: 1,
                hpMode: 'roll',
                ac: 10,
                hasArmor: false,
                hasShield: false,
                bab: 0,
                attacks: 1,

                // Damage configuration
                damageMode: 'weapon',     // 'weapon' | 'dice'
                weaponId: 'spear-light',
                diceCount: 1,
                diceType: 6,
                attackName: '',           // Custom attack name for dice mode
                dmgBonus: 0,
                shockValue: 0,
                shockAC: '10',
                shockOverride: false,

                mv: "30'",
                hasFly: false,
                hasSwim: false,
                ml: 7,
                inst: 5,
                skl: 1,
                sv: 15,
                abilities: []  // Array of {name, description}
            },

            // Group initiative tracking
            groupInitiatives: {},  // { "Group 1": 5, "Group 2": 3 }
            nextGroupNum: 1,       // For auto-naming groups
            editingGroup: null,    // Group name currently being edited
            editingCombatant: null, // Combatant ID for inline name editing
            editModalCombatantId: null, // Combatant ID for modal editing

            // PC Form
            pcForm: {
                name: 'Adventurer',
                group: '',
                level: 1,
                ac: 10,
                maxHp: 6,
                systemStrain: 0
            },

            // NPC templates (loaded from JSON in init)
            npcTemplates: [],

            // Computed
            get sortedCombatants() {
                return [...this.combatants].sort((a, b) => {
                    const initA = a.initiative ?? -999;
                    const initB = b.initiative ?? -999;
                    return initB - initA;
                });
            },

            get canStartCombat() {
                // Need combatants, not already in combat, and at least one initiative set
                if (this.combatants.length === 0) return false;
                if (this.currentTurnId !== null) return false;
                // Check if any group or individual has initiative
                const hasGroupInit = Object.values(this.groupInitiatives).some(init => init !== null);
                const hasIndividualInit = this.combatants.some(c => this.isIndividual(c) && c.initiative !== null);
                return hasGroupInit || hasIndividualInit;
            },

            get allGroups() {
                // Group all combatants (PCs and NPCs) by their group name, excluding individuals
                const groups = {};

                // Include empty groups from groupInitiatives (except _individual)
                Object.keys(this.groupInitiatives).forEach(groupName => {
                    if (groupName !== '_individual' && !groups[groupName]) {
                        groups[groupName] = {
                            name: groupName,
                            initiative: this.groupInitiatives[groupName] ?? null,
                            combatants: []
                        };
                    }
                });

                this.combatants.forEach(c => {
                    const groupName = this.getCombatantGroup(c);

                    // Skip individuals - they're handled separately
                    if (groupName === '_individual') return;

                    if (!groups[groupName]) {
                        groups[groupName] = {
                            name: groupName,
                            initiative: this.groupInitiatives[groupName] ?? null,
                            combatants: []
                        };
                    }
                    groups[groupName].combatants.push(c);
                });

                // Assign colors to groups
                const groupList = Object.values(groups);
                groupList.forEach((group, index) => {
                    group.color = groupColors[index % groupColors.length];
                });

                return groupList;
            },

            get individualCombatants() {
                // Filter and sort individuals by their initiative
                return this.combatants
                    .filter(c => this.isIndividual(c))
                    .sort((a, b) => {
                        const initA = a.initiative ?? -999;
                        const initB = b.initiative ?? -999;
                        return initB - initA;
                    });
            },

            get sortedGroups() {
                // Mix groups and individual combatants, sorted by initiative
                const items = [];

                // Add all groups
                this.allGroups.forEach(group => {
                    items.push({
                        type: 'group',
                        ...group
                    });
                });

                // Add individual combatants as single-item entries
                this.individualCombatants.forEach(combatant => {
                    items.push({
                        type: 'individual',
                        name: this.getCombatantDisplayName(combatant),
                        initiative: combatant.initiative,
                        combatants: [combatant],
                        color: null
                    });
                });

                // Sort by initiative (highest first), PCs win ties
                return items.sort((a, b) => {
                    const initA = a.initiative ?? -999;
                    const initB = b.initiative ?? -999;
                    if (initA !== initB) return initB - initA;
                    // On tie, PCs go first
                    const aHasPC = a.combatants.some(c => c.type === 'pc');
                    const bHasPC = b.combatants.some(c => c.type === 'pc');
                    if (aHasPC && !bHasPC) return -1;
                    if (!aHasPC && bHasPC) return 1;
                    return 0;
                });
            },

            get existingGroups() {
                // Get unique group names
                return this.allGroups.map(g => g.name);
            },

            // Init
            init() {
                this.loadFromStorage();
                fetch(NPC_TEMPLATES_URL)
                    .then(r => r.ok ? r.json() : [])
                    .then(data => { this.npcTemplates = data; })
                    .catch(err => console.error('Failed to load NPC templates:', err));
            },

            // Helpers
            generateId() {
                return 'c-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
            },

            getWeapon(weaponId) {
                return weaponsData.find(w => w.id === weaponId);
            },

            getPC(id) {
                return this.pcs.find(p => p.id === id);
            },

            getCombatantDisplayName(combatant) {
                if (!combatant) return '';
                if (combatant.type === 'pc') {
                    const pc = this.getPC(combatant.sourceId);
                    return pc?.name || 'Unknown PC';
                } else {
                    // NPC: full name stored directly (including any number)
                    return combatant.name || 'Unknown';
                }
            },

            getCombatantAC(combatant) {
                if (combatant.type === 'pc') {
                    return this.getPC(combatant.sourceId)?.ac || 10;
                } else {
                    return combatant.ac || 10;
                }
            },

            getAcSuffix(combatant) {
                if (combatant.type === 'pc') return '';
                let suffix = '';
                if (combatant.hasArmor) suffix += 'a';
                if (combatant.hasShield) suffix += 's';
                return suffix;
            },

            getMoveSuffix(combatant) {
                if (combatant.type === 'pc') return '';
                let suffix = '';
                if (combatant.hasFly) suffix += 'f';
                if (combatant.hasSwim) suffix += 's';
                return suffix;
            },

            getMoveTooltip(combatant) {
                if (combatant.type === 'pc') return '';
                const parts = [];
                if (combatant.hasFly) parts.push('Fly');
                if (combatant.hasSwim) parts.push('Swim');
                return parts.join(', ');
            },

            getAcTooltip(combatant) {
                if (combatant.type === 'pc') return '';
                const parts = [];
                if (combatant.hasArmor) parts.push('Armor');
                if (combatant.hasShield) parts.push('Shield');
                return parts.join(', ');
            },

            getNpcBab(combatant) {
                const attacks = combatant.attacks > 1 ? ' x' + combatant.attacks : '';
                return '+' + combatant.bab + attacks;
            },

            getWeaponName(combatant) {
                if (combatant.damageMode === 'dice') {
                    return combatant.attackName || 'Attack';
                }
                const weapon = this.getWeapon(combatant.weaponId);
                return weapon?.name?.en || '-';
            },

            hasWeaponTraits(combatant) {
                return this.getWeaponTraits(combatant).length > 0;
            },

            getNpcDamage(combatant) {
                let baseDamage = '';

                // Determine base damage based on mode (default to weapon if not set)
                if (combatant.damageMode === 'dice') {
                    baseDamage = `${combatant.diceCount}d${combatant.diceType}`;
                } else {
                    // Weapon mode (default)
                    const weapon = this.getWeapon(combatant.weaponId);
                    baseDamage = weapon?.damage || '-';
                }

                // ALWAYS add damage bonus (if present and > 0)
                if (combatant.dmgBonus > 0 && baseDamage !== '-') {
                    baseDamage += '+' + combatant.dmgBonus;
                }

                return baseDamage;
            },

            getNpcShock(combatant) {
                // Handle different damage modes (default to weapon if not set)
                if (combatant.damageMode === 'dice') {
                    if (!combatant.shockValue || combatant.shockValue === 0) return 'no';
                    // In dice mode, shock value is set directly (dmg bonus only applies to attack damage)
                    return combatant.shockValue + '/' + combatant.shockAC;  // shockAC can be number or "-"
                } else {
                    // Weapon mode (default)
                    const weapon = this.getWeapon(combatant.weaponId);
                    if (!weapon?.shock) return 'no';
                    // Add damage bonus to shock value
                    const shockVal = weapon.shock.value + (combatant.dmgBonus || 0);
                    // Check if shock override is enabled (applies to all AC)
                    const shockAC = combatant.shockOverride ? '-' : weapon.shock.ac;
                    return shockVal + '/' + shockAC;
                }
            },

            getNpcShockValue(combatant) {
                // Returns just the numeric shock damage value (for damage comparison)
                if (combatant.damageMode === 'dice') {
                    return combatant.shockValue || 0;
                } else {
                    const weapon = this.getWeapon(combatant.weaponId);
                    if (!weapon?.shock) return 0;
                    return weapon.shock.value + (combatant.dmgBonus || 0);
                }
            },

            getNpcMove(combatant) {
                let moveStr = combatant.mv || '-';
                const movementTypes = [];

                if (combatant.hasFly) movementTypes.push('fly');
                if (combatant.hasSwim) movementTypes.push('swim');

                if (movementTypes.length > 0 && moveStr !== '-') {
                    moveStr += ' ' + movementTypes.join(',');
                }

                return moveStr;
            },

            getWeaponTraits(combatant) {
                if (combatant.damageMode === 'dice') return [];
                const weapon = this.getWeapon(combatant.weaponId);
                if (!weapon?.traits) return [];
                const traitData = weaponTraitsData;
                return weapon.traits.map(code => ({
                    code: code,
                    desc: traitData[code]?.en || code
                }));
            },

            updateGroupInitiative(groupName, value) {
                this.groupInitiatives[groupName] = value === '' ? null : parseInt(value);
                this.saveToStorage();
            },

            updateIndividualInitiative(combatantId, value) {
                const combatant = this.combatants.find(c => c.id === combatantId);
                if (combatant) {
                    combatant.initiative = value === '' ? null : parseInt(value);
                    this.saveToStorage();
                }
            },

            getNpcStatLine(combatant) {
                const weapon = this.getWeapon(combatant.weaponId);
                let dmg = combatant.fixedDamage || weapon?.damage || '-';
                if (combatant.dmgBonus > 0 && !combatant.fixedDamage) dmg += '+' + combatant.dmgBonus;

                let shock = '-';
                if (combatant.fixedShock) {
                    shock = combatant.fixedShock;
                } else if (weapon?.shock) {
                    const shockVal = weapon.shock.value + (combatant.dmgBonus || 0);
                    shock = shockVal + '/AC' + weapon.shock.ac;
                }

                const attacks = combatant.attacks > 1 ? ' x' + combatant.attacks : '';

                return [
                    { label: 'BAB', value: '+' + combatant.bab + attacks },
                    { label: 'Dmg', value: dmg },
                    { label: 'Shock', value: shock },
                    { label: 'ML', value: combatant.ml },
                    { label: 'Inst', value: combatant.inst },
                ];
            },

            getPcStatLine(combatant) {
                const pc = this.getPC(combatant.sourceId);
                if (!pc) return [];
                return [
                    { label: 'Level', value: pc.level },
                    { label: 'Strain', value: combatant.systemStrain || 0 },
                ];
            },

            rollDice(notation) {
                const match = notation.match(/^(\d+)?d(\d+)([+-]\d+)?$/i);
                if (!match) return null;
                const count = parseInt(match[1]) || 1;
                const sides = parseInt(match[2]);
                const modifier = parseInt(match[3]) || 0;
                const rolls = Array.from({length: count}, () => Math.floor(Math.random() * sides) + 1);
                return rolls.reduce((a, b) => a + b, 0) + modifier;
            },

            // Modal controls
            openAddModal() {
                this.addModalOpen = true;
            },

            openAddToGroup(groupName) {
                // Open modal with group pre-filled
                this.npcForm.group = groupName;
                this.formTab = 'npc';
                this.addModalOpen = true;
            },

            addNewGroup() {
                // Auto-generate group name
                const groupName = 'Group ' + this.nextGroupNum;
                this.nextGroupNum++;
                this.groupInitiatives[groupName] = null;
                this.npcForm.group = groupName;
                this.pcForm.group = groupName;
                this.addModalOpen = true;
                this.saveToStorage();
            },

            addIndividualCombatant() {
                // Add combatant with individual initiative (not in a group)
                this.npcForm.group = '_individual';
                this.pcForm.group = '_individual';
                this.addModalOpen = true;
            },

            openEditCombatant(combatant) {
                this.editModalCombatantId = combatant.id;

                if (combatant.type === 'npc') {
                    // Populate NPC form from combatant (stats are embedded)
                    this.npcForm.name = combatant.name;
                    this.npcForm.group = combatant.group || '_individual';
                    this.npcForm.count = 1;  // Not relevant for editing
                    this.npcForm.hd = combatant.hd;
                    this.npcForm.hpMode = 'average';  // Not relevant for editing
                    this.npcForm.ac = combatant.ac;
                    this.npcForm.hasArmor = combatant.hasArmor || false;
                    this.npcForm.hasShield = combatant.hasShield || false;
                    this.npcForm.bab = combatant.bab;
                    this.npcForm.attacks = combatant.attacks || 1;
                    this.npcForm.damageMode = combatant.damageMode || 'weapon';
                    this.npcForm.weaponId = combatant.weaponId || 'spear-light';
                    this.npcForm.diceCount = combatant.diceCount || 1;
                    this.npcForm.diceType = combatant.diceType || 6;
                    this.npcForm.attackName = combatant.attackName || '';
                    this.npcForm.dmgBonus = combatant.dmgBonus || 0;
                    this.npcForm.shockValue = combatant.shockValue || 0;
                    this.npcForm.shockAC = combatant.shockAC || '10';
                    this.npcForm.shockOverride = combatant.shockOverride || false;
                    this.npcForm.mv = combatant.mv || "30'";
                    this.npcForm.hasFly = combatant.hasFly || false;
                    this.npcForm.hasSwim = combatant.hasSwim || false;
                    this.npcForm.ml = combatant.ml;
                    this.npcForm.inst = combatant.inst;
                    this.npcForm.skl = combatant.skl;
                    this.npcForm.sv = combatant.sv;
                    this.npcForm.abilities = combatant.abilities ? [...combatant.abilities] : [];

                    this.formTab = 'npc';
                    this.npcInputMode = 'template';  // Use template mode for editing
                } else {
                    // PC
                    const pc = this.getPC(combatant.sourceId);
                    if (!pc) return;

                    this.pcForm.name = pc.name;
                    this.pcForm.group = pc.group || '_individual';
                    this.pcForm.level = pc.level;
                    this.pcForm.ac = pc.ac;
                    this.pcForm.maxHp = combatant.maxHp;
                    this.pcForm.systemStrain = combatant.systemStrain || 0;

                    this.formTab = 'pc';
                }

                this.addModalOpen = true;
            },

            startEditingGroup(groupName) {
                this.editingGroup = groupName;
                // Focus the input after Alpine updates the DOM
                this.$nextTick(() => {
                    const input = this.$el.querySelector('.group-name-input:not([style*="display: none"])');
                    if (input) {
                        input.focus();
                        input.select();
                    }
                });
            },

            finishEditingGroup(oldName, newName) {
                this.editingGroup = null;
                if (newName && newName.trim() && newName.trim() !== oldName) {
                    const trimmedName = newName.trim();
                    // Update initiative tracking
                    this.groupInitiatives[trimmedName] = this.groupInitiatives[oldName];
                    delete this.groupInitiatives[oldName];
                    // Update all NPC combatants with this group
                    this.combatants.forEach(c => {
                        if (c.type === 'npc' && c.group === oldName) c.group = trimmedName;
                    });
                    // Update all PCs with this group
                    this.pcs.forEach(pc => {
                        if (pc.group === oldName) pc.group = trimmedName;
                    });
                    this.saveToStorage();
                }
            },

            startEditingCombatant(combatantId) {
                this.editingCombatant = combatantId;
                // Focus the input after Alpine updates the DOM
                this.$nextTick(() => {
                    const input = this.$el.querySelector('.combatant-name-input:not([style*="display: none"])');
                    if (input) {
                        input.focus();
                        input.select();
                    }
                });
            },

            finishEditingCombatant(combatantId, newName) {
                this.editingCombatant = null;
                const combatant = this.combatants.find(c => c.id === combatantId);
                if (combatant && newName !== undefined) {
                    const trimmedName = newName.trim();
                    if (trimmedName) {
                        if (combatant.type === 'npc') {
                            // NPC: update name directly on combatant
                            combatant.name = trimmedName;
                        } else {
                            // PC: update name on the PC record
                            const pc = this.getPC(combatant.sourceId);
                            if (pc) pc.name = trimmedName;
                        }
                        this.saveToStorage();
                    }
                }
            },

            getDefaultCombatantName(combatant) {
                if (!combatant) return '';
                if (combatant.type === 'pc') {
                    const pc = this.getPC(combatant.sourceId);
                    return pc?.name || 'Unknown PC';
                } else {
                    // NPC: full name stored directly
                    return combatant.name || 'Unknown';
                }
            },

            removeGroup(groupName) {
                if (!confirm(`Remove group "${groupName}" and all its combatants?`)) return;

                // Find combatants in this group and remove them
                this.combatants = this.combatants.filter(c => {
                    if (c.type === 'npc') {
                        return c.group !== groupName;
                    } else {
                        const pc = this.getPC(c.sourceId);
                        return pc?.group !== groupName;
                    }
                });

                // Remove PCs belonging to this group
                this.pcs = this.pcs.filter(pc => pc.group !== groupName);

                // Remove group from initiative tracking
                delete this.groupInitiatives[groupName];

                // Clear current turn if it was in this group
                if (this.currentTurnId && !this.combatants.find(c => c.id === this.currentTurnId)) {
                    this.currentTurnId = null;
                }

                this.saveToStorage();
            },

            closeAddModal() {
                this.addModalOpen = false;
                this.editModalCombatantId = null;
                // Reset NPC form to defaults
                this.npcForm.name = 'Monster';
                this.npcForm.group = '';
                this.npcForm.count = 1;
                this.npcForm.hd = 1;
                this.npcForm.hpMode = 'roll';
                this.npcForm.ac = 10;
                this.npcForm.hasArmor = false;
                this.npcForm.hasShield = false;
                this.npcForm.bab = 0;
                this.npcForm.attacks = 1;
                this.npcForm.damageMode = 'weapon';
                this.npcForm.weaponId = 'spear-light';
                this.npcForm.diceCount = 1;
                this.npcForm.diceType = 6;
                this.npcForm.attackName = '';
                this.npcForm.dmgBonus = 0;
                this.npcForm.shockValue = 0;
                this.npcForm.shockAC = '10';
                this.npcForm.shockOverride = false;
                this.npcForm.mv = "30'";
                this.npcForm.hasFly = false;
                this.npcForm.hasSwim = false;
                this.npcForm.ml = 7;
                this.npcForm.inst = 5;
                this.npcForm.skl = 1;
                this.npcForm.sv = 15;
                this.npcForm.abilities = [];
                // Reset PC form to defaults
                this.pcForm.name = 'Adventurer';
                this.pcForm.group = '';
                this.pcForm.level = 1;
                this.pcForm.ac = 10;
                this.pcForm.maxHp = 6;
                this.pcForm.systemStrain = 0;
                // Reset other state
                this.statblockPaste = '';
                this.parseError = '';
                this.npcInputMode = 'template';
            },

            applyTemplate(value) {
                if (!value) return;  // "Custom" selected, don't change anything

                // Parse "Category/TemplateName" (template name may contain /)
                const slashIndex = value.indexOf('/');
                const categoryName = value.substring(0, slashIndex);
                const templateName = value.substring(slashIndex + 1);
                const category = this.npcTemplates.find(c => c.category === categoryName);
                if (!category) return;
                const template = category.templates.find(t => t.name === templateName);
                if (!template) return;

                // Apply template values to form
                this.npcForm.name = template.name;
                this.npcForm.hd = template.hd;
                this.npcForm.ac = template.ac;
                this.npcForm.hasArmor = template.hasArmor || false;
                this.npcForm.hasShield = template.hasShield || false;
                this.npcForm.bab = template.bab;
                this.npcForm.attacks = template.attacks;
                this.npcForm.damageMode = template.damageMode;
                this.npcForm.dmgBonus = template.dmgBonus || 0;
                this.npcForm.shockOverride = template.shockOverride || false;
                this.npcForm.mv = template.mv;
                this.npcForm.hasFly = template.hasFly || false;
                this.npcForm.hasSwim = template.hasSwim || false;
                this.npcForm.ml = template.ml;
                this.npcForm.inst = template.inst;
                this.npcForm.skl = template.skl;
                this.npcForm.sv = template.sv;

                // Dice mode specific fields
                if (template.damageMode === 'dice') {
                    this.npcForm.diceCount = template.diceCount || 1;
                    this.npcForm.diceType = template.diceType || 6;
                    this.npcForm.attackName = template.attackName || '';
                    this.npcForm.shockValue = template.shockValue || 0;
                    this.npcForm.shockAC = template.shockAC || '10';
                } else {
                    this.npcForm.attackName = '';
                }
            },

            parseStatblock() {
                const input = this.statblockPaste.trim();
                if (!input) {
                    this.parseError = '';
                    return;
                }

                try {
                    const starCount = (input.match(/\*/g) || []).length;
                    const pilcrowCount = (input.match(/¶/g) || []).length;
                    const abilityCount = starCount + pilcrowCount;

                    const result = window.CombatTracker.parseStatblock(input);
                    if (!result.ok) {
                        this.parseError = result.error.message;
                        return;
                    }
                    const parsed = result.data;

                    this.npcForm.name = parsed.name;
                    this.npcForm.hd = parsed.hd;
                    this.npcForm.ac = parsed.ac;
                    this.npcForm.hasArmor = parsed.hasArmor || false;
                    this.npcForm.hasShield = parsed.hasShield || false;
                    this.npcForm.bab = parsed.bab;
                    this.npcForm.attacks = parsed.attacks || 1;
                    this.npcForm.mv = parsed.mv;
                    this.npcForm.hasFly = parsed.hasFly || false;
                    this.npcForm.hasSwim = parsed.hasSwim || false;
                    this.npcForm.ml = parsed.ml;
                    this.npcForm.inst = parsed.inst;
                    this.npcForm.skl = parsed.skl;
                    this.npcForm.sv = parsed.sv;

                    if (parsed.damageMode === 'dice') {
                        this.npcForm.damageMode = 'dice';
                        this.npcForm.diceCount = parsed.diceCount || 1;
                        this.npcForm.diceType = parsed.diceType || 6;
                        this.npcForm.attackName = parsed.attackName || '';
                        this.npcForm.dmgBonus = parsed.dmgBonus || 0;
                        this.npcForm.shockValue = parsed.shockValue || 0;
                        this.npcForm.shockAC = parsed.shockAC || '-';
                    } else {
                        this.npcForm.damageMode = 'weapon';
                        this.npcForm.attackName = '';
                        this.npcForm.dmgBonus = parsed.dmgBonus || 0;
                        this.npcForm.shockOverride = parsed.shockOverride || false;
                    }

                    this.npcForm.abilities = [];
                    for (let i = 0; i < abilityCount; i++) {
                        this.npcForm.abilities.push({ name: 'Ability ' + (i + 1), description: '' });
                    }

                    this.parseError = '';
                } catch (e) {
                    this.parseError = 'Parse error: ' + e.message;
                }
            },

            openHpModal(combatant) {
                this.hpModalTarget = combatant;
                this.hpModalAmount = 0;
                this.hpModalOpen = true;
                this.$nextTick(() => {
                    this.$refs.hpInput?.focus();
                });
            },

            closeHpModal() {
                this.hpModalOpen = false;
                this.hpModalTarget = null;
            },

            // Actions
            addNPC() {
                if (!this.npcForm.name.trim()) {
                    alert('Please enter a name');
                    return;
                }

                // Edit mode: update combatant directly
                if (this.editModalCombatantId) {
                    const combatant = this.combatants.find(c => c.id === this.editModalCombatantId);
                    if (!combatant) return;

                    // Check if HD changed
                    const hdChanged = combatant.hd !== this.npcForm.hd;

                    // Update combatant stats directly
                    combatant.name = this.npcForm.name.trim();
                    combatant.group = this.npcForm.group.trim() || combatant.group;
                    combatant.hd = this.npcForm.hd;
                    combatant.ac = this.npcForm.ac;
                    combatant.hasArmor = this.npcForm.hasArmor;
                    combatant.hasShield = this.npcForm.hasShield;
                    combatant.bab = this.npcForm.bab;
                    combatant.attacks = this.npcForm.attacks;
                    combatant.damageMode = this.npcForm.damageMode;
                    combatant.weaponId = this.npcForm.weaponId;
                    combatant.diceCount = this.npcForm.diceCount;
                    combatant.diceType = this.npcForm.diceType;
                    combatant.attackName = this.npcForm.attackName;
                    combatant.dmgBonus = this.npcForm.dmgBonus;
                    combatant.shockValue = this.npcForm.shockValue;
                    combatant.shockAC = this.npcForm.shockAC;
                    combatant.shockOverride = this.npcForm.shockOverride;
                    combatant.mv = this.npcForm.mv;
                    combatant.hasFly = this.npcForm.hasFly;
                    combatant.hasSwim = this.npcForm.hasSwim;
                    combatant.ml = this.npcForm.ml;
                    combatant.inst = this.npcForm.inst;
                    combatant.skl = this.npcForm.skl;
                    combatant.sv = this.npcForm.sv;
                    combatant.abilities = [...this.npcForm.abilities];

                    // If HD changed, recalculate HP and heal to full
                    if (hdChanged) {
                        let newMaxHp;
                        if (this.npcForm.hpMode === 'average') {
                            newMaxHp = Math.round(this.npcForm.hd * 4.5);
                        } else {
                            newMaxHp = this.rollDice(this.npcForm.hd + 'd8') || this.npcForm.hd;
                        }
                        combatant.maxHp = newMaxHp;
                        combatant.currentHp = newMaxHp;
                    }

                    this.saveToStorage();
                    this.closeAddModal();
                    return;
                }

                // Add mode: create combatants with embedded stats
                const groupName = this.npcForm.group.trim() || this.npcForm.name.trim() + 's';
                const baseName = this.npcForm.name.trim();
                const count = Math.max(1, Math.min(20, this.npcForm.count || 1));

                // Find highest existing number for this base name
                // Matches "Zombie", "Zombie 1", "Zombie 2", etc.
                let highestNum = 0;
                const namePattern = new RegExp('^' + baseName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?: (\\d+))?$');
                this.combatants.forEach(c => {
                    if (c.type === 'npc') {
                        const match = c.name?.match(namePattern);
                        if (match) {
                            const num = match[1] ? parseInt(match[1]) : 1;
                            if (num > highestNum) highestNum = num;
                        }
                    }
                });

                // Create multiple combatants based on count
                for (let i = 0; i < count; i++) {
                    // Roll HP individually for each monster
                    let maxHp;
                    if (this.npcForm.hpMode === 'average') {
                        maxHp = Math.round(this.npcForm.hd * 4.5);
                    } else {
                        maxHp = this.rollDice(this.npcForm.hd + 'd8') || this.npcForm.hd;
                    }

                    // Generate name with number
                    const num = highestNum + i + 1;
                    const fullName = baseName + ' ' + num;

                    const combatant = {
                        id: this.generateId(),
                        type: 'npc',
                        name: fullName,
                        group: groupName,
                        initiative: null,
                        currentHp: maxHp,
                        maxHp: maxHp,
                        // Embedded stats
                        hd: this.npcForm.hd,
                        ac: this.npcForm.ac,
                        hasArmor: this.npcForm.hasArmor,
                        hasShield: this.npcForm.hasShield,
                        bab: this.npcForm.bab,
                        attacks: this.npcForm.attacks,
                        damageMode: this.npcForm.damageMode,
                        weaponId: this.npcForm.weaponId,
                        diceCount: this.npcForm.diceCount,
                        diceType: this.npcForm.diceType,
                        attackName: this.npcForm.attackName,
                        dmgBonus: this.npcForm.dmgBonus,
                        shockValue: this.npcForm.shockValue,
                        shockAC: this.npcForm.shockAC,
                        shockOverride: this.npcForm.shockOverride,
                        mv: this.npcForm.mv,
                        hasFly: this.npcForm.hasFly,
                        hasSwim: this.npcForm.hasSwim,
                        ml: this.npcForm.ml,
                        inst: this.npcForm.inst,
                        skl: this.npcForm.skl,
                        sv: this.npcForm.sv,
                        abilities: [...this.npcForm.abilities],
                        conditions: [],
                        notes: ''
                    };
                    this.combatants.push(combatant);
                }

                this.saveToStorage();
                this.closeAddModal();
            },

            addPC() {
                if (!this.pcForm.name.trim()) {
                    alert('Please enter a name');
                    return;
                }

                // Edit mode: update existing PC and combatant
                if (this.editModalCombatantId) {
                    const combatant = this.combatants.find(c => c.id === this.editModalCombatantId);
                    if (!combatant) return;

                    const pc = this.getPC(combatant.sourceId);
                    if (!pc) return;

                    // Update PC
                    pc.name = this.pcForm.name.trim();
                    pc.group = this.pcForm.group.trim() || pc.group;
                    pc.level = this.pcForm.level;
                    pc.ac = this.pcForm.ac;
                    pc.maxHp = this.pcForm.maxHp;

                    // Update combatant
                    combatant.maxHp = this.pcForm.maxHp;
                    combatant.systemStrain = this.pcForm.systemStrain;
                    // Clamp current HP to new max if needed
                    if (combatant.currentHp > combatant.maxHp) {
                        combatant.currentHp = combatant.maxHp;
                    }

                    this.saveToStorage();
                    this.closeAddModal();
                    return;
                }

                // Add mode: create new PC and combatant
                const pcId = this.generateId();
                const groupName = this.pcForm.group.trim() || 'Group 1';
                const pc = {
                    id: pcId,
                    type: 'pc',
                    name: this.pcForm.name.trim(),
                    group: groupName,
                    level: this.pcForm.level,
                    ac: this.pcForm.ac,
                    maxHp: this.pcForm.maxHp,
                    systemStrain: this.pcForm.systemStrain
                };
                this.pcs.push(pc);

                const combatant = {
                    id: this.generateId(),
                    type: 'pc',
                    sourceId: pcId,
                    initiative: null,
                    currentHp: this.pcForm.maxHp,
                    maxHp: this.pcForm.maxHp,
                    systemStrain: this.pcForm.systemStrain,
                    conditions: [],
                    notes: ''
                };
                this.combatants.push(combatant);

                // Reset name but keep group for adding more to same group
                this.pcForm.name = 'Adventurer';
                this.saveToStorage();
                this.closeAddModal();
            },

            removeCombatant(id) {
                const idx = this.combatants.findIndex(c => c.id === id);
                if (idx !== -1) {
                    this.combatants.splice(idx, 1);
                    if (this.currentTurnId === id) {
                        this.currentTurnId = null;
                    }
                    this.saveToStorage();
                }
            },

            updateInitiative(id, value) {
                const combatant = this.combatants.find(c => c.id === id);
                if (combatant) {
                    combatant.initiative = value === '' ? null : parseInt(value);
                    this.saveToStorage();
                }
            },

            rollAllInitiative() {
                // Roll initiative for all groups
                this.allGroups.forEach(group => {
                    this.groupInitiatives[group.name] = this.rollDice('1d8') || 1;
                });
                // Roll for individual combatants
                this.combatants.forEach(c => {
                    if (this.isIndividual(c)) {
                        c.initiative = this.rollDice('1d8') || 1;
                    }
                });
                this.saveToStorage();
            },

            startCombat() {
                const sorted = this.getTurnOrder();
                if (sorted.length === 0) return;
                this.currentTurnId = sorted[0].id;
                this.saveToStorage();
            },

            endCombat() {
                this.currentTurnId = null;
                this.round = 1;
                this.saveToStorage();
            },

            prevTurn() {
                const sorted = this.getTurnOrder();
                if (sorted.length === 0 || !this.currentTurnId) return;

                const currentIdx = sorted.findIndex(c => c.id === this.currentTurnId);
                if (currentIdx === 0) {
                    // Go to last combatant of previous round
                    if (this.round > 1) {
                        this.round--;
                        this.flashRoundCounter();
                        this.currentTurnId = sorted[sorted.length - 1].id;
                    }
                } else {
                    this.currentTurnId = sorted[currentIdx - 1].id;
                }
                this.saveToStorage();
            },

            nextTurn() {
                const sorted = this.getTurnOrder();
                if (sorted.length === 0 || !this.currentTurnId) return;

                const currentIdx = sorted.findIndex(c => c.id === this.currentTurnId);
                const nextIdx = (currentIdx + 1) % sorted.length;
                if (nextIdx === 0) {
                    this.round++;
                    this.flashRoundCounter();
                }
                this.currentTurnId = sorted[nextIdx].id;
                this.saveToStorage();
            },

            flashRoundCounter() {
                this.roundFlash = false;
                // Force reflow to restart animation
                this.$nextTick(() => {
                    this.roundFlash = true;
                    setTimeout(() => { this.roundFlash = false; }, 800);
                });
            },

            getTurnOrder() {
                // Derive turn order from visual order (sortedGroups) to ensure consistency
                // This flattens groups so turn order matches top-to-bottom display
                const order = [];
                this.sortedGroups.forEach(item => {
                    item.combatants.forEach(c => order.push(c));
                });
                return order;
            },

            getEffectiveInitiative(combatant) {
                // Individual combatants use their own initiative
                if (this.isIndividual(combatant)) {
                    return combatant.initiative;
                }
                // Grouped combatants use group initiative
                const groupName = this.getCombatantGroup(combatant);
                return this.groupInitiatives[groupName] ?? null;
            },

            isIndividual(combatant) {
                const groupName = this.getCombatantGroup(combatant);
                return groupName === '_individual';
            },

            getCombatantGroup(combatant) {
                if (combatant.type === 'npc') {
                    return combatant.group || 'Group 1';
                } else {
                    const pc = this.getPC(combatant.sourceId);
                    return pc?.group || 'Group 1';
                }
            },

            clearCombat() {
                if (confirm('Clear all combatants?')) {
                    this.combatants = [];
                    this.pcs = [];
                    this.round = 1;
                    this.currentTurnId = null;
                    this.groupInitiatives = {};
                    this.nextGroupNum = 1;
                    this.saveToStorage();
                }
            },

            applyDamage() {
                if (this.hpModalTarget && this.hpModalAmount > 0) {
                    this.hpModalTarget.currentHp = Math.max(0, this.hpModalTarget.currentHp - this.hpModalAmount);
                    this.saveToStorage();
                }
                this.closeHpModal();
            },

            applyHealing() {
                if (this.hpModalTarget && this.hpModalAmount > 0) {
                    this.hpModalTarget.currentHp = Math.min(this.hpModalTarget.maxHp, this.hpModalTarget.currentHp + this.hpModalAmount);
                    this.saveToStorage();
                }
                this.closeHpModal();
            },

            // Persistence
            collectState() {
                return {
                    round: this.round,
                    currentTurnId: this.currentTurnId,
                    combatants: this.combatants,
                    pcs: this.pcs,
                    groupInitiatives: this.groupInitiatives,
                    nextGroupNum: this.nextGroupNum
                };
            },

            applyState(data) {
                this.round = data.round || 1;
                this.currentTurnId = data.currentTurnId || null;
                this.combatants = data.combatants || [];
                this.pcs = data.pcs || [];
                this.groupInitiatives = data.groupInitiatives || {};
                this.nextGroupNum = data.nextGroupNum || 1;
            },

            saveToStorage() {
                window.CombatTracker.storage.save(this.collectState());
            },

            loadFromStorage() {
                const data = window.CombatTracker.storage.load();
                if (data) this.applyState(data);
            },

            exportJson() {
                const payload = window.CombatTracker.storage.buildPayload(this.collectState());
                const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'combat-tracker-' + new Date().toISOString().slice(0, 10) + '.json';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            },

            importJson(file) {
                if (!file) return;
                const reader = new FileReader();
                reader.onload = (e) => {
                    let payload;
                    try {
                        payload = JSON.parse(e.target.result);
                    } catch (err) {
                        alert('Import failed: file is not valid JSON.');
                        return;
                    }
                    const data = window.CombatTracker.storage.readPayload(payload);
                    if (!data) {
                        alert('Import failed: unrecognized format or version mismatch (expected version ' + window.CombatTracker.storage.VERSION + ').');
                        return;
                    }
                    this.applyState(data);
                    this.saveToStorage();
                };
                reader.onerror = () => alert('Import failed: could not read file.');
                reader.readAsText(file);
            }
        };
    }

    window.combatTracker = combatTracker;
})();
