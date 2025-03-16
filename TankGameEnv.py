from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random

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
    def __init__(self, mode = "heuristic"):
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
        self.action_space = Discrete(8)


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
        max_bullets = 30
        max_walls = 10
        enemy_position_size = NUMBER_OF_ENEMIES * 2  # x,y for each enemy
        enemy_angle_size = NUMBER_OF_ENEMIES  # angle for each enemy
        enemy_shooter_size = NUMBER_OF_ENEMIES  # shooter angle for each enemy
        bullet_position_size = max_bullets * 2  # x,y for max 100 bullets 
        wall_position_size = max_walls * 4  # x,y,w,h for max 50 walls
        
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
            [WINDOW_WIDTH, WINDOW_HEIGHT] * max_bullets +  # Bullet positions
            [WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT] * max_walls,  # Wall positions
            dtype=np.float32
        )
        self.observation_space = Box(
            low=low_array,
            high=high_array,
            dtype=np.float32
        )

        self.state = self.get_all_info()



    def step(self, action):

        # Handle events
        self.game_state, running = self.game_state_handler.update_game_state(self.tanks, self.player_tank)


        # Convert action to game controls
        # Convert numeric action to game control
        # 0: Move forward
        # 1: Rotate left 
        # 2: Rotate right
        # 3: Rotate turret left
        # 4: Rotate turret right
        # 5: Shoot
        # 6: Idle
        # 7: Move backward
        if action == 0:  # Move forward
            self.player_tank.move()
        elif action == 1:  # Move backward
            self.player_tank.move_backward()
        elif action == 2:  # Rotate left
            self.player_tank.rotate(-1)
        elif action == 3:  # Rotate right 
            self.player_tank.rotate(1)
        elif action == 4:  # Rotate turret left
            self.player_tank.rotate_shooter(-1)
        elif action == 5:  # Rotate turret right
            self.player_tank.rotate_shooter(1)
        elif action == 6:  # Shoot
            self.player_tank.shoot()
        elif action == 7:  # Idle
            pass
        
        # Enemy moves
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
        self.bullets, self.tanks, self.walls, destroyed = self.collision_detector.check_all_collisions(self.tanks, self.walls, self.bullets)
        if destroyed:
            print("DESTROYED")
            self.status_bar.player_score += 1


        reward = 0
        # Player hits enemy
        for tank in self.tanks:
            if tank != self.player_tank and tank.health < enemy_health_prev[tank]:
                reward += 1

        # Player gets hit
        if player_health_prev > self.player_tank.health:
            reward -= 1

        # Player destroys enemy
        if destroyed:
            reward += 5

        done = False
        # Player wins
        if len(self.tanks) == 1 and self.player_tank in self.tanks:
            reward += 10
            done = True

        # Player dies/loses
        if self.player_tank.health <= 0:
            reward -= 10
            done = True
    
        info = {}

        self.state = self.get_all_info()

        return self.state, reward, done, info

    
    def reset(self, mode = "heuristic"):
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
    

    def render(self):
        # Clear screen
        self.screen.fill((200, 200, 200))

        # Update status bar
        self.status_bar.draw(self.screen)

        # Draw walls
        for wall in self.walls:
            wall.draw(self.screen)

        # Update tanks
        for tank in self.tanks:
            tank.draw(self.screen)

        # Update bullets
        for tank in self.tanks:
            for bullet in tank.bullets:
                    bullet.draw(self.screen)

        # Update display
        pygame.display.flip()
        # Control frame rate
        self.clock.tick(30)

    

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


            self.tanks.append(self.enemy_tank)
    

    # GAME API
    def get_game_state(self):
        return self.game_state
    
    def get_all_info(self):
        return self.get_player_location(), self.get_enemy_locations(), self.get_bullet_info(), self.get_wall_info()
    
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
