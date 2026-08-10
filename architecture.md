# Train the Dog: Reinforcement Learning Project Architecture

## 0. Project Overview

**Train the Dog** is a small Reinforcement Learning (RL) project where
an AI agent learns to move a dog through a grid and reach a bone while
avoiding obstacles.

The project has two main sides:

-   **Frontend**: shows the grid, dog, bone, obstacles, agent movement,
    training progress, and learned behavior.
-   **Backend**: contains the RL environment, Q-learning agent, training
    loop, and API that the frontend communicates with.

The project should be built in **4 major parts**:

1.  **RL Environment**
2.  **Q-Learning Agent + Training Engine**
3.  **Backend API**
4.  **Frontend + Visualization**

The order matters. Build and test each part before moving to the next.
Otherwise you get the traditional software-development experience of
five files failing for five unrelated reasons.

------------------------------------------------------------------------

# 1. Final Architecture

``` text
                           TRAIN THE DOG
                                |
              +-----------------+-----------------+
              |                                   |
          FRONTEND                            BACKEND
        React + Vite                       Python + FastAPI
              |                                   |
              | HTTP / JSON                       |
              +-------------> API <---------------+
                                  |
                         +--------+--------+
                         |                 |
                    RL Training        RL State
                         |                 |
                    +----+----+            |
                    |         |            |
               DogEnv     QLearningAgent  |
                    |         |            |
                    +----+----+            |
                         |                 |
                    Training Engine <------+
                         |
                     Q-Table
```

------------------------------------------------------------------------

# 2. Core RL Concept

The entire system revolves around this loop:

``` text
        STATE
          |
          v
       AGENT
          |
       ACTION
          |
          v
     ENVIRONMENT
          |
     +----+----+
     |         |
  REWARD   NEXT STATE
     |         |
     +----+----+
          |
          v
       LEARN
          |
          v
       repeat
```

For this project:

``` text
STATE
    = position of dog

ACTION
    = UP / DOWN / LEFT / RIGHT

REWARD
    = small negative reward for movement
    = large negative reward for invalid movement
    = large positive reward for reaching bone

NEXT STATE
    = dog's new position

LEARNING
    = update Q-table
```

------------------------------------------------------------------------

# 3. Recommended Project Structure

``` text
train-the-dog/
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── training.py
│   │   │   ├── environment.py
│   │   │   └── agent.py
│   │   │
│   │   ├── rl/
│   │   │   ├── __init__.py
│   │   │   ├── environment.py
│   │   │   ├── agent.py
│   │   │   └── trainer.py
│   │   │
│   │   ├── models/
│   │   │   └── schemas.py
│   │   │
│   │   └── core/
│   │       └── config.py
│   │
│   ├── tests/
│   │   ├── test_environment.py
│   │   ├── test_agent.py
│   │   └── test_api.py
│   │
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── Grid.jsx
│   │   │   ├── Cell.jsx
│   │   │   ├── TrainingControls.jsx
│   │   │   ├── TrainingStats.jsx
│   │   │   ├── QTable.jsx
│   │   │   └── Legend.jsx
│   │   │
│   │   ├── pages/
│   │   │   └── Dashboard.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
├── architecture.md
└── README.md
```

------------------------------------------------------------------------

# PART 1: RL ENVIRONMENT

## 4. Goal of Part 1

Build the world in which the dog exists.

The environment should know:

-   Grid size
-   Dog position
-   Bone position
-   Obstacles
-   Available actions
-   Valid/invalid movement
-   Reward system
-   When an episode ends
-   Current state

The environment should **not** know how the agent learns.

That separation is important.

------------------------------------------------------------------------

# 5. Grid

Start with a 5 × 5 grid.

``` text
       0   1   2   3   4
     +---+---+---+---+---+
  0  |   |   |   |   |   |
     +---+---+---+---+---+
  1  |   |   | X |   |   |
     +---+---+---+---+---+
  2  |   | D |   |   | B |
     +---+---+---+---+---+
  3  |   |   | X |   |   |
     +---+---+---+---+---+
  4  |   |   |   |   |   |
     +---+---+---+---+---+

D = Dog
B = Bone
X = Obstacle
```

