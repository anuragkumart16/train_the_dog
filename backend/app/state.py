import random
from threading import RLock
from .qtable_store import load_baseline, get_q_value, set_q_value, get_best_action


GRID_SIZE = 5
_state_lock = RLock()

# Q-learning hyperparameters
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9

# Actions mapping
ACTIONS = ["up", "down", "left", "right"]
ACTION_MAPPING = {
    "up": "UP",
    "down": "DOWN", 
    "left": "LEFT",
    "right": "RIGHT"
}
REVERSE_ACTION_MAPPING = {v: k for k, v in ACTION_MAPPING.items()}

# Current game state
game_state = {
    "dog_position": (0, 0),
    "bone_position": (0, 0),
    "home_position": (0, 0),
    "has_bone": False,
    "q_table": {},
    "move_count": 0,
    "score": 0,
    "pending_state": None,
    "pending_action": None,
    "current_state": None,
}


def random_position():
    """Generate a random position inside the 5x5 grid."""
    return (
        random.randint(0, GRID_SIZE - 1),
        random.randint(0, GRID_SIZE - 1),
    )


def get_direction(source_pos, target_pos):
    """
    Get the direction from source to target.
    Uses dominant axis when target is diagonal.
    
    Returns: "LEFT", "RIGHT", "UP", "DOWN", or "HERE"
    """
    source_x, source_y = source_pos
    target_x, target_y = target_pos
    
    dx = target_x - source_x
    dy = target_y - source_y
    
    # Same position
    if dx == 0 and dy == 0:
        return "HERE"
    
    # Dominant axis
    if abs(dx) >= abs(dy):
        return "DOWN" if dx > 0 else "UP"
    else:
        return "RIGHT" if dy > 0 else "LEFT"


def is_near_boundary(position):
    """Check if position is at the grid boundary (edges)."""
    x, y = position
    return x == 0 or x == GRID_SIZE - 1 or y == 0 or y == GRID_SIZE - 1


def get_current_state():
    """
    Get the current state representation for Q-learning.
    State = (bone_direction, human_direction, bone_picked, is_near_boundary)
    """
    if game_state["has_bone"]:
        bone_direction = "HERE"
    else:
        bone_direction = get_direction(
            game_state["dog_position"],
            game_state["bone_position"]
        )
    
    human_direction = get_direction(
        game_state["dog_position"],
        game_state["home_position"]
    )
    
    bone_picked = game_state["has_bone"]
    near_boundary = is_near_boundary(game_state["dog_position"])
    
    return (bone_direction, human_direction, bone_picked, near_boundary)


def generate_game_positions():
    """Generate distinct random positions for dog, bone, and home so they never render at the same place."""
    dog = random_position()
    
    while True:
        bone = random_position()
        if bone != dog:
            break
            
    while True:
        home = random_position()
        if home != dog and home != bone:
            break
            
    return dog, bone, home


def spawn_new_bone():
    """Spawn a new bone at a random location distinct from dog and home."""
    while True:
        pos = random_position()
        if pos != game_state["dog_position"] and pos != game_state["home_position"]:
            game_state["bone_position"] = pos
            break


