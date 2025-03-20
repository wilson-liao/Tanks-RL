from Train import *
from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random
import pickle
import matplotlib.pyplot as plt

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Lambda, Input
from tensorflow.keras.models import Model

from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy, LinearAnnealedPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory
from rl.callbacks import Callback
import signal
import sys

from config import *
from TankGameEnv import TankEnv
import tensorflow as tf


def test(model, total_episodes, path):
    rewards = []
    env = TankEnv()

    for i in range(total_episodes):
        state = env.reset()
        # agent.init_game_setting()
        done = False
        episode_reward = 0.0
        model.load_weights(path)
        #playing one game
        while(not done):
            action = agent.make_action(state, test=True)
            state, reward, done, info = env.step(action)
            episode_reward += reward

        rewards.append(episode_reward)
        print(rewards)
    print('Run %d episodes'%(total_episodes))
    print('Mean:', np.mean(rewards))

# dqn.load_weights('weights_duel_updated_reward/dqn_best_weights.h5f')
# test_scores = dqn.test(env, nb_episodes=2, visualize=True)
PATH_TO_MODEL = 'weights_duel_updated_reward/dqn_best_weights.h5f'
dqn = build_agent(model, actions)
test(dqn, 3, PATH_TO_MODEL)