Coordinates:

``` python
dog = [2, 1]
bone = [2, 4]

obstacles = [
    (1, 2),
    (3, 2)
]
```

------------------------------------------------------------------------

# 6. Observation Space

There are 25 possible dog positions:

``` text
5 rows × 5 columns = 25 states
```

Gymnasium:

``` python
self.observation_space = spaces.Discrete(25)
```

Convert coordinates into a single state:

``` python
state = row * 5 + column
```

Examples:

``` text
[0,0] -> 0
[0,1] -> 1
[0,2] -> 2

[1,0] -> 5
[1,1] -> 6
[1,2] -> 7

[2,1] -> 11

[4,4] -> 24
```

This means the agent only needs to work with integers from `0` to `24`.

------------------------------------------------------------------------

# 7. Action Space

There are four possible actions:

``` text
0 = UP
1 = DOWN
2 = LEFT
3 = RIGHT
```

Gymnasium:

``` python
self.action_space = spaces.Discrete(4)
```

Movement dictionary:

``` python
moves = {
    0: (-1, 0),
    1: (1, 0),
    2: (0, -1),
    3: (0, 1)
}
```

The first number changes the row.

The second number changes the column.

------------------------------------------------------------------------

# 8. Reset

`reset()` starts a new episode.

``` python
def reset(self, seed=None, options=None):
    super().reset(seed=seed)

    self.dog = [2, 1]

    return self.get_state(), {}
```

The environment should return:

``` text
initial_state
info
```

Example:

``` python
(11, {})
```

------------------------------------------------------------------------

# 9. Step

`step(action)` is the most important environment function.

It receives:

``` text
action
```

and returns:

``` text
next_state
reward
terminated
truncated
info
```

Example:

``` python
next_state, reward, terminated, truncated, info = env.step(3)
```

If action `3` is RIGHT:

``` text
Dog [2,1]
    |
    | RIGHT
    v
Dog [2,2]
```

------------------------------------------------------------------------

# 10. Reward Design

Use a simple reward system.

  Situation            Reward
  ----------------- ---------
  Normal movement     `-0.01`
  Outside grid           `-1`
  Obstacle               `-1`
  Reach bone            `+10`

Why a small negative movement reward?

Because we want the dog to reach the bone quickly.

Without it, the dog may learn:

``` text
move
move
move
move
move
...
bone eventually
```

The small penalty encourages shorter routes.

------------------------------------------------------------------------

# 11. Episode Termination

When the dog reaches the bone:

``` python
if self.dog == self.bone:
    reward = 10
    terminated = True
```

There is no future after this.

The episode ends.

------------------------------------------------------------------------

# 12. Environment Testing

Before creating an RL agent, test the environment manually.

Example:

``` python
env = DogEnv()

state, _ = env.reset()

print(state)

next_state, reward, done, _, _ = env.step(3)

print(next_state)
print(reward)
print(done)
```

You should be able to manually verify:

-   Dog moves correctly
-   Walls work
-   Obstacles work
-   Bone ends the episode
-   Rewards are correct
-   State conversion works

Do not move to Part 2 until this works.

------------------------------------------------------------------------

# PART 2: Q-LEARNING AGENT + TRAINING ENGINE

## 13. Goal of Part 2

Create the brain.

The agent needs to:

1.  Store knowledge
2.  Choose actions
3.  Explore
4.  Exploit
5.  Learn from rewards
6.  Reduce exploration over time

------------------------------------------------------------------------

# 14. Q-Table

The agent has:

``` python
q_table = np.zeros((25, 4))
```

This creates:

``` text
25 states × 4 actions
```

Conceptually:

``` text
              UP    DOWN    LEFT    RIGHT
State 0        0      0       0       0
State 1        0      0       0       0
State 2        0      0       0       0
...
State 11       0      0       0       0
...
State 24       0      0       0       0
```

