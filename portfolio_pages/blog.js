// blog
// Portfolio service


  (function () {
    var head = document.getElementById('svHead');
    var cards = document.querySelectorAll('.sv-card');

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('on');
        io.unobserve(e.target);
      });
    }, { threshold: 0.1 });

    io.observe(head);
    cards.forEach(function (c, i) {
      c.style.transitionDelay = (i * 0.07) + 's';
      io.observe(c);
    });
  })();
