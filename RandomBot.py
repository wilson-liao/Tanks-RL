from config import *
import math
from Tank import Tank
import random

class RandomBot(Tank):
    def __init__(self, game, x, y, color):
        super().__init__(x, y, color)
        self.game = game
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
    

    def take_action(self, action=None):
        if action is None:
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
