document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.getElementById("menu-btn");
  const mobileMenu = document.getElementById("mobile-menu");

  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener("click", () => {
      mobileMenu.classList.toggle("hidden");
    });
  }

  document.body.classList.add("transition-opacity", "duration-500", "opacity-0");

  window.addEventListener("load", () => {
    document.body.classList.remove("opacity-0");
    document.body.classList.add("opacity-100");
  });

  document.querySelectorAll("a.nav-link").forEach(link => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const href = this.getAttribute("href");
      document.body.classList.remove("opacity-100");
      document.body.classList.add("opacity-0");

      setTimeout(() => {
        window.location.href = href;
      }, 400);
    });
  });
});