Each cell answers:

> How valuable is this action from this state?

------------------------------------------------------------------------

# 15. Q-Learning Parameters

Use:

``` python
learning_rate = 0.1
discount_factor = 0.95

epsilon = 1.0
epsilon_decay = 0.995
epsilon_min = 0.01
```

### Learning rate

Controls how strongly new information changes existing knowledge.

``` text
0.1 = learn gradually
```

### Discount factor

Controls how much future rewards matter.

``` text
0.95 = future rewards matter a lot
```

### Epsilon

Controls exploration.

``` text
1.0 = explore heavily
0.01 = mostly exploit
```

### Epsilon decay

Reduces exploration after each episode.

------------------------------------------------------------------------

# 16. Action Selection

Use epsilon-greedy.

``` python
def choose_action(self, state):

    if np.random.random() < self.epsilon:
        return np.random.randint(0, 4)

    return np.argmax(self.q_table[state])
```

Two possibilities:

``` text
EXPLORE
    ↓
random action

EXPLOIT
    ↓
best known action
```

At the beginning, exploration is high.

Later, exploitation becomes dominant.

------------------------------------------------------------------------

# 17. Q-Learning Update

The basic equation is:

``` text
Q(s,a) = Q(s,a) +
         α ×
         [r + γ × max(Q(s',a')) - Q(s,a)]
```

Where:

``` text
s  = current state
a  = action
r  = reward
s' = next state
α  = learning rate
γ  = discount factor
```

In code:

``` python
old_value = self.q_table[state, action]

best_next_value = np.max(self.q_table[next_state])

new_value = old_value + self.learning_rate * (
    reward
    + self.discount_factor * best_next_value
    - old_value
)
```

------------------------------------------------------------------------

# 18. Terminal State Handling

When the dog reaches the bone, there is no future state.

Therefore:

``` python
if done:
    best_next_value = 0
else:
    best_next_value = np.max(self.q_table[next_state])
```

Recommended implementation:

``` python
def learn(
    self,
    state,
    action,
    reward,
    next_state,
    done
):

    old_value = self.q_table[state, action]

    if done:
        best_next_value = 0
    else:
        best_next_value = np.max(
            self.q_table[next_state]
        )

    new_value = old_value + self.learning_rate * (
        reward
        + self.discount_factor * best_next_value
        - old_value
    )

    self.q_table[state, action] = new_value
```

------------------------------------------------------------------------

# 19. Training Engine

Do not put the entire training system inside the API route.

Create:

``` text
rl/trainer.py
```

The trainer should handle:

-   Creating environment
-   Creating agent
-   Running episodes
-   Calling `reset()`
-   Calling `choose_action()`
-   Calling `step()`
-   Calling `learn()`
-   Decaying epsilon
-   Collecting statistics

Basic structure:

``` python
def train(episodes):

    env = DogEnv()

    agent = QLearningAgent(
        state_size=25,
        action_size=4
    )

    history = []

    for episode in range(episodes):

        state, _ = env.reset()

        total_reward = 0
        steps = 0

        while True:

            action = agent.choose_action(state)

            next_state, reward, done, _, _ = env.step(action)

            agent.learn(
                state,
                action,
                reward,
                next_state,
                done
            )

            state = next_state

            total_reward += reward
            steps += 1

            if done:
                break

        agent.decay_epsilon()

        history.append({
            "episode": episode,
            "reward": total_reward,
            "steps": steps,
            "epsilon": agent.epsilon
        })

    return agent, history
```

------------------------------------------------------------------------

# 20. Training Statistics

Store at least:

``` text
episode
reward
steps
epsilon
success
```

Example:

``` json
{
    "episode": 500,
    "reward": 9.92,
    "steps": 8,
    "epsilon": 0.08,
    "success": true
}
```

These statistics will later be sent to the frontend.

------------------------------------------------------------------------

# 21. Evaluation vs Training

Eventually you should separate:

