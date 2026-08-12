// ============================================
// GAME CONFIGURATION
// ============================================

const STEPS_PER_FETCH = 2;


// ============================================
// MOCK GAME STATE
// ============================================

const MOCK_GAME_STATE = {
    dogPos: { x: 0, y: 0 },

    bonePos: { x: 2, y: 3 },

    homePos: { x: 4, y: 4 },

    hasBone: false,

    score: 0,

    moveCount: 0
};


// ============================================
// GET CURRENT STATE
// ============================================

function getMockGameState() {

    return {
        dogPos: { ...MOCK_GAME_STATE.dogPos },

        bonePos: { ...MOCK_GAME_STATE.bonePos },

        homePos: { ...MOCK_GAME_STATE.homePos },

        hasBone: MOCK_GAME_STATE.hasBone,

        score: MOCK_GAME_STATE.score,

        moveCount: MOCK_GAME_STATE.moveCount
    };
}


// ============================================
// MOCK FETCH
// ============================================

function getMockFetchResponse() {

    const currentX = MOCK_GAME_STATE.dogPos.x;
    const currentY = MOCK_GAME_STATE.dogPos.y;

    // ----------------------------------------
    // Step 1
    // ----------------------------------------

    const step1 = {
        x: Math.min(currentX + 1, 4),
        y: currentY
    };


    // ----------------------------------------
    // Step 2
    // ----------------------------------------

    const step2 = {
        x: step1.x,
        y: Math.min(step1.y + 1, 4)
    };


    // ----------------------------------------
    // System updates its internal state
    // ----------------------------------------

    MOCK_GAME_STATE.dogPos = { ...step2 };

    MOCK_GAME_STATE.moveCount += 2;


    return {

        steps: [

            {
                pos: { ...step1 },

                action: "right",

                reward: 1,

                source: "system"
            },

            {
                pos: { ...step2 },

                action: "down",

                reward: null,

                source: "user_pending"
            }

        ],

        awaitingUserReward: true
    };
}


// ============================================
// USER REWARD
// ============================================

function getMockRewardResponse(value) {

    // Only the score changes.
    // Dog position and move count stay exactly
    // where they were after the fetch.

    MOCK_GAME_STATE.score += value;

    return {
        accepted: true,

        dogPos: {
            ...MOCK_GAME_STATE.dogPos
        },

        hasBone: MOCK_GAME_STATE.hasBone,

        score: MOCK_GAME_STATE.score,

        moveCount: MOCK_GAME_STATE.moveCount
    };
}


// ============================================
// RESET
// ============================================

function getMockResetResponse(type) {

    MOCK_GAME_STATE.dogPos = {
        x: 0,
        y: 0
    };

    MOCK_GAME_STATE.bonePos = {
        x: 3,
        y: 1
    };

    MOCK_GAME_STATE.homePos = {
        x: 4,
        y: 4
    };

    MOCK_GAME_STATE.hasBone = false;

    MOCK_GAME_STATE.score = 0;

    MOCK_GAME_STATE.moveCount = 0;


    return getMockGameState();
}