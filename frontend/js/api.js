const API_URL = "http://localhost:8000";

/* =========================
   API HELPER
========================= */

async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: options.method || "GET",
        headers: {
            "Content-Type": "application/json"
        },
        body: options.body
    });

    if (!response.ok) {
        const error = await response.text();
        throw new Error(`API ${response.status}: ${error}`);
    }

    return await response.json();
}


/* =========================
   START NEW GAME
========================= */

async function startGame() {
    try {
        const data = await apiRequest("/game/new", {
            method: "POST"
        });

        console.log("NEW GAME:", data);
        return data;

    } catch (error) {
        console.error("Failed to start game:", error);
        throw error;
    }
}
const createGame = startGame;


/* =========================
   FETCH / RUN AGENT
========================= */

async function fetchMove() {
    try {
        const data = await apiRequest("/game/fetch", {
            method: "POST"
        });

        console.log("FETCH:", data);
        return data;

    } catch (error) {
        console.error("Failed to fetch move:", error);
        throw error;
    }
}
const fetchMoves = fetchMove;


/* =========================
   GIVE REWARD
========================= */

async function sendReward(value) {
    if (value !== 1 && value !== -1) {
        throw new Error("Reward must be 1 or -1");
    }

    try {
        const data = await apiRequest("/game/reward", {
            method: "POST",
            body: JSON.stringify({
                value: value
            })
        });

        console.log("REWARD:", data);
        return data;

    } catch (error) {
        console.error("Failed to send reward:", error);
        throw error;
    }
}
const giveReward = sendReward;


/* =========================
   RESET GAME
========================= */

async function resetGame(type) {
    let endpoint = "/game/reset";
    if (type === "all") {
        endpoint = "/reset/all";
    } else if (type === "train" || type === "training") {
        endpoint = "/training/reset";
    }

    try {
        const data = await apiRequest(endpoint, {
            method: "POST"
        });

        console.log("RESET:", type, data);
        return data;

    } catch (error) {
        console.error("Failed to reset game:", error);
        throw error;
    }
}