### Training

The agent explores.

``` text
epsilon > 0
```

### Evaluation

The agent should use its learned policy.

``` text
epsilon = 0
```

Evaluation answers:

> "Can the trained agent actually solve the environment?"

This should be a separate backend function.

------------------------------------------------------------------------

# PART 3: BACKEND API

## 22. Goal of Part 3

The frontend should not directly import Python classes.

Instead:

``` text
Frontend
   |
 HTTP
   |
FastAPI
   |
RL Engine
```

The backend becomes the bridge between the browser and the RL system.

------------------------------------------------------------------------

# 23. Recommended Backend Stack

Use:

``` text
Python
FastAPI
Gymnasium
NumPy
Uvicorn
```

Install:

``` bash
pip install fastapi uvicorn gymnasium numpy
```

Create:

``` text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   ├── rl/
│   ├── models/
│   └── core/
└── requirements.txt
```

------------------------------------------------------------------------

# 24. FastAPI Entry Point

`main.py`:

``` python
from fastapi import FastAPI

app = FastAPI(
    title="Train the Dog API"
)

@app.get("/")
def root():
    return {
        "message": "Train the Dog API is running"
    }
```

Run:

``` bash
uvicorn app.main:app --reload
```

The API should be available locally at:

``` text
http://localhost:8000
```

FastAPI also gives interactive API documentation.

------------------------------------------------------------------------

# 25. API Endpoints

Keep the first version small.

## GET `/environment`

Returns the current environment.

Example response:

``` json
{
    "grid_size": 5,
    "dog": [2, 1],
    "bone": [2, 4],
    "obstacles": [
        [1, 2],
        [3, 2]
    ]
}
```

------------------------------------------------------------------------

## POST `/environment/reset`

Resets the environment.

Response:

``` json
{
    "state": 11,
    "dog": [2, 1]
}
```

------------------------------------------------------------------------

## POST `/environment/step`

Request:

``` json
{
    "action": 3
}
```

Response:

``` json
{
    "state": 12,
    "dog": [2, 2],
    "reward": -0.01,
    "terminated": false
}
```

This endpoint is useful for manually visualizing individual agent
actions.

------------------------------------------------------------------------

## POST `/training/start`

Request:

``` json
{
    "episodes": 5000
}
```

Response:

``` json
{
    "message": "Training completed",
    "episodes": 5000
}
```

For the first version, synchronous training is acceptable.

Later, move training into a background job.

------------------------------------------------------------------------

## GET `/training/stats`

Returns training history.

``` json
{
    "episodes": [
        {
            "episode": 0,
            "reward": -3.2,
            "steps": 320,
            "epsilon": 0.995
        },
        {
            "episode": 1,
            "reward": -1.8,
            "steps": 180,
            "epsilon": 0.990
        }
    ]
}
```

------------------------------------------------------------------------

## GET `/agent/q-table`

Returns the current Q-table.

Example:

``` json
{
    "q_table": [
        [0.0, -0.2, 0.1, 2.4],
        ...
    ]
}
```

------------------------------------------------------------------------

## POST `/agent/predict`

Given a state, return the best action.

Request:

``` json
{
    "state": 11
}
```

Response:

``` json
{
    "state": 11,
    "action": 3,
    "action_name": "RIGHT"
}
```

------------------------------------------------------------------------

# 26. Backend State Management

For the first version, keep the trained agent in memory.

Example:

``` python
agent = None
training_history = []
```

After training:

``` python
agent = trained_agent
training_history = history
```

This is enough for a prototype.

Do not add PostgreSQL, Redis, Celery, Docker, Kubernetes and the entire
United Nations just because the project contains an API.

------------------------------------------------------------------------

# 27. CORS

The frontend and backend will run on different ports.

Example:

``` text
Frontend
localhost:5173

Backend
localhost:8000
```

The backend must allow frontend requests.

Install/use FastAPI CORS middleware:

