from config import *
import math
from Tank import Tank
import random

DEGREE_TOLERANCE = 2

class TrainingBot(Tank):
    def __init__(self, game, x, y, color):
        super().__init__(x, y, color)
        print("Creating training bot 2")
        self.game = game
        self.move_angle = None
        self.action_probabilities = {
            "move": 0.5,
            "move_backward": 0.1, 
            "rotate_clockwise": 0.1,
            "rotate_counterclockwise": 0.1,
            "shoot": 0.1,
            "rotate_shooter_clockwise": 0.3,
            "rotate_shooter_counterclockwise": 0.3,
            "idle": 0
        }
    

    def take_action(self, skill):
        player_position = self.game.get_player_location()

        # Case 1: Shoot player

        # lower than skill level -> random
        if(random.choices([0, 1], weights=[skill, 1-skill])):
            # print("IN RANDOM")
            action = random.choices(list(self.action_probabilities.keys()), 
                                    weights=list(self.action_probabilities.values()))[0]
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
        else:
            # print("IN HEURISTIC")
            if self.cooldown == BULLET_COOLDOWN-1:
                self.shoot_player(player_position)

                # Every shot, change the angle
                self.move_angle = random.randint(0, 360)
                # print("SHOT, MOVING TOWARD", self.move_angle)
            # else:
            #     if self.move_angle == None:
            #         self.move_angle = random.randint(0, 360)
            #     # print("NOT SHOT, MOVING TOWARD", self.move_angle)
            #     self.move_toward(self.move_angle)


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

