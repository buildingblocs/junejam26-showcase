import pygame
import math
from scenes.base_scene import BaseScene
from settings import RENDER_W, RENDER_H, BLACK, WARM_WHITE, WARM_GOLD

# Font size standards used across the whole game:
# 16 = big title / chapter headers
# 12 = subtitle / section labels
#  8 = body text / narration lines
#  6 = hints, small labels, slot numbers

class MenuScene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)

        self.font_title  = self.assets.get_font(16)   # game title
        self.font_sub    = self.assets.get_font(12)   # subtitle
        self.font_button = self.assets.get_font(8)    # button text

        self.silhouette  = self.assets.get_image("characters/silhouette")
        self.bg_image = self.assets.get_image("scenes/menu_bg")

        self.timer       = 0.0
        self.title_alpha = 0
        self.sub_alpha   = 0
        self.btn_alpha   = 0
        self.sil_alpha   = 180

        # Button sits near the bottom, wide enough for the text at size 8
        self.btn_rect  = pygame.Rect(RENDER_W // 2 - 130, RENDER_H - 50, 260, 20)
        self.btn_hover = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my  = pygame.mouse.get_pos()
            scale_x = RENDER_W / pygame.display.get_surface().get_width()
            scale_y = RENDER_H / pygame.display.get_surface().get_height()
            scaled  = (int(mx * scale_x), int(my * scale_y))
            if self.btn_rect.collidepoint(scaled):
                self.manager.replace_scene("prologue")

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.manager.replace_scene("prologue")

    def update(self, dt):
        self.timer += dt

        if self.timer > 0.5:
            self.title_alpha = min(255, self.title_alpha + 120 * dt)
        if self.timer > 2.0:
            self.sub_alpha   = min(255, self.sub_alpha   + 80  * dt)
        if self.timer > 3.5:
            self.btn_alpha   = min(255, self.btn_alpha   + 60  * dt)

        self.sil_alpha = int(140 + 40 * math.sin(self.timer * 1.2))

        mx, my  = pygame.mouse.get_pos()
        scale_x = RENDER_W / pygame.display.get_surface().get_width()
        scale_y = RENDER_H / pygame.display.get_surface().get_height()
        scaled  = (int(mx * scale_x), int(my * scale_y))
        self.btn_hover = self.btn_rect.collidepoint(scaled)

    def draw(self, surface):
        bg = pygame.transform.scale(self.bg_image, (RENDER_W, RENDER_H))
        surface.blit(bg, (0, 0))

        # Silhouette centred in screen
        sil = pygame.transform.scale(self.silhouette, (RENDER_W, RENDER_H))
        sil.set_alpha(self.sil_alpha)
        surface.blit(sil, (0, 0))

        self._draw_scanlines(surface)

        # Title — size 16, near top
        if self.title_alpha > 0:
            title_surf = self.font_title.render("WHERE THE PATH USED TO BE", False, WARM_WHITE)
            title_surf.set_alpha(int(self.title_alpha))
            title_rect = title_surf.get_rect(center=(RENDER_W // 2, 26))
            surface.blit(title_surf, title_rect)

        # Subtitle — size 12, just below title
        if self.sub_alpha > 0:
            sub_surf = self.font_sub.render("a memory reconstruction", False, (150, 140, 160))
            sub_surf.set_alpha(int(self.sub_alpha))
            sub_rect = sub_surf.get_rect(center=(RENDER_W // 2, 50))
            surface.blit(sub_surf, sub_rect)

        # Button — size 8, near bottom
        if self.btn_alpha > 0:
            btn_color = WARM_GOLD if self.btn_hover else (160, 150, 170)
            btn_surf  = self.font_button.render("[ START MEMORY RECONSTRUCTION ]", False, btn_color)
            btn_surf.set_alpha(int(self.btn_alpha))
            btn_rect  = btn_surf.get_rect(center=self.btn_rect.center)
            surface.blit(btn_surf, btn_rect)

            if self.btn_hover and math.sin(self.timer * 6) > 0:
                cur_surf = self.font_button.render("_", False, WARM_GOLD)
                surface.blit(cur_surf, (btn_rect.right + 2, btn_rect.top))

    def _draw_scanlines(self, surface):
        scanline = pygame.Surface((RENDER_W, 1))
        scanline.fill((0, 0, 0))
        scanline.set_alpha(40)
        for y in range(0, RENDER_H, 2):
            surface.blit(scanline, (0, y))