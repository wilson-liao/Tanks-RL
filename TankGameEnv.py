from gym import Env
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
from TrainingBot import TrainingBot
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
        # self.action_space = Discrete(8)
        self.action_space = Discrete(3)
        self.skill_level = 0
        self.training_progress = 0


        # Observation space includes:
        # - Player position (x, y)
        # - Player angle
        # - Player shooter angle
        # - Enemy positions (x, y for each enemy)
        # - Enemy angles
        # - Enemy shooter angles
        # - Bullet positions (x, y for each bullet)
        # - Wall positions (x, y, width, height for each wall)
        # Calculate total size of observation space
        self.max_bullets = 10
        self.max_walls = 4
        enemy_position_size = NUMBER_OF_ENEMIES * 2  # x,y for each enemy
        enemy_angle_size = NUMBER_OF_ENEMIES  # angle for each enemy
        enemy_shooter_size = NUMBER_OF_ENEMIES  # shooter angle for each enemy
        bullet_position_size = self.max_bullets * 2  # x,y for max 100 bullets 
        wall_position_size = self.max_walls * 4  # x,y,w,h for max 50 walls
        
        # Create low array
        low_array = np.array(
            [0, 0] +  # Player position
            [0] +     # Player angle
            [0] +     # Player shooter angle
            [0] * enemy_position_size +  # Enemy positions
            [0] * enemy_angle_size +     # Enemy angles
            [0] * enemy_shooter_size +   # Enemy shooter angles
            [0] * bullet_position_size + # Bullet positions
            [0] * wall_position_size,    # Wall positions
            dtype=np.float32
        )
        
        # Create high array
        high_array = np.array(
            [WINDOW_WIDTH, WINDOW_HEIGHT] +  # Player position
            [360] +       # Player angle
            [360] +       # Player shooter angle
            [WINDOW_WIDTH, WINDOW_HEIGHT] * NUMBER_OF_ENEMIES +  # Enemy positions
            [360] * NUMBER_OF_ENEMIES +  # Enemy angles  
            [360] * NUMBER_OF_ENEMIES + # Enemy shooter angles
            [WINDOW_WIDTH, WINDOW_HEIGHT] * self.max_bullets +  # Bullet positions
            [WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT] * self.max_walls,  # Wall positions
            dtype=np.float32
        )
        self.observation_space = Box(
            low=low_array,
            high=high_array,
            dtype=np.float32
        )

        self.state = self.get_all_info()
        self.train_time = 0


    def step(self, action):
        # Handle events
        self.game_state, running = self.game_state_handler.update_game_state(self.tanks, self.player_tank)
        self.training_progress += 1

        # Gradually improve opponent based on progress (0 = pure random, 1 = full heuristic)
        self.skill_level = self.training_progress / 10000


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
        # print(f"Action: {action}")
        if action ==0:
            self.player_tank.rotate_shooter(-1)
        elif action == 1:  # Rotate turret right
            self.player_tank.rotate_shooter(1)
        elif action == 2:  # Shoot
            self.player_tank.shoot()
        elif action == 3:  # Idle
            pass
        
        # # Enemy moves with collision checking
        # for tank in self.tanks:
        #     if tank != self.player_tank:
        #         if isinstance(tank, TrainingBot):
        #             tank.take_action(self.skill_level)
        #         else:
        #             tank.take_action()
                
        

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
        self.bullets, self.tanks, self.walls, destroyed = self.collision_detector.check_all_collisions(self.tanks, self.walls, self.bullets)
        if destroyed:
            self.status_bar.player_score += 1


        reward = 0
        # Player hits enemy
        for tank in self.tanks:
            if tank != self.player_tank and tank.health < enemy_health_prev[tank]:
                reward += 5000

        # Player gets hit
        if player_health_prev > self.player_tank.health:
            reward -= 50

        # Player destroys enemy
        if destroyed:
            reward += 500

        done = False
        # Player wins
        if len(self.tanks) == 1 and self.player_tank in self.tanks:
            reward += 10 * self.player_tank.health
            done = True

        # Player dies/loses
        if self.player_tank.health <= 0:
            reward -= (10 * sum([i.health for i in self.tanks]) + 10 * (1-(self.train_time // TRAIN_TIME_LIMIT)))*100
            done = True

        # if barrel is within 3 degrees of the enemy
        # total aiming should be around 50 points
        if self.get_enemy_locations():
            target_angle = (math.degrees(self.calculate_enemy_angle(self.player_tank.x, self.player_tank.y, self.get_enemy_locations()[0])) + 90) % 360
            angle_diff = (self.player_tank.shooter_angle - target_angle)%360
            # aim_reward = 0
            if angle_diff <= 45:
                reward += 0.01
            if angle_diff <= 10:
                print("Aimed correctly")
                reward += 5
            else:
                reward -= 1
            # print("AIM REWARD: ", aim_reward, " TOTAL REWARD: ", reward)
            # reward += (aim_reward/self.training_progress)*80
            # print("REWARD AFTER WEIGHTED SUM: ", reward)
    
        info = {}

        self.state = self.get_all_info()

        self.train_time += 1
        if self.train_time > TRAIN_TIME_LIMIT:
            done = True
            self.train_time = 0

        return self.state, reward, done, info
    
    def calculate_enemy_angle(self, x, y, enemy_position):
        angle = math.atan2(enemy_position[1] - y, enemy_position[0] - x)
        return angle

    
    def reset(self, mode = BOT_MODE):
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


    # def render2(self, mode='rgb_array'):
    #     if mode == 'rgb_array':
    #         # Get the pygame surface as a RGB array
    #         self.screen.fill((200, 200, 200))

    #         # Draw all game elements
    #         self.status_bar.draw(self.screen)
    #         for wall in self.walls:
    #             wall.draw(self.screen)
    #         for tank in self.tanks:
    #             tank.draw(self.screen)
    #             for bullet in tank.bullets:
    #                 bullet.draw(self.screen)
                
    #         pygame.display.flip()
    #         self.clock.tick(30)
    #         return np.transpose(
    #             np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
    #         )
    #     elif mode == 'human':
    #         # Original render code
    #         self.screen.fill((200, 200, 200))
    #         self.status_bar.draw(self.screen)
    #         for wall in self.walls:
    #             wall.draw(self.screen)
    #         for tank in self.tanks:
    #             tank.draw(self.screen)
    #             for bullet in tank.bullets:
    #                 bullet.draw(self.screen)
    #         pygame.display.flip()
    #         self.clock.tick(30)
    #     else:
    #         raise NotImplementedError(f"Render mode {mode} not implemented")
    

    ########### HELPER FUNCTIONS ###########

    def update_objects(self):
        self.bullets = []
        for tank in self.tanks:
            self.bullets.extend(tank.bullets)

    def create_enemy_tanks(self, mode = "heuristic"):
        for i in range(NUMBER_OF_ENEMIES):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(0, WINDOW_HEIGHT)
            while check_spawn_spot_occupied(x, y, self.tanks, self.walls):
                x = random.randint(0, WINDOW_WIDTH)
                y = random.randint(0, WINDOW_HEIGHT)

            if mode == "heuristic":
                self.enemy_tank = HeuristicBot(self, x, y, (150, 0, 0))
            elif mode == "random":
                self.enemy_tank = RandomBot(self, x, y, (150, 0, 0))
            elif mode == "training":
                self.enemy_tank = TrainingBot(self, x, y, (150, 0, 0))


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
        
        # Enemy positions, angles, and shooter angles
        enemy_locations = self.get_enemy_locations()
        current_idx = 4
        for i, (ex, ey) in enumerate(enemy_locations):
            if i < NUMBER_OF_ENEMIES:  # Ensure we don't exceed the space allocated
                observation[current_idx + i*2] = ex
                observation[current_idx + i*2 + 1] = ey
        
        current_idx += NUMBER_OF_ENEMIES * 2
        for i, enemy in enumerate(self.tanks):
            if enemy != self.player_tank and i < NUMBER_OF_ENEMIES:
                observation[current_idx + i] = enemy.angle
        
        current_idx += NUMBER_OF_ENEMIES
        for i, enemy in enumerate(self.tanks):
            if enemy != self.player_tank and i < NUMBER_OF_ENEMIES:
                observation[current_idx + i] = enemy.shooter_angle
        
        # Bullet positions
        current_idx += NUMBER_OF_ENEMIES
        bullet_info = self.get_bullet_info()
        for i, (bx, by, _, _) in enumerate(bullet_info):
            if i < self.max_bullets:  # max_bullets from your observation space definition
                observation[current_idx + i*2] = bx
                observation[current_idx + i*2 + 1] = by
        
        # Wall positions
        current_idx += self.max_bullets * 2  # max_bullets * 2
        wall_info = self.get_wall_info()
        for i, (wx, wy, ww, wh) in enumerate(wall_info):
            if i < self.max_walls:  # max_walls from your observation space definition
                observation[current_idx + i*4] = wx
                observation[current_idx + i*4 + 1] = wy
                observation[current_idx + i*4 + 2] = ww
                observation[current_idx + i*4 + 3] = wh
        
        return observation
    
    def get_player_location(self):
        return self.player_tank.x, self.player_tank.y

    def get_enemy_locations(self):
        enemy_locations = []    
        for enemy in self.tanks:
            if enemy != self.player_tank:
                enemy_locations.append((enemy.x, enemy.y))
        return enemy_locations
    
    def get_bullet_info(self):
        bullet_info = []
        for bullet in self.bullets:
            bullet_info.append((bullet.x, bullet.y, bullet.angle, bullet))
        return bullet_info

    def get_wall_info(self):
        wall_info = []
        for wall in self.walls:
            wall_info.append((wall.x, wall.y, wall.width, wall.height))
        return wall_info
