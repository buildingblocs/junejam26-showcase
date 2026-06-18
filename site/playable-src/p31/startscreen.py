import pygame
import math
import sys
import os
import random

class TitleScreen:
    def __init__(self):
        self.view_state = "SPLASH"
        self.flash_timer = 0
        self.starting_currency = 200
        self.unlocked_weapons = ["Willpower Burst (Default)"]
        
        self.btn_w, self.btn_h = 320, 55
        self.center_x = 1280 // 2
        
        self.btn_configs = {
            "PLAY": {"center": (self.center_x, 340), "col": (75, 45, 100)},
            "STORE": {"center": (self.center_x, 415), "col": (50, 70, 95)},
            "SETTINGS": {"center": (self.center_x, 490), "col": (45, 65, 65)},
            "QUIT": {"center": (self.center_x, 565), "col": (95, 40, 55)}
        }
        
        self.scales = {"PLAY": 1.0, "STORE": 1.0, "SETTINGS": 1.0, "QUIT": 1.0, "w1": 1.0, "w2": 1.0}
        self.btn_back = pygame.Rect(50, 50, 130, 45)
        self.back_scale = 1.0
        
        self.store_items = [
            {"id": "w1", "name": "Plasma Repeater", "cost": 100, "base_rect": pygame.Rect(220, 320, 380, 200), "desc": "High velocity tracking fire rate."},
            {"id": "w2", "name": "Nightmare Cleaver", "cost": 150, "base_rect": pygame.Rect(680, 320, 380, 200), "desc": "Massive wide area damage blast."}
        ]
        self.game_volume = 80

        # --- TRANSITION JUICE VARIABLES ---
        self.impact_burst = 0.0      # Tracks extra title scale pop size
        self.screen_shake_amp = 0    # Current pixel camera shake offset duration
        self.white_out_alpha = 0     # Flash overlay visibility value

        # --- LOAD CUSTOM BACKGROUND ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_dir, "start_bg.png")
        if os.path.exists(bg_path):
            self.bg_image = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (1280, 800))
        else:
            self.bg_image = pygame.Surface((1280, 800))
            self.bg_image.fill((30, 20, 40))

    def trigger_entry_pop(self):
        """Ignites the visual explosion variables instantly when Spacebar lands."""
        self.impact_burst = 1.6       # Explodes title size up to 160% scale
        self.screen_shake_amp = 25    # Violent 25-pixel screen displacement vector
        self.white_out_alpha = 240    # Blinds the viewport with an alpha flash ring
        self.view_state = "MAIN_MENU"

    def run_cycle(self, screen, events, font_title, font_button, timer):
        self.flash_timer += 1
        m_pos = pygame.mouse.get_pos()
        
        # --- DECAY IMPACT JUICE MATH ---
        if self.impact_burst > 0.0:
            self.impact_burst -= (self.impact_burst) * 0.12  # Elastic snap back down to rest
        if self.screen_shake_amp > 0:
            self.screen_shake_amp -= 1
        if self.white_out_alpha > 0:
            self.white_out_alpha = max(0, self.white_out_alpha - 14) # Smoothly dim light overlay

        # Calculate erratic shake offsets based on current residual kinetic impact force
        shake_x = random.randint(-self.screen_shake_amp, self.screen_shake_amp) if self.screen_shake_amp > 0 else 0
        shake_y = random.randint(-self.screen_shake_amp, self.screen_shake_amp) if self.screen_shake_amp > 0 else 0

        # --- EVENT INTERCEPTIONS ---
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.view_state == "MAIN_MENU" and self.screen_shake_amp < 10: # Block input during heavy shake
                    for key, config in self.btn_configs.items():
                        test_rect = pygame.Rect(0, 0, self.btn_w, self.btn_h)
                        test_rect.center = config["center"]
                        if test_rect.collidepoint(m_pos):
                            if key == "PLAY": return "GO_TO_HUB"
                            elif key == "STORE": self.view_state = "STORE"
                            elif key == "SETTINGS": self.view_state = "SETTINGS"
                            elif key == "QUIT": pygame.event.post(pygame.event.Event(pygame.QUIT))
                            
                elif self.view_state in ["SETTINGS", "STORE"]:
                    if self.btn_back.collidepoint(m_pos):
                        self.view_state = "MAIN_MENU"
                    if self.view_state == "STORE":
                        for item in self.store_items:
                            if item["base_rect"].collidepoint(m_pos) and item["name"] not in self.unlocked_weapons:
                                if self.starting_currency >= item["cost"]:
                                    self.starting_currency -= item["cost"]
                                    self.unlocked_weapons.append(item["name"])

            elif event.type == pygame.KEYDOWN:
                if self.view_state == "SPLASH" and event.key == pygame.K_SPACE:
                    self.trigger_entry_pop()

        # 1. Render Background shifted inside the screen shake coordinates matrix
        screen.blit(self.bg_image, (shake_x, shake_y))
        
        # 2. Render dynamic pop-modified Title Header
        base_title_scale = 1.0 + self.impact_burst
        float_y = int(math.sin(timer * 1.5) * 8)
        
        # Re-render title scale surfaces dynamically during the pop blast frame spikes
        t_lbl = font_title.render("THE AWAKENING ENGINE", True, (255, 230, 245))
        if base_title_scale > 1.01:
            raw_w, raw_h = t_lbl.get_size()
            t_lbl = pygame.transform.scale(t_lbl, (int(raw_w * base_title_scale), int(raw_h * base_title_scale)))
            
        t_rect = t_lbl.get_rect(center=(1280 // 2 + shake_x, 140 + float_y + shake_y))
        screen.blit(t_lbl, t_rect)

        # --- VIEW STATE: SPLASH ---
        if self.view_state == "SPLASH":
            if (self.flash_timer // 25) % 2 == 0:
                p_lbl = font_button.render("PRESS SPACEBAR TO OPEN THE MIND", True, (255, 160, 200))
                screen.blit(p_lbl, p_lbl.get_rect(center=(1280 // 2, 500)))

        # --- VIEW STATE: MAIN MENU LAYOUT ---
        elif self.view_state == "MAIN_MENU":
            for key, config in self.btn_configs.items():
                dummy_rect = pygame.Rect(0, 0, self.btn_w, self.btn_h)
                dummy_rect.center = config["center"]
                hover = dummy_rect.collidepoint(m_pos)
                
                target_scale = 1.12 if hover else 1.0
                self.scales[key] += (target_scale - self.scales[key]) * 0.22
                
                cur_w = int(self.btn_w * self.scales[key])
                cur_h = int(self.btn_h * self.scales[key])
                draw_rect = pygame.Rect(0, 0, cur_w, cur_h)
                
                # Apply current screen shake to button alignments seamlessly
                draw_rect.center = (config["center"][0] + shake_x, config["center"][1] + shake_y)
                
                btn_surf = pygame.Surface((cur_w, cur_h), pygame.SRCALPHA)
                btn_surf.fill((*config["col"], 230 if hover else 160))
                screen.blit(btn_surf, draw_rect.topleft)
                
                pygame.draw.rect(screen, (255, 210, 235) if hover else (120, 95, 140), draw_rect, width=2 if hover else 1, border_radius=8)
                txt_surf = font_button.render(key if key != "PLAY" else "ENTER DREAM [PLAY]", True, (255, 255, 255))
                screen.blit(txt_surf, txt_surf.get_rect(center=draw_rect.center))

        # --- VIEW STATE: SETTINGS ---
        elif self.view_state == "SETTINGS":
            self._draw_pop_back_button(screen, font_button, m_pos)
            panel = pygame.Rect(1280 // 2 - 280 + shake_x, 280 + shake_y, 560, 240)
            pygame.draw.rect(screen, (25, 18, 35, 230), panel, border_radius=12)
            pygame.draw.rect(screen, (255, 180, 220), panel, width=1, border_radius=12)
            
            v_title = font_button.render("CORE SUBCONSCIOUS OPTIONS", True, (255, 200, 220))
            screen.blit(v_title, v_title.get_rect(center=panel.center).move(0, -40))

        # --- VIEW STATE: STORE ---
        elif self.view_state == "STORE":
            self._draw_pop_back_button(screen, font_button, m_pos)
            wallet_lbl = font_button.render(f"AVAILABLE MANIFEST FRAGMENTS: {self.starting_currency}", True, (255, 215, 0))
            screen.blit(wallet_lbl, wallet_lbl.get_rect(center=(1280 // 2 + shake_x, 230 + shake_y)))
            
            for item in self.store_items:
                hover = item["base_rect"].collidepoint(m_pos)
                is_unlocked = item["name"] in self.unlocked_weapons
                
                target_scale = 1.06 if hover else 1.0
                self.scales[item["id"]] += (target_scale - self.scales[item["id"]]) * 0.2
                
                cx, cy = item["base_rect"].center
                cur_w = int(item["base_rect"].width * self.scales[item["id"]])
                cur_h = int(item["base_rect"].height * self.scales[item["id"]])
                draw_rect = pygame.Rect(0, 0, cur_w, cur_h)
                draw_rect.center = (cx + shake_x, cy + shake_y)
                
                card_surf = pygame.Surface((cur_w, cur_h), pygame.SRCALPHA)
                card_surf.fill((45, 30, 60, 220) if is_unlocked else ((35, 45, 70, 190) if hover else (18, 15, 28, 150)))
                screen.blit(card_surf, draw_rect.topleft)
                pygame.draw.rect(screen, (255, 215, 0) if hover and not is_unlocked else ((100, 255, 180) if is_unlocked else (110, 100, 130)), draw_rect, width=2 if hover else 1, border_radius=10)

        # 3. --- OVERLAY DREAM BURST FLASH ALPHA SURFACE ---
        if self.white_out_alpha > 0:
            flash_surf = pygame.Surface((1280, 800), pygame.SRCALPHA)
            flash_surf.fill((245, 235, 255, self.white_out_alpha)) # Dream-purple/white tint wash
            screen.blit(flash_surf, (0, 0))

        return "KEEP_START_ALIVE"

    def _draw_pop_back_button(self, screen, font_button, m_pos):
        hover = self.btn_back.collidepoint(m_pos)
        target_scale = 1.1 if hover else 1.0
        self.back_scale += (target_scale - self.back_scale) * 0.25
        cx, cy = self.btn_back.center
        draw_rect = pygame.Rect(0, 0, int(self.btn_back.width * self.back_scale), int(self.btn_back.height * self.back_scale))
        draw_rect.center = (cx, cy)
        pygame.draw.rect(screen, (70, 45, 85) if hover else (35, 25, 45), draw_rect, border_radius=6)
        lbl = font_button.render("< RETURN", True, (255, 230, 245))
        screen.blit(lbl, lbl.get_rect(center=draw_rect.center))