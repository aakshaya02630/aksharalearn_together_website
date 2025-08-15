document.addEventListener("DOMContentLoaded", function () {
  const images = [
    {
      src: "/static/images/akshara2.jpeg",
      text: "WELCOME TO AKSHARA INSTITUTION"
    },
    {
      src: "/static/images/akshara1.jpeg",
      text: "Start Your SSC Preparation Today"
    }
  ];

  let currentIndex = 0;
  const slider = document.getElementById("slider");
  const bannerText = document.getElementById("banner-text");

  function updateSlide() {
    slider.style.backgroundImage = `url('${images[currentIndex].src}')`;
    bannerText.textContent = images[currentIndex].text;

    slider.classList.remove("fade-in");
    void slider.offsetWidth; // trigger reflow
    slider.classList.add("fade-in");
  }

  updateSlide(); // Initial load

  setInterval(() => {
    currentIndex = (currentIndex + 1) % images.length;
    updateSlide();
  }, 4000);
});
