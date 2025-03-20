import gymnasium as gym
import numpy as np
import math
import os
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

layer_dim = 32

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
            # nn.Linear(last_layer_dim_pi, last_layer_dim_pi), nn.ReLU()
        )
        # Value network
        self.value_net = nn.Sequential(
            nn.Linear(feature_dim, last_layer_dim_pi), nn.ReLU()
            # nn.Linear(last_layer_dim_pi, last_layer_dim_pi), nn.ReLU()
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


class EntropyDecayCallback(BaseCallback):
    def __init__(self, model, start_ent_coef=0.5, end_ent_coef=0.01, decay_steps=1000000, verbose=0):
        super(EntropyDecayCallback, self).__init__(verbose)
        self.model = model
        self.start_ent_coef = start_ent_coef
        self.end_ent_coef = end_ent_coef
        self.decay_steps = decay_steps
        
    def _on_step(self) -> bool:
        # Calculate current entropy coefficient based on progress
        progress = min(1.0, self.num_timesteps / self.decay_steps)
        current_ent_coef = self.start_ent_coef - progress * (self.start_ent_coef - self.end_ent_coef)
        
        # Update the entropy coefficient in the model
        self.model.ent_coef = current_ent_coef
        
        if self.verbose > 0 and self.n_calls % 10000 == 0:
            print(f"Current entropy coefficient: {current_ent_coef:.5f}")
            
        return True

class CombinedCallback(BaseCallback):
    def __init__(self, callbacks):
        super(CombinedCallback, self).__init__()
        self.callbacks = callbacks
        
    def _on_step(self):
        return all(callback._on_step() for callback in self.callbacks)

def generate_demonstrations(env, num_demos=1000000):
    """Generate demonstrations using a simple rule-based policy"""
    demonstrations = []
    filepath = "demonstrations.txt"
    obs = env.reset()
    traj = 0
    for _ in range(num_demos):
        # Simple rule-based policy: aim at nearest enemy and shoot
        enemy_pos = env.get_enemy_locations()[0]
        player_pos = env.get_player_location()
        
        # Calculate direction to aim
        angle = math.atan2(enemy_pos[1] - player_pos[1], enemy_pos[0] - player_pos[0])
        target_angle = (math.degrees(angle) + 90) % 360
        

        shooter_angle = env.player_tank.shooter_angle
        # Determine shortest rotation direction
        angle_diff = (target_angle - shooter_angle) % 360
        if angle_diff > 180:
            turn = 2
        else:
            turn = 1

        # Convert to action
        if abs((shooter_angle - target_angle) % 360) > ANGLE_TOLERANCE:
            action = turn
        else:
            # Once aligned, shoot
            action = 0

        # print(f"shooter_angle: {shooter_angle}, target_angle: {target_angle}, angle_diff: {angle_diff}, Action: {action}")
        
        # Execute action
        next_obs, reward, done, info = env.step(action)
        
        # Store demonstration
        demonstrations.append((obs, action))
        
        obs = next_obs if not done else env.reset()
        if done:
            traj += 1
        
    print(f"Trajectory: {traj}")

    with open(filepath, "w") as f:
        for demo in demonstrations:
            f.write(f"{demo}\n")

    
    return demonstrations


def load_demonstrations(file_path):
    """
    Load demonstrations from a file.
    Each line should contain a tuple of (state, action).
    """
    demonstrations = []
    
    with open(file_path, 'r') as f:
        content = f.read()
        # Split by closing parenthesis followed by newline to get complete entries
        entries = content.split(')\n')
        
        for entry in entries:
            if entry.strip():  # Skip empty entries
                # Add the closing parenthesis back
                entry = entry + ')'
                try:
                    # Use numpy in the evaluation context
                    demo = eval(entry, {"array": np.array, "dtype": np.dtype, "float32": np.float32})
                    demonstrations.append(demo)
                except Exception as e:
                    print(f"Error parsing entry: {e}")
                    continue
    
    return demonstrations


# Use demonstrations to pre-train or guide the policy
def pretrain_from_demos(model, demonstrations, epochs=1000):
    """Pre-train the model using demonstrations in a way compatible with SB3"""
    # Extract data from demonstrations
    states = np.array([demo[0] for demo in demonstrations])
    actions = np.array([demo[1] for demo in demonstrations])
    
    # Create a small buffer of demonstration data
    buffer_size = len(demonstrations)
    
    # Manual pre-training using the policy's optimizer
    optimizer = th.optim.Adam(model.parameters(), lr=3e-4)
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(epochs):
        total_loss = 0
        num_batches = 0
        
        # Sample random batch
        batch_indices = np.random.randint(0, buffer_size, size=min(64, buffer_size))
        batch_states = th.FloatTensor(states[batch_indices])
        batch_actions = th.LongTensor(actions[batch_indices])
        
        # Get action distribution from policy
        logits = model(batch_states)
        loss = criterion(logits, batch_actions)
        
        # Compute imitation loss (negative log likelihood)
        total_loss += loss.item()
        num_batches += 1
        
        # Optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if epoch % 2 == 0:
            print(f"Epoch {epoch}, Loss: {total_loss/num_batches:.4f}")
    
    print(f"Pre-training completed with {epochs} epochs")
    return model

if __name__=="__main__":
    env = TankEnv()
    # Define the PPO model
    model = nn.Sequential(
        nn.Linear(env.observation_space.shape[0], 256), nn.ReLU(),
        nn.Linear(256, env.action_space.n)
    )
    # model = PPO(
    #     CustomActorCriticPolicy,
    #     env,
    #     verbose=1,
    #     n_steps=2048,
    #     batch_size=64,
    #     gae_lambda=0.95,
    #     gamma=0.99,
    #     learning_rate=3e-3,
    #     clip_range=0.2,
    #     ent_coef=0.1,  # Starting entropy coefficient (high for exploration)
    #     device="cpu"
    # )
    # try:
    #     model.load("ppo_tank_model")
    # except:
    #     pass

    try:
        # Load model if it exists
        model.load_state_dict(th.load("sequential_tank_model.pt"))
        print("Loaded existing model")
    except:
        print("No existing model found, starting fresh")
        pass
    
    # Save the model
    th.save(model.state_dict(), "sequential_tank_model.pt")
    
    # Create callbacks
    # render_callback = RenderCallback(env.envs[2], render_freq=4, model=model)
    # entropy_callback = EntropyDecayCallback(model=model, start_ent_coef=0.1, end_ent_coef=0.01, decay_steps=EPISODES*0.8)
    # combined_callback = CombinedCallback([render_callback, entropy_callback])
    
    # Create environment for demonstrations
    demo_env = TankEnv()
    
    # Generate demonstrations
    if not os.path.exists("demonstrations.txt"):
        demos = generate_demonstrations(demo_env)
    else:
        demos = load_demonstrations("demonstrations.txt")
    
    # Pre-train the model using demonstrations
    model = pretrain_from_demos(model, demos)
    
    # Continue with regular training
    # model.learn(total_timesteps=EPISODES, callback=combined_callback)


    print("TESTING MODEL")

    test_env = env
    obs = test_env.reset()
    for _ in range(10000000):
        # Convert NumPy array to PyTorch tensor
        obs_tensor = th.FloatTensor(obs)
        actions = model(obs_tensor)
        action = actions.argmax().item()
        obs, reward, done, info = test_env.step(action)
        test_env.render()
        # test_env.render(mode="OTHER")
        if done:
            obs = test_env.reset()


    