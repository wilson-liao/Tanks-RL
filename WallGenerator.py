import pygame
import math
from config import *


class WallGenerator:
    def __init__(self, x, y, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color = WALL_COLOR
        self.walls = []
        self.width = WALL_THICKNESS


    def generate_walls(self):
        # Top wall
        self.walls.append(Wall(0, 0, self.screen_width, self.width))
        # Bottom wall
        self.walls.append(Wall(0, self.screen_height - self.width, self.screen_width, self.width))
        # Left wall
        self.walls.append(Wall(0, 0, self.width, self.screen_height))
        # Right wall 
        self.walls.append(Wall(self.screen_width - self.width, 0, self.width, self.screen_height))

            

    def draw(self, screen):
        for wall in self.walls:
            wall.draw(screen)








class Wall:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    

    def draw(self, screen):
        pygame.draw.rect(screen, WALL_COLOR, (self.x, self.y, self.width, self.height))

    

