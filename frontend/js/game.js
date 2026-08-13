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
  document.getElementById("move-count") || document.getElementById("moves");

const fetchButton =
  document.getElementById("fetch-button");

const positiveRewardButton =
  document.getElementById("positive-reward") || document.getElementById("reward-positive");

const negativeRewardButton =
  document.getElementById("negative-reward") || document.getElementById("reward-negative");

const resetAllButton =
  document.getElementById("reset-all");

const resetEnvironmentButton =
  document.getElementById("reset-environment");

const resetTrainingButton =
  document.getElementById("reset-training");

const statusMessage =
  document.getElementById("status-message") || document.getElementById("game-status");

const rewardPopup =
  document.getElementById("reward-popup");


// ============================================
// CONSTANTS
// ============================================

const GRID_SIZE = 5;

const STEP_DELAY = 500;


// ============================================
// POSITION PARSER
// ============================================

function parsePos(pos) {
  if (!pos) return null;
  if (Array.isArray(pos)) {
    // Backend returns [row, col] -> row is y (0..4), col is x (0..4)
    return { x: pos[1], y: pos[0] };
  }
  if (typeof pos === "object") {
    const x = pos.x !== undefined ? pos.x : pos.col;
    const y = pos.y !== undefined ? pos.y : pos.row;
    return { x, y };
  }
  return null;
}


// ============================================
// INITIALIZE GAME
// ============================================

async function initializeGame() {

  try {

    const data = await createGame();

    updateGameState(data);

    render();

    setStatus("The dog is ready");

  } catch (error) {

    console.error("Failed to initialize game:", error);

    setStatus("Unable to connect to game backend.");
  }
}


// ============================================
// UPDATE GAME STATE
// ============================================

function updateGameState(data) {

  if (!data) return;

  const dog = data.dog_position || data.dogPos;
  if (dog) {
    gameState.dogPos = parsePos(dog);
  }

  const bone = data.bone_position || data.bonePos;
  if (bone) {
    gameState.bonePos = parsePos(bone);
  }

  const home = data.home_position || data.homePos;
  if (home) {
    gameState.homePos = parsePos(home);
  }

  const hasBone = data.has_bone !== undefined ? data.has_bone : data.hasBone;
  if (typeof hasBone === "boolean") {
    gameState.hasBone = hasBone;
  }

  const score = data.score !== undefined ? data.score : data.score;
  if (typeof score === "number") {
    gameState.score = score;
  }

  const moveCount = data.move_count !== undefined ? data.move_count : data.moveCount;
  if (typeof moveCount === "number") {
    gameState.moveCount = moveCount;
  }
}


// ============================================
// RENDER EVERYTHING
// ============================================

function render() {

  renderGrid();

  if (scoreElement) scoreElement.textContent = gameState.score;

  if (moveCountElement) moveCountElement.textContent = gameState.moveCount;

  updateRewardButtons();
}

//=============================================
// HOME BUTTON
//=============================================

const homeButton = document.getElementById("home-button");

if (homeButton) {
  homeButton.addEventListener("click", () => {
      window.location.href = "index.html";
  });
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
    gameState.dogPos &&
    gameState.dogPos.x === x &&
    gameState.dogPos.y === y
  ) {
    const dog = document.createElement("img");
    dog.src = "assets/dog.svg";
    dog.alt = "Dog";
    dog.className = "cell-asset dog-asset";
    cell.appendChild(dog);
  }

  // Bone
  if (
    gameState.bonePos &&
    gameState.bonePos.x === x &&
    gameState.bonePos.y === y &&
    !gameState.hasBone
  ) {
    const bone = document.createElement("img");
    bone.src = "assets/bone.svg";
    bone.alt = "Bone";
    bone.className = "cell-asset bone-asset";
    cell.appendChild(bone);
  }

  // Home
  if (
    gameState.homePos &&
    gameState.homePos.x === x &&
    gameState.homePos.y === y
  ) {
    const home = document.createElement("img");
    home.src = "assets/dog-house.svg";
    home.alt = "Home";
    home.className = "cell-asset home-asset";
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

    if (response && response.steps) {
      await animateSteps(response.steps);
    }

    gameState.awaitingUserReward =
      response.awaiting_user_reward ?? response.awaitingUserReward ?? true;

    gameState.isAnimating = false;

    updateRewardButtons();

    if (gameState.awaitingUserReward) {
      setStatus("Was that a good move?");
    } else {
      setStatus("The dog is ready");
    }

  } catch (error) {

    console.error("Fetch failed:", error);

    gameState.isAnimating = false;

    fetchButton.disabled = false;

    setStatus("Fetch request failed.");
  }
}


// ============================================
// ANIMATE STEPS
// ============================================

async function animateSteps(steps) {

  for (const step of steps) {

    if (step.pos) {
      gameState.dogPos = parsePos(step.pos);
    }

    if (typeof step.reward === "number" && step.reward !== 0) {
      gameState.score += step.reward;
    }

    gameState.moveCount += 1;

    render();

    if (step.reward === 10 || step.reward === 5) {
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

    console.error("Reward failed:", error);

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

  if (positiveRewardButton) positiveRewardButton.disabled = !enabled;

  if (negativeRewardButton) negativeRewardButton.disabled = !enabled;

  if (
    !gameState.awaitingUserReward &&
    !gameState.isAnimating &&
    fetchButton
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

    console.error("Reset failed:", error);

    setStatus("Could not reset the game.");
  }
}


// ============================================
// +10 POPUP
// ============================================

function showRewardPopup() {

  if (!rewardPopup) return;

  rewardPopup.hidden = false;

  setTimeout(() => {

    rewardPopup.hidden = true;

  }, 900);
}


// ============================================
// STATUS
// ============================================

function setStatus(message) {

  if (statusMessage) statusMessage.textContent = message;
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

if (fetchButton) {
  fetchButton.addEventListener(
    "click",
    handleFetch
  );
}

if (positiveRewardButton) {
  positiveRewardButton.addEventListener(
    "click",
    () => handleUserReward(1)
  );
}

if (negativeRewardButton) {
  negativeRewardButton.addEventListener(
    "click",
    () => handleUserReward(-1)
  );
}

if (resetAllButton) {
  resetAllButton.addEventListener(
    "click",
    () => handleReset("all")
  );
}

if (resetEnvironmentButton) {
  resetEnvironmentButton.addEventListener(
    "click",
    () => handleReset("env")
  );
}

if (resetTrainingButton) {
  resetTrainingButton.addEventListener(
    "click",
    () => handleReset("train")
  );
}


// ============================================
// START
// ============================================

initializeGame();