``` python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

------------------------------------------------------------------------

# PART 4: FRONTEND + VISUALIZATION

## 28. Goal of Part 4

The frontend makes the RL system understandable.

The user should be able to:

1.  See the grid
2.  See the dog
3.  See the bone
4.  See obstacles
5.  Start training
6.  See training progress
7.  Watch the trained agent move
8.  See rewards
9.  See epsilon
10. Inspect Q-values

------------------------------------------------------------------------

# 29. Recommended Frontend Stack

Use:

``` text
React
Vite
JavaScript
CSS
```

Create:

``` bash
npm create vite@latest frontend
```

Choose:

``` text
React
JavaScript
```

Then:

``` bash
cd frontend
npm install
npm run dev
```

------------------------------------------------------------------------

# 30. Frontend Components

Create these components:

``` text
components/
│
├── Grid.jsx
├── Cell.jsx
├── TrainingControls.jsx
├── TrainingStats.jsx
├── QTable.jsx
└── Legend.jsx
```

------------------------------------------------------------------------

# 31. Grid Component

The grid receives:

``` text
grid size
dog position
bone position
obstacles
```

Example:

``` jsx
<Grid
    dog={[2, 1]}
    bone={[2, 4]}
    obstacles={[
        [1, 2],
        [3, 2]
    ]}
/>
```

The component generates:

``` text
5 × 5 = 25 cells
```

Each cell checks what is inside it.

------------------------------------------------------------------------

# 32. Cell Component

A cell can contain:

``` text
empty
dog
bone
obstacle
```

Example UI:

``` text
┌───┬───┬───┬───┬───┐
│   │   │   │   │   │
├───┼───┼───┼───┼───┤
│   │   │ X │   │   │
├───┼───┼───┼───┼───┤
│   │ 🐶│   │   │ 🦴│
├───┼───┼───┼───┼───┤
│   │   │ X │   │   │
├───┼───┼───┼───┼───┤
│   │   │   │   │   │
└───┴───┴───┴───┴───┘
```

------------------------------------------------------------------------

# 33. Training Controls

Create:

``` text
TrainingControls.jsx
```

Include:

``` text
Episodes: [5000]

[ Start Training ]

[ Reset ]

[ Run Agent ]
```

Later:

``` text
Training speed
Animation speed
Exploration
```

------------------------------------------------------------------------

# 34. Training Statistics

Display:

``` text
Episodes
Current reward
Average reward
Steps
Epsilon
Success rate
```

Example:

``` text
Training Progress

Episodes       5000
Best Reward    9.92
Avg Reward     8.74
Success Rate   96%
Epsilon        0.01
```

------------------------------------------------------------------------

# 35. Reward Graph

Use a graph to show:

``` text
Episode → Reward
```

Initially:

``` text
low / negative
```

After learning:

``` text
higher / positive
```

A moving average is useful because individual episodes can be noisy.

------------------------------------------------------------------------

# 36. Q-Table Visualization

Show the Q-table as a grid.

Instead of:

``` text
25 × 4 numbers
```

make it visually understandable.

For each state:

``` text
State 11

UP      -0.3
DOWN     0.1
LEFT    -1.0
RIGHT    8.4
```

Highlight:

``` text
RIGHT = best action
```

This makes it obvious what the agent has learned.

------------------------------------------------------------------------

# 37. Agent Playback

After training, the frontend should allow:

``` text
[ Run Learned Agent ]
```

The backend can repeatedly:

``` text
current state
    ↓
best action
    ↓
environment.step()
    ↓
new state
    ↓
send result
```

The frontend animates the dog.

Example:

``` text
Step 1
🐶 at [2,1]

        ↓ RIGHT

Step 2
🐶 at [2,2]

        ↓ RIGHT

Step 3
🐶 at [2,3]

        ↓ RIGHT

Step 4
🐶 at [2,4] 🦴

SUCCESS
```

------------------------------------------------------------------------

# 38. Frontend API Service

Keep API calls in one place:

``` text
src/services/api.js
```

Example:

``` javascript
const API_URL = "http://localhost:8000";

