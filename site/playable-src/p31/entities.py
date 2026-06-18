import pygame
import math

class Plr:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 5
        self.start_x = x
        self.start_y = y
        
    def move(self, keys, sw, sh, current_page):
        moved = False
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.rect.x -= self.speed; moved = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.rect.x += self.speed; moved = True
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.rect.y -= self.speed; moved = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.rect.y += self.speed; moved = True
            
        self.rect.clamp_ip(pygame.Rect(0, 0, sw, sh))
        
        if current_page == 13 and moved:
            if abs(self.rect.x - self.start_x) > 30 or abs(self.rect.y - self.start_y) > 30:
                return True
        return False

class Blt:
    def __init__(self, px, py, tx, ty, speed):
        self.x, self.y = float(px), float(py)
        angle = math.atan2(ty - py, tx - px)
        self.dx, self.dy = math.cos(angle) * speed, math.sin(angle) * speed
        self.rect = pygame.Rect(self.x, self.y, 8, 8)
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x, self.rect.y = int(self.x), int(self.y)