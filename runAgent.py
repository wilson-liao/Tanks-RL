
from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random
import pickle

from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.optimizers import Adam

from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy, LinearAnnealedPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory

from config import *
from TankGameEnv import TankEnv

env = TankEnv()

states = env.observation_space.shape
actions = env.action_space.n
print(states)


def build_model(states, actions):
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + states))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    
    return model


def build_agent(model, actions):
    policy = LinearAnnealedPolicy(
        EpsGreedyQPolicy(),
        attr='eps',
        value_max=1.0,    # Start with 100% exploration
        value_min=0.1,    # End with 10% exploration
        value_test=0.05,  # Testing exploration rate
        nb_steps=50000    # Number of steps for annealing
    )
    memory = SequentialMemory(limit=50000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=100,
                   target_model_update=1e-2)
    return dqn


model = build_model(states, actions)
dqn = build_agent(model, actions)
dqn.compile(Adam(learning_rate=0.01))

# Later, to load and test:
dqn.load_weights('dqn_best_weights_stationary_bot.h5f')
test_scores = dqn.test(env, nb_episodes=10, visualize=True)
print(test_scores)
