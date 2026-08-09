import gymnasium as gym
from gymnasium import spaces
import numpy as np


class DogEnv(gym.Env):

    def __init__(self):
        self.observation_space = spaces.Discrete(25)
        self.action_space = spaces.Discrete(4)

        # 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT
        self.dog = [2, 1]

        self.bone = [2, 4]
        self.player = [4, 2]

        self.obstacles = [(1, 2), (3, 2)]

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.dog = [2, 1]

        return self.get_state(), {}

    def get_state(self):
        # Convert (row, column) into a single number
        return self.dog[0] * 5 + self.dog[1]

    def step(self, action):

        moves = {
            0: (-1, 0),
            1: (1, 0),
            2: (0, -1),
            3: (0, 1)
        }

        dy, dx = moves[action]

        new_position = [
            self.dog[0] + dy,
            self.dog[1] + dx
        ]

        reward = -0.01
        terminated = False

        # Don't allow walking outside grid
        if not (
            0 <= new_position[0] < 5
            and 0 <= new_position[1] < 5
        ):
            reward = -1

        # Don't allow walking through obstacles
        elif tuple(new_position) in self.obstacles:
            reward = -1

        else:
            self.dog = new_position

        # Reached bone
        if self.dog == self.bone:
            reward = 10
            terminated = True

        return self.get_state(), reward, terminated, False, {}