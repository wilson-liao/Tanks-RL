import pygame
from Tank import Tank
from WallGenerator import Wall
from Bullet import Bullet
'''
Types of collisions:
    Tank and Wall
    Tank and Bullet
    Tank and Tank
    Bullet and Wall
    Bullet and Bullet
'''

class CollisionDetector:
    def __init__(self, tanks, walls, bullets):
        # Dictionary to store registered collision handlers
        
        
        self.collision_handlers = {}
        self.collidable_objects = ['Tank', 'Wall', 'Bullet']
        self.tanks = tanks
        self.walls = walls
        self.bullets = bullets

    
    def update_objects(self, tanks, walls, bullets):
        self.tanks = tanks
        self.walls = walls
        self.bullets = bullets

    def get_collide_key(self, obj1, obj2):
        return tuple(sorted([type(obj1).__name__, type(obj2).__name__]))

    def register_collision_handler(self):
        """Register a collision handler for specific object types"""
        for obj1 in self.collidable_objects:
            for obj2 in self.collidable_objects:
                key = tuple(sorted([obj1, obj2]))
                self.collision_handlers[key] = self._CollisionHandler


    def check_collision(self, obj1, obj2):
        """Check collision between two objects using rect collision"""
        # if hasattr(obj1, 'rect') and hasattr(obj2, 'rect'):
        return obj1.rect.colliderect(obj2.rect)
        # return False

    def check_collisions(self, group1, group2):
        if len(group1) == 0 or len(group2) == 0:
            return
        key = self.get_collide_key(group1[0], group2[0])
        if key not in self.collision_handlers:
            return
        
        """Check collisions between two groups of objects"""
        iterList = list(set(group1 + group2))
        for i in range(len(iterList)):
            for j in range(i + 1, len(iterList)):
                obj1 = iterList[i]
                obj2 = iterList[j]
                if obj1 == obj2:
                    print(f'{obj1} and {obj2} are the same object')
                    continue
                
                if self.check_collision(obj1, obj2):
                    # Get object types
                    type1 = type(obj1).__name__
                    type2 = type(obj2).__name__
                    
                    # Look for registered handler
                    key = self.get_collide_key(obj1, obj2)
                    handler = self.collision_handlers.get(key)
                    if handler:
                        handler(obj1, obj2)
    
    def check_all_collisions(self, tanks, walls, bullets):
        self.update_objects(tanks, walls, bullets)

        self.check_collisions(self.tanks, self.walls)
        self.check_collisions(self.bullets, self.walls)
        self.check_collisions(self.tanks, self.bullets)
        self.check_collisions(self.tanks, self.tanks)
        self.check_collisions(self.bullets, self.bullets)

        return self.bullets, self.tanks, self.walls


    def _CollisionHandler(self, obj1, obj2):
        key = self.get_collide_key(obj1, obj2)
        if key not in self.collision_handlers:
            return
        
        if "Tank" in key and "Wall" in key:
            print("Tank and Wall collision detected!!!")
            # Get the tank and wall objects
            tank = obj1 if type(obj1).__name__ == "Tank" else obj2
            
            # Revert tank to previous position before collision
            tank.x = tank.prev_x
            tank.y = tank.prev_y
            
        elif "Bullet" in key and "Wall" in key:
            # print("Bullet and Wall collision detected")
            bullet = obj1 if type(obj1).__name__ == "Bullet" else obj2
            try:
                self.bullets.remove(bullet)
                del bullet
            except:
                print(f'Bullet {bullet} not found in bullets list')

        elif "Tank" in key and "Bullet" in key:
            
            tank = obj1 if type(obj1).__name__ == "Tank" else obj2
            bullet = obj1 if type(obj1).__name__ == "Bullet" else obj2
            if tank == bullet.tank:
                # print(f'Tank {tank} hit by its own bullet {bullet}')
                return
            
            # print(f'Tank {tank} hit by bullet {bullet}')

            tank.health -= 1
            if tank.health <= 0:
                self.tanks.remove(tank)
                del tank
            
            try:
                self.bullets.remove(bullet)
                del bullet
            except:
                print(f'Bullet {bullet} not found in bullets list')

            
            
        elif "Tank" in key and "Tank" in key:
            obj1.x = obj1.prev_x
            obj1.y = obj1.prev_y
            obj2.x = obj2.prev_x
            obj2.y = obj2.prev_y
            print("Tank and Tank collision detected")

        elif "Bullet" in key and "Bullet" in key:
            try:
                self.bullets.remove(obj1)
                self.bullets.remove(obj2)   
                del obj1
                del obj2
            except:
                print(f'Bullet {obj1} or {obj2} not found in bullets list')
            

            # print("Bullet and Bullet collision detected")
        else:
            self.collision_handlers.pop(key)
            # print("Collision does not exist between", type(obj1).__name__, "and", type(obj2).__name__)