export async function resetEnvironment() {
    const response = await fetch(
        `${API_URL}/environment/reset`,
        {
            method: "POST"
        }
    );

    return response.json();
}
```

Do not scatter `fetch()` calls across every component.

------------------------------------------------------------------------

# 39. Frontend State

The main page should maintain:

``` text
dog
bone
obstacles
reward
episode
epsilon
training status
training history
q table
```

Example:

``` javascript
const [dog, setDog] = useState([2, 1]);
const [reward, setReward] = useState(0);
const [epsilon, setEpsilon] = useState(1);
const [training, setTraining] = useState(false);
```

------------------------------------------------------------------------

# 40. Complete Data Flow

When the user clicks:

``` text
START TRAINING
```

the flow is:

``` text
FRONTEND
   |
   | POST /training/start
   | { episodes: 5000 }
   v
FASTAPI
   |
   v
TRAINER
   |
   +----> DogEnv
   |
   +----> QLearningAgent
   |
   v
TRAINING
   |
   v
Q-TABLE
   |
   v
FASTAPI
   |
   | JSON
   v
FRONTEND
   |
   +----> Stats
   |
   +----> Q-table
   |
   +----> Success rate
```

------------------------------------------------------------------------

# 41. Recommended Development Order

Do not build everything at once.

Follow these 4 major milestones.

------------------------------------------------------------------------

## MILESTONE 1: Environment

### Build

``` text
backend/rl/environment.py
```

Implement:

-   `DogEnv`
-   5×5 grid
-   dog
-   bone
-   obstacles
-   action space
-   observation space
-   reset
-   state conversion
-   step
-   rewards
-   termination

### Test

Manually verify:

``` text
✓ Dog starts correctly
✓ Dog moves UP
✓ Dog moves DOWN
✓ Dog moves LEFT
✓ Dog moves RIGHT
✓ Walls work
✓ Obstacles work
✓ Bone gives +10
✓ Bone ends episode
```

------------------------------------------------------------------------

# MILESTONE 2: Agent + Training

### Build

``` text
backend/rl/agent.py
backend/rl/trainer.py
```

Implement:

-   Q-table
-   epsilon-greedy
-   learning rate
-   discount factor
-   Q-learning update
-   terminal-state handling
-   epsilon decay
-   training loop
-   training statistics

### Test

Run:

``` bash
python trainer.py
```

You want to see something like:

``` text
Episode: 0
Reward: -4.32

Episode: 500
Reward: 8.42

Episode: 1000
Reward: 9.72

Episode: 1500
Reward: 9.91
```

The exact numbers will vary.

The important thing is that the agent should generally become better.

------------------------------------------------------------------------

# MILESTONE 3: Backend API

### Build

``` text
backend/app/main.py
backend/app/api/
backend/app/models/
```

Implement:

``` text
GET  /environment
POST /environment/reset
POST /environment/step

POST /training/start
GET  /training/stats

GET  /agent/q-table
POST /agent/predict
```

### Test without frontend

Use:

-   Browser
-   FastAPI Swagger UI
-   Postman
-   curl

First make sure the API works independently.

------------------------------------------------------------------------

# MILESTONE 4: Frontend

### Build

``` text
frontend/
```

Implement:

``` text
Grid
Cell
TrainingControls
TrainingStats
QTable
RewardChart
AgentPlayback
```

Connect to:

``` text
FastAPI
```

Then build the final user flow:

``` text
OPEN APP
   ↓
SEE GRID
   ↓
CLICK TRAIN
   ↓
BACKEND TRAINS AGENT
   ↓
SEE TRAINING STATS
   ↓
SEE Q-TABLE
   ↓
CLICK RUN AGENT
   ↓
