from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random
import pickle

from keras.models import Sequential, Model
from keras.layers import Dense, Flatten, Input, Lambda, Softmax
from keras.optimizers import Adam, RMSprop
import keras.backend as K

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

layers = [256]
MODEL_SAVE_PATH = f"models/dqn_best_weights_heuristic_bot"
for layer in layers:
    MODEL_SAVE_PATH += f"_{layer}"
MODEL_SAVE_PATH += ".h5f"
# dqn_best_weights_heuristic_bot.h5f

def build_model(states, actions):
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + states))
    # model.add(Dense(64, activation='relu'))
    for layer in layers:
        model.add(Dense(layer, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    
    return model

def build_agent(model, actions):
    # Enhanced Linear Annealed Policy with longer exploration
    policy = LinearAnnealedPolicy(
        EpsGreedyQPolicy(),
        attr='eps',
        value_max=0.3,    # Start with 100% exploration
        value_min=0.1,   # End with 5% exploration (slightly lower)
        value_test=0.05,  # Lower test exploration
        nb_steps=EPISODES * 0.1  # Anneal over 70% of total episodes
    )
    # policy = BoltzmannQPolicy(tau=0.5)
    # policy = EpsGreedyQPolicy(eps=0.1)
    
    memory = SequentialMemory(limit=1000000, window_length=1)  # Larger memory
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=2000,  # More warmup steps
                   target_model_update=1e-2,
                   enable_double_dqn=True) 
    return dqn


model = build_model(states, actions)
# model.summary()
dqn = build_agent(model, actions)
# dqn.compile(Adam(learning_rate=LEARNING_RATE))
dqn.compile(RMSprop(learning_rate=LEARNING_RATE))

# Custom callback to save best weights and handle interruption
class TrainingCallback(Callback):
    def __init__(self):
        self.best_reward = float('-inf')
        self.interrupted = False
        
        # Set up signal handler for graceful interruption
        # signal.signal(signal.SIGINT, self.interrupt_handler)
    
    def interrupt_handler(self, signum, frame):
        print('\nTraining interrupted. Saving best weights...')
        self.interrupted = True
    
    def on_episode_end(self, episode, logs={}):
        episode_reward = logs.get('episode_reward')
        if episode_reward > self.best_reward:
            self.best_reward = episode_reward
            self.model.save_weights(MODEL_SAVE_PATH, overwrite=True)
            print(f'\nNew best reward: {self.best_reward:.2f} - Saved weights')
        else:
            print(f'\nEpisode {episode} reward: {episode_reward:.2f}')
        
        if self.interrupted:
            self.model.stop_training = True

# Create callback
training_callback = TrainingCallback()

# Load existing weights if they exist
try:
    dqn.load_weights(MODEL_SAVE_PATH)
    print("Successfully loaded existing weights")
except Exception as e:
    print("No existing weights found, starting fresh training")

# Modify training parameters
dqn.fit(env, nb_steps=EPISODES, visualize=True, verbose=1, callbacks=[training_callback])

# Save final weights
# dqn.save_weights('dqn_final_weights_heuristic_bot.h5f', overwrite=True)

# Test with visualization (using best weights)
print("\nTesting with best weights:")
dqn.load_weights(MODEL_SAVE_PATH)
test_scores = dqn.test(env, nb_episodes=TEST_EPISODES, visualize=True)
print("Test scores with best weights:", test_scores.history['episode_reward'])





