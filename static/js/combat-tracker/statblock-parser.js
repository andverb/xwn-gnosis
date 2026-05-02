// WWN statblock parser - pure module, no Alpine state.
//
// Exposes window.CombatTracker.parseStatblock(input) in browser, and
// module.exports.parseStatblock under Node (CommonJS) for tests.
//
// Three input formats are supported. parseStatblock() auto-detects:
//
//   1. SPACED    — fields separated by 2+ spaces (markdown-table-ish):
//        "Villager  1  10  +0  Wpn  Wpn  30'  7  5  +1  15+"
//
//   2. SINGLE    — fields separated by single spaces (multi-word names allowed,
//                  BAB token "+N" anchors the field positions):
//        "Lesser Anak Warrior 1 13a +1 Wpn+1 Wpn+1 20' 7 4 +1 15+"
//
//   3. COMPACT   — PDF copy-paste format, no separators between fields:
//        "Lesser Anak Warrior113a+1Wpn+1Wpn+120'74+115+"
//        "Undead Mage810+101d82/-30'94+211+"
//        "Ancient Warbot1420+15 x32d6+510/-60' fly122+28+"
//
// Field order in all three formats:
//   Name | HD | AC[a][s] | +BAB[xN] | Damage | Shock | Move | ML | Inst | +Skill | Save+
//
// parseStatblock returns one of:
//   { ok: true,  data: {...}, format: 'spaced' | 'single-space' | 'compact' }
//   { ok: false, error: { code, message, format? } }
//
// The internal parsers (parseSpacedStatblock, parseSingleSpaceStatblock,
// parseCompactStatblock) still return raw data | null and are used directly by
// tests; only the public parseStatblock wraps them in the result envelope.
(function () {
    'use strict';

    function parseDamage(dmgStr) {
        if (!dmgStr || dmgStr.toLowerCase().startsWith('wpn')) {
            const bonusMatch = dmgStr.match(/\+(\d+)/);
            return {
                damageMode: 'weapon',
                dmgBonus: bonusMatch ? parseInt(bonusMatch[1]) : 0
            };
        }
        const diceMatch = dmgStr.match(/(\d+)d(\d+)(\+(\d+))?/);
        if (diceMatch) {
            return {
                damageMode: 'dice',
                diceCount: parseInt(diceMatch[1]),
                diceType: parseInt(diceMatch[2]),
                dmgBonus: diceMatch[4] ? parseInt(diceMatch[4]) : 0
            };
        }
        return { damageMode: 'weapon', dmgBonus: 0 };
    }

    function parseShock(shockStr) {
        if (!shockStr || shockStr === '-' || shockStr.toLowerCase() === 'none') {
            return { shockValue: 0, shockAC: '-' };
        }
        if (shockStr.toLowerCase().startsWith('wpn')) {
            const override = shockStr.includes('/-');
            return { shockOverride: override };
        }
        const match = shockStr.match(/(\d+)\/(-|\d+)/);
        if (match) {
            return {
                shockValue: parseInt(match[1]),
                shockAC: match[2]
            };
        }
        return { shockValue: 0, shockAC: '-' };
    }

    function parseSpacedStatblock(input) {
        // Format: Name  HD  AC  +BAB  DMG  SHOCK  MV  ML  INST  +SKL  SV
        // Split on 2+ spaces
        const parts = input.split(/\s{2,}/).map(p => p.trim()).filter(p => p);
        if (parts.length < 10) return null;

        const name = parts[0].replace(/[\*¶]/g, '').trim();
        const hdMatch = parts[1].match(/(\d+)/);
        const hd = hdMatch ? parseInt(hdMatch[1]) : 1;

        // AC - may have 'a' or 's' suffix
        const acMatch = parts[2].match(/(\d+)(a?)(s?)/);
        const ac = acMatch ? parseInt(acMatch[1]) : 10;
        const hasArmor = acMatch ? acMatch[2] === 'a' : false;
        const hasShield = acMatch ? acMatch[3] === 's' : false;

        // BAB - format: +N or +N xM
        const babMatch = parts[3].match(/\+(\d+)(?:\s*x(\d+))?/);
        const bab = babMatch ? parseInt(babMatch[1]) : 0;
        const attacks = babMatch && babMatch[2] ? parseInt(babMatch[2]) : 1;

        const dmgParsed = parseDamage(parts[4]);
        const shockParsed = parseShock(parts[5]);

        const mv = parts[6] || "30'";

        const ml = parseInt(parts[7]) || 7;
        const inst = parseInt(parts[8]) || 5;
        const sklMatch = parts[9].match(/\+?(\d+)/);
        const skl = sklMatch ? parseInt(sklMatch[1]) : 1;
        const svMatch = parts[10].match(/(\d+)/);
        const sv = svMatch ? parseInt(svMatch[1]) : 15;

        return {
            name, hd, ac, hasArmor, hasShield, bab, attacks,
            ...dmgParsed, ...shockParsed,
            mv, ml, inst, skl, sv
        };
    }

    function parseSingleSpaceStatblock(input) {
        // Format: Name HD AC +BAB DMG SHOCK MV ML INST +SKL SV
        // Name can contain spaces; all other fields are single space-separated tokens.
        // Identify BAB by finding first token matching +digit (starting from index 2).
        const tokens = input.split(/\s+/).map(t => t.trim()).filter(t => t);

        let babIdx = -1;
        for (let i = 2; i < tokens.length - 5; i++) {
            if (/^\+\d/.test(tokens[i])) { babIdx = i; break; }
        }
        if (babIdx < 2) return null;

        const name = tokens.slice(0, babIdx - 2).join(' ').replace(/[\*¶]/g, '').trim();

        const hdMatch = tokens[babIdx - 2].match(/(\d+)/);
        const hd = hdMatch ? parseInt(hdMatch[1]) : 1;

        const acMatch = tokens[babIdx - 1].match(/(\d+)(a?)(s?)/);
        const ac = acMatch ? parseInt(acMatch[1]) : 10;
        const hasArmor = acMatch ? acMatch[2] === 'a' : false;
        const hasShield = acMatch ? acMatch[3] === 's' : false;

        const babMatch = tokens[babIdx].match(/\+(\d+)(?:x(\d+))?/);
        const bab = babMatch ? parseInt(babMatch[1]) : 0;
        const attacks = babMatch && babMatch[2] ? parseInt(babMatch[2]) : 1;

        const rest = tokens.slice(babIdx + 1);
        if (rest.length < 6) return null;

        const dmgParsed = parseDamage(rest[0]);
        const shockParsed = parseShock(rest[1]);
        const mv = rest[2] || "30'";
        const ml = parseInt(rest[3]) || 7;
        const inst = parseInt(rest[4]) || 5;
        const sklMatch = rest[5] ? rest[5].match(/\+?(\d+)/) : null;
        const skl = sklMatch ? parseInt(sklMatch[1]) : 1;
        const svMatch = rest[6] ? rest[6].match(/(\d+)/) : null;
        const sv = svMatch ? parseInt(svMatch[1]) : 15;

        return { name, hd, ac, hasArmor, hasShield, bab, attacks, ...dmgParsed, ...shockParsed, mv, ml, inst, skl, sv };
    }

    function parseCompactStatblockAlt(input) {
        // Parsing with game constraints:
        // AC: 10-20, ML: 2-12, Inst: 1-10, Skill: +0 to +5, Save: 2-15
        let rest = input;
        let result = {};

        // Extract name: everything before HD+AC pattern
        // HD is 1-2 digits, AC is always 10+ (2 digits)
        const nameMatch = rest.match(/^(.+?)(\d{1,2})(1[0-9]|20)/);
        if (!nameMatch) { return null; }
        result.name = nameMatch[1].trim();
        result.hd = parseInt(nameMatch[2]);
        rest = rest.substring(nameMatch[1].length + nameMatch[2].length);
        // AC (10-20 + optional a/s)
        const acMatch = rest.match(/^(1[0-9]|20)(a?)(s?)/);
        if (!acMatch) { return null; }
        result.ac = parseInt(acMatch[1]);
        result.hasArmor = acMatch[2] === 'a';
        result.hasShield = acMatch[3] === 's';
        rest = rest.substring(acMatch[0].length);
        // BAB (+1 to +20, optional xN where N is 2-9) - look ahead for Wpn or dice pattern
        // Pattern: +digits followed by optional xN (single digit), then Wpn or NdN
        const babMatch = rest.match(/^(\+\d{1,2})(x([2-9]))?(Wpn|\d+d)/i);
        if (!babMatch) { return null; }
        result.bab = parseInt(babMatch[1].replace('+', ''));
        result.attacks = babMatch[3] ? parseInt(babMatch[3]) : 1;
        // Only consume the BAB part and xN, not the damage lookahead
        rest = rest.substring(babMatch[1].length + (babMatch[2] ? babMatch[2].length : 0));
        // Damage (Wpn+N or dice notation NdX+N where X is valid dice: 2,4,6,8,10,12,20, bonus max +9)
        const dmgMatch = rest.match(/^(Wpn(?:\+[0-9])?|\d+d(20|12|10|8|6|4|2)(?:\+[0-9])?)/i);
        if (dmgMatch) {
            Object.assign(result, parseDamage(dmgMatch[1]));
            rest = rest.substring(dmgMatch[0].length);
        }

        // Capture attack name (words like "swoop", "thorn whip" between damage and shock)
        // Match spaces and letters but stop before None, Wpn, or digits
        const attackNameMatch = rest.match(/^[\s]*([a-z\s]+?)(?=None|Wpn|\d)/i);
        if (attackNameMatch) {
            result.attackName = attackNameMatch[1].trim();
            rest = rest.substring(attackNameMatch[0].length);
        }

        // Shock + Move combined (they often run together like "2/1530'" = shock 2/15, move 30')
        // Shock value: 1-10, Shock AC: 10-20 or -
        // Move: digits followed by quote(s) (fly/swim already removed at top level)
        const shockMoveMatch = rest.match(/^(10|[1-9])\/(1[0-9]|20|-)(\d+)['′''`]*/);
        if (shockMoveMatch) {
            result.shockValue = parseInt(shockMoveMatch[1]);
            result.shockAC = shockMoveMatch[2];
            result.mv = shockMoveMatch[3] + "'";
            rest = rest.substring(shockMoveMatch[0].length);
        } else {
            // Try None, Wpn shock (with optional /-), or -
            const altShockMatch = rest.match(/^(None|Wpn(?:\+\d)?(?:\/-)?|-)/i);
            if (altShockMatch) {
                result.shockValue = 0;
                result.shockAC = '-';
                if (altShockMatch[1].toLowerCase().startsWith('wpn')) {
                    result.shockOverride = altShockMatch[1].includes('/-');
                }
                rest = rest.substring(altShockMatch[0].length);
            }
            // Move (digits + ' or "None")
            const mvMatch = rest.match(/^(None|\d+)['′''`]*/i);
            if (mvMatch) {
                result.mv = mvMatch[1].toLowerCase() === 'none' ? "0'" : mvMatch[1] + "'";
                rest = rest.substring(mvMatch[0].length);
            } else {
                result.mv = "30'";
            }
        }

        // Remaining: ML (2-12) + Inst (1-10) + Skill (+0-5) + Save (2-15)+
        // Parse from END first since Skill and Save have clear patterns
        // e.g., "122+28+" = ML 12, Inst 2, Skill +2, Save 8+

        // Strip any leading non-digit characters (stray quotes, spaces, etc.)
        rest = rest.replace(/^[^0-9]+/, '');
        // Save (2-15+) - from end, pattern: digits followed by +
        let svMatch = rest.match(/(1[0-5]|[2-9])\+$/);
        if (svMatch) {
            result.sv = parseInt(svMatch[1]);
            rest = rest.substring(0, rest.length - svMatch[0].length);
        } else {
            result.sv = 15;
        }

        // Skill (+0 to +5) - from end, pattern: + followed by digit
        const sklMatch = rest.match(/\+([0-5])$/);
        if (sklMatch) {
            result.skl = parseInt(sklMatch[1]);
            rest = rest.substring(0, rest.length - sklMatch[0].length);
        } else {
            result.skl = 1;
        }

        // Now rest should be ML + Inst (e.g., "122" = ML 12, Inst 2)
        // ML: 2-12, Inst: 1-10
        // Try ML 2-digit (10, 11, 12) first
        let mlMatch = rest.match(/^(1[0-2])/);
        if (mlMatch) {
            result.ml = parseInt(mlMatch[1]);
            rest = rest.substring(mlMatch[0].length);
        } else {
            mlMatch = rest.match(/^([2-9])/);
            if (mlMatch) {
                result.ml = parseInt(mlMatch[1]);
                rest = rest.substring(mlMatch[0].length);
            } else {
                result.ml = 7;
            }
        }

        // Inst: remaining digits (1-10)
        let instMatch = rest.match(/^(10|[1-9])/);
        if (instMatch) {
            result.inst = parseInt(instMatch[1]);
        } else {
            result.inst = 5;
        }
        return result;
    }

    function parseCompactStatblock(input) {
        // PDF format: NameHDACAtk.Dmg.ShockMoveMLInst.SkillSave
        // Example: Lesser Anak Warrior113a+1Wpn+1Wpn+120'74+115+
        // Example: Undead Mage810+101d82/-30'94+211+
        // Example: Ancient Warbot1420+15 x32d6+510/-60' fly122+28+

        // Check for fly/swim before cleaning
        const hasFly = /fly/i.test(input);
        const hasSwim = /swim/i.test(input);
        // Clean input - remove header row if present, normalize
        let cleanInput = input
            .replace(/HDACAtk\.?Dmg\.?Shock\.?Move\.?ML\.?Inst\.?Skill\.?Save\.?/gi, '')
            .replace(/\s*[\*¶]+\s*/g, '')  // Remove ability markers and surrounding spaces
            .replace(/\s*x\s*/g, 'x')  // Normalize "x2" attack notation (remove spaces)
            .replace(/\/\s*AC\s*/gi, '/')  // Normalize shock "2/AC 15" to "2/15"
            .replace(/[''′`]/g, "'")  // Normalize all quote-like chars to straight quote
            .replace(/'\s*(fly|swim)\s*/gi, "'")  // Remove fly/swim after move quote
            .replace(/\s*(fly|swim)\s*/gi, '')  // Remove fly/swim text
            .trim();
        // Use the step-by-step parser which handles constraints better
        const result = parseCompactStatblockAlt(cleanInput);
        if (result) {
            result.hasFly = hasFly;
            result.hasSwim = hasSwim;
        }
        return result;
    }

    function parseStatblock(input) {
        const trimmed = (input || '').trim();
        if (!trimmed) {
            return { ok: false, error: { code: 'empty', message: 'Statblock is empty.' } };
        }

        const hasDoubleSpaces = /\s{2,}/.test(trimmed);
        const hasPilcrow = trimmed.includes('¶');
        // Single-space format: no double-spaces, no pilcrow, but has " +digit" (BAB token)
        const isSingleSpaceFormat = !hasPilcrow && !hasDoubleSpaces && /\s\+\d/.test(trimmed);
        const hasCompactFormat = hasPilcrow || (!isSingleSpaceFormat && !hasDoubleSpaces);

        let format, data;
        if (isSingleSpaceFormat) {
            format = 'single-space';
            data = parseSingleSpaceStatblock(trimmed);
        } else if (hasCompactFormat) {
            format = 'compact';
            data = parseCompactStatblock(trimmed);
        } else {
            format = 'spaced';
            data = parseSpacedStatblock(trimmed);
        }

        if (!data) {
            return {
                ok: false,
                error: {
                    code: 'parse_failed',
                    format,
                    message: 'Could not parse as ' + format + ' format. Expected fields: Name HD AC +BAB Damage Shock Move ML Inst +Skill Save+'
                }
            };
        }
        return { ok: true, data, format };
    }

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = {
            parseStatblock,
            parseDamage,
            parseShock,
            parseSpacedStatblock,
            parseSingleSpaceStatblock,
            parseCompactStatblock
        };
    }
    if (typeof window !== 'undefined') {
        window.CombatTracker = window.CombatTracker || {};
        window.CombatTracker.parseStatblock = parseStatblock;
    }
})();
