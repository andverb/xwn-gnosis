// Faction Tracker — shared constants/enums.
// Plain IIFE attaches to window.FactionTracker.constants.
(function () {
    'use strict';

    const ACTION = Object.freeze({
        ATTACK: 'attack',
        MOVE: 'move',
        REPAIR: 'repair',
        EXPAND: 'expand',
        CREATE: 'create',
        HIDE: 'hide',
        SELL: 'sell',
        NONE: 'none',
    });

    const QUALITY = Object.freeze({
        SUBTLE: 'subtle',
        STEALTH: 'stealth',
        ACTION: 'action',
        SPECIAL: 'special',
    });

    const ENTRY = Object.freeze({
        AUTO: 'auto',
        ACTION: 'action',
        ABILITY: 'ability',
        XP: 'xp',
        GOAL: 'goal',
        MANUAL: 'manual',
    });

    const MAGIC = Object.freeze({
        NONE: 'none',
        LOW: 'low',
        MEDIUM: 'medium',
        HIGH: 'high',
    });

    const MAGIC_ORDER = ['none', 'low', 'medium', 'high'];

    const ASSET_TYPE = Object.freeze({
        CUNNING: 'cunning',
        FORCE: 'force',
        WEALTH: 'wealth',
        SPECIAL: 'special',
    });

    const TURN_PHASE = Object.freeze({
        INITIATIVE: 'initiative',
        FACTION: 'faction',
    });

    const STORAGE_KEY = 'factionTrackerState';
    const STATE_VERSION = 1;
    const MAX_FACTIONS = 6;
    const FACTION_COLORS = 6;

    const QUALITY_DESCRIPTIONS = Object.freeze({
        Subtle: 'Can move to locations normally prohibited by ruling powers. Must be Attacked to dislodge or moved out by owner.',
        Action: 'Has a free action special ability that can be triggered each turn.',
        Stealthed: 'Moves freely to any location within reach. Cannot be Attacked until Stealth is lost (by being discovered or by Attacking).',
    });

    window.FactionTracker = window.FactionTracker || {};
    window.FactionTracker.constants = {
        ACTION,
        QUALITY,
        ENTRY,
        MAGIC,
        MAGIC_ORDER,
        ASSET_TYPE,
        TURN_PHASE,
        STORAGE_KEY,
        STATE_VERSION,
        MAX_FACTIONS,
        FACTION_COLORS,
        QUALITY_DESCRIPTIONS,
    };
})();
