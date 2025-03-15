import pygame
import math
from config import *


class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = math.radians(angle)
        self.speed = BULLET_SPEED

        self.lifeTime = 0

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

        self.lifeTime += 1
        

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), 5)

    def destroy(self):
        # Remove bullet from game 
        del self


