import pygame
import os

import entities  
import eyelid    
import health    
import shop      
import tutorial  
import enemies
# --- LOAD CHARGER IMAGE ---
# Make sure you have "charger.png" in your project folder 
# or update the filename to match your actual asset

wave_manager = None

# --- TOP OF FILE ---
charger_img = None
import game_state
from level_manager import WaveManager
W, H = 1280, 800  
C_TXT = (255, 255, 255)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITE_PATH = os.path.join(BASE_DIR, "character_portrait.png")
CHARGER_IMG_PATH = os.path.join(BASE_DIR, "assets", "charger.png")

if os.path.exists(CHARGER_IMG_PATH):
    charger_img = pygame.image.load(CHARGER_IMG_PATH).convert_alpha()
    # Adjust size as needed
    charger_img = pygame.transform.scale(charger_img, (50, 50)) 
else:
    # Fallback if the image file is missing
    charger_img = pygame.Surface((50, 50))
    charger_img.fill((200, 50, 50)) # Red block if image missing
# Initialize as None so the game knows it exists
# --- LOAD LEVEL 1 STAGE IMAGE INTRO BANNER ---
STAGE_IMG_PATH = os.path.join(BASE_DIR, "stage1_intro.png")
if os.path.exists(STAGE_IMG_PATH):
    stage_banner = pygame.image.load(STAGE_IMG_PATH).convert_alpha()
    stage_banner = pygame.transform.scale(stage_banner, (400, 150))
else:
    # Safe Fallback placeholder asset if image is absent
    stage_banner = pygame.Surface((400, 150))
    stage_banner.fill((45, 50, 70))
    pygame.draw.rect(stage_banner, (90, 100, 130), stage_banner.get_rect(), width=2)

if os.path.exists(SPRITE_PATH):
    talk_sprite = pygame.image.load(SPRITE_PATH).convert_alpha()
    talk_sprite = pygame.transform.scale(talk_sprite, (140, 140)) 
else:
    talk_sprite = pygame.Surface((140, 140))
    talk_sprite.fill((75, 85, 110))

page = 0
is_paused = False
last_page_turn_time = 0      
PAGE_TURN_COOLDOWN = 250     

has_moved = False
has_fired = False

player = None
bullets = []
eyelids = None  
health_sys = None  
shop_sys = None     



def run_level_cycle(screen, font_title, font_button, sw, sh, tc):
    global player, health_sys, wave_manager, charger_img, page, bullets, is_paused, eyelids, shop_sys, has_moved, has_fired

    # 1. INITIALIZATION
    if health_sys is None: health_sys = health.HealthManager(max_hearts=3)
    if player is None: player = entities.Plr(sw // 2, sh // 2 - 100)
    if wave_manager is None: wave_manager = WaveManager(stage_num=1); wave_manager.spawn_wave()
    if eyelids is None: eyelids = eyelid.EyelidManager(sw, sh, BASE_DIR)
    if shop_sys is None: shop_sys = shop.ShopManager()
    
    # 2. GAME LOGIC
    screen.fill((12, 12, 18))
    
    if not is_paused:
        # Combat/Movement Logic
        if page > 16 and player:
            if player.move(pygame.key.get_pressed(), sw, sh, page): has_moved = True
            
            # Bullet/Enemy Collision Loop
            for b in bullets[:]:
                b.update()
                hit = False
                for e in wave_manager.enemies[:]:
                    if b.rect.colliderect(e.rect):
                        e.hp -= 1
                        if e.hp <= 0: wave_manager.enemies.remove(e)
                        hit = True
                        break
                if hit or (b.rect.x < 0 or b.rect.x > sw or b.rect.y < 0 or b.rect.y > sh):
                    if b in bullets: bullets.remove(b)
        
        eyelids.update_gravity() 

    # 3. RENDERING LAYERS
    # Layer 1: Game World (Only during combat, i.e., page > 16)
    if page > 16 and eyelids.eyes_open:
        for e in wave_manager.enemies:
            screen.blit(charger_img, e.rect.topleft)
        for b in bullets:
            pygame.draw.circle(screen, (255, 255, 100), (int(b.rect.centerx), int(b.rect.centery)), 4)
        pygame.draw.rect(screen, (60, 220, 100), player.rect, border_radius=8)
        health_sys.draw_hud(screen, x=40, y=40)

    # Layer 2: UI/Dialogue (Hidden after Page 16)
    if page < 16:
        box_rect = pygame.Rect(50, 600, sw - 100, 150)
        pygame.draw.rect(screen, (0, 0, 0, 150), box_rect) # Text box background
        story_text = font_button.render(tutorial.DIALOGUE[page], True, (255, 255, 255))
        screen.blit(story_text, (70, 620))

    # Layer 3: Shop (Appears exactly on Page 16)
    if page == 16 and shop_sys:
        shop_sys.draw(screen, font_title, font_button, sw, sh, tc)

    # Layer 4: Eyelids (Always Last)
    eyelids.draw(screen, font_button)
def handle_events(events):
    global page, bullets, player, is_paused, eyelids, shop_sys, has_moved, has_fired, last_page_turn_time
    
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                is_paused = True
                continue
            if is_paused:
                if event.key == pygame.K_SPACE: is_paused = False
                continue

            if page == 16 and shop_sys:
                if event.key == pygame.K_1: shop_sys.buy_fire_rate()
                elif event.key == pygame.K_2: shop_sys.buy_damage()

            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                current_time = pygame.time.get_ticks()
                if current_time - last_page_turn_time < PAGE_TURN_COOLDOWN: 
                    continue 
                
                if tutorial.can_advance_page(page, has_moved, has_fired, shop_sys.has_shopped):
                    page += 1
                    last_page_turn_time = current_time 
                    
            elif event.key == pygame.K_SPACE and eyelids:
                if page == len(tutorial.DIALOGUE) - 1 and not eyelids.is_waking_up:
                    eyelids.drop_eyelids() 
                else:
                    eyelids.register_mash()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = pygame.mouse.get_pos()
            
            if page == 16 and shop_sys:
                if shop_sys.btn1_rect.collidepoint(m_pos):
                    shop_sys.buy_fire_rate()
                elif shop_sys.btn2_rect.collidepoint(m_pos):
                    shop_sys.buy_damage()
                continue

            if player and eyelids and shop_sys and (page >= 14 or eyelids.is_waking_up or eyelids.eyes_open):
                bullets.append(entities.Blt(player.rect.centerx, player.rect.centery, m_pos[0], m_pos[1], shop_sys.bullet_speed))
                if page == 14: 
                    has_fired = True
            # If in the shop (Page 16) and an item is bought, move to game
            if page == 16 and shop_sys.has_shopped:
                if event.key == pygame.K_RETURN:
                    page += 1 # Advance to gameplay (page 17+)