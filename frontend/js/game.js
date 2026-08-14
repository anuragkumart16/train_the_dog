const GRID_SIZE = 5;
const STEP_DELAY_MS = 300;

const state = {
  dogPos: { x: 0, y: 0 },
  bonePos: { x: 0, y: 0 },
  homePos: { x: 0, y: 0 },
  hasBone: false,
  score: 0,
  moveCount: 0,
  awaitingUserReward: false,
  busy: false,
  operationId: 0
};

const gridEl = document.getElementById("game-grid");
const scoreEl = document.getElementById("score-value");
const movesEl = document.getElementById("moves-value");
const statusEl = document.getElementById("status-message");
const fetchButton = document.getElementById("fetch-button");
const rewardPositiveButton = document.getElementById("reward-positive");
const rewardNegativeButton = document.getElementById("reward-negative");
const homeButton = document.getElementById("home-button");
const resetEnvButton = document.getElementById("reset-env");
const resetTrainButton = document.getElementById("reset-train");
const resetAllButton = document.getElementById("reset-all");
const congratsPopup = document.getElementById("congrats-popup");
const congratsCloseButton = document.getElementById("congrats-close");

const assets = {
  dog: "assets/dog.svg",
  bone: "assets/bone.svg",
  home: "assets/dog-house.svg"
};

function samePosition(a, b) {
  return a && b && a.x === b.x && a.y === b.y;
}

function updateState(nextState) {
  if (!nextState) {
    return;
  }

  state.dogPos = nextState.dogPos || state.dogPos;
  state.bonePos = nextState.bonePos || state.bonePos;
  state.homePos = nextState.homePos || state.homePos;
  state.hasBone = Boolean(nextState.hasBone);
  state.score = Number(nextState.score || 0);
  state.moveCount = Number(nextState.moveCount || 0);
}

function setStatus(message) {
  statusEl.textContent = message;
}

function setControls() {
  fetchButton.disabled = state.busy || state.awaitingUserReward;
  rewardPositiveButton.disabled = state.busy || !state.awaitingUserReward;
  rewardNegativeButton.disabled = state.busy || !state.awaitingUserReward;
  resetEnvButton.disabled = state.busy;
  resetTrainButton.disabled = state.busy;
  resetAllButton.disabled = state.busy;
}

function beginOperation() {
  state.operationId += 1;
  state.busy = true;
  render();
  return state.operationId;
}

function isCurrentOperation(operationId) {
  return operationId === state.operationId;
}

function finishOperation(operationId) {
  if (!isCurrentOperation(operationId)) {
    return;
  }

  state.busy = false;
  render();
}

function hideCongratulations() {
  congratsPopup.hidden = true;
}

function showCongratulations() {
  congratsPopup.hidden = false;
}

function renderGrid() {
  gridEl.innerHTML = "";

  for (let y = 0; y < GRID_SIZE; y += 1) {
    for (let x = 0; x < GRID_SIZE; x += 1) {
      const cell = document.createElement("div");
      cell.className = "grid-cell";

      const pos = { x, y };

      if (samePosition(pos, state.homePos)) {
        const homeImg = document.createElement("img");
        homeImg.src = assets.home;
        homeImg.alt = "Home";
        cell.appendChild(homeImg);
      }

      if (!state.hasBone && samePosition(pos, state.bonePos)) {
        const boneImg = document.createElement("img");
        boneImg.src = assets.bone;
        boneImg.alt = "Bone";
        cell.appendChild(boneImg);
      }

      if (samePosition(pos, state.dogPos)) {
        if (state.hasBone) {
          const carriedPack = document.createElement("div");
          carriedPack.className = "carried-pack";

          const dogImg = document.createElement("img");
          dogImg.src = assets.dog;
          dogImg.alt = "Dog";
          dogImg.className = "carried-dog";
          carriedPack.appendChild(dogImg);

          const carriedBoneImg = document.createElement("img");
          carriedBoneImg.src = assets.bone;
          carriedBoneImg.alt = "Bone";
          carriedBoneImg.className = "carried-bone";
          carriedPack.appendChild(carriedBoneImg);

          cell.appendChild(carriedPack);
        } else {
          const dogImg = document.createElement("img");
          dogImg.src = assets.dog;
          dogImg.alt = "Dog";
          cell.appendChild(dogImg);
        }
      }

      gridEl.appendChild(cell);
    }
  }

  scoreEl.textContent = state.score;
  movesEl.textContent = state.moveCount;
}

