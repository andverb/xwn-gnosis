/**
 * Rules Search - Client-side search with lunr.js
 *
 * Follows the MkDocs Material pattern:
 * 1. Fetch search_index_{lang}.json on first modal open
 * 2. Build lunr index from docs array
 * 3. Search on keyup (debounced)
 * 4. Render results with links to location
 */

(function() {
    'use strict';

    // State
    let searchIndex = null;
    let searchDocs = null;
    let searchModal = null;
    let searchInput = null;
    let resultsContainer = null;
    let selectedIndex = -1;
    let isLoading = false;

    // Get current language from HTML lang attribute
    function getLang() {
        return document.documentElement.lang || 'en';
    }

    // Section icons mapping (matching Django SECTION_META)
    const sectionIcons = {
        'basics': 'bi-star',
        'survival': 'bi-heart-pulse',
        'combat': 'bi-shield',
        'equipment': 'bi-backpack',
        'magic': 'bi-magic',
        'character': 'bi-person',
        'campaign': 'bi-map',
        'reference': 'bi-bookmark'
    };

    // Section title translations
    const sectionTitles = {
        'en': {
            'basics': 'Basics',
            'survival': 'Survival',
            'combat': 'Combat',
            'equipment': 'Equipment',
            'magic': 'Magic',
            'character': 'Character',
            'campaign': 'Campaign',
            'reference': 'Reference'
        },
        'uk': {
            'basics': 'Основи',
            'survival': 'Виживання',
            'combat': 'Бій',
            'equipment': 'Спорядження',
            'magic': 'Магія',
            'character': 'Персонаж',
            'campaign': 'Кампанія',
            'reference': 'Довідник'
        }
    };

    /**
     * Initialize search functionality
     */
    function initSearch() {
        searchModal = document.getElementById('searchModal');
        searchInput = document.getElementById('searchQuery');
        resultsContainer = document.getElementById('searchResults');

        if (!searchModal || !searchInput || !resultsContainer) {
            console.warn('Search elements not found');
            return;
        }

        // Load index when modal opens (first time only)
        searchModal.addEventListener('show.bs.modal', async function() {
            if (!searchIndex && !isLoading) {
                await loadSearchIndex();
            }
            // Focus input after modal is shown
            setTimeout(() => searchInput.focus(), 100);
        });

        // Clear and focus on modal show
        searchModal.addEventListener('shown.bs.modal', function() {
            searchInput.value = '';
            searchInput.focus();
            showEmptyState();
        });

        // Search on input (debounced)
        let debounceTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => performSearch(this.value), 150);
        });

        // Keyboard navigation
        searchInput.addEventListener('keydown', handleKeydown);

        // Global keyboard shortcut (Ctrl+K or /)
        document.addEventListener('keydown', function(e) {
            // Ctrl+K or Cmd+K
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                openSearchModal();
            }
            // / key (when not in input)
            if (e.key === '/' && !isInputFocused()) {
                e.preventDefault();
                openSearchModal();
            }
        });
    }

    /**
     * Check if an input element is focused
     */
    function isInputFocused() {
        const active = document.activeElement;
        return active && (
            active.tagName === 'INPUT' ||
            active.tagName === 'TEXTAREA' ||
            active.isContentEditable
        );
    }

    /**
     * Open the search modal
     */
    function openSearchModal() {
        if (searchModal) {
            const modal = bootstrap.Modal.getOrCreateInstance(searchModal);
            modal.show();
        }
    }

    /**
     * Load search index from JSON file
     */
    async function loadSearchIndex() {
        isLoading = true;
        showLoadingState();

        const lang = getLang();
        const indexUrl = `/static/data/search_index_${lang}.json`;

        try {
            const response = await fetch(indexUrl);
            if (!response.ok) {
                throw new Error(`Failed to load search index: ${response.status}`);
            }

            const data = await response.json();
            searchDocs = data.docs;

            // Build lunr index
            searchIndex = lunr(function() {
                // Use Russian stemmer for Ukrainian (close enough linguistically)
                if (lang === 'uk' && lunr.ru) {
                    this.use(lunr.ru);
                }

                this.ref('location');
                this.field('title', { boost: 10 });
                this.field('text');

                data.docs.forEach(doc => {
                    this.add(doc);
                });
            });

            showEmptyState();
            updateStatus(`${searchDocs.length} ${lang === 'uk' ? 'документів' : 'documents'}`);

        } catch (error) {
            console.error('Failed to load search index:', error);
            showErrorState(error.message);
        } finally {
            isLoading = false;
        }
    }

    /**
     * Perform search with current query
     */
    function performSearch(query) {
        if (!searchIndex) return;

        query = query.trim();

        if (!query) {
            showEmptyState();
            return;
        }

        // Search with wildcards for partial matching
        const searchTerms = query.split(/\s+/).map(term => {
            // Add wildcards for partial matching
            return `*${term}*`;
        }).join(' ');

        let results;
        try {
            results = searchIndex.search(searchTerms);
        } catch (e) {
            // If lunr query syntax fails, try simple search
            try {
                results = searchIndex.search(query);
            } catch (e2) {
                results = [];
            }
        }

        if (results.length === 0) {
            showNoResultsState();
            return;
        }

        // Get full doc info and render
        const matchedDocs = results.slice(0, 20).map(r => {
            const doc = searchDocs.find(d => d.location === r.ref);
            return {
                ...doc,
                score: r.score
            };
        });

        renderResults(matchedDocs, query);
    }

    /**
     * Render search results
     */
    function renderResults(docs, query) {
        hideAllStates();
        resultsContainer.innerHTML = '';
        selectedIndex = -1;

        const lang = getLang();
        const titles = sectionTitles[lang] || sectionTitles['en'];

        docs.forEach((doc, index) => {
            const [section, page] = doc.location.split('/');
            const hasAnchor = page && page.includes('#');
            const [basePage, anchor] = hasAnchor ? page.split('#') : [page, null];

            // Build URL (rules are under /wwn/rules/)
            let url = `/wwn/rules/${section}/`;
            if (basePage) {
                url += `${basePage}/`;
            }
            if (anchor) {
                url += `#${anchor}`;
            }

            // Get section info
            const sectionTitle = titles[section] || section;
            const sectionIcon = sectionIcons[section] || 'bi-folder';

            // Create snippet with highlighted terms
            let snippet = '';
            if (doc.text) {
                snippet = createSnippet(doc.text, query, 150);
            }

            const resultEl = document.createElement('a');
            resultEl.href = url;
            resultEl.className = 'search-result list-group-item list-group-item-action';
            resultEl.dataset.index = index;

            resultEl.innerHTML = `
                <div class="search-result-title">${escapeHtml(doc.title)}</div>
                <div class="search-result-section">
                    <i class="bi ${sectionIcon}"></i>
                    <span>${escapeHtml(sectionTitle)}</span>
                    ${basePage ? `<span class="text-body-tertiary">/ ${escapeHtml(basePage.replace(/-/g, ' '))}</span>` : ''}
                </div>
                ${snippet ? `<div class="search-result-snippet">${snippet}</div>` : ''}
            `;

            // Click handler
            resultEl.addEventListener('click', function(e) {
                // Close modal on navigation
                const modal = bootstrap.Modal.getInstance(searchModal);
                if (modal) modal.hide();
            });

            // Hover handler
            resultEl.addEventListener('mouseenter', function() {
                setSelectedResult(index);
            });

            resultsContainer.appendChild(resultEl);
        });

        updateStatus(`${docs.length} ${lang === 'uk' ? 'результатів' : 'results'}`);
    }

    /**
     * Create a text snippet with highlighted search terms
     */
    function createSnippet(text, query, maxLength) {
        const terms = query.toLowerCase().split(/\s+/).filter(t => t.length > 1);
        const textLower = text.toLowerCase();

        // Find first occurrence of any term
        let startPos = 0;
        for (const term of terms) {
            const pos = textLower.indexOf(term);
            if (pos !== -1) {
                startPos = Math.max(0, pos - 30);
                break;
            }
        }

        // Extract snippet
        let snippet = text.substring(startPos, startPos + maxLength);

        // Add ellipsis if needed
        if (startPos > 0) snippet = '...' + snippet;
        if (startPos + maxLength < text.length) snippet += '...';

        // Highlight terms
        for (const term of terms) {
            const regex = new RegExp(`(${escapeRegex(term)})`, 'gi');
            snippet = snippet.replace(regex, '<mark>$1</mark>');
        }

        return snippet;
    }

    /**
     * Handle keyboard navigation
     */
    function handleKeydown(e) {
        const results = resultsContainer.querySelectorAll('.search-result');
        if (results.length === 0) return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                setSelectedResult(Math.min(selectedIndex + 1, results.length - 1));
                break;

            case 'ArrowUp':
                e.preventDefault();
                setSelectedResult(Math.max(selectedIndex - 1, 0));
                break;

            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0 && results[selectedIndex]) {
                    results[selectedIndex].click();
                }
                break;
        }
    }

    /**
     * Set the selected result by index
     */
    function setSelectedResult(index) {
        const results = resultsContainer.querySelectorAll('.search-result');
        results.forEach((r, i) => {
            r.classList.toggle('active', i === index);
        });
        selectedIndex = index;

        // Scroll into view
        if (results[index]) {
            results[index].scrollIntoView({ block: 'nearest' });
        }
    }

    // UI State helpers
    function showLoadingState() {
        hideAllStates();
        document.getElementById('searchLoading')?.classList.remove('d-none');
    }

    function showEmptyState() {
        hideAllStates();
        document.getElementById('searchEmpty')?.classList.remove('d-none');
    }

    function showNoResultsState() {
        hideAllStates();
        document.getElementById('searchNoResults')?.classList.remove('d-none');
    }

    function showErrorState(message) {
        hideAllStates();
        resultsContainer.innerHTML = `
            <div class="text-center py-4 text-danger">
                <i class="bi bi-exclamation-triangle fs-1 mb-2 d-block"></i>
                ${escapeHtml(message)}
            </div>
        `;
    }

    function hideAllStates() {
        document.getElementById('searchLoading')?.classList.add('d-none');
        document.getElementById('searchEmpty')?.classList.add('d-none');
        document.getElementById('searchNoResults')?.classList.add('d-none');
        resultsContainer.innerHTML = '';
    }

    function updateStatus(text) {
        const statusEl = document.getElementById('searchStatus');
        if (statusEl) statusEl.textContent = text;
    }

    // Utility functions
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSearch);
    } else {
        initSearch();
    }
})();
