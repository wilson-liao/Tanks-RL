import pygame


class InputHandler:
    def __init__(self):
        self.keys = pygame.key.get_pressed()
        self.space_pressed = False  # Track space key state

    def get_keys(self):
        return self.keys

    def handle_events(self, event, keys, tank):
        if keys[pygame.K_LEFT]:
            tank.rotate(-1)
        if keys[pygame.K_RIGHT]:
            tank.rotate(1)
        if keys[pygame.K_UP]:
            tank.move()
        if keys[pygame.K_DOWN]:
            tank.move_backward()
        
        # Only shoot if space is pressed and wasn't pressed in the previous frame
        if keys[pygame.K_SPACE] and not self.space_pressed:
            tank.shoot()

        self.space_pressed = keys[pygame.K_SPACE]  # Update space key state

        if keys[pygame.K_a]:
            tank.rotate_shooter(-1)
        if keys[pygame.K_d]:
            tank.rotate_shooter(1)