WATCH DOG FIND BONE
```

------------------------------------------------------------------------

# 42. Final API Contract

Keep the frontend/backend contract simple.

## Environment

### `GET /environment`

``` json
{
    "grid_size": 5,
    "dog": [2, 1],
    "bone": [2, 4],
    "obstacles": [[1, 2], [3, 2]]
}
```

### `POST /environment/reset`

``` json
{
    "state": 11,
    "dog": [2, 1]
}
```

### `POST /environment/step`

Request:

``` json
{
    "action": 3
}
```

Response:

``` json
{
    "state": 12,
    "dog": [2, 2],
    "reward": -0.01,
    "terminated": false,
    "truncated": false
}
```

------------------------------------------------------------------------

## Training

### `POST /training/start`

Request:

``` json
{
    "episodes": 5000
}
```

Response:

``` json
{
    "status": "completed",
    "episodes": 5000
}
```

### `GET /training/stats`

``` json
{
    "episodes": [
        {
            "episode": 0,
            "reward": -3.5,
            "steps": 350,
            "epsilon": 0.995
        }
    ]
}
```

------------------------------------------------------------------------

## Agent

### `GET /agent/q-table`

``` json
{
    "q_table": [
        [0, 0, 0, 0]
    ]
}
```

### `POST /agent/predict`

Request:

``` json
{
    "state": 11
}
```

Response:

``` json
{
    "state": 11,
    "action": 3,
    "action_name": "RIGHT"
}
```

------------------------------------------------------------------------

# 43. Important Architecture Rules

## Rule 1: Environment does not learn

Bad:

``` text
DogEnv
    ↓
changes Q-table
```

Good:

``` text
DogEnv
    ↓
returns state + reward

Agent
    ↓
updates Q-table
```

------------------------------------------------------------------------

## Rule 2: Agent does not control the environment directly

The agent should say:

``` text
"I choose action 3."
```

The environment decides whether that action is valid.

------------------------------------------------------------------------

## Rule 3: Trainer coordinates both

``` text
Trainer
   |
   +--> Agent chooses action
   |
   +--> Environment executes action
   |
   +--> Agent learns
```

------------------------------------------------------------------------

## Rule 4: Frontend never contains RL logic

Frontend should not calculate:

``` text
Q-values
rewards
epsilon
Q-learning
```

Frontend only:

``` text
display
controls
API calls
animation
```

------------------------------------------------------------------------

## Rule 5: Backend owns the RL state

The backend should own:

``` text
environment
agent
Q-table
training history
```

The frontend receives representations of these things.

------------------------------------------------------------------------

# 44. Future Improvements

Once the basic project works, add features in this order.

### Level 1

-   Better UI
-   Agent animation
-   Reward chart
-   Q-table visualization
-   Current action display

### Level 2

-   Change grid size
-   Add/remove obstacles
-   Move bone
-   Change rewards
-   Change learning rate
-   Change discount factor
-   Change epsilon decay

### Level 3

-   Save Q-table
-   Load trained model
-   Multiple environments
-   Randomized starting positions
-   Randomized obstacles
-   Training history

### Level 4

Try other RL algorithms:

``` text
Q-Learning
    ↓
SARSA
    ↓
Deep Q-Network (DQN)
    ↓
Policy Gradient
```

At that point the project becomes much more interesting because you can
compare algorithms on the same environment.

------------------------------------------------------------------------

# 45. Suggested Final UI

A simple dashboard:

``` text
┌─────────────────────────────────────────────────────────────┐
│                    TRAIN THE DOG                            │
├───────────────────────────┬─────────────────────────────────┤
│                           │                                 │
│       5 × 5 GRID          │       TRAINING                  │
│                           │                                 │
│  ┌───┬───┬───┬───┬───┐   │ Episodes: [5000]               │
│  │   │   │   │   │   │   │                                 │
│  ├───┼───┼───┼───┼───┤   │ [ Start Training ]              │
│  │   │   │ X │   │   │   │                                 │
│  ├───┼───┼───┼───┼───┤   │ Reward: 9.82                    │
│  │   │ D │   │   │ B │   │ Epsilon: 0.01                   │
│  ├───┼───┼───┼───┼───┤   │ Steps: 5                       │
│  │   │   │ X │   │   │   │                                 │
│  ├───┼───┼───┼───┼───┤   │ [ Run Learned Agent ]           │
│  │   │   │   │   │   │   │                                 │
│  └───┴───┴───┴───┴───┘   │                                 │
│                           │                                 │
├───────────────────────────┴─────────────────────────────────┤
│                      REWARD GRAPH                            │
│                                                             │
│       reward ↑                                               │
│              |                         ______                │
│              |                   _____/                      │
│              |             _____/                            │
│              |___________/                                   │
│              +──────────────────────────────→ episodes       │
├─────────────────────────────────────────────────────────────┤
│                       Q-TABLE                                │
│                                                             │
│ State    UP       DOWN      LEFT      RIGHT                  │
│ 0       -1.0      0.2       -1.0       2.1                   │
│ 1       -1.0      0.4       -1.0       3.4                   │
│ ...                                                           │
└─────────────────────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 46. Definition of Done

