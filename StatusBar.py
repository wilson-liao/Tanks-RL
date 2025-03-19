import pygame
from config import *

class StatusBar:
    def __init__(self, placement, player_tank):
        if placement == "top":
            self.x = 0 + WALL_THICKNESS
            self.y = 0 + WALL_THICKNESS
        elif placement == "bottom":
            self.x = 0 + WALL_THICKNESS
            self.y = WINDOW_HEIGHT - STATUS_BAR_HEIGHT - WALL_THICKNESS

        self.width = STATUS_BAR_WIDTH
        self.height = STATUS_BAR_HEIGHT
        self.color = STATUS_BAR_BACKGROUND_COLOR  
        self.font = pygame.font.Font(None, 24)

        self.x_offset = 5
        self.y_offset = 25

        self.gameTime = 0
        self.player_health = player_tank.health
        self.player_score = 0

    def backGroundPanel(self):
        pygame.Rect(self.x, self.y, self.width, self.height)
        
    def playerHealthBar(self):
        pygame.Rect(self.x, self.y, self.width, self.height)

    def playerScoreBar(self):
        pygame.Rect(self.x, self.y, self.width, self.height)

    
    def update(self, player_tank):
        self.player_health = player_tank.health

    def draw(self, screen):

        # Draw the background panel to cover text
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height + self.y_offset + 10))

        # Draw player health text
        
        health_text = self.font.render(f"Health: {self.player_health}", True, (0, 0, 0))
        screen.blit(health_text, (self.x + self.x_offset, self.y))

        # Draw player score text
        score_text = self.font.render(f"Score: {self.player_score}", True, (0, 0, 0))
        screen.blit(score_text, (self.x + self.x_offset, self.y + self.y_offset))


