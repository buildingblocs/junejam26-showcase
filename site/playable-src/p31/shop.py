import pygame

class ShopManager:
    def __init__(self):
        self.fragments = 100
        self.bullet_speed = 12
        self.fire_rate_level = 1
        self.damage_level = 1
        self.has_shopped = False
        
        self.btn1_rect = pygame.Rect(1280 // 2 - 220, 240, 440, 50)
        self.btn2_rect = pygame.Rect(1280 // 2 - 220, 310, 440, 50)

    def reset(self):
        self.fragments = 100
        self.bullet_speed = 12
        self.fire_rate_level = 1
        self.damage_level = 1
        self.has_shopped = False

    def buy_fire_rate(self):
        if self.fragments >= 50:
            self.fragments -= 50
            self.fire_rate_level += 1
            self.bullet_speed += 3
            self.has_shopped = True

    def buy_damage(self):
        if self.fragments >= 50:
            self.fragments -= 50
            self.damage_level += 1
            self.has_shopped = True

    def draw(self, screen, font_title, font_button, sw, sh, c_txt):
        shop_rect = pygame.Rect(sw // 2 - 250, 120, 500, 320)
        pygame.draw.rect(screen, (24, 24, 36), shop_rect, border_radius=12)
        pygame.draw.rect(screen, (100, 110, 140), shop_rect, width=2, border_radius=12)
        
        s_title = font_title.render("MIND UPGRADES", False, (255, 215, 0))
        screen.blit(s_title, s_title.get_rect(center=(sw // 2, 160)))
        wallet = font_button.render(f"FRAGMENTS: {self.fragments}", False, (150, 255, 150))
        screen.blit(wallet, wallet.get_rect(center=(sw // 2, 200)))
        
        pygame.draw.rect(screen, (40, 50, 75), self.btn1_rect, border_radius=6)
        t1 = font_button.render(f"[1] Upgrade Fire Rate (Lvl {self.fire_rate_level}) - Cost: 50", False, c_txt)
        screen.blit(t1, t1.get_rect(center=self.btn1_rect.center))
        
        pygame.draw.rect(screen, (50, 40, 75), self.btn2_rect, border_radius=6)
        t2 = font_button.render(f"[2] Upgrade Damage Radius (Lvl {self.damage_level}) - Cost: 50", False, c_txt)
        screen.blit(t2, t2.get_rect(center=self.btn2_rect.center))