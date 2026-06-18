import pygame
import sys
import math
import random
import asyncio

pygame.mixer.pre_init(44100, -16, 2, 512)

pygame.init()
pygame.font.init()
pygame.mixer.init()

SCREEN_WIDTH = 950
SCREEN_HEIGHT = 650
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Character Selection Portal & Subway Obby with Math Test")
clock = pygame.time.Clock()

COLOR_BG = (212, 218, 224)          
COLOR_CARD = (255, 255, 255)        
COLOR_PRIMARY = (30, 41, 59)        
COLOR_SECONDARY = (71, 85, 105)     
COLOR_ACCENT = (79, 70, 229)        
COLOR_HOVER = (243, 244, 246)       
WHITE = (255, 255, 255)
COLOR_SUCCESS = (16, 185, 129)  
COLOR_RED = (239, 68, 68)

font_title = pygame.font.SysFont("Helvetica", 42, bold=True)
font_header = pygame.font.SysFont("Helvetica", 26, bold=True)
font_body = pygame.font.SysFont("Helvetica", 20)
font_small = pygame.font.SysFont("Helvetica", 15)

current_volume = 0.3
track_list = [
    {"name": "The Neighbourhood - Sweater Weather", "file": "music/sweater_weather.ogg"},
    {"name": "Wave to Earth - Love", "file": "music/love.ogg"},
    {"name": "Malcolm Todd - Slowww", "file": "music/Slowww.ogg"},
    {"name": "Malcolm Todd - Chest Pain", "file": "music/Chest_pain.ogg"},
    {"name": "Malcolm Todd - Incorrect", "file": "music/Incorrect.ogg"},
    {"name": "Malcolm Todd - Attention", "file": "music/Attention.ogg"},
]
active_track_idx = 0

# --- JUKEBOX SCROLLING SYSTEM ---
scroll_offset = 0
MAX_VISIBLE_TRACKS = 3
TRACK_CARD_WIDTH = 250
TRACK_CARD_HEIGHT = 70
TRACK_CARD_GAP = 15

def play_selected_track():
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(track_list[active_track_idx]["file"])
        pygame.mixer.music.set_volume(current_volume)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"Error loading song file {track_list[active_track_idx]['file']}: {e}")

# Play initial default track
play_selected_track()

# --- PIXEL ART OBBY DEFINITIONS ---
def create_pixel_surface(art_array, colors_dict, scale):
    grid_width = len(art_array[0])
    grid_height = len(art_array)
    small_surf = pygame.Surface((grid_width, grid_height), pygame.SRCALPHA)
    for y, row in enumerate(art_array):
        for x, char in enumerate(row):
            if char in colors_dict:
                small_surf.set_at((x, y), colors_dict[char])
    return pygame.transform.scale(small_surf, (grid_width * scale, grid_height * scale))

SPIKE_COLORS = {
    '.': (0, 0, 0, 0), 'R': (220, 50, 50, 255),
    'D': (130, 20, 20, 255), 'W': (255, 150, 150, 255)
}
SPIKE_ART = [
    "........", "...WR...", "..WWRR..", "..WWRR..",
    ".WWDDDR.", ".WWDDDR.", "WWDDDDDDR", "WWDDDDDDR"
]

DOOR_COLORS = {
    '.': (0, 0, 0, 0), 'D': (60, 30, 15, 255),
    'L': (139, 69, 19, 255), 'G': (255, 215, 0, 255)
}
DOOR_ART = [
    "DDDDDDDDDD", "DLLLLLLLLD", "DLDDDDDDDD", "DLDDDDDDDD",
    "DLLLLLLLLD", "DLDDDDDDDD", "DLDDDDDDDD", "DLLLLLLLLD",
    "DLDDDDDDDD", "DLDDDDDGGD", "DLLLLLLGGD", "DLDDDDDDDD",
    "DLDDDDDDDD", "DLLLLLLLLD", "DDDDDDDDDD"
]

# --- SUBWAY OBBY SPRITE CLASSES ---
class ObbyPlayer(pygame.sprite.Sprite):
    def __init__(self, width, ground_level, player_surface):
        super().__init__()
        self.image = player_surface
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.left = 150
        self.rect.bottom = ground_level
        self.y_vel = 0
        self.jump_power = -15
        self.is_jumping = False
        self.ground_level = ground_level

    def jump(self):
        if not self.is_jumping:
            self.y_vel = self.jump_power
            self.is_jumping = True

    def update(self):
        self.y_vel += 0.8  # Gravity
        self.rect.y += self.y_vel
        if self.rect.bottom >= self.ground_level:
            self.rect.bottom = self.ground_level
            self.y_vel = 0
            self.is_jumping = False

class ObbyObstacle(pygame.sprite.Sprite):
    def __init__(self, width, ground_level):
        super().__init__()
        scale = random.choice([4, 5, 6])
        self.image = create_pixel_surface(SPIKE_ART, SPIKE_COLORS, scale)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.left = width + 50
        self.rect.bottom = ground_level
        self.width = width

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < -50:
            self.kill()

class ObbyExitDoor(pygame.sprite.Sprite):
    def __init__(self, width, ground_level):
        super().__init__()
        self.image = create_pixel_surface(DOOR_ART, DOOR_COLORS, scale=6)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.left = width + 50
        self.rect.bottom = ground_level
        self.width = width

    def update(self, speed):
        self.rect.x -= speed
        if self.rect.right < -50:
            self.kill()

