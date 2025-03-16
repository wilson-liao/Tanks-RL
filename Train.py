from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random


from config import *
from TankGameEnv import TankEnv

env = TankEnv()


episodes = 1000
for episode in range(episodes):
    state = env.reset()
    done = False
    score = 0

    while not done:
        env.render()
        action = env.action_space.sample()
        next_state, reward, done, info = env.step(action)
        score += reward
    
    print(f"Episode {episode} Score: {score}")


    
        

