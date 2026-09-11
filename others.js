// New Animations
const container = document.querySelector('.bg-animation-container');
// Create Data Nodes
function createDataNodes() {
    for (let i = 0; i < 15; i++) {
        const node = document.createElement('div');
        node.className = 'data-node';
        node.style.left = Math.random() * 100 + '%';
        node.style.setProperty('--drift', (Math.random() - 0.5) * 200 + 'px');
        node.style.animationDuration = (15 + Math.random() * 15) + 's';
        node.style.animationDelay = Math.random() * 10 + 's';
        container.appendChild(node);
    }
}
// Create Geometric Shapes
function createGeoShapes() {
    const shapes = ['circle', 'triangle'];
    for (let i = 0; i < 8; i++) {
        const shape = document.createElement('div');
        shape.className = 'geo-shape ' + shapes[Math.floor(Math.random() * shapes.length)];
        const size = 40 + Math.random() * 60;
        shape.style.width = size + 'px';
        shape.style.height = size + 'px';
        shape.style.left = Math.random() * 100 + '%';
        shape.style.animationDuration = (20 + Math.random() * 20) + 's';
        shape.style.animationDelay = Math.random() * 15 + 's';
        container.appendChild(shape);
    }
}
// Create Connection Lines
function createConnectionLines() {
    for (let i = 0; i < 6; i++) {
        const line = document.createElement('div');
        line.className = 'connection-line';
        line.style.width = (30 + Math.random() * 40) + '%';
        line.style.left = Math.random() * 100 + '%';
        line.style.animationDuration = (12 + Math.random() * 10) + 's';
        line.style.animationDelay = Math.random() * 8 + 's';
        container.appendChild(line);
    }
}
// Create Particles
function createParticles() {
    for (let i = 0; i < 25; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.setProperty('--particle-drift', (Math.random() - 0.5) * 300 + 'px');
        particle.style.animationDuration = (10 + Math.random() * 15) + 's';
        particle.style.animationDelay = Math.random() * 10 + 's';
        container.appendChild(particle);
    }
}
// Create Chart Bars
function createChartBars() {
    for (let i = 0; i < 10; i++) {
        const bar = document.createElement('div');
        bar.className = 'chart-bar';
        bar.style.height = (50 + Math.random() * 100) + 'px';
        bar.style.left = Math.random() * 100 + '%';
        bar.style.animationDuration = (15 + Math.random() * 10) + 's';
        bar.style.animationDelay = Math.random() * 12 + 's';
        container.appendChild(bar);
    }
}
// Initialize all animations
createDataNodes();
createGeoShapes();
createConnectionLines();
createParticles();
createChartBars();
// Recreate elements periodically to maintain continuous animation
setInterval(() => {
    const oldNodes = document.querySelectorAll('.data-node, .particle, .chart-bar');
    if (oldNodes.length < 30) {
        createDataNodes();
        createParticles();
        createChartBars();
    }
}, 20000);
// Back to top
$(document).ready(function () {
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('#scroll').fadeIn();
        } else {
            $('#scroll').fadeOut();
        }
    });
    $('#scroll').click(function () {
        $("html, body").animate({ scrollTop: 0 }, 600);
        return false;
    });
});
