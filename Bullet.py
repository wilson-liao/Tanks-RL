import pygame
import math
from config import *


class Bullet:
    def __init__(self, x, y, angle, tank):
        self.x = x
        self.y = y
        self.angle = math.radians(angle)
        self.speed = BULLET_SPEED

        self.tank = tank

        self.lifeTime = 0

    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

        self.lifeTime += 1

    
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, BULLET_SIZE, BULLET_SIZE)

    def draw(self, screen):
        pygame.draw.circle(screen, BULLET_COLOR, (self.x, self.y), BULLET_SIZE)

    def destroy(self):
        # Remove bullet from game 
        del self


