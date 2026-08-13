from environment import Environment
from config import no_of_training_episodes, degree_of_randomness
from q_learning_agent import QLearningAgent
from utils import (
    get_bone_direction,
    get_human_direction,
    should_explore,
    choose_random_action
)


GRID_SIZE = 5

ALPHA = 0.1
GAMMA = 0.9


def get_state(agent, env):
    bone_direction = get_bone_direction(
        env.get_dog_position(),
        env.get_bone_position()
    )

    human_direction = get_human_direction(
        env.get_dog_position(),
        env.get_human_position()
    )

    bone_picked = env.is_bone_picked()

    return agent.get_state(
        bone_direction,
        human_direction,
        bone_picked
    )


def perform_action(env, action):
    if action == "UP":
        return env.move_dog_up()

    if action == "DOWN":
        return env.move_dog_down()

    if action == "LEFT":
        return env.move_dog_left()

    if action == "RIGHT":
        return env.move_dog_right()

    raise ValueError(f"Unknown action: {action}")


def calculate_reward(env, moved):
    # Invalid movement
    if not moved:
        return -2, False

    # Dog reaches the bone
    if (
        not env.is_bone_picked()
        and env.get_dog_position() == env.get_bone_position()
    ):
        env.set_bone_picked()
        return 10, False

    # Dog returns to human with bone
    if (
        env.is_bone_picked()
        and env.get_dog_position() == env.get_human_position()
    ):
        return 20, True

    # Normal movement
    return -1, False


agent = QLearningAgent()


for episode in range(no_of_training_episodes):

    env = Environment(GRID_SIZE)

    env.init_grid()

    state = get_state(agent, env)

    done = False
    total_reward = 0
    steps = 0

    while not done:

        # --------------------------------
        # 1. Choose action
        # --------------------------------

        if should_explore(degree_of_randomness):
            action = choose_random_action()
        else:
            action = agent.get_best_action(state)

        # --------------------------------
        # 2. Perform action
        # --------------------------------

        moved, grid = perform_action(env, action)

        # --------------------------------
        # 3. Calculate reward
        # --------------------------------

        reward, done = calculate_reward(env, moved)

        total_reward += reward
        steps += 1

        # --------------------------------
        # 4. Get new state
        # --------------------------------

        new_state = get_state(agent, env)

        # --------------------------------
        # 5. Calculate target
        # --------------------------------

        agent.initialize_state(state)
        agent.initialize_state(new_state)

        best_next_q = max(
            agent.q_table[new_state].values()
        )

        target = reward + GAMMA * best_next_q

        # --------------------------------
        # 6. Calculate TD error
        # --------------------------------

        old_q = agent.get_q_value(state, action)

        td_error = target - old_q

        # --------------------------------
        # 7. Update Q-value
        # --------------------------------

        new_q = old_q + ALPHA * td_error

        agent.set_q_value(
            state,
            action,
            new_q
        )

        # --------------------------------
        # 8. Move to next state
        # --------------------------------

        state = new_state

    # print(
    #     f"Episode: {episode + 1:4} | "
    #     f"Steps: {steps:3} | "
    #     f"Reward: {total_reward:4}"
    # )

with open("q_table.py", "w") as file:
    file.write("Q_TABLE = ")
    file.write(repr(agent.q_table))