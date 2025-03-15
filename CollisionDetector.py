import pygame


class CollisionDetector:
    def __init__(self):
        # Dictionary to store registered collision handlers
        self.collision_handlers = {}

    def register_collision_handler(self, obj1_type, obj2_type, handler_function):
        """Register a collision handler for specific object types"""
        key = (obj1_type, obj2_type)
        self.collision_handlers[key] = handler_function

    def check_collision(self, obj1, obj2):
        """Check collision between two objects using rect collision"""
        if hasattr(obj1, 'rect') and hasattr(obj2, 'rect'):
            return obj1.rect.colliderect(obj2.rect)
        return False

    def check_collisions(self, group1, group2):
        """Check collisions between two groups of objects"""
        for obj1 in group1:
            for obj2 in group2:
                if self.check_collision(obj1, obj2):
                    # Get object types
                    type1 = type(obj1).__name__
                    type2 = type(obj2).__name__
                    
                    # Look for registered handler
                    handler = self.collision_handlers.get((type1, type2))
                    if handler:
                        handler(obj1, obj2)

    def printCollision(self, obj1, obj2):
        print(f"Collision detected between {type(obj1).__name__} and {type(obj2).__name__}")


