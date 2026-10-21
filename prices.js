// Winter 2026/27 room rates (USD per room per night, VAT and breakfast included)
// from "Monte Hotel Gudauri - Rates & Reservation Terms". Update here for a new season.
(function (root) {
    // Percentage added on top of the rate sheet prices.
    const MARKUP_PERCENT = 15;
    // Nights before this date are priced exactly as in the rate sheet, with no markup.
    const MARKUP_FROM = '2026-12-20';

    // Each night is priced by the season its date falls in (both ends inclusive).
    const SEASONS = [
        { from: '2026-12-04', to: '2026-12-23' },
        { from: '2026-12-24', to: '2027-01-10' },
        { from: '2027-01-11', to: '2027-01-27' },
        { from: '2027-01-28', to: '2027-03-12' },
        { from: '2027-03-13', to: '2027-03-27' },
        { from: '2027-03-28', to: '2027-04-10' },
    ];

    // Base prices per season, in the same order as SEASONS.
    const RATES = {
        standard_double: [130, 190, 130, 160, 120, 110],
        large_double: [150, 210, 140, 175, 140, 120],
        superior_double: [165, 224, 154, 194, 154, 138],
        deluxe_double: [182, 242, 171, 211, 171, 154],
        suite_double: [193, 261, 182, 224, 182, 165],
        triple: [190, 260, 180, 220, 180, 165],
        standard_family: [275, 332, 264, 321, 264, 248],
        superior_family: [325, 393, 314, 375, 314, 297],
    };

    function seasonIndex(iso) {
        // ISO dates compare correctly as strings.
        return SEASONS.findIndex((s) => iso >= s.from && iso <= s.to);
    }

    // Integer math so .5 always rounds up (190 -> 219) with no float drift.
    function withMarkup(base) {
        return Math.round((base * (100 + MARKUP_PERCENT)) / 100);
    }

    // Price for the night starting on `iso`, or null when there is no rate for it.
    function nightPrice(room, iso) {
        const rates = RATES[room];
        const i = seasonIndex(iso);
        if (!rates || i === -1) return null;
        return iso < MARKUP_FROM ? rates[i] : withMarkup(rates[i]);
    }

    function addDays(iso, n) {
        const d = new Date(iso + 'T00:00:00Z');
        d.setUTCDate(d.getUTCDate() + n);
        return d.toISOString().slice(0, 10);
    }

    // Total for nights checkin .. checkout-1, or null if any night has no rate.
    function stayTotal(room, checkin, checkout) {
        if (!RATES[room] || !checkin || !checkout || checkout <= checkin) return null;
        let total = 0;
        let nights = 0;
        for (let d = checkin; d < checkout; d = addDays(d, 1)) {
            const p = nightPrice(room, d);
            if (p === null) return null;
            total += p;
            nights += 1;
        }
        return { total, nights };
    }

    // Cheapest nightly price across all rooms for a date (used before a room is chosen).
    function fromPrice(iso) {
        const prices = Object.keys(RATES)
            .map((room) => nightPrice(room, iso))
            .filter((p) => p !== null);
        return prices.length ? Math.min.apply(null, prices) : null;
    }

    const api = { MARKUP_PERCENT, MARKUP_FROM, SEASONS, RATES, nightPrice, stayTotal, fromPrice, addDays };
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    } else {
        root.MontePrices = api;
    }
})(typeof window !== 'undefined' ? window : this);
