import random


GRID_SIZE = 5


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
}


def random_position():
    """Generate a random position inside the 5x5 grid."""
    return (
        random.randint(0, GRID_SIZE - 1),
        random.randint(0, GRID_SIZE - 1),
    )
def create_game():
    """Create a new game."""

    game_state["dog_position"] = random_position()
    game_state["bone_position"] = random_position()
    game_state["home_position"] = random_position()

    game_state["has_bone"] = False
    game_state["score"] = 0
    game_state["move_count"] = 0

    game_state["pending_state"] = None
    game_state["pending_action"] = None

    return game_state
def reset_environment():
    """Reset the game environment while keeping the Q-table."""

    game_state["dog_position"] = random_position()
    game_state["bone_position"] = random_position()
    game_state["home_position"] = random_position()

    game_state["has_bone"] = False
    game_state["score"] = 0
    game_state["move_count"] = 0

    game_state["pending_state"] = None
    game_state["pending_action"] = None

    return game_state
def reset_training():
    """Reload the baseline Q-table without changing the game positions."""

    # pyrefly: ignore [missing-import]
    from q_table_store import load_baseline

    game_state["q_table"] = load_baseline()

    return game_state
def reset_all():
    """Reset both the game environment and the training knowledge."""

    reset_environment()
    reset_training()

    return game_state

    ACTIONS = ["up", "down", "left", "right"]


def move(position, action):
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


def best_action():
    dog = game_state["dog_position"]

    target = (
        game_state["home_position"]
        if game_state["has_bone"]
        else game_state["bone_position"]
    )

    dx = target[0] - dog[0]
    dy = target[1] - dog[1]

    if abs(dx) >= abs(dy):
        return "down" if dx > 0 else "up"
    else:
        return "right" if dy > 0 else "left"


def fetch_sequence():
    steps = []

    for _ in range(4):
        action = best_action()
        new_pos = move(game_state["dog_position"], action)

        game_state["dog_position"] = new_pos
        game_state["move_count"] += 1

        reward = 0

        if (
            not game_state["has_bone"]
            and new_pos == game_state["bone_position"]
        ):
            game_state["has_bone"] = True
            reward = 1

        elif (
            game_state["has_bone"]
            and new_pos == game_state["home_position"]
        ):
            reward = 5
            game_state["score"] += 5

        steps.append(
            {
                "pos": new_pos,
                "action": action,
                "reward": reward,
                "source": "automatic",
            }
        )

    pending_action = best_action()

    game_state["pending_state"] = game_state["dog_position"]
    game_state["pending_action"] = pending_action

    steps.append(
        {
            "pos": game_state["dog_position"],
            "action": pending_action,
            "reward": None,
            "source": "human",
        }
    )

    return {
        "steps": steps,
        "awaiting_user_reward": True,
    }


def apply_reward(value):
    if game_state["pending_action"] is None:
        return {"accepted": False}

    new_pos = move(
        game_state["dog_position"],
        game_state["pending_action"],
    )

    game_state["dog_position"] = new_pos
    game_state["move_count"] += 1
    game_state["score"] += value

    if (
        not game_state["has_bone"]
        and new_pos == game_state["bone_position"]
    ):
        game_state["has_bone"] = True

    game_state["pending_state"] = None
    game_state["pending_action"] = None

    return {
        "accepted": True,
        "dog_position": new_pos,
        "has_bone": game_state["has_bone"],
        "score": game_state["score"],
    }
