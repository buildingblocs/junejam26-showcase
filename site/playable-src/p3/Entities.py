import pygame
from random import randint
from math import floor

enemies = []
enemy_num = 0
enemy_speed = 4

class Tile():
    def __init__(self, img, x, y):
        self.x = x
        self.y = y
        self.speed_y = 0
        self.img = pygame.image.load(img).convert_alpha()
        self.img = pygame.transform.scale(self.img, (100, 100))
    
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

class Health:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = pygame.image.load("Assets/Full Heart.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (65, 64))
    
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

class Player:
    def __init__(self, img, hp):
        self.x = 320
        self.y = 350
        self.hp = hp
        self.frame = 1
        self.speed_y = 5
        self.iframes = 120

        self.ground_collision = False
        self.img = pygame.image.load(img).convert_alpha()
        self.img = pygame.transform.scale(self.img, (100, 100))
    
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
    
    def movement(self, keys, screen):
            mousex = pygame.mouse.get_pos()[0]
            if mousex > self.x:
                self.img = pygame.image.load(f"Assets/PlayerR{floor(self.frame)%4}.png").convert_alpha()
                self.img = pygame.transform.scale(self.img, (100, 100))
                self.frame += 0.5
            else:
                self.img = pygame.image.load(f"Assets/PlayerL{floor(self.frame)%4}.png").convert_alpha()
                self.img = pygame.transform.scale(self.img, (100, 100))
                self.frame += 0.5
                
class Enemy:
    def __init__(self, img, hp):
        self.x = randint(-200, 0)
        self.y = 350
        self.speed_y = 0
        self.jump_height = 10
        self.ground_collision = False
        self.hp = hp
        self.frame = 1
        self.speed = 9
        self.iframes = 0
        self.img = pygame.image.load(img).convert_alpha()
        self.img = pygame.transform.scale(self.img, (100, 100))
    
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

class Player_Bullet:
    def __init__(self, speed, x, y):
        self.x = x
        self.y = y
        self.speed_y = 0
        self.speed = speed
        self.jump_height = 10
        self.lifespan = 3600
        self.img = pygame.image.load("Assets/Ammo.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (100, 100))
    
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
    
    def update(self):
        self.lifespan -= 1
        self.x += self.speed

# class Enemy_Bullet:
#     def __init__(self, speed, x, y, px, py):
#         self.x = x
#         self.y = y
#         self.speed_y = 0
#         self.speed = speed
#         self.jump_height = 10
#         self.lifespan = 3600
#         self.img = pygame.image.load(f"Assets/Projectile{randint(0, 1)}.png").convert_alpha()
#         self.img = pygame.transform.scale(self.img, (100, 100))
    
#     def draw(self, screen):
#         screen.blit(self.img, (self.x, self.y))
    
#     def update(self):
#         self.lifespan -= 1
#         self.x += 

def spawn_enemy(num, img):
    global enemy_num
    for _ in range(num):
        enemies.append(Enemy(img, 5))
        enemy_num += 1