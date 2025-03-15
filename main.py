import pygame
from Tank import Tank
from InputHandler import InputHandler
from config import *
from WallGenerator import WallGenerator

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tank Game")



def main():
    clock = pygame.time.Clock()
    
    # Create a tank
    player_tank = Tank(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, (0, 150, 0))
    input_handler = InputHandler()
    wall_generator = WallGenerator(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    wall_generator.generate_walls()

    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # Handle input
        keys = pygame.key.get_pressed()
        input_handler.handle_events(event, keys, player_tank)
        
        # Clear screen
        screen.fill((200, 200, 200))
        

        # Draw tank
        player_tank.draw(screen)
        if player_tank.cooldown < BULLET_COOLDOWN:
            player_tank.cooldown += 1

        # Draw walls

        wall_generator.draw(screen)

        # Draw bullets
        for bullet in player_tank.bullets:
            if bullet.lifeTime >= BULLET_LIFETIME:
                player_tank.bullets.remove(bullet)
                del bullet
            else:
                bullet.draw(screen)
                bullet.move()


        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
