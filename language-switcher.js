// Progressive enhancement for the <details> language selector:
// close it on Escape, on an outside click/tap, and when focus leaves it.
document.querySelectorAll('.language-selector').forEach((selector) => {
    const summary = selector.querySelector('summary');

    document.addEventListener('click', (event) => {
        if (selector.open && !selector.contains(event.target)) {
            selector.open = false;
        }
    });

    selector.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && selector.open) {
            selector.open = false;
            summary.focus();
        }
    });

    selector.addEventListener('focusout', (event) => {
        if (selector.open && event.relatedTarget && !selector.contains(event.relatedTarget)) {
            selector.open = false;
        }
    });
});
