from config import *
import math
from Tank import Tank

DEGREE_TOLERANCE = 2

class HeuristicBot(Tank):
    def __init__(self, game, x, y, color):
        super().__init__(x, y, color)
        self.game = game
    

    def take_action(self):
        player_position = self.game.get_player_location()

        # Case 1: Shoot player
        self.shoot_player(player_position)


    def calculate_angle(self, player_position):
        angle = math.atan2(player_position[1] - self.y, player_position[0] - self.x)
        return angle


    def shoot_player(self, player_position):
        # Calculate angle between bot and player
        target_angle = (math.degrees(self.calculate_angle(player_position)) + 90) % 360
        
        # Determine shortest rotation direction
        angle_diff = (target_angle - self.shooter_angle) % 360
        if angle_diff > 180:
            direction = -1  # Rotate counterclockwise
        else:
            direction = 1   # Rotate clockwise
            
        # Rotate turret until aligned with player
        if abs(self.shooter_angle - target_angle) > DEGREE_TOLERANCE:
            self.rotate_shooter(direction)
        else:
            # Once aligned, shoot
            self.shoot()
