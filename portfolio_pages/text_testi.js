// Home text testimonials
(function () {
    var cards = Array.from(document.querySelectorAll('.testi-card'));
    var dots = document.getElementById('testiDots');
    var prevBtn = document.getElementById('testiPrev');
    var nextBtn = document.getElementById('testiNext');
    var total = cards.length;
    var current = 0;
    var autoTimer;
    /* Build dots */
    cards.forEach(function (_, i) {
        var d = document.createElement('button');
        d.className = 'testi-dot' + (i === 0 ? ' active' : '');
        d.setAttribute('aria-label', 'Go to slide ' + (i + 1));
        d.addEventListener('click', function () { goTo(i); });
        dots.appendChild(d);
    });
    function posClass(i) {
        var diff = i - current;
        /* wrap around */
        if (diff > total / 2) diff -= total;
        if (diff < -total / 2) diff += total;
        if (diff === 0) return 'pos-active';
        if (diff === -1) return 'pos-prev';
        if (diff === 1) return 'pos-next';
        if (diff < -1) return 'pos-far-prev';
        if (diff > 1) return 'pos-far-next';
        return '';
    }
    function render() {
        cards.forEach(function (card, i) {
            card.className = 'testi-card ' + posClass(i);
        });
        /* dots */
        Array.from(dots.children).forEach(function (d, i) {
            d.classList.toggle('active', i === current);
        });
    }
    function goTo(n) {
        current = ((n % total) + total) % total;
        render();
        resetAuto();
    }
    prevBtn.addEventListener('click', function () { goTo(current - 1); });
    nextBtn.addEventListener('click', function () { goTo(current + 1); });
    /* click side cards to navigate */
    cards.forEach(function (card, i) {
        card.addEventListener('click', function () {
            if (i !== current) goTo(i);
        });
    });
    /* swipe / drag */
    var startX = null;
    var stage = document.getElementById('testiStage');
    stage.addEventListener('touchstart', function (e) {
        startX = e.touches[0].clientX;
    }, { passive: true });
    stage.addEventListener('touchend', function (e) {
        if (startX === null) return;
        var dx = e.changedTouches[0].clientX - startX;
        if (Math.abs(dx) > 40) goTo(dx < 0 ? current + 1 : current - 1);
        startX = null;
    }, { passive: true });
    stage.addEventListener('mousedown', function (e) { startX = e.clientX; });
    stage.addEventListener('mouseup', function (e) {
        if (startX === null) return;
        var dx = e.clientX - startX;
        if (Math.abs(dx) > 40) goTo(dx < 0 ? current + 1 : current - 1);
        startX = null;
    });
    /* auto-play */
    function resetAuto() {
        clearInterval(autoTimer);
        autoTimer = setInterval(function () { goTo(current + 1); }, 5000);
    }
    resetAuto();
    /* pause on hover */
    if (stage) {
        stage.addEventListener('mouseenter', function () { clearInterval(autoTimer); });
        stage.addEventListener('mouseleave', resetAuto);
    }
    /* keyboard */
    document.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') goTo(current - 1);
        if (e.key === 'ArrowRight') goTo(current + 1);
    });
    /* scroll reveal header */
    var head = document.getElementById('testiHead');
    if (head && 'IntersectionObserver' in window) {
        new IntersectionObserver(function (entries, obs) {
            if (entries[0].isIntersecting) {
                head.classList.add('on');
                obs.disconnect();
            }
        }, { threshold: 0.2 }).observe(head);
    }
    /* initial render */
    render();
})();

// ═══════════════════════════════════════════════════════════════
// HOMEPAGE DYNAMIC PORTFOLIO GRID SYNCHRONIZATION
// Syncs index.html .portfolio-grid cards with live Admin modifications
// ═══════════════════════════════════════════════════════════════
(function initHomeDynamicPortfolio() {
    function formatImgUrl(url) {
        if (!url) return '';
        if (url.startsWith('/') || url.startsWith('http')) return url;
        return '/' + url;
    }

    function syncPortfolioGrid() {
        var grid = document.querySelector('.portfolio-section .portfolio-grid');
        if (!grid) return;
        fetch('/api/portfolio?_=' + Date.now())
            .then(function (res) { return res.json(); })
            .then(function (json) {
                if (!json || !json.success || !Array.isArray(json.data) || json.data.length === 0) return;
                var items = json.data;
                grid.innerHTML = items.map(function (p) {
                    var thumb = p.thumbnail_image || p.cover_image || 'assets/images/portfolio/hp/4.jpg';
                    var thumbSrc = formatImgUrl(thumb);
                    var targetUrl = p.project_url || ('/portfolio/' + (p.slug || p.id));
                    var badgeText = p.badge || p.client || p.title;
                    var descText = p.quote || p.short_desc || '';
                    var cat = (p.category || 'all').toLowerCase().replace(/[^a-z0-9]/g, '');
                    return (
                        '<article class="portfolio-card" data-category="' + cat + '">' +
                            '<a href="' + targetUrl + '">' +
                                '<div class="card-image-wrapper">' +
                                    '<div class="card-image">' +
                                        '<img src="' + thumbSrc + '" alt="' + (p.title || '') + '" onerror="this.onerror=null; this.src=\'assets/images/portfolio/hp/4.jpg\';">' +
                                    '</div>' +
                                    '<div class="card-overlay"></div>' +
                                    '<div class="card-badge">' + badgeText + '</div>' +
                                '</div>' +
                                '<div class="card-content">' +
                                    '<h3 class="card-title">' + (p.title || '') + '</h3>' +
                                    (descText ? '<p class="portfolio-description"><i>"' + descText.replace(/^"|"$/g, '') + '"</i></p>' : '') +
                                '</div>' +
                            '</a>' +
                        '</article>'
                    );
                }).join('');
            })
            .catch(function (err) {
                console.warn('Home portfolio sync notice:', err);
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', syncPortfolioGrid);
    } else {
        syncPortfolioGrid();
    }
})();
