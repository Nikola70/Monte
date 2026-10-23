// Pre-selects the room category on the contact form when the page is opened from a room card
// (for example /contact?room=deluxe_double). Runs after booking-calendar.js so prices update too.
(function () {
    'use strict';

    const select = document.getElementById('room_category');
    if (!select) return;

    let room = '';
    try {
        room = new URLSearchParams(window.location.search).get('room') || '';
    } catch (e) {
        return;
    }
    if (!room || !Array.from(select.options).some((option) => option.value === room)) return;

    select.value = room;
    select.dispatchEvent(new Event('change', { bubbles: true }));
})();
