class QLearningAgent:

    ACTIONS = ("LEFT", "RIGHT", "UP", "DOWN")

    def __init__(self):
        self.q_table = {}

    def get_state(self, bone_direction, human_direction, bone_picked):
        return (
            bone_direction,
            human_direction,
            bone_picked
        )

    def initialize_state(self, state):
        if state not in self.q_table:
            self.q_table[state] = {
                action: 0.0
                for action in self.ACTIONS
            }

    def get_q_value(self, state, action):
        self.initialize_state(state)
        return self.q_table[state][action]

    def set_q_value(self, state, action, value):
        self.initialize_state(state)
        self.q_table[state][action] = value

    def get_best_action(self, state):
        self.initialize_state(state)

        return max(
            self.q_table[state],
            key=self.q_table[state].get
        )
