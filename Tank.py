import pygame
import math
from Bullet import Bullet   
from config import *


class Tank:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.angle = 0  # Angle in degrees
        self.speed = TANK_SPEED
        self.rotation_speed = TANK_ROTATION_SPEED
        self.shooter_rotation_speed = TANK_SHOOTER_ROTATION_SPEED
        self.color = color
        self.shooter_color = (255, 255, 255)
        self.shooter_angle = 0

        self.cooldown = 0
        
        # Make surface much larger to accommodate the shooter
        self.width = 40
        self.height = 60
        self.surface_size = max(400, self.width * 2, self.height * 2)  # Bigger surface to fit everything
        self.surface = pygame.Surface((self.surface_size, self.surface_size), pygame.SRCALPHA)
        
        self.bullets = []

    def draw(self, screen):
        # Clear the surface with transparent pixels before drawing
        self.surface.fill((0, 0, 0, 0))
        
        # Adjust drawing positions to center of the larger surface
        center_x = self.surface_size // 2
        center_y = self.surface_size // 2
        
        # Draw tank body (centered)
        pygame.draw.rect(self.surface, self.color, 
                        (center_x - self.width//2, center_y - self.height//2, 
                         self.width, self.height))
        
        # Create separate surface for turret
        turret_surface = pygame.Surface((self.surface_size, self.surface_size), pygame.SRCALPHA)
        # Draw tank turret on separate surface
        pygame.draw.rect(turret_surface, self.shooter_color, 
                        (center_x - self.width//6, center_y - self.height, 
                         self.width//3, self.height))
        
        # Rotate turret separately
        rotated_turret = pygame.transform.rotate(turret_surface, -self.shooter_angle)
        
        # Create a new surface for tank body rotation
        rotated_surface = pygame.transform.rotate(self.surface, -self.angle)
        
        # Get the rectangles for both surfaces
        rect = rotated_surface.get_rect(center=(self.x, self.y))
        turret_rect = rotated_turret.get_rect(center=(self.x, self.y))
        
        # Draw both surfaces
        screen.blit(rotated_surface, rect)
        screen.blit(rotated_turret, turret_rect)
        
    def move(self):
        # Convert angle to radians
        rad = math.radians(self.angle)
        
        # Calculate movement based on angle
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)
    
    def move_backward(self):
        # Convert angle to radians
        rad = math.radians(self.angle)
        
        # Calculate movement based on angle but in reverse
        self.x -= self.speed * math.sin(rad)
        self.y += self.speed * math.cos(rad)


    def rotate(self, direction):
        # Rotate tank (1 for right, -1 for left)
        self.angle += self.rotation_speed * direction


    def rotate_shooter(self, direction):
        self.shooter_angle += self.shooter_rotation_speed * direction


    def shoot(self):
        # Create a new ammo object
        if self.cooldown >= BULLET_COOLDOWN:
            bullet = Bullet(self.x, self.y, self.shooter_angle - 90)
            self.bullets.append(bullet)
            self.cooldown = 0
            return bullet
    

