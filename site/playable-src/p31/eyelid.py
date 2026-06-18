import pygame
import os

class EyelidManager:
    def __init__(self, sw, sh, base_dir):
        self.sw = sw
        self.sh = sh
        self.eye_frames = []
        self.current_frame = 0.0
        self.is_waking_up = False
        self.eyes_open = True  

        assets_dir = os.path.join(base_dir, "assets")
        for i in range(8):
            img_path = os.path.join(assets_dir, f"Eye{i}.png.png")
            if os.path.exists(img_path):
                raw_img = pygame.image.load(img_path).convert_alpha()
                self.eye_frames.append(pygame.transform.scale(raw_img, (sw, sh)))

    def reset(self):
        self.current_frame = 0.0
        self.is_waking_up = False
        self.eyes_open = True

    def drop_eyelids(self):
        self.eyes_open = False
        self.is_waking_up = True
        self.current_frame = 0.0

    def update_gravity(self):
        if self.is_waking_up and not self.eyes_open:
            self.current_frame -= 0.045
            if self.current_frame < 0.0:
                self.current_frame = 0.0

    def register_mash(self):
        if self.is_waking_up and not self.eyes_open:
            self.current_frame += 0.65

    def draw(self, screen, font_button):
        if not self.eyes_open and len(self.eye_frames) > 0:
            if self.is_waking_up and int(self.current_frame) >= len(self.eye_frames) - 1:
                self.eyes_open = True
                self.current_frame = len(self.eye_frames) - 1
            
            frame_idx = max(0, min(int(self.current_frame), len(self.eye_frames) - 1))
            screen.blit(self.eye_frames[frame_idx], (0, 0))

            if not self.eyes_open:
                hint = font_button.render("MASH SPACEBAR TO FORCE YOUR EYES OPEN!", False, (255, 150, 50))
                screen.blit(hint, hint.get_rect(center=(self.sw // 2, 60)))
                
                p_bar = pygame.Rect(self.sw // 2 - 150, 95, 300, 14)
                pygame.draw.rect(screen, (40, 40, 50), p_bar, border_radius=4)
                
                fill_w = int((self.current_frame / (len(self.eye_frames) - 1)) * 296) if len(self.eye_frames) > 1 else 0
                pygame.draw.rect(screen, (100, 255, 100), pygame.Rect(self.sw // 2 - 148, 97, max(0, fill_w), 10), border_radius=2)