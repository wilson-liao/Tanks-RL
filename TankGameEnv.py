from gym import Env
from gym.utils import seeding
from gym.spaces import Discrete, Box
import numpy as np
import random
import math

from config import *
from Game import Game
from GameStateHandler import GameStateHandler, GameState
from Tank import Tank
from StatusBar import StatusBar
from InputHandler import InputHandler
from WallGenerator import WallGenerator
from CollisionDetector import CollisionDetector
from HeuristicBot import HeuristicBot
from RandomBot import RandomBot
from util import check_spawn_spot_occupied
import pygame


class TankEnv(Env):
    def __init__(self, mode = BOT_MODE):
        super().__init__()
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tank Game")
        self.clock = pygame.time.Clock()

         # self.game = Game()
        self.game_state_handler = GameStateHandler()

        self.mode = mode

        # Create a object groups
        self.tanks = []
        self.walls = []
        self.bullets = []


        # Create Objects
        self.player_tank = Tank(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, (0, 150, 0))
        self.tanks.append(self.player_tank)
        self.create_enemy_tanks(mode)

        # Create Status Bar
        self.status_bar = StatusBar(PLACEMENT, self.player_tank)
        

        self.input_handler = InputHandler()

        self.wall_generator = WallGenerator(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.wall_generator.generate_walls()
        self.walls.extend(self.wall_generator.walls)

        # Create Collision Detector
        self.collision_detector = CollisionDetector(self.tanks, self.walls, self.bullets)
        self.collision_detector.register_collision_handler()

        # Create Game State Handler
        self.game_state = GameState.MENU
        self.game_state_handler = GameStateHandler()  


        # Move forward, move backward, turn left, turn right,
        # turn turret left, turn turret right, shoot, do nothing
        self.action_space = Discrete(3)


        # Observation space includes:
        # - Player position (x, y)
        # - Player angle
        # - Player shooter angle
        # - Player health
        # - Player cooldown
        # - Enemy positions (x, y for each enemy)
        # - Enemy health
        # - Enemy cooldowns
        # - Bullet positions (x, y for each bullet)
        # - Bullet distances to player (distance for each bullet)
        self.max_bullets = 2
        enemy_position_size = NUMBER_OF_ENEMIES * 2  # x,y for each enemy
        enemy_health_size = NUMBER_OF_ENEMIES  # health for each enemy
        enemy_cooldown_size = NUMBER_OF_ENEMIES  # cooldown for each enemy
        bullet_position_size = self.max_bullets * 2  # x,y for bullets
        bullet_distance_size = self.max_bullets  # distance to player for each bullet
        
        # Create low array
        low_array = np.array(
            [0, 0] +  # Player position
            [0] +     # Player angle
            [0] +     # Player shooter angle
            [0] +     # Player health
            [0] +     # Player cooldown
            [0] * enemy_position_size +  # Enemy positions
            [0] * enemy_health_size +    # Enemy health
            [0] * enemy_cooldown_size +  # Enemy cooldowns
            [0] * bullet_position_size +  # Bullet positions
            [0] * bullet_distance_size,  # Bullet distances to player
            dtype=np.float32
        )
        
        # Create high array
        high_array = np.array(
            [WINDOW_WIDTH, WINDOW_HEIGHT] +  # Player position
            [360] +       # Player angle
            [360] +       # Player shooter angle
            [TANK_HEALTH] +  # Player health
            [BULLET_COOLDOWN] +  # Player cooldown
            [WINDOW_WIDTH, WINDOW_HEIGHT] * NUMBER_OF_ENEMIES +  # Enemy positions
            [TANK_HEALTH] * NUMBER_OF_ENEMIES +  # Enemy health
            [BULLET_COOLDOWN] * NUMBER_OF_ENEMIES +  # Enemy cooldowns
            [WINDOW_WIDTH, WINDOW_HEIGHT] * self.max_bullets +  # Bullet positions
            [np.sqrt(WINDOW_WIDTH**2 + WINDOW_HEIGHT**2)] * self.max_bullets,  # Bullet distances to player (max diagonal distance)
            dtype=np.float32
        )
        self.observation_space = Box(
            low=low_array,
            high=high_array,
            dtype=np.float32
        )

        self.state = self.get_all_info()
        self.train_time = 0
        self.total_reward_before_death = 0



    def step(self, action):
        # Handle events
        self.game_state, running = self.game_state_handler.update_game_state(self.tanks, self.player_tank)

        # Store player bullet positions before action for reward calculation
        player_bullets_before = [(bullet.x, bullet.y) for bullet in self.player_tank.bullets]

        # Convert action to game controls
        # if action == 0:  # Move forward
        #     self.player_tank.move()
        # elif action == 1:  # Move backward
        #     self.player_tank.move_backward()
        # elif action == 2:  # Rotate left
        #     self.player_tank.rotate(-1)
        # elif action == 3:  # Rotate right 
        #     self.player_tank.rotate(1)
        # elif action == 4:  # Rotate turret left
        #     self.player_tank.rotate_shooter(-1)
        # elif action == 5:  # Rotate turret right
        #     self.player_tank.rotate_shooter(1)
        # elif action == 6:  # Shoot
        #     self.player_tank.shoot()
        # elif action == 7:  # Idle
        #     pass

        if action == 0:  # Move forward
            self.player_tank.shoot()
        elif action == 1:  # Rotate turret right
            self.player_tank.rotate_shooter(1)
        elif action == 2:  # Rotate turret left
            self.player_tank.rotate_shooter(-1)
        else:
            pass


        # print(f"Action: {action}")
        
        # Enemy moves with collision checking
        for tank in self.tanks:
            if tank != self.player_tank:
                tank.take_action()
                
        

        # Update status bar
        self.status_bar.update(self.player_tank)

        # Update tanks
        for tank in self.tanks:
            if tank.cooldown < BULLET_COOLDOWN:
                tank.cooldown += 1


        # Update bullets
        for tank in self.tanks:
            for bullet in tank.bullets:
                if bullet.lifeTime >= BULLET_LIFETIME:
                    tank.bullets.remove(bullet)
                    del bullet
                else:
                    bullet.move()
        self.update_objects()

        # Check collisions
        player_health_prev = self.player_tank.health
        enemy_health_prev = {tank: tank.health for tank in self.tanks if tank != self.player_tank}
        self.bullets, self.tanks, self.walls, destroyed = \
            self.collision_detector.check_all_collisions(self.player_tank, self.tanks, self.walls, self.bullets)
        if destroyed:
            # print("DESTROYED")
            self.status_bar.player_score += 1

        # Calculate rewards with better scaling
        reward = 0.0  # No constant reward

        reward = self.add_trajectory_reward(reward)
        
        # Reward for hitting enemy (scaled down)
        for tank in self.tanks:
            if tank != self.player_tank and tank.health < enemy_health_prev[tank]:
                reward += 1.0  # More reasonable reward

        # Penalty for getting hit (scaled down)
        if player_health_prev > self.player_tank.health:
            reward -= 1.0  # More reasonable penalty
        
        # Reward for destroying enemy (scaled down)
        if destroyed:
            reward += 5.0  # More reasonable reward

        
        # Remove the penalty for not aiming at enemy
        
        done = False
        # Player wins (scaled reward based on remaining health)
        if len(self.tanks) == 1 and self.player_tank in self.tanks:
            time_factor = 1 - (self.train_time / TRAIN_TIME_LIMIT)  # Higher reward for winning faster
            reward += 10 + (self.player_tank.health / TANK_HEALTH) * time_factor * 5  # Normalized between 0 and 1
            done = True
            self.train_time = 0

        # Player dies/loses (scaled punishment based on remaining enemy health)
        if self.player_tank.health <= 0:
            total_enemy_health = sum([i.health for i in self.tanks])
            survival_factor = self.train_time / TRAIN_TIME_LIMIT  # Normalize survival time between 0 and 1
            reward -= 10 * (1 - survival_factor)  # Less penalty the longer it survives
            done = True
            self.train_time = 0

        # Clip final reward to stay within [-1, 1] range
        # reward = np.clip(reward, -1.0, 1.0)

        info = {}

        self.state = self.get_all_info()

        self.train_time += 1
        if self.train_time > TRAIN_TIME_LIMIT:
            done = True
            self.train_time = 0

        self.total_reward_before_death += reward

        return self.state, reward, done, info

    
    def reset(self, mode = BOT_MODE):
        # print("RESET, last reward:", self.total_reward_before_death)
        self.total_reward_before_death = 0
        # self.game = Game()
        self.game_state_handler = GameStateHandler()

        self.mode = mode

        # Create a object groups
        self.tanks = []
        self.walls = []
        self.bullets = []


        # Create Objects
        self.player_tank = Tank(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, (0, 150, 0))
        self.tanks.append(self.player_tank)
        self.create_enemy_tanks(mode)

        # Create Status Bar
        self.status_bar = StatusBar(PLACEMENT, self.player_tank)
        

        self.input_handler = InputHandler()

        self.wall_generator = WallGenerator(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.wall_generator.generate_walls()
        self.walls.extend(self.wall_generator.walls)

        # Create Collision Detector
        self.collision_detector = CollisionDetector(self.tanks, self.walls, self.bullets)
        self.collision_detector.register_collision_handler()

        # Create Game State Handler
        self.game_state = GameState.MENU
        self.game_state_handler = GameStateHandler()  

        return self.state
    

    def seed(self, seed=None):
        """
        Sets the random seed for the environment.
        """
        self.np_random, seed = seeding.np_random(seed)  # Creates a seeded RNG
        random.seed(seed)  # Seed Python's random module
        np.random.seed(seed)  # Seed NumPy's random module
        return [seed]

    def render(self, mode='rgb_array'):
        # Original render code
        self.screen.fill((200, 200, 200))
        self.status_bar.draw(self.screen)
        for wall in self.walls:
            wall.draw(self.screen)
        for tank in self.tanks:
            tank.draw(self.screen)
            for bullet in tank.bullets:
                bullet.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(60)



    ########### HELPER FUNCTIONS ###########

    def update_objects(self):
        self.bullets = []
        for tank in self.tanks:
            self.bullets.extend(tank.bullets)

    def create_enemy_tanks(self, mode = "heuristic"):
        for i in range(NUMBER_OF_ENEMIES):
            x = random.randint(30, WINDOW_WIDTH - 30)
            y = random.randint(30, WINDOW_HEIGHT - 30)
            # x = 100
            # y = 100
            while check_spawn_spot_occupied(x, y, self.tanks, self.walls):
                x = random.randint(30, WINDOW_WIDTH - 30)
                y = random.randint(30, WINDOW_HEIGHT - 30)

            if mode == "heuristic":
                self.enemy_tank = HeuristicBot(self, x, y, (150, 0, 0))
            elif mode == "random":
                self.enemy_tank = RandomBot(self, x, y, (150, 0, 0))


            self.tanks.append(self.enemy_tank)
    

    # GAME API
    def get_game_state(self):
        return self.game_state
    
    def get_all_info(self):
        # Instead of returning a tuple of different structures, create a flat numpy array
        observation = np.zeros(self.observation_space.shape[0], dtype=np.float32)
        
        # Player position (2 values)
        player_x, player_y = self.get_player_location()
        observation[0] = player_x
        observation[1] = player_y
        
        # Player angle (1 value)
        observation[2] = self.player_tank.angle
        
        # Player shooter angle (1 value)
        observation[3] = self.player_tank.shooter_angle

        # Player health (1 value)
        observation[4] = self.player_tank.health

        # Player cooldown (1 value)
        observation[5] = self.player_tank.cooldown
        
        # Enemy positions, health, and cooldowns
        enemy_locations = self.get_enemy_locations()
        current_idx = 6
        for i, (ex, ey) in enumerate(enemy_locations):
            if i < NUMBER_OF_ENEMIES:
                observation[current_idx + i*2] = ex
                observation[current_idx + i*2 + 1] = ey
        
        current_idx += NUMBER_OF_ENEMIES * 2
        for i, enemy in enumerate(self.tanks):
            if enemy != self.player_tank and i < NUMBER_OF_ENEMIES:
                observation[current_idx + i] = enemy.health

        current_idx += NUMBER_OF_ENEMIES
        for i, enemy in enumerate(self.tanks):
            if enemy != self.player_tank and i < NUMBER_OF_ENEMIES:
                observation[current_idx + i] = enemy.cooldown
        
        # Bullet positions
        current_idx += NUMBER_OF_ENEMIES
        enemy_bullet_info = self.get_enemy_bullet_info()
        for i, (bx, by, _, _) in enumerate(enemy_bullet_info):
            if i < self.max_bullets:
                observation[current_idx + i*2] = bx
                observation[current_idx + i*2 + 1] = by
        
        # Bullet distances to player
        current_idx += self.max_bullets * 2
        for i, (bx, by, _, _) in enumerate(enemy_bullet_info):
            if i < self.max_bullets:
                # Calculate Euclidean distance between bullet and player
                distance = np.sqrt((bx - player_x)**2 + (by - player_y)**2)
                observation[current_idx + i] = distance
        
        return observation
    
    def get_player_location(self):
        return self.player_tank.x, self.player_tank.y

    def get_enemy_locations(self):
        enemy_locations = []    
        for enemy in self.tanks:
            if enemy != self.player_tank:
                enemy_locations.append((enemy.x, enemy.y))
        return enemy_locations
    
    def get_all_bullet_info(self):
        bullet_info = []
        for bullet in self.bullets:
            bullet_info.append((bullet.x, bullet.y, bullet.angle, bullet))
        return bullet_info
    
    def get_enemy_bullet_info(self):
        enemy_bullet_info = []
        for bullet in self.bullets:
            if bullet.tank != self.player_tank:
                enemy_bullet_info.append((bullet.x, bullet.y, bullet.angle, bullet))
        return enemy_bullet_info

    def get_wall_info(self):
        wall_info = []
        for wall in self.walls:
            wall_info.append((wall.x, wall.y, wall.width, wall.height))
        return wall_info

    def add_trajectory_reward(self, reward):
        """Add reward based on how close bullets are to the line connecting player to enemies"""
        enemy_angles = []
        for enemy in self.tanks:
            if enemy != self.player_tank:
                angle = (math.degrees(self.calculate_enemy_angle_from_player((enemy.x, enemy.y)))+90) % 360
                enemy_angles.append(angle)
                # print(self.player_tank.shooter_angle, angle)

        
        for angle in enemy_angles:
            if abs(self.player_tank.shooter_angle - angle) < ANGLE_TOLERANCE:
                # print("ANGLE MATCH")
                reward += 1
            # else:
            #     reward -= 1
        
        return reward

    
    def calculate_enemy_angle_from_player(self, enemy_position):
        angle = math.atan2(enemy_position[1] - self.player_tank.y, enemy_position[0] - self.player_tank.x)
        return angle
    
    # def point_to_line_distance(self, px, py, x1, y1, x2, y2):
    #     """Calculate the distance from point (px,py) to line defined by points (x1,y1) and (x2,y2)"""
    #     # Line length
    #     line_length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
    #     # If line has zero length, return distance to the point
    #     if line_length == 0:
    #         return np.sqrt((px - x1)**2 + (py - y1)**2)
        
    #     # Calculate the distance using the formula for point-to-line distance
    #     return abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1) / line_length
