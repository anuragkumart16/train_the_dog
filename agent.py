import numpy as np


class QLearningAgent:

    def __init__(self, state_size, action_size):
        self.q_table = np.zeros((state_size, action_size))

        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

    def choose_action(self, state):

        # Explore
        if np.random.random() < self.epsilon:
            return np.random.randint(0, 4)

        # Exploit
        return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):

        old_value = self.q_table[state, action]

        best_next_value = np.max(self.q_table[next_state])

        new_value = old_value + self.learning_rate * (
            reward
            + self.discount_factor * best_next_value
            - old_value
        )

        self.q_table[state, action] = new_value

    def decay_epsilon(self):
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon * self.epsilon_decay
        )