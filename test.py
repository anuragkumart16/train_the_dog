from environment import DogEnv

env = DogEnv()

state, _ = env.reset()

print("Initial state:", state)

for action in [3, 3, 3]:
    state, reward, done, _, _ = env.step(action)
    print("State:", state, "Reward:", reward, "Done:", done)