// Portfolio page
// Testi
/* ── Scroll reveal ── */
new IntersectionObserver((entries, obs) => {
    if (!entries[0].isIntersecting) return;
    document.getElementById('tsHeader').classList.add('on');
    setTimeout(() => document.getElementById('tsBody').classList.add('on'), 180);
    obs.disconnect();
}, { threshold: 0.1 }).observe(document.getElementById('ts'));
