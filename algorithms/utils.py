import random


DIRECTIONS = ("LEFT", "RIGHT", "UP", "DOWN", "HERE")
ACTIONS = ("LEFT", "RIGHT", "UP", "DOWN")


def get_direction(source_x, source_y, target_x, target_y):
    """
    Returns the direction of the target relative to the source.

    The dominant axis is used when the target is diagonally positioned.
    """

    dx = target_x - source_x
    dy = target_y - source_y

    # Same position
    if dx == 0 and dy == 0:
        return "HERE"

    # Choose the dominant axis
    if abs(dx) >= abs(dy):
        return "RIGHT" if dx > 0 else "LEFT"

    return "UP" if dy > 0 else "DOWN"


def get_bone_direction(dog_position, bone_position):
    """
    Returns the bone's direction relative to the dog.
    """

    dog_x, dog_y = dog_position
    bone_x, bone_y = bone_position

    return get_direction(
        dog_x,
        dog_y,
        bone_x,
        bone_y
    )


def get_human_direction(dog_position, human_position):
    """
    Returns the human's direction relative to the dog.
    """

    dog_x, dog_y = dog_position
    human_x, human_y = human_position

    return get_direction(
        dog_x,
        dog_y,
        human_x,
        human_y
    )


def should_explore(epsilon):
    """
    Determines whether the agent should explore.

    epsilon = probability of exploration.
    """

    if not 0 <= epsilon <= 1:
        raise ValueError("epsilon must be between 0 and 1")

    return random.random() < epsilon


def choose_random_action():
    """
    Selects a random action for exploration.
    """

    return random.choice(ACTIONS)