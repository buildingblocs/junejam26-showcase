import pygame
import os
import math
import random
import entities  
import health    

W, H = 1280, 800  
page = 0
is_paused = False
has_moved = False
has_fired = False

player = None
bullets = []
enemy_bullets = [] # <-- Level 3 exclusive threat vector tracker
health_sys = None  
survival_score = 0
spawn_timer = 0
pulse_time = 0.0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- LOAD LEVEL 3 STAGE IMAGE INTRO BANNER ---
STAGE_IMG_PATH = os.path.join(BASE_DIR, "stage3_intro.png")
if os.path.exists(STAGE_IMG_PATH):
    stage_banner = pygame.image.load(STAGE_IMG_PATH).convert_alpha()
    stage_banner = pygame.transform.scale(stage_banner, (400, 150))
else:
    # Deep void neon fallback layout placeholder
    stage_banner = pygame.Surface((400, 150))
    stage_banner.fill((15, 30, 30))
    pygame.draw.rect(stage_banner, (0, 255, 200), stage_banner.get_rect(), width=2)

def run_level_cycle(screen, font_title, font_button, sw, sh, c_txt):
    global player, bullets, enemy_bullets, is_paused, health_sys, survival_score, spawn_timer, pulse_time
    
    if player is None:
        player = entities.Plr(sw // 2, sh // 2 + 80)
    if health_sys is None:
        health_sys = health.HealthManager(max_hearts=3)

    if not is_paused:
        player.move(pygame.key.get_pressed(), sw, sh, current_page=99)
        survival_score += 1
        spawn_timer += 1
        pulse_time += 0.08

        # --- DYNAMIC HARDCORE THREAT GENERATOR ---
        # Spawns ring arrays of hostile bullets firing from off-screen points inward
        if spawn_timer >= 45:  # Every 45 frames, spawn bullet traps
            spawn_timer = 0
            angles = [0, 45, 90, 135, 180, 225, 270, 315]
            spawn_radius = 500
            
            # Choose a shifting anchor point near the center of the viewport
            anchor_x = sw // 2 + random.randint(-150, 150)
            anchor_y = sh // 2 + random.randint(-100, 100)
            
            for a in angles:
                rad = math.radians(a)
                sx = anchor_x + math.cos(rad) * spawn_radius
                sy = anchor_y + math.sin(rad) * spawn_radius
                # Fire inward toward the center anchor target position vector paths
                enemy_bullets.append(entities.Blt(sx, sy, anchor_x, anchor_y, speed=6))

        # Track friendly projectiles
        for b in bullets[:]:
            b.update()
            if b.rect.x < 0 or b.rect.x > sw or b.rect.y < 0 or b.rect.y > sh:
                bullets.remove(b)

        # Track hostile projectile behaviors + Process bounding hit collision logic
        for eb in enemy_bullets[:]:
            eb.update()
            # If hit box intersects player character limits, execute life point reductions
            if eb.rect.colliderect(player.rect):
                health_sys.take_damage(1)
                if eb in enemy_bullets:
                    enemy_bullets.remove(eb)
            elif eb.rect.x < -100 or eb.rect.x > sw + 100 or eb.rect.y < -100 or eb.rect.y > sh + 100:
                if eb in enemy_bullets:
                    enemy_bullets.remove(eb)

    # --- RENDERING GENERATION ---
    # Shifting dynamic canvas color tint background layer (Simulating deep panic state pulse)
    pulse_intensity = int(14 + math.sin(pulse_time) * 6)
    screen.fill((pulse_intensity, 12, pulse_intensity + 4)) 
    
    # Render Stage Image graphic overhead
    screen.blit(stage_banner, (sw // 2 - 200, 110))
    
    # Draw Player 
    pygame.draw.rect(screen, (60, 220, 100), player.rect, border_radius=8)

    # Draw player tracking ammo paths
    for b in bullets:
        pygame.draw.circle(screen, (100, 255, 255), (b.rect.centerx, b.rect.centery), 6)
        
    # Draw hostile bullet structures (Flaming warning orange particles)
    for eb in enemy_bullets:
        pygame.draw.circle(screen, (255, 140, 0), (eb.rect.centerx, eb.rect.centery), 7)
        pygame.draw.circle(screen, (255, 255, 200), (eb.rect.centerx, eb.rect.centery), 3)

    # Heads-Up Dashboard
    health_sys.draw_hud(screen, x=40, y=40)
    
    # Live data text streams
    hud_txt = font_button.render(f"LEVEL 3: DEEPEST LAYER | CORRUPTION DEPTH: {survival_score // 10}m", False, (0, 255, 200))
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
                # Fast bullet counter attack velocity limits configuration mapping
                bullets.append(entities.Blt(player.rect.centerx, player.rect.centery, m_pos[0], m_pos[1], speed=16))