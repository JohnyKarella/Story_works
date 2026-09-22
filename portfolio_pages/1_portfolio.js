// ═══════════════════════════════════════════════════════════════
// CASE STUDY PORTFOLIO DETAIL SYNCHRONIZATION
// Hydrates case study pages with live data from Admin modifications
// (Hero Banner, Approach Photo, Approach Text, Middle Banner, Descriptions)
// ═══════════════════════════════════════════════════════════════

/* ── Scroll reveal for testimonial block ── */
(function initTestiObserver() {
    const ts = document.getElementById('ts');
    if (!ts) return;
    try {
        new IntersectionObserver((entries, obs) => {
            if (!entries[0] || !entries[0].isIntersecting) return;
            const tsHeader = document.getElementById('tsHeader');
            const tsBody = document.getElementById('tsBody');
            if (tsHeader) tsHeader.classList.add('on');
            if (tsBody) setTimeout(() => tsBody.classList.add('on'), 180);
            obs.disconnect();
        }, { threshold: 0.1 }).observe(ts);
    } catch (e) {
        // Fallback for older browsers
    }
})();

/* ── Dynamic Case Study Content Hydration from Admin DB ── */
(function initCaseStudySync() {
    function formatImgUrl(url) {
        if (!url) return '';
        if (url.startsWith('/') || url.startsWith('http')) return url;
        return '/' + url;
    }

    function syncCaseStudy() {
        const rawPath = window.location.pathname;
        const pageFile = rawPath.split('/').pop().toLowerCase();
        if (!pageFile) return;

        // Fetch matching portfolio project by page url or slug
        fetch('/api/portfolio?url=' + encodeURIComponent(pageFile) + '&_=' + Date.now())
            .then(res => {
                if (!res.ok) {
                    // Try getting all projects and matching by project_url
                    return fetch('/api/portfolio?_=' + Date.now()).then(r => r.json()).then(data => {
                        if (data && data.data) {
                            return {
                                success: true,
                                data: data.data.find(p => (p.project_url && p.project_url.toLowerCase().includes(pageFile)) || (p.slug && pageFile.includes(p.slug)))
                            };
                        }
                        return { success: false };
                    });
                }
                return res.json();
            })
            .then(json => {
                if (!json || !json.success || !json.data) return;
                const project = json.data;

                // 1. Update Title & Heading
                if (project.title) {
                    document.title = project.title + ' — Storyworks Studio';
                    const aboutHead = document.querySelector('.case-content_head .work-content_heading') 
                                   || document.querySelector('.case-content_final-head .work-content_heading');
                    if (aboutHead) {
                        aboutHead.textContent = 'About ' + (project.client || project.title);
                    }
                }

                // 2. Update Hero Banner Image
                if (project.banner_image) {
                    const heroImg = document.querySelector('.work-header_img');
                    if (heroImg) {
                        heroImg.src = formatImgUrl(project.banner_image);
                    }
                }

                // 3. Update About / Overview Text
                const aboutText = project.full_desc || project.short_desc;
                if (aboutText) {
                    const aboutP = document.querySelector('.case-content_final p');
                    if (aboutP) {
                        aboutP.textContent = aboutText;
                    }
                }

                // 4. Update Approach Photo
                if (project.approach_image) {
                    const approachImg = document.querySelector('.case-content_image');
                    if (approachImg) {
                        approachImg.src = formatImgUrl(project.approach_image);
                    }
                }

                // 5. Update Approach Narrative Text
                if (project.approach) {
                    const approachP = document.querySelector('.work-content_content p');
                    if (approachP) {
                        approachP.textContent = project.approach;
                    }
                }

                // 6. Update Middle Banner Image
                if (project.middle_banner_image) {
                    const midImg = document.querySelector('.work-final_img') 
                                || document.querySelector('.work-final_img-wrap img');
                    if (midImg) {
                        midImg.src = formatImgUrl(project.middle_banner_image);
                    }
                }

                // 7. Update Testimonial Quote if available
                if (project.quote) {
                    const quoteBody = document.querySelector('.testimonial-content .t-body');
                    if (quoteBody) {
                        quoteBody.textContent = project.quote;
                    }
                }
            })
            .catch(err => {
                console.warn('Case study dynamic sync notice:', err);
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', syncCaseStudy);
    } else {
        syncCaseStudy();
    }
})();
