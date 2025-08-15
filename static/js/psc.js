document.addEventListener("DOMContentLoaded", function () {
  feather.replace();

  function showOnlySection(sectionId) {
    document.querySelectorAll(".content-section").forEach(sec => {
      sec.style.display = "none";
    });
    const active = document.getElementById(sectionId);
    if (active) active.style.display = "block";
  }

  const params = new URLSearchParams(window.location.search);
  const section = params.get("section") || "video";
  showOnlySection(section);
});
