// Home page hero video. The video is not part of the HTML so that phones, data-saver mode and
// visitors who prefer reduced motion do not download a large file: they see the poster image.
(function () {
    'use strict';

    const video = document.getElementById('hero_video');
    if (!video) return;

    const connection = navigator.connection || {};
    const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (connection.saveData || reduceMotion) return;

    const small = window.matchMedia && window.matchMedia('(max-width: 767px)').matches;
    video.src = small ? video.dataset.srcMobile : video.dataset.srcDesktop;
    video.play().catch(function () { /* autoplay blocked: the poster stays */ });
})();