function render() {
  renderGrid();
  setControls();
}

function wait(ms) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

async function playSteps(steps, operationId) {
  for (const step of steps) {
    if (!isCurrentOperation(operationId)) {
      return;
    }

    if (step.pos) {
      state.dogPos = step.pos;
      if (step.bonePos) {
        state.bonePos = step.bonePos;
      }
      if (typeof step.carriedBone === "boolean") {
        state.hasBone = step.carriedBone;
      } else if (typeof step.hasBone === "boolean") {
        state.hasBone = step.hasBone;
      }
      if (typeof step.reward === "number") {
        state.score += step.reward;
      }
      state.moveCount += step.source === "automatic" ? 1 : 0;
      setStatus(`${step.source === "human" ? "Suggested" : "Auto"}: ${step.action}`);
      render();

      if (step.missionCompleted) {
        showCongratulations();
      }

      await wait(STEP_DELAY_MS);
    }
  }
}

async function loadGame() {
  const operationId = beginOperation();
  hideCongratulations();

  try {
    const game = await createGame();
    if (!isCurrentOperation(operationId)) {
      return;
    }
    updateState(game);
    state.awaitingUserReward = false;
    setStatus("Ready. Fetch a move sequence.");
  } catch (error) {
    if (isCurrentOperation(operationId)) {
      setStatus(error.message);
    }
  } finally {
    finishOperation(operationId);
  }
}

async function handleFetch() {
  if (state.busy || state.awaitingUserReward) {
    return;
  }

  const operationId = beginOperation();

  try {
    const response = await fetchMoves();
    if (!isCurrentOperation(operationId)) {
      return;
    }
    await playSteps(response.steps || [], operationId);
    if (!isCurrentOperation(operationId)) {
      return;
    }
    updateState(response);
    state.awaitingUserReward = Boolean(response.awaitingUserReward);
    if (response.congratulations || response.missionCompleted) {
      showCongratulations();
      setStatus("Home reached. The dog completed the delivery.");
    } else {
      setStatus(state.awaitingUserReward ? "Give feedback for the suggested move." : "Fetch again to continue.");
    }
  } catch (error) {
    if (isCurrentOperation(operationId)) {
      setStatus(error.message);
    }
  } finally {
    finishOperation(operationId);
  }
}

async function handleReward(value) {
  if (state.busy || !state.awaitingUserReward) {
    return;
  }

  const operationId = beginOperation();

  try {
    const response = await giveReward(value);
    if (!isCurrentOperation(operationId)) {
      return;
    }
    if (response.accepted) {
      updateState(response);
      state.awaitingUserReward = false;
      if (response.congratulations || response.missionCompleted) {
        showCongratulations();
        setStatus("Home reached. The dog completed the delivery.");
      } else {
        setStatus(value > 0 ? "Reward applied. The dog learned from that move." : "Penalty applied. The dog avoided that move.");
      }
    } else {
      setStatus("No pending move to reward.");
    }
  } catch (error) {
    if (isCurrentOperation(operationId)) {
      setStatus(error.message);
    }
  } finally {
    finishOperation(operationId);
  }
}

async function handleReset(type) {
  if (state.busy) {
    return;
  }

  const operationId = beginOperation();
  hideCongratulations();

  try {
    const response = await resetGame(type);
    if (!isCurrentOperation(operationId)) {
      return;
    }
    updateState(response);
    state.awaitingUserReward = false;
    setStatus("Reset complete.");
  } catch (error) {
    if (isCurrentOperation(operationId)) {
      setStatus(error.message);
    }
  } finally {
    finishOperation(operationId);
  }
}

fetchButton.addEventListener("click", handleFetch);
rewardPositiveButton.addEventListener("click", () => handleReward(1));
rewardNegativeButton.addEventListener("click", () => handleReward(-1));
resetEnvButton.addEventListener("click", () => handleReset("env"));
resetTrainButton.addEventListener("click", () => handleReset("train"));
resetAllButton.addEventListener("click", () => handleReset("all"));
congratsCloseButton.addEventListener("click", hideCongratulations);
homeButton.addEventListener("click", () => {
  window.location.href = "index.html";
});

loadGame();