The project is complete when all of these work:

## Environment

-   [ ] 5×5 grid exists
-   [ ] Dog exists
-   [ ] Bone exists
-   [ ] Obstacles exist
-   [ ] Four actions work
-   [ ] Invalid movement is blocked
-   [ ] Rewards work
-   [ ] Episode terminates at bone

## Agent

-   [ ] Q-table is created
-   [ ] Random exploration works
-   [ ] Exploitation works
-   [ ] Q-values update
-   [ ] Terminal states are handled
-   [ ] Epsilon decays
-   [ ] Agent learns a useful route

## Backend

-   [ ] FastAPI starts
-   [ ] CORS works
-   [ ] Environment endpoint works
-   [ ] Training endpoint works
-   [ ] Stats endpoint works
-   [ ] Q-table endpoint works
-   [ ] Prediction endpoint works

## Frontend

-   [ ] Grid renders
-   [ ] Dog renders
-   [ ] Bone renders
-   [ ] Obstacles render
-   [ ] Training can be started
-   [ ] Training progress is shown
-   [ ] Reward graph works
-   [ ] Q-table is visible
-   [ ] Learned agent can be played back

------------------------------------------------------------------------

# 47. The Mental Model to Remember

If you are new to RL, do not try to memorize every formula first.

Remember these five things:

``` text
1. ENVIRONMENT
   "What world am I in?"

2. STATE
   "Where am I / what do I see?"

3. ACTION
   "What can I do?"

4. REWARD
   "Was that good or bad?"

5. LEARNING
   "Given what happened, should I change my future decision?"
```

For this project:

``` text
Environment = 5×5 dog world

State = dog's position

Actions = UP/DOWN/LEFT/RIGHT

Reward =
    -0.01 normal movement
    -1 invalid movement
    +10 bone

Learning =
    Q-table + Q-learning
```

Everything in the project is built around those five ideas.

------------------------------------------------------------------------

# 48. Final Architecture Summary

``` text
                    USER
                     |
                     v
              REACT FRONTEND
                     |
              HTTP / JSON
                     |
                     v
              FASTAPI BACKEND
                     |
          +----------+----------+
          |                     |
          v                     v
      TRAINER               ENVIRONMENT
          |                     |
          |                 DogEnv
          |                     |
          v                     |
    QLearningAgent <------------+
          |
          v
       Q-TABLE
          |
          v
   Training Statistics
          |
          v
       FastAPI
          |
          v
       Frontend
          |
     Visualization
          |
          v
    "Dog learned!"
```

The clean separation is:

``` text
FRONTEND
    = what the user sees

BACKEND API
    = communication layer

TRAINER
    = controls training

AGENT
    = learns

ENVIRONMENT
    = world/rules
```

Build the project in exactly that order:

``` text
1. Environment
       ↓
2. Agent + Training
       ↓
3. Backend API
       ↓
4. Frontend
```

That gives you a working RL system before you add visual polish, which
is considerably less painful than building a beautiful dashboard for an
algorithm that quietly doesn't work.
