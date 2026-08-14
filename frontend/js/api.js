// ============================================
// API CONFIGURATION
// ============================================

// Change this to false when the FastAPI backend
// is ready and we want to use the real backend.

const USE_MOCK_DATA = false;

const API_BASE_URL = "http://localhost:8000";


// ============================================
// CREATE GAME
// ============================================

async function createGame() {

  if (USE_MOCK_DATA) {

    return getMockGameState();
  }

  const response = await fetch(
    `${API_BASE_URL}/game/new`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    }
  );

  if (!response.ok) {
    throw new Error("Failed to create game");
  }

  return await response.json();
}


// ============================================
// FETCH MOVES
// ============================================

async function fetchMoves() {

  if (USE_MOCK_DATA) {

    return getMockFetchResponse();
  }

  const response = await fetch(
    `${API_BASE_URL}/game/fetch`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      }
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch moves");
  }

  return await response.json();
}


// ============================================
// GIVE USER REWARD
// ============================================

async function giveReward(value) {

  if (value !== 1 && value !== -1) {
    throw new Error("Reward must be 1 or -1");
  }


  if (USE_MOCK_DATA) {

    return getMockRewardResponse(value);
  }


  const response = await fetch(
    `${API_BASE_URL}/game/reward`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        value: value
      })
    }
  );

  if (!response.ok) {
    throw new Error("Failed to submit reward");
  }

  return await response.json();
}


// ============================================
// RESET GAME
// ============================================

async function resetGame(type) {

  const validTypes = [
    "all",
    "env",
    "train"
  ];

  if (!validTypes.includes(type)) {
    throw new Error("Invalid reset type");
  }


  if (USE_MOCK_DATA) {

    return getMockResetResponse(type);
  }


  const response = await fetch(
    `${API_BASE_URL}/game/reset`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        type: type
      })
    }
  );

  if (!response.ok) {
    throw new Error("Failed to reset game");
  }

  return await response.json();
}