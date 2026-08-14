# Frontend Analysis - Train the Dog UI

## Overview
The frontend is a web-based interactive training interface where users can teach a reinforcement learning model (the dog) to fetch a bone and return home by providing rewards/penalties for good/bad moves.

---

## Files Structure

### 1. **index.html** - Home Page
- **Purpose**: Landing page
- **Key Elements**:
  - AIRIS Logo
  - Game Title: "Train the Dog"
  - Subtitle: "Teach a dog to find a bone and return home using reinforcement learning"
  - "NEW GAME" button → redirects to `game.html`
  - "Read docs" button → opens external documentation
- **Script**: `js/home.js`

---

### 2. **game.html** - Main Game Interface
- **Layout**: Split screen design
  
#### Left Side: Game Grid
- **Grid Component**: `id="game-grid"` - 5×5 interactive grid
- **Visual Elements**:
  - 🐕 Dog (SVG asset) - controllable agent
  - 🦴 Bone (SVG asset) - target object
  - 🏠 Dog House (SVG asset) - home base
- **Home Button**: Navigate back to index.html

#### Right Side: Control Panel
**Stats Section**:
- SCORE: Current game score (updated with rewards)
- MOVES: Move counter

**FETCH Button**: 
- Triggers the dog's next action sequence
- Makes 4 automatic moves + 1 pending action waiting for user feedback

**Reward Section**:
- Question: "Was that a good move?"
- Two buttons (disabled until action is pending):
  - **+1 Button**: User rewards good behavior
  - **-1 Button**: User penalizes bad behavior

**Status Message**: 
- Real-time feedback to user
- Shows: "Ready to train", "The dog is deciding...", "Was that a good move?", etc.

**Reset Controls**:
- **Reset All**: Clear game state + reset Q-table to baseline
- **Reset Environment**: Reset dog/bone/home positions but keep Q-table
- **Reset Training**: Reset Q-table to baseline, keep environment

---

## UI Workflow

### Game Flow
1. **User clicks "NEW GAME"**
   - Page transitions to `game.html`
   - Backend creates new game (random positions for dog, bone, home)
   - Grid renders with current positions

2. **User clicks "FETCH"**
   - Dog makes 4 automatic moves (using Q-learning best action)
   - Each move is animated on the grid (500ms delay between steps)
   - 5th move is shown but awaits user feedback
   - "+1" and "-1" reward buttons become enabled

3. **User Provides Reward**
   - User clicks "+1" (good move) or "-1" (bad move)
   - Reward is sent to backend
   - Q-table is updated with the reward
   - Dog's position is finalized
   - Score is updated
   - Reward buttons become disabled
   - FETCH button re-enables
   - Status shows feedback

4. **User Continues Training**
   - Repeats FETCH → Reward cycle
   - Each cycle trains the model
   - Over time, Q-table improves

### Reset Scenarios
- **Reset All**: Starts fresh with baseline Q-table (resets training progress)
- **Reset Environment**: New random positions, keeps learned Q-table
- **Reset Training**: Back to baseline Q-table, same grid positions

---

## API Communication

### File: `js/api.js`
**Base URL**: `http://localhost:8000`

#### Endpoints Called:

1. **POST /game/new**
   - Creates new game instance
   - Returns: `{ dogPos, bonePos, homePos, hasBone, score, moveCount }`

2. **POST /game/fetch**
   - Gets next sequence of moves
   - Returns:
     ```json
     {
       "steps": [
         { "pos": {x, y}, "action": "up|down|left|right", "reward": float|null, "source": "automatic|human" },
         ...
       ],
       "awaitingUserReward": true
     }
     ```

3. **POST /game/reward**
   - Submits user's reward for pending action
   - Body: `{ "value": 1 or -1 }`
   - Returns: Updated game state

4. **POST /game/reset**
   - Resets game state
   - Body: `{ "type": "all" | "env" | "train" }`
   - Returns: New game state

---

## JavaScript Files

### `js/home.js`
- Simple navigation script
- Handles "NEW GAME" and "Read docs" button clicks

### `js/game.js` (~400+ lines)
- **Game State Management**: Tracks dog position, bone position, home position, score, moves
- **Grid Rendering**: Dynamically creates and updates 5×5 grid
- **Animation**: Animates dog movements with 500ms delays
- **Event Listeners**: 
  - FETCH button → triggers move sequence
  - +1/-1 buttons → submit rewards
  - Reset buttons → reset game state
- **UI Updates**: Updates score, moves, status message, reward button states
- **Reward Popup**: Shows "+10" bonus when reaching home with bone

### `js/api.js`
- Wraps all HTTP calls to backend
- Supports mock data mode (`USE_MOCK_DATA = true`) for testing
- Handles response parsing and error handling

### `js/mockData.js`
- Simulates backend responses for frontend testing
- Contains mock game state, fetch responses, reward responses

---

## Styling

### `css/style.css`
**Color Scheme**:
- Background: `#080808` (almost black)
- Text: `#ffffff` (white)
- Accent: Various grays for borders and secondary elements

**Layout**:
- Flexbox-based responsive design
- Game page uses split layout (left grid + right controls)
- Grid cells are square and arranged in 5×5

---

## Key UI Features

✅ **Real-time Feedback**: Status messages update in real-time  
✅ **Visual Animation**: Smooth step-by-step movement visualization  
✅ **Interactive Training**: User provides immediate rewards  
✅ **State Tracking**: Score and move count always visible  
✅ **Multiple Reset Options**: Flexible reset scenarios  
✅ **Responsive Controls**: Buttons enable/disable based on game state  
✅ **Clean Minimalist Design**: Dark mode, clear hierarchy  

---

## Integration Points with Backend

The frontend expects the backend to:

1. **Maintain game state** (positions, score, moves)
2. **Generate action sequences** based on Q-learning best actions
3. **Apply rewards** to update Q-table when `/game/reward` is called
4. **Support three reset modes** (all, env, train)
5. **Return structured responses** with step-by-step moves and animations

---

## Current State

🟢 **UI is fully functional** - All buttons, grid rendering, and animations work  
🔴 **Backend is incomplete** - Q-learning integration missing (see BACKEND_ANALYSIS.md)
