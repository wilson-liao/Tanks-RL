import pygame
from config import *
import numpy as np


def check_spawn_spot_occupied(x, y, tanks, walls):
    width = TANK_WIDTH
    height = TANK_HEIGHT
    surface_size = max(400, width * 2, height * 2)
    center_x = x + surface_size // 2
    center_y = y + surface_size // 2
    
    temp_rect = pygame.Rect((center_x - width//2, center_y - height//2, 
                        width, height))
    for tank in tanks:
        # if temp_rect.colliderect(tank.body_rect()):
        if np.abs(x - tank.x) <=30 or np.abs(y - tank.y) <=30:
            return True
    for wall in walls:
        if temp_rect.colliderect(wall.rect):
            return True
    return False


