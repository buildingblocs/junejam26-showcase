import pygame
import os

class HealthManager:  
    def grant_boon(self):
        """Heals the player for one heart every stage."""
        if self.current_hearts < self.max_hearts:
            self.current_hearts += 1
            print("Boon granted: Health Restored!")
    def __init__(self, max_hearts=3, i_frames_duration=1200):
        self.max_hearts = max_hearts
        self.current_hearts = max_hearts
        self.i_frames_duration = i_frames_duration
        self.last_hit_time = 0
        self.is_dead = False

        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load Full Variant
        full_path = os.path.join(base_dir, "assets", "Health.png")
        if os.path.exists(full_path):
            self.img_full = pygame.image.load(full_path).convert_alpha()
            self.img_full = pygame.transform.scale(self.img_full, (40, 40))
        else:
            self.img_full = pygame.Surface((40, 40))
            self.img_full.fill((230, 100, 100))

        # Load Lost Variant
        lose_path = os.path.join(base_dir, "assets", "HealthLose.png")
        if os.path.exists(lose_path):
            self.img_lose = pygame.image.load(lose_path).convert_alpha()
            self.img_lose = pygame.transform.scale(self.img_lose, (40, 40))
        else:
            self.img_lose = pygame.Surface((40, 40))
            self.img_lose.fill((80, 80, 90))

    def take_damage(self, amount=1):
        if self.is_dead:
            return False

        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time > self.i_frames_duration:
            self.current_hearts -= amount
            self.last_hit_time = current_time

            if self.current_hearts <= 0:
                self.current_hearts = 0
                self.is_dead = True
            return True
        return False

    def check_negative_hp(self):
        if self.current_hearts <= 0:
            self.current_hearts = 0
            self.is_dead = True
            return True
        return False

    def reset(self):
        self.current_hearts = self.max_hearts
        self.is_dead = False
        self.last_hit_time = 0

    def draw_hud(self, screen, x, y):
        if self.current_hearts < 0:
            self.current_hearts = 0

        for i in range(self.max_hearts):
            spawn_x = x + (i * 48)
            if i < self.current_hearts:
                screen.blit(self.img_full, (spawn_x, y))
            else:
                screen.blit(self.img_lose, (spawn_x, y))