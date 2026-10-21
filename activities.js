// Filtering and sorting for the Things to Do page (/gudauri). Without JavaScript the page is
// simply a list of places in distance order, so the controls stay hidden until this runs.
(function () {
    'use strict';

    const controls = document.getElementById('act_controls');
    const grid = document.getElementById('act_grid');
    if (!controls || !grid) return;

    const cards = Array.from(grid.querySelectorAll('.act_card'));
    const countEl = document.getElementById('act_count');
    const emptyEl = document.getElementById('act_empty');
    const sortEl = document.getElementById('act_sort');
    const resetEl = document.getElementById('act_reset');
    const chips = Array.from(controls.querySelectorAll('.act_chip'));
    const total = Number(controls.dataset.total) || cards.length;
    const countTemplate = controls.dataset.count || '{n} / {t}';
    const lang = document.documentElement.lang || 'en';

    const state = { season: 'all', hike: 'all', cost: 'all' };

    function matches(card) {
        const d = card.dataset;
        if (state.season !== 'all' && d.season.split(' ').indexOf(state.season) === -1) return false;
        if (state.hike !== 'all' && d.hike !== state.hike) return false;
        // places with free entry but paid extras count as both Free and Paid
        if (state.cost === 'free' && d.cost !== 'free' && d.cost !== 'mixed') return false;
        if (state.cost === 'paid' && d.cost !== 'paid' && d.cost !== 'mixed') return false;
        return true;
    }

    function compare(a, b) {
        const km = (x) => parseFloat(x.dataset.km);
        const order = (x) => Number(x.dataset.order);
        const by = sortEl.value;
        if (by === 'name') return a.dataset.name.localeCompare(b.dataset.name, lang) || order(a) - order(b);
        if (by === 'hike') return (Number(a.dataset.hike) - Number(b.dataset.hike)) || (km(a) - km(b)) || (order(a) - order(b));
        return (km(a) - km(b)) || (order(a) - order(b));
    }

    function render() {
        let shown = 0;
        cards.slice().sort(compare).forEach((card) => {
            const ok = matches(card);
            card.hidden = !ok;
            if (ok) shown += 1;
            grid.appendChild(card); // re-append in the new order
        });
        countEl.textContent = countTemplate.replace('{n}', shown).replace('{t}', total);
        emptyEl.hidden = shown !== 0;
    }

    function setChip(filter, value) {
        state[filter] = value;
        chips.forEach((chip) => {
            if (chip.dataset.filter === filter) {
                chip.setAttribute('aria-pressed', chip.dataset.value === value ? 'true' : 'false');
            }
        });
    }

    chips.forEach((chip) => {
        chip.addEventListener('click', () => {
            setChip(chip.dataset.filter, chip.dataset.value);
            render();
        });
    });

    sortEl.addEventListener('change', render);

    resetEl.addEventListener('click', () => {
        ['season', 'hike', 'cost'].forEach((f) => setChip(f, 'all'));
        sortEl.value = 'near';
        render();
    });

    controls.hidden = false;
    render();
})();
