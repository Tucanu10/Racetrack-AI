import pygame
import math

screen = pygame.display.set_mode((1080, 720))
clock = pygame.time.Clock()
running = True
dt = 0

class Track(pygame.sprite.Sprite):
    def __init__(self, path):
        super().__init__()
        image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(image, (1080, 720))
        self.rect = self.image.get_rect(topleft=(0, 0)) # Added rect for proper sprite collisions
        self.mask = pygame.mask.from_surface(self.image)

class Player(pygame.sprite.Sprite):
    def __init__(self, path, x, y):
        super().__init__()
        image = pygame.image.load(path).convert_alpha()
        
        self.original_image = pygame.transform.scale(image, (40, 40)) 
        
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0
        
        self.pos_x = float(x)
        self.pos_y = float(y)

        self.mask = pygame.mask.from_surface(self.image)

        self.current_checkpoint = 0
        self.laps = 0

    def rotate(self, angle):
        self.angle += angle
        self.image = pygame.transform.rotate(self.original_image, self.angle) 
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, speed, dt, track):
        dx = -math.sin(math.radians(self.angle)) * speed * dt
        dy = -math.cos(math.radians(self.angle)) * speed * dt
        
        self.pos_x += dx
        self.pos_y += dy
        
        self.rect.centerx = round(self.pos_x)
        self.rect.centery = round(self.pos_y)

        # Screen boundary collisions
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen.get_width():
            self.rect.right = screen.get_width()
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen.get_height():
            self.rect.bottom = screen.get_height()

        # Check for mask collision
        if pygame.sprite.collide_mask(self, track):
            return True # Tell the main loop a crash happened
            
        self.pos_x = self.rect.centerx
        self.pos_y = self.rect.centery
        return False # No crash

    def check_checkpoints(self, checkpoints):
        target = checkpoints[self.current_checkpoint]

        if self.rect.colliderect(target):
            self.current_checkpoint += 1
            print(f"Checkpoint {self.current_checkpoint} reached!")
            if self.current_checkpoint >= len(checkpoints):
                self.current_checkpoint = 0
                return True # Lap completed

            return False
        return False