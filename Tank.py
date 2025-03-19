import pygame
import math
from Bullet import Bullet   
from config import *


class Tank:
    def __init__(self, x, y, color, width=TANK_WIDTH, height=TANK_HEIGHT, 
                 bullet_cooldown=BULLET_COOLDOWN, bullet_size=BULLET_SIZE, game=None):
        self.width = width
        self.height = height
        self.health = TANK_HEALTH

        self.x = x
        self.y = y

        self.prev_x = x
        self.prev_y = y
        
        self.angle = 0  # Angle in degrees
        self.speed = TANK_SPEED
        self.rotation_speed = TANK_ROTATION_SPEED
        self.shooter_rotation_speed = TANK_SHOOTER_ROTATION_SPEED
        self.color = color
        self.shooter_color = (255, 255, 255)
        self.shooter_angle = 0

        self.cooldown = 0
        
        # Make surface much larger to accommodate the shooter
        # self.width = TANK_WIDTH
        # self.height = TANK_HEIGHT
        self.surface_size = max(400, self.width * 2, self.height * 2)  # Bigger surface to fit everything
        self.surface = pygame.Surface((self.surface_size, self.surface_size), pygame.SRCALPHA)
        
        # Center of the surface
        self.center_x = self.surface_size // 2
        self.center_y = self.surface_size // 2

        # Bullet list
        self.bullets = []
    

    @property
    def rect(self):
        # Return a rect that matches the tank's visual representation more closely
        return pygame.Rect(
            self.x - self.width//2,     # Center the rect horizontally
            self.y - self.height//2,    # Center the rect vertically
            self.width,                 # Width of tank body
            self.height                 # Height of tank body
        )
    
    # Get the rects for the tank
    def body_rect(self):
        return pygame.Rect((self.center_x - self.width//2, self.center_y - self.height//2, 
                         self.width, self.height))
    

    # Get the rect for the turret
    def turret_rect(self):
        return pygame.Rect((self.center_x - self.width//6, self.center_y - self.height, 
                         self.width//3, self.height))

    def draw(self, screen):
        # Clear the surface with transparent pixels before drawing
        self.surface.fill((0, 0, 0, 0))
        
        # Adjust drawing positions to center of the larger surface
        
        
        # Draw tank body (centered)
        pygame.draw.rect(self.surface, self.color, self.body_rect())
        
        # Create separate surface for turret
        turret_surface = pygame.Surface((self.surface_size, self.surface_size), pygame.SRCALPHA)
        # Draw tank turret on separate surface
        pygame.draw.rect(turret_surface, self.shooter_color, self.turret_rect())
        
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
        self.prev_x = self.x
        self.prev_y = self.y
        # Convert angle to radians
        rad = math.radians(self.angle)
        
        # Calculate movement based on angle
        self.x += self.speed * math.sin(rad)
        self.y -= self.speed * math.cos(rad)
        # self.keep_in_bounds()
    
    def move_backward(self):
        self.prev_x = self.x
        self.prev_y = self.y
        # Convert angle to radians
        rad = math.radians(self.angle)
        
        # Calculate movement based on angle but in reverse
        self.x -= self.speed * math.sin(rad)
        self.y += self.speed * math.cos(rad)
        # self.keep_in_bounds()


    def rotate(self, direction):
        # Rotate tank (1 for right, -1 for left)
        self.angle += self.rotation_speed * direction


    def rotate_shooter(self, direction):
        self.shooter_angle += self.shooter_rotation_speed * direction
        self.shooter_angle = self.shooter_angle % 360


    def shoot(self, location=None):
        if location != None:
            self.auto_aim(location)
        # Create a new ammo object
        if self.cooldown >= BULLET_COOLDOWN:
            # Calculate bullet spawn position at end of turret
            turret_length = self.turret_rect().height
            spawn_x = self.x + turret_length * math.cos(math.radians(self.shooter_angle - 90))
            spawn_y = self.y + turret_length * math.sin(math.radians(self.shooter_angle - 90))
            
            bullet = Bullet(spawn_x, spawn_y, self.shooter_angle - 90, self, self.color)
            self.bullets.append(bullet)
            self.cooldown = 0
            return bullet
    

    def take_action(self, action):
        if action == "move":
            self.move()
        elif action == "move_backward":
            self.move_backward()
        elif action == "rotate_clockwise":
            self.rotate(1)
        elif action == "rotate_counterclockwise":
            self.rotate(-1)
        elif action == "shoot":
            self.shoot()
        elif action == "rotate_shooter_clockwise":
            self.rotate_shooter(1)
        elif action == "rotate_shooter_counterclockwise":
            self.rotate_shooter(-1)
        else:
            # print(f"Invalid action: {action}")
            pass

    def keep_in_bounds(self):
        self.x = max(self.width // 2, min(WINDOW_WIDTH - self.width // 2, self.x))
        self.y = max(self.height // 2, min(WINDOW_HEIGHT - self.height // 2, self.y))


    def calculate_player_angle(self, player_position):
        angle = math.atan2(player_position[1] - self.y, player_position[0] - self.x)
        return angle
    
    def auto_aim(self, target_tank):
        # Calculate angle between bot and player
        target_angle = (math.degrees(self.calculate_player_angle(target_tank)) + 90) % 360
        
        # Determine shortest rotation direction
        angle_diff = (target_angle - self.shooter_angle) % 360
        if angle_diff > 180:
            direction = -1  # Rotate counterclockwise
        else:
            direction = 1   # Rotate clockwise
            
        # Rotate turret until aligned with player
        while abs((self.shooter_angle - target_angle) % 360) > DEGREE_TOLERANCE:
            self.rotate_shooter(direction)
        
