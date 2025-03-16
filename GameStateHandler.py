import pygame
from enum import Enum

class GameStateHandler:
    def __init__(self):
        self.game_state = GameState.MENU
        

    def update_game_state(self, tanks, player_tank):
        running = True
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        
        if player_tank.health <= 0: 
            print("Player tank is dead")
            self.game_state = GameState.GAME_OVER
            # Stop game clock
            pygame.time.set_timer(pygame.USEREVENT, 0)
            
            # Create font and render game over text
            font = pygame.font.Font(None, 74)
            text = font.render('Game Over - You Lost!', True, (255, 0, 0))
            text_rect = text.get_rect(center=(500, 500))
            pygame.display.get_surface().blit(text, text_rect)
            pygame.display.flip()
            pygame.time.wait(10000)  
            running = False

        return self.game_state, running

    def get_game_state(self):
        return self.game_state



class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing" 
    PAUSED = "paused"
    GAME_OVER = "game_over"
