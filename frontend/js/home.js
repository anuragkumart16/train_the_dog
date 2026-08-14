const startButton = document.getElementById("start-button");
const docsButton = document.getElementById("docs-button");

if (startButton) {
  startButton.addEventListener("click", () => {
    window.location.href = "game.html";
  });
}

if (docsButton) {
  docsButton.addEventListener("click", () => {
    window.location.href = "../architecture.md";
  });
}
