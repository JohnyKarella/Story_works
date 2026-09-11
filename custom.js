// Homepage
// portfolio
$(document).ready(function () {
	$("[unique-script-id='w-w-dm-id'] .btn-box").click(function () {
		$(this).parent().children(".overlay").show();
	});
	$("[unique-script-id='w-w-dm-id'] .close").click(function () {
		$(".overlay").hide();
	});
	$("[unique-script-id='w-w-dm-id'] .list").click(function () {
		const value = $(this).attr('data-filter');
		if (value == 'all') {
			$("[unique-script-id='w-w-dm-id'] .squareImg").show('1000');
		} else {
			$("[unique-script-id='w-w-dm-id'] .squareImg").not('.' + value).hide('1000');
			$("[unique-script-id='w-w-dm-id'] .squareImg").filter('.' + value).show('1000');
		}
	})
	$("[unique-script-id='w-w-dm-id'] .list").click(function () {
		$(this).addClass('active').siblings().removeClass('active');
	})
})
// Robot
// Extraa
// ♡ This pen is a remix of https://codepen.io/jh3y/pen/jORQyzZ by @jh3y
const UPDATE = ({ x, y }) => {
	const xNorm = (x / window.innerWidth - 0.5) * 2;
	const yNorm = (y / window.innerHeight - 0.5) * 2;
	document.documentElement.style.setProperty("--x", xNorm);
	document.documentElement.style.setProperty("--y", yNorm);
};
window.addEventListener("mousemove", UPDATE);
const handleOrientation = ({ beta, gamma }) => {
	const isLandscape = window.matchMedia("(orientation: landscape)").matches;
	const xVal = Math.max(
		-1,
		Math.min(1, isLandscape ? (beta || 0) / 45 : (gamma || 0) / 45)
	);
	const yVal = Math.max(
		-1,
		Math.min(1, isLandscape ? Math.abs(gamma || 0) / 45 : (beta || 0) / 45)
	);
	document.documentElement.style.setProperty("--x", xVal);
	document.documentElement.style.setProperty("--y", yVal);
};
const START = () => {
	if (DeviceOrientationEvent?.requestPermission) {
		DeviceOrientationEvent.requestPermission().then((result) => {
			if (result === "granted") {
				window.addEventListener("deviceorientation", handleOrientation);
			}
		});
	} else {
		window.addEventListener("deviceorientation", handleOrientation);
	}
};
document.body.addEventListener("click", START, { once: true });
// Services
// Track mouse movement for glow effect
document.addEventListener('DOMContentLoaded', function () {
	const cards = document.querySelectorAll('.service-card');
	cards.forEach(card => {
		card.addEventListener('mousemove', function (e) {
			const rect = card.getBoundingClientRect();
			const x = ((e.clientX - rect.left) / rect.width) * 100;
			const y = ((e.clientY - rect.top) / rect.height) * 100;
			card.style.setProperty('--x', x + '%');
			card.style.setProperty('--y', y + '%');
		});
	});
});
// new portfolio
// Portfolio Filtering Functionality
document.addEventListener('DOMContentLoaded', function () {
	const filterButtons = document.querySelectorAll('.filter-btn');
	const portfolioCards = document.querySelectorAll('.portfolio-card');
	filterButtons.forEach(button => {
		button.addEventListener('click', function () {
			const category = this.getAttribute('data-category');
			// Update active button
			filterButtons.forEach(btn => btn.classList.remove('active'));
			this.classList.add('active');
			// Filter cards
			portfolioCards.forEach((card, index) => {
				const cardCategory = card.getAttribute('data-category');
				if (category === 'all' || cardCategory === category) {
					card.classList.remove('hidden');
					card.style.animation = 'none';
					setTimeout(() => {
						card.style.animation = `cardReveal 0.6s ease-out ${index * 0.1}s forwards`;
					}, 10);
				} else {
					card.classList.add('hidden');
				}
			});
		});
	});
	// Add hover effect tracking for cards
	const cards = document.querySelectorAll('.portfolio-card');
	cards.forEach(card => {
		card.addEventListener('mouseenter', function () {
			this.style.zIndex = '10';
		});
		card.addEventListener('mouseleave', function () {
			this.style.zIndex = '1';
		});
	});
});
// New banner
// ═══════════════════════════════════════════════════════════════
// UNIVERSAL TERMS & CONDITIONS CLEAN WHITE MODAL
// Works consistently across ALL pages without page reloads/navigation
// ═══════════════════════════════════════════════════════════════
(function () {
  const termsModalHtml = `
  <div id="termsModal" class="terms-modal" style="display: none;" role="dialog" aria-modal="true" aria-labelledby="termsModalTitle" aria-hidden="true">
    <div class="terms-modal-backdrop" id="termsModalBackdrop"></div>
    <div class="terms-modal-dialog">
      <div class="terms-modal-header">
        <h2 id="termsModalTitle">Terms &amp; Conditions</h2>
        <button type="button" class="terms-modal-close" id="termsModalClose" aria-label="Close">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div class="terms-modal-body">
        <p class="terms-updated">Last updated: September 2026</p>
        <p class="terms-intro">
          Welcome to Storyworks, the digital storytelling and marketing studio of Sri Bhagyalakshmi Enterprises. By accessing or using this website, you agree to be bound by the following Terms &amp; Conditions. Please read them carefully before using our site or engaging our services.
        </p>
        <h3 class="terms-heading">1. Acceptance of Terms</h3>
        <p class="terms-text">
          By browsing this website, filling out a contact form, or otherwise engaging with our content, you confirm that you accept these Terms &amp; Conditions and agree to comply with them. If you do not agree with any part of these terms, please discontinue use of the website.
        </p>
        <h3 class="terms-heading">2. Use of the Website</h3>
        <p class="terms-text">
          This website and its content are intended to showcase our work, services, and brand stories. You agree to use the site only for lawful purposes and in a manner that does not infringe the rights of, or restrict or inhibit the use and enjoyment of the site by, any third party.
        </p>
        <h3 class="terms-heading">3. Intellectual Property</h3>
        <p class="terms-text">
          All content on this website — including but not limited to text, graphics, logos, images, videos, portfolio work, and page design — is the property of Storyworks / Sri Bhagyalakshmi Enterprises or its content partners and is protected by applicable intellectual property laws. No content may be reproduced, copied, or redistributed without prior written permission.
        </p>
        <h3 class="terms-heading">4. Our Services</h3>
        <p class="terms-text">
          Details of our services, portfolio, and case studies presented on this site are for informational purposes and do not constitute a binding offer. Actual scope of work, timelines, and deliverables for any engagement will be governed by a separate agreement or proposal signed between Storyworks and the client.
        </p>
        <h3 class="terms-heading">5. User Submissions</h3>
        <p class="terms-text">
          Any information you submit through our contact or enquiry forms (such as your name, email, or project details) will be used solely to respond to your enquiry and to communicate with you about our services. Please avoid submitting confidential or sensitive information through these forms.
        </p>
        <h3 class="terms-heading">6. Third-Party Links</h3>
        <p class="terms-text">
          Our website may contain links to third-party websites or social media platforms. We do not control and are not responsible for the content, policies, or practices of any third-party sites. Visiting these links is at your own discretion and risk.
        </p>
        <h3 class="terms-heading">7. Limitation of Liability</h3>
        <p class="terms-text">
          While we strive to keep information on this website accurate and up to date, Storyworks makes no warranties about the completeness or reliability of the content. We shall not be liable for any direct or indirect loss arising from the use of, or inability to use, this website.
        </p>
        <h3 class="terms-heading">8. Changes to These Terms</h3>
        <p class="terms-text">
          We may update these Terms &amp; Conditions from time to time to reflect changes in our practices or for legal or regulatory reasons. Continued use of the website after changes are posted constitutes your acceptance of the revised terms.
        </p>
        <h3 class="terms-heading">9. Governing Law</h3>
        <p class="terms-text">
          These Terms &amp; Conditions are governed by and construed in accordance with the laws of India, and any disputes arising from them shall be subject to the exclusive jurisdiction of the courts having competent authority.
        </p>
        <h3 class="terms-heading">10. Contact Us</h3>
        <p class="terms-text">
          If you have any questions about these Terms &amp; Conditions, please reach out to us through the contact details listed on our <a href="contact.html" class="terms-link">Contact page</a>.
        </p>
      </div>
    </div>
  </div>`;
  function ensureTermsModal() {
    let modal = document.getElementById("termsModal");
    if (!modal) {
      const container = document.createElement("div");
      container.innerHTML = termsModalHtml.trim();
      modal = container.firstElementChild;
      document.body.appendChild(modal);
    }
    return modal;
  }
  function openTerms(e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    const modal = ensureTermsModal();
    if (!modal) return;
    modal.classList.add("active");
    modal.style.display = "flex";
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }
  function closeTerms(e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    const modal = document.getElementById("termsModal");
    if (!modal) return;
    modal.classList.remove("active");
    modal.style.display = "none";
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if (window.location.hash === "#terms" || window.location.hash === "#termsModal") {
      try {
        history.replaceState(null, document.title, window.location.pathname + window.location.search);
      } catch (err) {}
    }
  }
  function initTermsModal() {
    ensureTermsModal();
    // Event delegation on document to catch all terms link clicks
    document.addEventListener("click", function (e) {
      // Check close button or backdrop
      if (e.target.closest("#termsModalClose") || e.target.closest("#termsModalBackdrop") || e.target.closest("#termsModalAgreeBtn")) {
        closeTerms(e);
        return;
      }
      // Check terms trigger links
      const link = e.target.closest("a");
      if (!link) return;
      const href = (link.getAttribute("href") || "").trim();
      const id = link.getAttribute("id") || "";
      const text = (link.textContent || "").trim().toLowerCase();
      const isTermsLink =
        id === "footerTermsLink" ||
        href === "#termsModal" ||
        href === "#terms" ||
        href === "terms.html" ||
        href.endsWith("/terms.html") ||
        href.endsWith("terms.html") ||
        ((link.classList.contains("footer_template-link") || link.classList.contains("terms-trigger")) && text.includes("terms"));
      if (isTermsLink) {
        openTerms(e);
      }
    });
    // Close on Escape key
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        const modal = document.getElementById("termsModal");
        if (modal && (modal.classList.contains("active") || modal.style.display === "flex")) {
          closeTerms(e);
        }
      }
    });
    // Check URL hash on initial load
    if (window.location.hash === "#terms" || window.location.hash === "#termsModal") {
      openTerms();
    }
    // Also listen to hashchange
    window.addEventListener("hashchange", function () {
      if (window.location.hash === "#terms" || window.location.hash === "#termsModal") {
        openTerms();
      }
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTermsModal);
  } else {
    initTermsModal();
  }
})();
