from config import *
import math
from Tank import Tank
import random

DEGREE_TOLERANCE = 2

class HeuristicBot(Tank):
    def __init__(self, game, x, y, color,  width=HEURISTIC_WIDTH, height=HEURISTIC_HEIGHT):
        super().__init__(x, y, color, width, height)
        self.game = game
        self.move_angle = None
    

    def take_action(self):
        player_position = self.game.get_player_location()

        # Shoot much less frequently (20% probability when ready)
        if self.cooldown >= BULLET_COOLDOWN and random.random() < HEURISTIC_SHOOT_PROBABILITY:
            self.shoot_player(player_position)
            # Change movement angle after shooting
            self.move_angle = random.randint(0, 360)

        # Move randomly, update movement direction occasionally
        if self.move_angle is None or random.random() < 0.05:
            self.move_angle = random.randint(0, 360)

        self.move_toward(self.move_angle)


    def calculate_player_angle(self, player_position):
        angle = math.atan2(player_position[1] - self.y, player_position[0] - self.x)
        return angle


    def shoot_player(self, player_position):
        # Calculate angle between bot and player
        target_angle = (math.degrees(self.calculate_player_angle(player_position)) + 90) % 360
        
        # Determine shortest rotation direction
        angle_diff = (target_angle - self.shooter_angle) % 360
        if angle_diff > 180:
            direction = -1  # Rotate counterclockwise
        else:
            direction = 1   # Rotate clockwise
            
        # Rotate turret until aligned with player
        if abs((self.shooter_angle - target_angle) % 360) > DEGREE_TOLERANCE:
            self.rotate_shooter(direction)
        else:
            # Once aligned, shoot
            self.shoot()


    def move_toward(self, angle):
        # Convert angle to match tank angle format (0-360)
        tank_angle = self.angle % 360
        target_angle = angle % 360
        
        angle_diff = (target_angle - tank_angle) % 360
        if angle_diff > 180:
            direction = -1  # Rotate counterclockwise
        else:
            direction = 1   # Rotate clockwise

        if abs((self.angle - target_angle) % 360) > DEGREE_TOLERANCE:
            self.rotate(direction)
        else:
            self.move()

