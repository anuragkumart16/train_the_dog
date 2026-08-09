from environment import DogEnv
from agent import QLearningAgent

env = DogEnv()

agent = QLearningAgent(
    state_size=25,
    action_size=4
)

episodes = 5000

for episode in range(episodes):

    state, _ = env.reset()
    total_reward = 0

    while True:

        action = agent.choose_action(state)

        next_state, reward, done, _, _ = env.step(action)

        agent.learn(
            state,
            action,
            reward,
            next_state
        )

        state = next_state
        total_reward += reward

        if done:
            break

    agent.decay_epsilon()

    if episode % 500 == 0:
        print(
            f"Episode: {episode}, "
            f"Reward: {total_reward:.2f}, "
            f"Epsilon: {agent.epsilon:.2f}"
        )