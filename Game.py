import pygame
from Tank import Tank
from InputHandler import InputHandler
from config import *
from WallGenerator import WallGenerator
from CollisionDetector import CollisionDetector
from GameStateHandler import GameStateHandler, GameState
from StatusBar import StatusBar
import random

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tank Game")
        self.game_state_handler = GameStateHandler()
        self.clock = pygame.time.Clock()

        # Create Status Bar
        self.status_bar = StatusBar(PLACEMENT)

        # Create a object groups
        self.tanks = []
        self.walls = []
        self.bullets = []

        # Create Objects
        self.player_tank = Tank(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, (0, 150, 0))
        self.tanks.append(self.player_tank)

        for i in range(NUMBER_OF_ENEMIES):
            self.enemy_tank = Tank(100, 100, (150, 0, 0))
            self.tanks.append(self.enemy_tank)
        

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


    def run(self):
        
        running = True
        while running:
            # Handle events
            self.game_state, running = self.game_state_handler.update_game_state(self.tanks, self.player_tank)

            # Clear screen
            self.screen.fill((200, 200, 200))

            # Handle input
            self.input_handler.handle_events(self.player_tank)
            for tank in self.tanks:
                if tank != self.player_tank:
                    tank.take_action(random.choice(ACTIONS))


            # Update status bar
            self.status_bar.draw(self.screen)

            # Draw walls
            for wall in self.walls:
                wall.draw(self.screen)

            # Update tanks
            for tank in self.tanks:
                tank.draw(self.screen)
                if tank.cooldown < BULLET_COOLDOWN:
                    tank.cooldown += 1


            # Update bullets
            for tank in self.tanks:
                for bullet in tank.bullets:
                    if bullet.lifeTime >= BULLET_LIFETIME:
                        tank.bullets.remove(bullet)
                        del bullet
                    else:
                        bullet.draw(self.screen)
                        bullet.move()
            self.update_objects()


            # Check collisions
            self.bullets, self.tanks, self.walls = self.collision_detector.check_all_collisions(self.tanks, self.walls, self.bullets)

            # Update display
            pygame.display.flip()
            # Control frame rate
            self.clock.tick(60)

        pygame.quit()
    
    def update_objects(self):
        self.bullets = []
        for tank in self.tanks:
            self.bullets.extend(tank.bullets)

        

