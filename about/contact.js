// Storyworks Contact Page Scripts (Scroll reveal & FAQ Accordion)

/* ── Scroll reveal ── */
const revEls = [
  document.getElementById("formCard"),
  document.getElementById("sidebar"),
  document.getElementById("mapStrip"),
  document.getElementById("faqSection"),
];
const revIO = new IntersectionObserver(
  (entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add("on");
        revIO.unobserve(e.target);
      }
    });
  },
  { threshold: 0.08 }
);
revEls.forEach((el) => {
  if (el) revIO.observe(el);
});

/* ── FAQ accordion ── */
document.querySelectorAll(".faq-q").forEach((btn) => {
  btn.addEventListener("click", () => {
    const item = btn.closest(".faq-item");
    if (!item) return;
    const isOpen = item.classList.contains("open");
    document.querySelectorAll(".faq-item").forEach((i) => i.classList.remove("open"));
    if (!isOpen) item.classList.add("open");
  });
});
