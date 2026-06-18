import pygame
import random

class Enemy:
    def __init__(self, x, y, hp, speed):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.hp = hp
        self.speed = speed

class Charger(Enemy):
    def update(self, player_rect, health_sys):
        if self.rect.x < player_rect.x: self.rect.x += self.speed
        if self.rect.x > player_rect.x: self.rect.x -= self.speed
        if self.rect.y < player_rect.y: self.rect.y += self.speed
        if self.rect.y > player_rect.y: self.rect.y -= self.speed
        
        if self.rect.colliderect(player_rect):
            health_sys.take_damage(1)
            self.hp = 0 # Die on contact

class Poisoner(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 2, 1)
        self.puddle = None

    def update(self, player_rect):
        # Move towards player
        if self.rect.x < player_rect.x: self.rect.x += self.speed
        if self.rect.x > player_rect.x: self.rect.x -= self.speed
        
    def die(self):
        # Returns a Puddle rect
        return pygame.Rect(self.rect.x, self.rect.y, 60, 60)

class Shooter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, 1, 0)
        self.shoot_timer = 0
        
    def update(self, player_rect, bullets_list):
        self.shoot_timer += 1
        if self.shoot_timer > 100:
            # Add a 'mindwave' to the bullet list
            bullets_list.append(pygame.Rect(self.rect.x, self.rect.y, 10, 10))
            self.shoot_timer = 0