// Services
const pToggle = document.getElementById('pricingToggle');
let isAnnual = false;
if (pToggle) {
    pToggle.addEventListener('click', () => {
    isAnnual = !isAnnual;
    pToggle.classList.toggle('on', isAnnual);
    document.querySelectorAll('.pc-price').forEach(container => {
        const v = container.querySelector('.price-val');
        const period = container.querySelector('.period');
        // Skip "Custom" price cards or cards without data attributes
        if (!v || !v.dataset.monthly) return;
        // Visual transition: fade out
        v.style.opacity = '0';
        setTimeout(() => {
            // 1. Update the main price
            v.textContent = isAnnual ? v.dataset.annual : v.dataset.monthly;
            // 2. Handle the Strikethrough (the monthly price)
            let oldPriceLabel = container.querySelector('.old-price-strike');
            if (isAnnual) {
                // If it doesn't exist, create it
                if (!oldPriceLabel) {
                    oldPriceLabel = document.createElement('del');
                    oldPriceLabel.className = 'old-price-strike';
                    container.appendChild(oldPriceLabel);
                }
                oldPriceLabel.textContent = `₹${v.dataset.monthly}`;
                period.textContent = "/ mo*"; // Added asterisk for footnote
            } else {
                // Remove it when going back to monthly
                if (oldPriceLabel) oldPriceLabel.remove();
                period.textContent = "/ mo";
            }
            // Visual transition: fade in
            v.style.opacity = '1';
        }, 150);
    });
});
}
