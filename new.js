// port


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





// TEAMS
// Optional: Add click event to view profile buttons
document.querySelectorAll('.view-profile-btn').forEach(btn => {
  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    const memberName = this.closest('.team-member').querySelector('.member-name').textContent;
    console.log('View profile for:', memberName);
    // Add your profile viewing logic here
    alert('Opening profile for ' + memberName);
  });
});

// Optional: Add click event to social links
document.querySelectorAll('.social-link').forEach(link => {
  link.addEventListener('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    console.log('Social link clicked');
    // Add your social link logic here
  });
});



// Clients

new IntersectionObserver((entries, obs) => {
  if (entries[0].isIntersecting) {
    document.getElementById('logoHeader').classList.add('on');
    obs.disconnect();
  }
}, { threshold: 0.15 }).observe(document.getElementById('logoSection'));

/*
  TO USE YOUR OWN CLIENT LOGOS:
  Replace each <img src="data:image/svg+xml..."> with:
  <img src="path/to/your-logo.svg" alt="Client Name"/>
  or
  <img src="path/to/your-logo.png" alt="Client Name"/>
 
  Use PNG/SVG with transparent background.
  Remember to keep both COPY 1 and COPY 2 updated for seamless loop.
*/
