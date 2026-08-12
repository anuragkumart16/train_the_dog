# Train the Dog — Frontend

Standalone HTML/CSS/JS implementation based on the supplied design mockup and video reference.

## Run
Open `index.html` in a browser. If your browser blocks ES modules from `file://`, run a tiny local server:

    python3 -m http.server 8080

Then open `http://localhost:8080/frontend/`.

## Controls
- NEW GAME → game.html
- FETCH → moves the dog up one cell
- Arrow keys / WASD → move the dog
- -1 / +1 / +10 → assign reward
- reset env / train / all → reset state

## Backend switch
Edit `js/api.js`:
- `USE_MOCK = true` → standalone mock API
- `USE_MOCK = false` → requests go to `API_BASE`
