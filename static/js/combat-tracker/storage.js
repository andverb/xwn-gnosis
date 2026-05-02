window.CombatTracker = window.CombatTracker || {};

window.CombatTracker.storage = (function() {
    const KEY = 'wwn-combat-tracker';
    const VERSION = 1;
    const DEBOUNCE_MS = 250;

    let saveTimer = null;

    function save(state) {
        if (saveTimer) clearTimeout(saveTimer);
        saveTimer = setTimeout(() => {
            saveTimer = null;
            try {
                const payload = {
                    version: VERSION,
                    savedAt: new Date().toISOString(),
                    state: state
                };
                localStorage.setItem(KEY, JSON.stringify(payload));
            } catch (e) {
                console.error('Failed to save combat tracker state:', e);
            }
        }, DEBOUNCE_MS);
    }

    function load() {
        let raw;
        try {
            raw = localStorage.getItem(KEY);
        } catch (e) {
            console.error('Failed to read combat tracker state:', e);
            return null;
        }
        if (!raw) return null;
        let payload;
        try {
            payload = JSON.parse(raw);
        } catch (e) {
            console.error('Corrupt combat tracker state in localStorage; ignoring:', e);
            return null;
        }
        if (!payload || typeof payload !== 'object') return null;
        // Versioned format
        if (payload.version === VERSION && payload.state) return payload.state;
        // Legacy flat format (pre-versioning)
        if ('round' in payload || 'combatants' in payload) return payload;
        return null;
    }

    function buildPayload(state) {
        return {
            version: VERSION,
            savedAt: new Date().toISOString(),
            state: state
        };
    }

    function readPayload(payload) {
        if (!payload || typeof payload !== 'object') return null;
        if (payload.version === VERSION && payload.state) return payload.state;
        if ('round' in payload || 'combatants' in payload) return payload;
        return null;
    }

    return { save, load, buildPayload, readPayload, VERSION };
})();
