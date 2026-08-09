# 🐶 AIRIS Orientation Demo — Train the Dog

> **"Watch this dog learn to fetch, just by being told good dog or bad dog."**

---

## 📌 Overview

**AIRIS Orientation Demo** is a live, interactive Reinforcement Learning (RL) showcase designed for orientation day at the atrium. Visitors interact directly with a virtual dog on a $5 \times 5$ grid, guiding it to find a bone and return home by manually giving positive ("Good dog") or negative ("Bad dog") feedback after each move.

### 🎯 Purpose
* **Interactive Engagement:** Gives incoming students and parents a hands-on experience with Artificial Intelligence.
* **Tangible AI/RL Concept:** Demonstrates fundamental Reinforcement Learning (Q-learning) visually in under **60 seconds**, moving from random exploration to goal-directed behavior without complex math lectures.
* **Zero Onboarding Needed:** The grid, dog sprite, bone, and simple feedback buttons make the core mechanic self-explanatory.

---

## 🕹️ Core Mechanics & Workflow

1. **Grid Setup:** A $5 \times 5$ grid (25 discrete states). The dog spawns at a starting cell, the bone is placed on the grid, and obstacles are placed dynamically or statically.
2. **Action Selection:** On each turn, the dog selects an action: Up (`0`), Down (`1`), Left (`2`), or Right (`3`).
3. **Human / Environment Feedback:**
   * In interactive kiosk mode, the visitor clicks **"Good dog"** (+ reward) or **"Bad dog"** (- punishment).
   * In automated mode, step rewards are computed based on environmental rules (hitting obstacles, boundary collisions, or reaching the bone).
4. **Q-Table Update:** Feedback immediately updates the dog's internal Q-table ($Q(s, a)$).
5. **Visible Arc:** Over 20–40 moves, the dog transitions from random wandering to taking an optimal, direct path to the bone.
6. **Session Reset:** A single click resets the Q-table and respawns the dog and bone at new positions, providing a fresh session for the next visitor.

---

## 📁 Repository Structure

```
train_the_dog/
├── agent.py          # QLearningAgent implementation with tabular Q-learning & epsilon decay
├── environment.py    # DogEnv custom Gymnasium environment (5x5 grid world)
├── train.py          # Automated simulation training script for parameter testing
├── test.py           # Quick environment step validation script
├── LICENSE           # Project license (Apache 2.0)
└── README.md         # Project documentation
```

### Key Modules

* [environment.py](file:///Users/djha/Desktop/train_the_dog/environment.py): Implements `DogEnv`, a custom [Gymnasium](https://gymnasium.farama.org/) `gym.Env` subclass representing the $5 \times 5$ grid world. Tracks agent position, goal (bone), player position, and fixed obstacles.
* [agent.py](file:///Users/djha/Desktop/train_the_dog/agent.py): Implements `QLearningAgent` with state-action lookup table, $\epsilon$-greedy exploration policy, learning rate ($\alpha$), and discount factor ($\gamma$).
* [train.py](file:///Users/djha/Desktop/train_the_dog/train.py): Runs a multi-episode automated training loop to benchmark convergence speed and reward optimization.
* [test.py](file:///Users/djha/Desktop/train_the_dog/test.py): Performs sanity checks on environment resets and state transitions.

---

## 🧮 How the AI Learns (Q-Learning)

The dog uses **Tabular Q-Learning**, an model-free reinforcement learning algorithm.

### Math & Bellman Equation

The Q-value update rule is defined as:

$$Q(s, a) \leftarrow Q(s, a) + \alpha \left[ R + \gamma \max_{a'} Q(s', a') - Q(s, a) \right]$$

Where:
* $s$: Current grid state (calculated as $\text{row} \times 5 + \text{col}$, values $0..24$).
* $a$: Action chosen ($\text{UP}, \text{DOWN}, \text{LEFT}, \text{RIGHT}$).
* $R$: Reward or penalty received from visitor click or environment.
* $\alpha$: Learning Rate (default `0.1`).
* $\gamma$: Discount Factor (default `0.95`).
* $\epsilon$: Exploration Rate (decays from `1.0` to `0.01`).

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10 or higher
* Virtual environment tool (`venv` or `conda`)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anuragkumart16/train_the_dog.git
   cd train_the_dog
   ```

2. **Set up virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install gymnasium numpy
   ```

### Running Automated Tests & Training

* **Test environment step logic:**
  ```bash
  python test.py
  ```

* **Run automated Q-learning simulation:**
  ```bash
  python train.py
  ```

---

## 🗣️ Booth & Kiosk Operational Guide

### 📢 Scripted Attendee Line
For booth volunteers guiding confused visitors:
> *"This dog starts completely untrained and makes random moves. Every time it moves, tell it whether it did a good job or a bad job. Watch how fast it figures out the path to the bone!"*

### 🔄 Reset Protocol
Between visitors, hit the **Reset** button to:
1. Re-initialize the Q-table to zeros ($\mathbf{0}_{25 \times 4}$).
2. Randomize starting positions for the dog and bone.
3. Reset exploration parameters so each visitor experiences a fresh learning curve.

---

## 📋 Open Action Items & Roadmap

- [ ] **Parameter Tuning:** Optimize learning rate ($\alpha$), reward magnitudes, and $\epsilon$-decay for fast 20–40 move human-in-the-loop convergence.
- [ ] **GUI / Visual Layer:** Build a visual interface (Vite/Web or Pygame) featuring grid rendering, dog sprite animations, interactive "Good Dog" / "Bad Dog" buttons, and an optional Q-value heat-map overlay.
- [ ] **Kiosk Stability:** Implement auto-restart watchdog and crash recovery scripts for unattended atrium runtime.
- [ ] **Booth Setup & Logistics:** Finalize hardware station count, screen layouts, and attendee shift scheduling.

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](file:///Users/djha/Desktop/train_the_dog/LICENSE) file for details.
