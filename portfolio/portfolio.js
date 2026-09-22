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
const imgPanel = document.querySelector('.img-panel');
if (imgPanel) {
    imgPanel.addEventListener('click', e => {
        const card = e.target.closest('.pc');
        if (!card) return;
        const grid = card.closest('.grid-set');
        if (!grid) return;
        const cards = Array.from(grid.querySelectorAll('.pc'));
        const i = cards.indexOf(card);
        const l = cards.map(c => ({
            img: c.querySelector('img')?.src || '',
            title: c.querySelector('.pc-title')?.textContent || c.querySelector('.pc-lbl')?.textContent || '',
            badge: c.querySelector('.pc-badge')?.textContent || '',
            quote: (c.querySelector('.pc-quote')?.textContent || '').replace(/^"|"$/g, ''),
        }));
        openLB(l, i);
    });
}

// ═══════════════════════════════════════
// DYNAMIC PORTFOLIO GRID SYNCHRONIZATION
// Hydrates portfolio.html with live backend data
// ═══════════════════════════════════════
(function initDynamicPortfolio() {
    function syncPortfolioGrid() {
        const grid = document.querySelector('.portfolio-grid');
        if (!grid) return;
        fetch('/api/portfolio?_=' + Date.now())
            .then(res => res.json())
            .then(json => {
                if (!json || !json.success || !Array.isArray(json.data) || json.data.length === 0) return;
                const items = json.data;
                grid.innerHTML = items.map(p => {
                    const thumb = p.thumbnail_image || p.cover_image || 'assets/images/portfolio/hp/4.jpg';
                    const thumbSrc = (thumb.startsWith('/') || thumb.startsWith('http')) ? thumb : ('/' + thumb);
                    const targetUrl = p.project_url || ('/portfolio/' + p.slug);
                    const badgeText = p.badge || p.client || p.title;
                    const descText = p.quote || p.short_desc || '';
                    const cat = (p.category || 'all').toLowerCase().replace(/[^a-z0-9]/g, '');
                    return `
                        <article class="portfolio-card" data-category="${cat}">
                            <a href="${targetUrl}">
                                <div class="card-image-wrapper">
                                    <div class="card-image">
                                        <img src="${thumbSrc}" alt="${p.title}" onerror="this.onerror=null; this.src='assets/images/portfolio/hp/4.jpg';">
                                    </div>
                                    <div class="card-overlay"></div>
                                    <div class="card-badge">${badgeText}</div>
                                </div>
                                <div class="card-content">
                                    <h3 class="card-title">${p.title}</h3>
                                    ${descText ? `<p class="portfolio-description"><i>"${descText.replace(/^"|"$/g, '')}"</i></p>` : ''}
                                </div>
                            </a>
                        </article>
                    `;
                }).join('');
            })
            .catch(err => {
                console.warn('Portfolio sync notice:', err);
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', syncPortfolioGrid);
    } else {
        syncPortfolioGrid();
    }
})();
