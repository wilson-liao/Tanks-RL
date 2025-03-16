from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random
import pickle

from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.optimizers import Adam

from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

from config import *
from TankGameEnv import TankEnv

env = TankEnv()
EPISODES = 1000

states = env.observation_space.shape
actions = env.action_space.n
print("Observation space shape:", env.observation_space.shape)

def build_model(states, actions):
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + states))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    return model

def build_agent(model, actions):
    policy = BoltzmannQPolicy()
    memory = SequentialMemory(limit=50000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=10,
                   target_model_update=1e-2)
    return dqn


model = build_model(states, actions)
# model.summary()
dqn = build_agent(model, actions)
dqn.compile(Adam(learning_rate=0.001))

# Train the agent 
dqn.fit(env, nb_steps=10000, visualize=True, verbose=2)


# Save the trained weights
dqn.save_weights('dqn_weights.h5f', overwrite=True)

# Later, to load and test:
dqn.load_weights('dqn_weights.h5f')
test_scores = dqn.test(env, nb_episodes=10, visualize=True)