def distance(pos1, pos2):
    """Calculate Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def create_game():
    """Create a new game and load baseline Q-table."""
    with _state_lock:
        return _create_game_unlocked()


def _create_game_unlocked():
    """Create a new game without acquiring the state lock."""

    dog_pos, bone_pos, home_pos = generate_game_positions()
    game_state["dog_position"] = dog_pos
    game_state["bone_position"] = bone_pos
    game_state["home_position"] = home_pos

    game_state["has_bone"] = False
    game_state["score"] = 0
    game_state["move_count"] = 0

    game_state["pending_state"] = None
    game_state["pending_action"] = None
    
    # Load baseline Q-table from q_table.py
    game_state["q_table"] = load_baseline()
    
    # Get current state
    game_state["current_state"] = get_current_state()

    return game_state


def serialize_game_state():
    """Return the public game state using the frontend API contract."""
    with _state_lock:
        return _serialize_game_state_unlocked()


def _serialize_game_state_unlocked():
    """Return the public game state without acquiring the state lock."""
    dog_pos = {"x": game_state["dog_position"][1], "y": game_state["dog_position"][0]}
    bone_pos = {"x": game_state["bone_position"][1], "y": game_state["bone_position"][0]}

    if game_state["has_bone"]:
        bone_pos = dog_pos.copy()

    return {
        "dogPos": dog_pos,
        "bonePos": bone_pos,
        "homePos": {"x": game_state["home_position"][1], "y": game_state["home_position"][0]},
        "hasBone": game_state["has_bone"],
        "score": game_state["score"],
        "moveCount": game_state["move_count"],
    }


def reset_environment():
    """Reset the game environment while keeping the Q-table."""
    with _state_lock:
        return _reset_environment_unlocked()


def _reset_environment_unlocked():
    """Reset the game environment without acquiring the state lock."""

    dog_pos, bone_pos, home_pos = generate_game_positions()
    game_state["dog_position"] = dog_pos
    game_state["bone_position"] = bone_pos
    game_state["home_position"] = home_pos

    game_state["has_bone"] = False
    game_state["score"] = 0
    game_state["move_count"] = 0

    game_state["pending_state"] = None
    game_state["pending_action"] = None
    
    # Get current state
    game_state["current_state"] = get_current_state()

    return game_state


def reset_training():
    """Reload the baseline Q-table without changing the game positions."""
    with _state_lock:
        return _reset_training_unlocked()


def _reset_training_unlocked():
    """Reload the baseline Q-table without acquiring the state lock."""

    game_state["q_table"] = load_baseline()

    return game_state


def reset_all():
    """Reset both the game environment and the training knowledge."""
    with _state_lock:
        _reset_environment_unlocked()
        _reset_training_unlocked()
        return game_state


def create_game_response():
    """Create a game and return the serialized API payload atomically."""
    with _state_lock:
        _create_game_unlocked()
        return _serialize_game_state_unlocked()


def reset_response(reset_type):
    """Reset the requested scope and return the serialized API payload atomically."""
    with _state_lock:
        if reset_type == "env":
            _reset_environment_unlocked()
        elif reset_type == "train":
            _reset_training_unlocked()
        else:
            _reset_environment_unlocked()
            _reset_training_unlocked()

        return _serialize_game_state_unlocked()


def move(position, action):
    """Move dog in the given direction (action format: "up", "down", "left", "right")."""
    x, y = position

    if action == "up" and x > 0:
        x -= 1
    elif action == "down" and x < GRID_SIZE - 1:
        x += 1
    elif action == "left" and y > 0:
        y -= 1
    elif action == "right" and y < GRID_SIZE - 1:
        y += 1

    return (x, y)


def best_action(forbidden_pos=None):
    """
    Get the best action using Q-learning values.
    
    Converts current state representation, looks up Q-values,
    and returns the action with the highest Q-value.
    Optional forbidden_pos prevents immediate backtracking.
    """
    current_state = game_state["current_state"]
    q_table = game_state["q_table"]
    dog_pos = game_state["dog_position"]
    
    # Get best valid action from Q-table (filtering out wall moves and backtrack)
    best_q_action = get_best_action(q_table, current_state, dog_pos, forbidden_pos)
    
    # Convert from Q-table action format (UP/DOWN/LEFT/RIGHT) to movement format (up/down/left/right)
    return REVERSE_ACTION_MAPPING.get(best_q_action, "up")


def update_q_value(state_before_action, action, reward, next_state):
    """Apply the Q-learning update for a single transition."""
    q_table = game_state["q_table"]
    q_action = ACTION_MAPPING[action]

    current_q = get_q_value(q_table, state_before_action, q_action)
    if next_state not in q_table:
        get_best_action(q_table, next_state, game_state["dog_position"])
    next_actions = q_table.get(next_state)
    best_next_q_value = max(next_actions.values()) if next_actions else 0.0

    td_target = reward + DISCOUNT_FACTOR * best_next_q_value
    new_q = current_q + LEARNING_RATE * (td_target - current_q)
    set_q_value(q_table, state_before_action, q_action, new_q)


def apply_environment_effects(new_pos):
    """Update carry/drop state after the dog reaches a target."""
    mission_completed = False
    picked_bone = False

    if not game_state["has_bone"] and new_pos == game_state["bone_position"]:
        game_state["has_bone"] = True
        game_state["bone_position"] = new_pos
        picked_bone = True
    elif game_state["has_bone"] and new_pos == game_state["home_position"]:
        game_state["bone_position"] = new_pos
        game_state["has_bone"] = False
        spawn_new_bone()
        mission_completed = True
    elif game_state["has_bone"]:
        game_state["bone_position"] = new_pos

    return {
        "picked_bone": picked_bone,
        "mission_completed": mission_completed,
    }


def fetch_sequence():
    """Generate the next sequence of moves."""
    with _state_lock:
        return _fetch_sequence_unlocked()


def _fetch_sequence_unlocked():
    """Generate the next sequence of moves without acquiring the state lock."""
    steps = []

    mission_completed = False

    # Make 4 automatic moves
    prev_pos = None
    for _ in range(4):
        state_before_action = game_state["current_state"]
        old_pos = game_state["dog_position"]
        action = best_action(forbidden_pos=prev_pos)
        new_pos = move(old_pos, action)

        game_state["dog_position"] = new_pos
        game_state["move_count"] += 1
        prev_pos = old_pos

        target_pos = game_state["home_position"] if game_state["has_bone"] else game_state["bone_position"]
        old_dist = distance(old_pos, target_pos)
        new_dist = distance(new_pos, target_pos)

        reward = 0
        mission_completed = False
        picked_bone = False

        if (
            not game_state["has_bone"]
            and new_pos == game_state["bone_position"]
        ):
            reward = 10.0
            game_state["score"] += 10
            effect = apply_environment_effects(new_pos)
            picked_bone = effect["picked_bone"]
            mission_completed = effect["mission_completed"]

        elif (
            game_state["has_bone"]
            and new_pos == game_state["home_position"]
        ):
            reward = 20.0
            game_state["score"] += 20
            effect = apply_environment_effects(new_pos)
            picked_bone = effect["picked_bone"]
            mission_completed = effect["mission_completed"]
        elif new_pos == old_pos:
            # Wall bump penalty
            reward = -2.0
        else:
            apply_environment_effects(new_pos)

            # Direction reward / penalty (moving towards vs away from bone/home)
            if new_dist < old_dist:
                reward = 1.0
            elif new_dist > old_dist:
                reward = -1.0

            # Increased penalty for being on edges
            if is_near_boundary(new_pos):
                reward -= 0.5

        # Update current state AFTER has_bone is updated so next best_action() uses correct state
        game_state["current_state"] = get_current_state()
        update_q_value(state_before_action, action, reward, game_state["current_state"])

        steps.append(
            {
                "pos": {"x": new_pos[1], "y": new_pos[0]},
                "action": action,
                "reward": reward,
                "source": "automatic",
                "hasBone": game_state["has_bone"],
                "bonePos": (
                    {"x": new_pos[1], "y": new_pos[0]}
                    if game_state["has_bone"] or picked_bone or mission_completed
                    else {"x": game_state["bone_position"][1], "y": game_state["bone_position"][0]}
                ),
                "carriedBone": game_state["has_bone"] or picked_bone or mission_completed,
                "pickedBone": picked_bone,
                "missionCompleted": mission_completed,
            }
        )

        if mission_completed:
            break

    if mission_completed:
        response = {
            "steps": steps,
            "awaitingUserReward": False,
            "missionCompleted": True,
            "congratulations": True,
        }
        response.update(_serialize_game_state_unlocked())
        return response

    # Get the next pending action
    pending_action = best_action()

    # Store state and action for when user provides reward
    game_state["pending_state"] = game_state["current_state"]
    game_state["pending_action"] = pending_action

    steps.append(
        {
            "pos": {"x": game_state["dog_position"][1], "y": game_state["dog_position"][0]},
            "action": pending_action,
            "reward": None,
            "source": "human",
            "hasBone": game_state["has_bone"],
            "bonePos": {"x": game_state["bone_position"][1], "y": game_state["bone_position"][0]},
            "carriedBone": game_state["has_bone"],
            "pickedBone": False,
            "missionCompleted": False,
        }
    )

    return {
        "steps": steps,
        "awaitingUserReward": True,
        **_serialize_game_state_unlocked(),
    }


def apply_reward(value):
    """
    Apply user's reward and update Q-table using Q-learning.
    
    Q-learning update formula:
    Q(s, a) = Q(s, a) + α * (r + γ * max(Q(s', a')) - Q(s, a))
    
    Args:
        value: +1 for positive reward, -1 for negative reward
    """
    with _state_lock:
        return _apply_reward_unlocked(value)


def _apply_reward_unlocked(value):
    """Apply user feedback without acquiring the state lock."""
    if game_state["pending_action"] is None or game_state["pending_state"] is None:
        return {"accepted": False}

    # Get state before taking the pending action
    state_before_action = game_state["pending_state"]
    action_taken = game_state["pending_action"]
    
    if value > 0:
        # Positive feedback: accept and execute the pending action
        new_pos = move(
            game_state["dog_position"],
            game_state["pending_action"],
        )
        env_reward = 0.0
        if not game_state["has_bone"] and new_pos == game_state["bone_position"]:
            env_reward = 10.0
        elif game_state["has_bone"] and new_pos == game_state["home_position"]:
            env_reward = 20.0

        game_state["dog_position"] = new_pos
        game_state["move_count"] += 1
        game_state["score"] += value + env_reward
        
        effect = apply_environment_effects(new_pos)
        learning_reward = float(value) + env_reward
    else:
        # Negative feedback: penalize action without moving dog into bad cell
        new_pos = game_state["dog_position"]
        game_state["score"] += value
        learning_reward = float(value)
        effect = {
            "picked_bone": False,
            "mission_completed": False,
        }

    # Update current state after applying feedback
    game_state["current_state"] = get_current_state()
    new_state = game_state["current_state"]

    update_q_value(state_before_action, action_taken, learning_reward, new_state)

    # Clear pending state and action
    game_state["pending_state"] = None
    game_state["pending_action"] = None

    return {
        "accepted": True,
        "missionCompleted": effect["mission_completed"],
        "congratulations": effect["mission_completed"],
        **_serialize_game_state_unlocked(),
    }
