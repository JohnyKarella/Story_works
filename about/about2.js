// About2
// Service Flow
// Animate the flowing line on page load/refresh
window.addEventListener('load', function () {
    const animatedPaths = document.querySelectorAll('.path-animated');
    // Set up all animated paths
    animatedPaths.forEach((path, index) => {
        const pathLength = path.getTotalLength();
        // Set up the starting positions
        path.style.strokeDasharray = pathLength + ' ' + pathLength;
        path.style.strokeDashoffset = pathLength;
        // Trigger the animation with sequential delay
        setTimeout(() => {
            path.style.transition = 'stroke-dashoffset 0.4s ease-in-out';
            path.style.strokeDashoffset = '0';
        }, 100 + (index * 250));
    });
    // Animate numbers appearing sequentially
    const processNumbers = document.querySelectorAll('.process-number');
    const numberOrder = [0, 1, 2, 5, 4, 3]; // Order: 1,2,3,4,5,6 based on flow
    numberOrder.forEach((numIndex, i) => {
        const number = processNumbers[numIndex];
        setTimeout(() => {
            number.style.opacity = '0';
            number.style.transform = 'scale(0)';
            number.style.transition = 'all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
            setTimeout(() => {
                number.style.opacity = '1';
                number.style.transform = 'scale(1)';
            }, 50);
        }, 200 + (i * 500));
    });
});
// Services Card
// Service data
const services = [
    {
        icon: 'fas fa-chart-line',
        title: 'Brand Strategy',
        description: 'We move beyond aesthetics to architect the strategic soul of your business. By synthesizing market intelligence with intuition, we build the narrative frameworks that drive your brand’s future.'
    },
    {
        icon: 'fas fa-search',
        title: 'Brand Identity &<br> Design',
        description: 'We craft visual legacies through intentional design, from signature logos to multi-sensory systems. Every touchpoint is engineered for flawless consistency, creating a timeless invitation into your brand’s world.'
    },
    {
        icon: 'fas fa-thumbs-up',
        title: 'Content & <br>Copywriting',
        description: 'Our narratives do more than fill space; they command attention and build lasting rapport. We translate complex value propositions into persuasive human stories that sell a philosophy, not just a product.'
    },
    {
        icon: 'fab fa-google',
        title: 'Digital <br>Marketing',
        description: 'Our approach integrates high-intent SEO and strategic social storytelling into performance-driven ecosystems that grow your community and your revenue in equal measure.'
    },
    {
        icon: 'fas fa-laptop-code',
        title: 'Web & <br>Experience Design',
        description: 'We view the digital interface as a premier storefront. Our team designs high-conversion digital environments where elegant minimalism meets functional rigor, ensuring every click feels intuitive and every interaction reinforces trust.'
    },
    {
        icon: 'fas fa-code',
        title: 'Launch & <br>Campaign Strategy',
        description: 'We transform entries into arrivals through strategic blueprints and high-impact storytelling. By orchestrating the pivotal moments where brands meet the world, we ensure your debut is both seen and felt.'
    }
];
// Generate cards
const servicesGrid = document.getElementById('servicesGrid');
services.forEach(service => {
    const card = document.createElement('div');
    card.className = 'service-card-container';
    // Generate 60 icons for seamless scroll (6 columns × 10 rows)
    let iconHTML = '';
    for (let i = 0; i < 60; i++) {
        iconHTML += `<i class="${service.icon}"></i>`;
    }
    card.innerHTML = `
                <div class="service-card-inner">
                    <div class="service-card-front">
                        <div class="icon-pattern">
                            <div class="icon-pattern-wrapper">
                                ${iconHTML}
                            </div>
                        </div>
                        <div class="card-content">
                            <div class="icon-wrapper">
                                <i class="${service.icon}"></i>
                            </div>
                            <h3>${service.title}</h3>
                        </div>
                    </div>
                    <div class="service-card-back">
                        <h3>${service.title.replace('<br>', ' ')}</h3>
                        <p>${service.description}</p>
                    </div>
                </div>
            `;
    servicesGrid.appendChild(card);
});
