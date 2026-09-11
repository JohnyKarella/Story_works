// Home testimonials

/* ══ DATA ══ */
const DATA = [
    { name: "Name", role: "Designation" },
    { name: "Name", role: "Designation" },
    { name: "Name", role: "Designation" },
    { name: "Name", role: "Designation" },
    { name: "Name", role: "Designation" },
];

const cards = [...document.querySelectorAll('.card')];
const total = cards.length;
const iName = document.getElementById('iName');
const iRole = document.getElementById('iRole');
const dotsWrap = document.getElementById('dotsWrap');
let current = 0;
let busy = false;
let rafId = null;

/* ── Build dots ── */
DATA.forEach((_, i) => {
    const b = document.createElement('button');
    b.className = 'dot' + (i === 0 ? ' active' : '');
    b.setAttribute('aria-label', `Slide ${i + 1}`);
    b.addEventListener('click', () => goTo(i));
    dotsWrap.appendChild(b);
});

/* ── Layout ── */
function layout() {
    cards.forEach((c, i) => {
        let p = ((i - current) % total + total) % total;
        if (p > Math.floor(total / 2)) p -= total;
        c.setAttribute('data-pos', String(p));
    });
    iName.textContent = DATA[current].name;
    iRole.textContent = DATA[current].role;
    [...dotsWrap.querySelectorAll('.dot')].forEach((d, i) => d.classList.toggle('active', i === current));
}

/* ── Icon sync (no-op — buttons hidden) ── */
function setIcons() { }

/* ── Stop all ── */
function stopAll() {
    cancelAnimationFrame(rafId);
    cards.forEach(c => {
        const v = c.querySelector('video');
        v.pause(); v.currentTime = 0;
    });
}

/* ── RAF — unused now (native bar handles progress) ── */
function startProgress() { }

/* ── Play active ── */
function playActive() {
    const ac = cards.find(c => c.getAttribute('data-pos') === '0');
    if (!ac) return;
    const v = ac.querySelector('video');
    v.muted = true;
    v.play()
        .then(() => { v.muted = false; })
        .catch(() => { });
}

/* ── Navigate ── */
function goTo(idx) {
    if (busy) return;
    const target = ((idx % total) + total) % total;
    if (target === current) return;
    busy = true;
    stopAll();
    current = target;
    layout();
    playActive();
    setTimeout(() => { busy = false; }, 560);
}
const prev = () => goTo(current - 1);
const next = () => goTo(current + 1);

/* ── Auto-advance on video end ── */
cards.forEach(c => {
    c.querySelector('video').addEventListener('ended', () => { next(); });
});

/* play/pause button removed */

/* ── Click side card ── */
cards.forEach((c, i) => {
    c.addEventListener('click', () => { if (c.getAttribute('data-pos') !== '0') goTo(i); });
});

/* ── Arrows ── */
document.getElementById('prevBtn').addEventListener('click', prev);
document.getElementById('nextBtn').addEventListener('click', next);

/* ── Keyboard ── */
document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') prev();
    if (e.key === 'ArrowRight') next();
});

/* ── Touch swipe ── */
let tx = 0, ty = 0;
const stage = document.getElementById('stage');
stage.addEventListener('touchstart', e => { tx = e.touches[0].clientX; ty = e.touches[0].clientY; }, { passive: true });
stage.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty;
    if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 40) { dx < 0 ? next() : prev(); }
}, { passive: true });

/* ── Mouse drag ── */
let mx = 0, dragging = false;
stage.addEventListener('mousedown', e => { mx = e.clientX; dragging = true; });
stage.addEventListener('mouseup', e => { if (!dragging) return; dragging = false; const dx = e.clientX - mx; if (Math.abs(dx) > 50) { dx < 0 ? next() : prev(); } });
stage.addEventListener('mouseleave', () => { dragging = false; });

/* ── INIT ── */
layout();
playActive();

