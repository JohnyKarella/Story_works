// Portfolio testimonials


(function () {
    const canvas = document.getElementById('bg-canvas');
    const ctx = canvas.getContext('2d');
    let W, H, tick = 0;

    /* ── particles ── */
    const PCOUNT = 72;
    let pts = [];
    function mkPt() {
        return {
            x: Math.random() * W, y: Math.random() * H,
            r: Math.random() * 2.4 + 0.5,
            vx: (Math.random() - .5) * 0.32, vy: (Math.random() - .5) * 0.32,
            a: Math.random() * 0.22 + 0.06,
            ph: Math.random() * Math.PI * 2,
            sp: 0.007 + Math.random() * 0.013,
            hue: 270 + Math.random() * 55,
        };
    }

    /* ── ripple rings ── */
    let rings = [];
    function spawnRing() {
        rings.push({
            x: Math.random() * W, y: Math.random() * H,
            r: 0, maxR: 80 + Math.random() * 90,
            a: 0.16, speed: 0.5 + Math.random() * 0.45
        });
    }

    /* ── flowing lines data ── */
    const LINES = Array.from({ length: 7 }, (_, i) => ({
        yFrac: (i + 0.5) / 7,
        amp: 16 + i * 5, freq: 0.006 + i * 0.001,
        sp: 0.0018 + i * 0.0005, a: 0.055 - i * 0.006,
    }));

    /* ── shimmering grid dots ── */
    let gdots = [];
    function initGrid() {
        for (let gx = 60; gx < 1500; gx += 85)
            for (let gy = 30; gy < 700; gy += 65)
                gdots.push({
                    x: gx + (Math.random() - .5) * 28,
                    y: gy + (Math.random() - .5) * 28,
                    r: Math.random() * 1.3 + 0.35,
                    ph: Math.random() * Math.PI * 2,
                    sp: 0.011 + Math.random() * 0.019,
                });
    }

    function resize() { W = canvas.width = canvas.offsetWidth; H = canvas.height = canvas.offsetHeight; }

    function init() {
        resize();
        pts = Array.from({ length: PCOUNT }, mkPt);
        rings = [];
        for (let i = 0; i < 5; i++) spawnRing();
    }

    /* ── DRAW ORBS ── */
    function drawOrbs() {
        const pulse = 0.88 + 0.12 * Math.sin(tick * 0.005);

        // large purple orb, top-right
        const ox = W * 0.8 + Math.sin(tick * 0.0022) * 38, oy = H * 0.2 + Math.cos(tick * 0.003) * 22, r = 210 * pulse;
        const g = ctx.createRadialGradient(ox, oy, 0, ox, oy, r);
        g.addColorStop(0, 'rgba(150,80,195,0.13)');
        g.addColorStop(.5, 'rgba(130,60,175,0.06)');
        g.addColorStop(1, 'rgba(130,60,175,0)');
        ctx.beginPath(); ctx.arc(ox, oy, r, 0, Math.PI * 2); ctx.fillStyle = g; ctx.fill();

        // warm gold, bottom-centre
        const ox2 = W * .5 + Math.cos(tick * 0.003) * 55, oy2 = H * .88 + Math.sin(tick * 0.0025) * 16;
        const g2 = ctx.createRadialGradient(ox2, oy2, 0, ox2, oy2, 150);
        g2.addColorStop(0, 'rgba(195,150,90,0.11)');
        g2.addColorStop(1, 'rgba(195,150,90,0)');
        ctx.beginPath(); ctx.arc(ox2, oy2, 150, 0, Math.PI * 2); ctx.fillStyle = g2; ctx.fill();

        // small accent, left
        const ox3 = W * .06 + Math.sin(tick * 0.004) * 18, oy3 = H * .44 + Math.cos(tick * 0.003) * 25;
        const g3 = ctx.createRadialGradient(ox3, oy3, 0, ox3, oy3, 110);
        g3.addColorStop(0, 'rgba(123,63,160,0.11)');
        g3.addColorStop(1, 'rgba(123,63,160,0)');
        ctx.beginPath(); ctx.arc(ox3, oy3, 110, 0, Math.PI * 2); ctx.fillStyle = g3; ctx.fill();
    }

    /* ── DRAW FLOWING LINES ── */
    function drawLines() {
        for (const l of LINES) {
            const yBase = H * l.yFrac;
            ctx.beginPath();
            ctx.moveTo(0, yBase + Math.sin(tick * l.sp) * l.amp);
            for (let x = 0; x <= W; x += 6) {
                const y = yBase
                    + Math.sin(x * l.freq + tick * l.sp * 3.5) * l.amp
                    + Math.cos(x * l.freq * 1.8 + tick * l.sp * 2.2) * (l.amp * .45);
                ctx.lineTo(x, y);
            }
            ctx.strokeStyle = `rgba(123,63,160,${l.a})`;
            ctx.lineWidth = 1; ctx.stroke();
        }
    }

    /* ── DRAW GRID DOTS ── */
    function drawGrid() {
        for (const d of gdots) {
            d.ph += d.sp;
            const a = 0.045 + 0.09 * Math.abs(Math.sin(d.ph));
            ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(123,63,160,${a})`; ctx.fill();
        }
    }

    /* ── DRAW RIPPLES ── */
    function drawRipples() {
        for (let i = rings.length - 1; i >= 0; i--) {
            const rg = rings[i];
            rg.r += rg.speed;
            rg.a = 0.16 * (1 - rg.r / rg.maxR);
            ctx.beginPath(); ctx.arc(rg.x, rg.y, rg.r, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(123,63,160,${rg.a})`;
            ctx.lineWidth = 1.2; ctx.stroke();
            if (rg.r >= rg.maxR) { rings.splice(i, 1); spawnRing(); }
        }
    }

    /* ── DRAW PARTICLES ── */
    function drawPts() {
        for (const p of pts) {
            p.ph += p.sp;
            const a = p.a * (0.55 + 0.45 * Math.sin(p.ph));
            ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `hsla(${p.hue},50%,50%,${a})`; ctx.fill();
            p.x += p.vx; p.y += p.vy;
            if (p.x < -4) p.x = W + 4; if (p.x > W + 4) p.x = -4;
            if (p.y < -4) p.y = H + 4; if (p.y > H + 4) p.y = -4;
        }
    }

    /* ── AURORA sweep across background ── */
    function drawAurora() {
        const sweep = ((tick * 0.0015) % 1);
        const ax = W * (sweep - 0.1);
        const ag = ctx.createLinearGradient(ax, 0, ax + W * 0.45, H);
        ag.addColorStop(0, 'rgba(185,140,210,0)');
        ag.addColorStop(.3, 'rgba(185,140,210,0.04)');
        ag.addColorStop(.6, 'rgba(200,160,100,0.03)');
        ag.addColorStop(1, 'rgba(200,160,100,0)');
        ctx.fillStyle = ag;
        ctx.fillRect(0, 0, W, H);
    }

    function loop() {
        tick++;
        ctx.clearRect(0, 0, W, H);
        drawAurora();
        drawOrbs();
        drawLines();
        drawGrid();
        drawRipples();
        drawPts();
        requestAnimationFrame(loop);
    }

    window.addEventListener('resize', () => { resize(); });
    init(); initGrid(); loop();
})();
