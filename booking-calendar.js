// Contact page date pickers that show prices (Flatpickr) and an estimated stay total.
// Prices come from prices.js. If Flatpickr fails to load, the native date inputs keep working.
(function () {
    'use strict';

    const P = window.MontePrices;
    const roomSelect = document.getElementById('room_category');
    const estimateBox = document.getElementById('estimate');
    if (typeof flatpickr === 'undefined' || !P || !roomSelect || !estimateBox) return;

    const form = roomSelect.form;
    const lang = document.documentElement.lang || 'en';
    const ROOMS = Object.keys(P.RATES);

    const STRINGS = {
        en: {
            legendNight: 'Price per night in USD',
            legendNightFrom: 'Price per night in USD for our most affordable room. Choose a room to see its price.',
            legendTotal: 'Total in USD if you leave on this day',
            legendTotalFrom: 'Total in USD for our most affordable room if you leave on this day. Choose a room to see its price.',
            legendPickIn: 'Choose a check-in date to see the total for each check-out day.',
            totalLabel: 'Estimated total',
            night: (n) => (n === 1 ? 'night' : 'nights'),
            avg: (p) => 'about ' + p + ' per night',
            noRoom: 'Select a room category to see the estimated total.',
            onRequest: 'There is no online rate for these dates (rates cover 4 Dec to 10 Apr). We will confirm the price in our reply.',
            note: 'Prices include VAT and breakfast, access to the steam and Finnish saunas, indoor pool and game room, and the shuttle to the Shino ski lift (during the ski season). This is an estimate only; the hotel confirms the final price.',
            newYearMin: 'Stays that include 30 Dec, 31 Dec or 1 Jan require a minimum of 3 nights.',
            newYearJan1: 'Check-in and check-out are not available on 1 January.',
        },
        ka: {
            legendNight: 'ფასი ღამეში, USD',
            legendNightFrom: 'ფასი ღამეში USD-ით ყველაზე ხელმისაწვდომი ნომრისთვის. აირჩიეთ ნომერი მისი ფასის სანახავად.',
            legendTotal: 'ჯამი USD-ით, თუ ამ დღეს გახვალთ',
            legendTotalFrom: 'ჯამი USD-ით ყველაზე ხელმისაწვდომი ნომრისთვის, თუ ამ დღეს გახვალთ. აირჩიეთ ნომერი მისი ფასის სანახავად.',
            legendPickIn: 'აირჩიეთ შემოსვლის თარიღი, რომ გასვლის თითოეული დღის ჯამი ნახოთ.',
            totalLabel: 'სავარაუდო ჯამური ფასი',
            night: () => 'ღამე',
            avg: (p) => 'დაახლოებით ' + p + ' ღამეში',
            noRoom: 'აირჩიეთ ნომრის კატეგორია სავარაუდო ფასის სანახავად.',
            onRequest: 'ამ თარიღებისთვის ონლაინ ტარიფი არ არის (ტარიფები მოიცავს პერიოდს 4 დეკემბრიდან 10 აპრილამდე). ფასს პასუხში დაგიდასტურებთ.',
            note: 'ფასი მოიცავს დღგ-სა და საუზმეს, ორთქლისა და ფინური საუნების, დახურული აუზისა და გასართობი ოთახის გამოყენებას, ასევე შატლს შინოს სათხილამურო ამწემდე (სათხილამურო სეზონზე). ეს მხოლოდ სავარაუდო ფასია; საბოლოო ფასს სასტუმრო დაადასტურებს.',
            newYearMin: 'იმ ყოფნისთვის, რომელიც მოიცავს 30 დეკემბერს, 31 დეკემბერს ან 1 იანვარს, მინიმალური ვადა 3 ღამეა.',
            newYearJan1: '1 იანვარს შემოსვლა და გასვლა შეუძლებელია.',
        },
        ru: {
            legendNight: 'Цена за ночь в USD',
            legendNightFrom: 'Цена за ночь в USD для самого доступного номера. Выберите номер, чтобы увидеть его цену.',
            legendTotal: 'Итого в USD, если выехать в этот день',
            legendTotalFrom: 'Итого в USD для самого доступного номера, если выехать в этот день. Выберите номер, чтобы увидеть его цену.',
            legendPickIn: 'Выберите дату заезда, чтобы увидеть итог для каждого дня выезда.',
            totalLabel: 'Ориентировочная стоимость',
            night: (n) => {
                const t = n % 10;
                const h = n % 100;
                if (t === 1 && h !== 11) return 'ночь';
                if (t >= 2 && t <= 4 && (h < 12 || h > 14)) return 'ночи';
                return 'ночей';
            },
            avg: (p) => 'около ' + p + ' за ночь',
            noRoom: 'Выберите категорию номера, чтобы увидеть ориентировочную стоимость.',
            onRequest: 'На эти даты нет онлайн-тарифа (тарифы действуют с 4 декабря по 10 апреля). Стоимость подтвердим в ответе.',
            note: 'Цены включают НДС, завтрак, доступ к паровой и финской саунам, крытому бассейну и игровой комнате, а также трансфер до подъёмника Шино (в лыжный сезон). Это лишь ориентировочная стоимость, окончательную цену подтверждает отель.',
            newYearMin: 'Для проживания, включающего 30 декабря, 31 декабря или 1 января, минимальный срок составляет 3 ночи.',
            newYearJan1: '1 января заезд и выезд недоступны.',
        },
    };
    const T = STRINGS[lang] || STRINGS.en;

    const pad = (n) => String(n).padStart(2, '0');
    const toIso = (d) => d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
    const money = (n) => '$' + n.toLocaleString('en-US');

    // Nightly price for a date: the chosen room, or the cheapest room when none is chosen.
    function nightPrice(iso) {
        return roomSelect.value ? P.nightPrice(roomSelect.value, iso) : P.fromPrice(iso);
    }

    // Total if the guest checks in on `checkin` and leaves on `checkout`.
    function stayTotal(checkin, checkout) {
        const rooms = roomSelect.value ? [roomSelect.value] : ROOMS;
        let best = null;
        rooms.forEach((room) => {
            const stay = P.stayTotal(room, checkin, checkout);
            if (stay && (best === null || stay.total < best)) best = stay.total;
        });
        return best;
    }

    let inFp;
    let outFp;

    function decorate(kind, dayElem) {
        const iso = toIso(dayElem.dateObj);
        let price = null;
        if (kind === 'in') {
            price = nightPrice(iso);
        } else if (inFp.selectedDates[0]) {
            const checkin = toIso(inFp.selectedDates[0]);
            if (iso > checkin) price = stayTotal(checkin, iso);
        }
        if (price === null) return;
        const tag = document.createElement('span');
        tag.className = 'day_price';
        tag.textContent = money(price);
        dayElem.appendChild(tag);
        dayElem.setAttribute('aria-label', dayElem.getAttribute('aria-label') + ', ' + money(price));
    }

    function legendText(kind) {
        if (kind === 'in') return roomSelect.value ? T.legendNight : T.legendNightFrom;
        if (!inFp.selectedDates[0]) return T.legendPickIn;
        return roomSelect.value ? T.legendTotal : T.legendTotalFrom;
    }

    function refresh() {
        [['in', inFp], ['out', outFp]].forEach(([kind, fp]) => {
            fp.redraw();
            fp.calendarContainer.querySelector('.price_legend').textContent = legendText(kind);
        });
    }

    function setup(input, kind, extra) {
        const base = {
            altInput: true,
            altFormat: 'j M Y',
            dateFormat: 'Y-m-d',
            disableMobile: true, // the native mobile picker can't show prices
            locale: Object.assign({}, flatpickr.l10ns[lang] || flatpickr.l10ns.default, { firstDayOfWeek: 1 }),
            onDayCreate: (selected, str, inst, dayElem) => decorate(kind, dayElem),
            onReady: (selected, str, inst) => {
                const legend = document.createElement('div');
                legend.className = 'price_legend';
                inst.calendarContainer.appendChild(legend);
                // keep the visible field tied to its label
                const label = document.querySelector('label[for="' + input.id + '"]');
                inst.altInput.id = input.id + '_display';
                inst.altInput.setAttribute('autocomplete', 'off');
                if (label) label.setAttribute('for', inst.altInput.id);
            },
        };
        return flatpickr(input, Object.assign(base, extra));
    }

    function showSeasonStart(fp) {
        const first = P.SEASONS[0].from;
        if (!fp.selectedDates.length && toIso(new Date()) < first) fp.jumpToDate(first);
    }

    // Does the stay (nights from a up to, not including, b) include 30 Dec, 31 Dec or 1 Jan?
    function touchesNewYear(a, b) {
        for (let d = a; d < b; d = P.addDays(d, 1)) {
            const md = d.slice(5);
            if (md === '12-30' || md === '12-31' || md === '01-01') return true;
        }
        return false;
    }

    function addLine(className, text, strong) {
        const p = document.createElement('p');
        p.className = className;
        if (strong) {
            const b = document.createElement('strong');
            b.textContent = strong;
            p.appendChild(b);
            p.appendChild(document.createTextNode(text));
        } else {
            p.textContent = text;
        }
        estimateBox.appendChild(p);
    }

    function update() {
        form.elements.nights.value = '';
        form.elements.estimated_total.value = '';
        const inDate = inFp.selectedDates[0];
        const outDate = outFp.selectedDates[0];
        estimateBox.textContent = '';
        if (!inDate || !outDate) {
            estimateBox.hidden = true;
            return;
        }
        const a = toIso(inDate);
        const b = toIso(outDate);
        const room = roomSelect.value;
        const stay = room ? P.stayTotal(room, a, b) : null;

        if (!room) {
            addLine('estimate_total', T.noRoom);
        } else if (stay) {
            form.elements.nights.value = stay.nights;
            form.elements.estimated_total.value = stay.total + ' USD';
            const avg = money(Math.round(stay.total / stay.nights));
            addLine(
                'estimate_total',
                ' ' + money(stay.total) + ' · ' + stay.nights + ' ' + T.night(stay.nights) + ' (' + T.avg(avg) + ')',
                T.totalLabel + ':'
            );
        } else {
            addLine('estimate_total', T.onRequest);
        }

        let nights = 0;
        for (let d = a; d < b; d = P.addDays(d, 1)) nights += 1;
        if (touchesNewYear(a, b) && nights < 3) addLine('estimate_warning', T.newYearMin);
        if (a.slice(5) === '01-01' || b.slice(5) === '01-01') addLine('estimate_warning', T.newYearJan1);
        addLine('estimate_note', T.note);
        estimateBox.hidden = false;
    }

    inFp = setup(document.getElementById('checkin'), 'in', {
        minDate: 'today',
        onOpen: (selected, str, inst) => {
            showSeasonStart(inst);
            inst.calendarContainer.querySelector('.price_legend').textContent = legendText('in');
        },
        onChange: (selected) => {
            const checkin = selected[0] ? toIso(selected[0]) : null;
            outFp.set('minDate', checkin ? P.addDays(checkin, 1) : 'today');
            if (checkin && outFp.selectedDates[0] && toIso(outFp.selectedDates[0]) <= checkin) outFp.clear();
            refresh();
            update();
            if (checkin && !outFp.selectedDates[0]) setTimeout(() => outFp.open(), 0);
        },
    });

    outFp = setup(document.getElementById('checkout'), 'out', {
        minDate: 'today',
        onOpen: (selected, str, inst) => {
            if (!inFp.selectedDates[0]) showSeasonStart(inst);
            inst.calendarContainer.querySelector('.price_legend').textContent = legendText('out');
        },
        onChange: update,
    });

    roomSelect.addEventListener('change', () => {
        refresh();
        update();
    });

    // Flatpickr's visible fields don't clear on form.reset() (done after a successful send)
    form.addEventListener('reset', () => {
        setTimeout(() => {
            inFp.clear();
            outFp.clear();
            outFp.set('minDate', 'today');
            refresh();
            update();
        }, 0);
    });
})();
