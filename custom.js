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