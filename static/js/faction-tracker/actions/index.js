// Faction Tracker — registry of available faction actions.
// Each descriptor only carries metadata + an availability predicate. The
// per-action sub-flow logic still lives in the component's executeX methods
// (Phase 2 partial); flattening those onto descriptors is deferred.
//
// Descriptor shape:
//   {
//       id: ACTION.<X>,
//       label: string,            // Picker button label
//       icon: string,             // Bootstrap-icon class name (without the `bi` prefix)
//       variant: string,          // Bootstrap btn-outline-<variant>
//       available(faction, R)?    // optional: returns true if action is allowed
//   }
(function () {
    'use strict';

    const C = window.FactionTracker.constants;
    const R = window.FactionTracker.rules;

    // Order is significant — drives the picker layout.
    const ACTIONS = [
        { id: C.ACTION.ATTACK, label: 'Attack',     icon: 'lightning',    variant: 'danger' },
        { id: C.ACTION.MOVE,   label: 'Move',       icon: 'arrows-move',  variant: 'primary' },
        { id: C.ACTION.REPAIR, label: 'Repair',     icon: 'wrench',       variant: 'success' },
        { id: C.ACTION.EXPAND, label: 'Expand',     icon: 'geo-alt',      variant: 'warning' },
        { id: C.ACTION.CREATE, label: 'Create',     icon: 'plus-circle',  variant: 'info' },
        { id: C.ACTION.HIDE,   label: 'Hide',       icon: 'eye-slash',    variant: 'secondary' },
        { id: C.ACTION.SELL,   label: 'Sell',       icon: 'cash-coin',    variant: 'secondary' },
        { id: C.ACTION.NONE,   label: 'No Action',  icon: 'dash-circle',  variant: 'secondary' },
    ];

    // Hook for future per-faction filtering. Currently always available (matches
    // existing UI exactly). Callers can read `.available(faction)` if a
    // descriptor adds the predicate later.
    function isAvailable(descriptor, faction) {
        if (typeof descriptor.available !== 'function') return true;
        try {
            return !!descriptor.available(faction);
        } catch {
            return true; // Fail open — never hide an action on predicate error.
        }
    }

    window.FactionTracker = window.FactionTracker || {};
    window.FactionTracker.actions = {
        list: ACTIONS,
        isAvailable,
    };
})();
