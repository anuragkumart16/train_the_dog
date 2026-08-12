// ============================================
// GAME STATE
// ============================================

const gameState = {
  dogPos: { x: 0, y: 0 },
  bonePos: { x: 2, y: 3 },
  homePos: { x: 4, y: 4 },

  hasBone: false,

  score: 0,
  moveCount: 0,

  isAnimating: false,
  awaitingUserReward: false
};


// ============================================
// DOM ELEMENTS
// ============================================

const gameGrid = document.getElementById("game-grid");

const scoreElement = document.getElementById("score");

const moveCountElement =
  document.getElementById("move-count");

const fetchButton =
  document.getElementById("fetch-button");

const positiveRewardButton =
  document.getElementById("positive-reward");

const negativeRewardButton =
  document.getElementById("negative-reward");

const resetAllButton =
  document.getElementById("reset-all");

const resetEnvironmentButton =
  document.getElementById("reset-environment");

const resetTrainingButton =
  document.getElementById("reset-training");

const statusMessage =
  document.getElementById("status-message");

const rewardPopup =
  document.getElementById("reward-popup");


// ============================================
// CONSTANTS
// ============================================

const GRID_SIZE = 5;

const STEP_DELAY = 500;


// ============================================
// INITIALIZE GAME
// ============================================

async function initializeGame() {

  try {

    const data = await createGame();

    updateGameState(data);

    render();

    setStatus("Ready to train the dog.");

  } catch (error) {

    console.error(error);

    setStatus("Unable to start the game.");
  }
}


// ============================================
// UPDATE GAME STATE
// ============================================

function updateGameState(data) {

  if (data.dogPos) {
    gameState.dogPos = { ...data.dogPos };
  }

  if (data.bonePos) {
    gameState.bonePos = { ...data.bonePos };
  }

  if (data.homePos) {
    gameState.homePos = { ...data.homePos };
  }

  if (typeof data.hasBone === "boolean") {
    gameState.hasBone = data.hasBone;
  }

  if (typeof data.score === "number") {
    gameState.score = data.score;
  }

  if (typeof data.moveCount === "number") {
    gameState.moveCount = data.moveCount;
  }
}


// ============================================
// RENDER EVERYTHING
// ============================================

function render() {

  renderGrid();

  scoreElement.textContent = gameState.score;

  moveCountElement.textContent =
    gameState.moveCount;

  updateRewardButtons();
}


// ============================================
// RENDER GRID
// ============================================

function renderGrid() {

  gameGrid.innerHTML = "";

  for (let y = 0; y < GRID_SIZE; y++) {

    for (let x = 0; x < GRID_SIZE; x++) {

      const cell = document.createElement("div");

      cell.className = "grid-cell";

      cell.dataset.x = x;
      cell.dataset.y = y;

      renderCell(cell, x, y);

      gameGrid.appendChild(cell);
    }
  }
}


// ============================================
// RENDER INDIVIDUAL CELL
// ============================================

function renderCell(cell, x, y) {

  // Dog
  if (
    gameState.dogPos.x === x &&
    gameState.dogPos.y === y
  ) {

    const dog = document.createElement("div");

    dog.textContent = "🐶";

    dog.style.fontSize = "32px";

    cell.appendChild(dog);
  }


  // Bone
  if (
    gameState.bonePos.x === x &&
    gameState.bonePos.y === y &&
    !gameState.hasBone
  ) {

    const bone = document.createElement("div");

    bone.textContent = "🦴";

    bone.style.fontSize = "28px";

    cell.appendChild(bone);
  }


  // Home
  if (
    gameState.homePos.x === x &&
    gameState.homePos.y === y
  ) {

    const home = document.createElement("div");

    home.textContent = "🏠";

    home.style.fontSize = "28px";

    cell.appendChild(home);
  }
}


// ============================================
// FETCH
// ============================================

async function handleFetch() {

  if (
    gameState.isAnimating ||
    gameState.awaitingUserReward
  ) {
    return;
  }

  gameState.isAnimating = true;

  fetchButton.disabled = true;

  setStatus("The dog is deciding...");

  try {

    const response = await fetchMoves();

    await animateSteps(response.steps);

    gameState.moveCount += response.steps.length;

    gameState.awaitingUserReward =
      response.awaitingUserReward;

    gameState.isAnimating = false;

    updateRewardButtons();

    if (gameState.awaitingUserReward) {

      setStatus(
        "Was that a good move?"
      );
    }

  } catch (error) {

    console.error(error);

    gameState.isAnimating = false;

    fetchButton.disabled = false;

    setStatus("Something went wrong.");
  }
}


// ============================================
// ANIMATE STEPS
// ============================================

async function animateSteps(steps) {

  for (const step of steps) {

    gameState.dogPos = {
      ...step.pos
    };

    if (step.reward !== null) {
      gameState.score += step.reward;
    }

    render();

    if (step.reward === 10) {

      showRewardPopup();
    }

    await wait(STEP_DELAY);
  }
}


// ============================================
// USER REWARD
// ============================================

async function handleUserReward(value) {

  if (
    !gameState.awaitingUserReward ||
    gameState.isAnimating
  ) {
    return;
  }

  positiveRewardButton.disabled = true;

  negativeRewardButton.disabled = true;

  setStatus("Updating the dog's training...");

  try {

    const response =
      await giveReward(value);

    updateGameState(response);

    gameState.awaitingUserReward = false;

    fetchButton.disabled = false;

    render();

    setStatus(
      value === 1
        ? "Good move. The dog learned from it."
        : "The dog received a penalty."
    );

  } catch (error) {

    console.error(error);

    updateRewardButtons();

    setStatus(
      "Could not submit the reward."
    );
  }
}


// ============================================
// REWARD BUTTON STATE
// ============================================

function updateRewardButtons() {

  const enabled =
    gameState.awaitingUserReward &&
    !gameState.isAnimating;

  positiveRewardButton.disabled = !enabled;

  negativeRewardButton.disabled = !enabled;

  if (
    !gameState.awaitingUserReward &&
    !gameState.isAnimating
  ) {
    fetchButton.disabled = false;
  }
}


// ============================================
// RESET
// ============================================

async function handleReset(type) {

  if (gameState.isAnimating) {
    return;
  }

  try {

    const response =
      await resetGame(type);

    updateGameState(response);

    gameState.awaitingUserReward = false;

    gameState.isAnimating = false;

    render();

    fetchButton.disabled = false;

    setStatus("Game reset.");

  } catch (error) {

    console.error(error);

    setStatus("Could not reset the game.");
  }
}


// ============================================
// +10 POPUP
// ============================================

function showRewardPopup() {

  rewardPopup.hidden = false;

  setTimeout(() => {

    rewardPopup.hidden = true;

  }, 900);
}


// ============================================
// STATUS
// ============================================

function setStatus(message) {

  statusMessage.textContent = message;
}


// ============================================
// WAIT
// ============================================

function wait(milliseconds) {

  return new Promise(resolve => {

    setTimeout(resolve, milliseconds);

  });
}


// ============================================
// EVENT LISTENERS
// ============================================

fetchButton.addEventListener(
  "click",
  handleFetch
);

positiveRewardButton.addEventListener(
  "click",
  () => handleUserReward(1)
);

negativeRewardButton.addEventListener(
  "click",
  () => handleUserReward(-1)
);

resetAllButton.addEventListener(
  "click",
  () => handleReset("all")
);

resetEnvironmentButton.addEventListener(
  "click",
  () => handleReset("env")
);

resetTrainingButton.addEventListener(
  "click",
  () => handleReset("train")
);


// ============================================
// START
// ============================================

initializeGame();