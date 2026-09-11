// ABOUT US
// ==================== CUBE MOUSE INTERACTION ====================
const heroCube = document.getElementById('heroCube');
let mouseX = 0;
let mouseY = 0;
let cubeRotationX = 0;
let cubeRotationY = 0;

document.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
});

function animateCube() {
    cubeRotationX += (mouseY * 20 - cubeRotationX) * 0.05;
    cubeRotationY += (mouseX * 20 - cubeRotationY) * 0.05;

    if (heroCube && !heroCube.matches(':hover')) {
        heroCube.style.transform = `rotateX(${cubeRotationX}deg) rotateY(${cubeRotationY}deg)`;
    }

    requestAnimationFrame(animateCube);
}

animateCube();

// ==================== PARALLAX EFFECT FOR GRADIENT ORBS ====================
const orbs = document.querySelectorAll('.gradient-orb');

document.addEventListener('mousemove', (e) => {
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;

    orbs.forEach((orb, index) => {
        const speed = (index + 1) * 0.05;
        const xOffset = (x - 0.5) * 100 * speed;
        const yOffset = (y - 0.5) * 100 * speed;

        orb.style.transform = `translate(${xOffset}px, ${yOffset}px)`;
    });
});

// ==================== SMOOTH SCROLL ====================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (!href || href === '#') return;
        try {
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        } catch (err) {}
    });
});

// ==================== BUTTON RIPPLE EFFECT ====================
document.querySelectorAll('.btn').forEach(button => {
    button.addEventListener('click', function (e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.5);
                    left: ${x}px;
                    top: ${y}px;
                    transform: scale(0);
                    animation: ripple 0.6s ease-out;
                    pointer-events: none;
                `;

        this.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });
});

// Add ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
        transform: scale(4);
    opacity: 0;
                }
            }
    `;
document.head.appendChild(style);

// ==================== CONSOLE MESSAGE ====================
console.log('%c Welcome to Innovation! ',
    'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 20px; padding: 15px; border-radius: 10px; font-weight: bold;');
console.log('%c Crafting digital experiences that matter ✨',
    'color: #667eea; font-size: 16px; padding: 10px;');







// faq

function toggleFaq(btn) {
    const item = btn.closest('.faq-item');
    const isActive = item.classList.contains('active');
    // close all
    document.querySelectorAll('.faq-item').forEach(el => el.classList.remove('active'));
    // toggle clicked
    if (!isActive) item.classList.add('active');
}
