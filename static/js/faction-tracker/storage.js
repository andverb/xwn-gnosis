// Faction Tracker — localStorage persistence + schema validation + migrations.
(function () {
    'use strict';

    const C = window.FactionTracker.constants;

    function defaultState() {
        return {
            version: C.STATE_VERSION,
            campaignName: '',
            currentTurn: 0,
            factions: [],
            log: [],
        };
    }

    // Soft validation: returns { ok, errors[] }. We don't reject loose shapes —
    // missing optional fields are OK. We reject only on structural breakage.
    function validate(state) {
        const errors = [];
        if (!state || typeof state !== 'object') errors.push('state is not an object');
        if (state && !Array.isArray(state.factions)) errors.push('factions is not an array');
        if (state && !Array.isArray(state.log)) errors.push('log is not an array');
        if (state && state.version != null && typeof state.version !== 'number') {
            errors.push('version is not a number');
        }
        return { ok: errors.length === 0, errors };
    }

    // Migrations are keyed by FROM version. Each returns the upgraded state.
    // Add entries here as the schema evolves.
    const migrations = {
        // Example: 1: (state) => ({ ...state, version: 2, newField: [] }),
    };

    function migrate(state) {
        let s = state;
        let v = s.version || 1;
        while (v < C.STATE_VERSION && migrations[v]) {
            s = migrations[v](s);
            v = s.version || (v + 1);
        }
        s.version = C.STATE_VERSION;
        return s;
    }

    function load() {
        const raw = localStorage.getItem(C.STORAGE_KEY);
        if (!raw) return defaultState();
        try {
            const parsed = JSON.parse(raw);
            const { ok, errors } = validate(parsed);
            if (!ok) {
                console.warn('Faction Tracker: invalid stored state, falling back to default.', errors, parsed);
                return defaultState();
            }
            return migrate({ ...defaultState(), ...parsed });
        } catch (err) {
            console.error('Faction Tracker: failed to parse stored state.', err);
            return defaultState();
        }
    }

    function save(state) {
        try {
            localStorage.setItem(C.STORAGE_KEY, JSON.stringify(state));
        } catch (err) {
            console.error('Faction Tracker: failed to save state.', err);
        }
    }

    // Triggers a browser download of the campaign as JSON.
    function exportToFile(state) {
        const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = (state.campaignName || 'faction-tracker') + '.json';
        a.click();
        URL.revokeObjectURL(url);
    }

    // Reads a File object and returns a Promise<state> — caller decides what to do.
    function importFromFile(file) {
        return new Promise((resolve, reject) => {
            if (!file) return reject(new Error('No file'));
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const parsed = JSON.parse(e.target.result);
                    const { ok, errors } = validate(parsed);
                    if (!ok) return reject(new Error('Invalid campaign file: ' + errors.join('; ')));
                    resolve(migrate({ ...defaultState(), ...parsed }));
                } catch (err) {
                    reject(err);
                }
            };
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    window.FactionTracker = window.FactionTracker || {};
    window.FactionTracker.storage = {
        defaultState,
        validate,
        migrate,
        migrations,
        load,
        save,
        exportToFile,
        importFromFile,
    };
})();
