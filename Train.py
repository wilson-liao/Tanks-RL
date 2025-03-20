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

env = TankEnv()

states = env.observation_space.shape
actions = env.action_space.n



def build_model(states, actions):
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + states))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(actions, activation='linear'))
    
    return model

def build_dueling_model(states, actions):
    inputs = Input(shape=(1,) + states)
    x = Flatten()(inputs)
    x = Dense(24, activation="relu")(x)
    x = Dense(24, activation="relu")(x)

    # Split into Value and Advantage Streams
    value = Dense(1, activation="linear")(x)  # V(s)
    advantage = Dense(actions, activation="linear")(x)  # A(s, a)

    # Combine the two streams
    q_values = Lambda(lambda a: a[0] + (a[1] - tf.reduce_mean(a[1], axis=1, keepdims=True)),
                      output_shape=(actions,))([value, advantage])

    model = Model(inputs=inputs, outputs=q_values)
    return model



def build_agent(model, actions):
    policy = LinearAnnealedPolicy(
        EpsGreedyQPolicy(),
        attr='eps',
        value_max=1.0,    # Start with 100% exploration
        value_min=0.05,    # End with 10% exploration
        value_test=0.05,  # Testing exploration rate
        nb_steps=30000    # Number of steps for annealing
    )
    # policy = BoltzmannQPolicy(tau=0.01)
    memory = SequentialMemory(limit=5000000, window_length=1)
    dqn = DQNAgent(model=model, memory=memory, policy=policy,
                   nb_actions=actions, nb_steps_warmup=100,
                   target_model_update=1e-2)
    return dqn


# model = build_model(states, actions)
model = build_dueling_model(states, actions)
# model.summary()
dqn = build_agent(model, actions)
dqn.compile(Adam(learning_rate=0.005))
reward_history = []
episode_history = []

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
        print("[INFO] Exiting program.")
        plt.figure(figsize=(10,5))
        plt.plot(episode_history, reward_history, label="Episode Reward", color="b")
        plt.xlabel("Episode")
        plt.ylabel("Total Reward")
        plt.title("Reward Progression Over Training")
        plt.legend()
        plt.grid()
        plt.show()
        graph_path = "training_logs/reward_progression.png"
        plt.savefig(graph_path, dpi=300)

        sys.exit(0)
    
    def on_episode_end(self, episode, logs={}):
        episode_reward = logs.get('episode_reward')
        reward_history.append(episode_reward)
        episode_history.append(episode)

        if episode_reward > self.best_reward:
            self.best_reward = episode_reward
            self.model.save_weights('dqn_best_weights.h5f', overwrite=True)
            print(f'\nNew best reward: {self.best_reward:.2f} - Saved weights')
        
        if self.interrupted:
            self.model.stop_training = True

# Create callback
training_callback = TrainingCallback()

# Modify training parameters
dqn.fit(env, nb_steps=5000000, visualize=True, verbose=1, callbacks=[training_callback])

# Test with visualization (now using best weights)
dqn.load_weights('dqn_best_weights.h5f')
test_scores = dqn.test(env, nb_episodes=5, visualize=True)
print(test_scores)





