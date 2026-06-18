import pygame
import os
import entities  
import health    

W, H = 1280, 800  
page = 0
is_paused = False
has_moved = False
has_fired = False

player = None
bullets = []
health_sys = None  
level_timer = 1800  # 30 seconds at 60 FPS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- LOAD LEVEL 2 STAGE IMAGE INTRO BANNER ---
STAGE_IMG_PATH = os.path.join(BASE_DIR, "stage2_intro.png")
if os.path.exists(STAGE_IMG_PATH):
    stage_banner = pygame.image.load(STAGE_IMG_PATH).convert_alpha()
    stage_banner = pygame.transform.scale(stage_banner, (400, 150))
else:
    # Safe Fallback placeholder if file is absent
    stage_banner = pygame.Surface((400, 150))
    stage_banner.fill((70, 45, 45))
    pygame.draw.rect(stage_banner, (130, 90, 90), stage_banner.get_rect(), width=2)

def run_level_cycle(screen, font_title, font_button, sw, sh, c_txt):
    global player, bullets, is_paused, health_sys, level_timer
    
    if player is None:
        player = entities.Plr(sw // 2, sh // 2 + 80)
    if health_sys is None:
        health_sys = health.HealthManager(max_hearts=3)

    if not is_paused:
        player.move(pygame.key.get_pressed(), sw, sh, current_page=99)
        level_timer -= 1  

        for b in bullets[:]:
            b.update()
            if b.rect.x < 0 or b.rect.x > sw or b.rect.y < 0 or b.rect.y > sh:
                bullets.remove(b)

    screen.fill((18, 12, 12))  # Dark Red Tint 
    
    # Render Stage Intro Banner graphic
    screen.blit(stage_banner, (sw // 2 - 200, 110))
    
    for b in bullets:
        pygame.draw.circle(screen, (255, 100, 100), (b.rect.centerx, b.rect.centery), 5)
    pygame.draw.rect(screen, (60, 220, 100), player.rect, border_radius=8)

    health_sys.draw_hud(screen, x=40, y=40)
    
    time_left = max(0, level_timer // 60)
    hud_txt = font_button.render(f"LEVEL 2: SURVIVE THE NIGHTMARE | TIME: {time_left}s", False, (255, 255, 255))
    screen.blit(hud_txt, (40, 95))

def handle_events(events):
    global bullets, player, is_paused
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                is_paused = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if player:
                m_pos = pygame.mouse.get_pos()
                bullets.append(entities.Blt(player.rect.centerx, player.rect.centery, m_pos[0], m_pos[1], speed=14))