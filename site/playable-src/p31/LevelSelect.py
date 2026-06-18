import pygame
import os
import math

COLOUR_TEXT = (255, 235, 245)
COLOUR_TEXT_SHADOW = (60, 40, 70)

pygame.font.init()
font_title = pygame.font.SysFont("Courier New", 44, bold=True)
font_button = pygame.font.SysFont("Lucida Console", 18)

game_state = "level_select"
card_w, card_h = 280, 360
card_y = 260
rects = {
    "LVL_1": pygame.Rect(180, card_y, card_w, card_h),
    "LVL_2": pygame.Rect(500, card_y, card_w, card_h),
    "LVL_3": pygame.Rect(820, card_y, card_w, card_h)
}

# --- LOAD LEVEL SELECT BACKGROUND ---
base_dir = os.path.dirname(os.path.abspath(__file__))
bg_path = os.path.join(base_dir, "select_bg.png")
if os.path.exists(bg_path):
    select_bg = pygame.image.load(bg_path).convert()
    select_bg = pygame.transform.scale(select_bg, (1280, 800))
else:
    select_bg = pygame.Surface((1280, 800))
    select_bg.fill((20, 24, 38))

def run_level_select_cycle(screen, events, mouse_pos, timer):
    global game_state
    
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rects["LVL_1"].collidepoint(mouse_pos): return "LAUNCH_LEVEL_ONE"
            elif rects["LVL_2"].collidepoint(mouse_pos): return "LAUNCH_LEVEL_TWO"
            elif rects["LVL_3"].collidepoint(mouse_pos): return "LAUNCH_LEVEL_THREE"

    # 1. Render Custom Image Background
    screen.blit(select_bg, (0, 0))
    
    # Animated breathing title text
    title_pulse = int(math.sin(timer * 2) * 4)
    title_lbl = font_title.render("SELECT A SUBCONSCIOUS LAYER", True, COLOUR_TEXT)
    title_rect = title_lbl.get_rect(center=(1280 // 2, 100 + title_pulse))
    
    screen.blit(font_title.render("SELECT A SUBCONSCIOUS LAYER", True, COLOUR_TEXT_SHADOW), (title_rect.x + 3, title_rect.y + 3))
    screen.blit(title_lbl, title_rect)

    # 2. Level Cards (Semi-transparent with shifting neon borders)
    labels = [
        ("LAYER 1", "The Sleep Barrier", "Tutorial", rects["LVL_1"], (150, 100, 250)),
        ("LAYER 2", "The Deep Dream", "30s Survival", rects["LVL_2"], (250, 100, 150)),
        ("LAYER 3", "Infinite Void", "Endless Run", rects["LVL_3"], (100, 250, 200))
    ]

    # Calculate a moving pastel neon glow value based on your timer
    glow_color = (
        int(180 + math.sin(timer) * 75),
        int(140 + math.cos(timer) * 60),
        int(220 + math.sin(timer * 0.5) * 35)
    )

    for name, sub, desc, rect, hover_col in labels:
        is_hovered = rect.collidepoint(mouse_pos)
        
        # Transparent overlay container layout
        card_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        card_surf.fill((30, 20, 40, 160) if not is_hovered else (*hover_col, 80))
        screen.blit(card_surf, rect.topleft)
        
        # Shifting animated glowing borders
        border_col = glow_color if is_hovered else (100, 80, 120)
        border_w = 3 if is_hovered else 1
        pygame.draw.rect(screen, border_col, rect, width=border_w, border_radius=12)
        
        # Text layouts
        t_lbl = font_title.render(name, True, COLOUR_TEXT)
        s_lbl = font_button.render(sub, True, (240, 200, 230))
        d_lbl = font_button.render(desc, True, (180, 170, 190))
        
        screen.blit(t_lbl, t_lbl.get_rect(center=(rect.centerx, rect.y + 60)))
        screen.blit(s_lbl, s_lbl.get_rect(center=(rect.centerx, rect.y + 140)))
        screen.blit(d_lbl, d_lbl.get_rect(center=(rect.centerx, rect.y + 280)))

    return "KEEP_MENU_ALIVE"