// PORTFOLIO PAGE
/* ═══════════════════════════════════════
TAB & SIDEBAR SWITCHING
JS only handles show/hide — no rendering
═══════════════════════════════════════ */

/* map each cat key → which client is default-active */
const defaultClient = {
    pkg: 'pkg-sbl', brd: 'brd-shaanvi', web: 'web-bship', mkt: 'mkt-sbl', pho: 'pho-sbl'
};
let activeCat = 'pkg';
let activeClient = 'pkg-sbl';

function switchCat(cat) {
    activeCat = cat;
    activeClient = defaultClient[cat];

    /* tabs */
    document.querySelectorAll('.cat-tab').forEach(t =>
        t.classList.toggle('active', t.dataset.cat === cat));

    /* sidebar groups */
    document.querySelectorAll('.sb-group').forEach(g =>
        g.classList.toggle('active', g.dataset.cat === cat));

    /* reset all sb-items; activate first of new group */
    document.querySelectorAll('.sb-item').forEach(i => i.classList.remove('active'));
    const firstItem = document.querySelector(`.sb-item[data-client="${activeClient}"]`);
    if (firstItem) firstItem.classList.add('active');

    showClient(activeClient);
}

function switchClient(client) {
    activeClient = client;

    /* sidebar items */
    document.querySelectorAll('.sb-item').forEach(i =>
        i.classList.toggle('active', i.dataset.client === client));

    showClient(client);
}

function showClient(client) {
    /* info bars */
    document.querySelectorAll('.info-set').forEach(el =>
        el.classList.toggle('active', el.dataset.client === client));

    /* grids — fade out, swap, fade in */
    const current = document.querySelector('.grid-set.active');
    const next = document.querySelector(`.grid-set[data-client="${client}"]`);
    if (!next || current === next) return;

    current.classList.add('out');
    setTimeout(() => {
        current.classList.remove('active', 'out');
        next.classList.add('active');
    }, 200);
}

/* bind tab clicks */
document.querySelectorAll('.cat-tab').forEach(btn =>
    btn.addEventListener('click', () => switchCat(btn.dataset.cat)));

/* bind sidebar item clicks */
document.querySelectorAll('.sb-item').forEach(item =>
    item.addEventListener('click', () => switchClient(item.dataset.client)));

/* ═══════════════════════════════════════
   LIGHTBOX  (unchanged)
═══════════════════════════════════════ */
const lb = document.getElementById('lb');
const lbBox = document.getElementById('lbBox');
const lbImg = document.getElementById('lbImg');
const lbBadge = document.getElementById('lbBadge');
const lbTitle = document.getElementById('lbTitle');
const lbQuote = document.getElementById('lbQuote');

const lbDots = document.getElementById('lbDots');
const lbX = document.getElementById('lbX');
const lbPrev = document.getElementById('lbPrev');
const lbNext = document.getElementById('lbNext');

let list = [], idx = 0;

function openLB(l, i) { list = l; idx = i; sync(); lb.classList.add('open'); document.body.style.overflow = 'hidden'; }
function closeLB() { lb.classList.remove('open'); document.body.style.overflow = ''; }
function goLB(dir) {
    lbImg.classList.add('fade');
    setTimeout(() => { idx = (idx + dir + list.length) % list.length; sync(); lbImg.classList.remove('fade'); }, 170);
}
function sync() {
    const p = list[idx];
    lbImg.src = p.img;
    lbImg.alt = p.title;
    lbBadge.textContent = p.badge || '';
    lbTitle.textContent = p.title || '';
    lbQuote.textContent = p.quote ? `"${p.quote}"` : '';
  
    lbDots.innerHTML = '';
    list.forEach((_, i) => {
        const d = document.createElement('span');
        d.className = 'ld' + (i === idx ? ' on' : '');
        d.onclick = () => { if (i !== idx) { idx = i; sync(); } };
        lbDots.appendChild(d);
    });
    const m = list.length > 1;
    lbPrev.style.display = m ? '' : 'none';
    lbNext.style.display = m ? '' : 'none';
}

lb.addEventListener('click', e => { if (e.target === lb) closeLB(); });
lbX.addEventListener('click', closeLB);
lbPrev.addEventListener('click', e => { e.stopPropagation(); goLB(-1); });
lbNext.addEventListener('click', e => { e.stopPropagation(); goLB(+1); });
document.addEventListener('keydown', e => {
    if (!lb.classList.contains('open')) return;
    if (e.key === 'Escape') closeLB();
    if (e.key === 'ArrowLeft') goLB(-1);
    if (e.key === 'ArrowRight') goLB(+1);
});
let tx = 0;
lbBox.addEventListener('touchstart', e => { tx = e.changedTouches[0].clientX; }, { passive: true });
lbBox.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - tx;
    if (Math.abs(dx) > 45) goLB(dx < 0 ? 1 : -1);
}, { passive: true });

/* card click → lightbox — reads from live HTML */
document.querySelector('.img-panel').addEventListener('click', e => {
    const card = e.target.closest('.pc');
    if (!card) return;
    const grid = card.closest('.grid-set');
    const cards = Array.from(grid.querySelectorAll('.pc'));
    const i = cards.indexOf(card);
    const l = cards.map(c => ({
        img: c.querySelector('img').src,
        title: c.querySelector('.pc-title')?.textContent || c.querySelector('.pc-lbl')?.textContent || '',
        badge: c.querySelector('.pc-badge')?.textContent || '',
        quote: (c.querySelector('.pc-quote')?.textContent || '').replace(/^"|"$/g, ''),
    }));
    openLB(l, i);
});
