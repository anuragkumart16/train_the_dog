// ============================================
// HOME PAGE
// ============================================

const startButton = document.getElementById("start-button");
const docsButton = document.getElementById("docs-button");

startButton.addEventListener("click", () => {
    window.location.href = "game.html";
});

docsButton.addEventListener("click", () => {
    window.open(
        "https://docs.google.com/document/d/1pyXg_dKLyk26LyDn7O-QKh3EKQULHlE4Bdds7uFWT3Y/edit?tab=t.ppqcac8huhsl#heading=h.rdcxejj68dcd",
        "_blank",
        "noopener,noreferrer"
    );
});