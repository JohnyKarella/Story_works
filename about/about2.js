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
// Default Service data fallback
const defaultServices = [
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

function getServiceIconClass(icon) {
    if (!icon) return 'fas fa-star';
    const trimmed = icon.trim();
    if (trimmed.startsWith('fa-') || trimmed.startsWith('fas ') || trimmed.startsWith('fab ') || trimmed.startsWith('far ')) {
        if (!trimmed.includes(' ')) {
            return 'fas ' + trimmed;
        }
        return trimmed;
    }
    const map = {
        'strategy': 'fas fa-chart-line',
        'chart-line': 'fas fa-chart-line',
        'identity': 'fas fa-search',
        'design': 'fas fa-search',
        'search': 'fas fa-search',
        'content': 'fas fa-thumbs-up',
        'copywriting': 'fas fa-thumbs-up',
        'thumbs-up': 'fas fa-thumbs-up',
        'digital': 'fab fa-google',
        'marketing': 'fab fa-google',
        'google': 'fab fa-google',
        'web': 'fas fa-laptop-code',
        'laptop-code': 'fas fa-laptop-code',
        'launch': 'fas fa-code',
        'campaign': 'fas fa-code',
        'code': 'fas fa-code',
        'sparkles': 'fas fa-magic',
        'layout': 'fas fa-laptop-code',
        'camera': 'fas fa-camera',
        'trending-up': 'fas fa-chart-line'
    };
    return map[trimmed.toLowerCase()] || `fas fa-${trimmed}`;
}

function renderServices(items) {
    const servicesGrid = document.getElementById('servicesGrid');
    if (!servicesGrid || !items || !items.length) return;
    servicesGrid.innerHTML = '';

    items.forEach(service => {
        const card = document.createElement('div');
        card.className = 'service-card-container';
        const iconClass = getServiceIconClass(service.icon);

        // Generate 60 icons for seamless scroll (6 columns × 10 rows)
        let iconHTML = '';
        for (let i = 0; i < 60; i++) {
            iconHTML += `<i class="${iconClass}"></i>`;
        }

        let rawTitle = service.title || '';
        let frontTitle = rawTitle;
        if (!frontTitle.includes('<br>') && frontTitle.includes(' & ')) {
            frontTitle = frontTitle.replace(' & ', ' &<br> ');
        }
        const backTitle = rawTitle.replace(/<br\s*[\/]?>/gi, ' ');
        const description = service.short_desc || service.description || service.full_desc || '';

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
                            <i class="${iconClass}"></i>
                        </div>
                        <h3>${frontTitle}</h3>
                    </div>
                </div>
                <div class="service-card-back">
                    <h3>${backTitle}</h3>
                    <p>${description}</p>
                </div>
            </div>
        `;
        servicesGrid.appendChild(card);
    });
}

// Generate cards immediately from default fallback, then hydrate from live API
const servicesGrid = document.getElementById('servicesGrid');
if (servicesGrid) {
    renderServices(defaultServices);

    fetch('/api/services')
        .then(res => {
            if (!res.ok) throw new Error('Network response not ok');
            return res.json();
        })
        .then(data => {
            if (data && data.success && Array.isArray(data.data) && data.data.length > 0) {
                renderServices(data.data);
            }
        })
        .catch(err => {
            console.warn('Live services load notice:', err.message);
        });
}