# --- DICTIONARIES TO SUPPORT DIRECTIONAL ASSETS ---
sprites_small = {}
sprites_home_left = {}
sprites_home_right = {}
sprites_uni_left = {}
sprites_uni_right = {}
bg_home = None
bg_house_outside = None
bg_outside_morning = None
bg_outside_dark = None
bg_inside_taxi = None
bg_inside_bus = None
bg_mrt_station = None
bg_mrt_obby = None

try:
    guy_img = pygame.image.load("pictures/guy_at_home.png")
    sprites_small["Guy"] = pygame.transform.smoothscale(guy_img, (90, 110))
    sprites_home_left["Guy"] = pygame.transform.smoothscale(guy_img, (180, 220))
    
    guy_right_home = pygame.image.load("pictures/guy_right_home.png")
    sprites_home_right["Guy"] = pygame.transform.smoothscale(guy_right_home, (180, 220))
    
    guy_uni = pygame.image.load("pictures/guy_uniform.png")
    sprites_uni_left["Guy"] = pygame.transform.smoothscale(guy_uni, (180, 220))
    
    guy_right_uni = pygame.image.load("pictures/guy_right_uni.png")
    sprites_uni_right["Guy"] = pygame.transform.smoothscale(guy_right_uni, (180, 220))
    
    girl_img = pygame.image.load("pictures/girl_at_home.png")
    sprites_small["Girl"] = pygame.transform.smoothscale(girl_img, (90, 110))
    sprites_home_left["Girl"] = pygame.transform.smoothscale(girl_img, (180, 220))
    
    girl_right_home = pygame.image.load("pictures/girl_right_home.png")
    sprites_home_right["Girl"] = pygame.transform.smoothscale(girl_right_home, (180, 220))
    
    girl_uni = pygame.image.load("pictures/girl_uniform.png")
    sprites_uni_left["Girl"] = pygame.transform.smoothscale(girl_uni, (180, 220))
    
    girl_right_uni = pygame.image.load("pictures/girl_right_uni.png")
    sprites_uni_right["Girl"] = pygame.transform.smoothscale(girl_right_uni, (180, 220))

    raw_home = pygame.image.load("pictures/home.png")
    bg_home = pygame.transform.smoothscale(raw_home, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    raw_house_out = pygame.image.load("pictures/house_outside.png")
    bg_house_outside = pygame.transform.smoothscale(raw_house_out, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    raw_morning = pygame.image.load("pictures/outside_morning.png")
    bg_outside_morning = pygame.transform.smoothscale(raw_morning, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    raw_dark = pygame.image.load("pictures/outside_dark.png")
    bg_outside_dark = pygame.transform.smoothscale(raw_dark, (SCREEN_WIDTH, SCREEN_HEIGHT))

    raw_taxi = pygame.image.load("pictures/inside_taxi.png")
    bg_inside_taxi = pygame.transform.smoothscale(raw_taxi, (SCREEN_WIDTH, SCREEN_HEIGHT))

    raw_bus = pygame.image.load("pictures/in_bus.png")
    bg_inside_bus = pygame.transform.smoothscale(raw_bus, (SCREEN_WIDTH, SCREEN_HEIGHT))

    raw_mrt = pygame.image.load("pictures/mrt_station.png")
    bg_mrt_station = pygame.transform.smoothscale(raw_mrt, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    raw_mrt_obby = pygame.image.load("pictures/mrt.png")
    bg_mrt_obby = pygame.transform.smoothscale(raw_mrt_obby, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
except pygame.error as e:
    print(f"Asset loading error: {e}. Check directory file placements.")

characters = [
    {"name": "Guy", "desc": "A Guy.", "color": (59, 130, 246)},
    {"name": "Girl", "desc": "A Girl.", "color": (236, 72, 153)}
]

state = "LOGIN"  
previous_state = "LOGIN" 
username_str = ""
selected_char_idx = None

# --- MAP NAVIGATION MECHANICS ---
char_x = 400  
char_y = 345  
char_speed = 10  
facing_direction = "LEFT"  
movement_enabled = False  
near_wardrobe = False
near_door = False
outfit_changed = False

near_bus_stop = False
near_taxi_stand = False
near_mrt_entrance = False
near_train_doors = False

current_scene = "ROOM" 
time_of_day_ticks = 0.0
MAX_TIME_TICKS = 200.0  

evening_walk_ticks = 0
MAX_EVENING_WALK = 120  

fade_alpha = 0
fade_direction = 1  
next_scene_target = None

# --- OBBY MANAGEMENT STATES ---
OBBY_SPAWN_EVENT = pygame.USEREVENT + 2
obby_initialized = False
obby_player = None
obby_obstacles = None
obby_doors = None
obby_all_moving = None
obby_speed = 7
obby_spawn_delay = 1400
obby_obstacles_spawned = 0
obby_game_started = False
obby_instruction_alpha = 255
snapshot_surf = None

# --- MATH EXAM SYSTEM CONFIGURATION (5 QUESTIONS) ---
math_questions = [
    {"q": "Question 1:  12 + 15 = ?", "a": "27"},
    {"q": "Question 2:  45 - 18 = ?", "a": "27"},
    {"q": "Question 3:  7 * 8 = ?", "a": "56"},
    {"q": "Question 4:  81 / 9 = ?", "a": "9"},
    {"q": "Question 5:  12 * 5 = ?", "a": "60"}
]
math_answers_input = ["", "", "", "", ""]
active_math_field = 0  
math_exam_submitted = False
math_exam_score = 0
math_exam_passed = False

def draw_text_centered(text, font, color, center_x, y):
    surface = font.render(text, True, color)
    text_width = surface.get_width()
    screen.blit(surface, (center_x - text_width // 2, y))

def draw_time_widget(surface, x, y, radius, progress):
    pygame.draw.circle(surface, (51, 65, 85), (x, y), radius + 3, 2)
    pygame.draw.circle(surface, (15, 23, 42), (x, y), radius)
    if progress > 0:
        points = [(x, y)]
        steps = int(360 * progress)
        for angle in range(-90, steps - -90 + 1):
            rad = math.radians(angle)
            px = x + radius * math.cos(rad)
            py = y + radius * math.sin(rad)
            points.append((px, py))
        if len(points) > 2:
            pygame.draw.polygon(surface, (251, 146, 60), points)

async def main():
    global active_math_field, active_track_idx, char_x, current_scene, current_volume
    global evening_walk_ticks, facing_direction, fade_alpha, fade_direction, font_small
    global math_exam_passed, math_exam_score, math_exam_submitted, movement_enabled
    global near_bus_stop, near_door, near_mrt_entrance, near_taxi_stand, near_train_doors
    global near_wardrobe, next_scene_target, obby_all_moving, obby_doors, obby_game_started
    global obby_initialized, obby_instruction_alpha, obby_obstacles, obby_obstacles_spawned
    global obby_player, obby_speed, outfit_changed, previous_state, running, scroll_offset
    global selected_char_idx, snapshot_surf, state, time_of_day_ticks, username_str

    running = True
    while running:
        screen.fill(COLOR_BG)

        mx, my = pygame.mouse.get_pos()
        mid_x = SCREEN_WIDTH // 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == "SETTINGS":
                    if event.button == 4:  
                        scroll_offset = max(0, scroll_offset - 1)
                    elif event.button == 5:  
                        scroll_offset = min(len(track_list) - MAX_VISIBLE_TRACKS, scroll_offset + 1)

                if event.button == 1: 
                    if state == "LOGIN":
                        if (mid_x - 150) <= mx <= (mid_x + 150) and 380 <= my <= 445:
                            if username_str.strip() == "":
                                username_str = "Player 1"
                            state = "CHAR_SELECT"

                    elif state == "CHAR_SELECT":
                        for idx in range(len(characters)):
                            bx = mid_x - 270 + idx * 280
                            by = 220
                            if bx <= mx <= bx + 260 and by <= my <= by + 260:
                                selected_char_idx = idx

                        if selected_char_idx is not None:
                            if (mid_x - 120) <= mx <= (mid_x + 120) and 535 <= my <= 590:
                                state = "GAME_START"

                    elif state == "SETTINGS":
                        for i in range(5):
                            btn_x = mid_x - 200 + i * 100
                            if btn_x - 40 <= mx <= btn_x + 40 and 220 <= my <= 270:
                                current_volume = i * 0.25
                                pygame.mixer.music.set_volume(current_volume)

                        for visible_idx in range(MAX_VISIBLE_TRACKS):
                            actual_idx = scroll_offset + visible_idx
                            if actual_idx >= len(track_list):
                                break

                            card_x = mid_x - 390 + visible_idx * (TRACK_CARD_WIDTH + TRACK_CARD_GAP)
                            if card_x <= mx <= card_x + TRACK_CARD_WIDTH and 360 <= my <= 430:
                                if active_track_idx != actual_idx:
                                    active_track_idx = actual_idx
                                    play_selected_track()

                        if mid_x - 100 <= mx <= mid_x + 100 and 520 <= my <= 580:
                            state = previous_state

                    elif state == "GAME_START":
                        if current_scene == "OBBY_WIN" and not math_exam_submitted:
                            for i in range(len(math_questions)):
                                box_rect = pygame.Rect(mid_x + 80, 176 + i * 65, 120, 40)
                                if box_rect.collidepoint((mx, my)):
                                    active_math_field = i

                            submit_btn = pygame.Rect(mid_x - 100, 500, 200, 50)
                            if submit_btn.collidepoint((mx, my)):
                                math_exam_score = 0
                                for idx, q_data in enumerate(math_questions):
                                    if math_answers_input[idx].strip() == q_data["a"]:
                                        math_exam_score += 1
                                math_exam_passed = (math_exam_score >= 4)  
                                math_exam_submitted = True

            elif event.type == OBBY_SPAWN_EVENT and state == "GAME_START" and current_scene == "MRT_RIDE" and obby_game_started:
                if obby_obstacles_spawned < 10:
                    obs = ObbyObstacle(SCREEN_WIDTH, SCREEN_HEIGHT - 120)
                    obby_obstacles.add(obs)
                    obby_all_moving.add(obs)
                    obby_obstacles_spawned += 1
                elif obby_obstacles_spawned == 10:
                    door = ObbyExitDoor(SCREEN_WIDTH, SCREEN_HEIGHT - 120)
                    obby_doors.add(door)
                    obby_all_moving.add(door)
                    obby_obstacles_spawned += 1
                    pygame.time.set_timer(OBBY_SPAWN_EVENT, 0)

            elif event.type == pygame.KEYDOWN:
                if state == "LOGIN":
                    if event.key == pygame.K_BACKSPACE:
                        username_str = username_str[:-1]
                    elif event.key == pygame.K_RETURN:
                        if username_str.strip() == "":
                            username_str = "Player 1"
                        state = "CHAR_SELECT"
                    elif event.key == pygame.K_s:
                        previous_state = "LOGIN"
                        state = "SETTINGS"
                    else:
                        if len(username_str) < 16 and event.unicode.isprintable():
                            username_str += event.unicode

                elif state == "CHAR_SELECT":
                    if event.key == pygame.K_s:
                        previous_state = "CHAR_SELECT"
                        state = "SETTINGS"

                elif state == "SETTINGS":
                    if event.key == pygame.K_ESCAPE:
                        state = previous_state
                    elif event.key == pygame.K_LEFT:
                        scroll_offset = max(0, scroll_offset - 1)
                    elif event.key == pygame.K_RIGHT:
                        scroll_offset = min(len(track_list) - MAX_VISIBLE_TRACKS, scroll_offset + 1)

                elif state == "GAME_START":
                    if current_scene == "MRT_RIDE":
                        if event.key in (pygame.K_SPACE, pygame.K_UP):
                            if not obby_game_started:
                                obby_game_started = True
                                pygame.time.set_timer(OBBY_SPAWN_EVENT, obby_spawn_delay)
                            if obby_player:
                                obby_player.jump()
                    elif current_scene in ["OBBY_LOSE", "TAXI_LOSE"]:
                        pass
                    elif current_scene == "OBBY_WIN":
                        if not math_exam_submitted:
                            if event.key == pygame.K_BACKSPACE:
                                math_answers_input[active_math_field] = math_answers_input[active_math_field][:-1]
                            elif event.key == pygame.K_TAB:
                                active_math_field = (active_math_field + 1) % len(math_questions)
                            else:
                                if len(math_answers_input[active_math_field]) < 5 and event.unicode.isdigit():
                                    math_answers_input[active_math_field] += event.unicode
                        else:
                            pass

                    if event.key == pygame.K_s and current_scene not in ["OBBY_LOSE", "TAXI_LOSE", "OBBY_WIN", "ENDING_SCENE"]:
                        previous_state = "GAME_START"
                        state = "SETTINGS"
                    elif event.key == pygame.K_f:
                        movement_enabled = True
                    elif event.key == pygame.K_e:
                        if current_scene == "ROOM":
                            if near_wardrobe and not outfit_changed:
                                outfit_changed = True
                            elif near_door and outfit_changed:
                                current_scene = "HOUSE_OUTSIDE"
                                char_x = 50  
                        elif current_scene == "STREET_WALK":
                            if near_bus_stop:
                                current_scene = "FADE_TO_EVENING"
                                fade_alpha = 0
                                fade_direction = 1
                                next_scene_target = "BUS_RIDE"
                            elif near_taxi_stand:
                                current_scene = "TAXI_RIDE"
                                time_of_day_ticks = 0.0  # Reset timer specifically for taxi ride tracking
                            elif near_mrt_entrance:
                                current_scene = "FADE_TO_EVENING"
                                fade_alpha = 0
                                fade_direction = 1
                                next_scene_target = "MRT_APPROACH"
                        elif current_scene == "MRT_APPROACH" and near_train_doors:
                            current_scene = "FADE_TO_EVENING"
                            fade_alpha = 0
                            fade_direction = 1
                            next_scene_target = "MRT_RIDE"

        # --- Live Engine Updates ---
        if state == "GAME_START" and movement_enabled:
            keys = pygame.key.get_pressed()

            if current_scene not in ["FADE_TO_EVENING", "BUS_RIDE", "MRT_RIDE", "TAXI_RIDE", "STREET_EVENING", "ENDING_SCENE", "OBBY_LOSE", "TAXI_LOSE", "OBBY_WIN"]:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    char_x -= char_speed
                    facing_direction = "LEFT"  
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    char_x += char_speed
                    facing_direction = "RIGHT" 

            if current_scene == "ROOM":
                if char_x < -40: char_x = -40
                if char_x > SCREEN_WIDTH - 140: char_x = SCREEN_WIDTH - 140
                near_wardrobe = (char_x >= 720)
                near_door = (char_x <= 40)

            elif current_scene == "HOUSE_OUTSIDE":
                if char_x < -40: char_x = -40
                if char_x > SCREEN_WIDTH - 130:
                    current_scene = "STREET_WALK"
                    char_x = 40  

            elif current_scene == "STREET_WALK":
                if char_x < -40: char_x = -40
                if char_x > SCREEN_WIDTH - 140: char_x = SCREEN_WIDTH - 140

                near_bus_stop = (150 <= char_x <= 320)
                near_taxi_stand = (380 <= char_x <= 540)
                near_mrt_entrance = (600 <= char_x <= 820)

                if time_of_day_ticks < MAX_TIME_TICKS:
                    time_of_day_ticks += 0.5
                else:
                    current_scene = "FADE_TO_EVENING"
                    fade_alpha = 0
                    fade_direction = 1
                    next_scene_target = "STREET_EVENING"

            elif current_scene == "MRT_APPROACH":
                if char_x < -40: char_x = -40
                if char_x > SCREEN_WIDTH - 140: char_x = SCREEN_WIDTH - 140
                near_train_doors = (char_x >= 650)

            elif current_scene == "BUS_RIDE":
                if time_of_day_ticks < MAX_TIME_TICKS:
                    time_of_day_ticks += 2.0
                else:
                    current_scene = "FADE_TO_EVENING"
                    fade_alpha = 0
                    fade_direction = 1
                    next_scene_target = "STREET_EVENING"

            elif current_scene == "TAXI_RIDE":
                if time_of_day_ticks < MAX_TIME_TICKS:
                    time_of_day_ticks += 2.0
                else:
                    snapshot_surf = screen.copy()
                    current_scene = "TAXI_LOSE"

            elif current_scene == "STREET_EVENING":
                if char_x < -40: char_x = -40
                if char_x > SCREEN_WIDTH - 140: char_x = SCREEN_WIDTH - 140

                evening_walk_ticks += 1
                if evening_walk_ticks >= MAX_EVENING_WALK:
                    current_scene = "ENDING_SCENE"

            elif current_scene == "MRT_RIDE":
                if not obby_initialized:
                    GROUND_LEVEL = SCREEN_HEIGHT - 70
                    chosen_name = characters[selected_char_idx]["name"]
                    if outfit_changed:
                        player_asset = sprites_uni_right.get(chosen_name, sprites_uni_left.get(chosen_name))
                    else:
                        player_asset = sprites_home_right.get(chosen_name, sprites_home_left.get(chosen_name))

                    obby_char_surface = pygame.transform.smoothscale(player_asset, (75, 95))

                    obby_player = ObbyPlayer(SCREEN_WIDTH, GROUND_LEVEL, obby_char_surface)
                    obby_obstacles = pygame.sprite.Group()
                    obby_doors = pygame.sprite.Group()
                    obby_all_moving = pygame.sprite.Group()
                    obby_speed = 7
                    obby_obstacles_spawned = 0
                    obby_game_started = False
                    obby_instruction_alpha = 255
                    obby_initialized = True

                obby_player.update()
                if obby_game_started:
                    for obj in obby_all_moving:
                        obj.update(obby_speed)
                    if obby_instruction_alpha > 0:
                        font_obby_inst = pygame.font.SysFont("Courier New", 32, bold=True)
                        shadow = font_obby_inst.render("PRESS SPACE / UP TO START & JUMP", True, (0, 0, 0))
                        text = font_obby_inst.render("PRESS SPACE / UP TO START & JUMP", True, (255, 255, 50))

                        fade_surface = pygame.Surface((text.get_width() + 4, text.get_height() + 4), pygame.SRCALPHA)
                        fade_surface.blit(shadow, (4, 4))
                        fade_surface.blit(text, (0, 0))
                        fade_surface.set_alpha(obby_instruction_alpha)

                        screen.blit(fade_surface, fade_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))

                if pygame.sprite.spritecollide(obby_player, obby_obstacles, False, pygame.sprite.collide_mask):
                    snapshot_surf = screen.copy()
                    current_scene = "OBBY_LOSE"
                    pygame.time.set_timer(OBBY_SPAWN_EVENT, 0)

                if pygame.sprite.spritecollide(obby_player, obby_doors, False, pygame.sprite.collide_mask):
                    current_scene = "ENDING_SCENE"
                    pygame.time.set_timer(OBBY_SPAWN_EVENT, 0)

        # --- RENDER ENGINE RUNNER ---
        if state == "LOGIN":
            draw_text_centered("The Character Portal", font_title, COLOR_PRIMARY, mid_x, 130)
            draw_text_centered("Enter your username to continue:", font_body, COLOR_SECONDARY, mid_x, 210)
            pygame.draw.rect(screen, COLOR_CARD, (mid_x - 200, 260, 400, 60), border_radius=12)
            pygame.draw.rect(screen, COLOR_ACCENT, (mid_x - 200, 260, 400, 60), width=2, border_radius=12)
            if username_str == "":
                draw_text_centered("Type username...", font_body, COLOR_SECONDARY, mid_x, 278)
            else:
                draw_text_centered(username_str, font_header, COLOR_PRIMARY, mid_x, 276)
            is_btn_hover = (mid_x - 150) <= mx <= (mid_x + 150) and 380 <= my <= 445
            pygame.draw.rect(screen, COLOR_HOVER if is_btn_hover else COLOR_ACCENT, (mid_x - 150, 380, 300, 65), border_radius=12)
            draw_text_centered("Start Game", font_header, WHITE if not is_btn_hover else COLOR_PRIMARY, mid_x, 398)

            draw_text_centered(f"♫ Playing: {track_list[active_track_idx]['name']}", font_small, COLOR_SECONDARY, mid_x, 560)
            draw_text_centered("[Press 'S' for Settings & Track Selection]", font_small, COLOR_ACCENT, mid_x, 590)

        elif state == "CHAR_SELECT":
            draw_text_centered("Select Your Character", font_title, COLOR_PRIMARY, mid_x, 65)
            for idx, char in enumerate(characters):
                bx = mid_x - 270 + idx * 280
                by = 220
                is_card_hover = bx <= mx <= bx + 260 and by <= my <= by + 270
                is_selected = (selected_char_idx == idx)

                pygame.draw.rect(screen, COLOR_CARD, (bx, by, 260, 270), border_radius=16)
                if is_selected:
                    pygame.draw.rect(screen, char["color"], (bx, by, 260, 270), width=4, border_radius=16)
                elif is_card_hover:
                    pygame.draw.rect(screen, COLOR_ACCENT, (bx, by, 260, 270), width=2, border_radius=16)
                else:
                    pygame.draw.rect(screen, COLOR_SECONDARY, (bx, by, 260, 270), width=1, border_radius=16)

                draw_text_centered(char["name"], font_header, COLOR_PRIMARY, bx + 130, by + 30)
                if char["name"] in sprites_small:
                    screen.blit(sprites_small[char["name"]], (bx + 85, by + 110))

            if selected_char_idx is not None:
                pygame.draw.rect(screen, COLOR_ACCENT, (mid_x - 120, 535, 240, 55), border_radius=10)
                draw_text_centered("Confirm Selection", font_body, WHITE, mid_x, 550)

            draw_text_centered("[Press 'S' for Settings & Track Selection]", font_small, COLOR_SECONDARY, mid_x, 15)

        elif state == "SETTINGS":
            draw_text_centered("Settings Menu", font_title, COLOR_PRIMARY, mid_x, 60)

            draw_text_centered("Adjust Music Volume:", font_header, COLOR_SECONDARY, mid_x, 160)
            volume_levels = ["0%", "25%", "50%", "75%", "100%"]
            for i, text in enumerate(volume_levels):
                btn_x = mid_x - 200 + i * 100
                is_selected = (abs(current_volume - i * 0.25) < 0.05)
                is_hover = (btn_x - 40 <= mx <= btn_x + 40 and 220 <= my <= 270)

                box_color = COLOR_ACCENT if is_selected else (COLOR_HOVER if is_hover else COLOR_CARD)
                text_color = WHITE if is_selected else COLOR_PRIMARY

                pygame.draw.rect(screen, box_color, (btn_x - 40, 220, 80, 50), border_radius=8)
                pygame.draw.rect(screen, COLOR_SECONDARY, (btn_x - 40, 220, 80, 50), width=1, border_radius=8)
                draw_text_centered(text, font_body, text_color, btn_x, 234)

            draw_text_centered("Select Jukebox Soundtrack Track (Scroll using Mouse Wheel / Left-Right Arrows):", font_header, COLOR_SECONDARY, mid_x, 310)
            for visible_idx in range(MAX_VISIBLE_TRACKS):
                actual_idx = scroll_offset + visible_idx
                if actual_idx >= len(track_list):
                    break

                track = track_list[actual_idx]
                card_x = mid_x - 390 + visible_idx * (TRACK_CARD_WIDTH + TRACK_CARD_GAP)
                is_active_song = (active_track_idx == actual_idx)
                is_song_hover = (card_x <= mx <= card_x + TRACK_CARD_WIDTH and 360 <= my <= 430)

                card_bg = COLOR_SUCCESS if is_active_song else (COLOR_HOVER if is_song_hover else COLOR_CARD)
                text_color = WHITE if is_active_song else COLOR_PRIMARY

                pygame.draw.rect(screen, card_bg, (card_x, 360, TRACK_CARD_WIDTH, TRACK_CARD_HEIGHT), border_radius=10)
                pygame.draw.rect(screen, COLOR_SECONDARY, (card_x, 360, TRACK_CARD_WIDTH, TRACK_CARD_HEIGHT), width=1, border_radius=10)

                display_name = track["name"]
                if len(display_name) > 22:
                    display_name = display_name[:19] + "..."

                draw_text_centered(display_name, font_body, text_color, card_x + (TRACK_CARD_WIDTH // 2), 373)
                status_txt = "● Playing Now" if is_active_song else "Click to Select"
                status_color = WHITE if is_active_song else COLOR_SECONDARY
                draw_text_centered(status_txt, font_small, status_color, card_x + (TRACK_CARD_WIDTH // 2), 402)

            draw_text_centered(f"Showing tracks {scroll_offset + 1}-{min(scroll_offset + MAX_VISIBLE_TRACKS, len(track_list))} of {len(track_list)}", font_small, COLOR_SECONDARY, mid_x, 450)

            is_back_hover = mid_x - 100 <= mx <= mid_x + 100 and 520 <= my <= 580
            pygame.draw.rect(screen, COLOR_PRIMARY if is_back_hover else COLOR_SECONDARY, (mid_x - 100, 520, 200, 60), border_radius=10)
            draw_text_centered("Back (ESC)", font_body, WHITE, mid_x, 538)

        elif state == "GAME_START":
            if current_scene == "ROOM":
                screen.blit(bg_home, (0, 0)) if bg_home else screen.fill((45, 55, 72))
            elif current_scene == "HOUSE_OUTSIDE":
                screen.blit(bg_house_outside, (0, 0)) if bg_house_outside else screen.fill((30, 41, 59))
            elif current_scene == "STREET_WALK":
                screen.blit(bg_outside_morning, (0, 0)) if bg_outside_morning else screen.fill((125, 211, 252))
            elif current_scene == "BUS_RIDE":
                screen.blit(bg_inside_bus, (0, 0)) if bg_inside_bus else screen.fill((30, 35, 45))
            elif current_scene == "MRT_APPROACH":
                screen.blit(bg_mrt_station, (0, 0)) if bg_mrt_station else screen.fill((24, 24, 37))
            elif current_scene == "TAXI_RIDE":
                screen.blit(bg_inside_taxi, (0, 0)) if bg_inside_taxi else screen.fill((20, 20, 30))
            elif current_scene == "STREET_EVENING":
                screen.blit(bg_outside_dark, (0, 0)) if bg_outside_dark else screen.fill((15, 23, 42))
            elif current_scene in ["FADE_TO_EVENING", "ENDING_SCENE", "OBBY_WIN"]:
                screen.fill((240, 242, 245)) 

            # --- DRAW ACTIVE SUBWAY OBBY RUNNER ---
            if current_scene == "MRT_RIDE":
                if bg_mrt_obby:
                    screen.blit(bg_mrt_obby, (0, 0))
                else:
                    screen.fill((24, 24, 37))
                    pygame.draw.rect(screen, (51, 65, 85), (0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 70))

                if obby_initialized:
                    screen.blit(obby_player.image, obby_player.rect)
                    obby_all_moving.draw(screen)

                    if obby_instruction_alpha > 0:
                        font_obby_inst = pygame.font.SysFont("Courier New", 32, bold=True)
                        shadow = font_obby_inst.render("PRESS SPACE / UP TO START & JUMP", True, (0, 0, 0))
                        text = font_obby_inst.render("PRESS SPACE / UP TO START & JUMP", True, (255, 255, 50))

                        fade_surface = pygame.Surface((text.get_width() + 4, text.get_height() + 4), pygame.SRCALPHA)
                        fade_surface.blit(shadow, (4, 4))
                        fade_surface.blit(text, (0, 0))
                        fade_surface.set_alpha(obby_instruction_alpha)

                        screen.blit(fade_surface, fade_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))


            if current_scene not in ["FADE_TO_EVENING", "BUS_RIDE", "MRT_RIDE", "TAXI_RIDE", "ENDING_SCENE", "OBBY_LOSE", "TAXI_LOSE", "OBBY_WIN"]:
                chosen = characters[selected_char_idx]
                if outfit_changed:
                    if facing_direction == "RIGHT" and chosen["name"] in sprites_uni_right:
                        screen.blit(sprites_uni_right[chosen["name"]], (char_x, char_y))
                    elif chosen["name"] in sprites_uni_left:
                        screen.blit(sprites_uni_left[chosen["name"]], (char_x, char_y))
                else:
                    if facing_direction == "RIGHT" and chosen["name"] in sprites_home_right:
                        screen.blit(sprites_home_right[chosen["name"]], (char_x, char_y))
                    elif chosen["name"] in sprites_home_left:
                        screen.blit(sprites_home_left[chosen["name"]], (char_x, char_y))

            if current_scene == "FADE_TO_EVENING":
                fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(fade_alpha)
                screen.blit(fade_surface, (0, 0))

                if fade_direction == 1:
                    fade_alpha += 10
                    if fade_alpha >= 255:
                        fade_direction = -1
                        if next_scene_target == "MRT_APPROACH":
                            char_x = 100
                        current_scene = next_scene_target
                else:
                    fade_alpha -= 10
                    if fade_alpha <= 0:
                        fade_alpha = 0

            if current_scene not in ["FADE_TO_EVENING", "ENDING_SCENE", "OBBY_LOSE", "TAXI_LOSE", "OBBY_WIN"]:
                panel = pygame.Surface((910, 50), pygame.SRCALPHA)
                panel.fill((15, 23, 42, 180)) 
                screen.blit(panel, (20, 20))

                if not movement_enabled:
                    display_msg = "🔒 PRESS 'F' TO AWAKEN MOVEMENT MECHANICS"
                elif current_scene == "ROOM":
                    if not near_wardrobe and not outfit_changed:
                        display_msg = f"🎯 OBJECTIVE: Walk right to inspect the Wardrobe, {username_str}! [Press 'S' for Settings]"
                    elif near_wardrobe and not outfit_changed:
                        display_msg = "👕 PRESS 'E' TO CHANGE INTO YOUR UNIFORM"
                    elif outfit_changed and not near_door:
                        display_msg = f"👕 OUTFIT EQUIPPED! Now head left to the front door, {username_str}."
                    elif outfit_changed and near_door:
                        display_msg = "🚪 PRESS 'E' TO EXIT THE HOUSE"
                elif current_scene == "HOUSE_OUTSIDE":
                    display_msg = "🏡 Outside! Continue right to begin your walk down the street... [Press 'S' for Settings]"
                elif current_scene == "STREET_WALK":
                    progress_ratio = time_of_day_ticks / MAX_TIME_TICKS
                    draw_time_widget(screen, SCREEN_WIDTH - 60, 45, 16, progress_ratio)
                    if near_bus_stop:
                        display_msg = "🚌 PRESS 'E' TO BOARD THE BUS"
                    elif near_taxi_stand:
                        display_msg = "🚕 PRESS 'E' TO HAIL A TAXI RIDE"
                    elif near_mrt_entrance:
                        display_msg = "🚇 PRESS 'E' TO APPROACH THE MRT STATION"
                    else:
                        display_msg = "🌅 Walk right to choose a method of transportation layout... [Press 'S' for Settings]"
                elif current_scene == "MRT_APPROACH":
                    if near_train_doors:
                        display_msg = "🚇 OBJECTIVE: PRESS 'E' TO BOARD THE MRT TRAIN"
                    else:
                        display_msg = "🚉 OBJECTIVE: GO TO THE MRT (Walk right toward platform gates)"
                elif current_scene == "BUS_RIDE":
                    progress_ratio = time_of_day_ticks / MAX_TIME_TICKS
                    draw_time_widget(screen, SCREEN_WIDTH - 60, 45, 16, progress_ratio)
                    display_msg = "🚌 Traveling by bus... Looking out towards North Square..."
                elif current_scene == "TAXI_RIDE":
                    progress_ratio = time_of_day_ticks / MAX_TIME_TICKS
                    draw_time_widget(screen, SCREEN_WIDTH - 60, 45, 16, progress_ratio)
                    display_msg = "🚕 Stuck in bumper-to-bumper traffic! The clock is running down fast..."
                elif current_scene == "STREET_EVENING":
                    display_msg = "🌙 It's getting pitch dark... Something feels wrong..."
                elif current_scene == "MRT_RIDE":
                    display_msg = "🚇 MRT delayed! Jump over subway track spikes! (Press SPACE / UP to Jump)"

                draw_text_centered(display_msg, font_body, WHITE, mid_x - 30 if current_scene in ["STREET_WALK", "BUS_RIDE", "TAXI_RIDE"] else mid_x, 32)

            if current_scene == "OBBY_LOSE":
                if snapshot_surf:
                    screen.blit(snapshot_surf, (0, 0))
                dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                dim_surface.fill((0, 0, 0))
                dim_surface.set_alpha(190)
                screen.blit(dim_surface, (0, 0))

                font_large = pygame.font.SysFont("Courier New", 48, bold=True)
                font_small = pygame.font.SysFont("Courier New", 26, bold=True)

                draw_text_centered("GAME OVER", font_large, COLOR_RED, mid_x, SCREEN_HEIGHT // 2 - 60)
                draw_text_centered("You did not arrive in time for the exam!", font_small, WHITE, mid_x, SCREEN_HEIGHT // 2 + 10)
                draw_text_centered("[No retries allowed. Please close the window to exit]", font_body, COLOR_SECONDARY, mid_x, SCREEN_HEIGHT // 2 + 70)

            elif current_scene == "TAXI_LOSE":
                if snapshot_surf:
                    screen.blit(snapshot_surf, (0, 0))
                dim_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                dim_surface.fill((0, 0, 0))
                dim_surface.set_alpha(190)
                screen.blit(dim_surface, (0, 0))

                font_large = pygame.font.SysFont("Courier New", 48, bold=True)
                font_small = pygame.font.SysFont("Courier New", 26, bold=True)

                draw_text_centered("YOU FAILED: TRAFFIC JAM", font_large, COLOR_RED, mid_x, SCREEN_HEIGHT // 2 - 60)
                draw_text_centered("The highway completely blocked up. You missed the paper!", font_small, WHITE, mid_x, SCREEN_HEIGHT // 2 + 10)
                draw_text_centered("[No retries allowed. Please close the window to exit]", font_body, COLOR_SECONDARY, mid_x, SCREEN_HEIGHT // 2 + 70)

            # --- INTERACTIVE MATH TEST PAPER WIN STATE ---
            elif current_scene == "OBBY_WIN":
                pygame.draw.rect(screen, COLOR_CARD, (mid_x - 280, 40, 560, 560), border_radius=12)
                pygame.draw.rect(screen, COLOR_PRIMARY, (mid_x - 280, 40, 560, 560), width=2, border_radius=12)

                if not math_exam_submitted:
                    draw_text_centered("MATH TEST (EASY PAPER)", font_title, COLOR_ACCENT, mid_x, 60)
                    draw_text_centered(f"Candidate: {username_str} | Click box or TAB to change question", font_small, COLOR_SECONDARY, mid_x, 115)
                    pygame.draw.line(screen, COLOR_SECONDARY, (mid_x - 240, 135), (mid_x + 240, 135), 2)

                    for i, q_item in enumerate(math_questions):
                        y_pos = 180 + i * 65
                        screen.blit(font_header.render(q_item["q"], True, COLOR_PRIMARY), (mid_x - 230, y_pos))

                        box_rect = pygame.Rect(mid_x + 80, y_pos - 4, 120, 40)
                        is_active = (active_math_field == i)

                        pygame.draw.rect(screen, WHITE if not is_active else COLOR_HOVER, box_rect, border_radius=6)
                        pygame.draw.rect(screen, COLOR_ACCENT if is_active else COLOR_SECONDARY, box_rect, width=2 if is_active else 1, border_radius=6)

                        val_text = font_header.render(math_answers_input[i], True, COLOR_PRIMARY)
                        screen.blit(val_text, (box_rect.x + 15, box_rect.y + 3))

                    submit_btn = pygame.Rect(mid_x - 100, 500, 200, 50)
                    is_sub_hover = submit_btn.collidepoint((mx, my))
                    pygame.draw.rect(screen, COLOR_SUCCESS if is_sub_hover else COLOR_ACCENT, submit_btn, border_radius=8)
                    draw_text_centered("SUBMIT PAPER", font_header, WHITE, mid_x, 512)

                else:
                    draw_text_centered("EXAM REPORT CARD", font_title, COLOR_PRIMARY, mid_x, 100)
                    pygame.draw.line(screen, COLOR_SECONDARY, (mid_x - 240, 160), (mid_x + 240, 160), 2)

                    score_str = f"Your Score: {math_exam_score} / {len(math_questions)}"
                    draw_text_centered(score_str, font_title, COLOR_PRIMARY, mid_x, 220)

                    if math_exam_passed:
                        draw_text_centered("PASSED IN FLYING COLOURS!", font_title, COLOR_SUCCESS, mid_x, 300)
                        draw_text_centered("You arrived just in time and conquered the test!", font_body, COLOR_SECONDARY, mid_x, 360)
                    else:
                        draw_text_centered("FAILED THE EXAM", font_title, COLOR_RED, mid_x, 300)
                        draw_text_centered("You made it to the room but didn't solve enough equations.", font_body, COLOR_SECONDARY, mid_x, 360)

                    draw_text_centered("[GAME OVER - Close the window to exit layout]", font_body, COLOR_PRIMARY, mid_x, 500)

            elif current_scene == "ENDING_SCENE":
                screen.fill((240, 242, 245))
                draw_text_centered("PASSED WITH FLYING COLOURS!", font_title, COLOR_SUCCESS, mid_x, SCREEN_HEIGHT // 2 - 80)
                draw_text_centered(f"Congratulations, {username_str}!", font_header, COLOR_PRIMARY, mid_x, SCREEN_HEIGHT // 2 - 10)
                draw_text_centered("You arrived on time and aced your exam.", font_body, COLOR_SECONDARY, mid_x, SCREEN_HEIGHT // 2 + 40)
                draw_text_centered("[GAME COMPLETE - Close the window to exit]", font_body, COLOR_PRIMARY, mid_x, SCREEN_HEIGHT // 2 + 110)

        pygame.display.flip()
        clock.tick(30)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
