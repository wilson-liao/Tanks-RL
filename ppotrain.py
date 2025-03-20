import gymnasium as gym
import numpy as np

from TankGameEnv import TankEnv

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback
from config import *

from gymnasium import spaces
import torch as th
from torch import nn

from stable_baselines3.common.policies import ActorCriticPolicy
from typing import Callable, Tuple


class RenderCallback(BaseCallback):
    def __init__(self, env, render_freq=4, model=None, verbose=0):
        super(RenderCallback, self).__init__(verbose)
        self.env = env
        self.render_freq = render_freq
        self.render_time = 5000
        self.model = model
        self.save_freq = self.render_time * self.render_freq

    def _on_step(self) -> bool:
        # Render the environment every `render_freq` steps
        # print(self.n_calls, self.num_timesteps)
        if (self.n_calls // self.render_time) % self.render_freq == 0:
            self.env.render()
        if self.n_calls % self.save_freq == 0:
            self.model.save("ppo_tank_model")
        return True  # Continue training

    # def on_rollout_end(self) -> None:
    #     print(f'Rollout end: {self.env.reward}')

layer_dim = 128

class CustomNetwork(nn.Module):
    """
    Custom network for policy and value function.
    It receives as input the features extracted by the features extractor.

    :param feature_dim: dimension of the features extracted with the features_extractor (e.g. features from a CNN)
    :param last_layer_dim_pi: (int) number of units for the last layer of the policy network
    :param last_layer_dim_vf: (int) number of units for the last layer of the value network
    """

    def __init__(
        self,
        feature_dim: int,
        last_layer_dim_pi: int = layer_dim,
        last_layer_dim_vf: int = layer_dim,
    ):
        super().__init__()

        # IMPORTANT:
        # Save output dimensions, used to create the distributions
        self.latent_dim_pi = last_layer_dim_pi
        self.latent_dim_vf = last_layer_dim_vf

        # Policy network
        self.policy_net = nn.Sequential(
            nn.Linear(feature_dim, last_layer_dim_pi), nn.ReLU()
        )
        # Value network
        self.value_net = nn.Sequential(
            nn.Linear(feature_dim, last_layer_dim_vf), nn.ReLU()
        )

    def forward(self, features: th.Tensor) -> Tuple[th.Tensor, th.Tensor]:
        """
        :return: (th.Tensor, th.Tensor) latent_policy, latent_value of the specified network.
            If all layers are shared, then ``latent_policy == latent_value``
        """
        return self.forward_actor(features), self.forward_critic(features)

    def forward_actor(self, features: th.Tensor) -> th.Tensor:
        return self.policy_net(features)

    def forward_critic(self, features: th.Tensor) -> th.Tensor:
        return self.value_net(features)


class CustomActorCriticPolicy(ActorCriticPolicy):
    def __init__(
        self,
        observation_space: spaces.Space,
        action_space: spaces.Space,
        lr_schedule: Callable[[float], float],
        *args,
        **kwargs,
    ):
        # Disable orthogonal initialization
        kwargs["ortho_init"] = False
        super().__init__(
            observation_space,
            action_space,
            lr_schedule,
            # Pass remaining arguments to base class
            *args,
            **kwargs,
        )


    def _build_mlp_extractor(self) -> None:
        self.mlp_extractor = CustomNetwork(self.features_dim, last_layer_dim_pi=256, last_layer_dim_vf=256)


if __name__=="__main__":
    env = make_vec_env(
        TankEnv, 
        n_envs=8
    )
   # Define the PPO model
    model = PPO(
        CustomActorCriticPolicy,  # Multi-layer perceptron policy
        env,          # Your environment
        verbose=1,    # Verbosity level
        n_steps=1000000, # Number of steps to run for each environment per update
        batch_size=64, # Minibatch size
        gae_lambda=0.95, # GAE parameter
        gamma=0.99,  # Discount factor
        learning_rate=5e-3, # Learning rate
        clip_range=0.2,  # Clipping range
        ent_coef=0.5,   # Entropy coefficient for exploration
        device="cpu"
    )
    try:
        model.load("ppo_tank_model")
    except:
        pass
    model.learn(total_timesteps=EPISODES, callback=RenderCallback(env.envs[1], render_freq=4, model=model))
    # model.learn(total_timesteps=EPISODES)
    model.save("ppo_tank_model")

    model = PPO.load("ppo_tank_model")
    print("TESTING MODEL")

    test_env = env
    obs = test_env.reset()
    for _ in range(10000000):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, done, info = test_env.step(action)
        done = done[0]
        test_env.envs[0].render()
        # test_env.render(mode="OTHER")
        if done:
            obs = test_env.reset()


    