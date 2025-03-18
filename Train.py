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
from rl.callbacks import Callback
import signal

from config import *
from TankGameEnv import TankEnv

env = TankEnv()

states = env.observation_space.shape
actions = env.action_space.n


def build_model(states, actions):
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + states))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(128, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    
    return model


def build_agent(model, actions):
    policy = LinearAnnealedPolicy(
        EpsGreedyQPolicy(),
        attr='eps',
        value_max=1.0,    # Start with 100% exploration
        value_min=0.1,    # End with 10% exploration
        value_test=0.05,  # Testing exploration rate
        nb_steps=EPISODES    # Number of steps for annealing
    )
    # policy = BoltzmannQPolicy(tau=0.01)
    memory = SequentialMemory(limit=500000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=100,
                   target_model_update=1e-2,
                   enable_double_dqn=True)  # Enable Double DQN
    return dqn


model = build_model(states, actions)
# model.summary()
dqn = build_agent(model, actions)
dqn.compile(Adam(learning_rate=LEARNING_RATE))

# Custom callback to save best weights and handle interruption
class TrainingCallback(Callback):
    def __init__(self):
        self.best_reward = float('-inf')
        self.interrupted = False
        
        # Set up signal handler for graceful interruption
        signal.signal(signal.SIGINT, self.interrupt_handler)
    
    def interrupt_handler(self, signum, frame):
        print('\nTraining interrupted. Saving best weights...')
        self.interrupted = True
    
    def on_episode_end(self, episode, logs={}):
        episode_reward = logs.get('episode_reward')
        if episode_reward > self.best_reward:
            self.best_reward = episode_reward
            self.model.save_weights('dqn_best_weights_stationary_bot.h5f', overwrite=True)
            print(f'\nNew best reward: {self.best_reward:.2f} - Saved weights')
        
        if self.interrupted:
            self.model.stop_training = True

# Create callback
training_callback = TrainingCallback()

# Modify training parameters
dqn.fit(env, nb_steps=EPISODES, visualize=True, verbose=1, callbacks=[training_callback])

# Test with visualization (now using best weights)
dqn.load_weights('dqn_best_weights_stationary_bot.h5f')
test_scores = dqn.test(env, nb_episodes=TEST_EPISODES, visualize=True)
print(test_scores)





