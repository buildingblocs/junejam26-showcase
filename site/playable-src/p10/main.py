"""
Traffic Crosser
BuildingBloCS June Jam (PyGame) 2026

Author: Eng Kai Yang & Lau Zi Yu
School: NYP (Applied AI & Analytics)
Team: P10
"""

import asyncio
import pygame
import random
import os
import sys
from dataclasses import dataclass
from enum import Enum

# Constant variables
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GRID_SIZE = 50
FPS = 60

# Colors
COLOR_GRASS = (34, 139, 34)
COLOR_ROAD = (45, 45, 45)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GOLD = (255, 215, 0)
COLOR_XP = (100, 200, 255)
COLOR_ROAD_LINE = (180, 180, 180)

# States & configurations
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

class LightState(Enum):
    GREEN = 1
    RED = 2

@dataclass
class VehicleType:
    name: str
    width: int
    height: int
    color: tuple
    speed_mult: float
    image_path: str

VEHICLE_CONFIGS = [
    VehicleType("Car", 75, 35, (200, 30, 30), 1.0, "assets/car.png"),
    VehicleType("Van", 100, 40, (50, 100, 200), 0.7, "assets/van.png"),
    VehicleType("Truck", 150, 45, (120, 120, 120), 0.5, "assets/truck.png"),
]

class AssetManager: # helper function for loading assets
    def __init__(self):
        self.images = {}
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.load_assets()

    def load_assets(self):
        for config in VEHICLE_CONFIGS:
            path = os.path.join(self.script_dir, config.image_path)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (config.width, config.height))
                self.images[config.name] = img
            else:
                surf = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
                pygame.draw.rect(surf, config.color, (0, 0, config.width, config.height), border_radius=10)
                pygame.draw.rect(surf, (180, 240, 255), (config.width-25, 5, 20, config.height-10), border_radius=4)
                self.images[config.name] = surf

    def get_vehicle_image(self, name, direction):
        img = self.images[name]
        return pygame.transform.flip(img, True, False) if direction == -1 else img

class TrafficLight: # helper function for traffic lights
    def __init__(self):
        self.state = LightState.GREEN
        self.timer = 0
        self.next_change = random.randint(150, 350)
        self.red_alpha = 0
        self.green_alpha = 255

    def update(self):
        self.timer += 1
        if self.timer >= self.next_change:
            self.timer = 0
            if self.state == LightState.GREEN:
                self.state = LightState.RED
                self.next_change = random.randint(300, 600)
            else:
                self.state = LightState.GREEN
                self.next_change = random.randint(25, 100)

        target_red = 255 if self.state == LightState.RED else 0
        target_green = 255 if self.state == LightState.GREEN else 0
        self.red_alpha += (target_red - self.red_alpha) * 0.1
        self.green_alpha += (target_green - self.green_alpha) * 0.1

    def draw(self, surface, x, y):
        pygame.draw.rect(surface, (30, 30, 30), (x, y - 45, 26, 46), border_radius=5)
        rs = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(rs, (255, 0, 0, int(self.red_alpha)), (8, 8), 8)
        surface.blit(rs, (x + 5, y - 40))
        gs = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(gs, (0, 255, 0, int(self.green_alpha)), (8, 8), 8)
        surface.blit(gs, (x + 5, y - 20))

class Player: # helper function for player
    def __init__(self):
        self.grid_x = SCREEN_WIDTH // 2
        self.grid_y = SCREEN_HEIGHT - GRID_SIZE
        self.curr_x = float(self.grid_x)
        self.curr_y = float(self.grid_y)
        self.speed = 0.22
        self.size = 38

    def move(self, dx, dy):
        self.grid_x += dx
        self.grid_y += dy
        self.grid_x = max(0, min(self.grid_x, SCREEN_WIDTH - GRID_SIZE))

    def update(self):
        self.curr_x += (self.grid_x - self.curr_x) * self.speed
        self.curr_y += (self.grid_y - self.curr_y) * self.speed

    def get_rect(self):
        return pygame.Rect(self.curr_x + 10, self.curr_y + 10, self.size - 20, self.size - 20)

    def draw(self, surface, camera_y):
        dy = self.curr_y - camera_y
        pygame.draw.rect(surface, (255, 220, 0), (self.curr_x+4, dy+4, self.size, self.size), border_radius=10)
        pygame.draw.circle(surface, COLOR_BLACK, (int(self.curr_x + 14), int(dy + 15)), 3)
        pygame.draw.circle(surface, COLOR_BLACK, (int(self.curr_x + 30), int(dy + 15)), 3)

class Vehicle: # helper function for vehicles
    def __init__(self, x, y, config, direction, speed, image):
        self.x = x
        self.y = y
        self.config = config
        self.direction = direction
        self.speed = speed * config.speed_mult
        self.image = image

    def update(self):
        self.x += self.speed * self.direction

    def draw(self, surface, camera_y):
        dy = self.y - camera_y + (GRID_SIZE - self.config.height) // 2
        surface.blit(self.image, (self.x, dy))

class Lane: # helper functions for lanes
    def __init__(self, y, l_type, has_light=False):
        self.y = y
        self.type = l_type
        self.vehicles = []
        self.direction = random.choice([-1, 1])
        self.base_speed = random.uniform(3.5, 4.8)
        self.spawn_timer = 0
        self.traffic_light = TrafficLight() if has_light else None

    def update(self, linked_light, assets, level):
        if self.traffic_light: self.traffic_light.update()
        for v in self.vehicles: v.update()

        if self.type == "road":
            is_red = linked_light and linked_light.state == LightState.RED
            self.spawn_timer += 1
            if not is_red: self.spawn_timer = 0

            spawn_threshold = max(25, 80 - (level * 4))
            if self.spawn_timer > spawn_threshold and is_red:
                config = random.choice(VEHICLE_CONFIGS)
                start_x = -250 if self.direction == 1 else SCREEN_WIDTH + 250
                can_spawn = True
                for v in self.vehicles:
                    if self.direction == 1 and v.x < 180: can_spawn = False
                    if self.direction == -1 and v.x > SCREEN_WIDTH - 180: can_spawn = False
                
                if can_spawn:
                    speed_mult = min(2.0, 1.0 + (level - 1) * 0.12)
                    img = assets.get_vehicle_image(config.name, self.direction)
                    self.vehicles.append(Vehicle(start_x, self.y, config, self.direction, self.base_speed * speed_mult, img))
                    self.spawn_timer = 0
        self.vehicles = [v for v in self.vehicles if -500 < v.x < SCREEN_WIDTH + 500]

    def draw(self, surface, camera_y, road_below=False):
        dy = self.y - camera_y
        color = COLOR_ROAD if self.type == "road" else COLOR_GRASS
        pygame.draw.rect(surface, color, (0, dy, SCREEN_WIDTH, GRID_SIZE))
        if self.type == "road" and road_below:
            for x in range(0, SCREEN_WIDTH, 50):
                pygame.draw.rect(surface, COLOR_ROAD_LINE, (x + 15, dy + GRID_SIZE - 2, 25, 4))
        if self.traffic_light: self.traffic_light.draw(surface, 15, dy)
        for v in self.vehicles: v.draw(surface, camera_y)

class Game: # main game
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Traffic Crosser")
        self.clock = pygame.time.Clock()
        self.font_main = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_ui = pygame.font.SysFont("Arial", 22, bold=True)
        
        self.assets = AssetManager()
        self.highscore = 0
        self.volume = 0.5
        self.volume_input = "50"
        self.first_type_done = False 
        self.state = GameState.MENU
        
        self.crash_sound = None
        self.load_audio()
        self.reset_game_logic()
        
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 128)) # dark overlay for menus

    def load_audio(self):
        sd = os.path.dirname(os.path.abspath(__file__))
        m_path = os.path.join(sd, "assets/music.ogg")
        c_path = os.path.join(sd, "assets/crash.ogg")
        if os.path.exists(m_path):
            pygame.mixer.music.load(m_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1)
        if os.path.exists(c_path):
            self.crash_sound = pygame.mixer.Sound(c_path)
            self.crash_sound.set_volume(self.volume)

    def set_state(self, new_state):
        if new_state == GameState.GAME_OVER:
            pygame.mixer.music.stop()
            if self.crash_sound:
                self.crash_sound.play()
        
        elif self.state == GameState.GAME_OVER and new_state in [GameState.MENU, GameState.PLAYING]:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)

        self.state = new_state

    def set_volume_from_input(self):
        if not self.volume_input:
            temp_vol = 0
        else:
            try: temp_vol = int(self.volume_input)
            except: temp_vol = 0
        
        self.volume = max(0.0, min(1.0, temp_vol / 100))
        pygame.mixer.music.set_volume(self.volume)
        if self.crash_sound: self.crash_sound.set_volume(self.volume)

    def reset_game_logic(self):
        self.player = Player()
        self.lanes = []
        self.camera_y = 0 
        self.score = 0
        self.level = 1
        self.xp_progress = 0
        self.xp_needed = 10
        self.first_type_done = False
        
        last_type = "grass"
        for i in range(-25, 25):
            y = i * GRID_SIZE
            curr_type = "grass" if i > 12 or random.random() > 0.75 else "road"
            has_light = (curr_type == "grass" and last_type == "road")
            self.lanes.append(Lane(y, curr_type, has_light))
            last_type = curr_type

    def update_xp(self, new_score):
        if new_score > self.score:
            diff = new_score - self.score
            self.score = new_score
            self.xp_progress += diff
            while self.xp_progress >= self.xp_needed:
                self.xp_progress -= self.xp_needed
                self.level += 1
                self.xp_needed += 5

    def common_update(self): # update the game only if its not paused (game is being played)
        if self.state == GameState.PAUSED:
            return

        for i, lane in enumerate(self.lanes):
            light = None
            if lane.type == "road":
                for j in range(i+1, len(self.lanes)):
                    if self.lanes[j].type == "grass":
                        light = self.lanes[j].traffic_light; break
            lane.update(light, self.assets, self.level)

        lowest_y = min(l.y for l in self.lanes)
        if self.camera_y < lowest_y + 600:
            new_y = lowest_y - GRID_SIZE
            new_type = "grass" if random.random() > 0.8 else "road"
            self.lanes.insert(0, Lane(new_y, new_type, (new_type == "grass" and self.lanes[0].type == "road")))

    def draw_world(self):
        self.screen.fill(COLOR_GRASS)
        for i, lane in enumerate(self.lanes):
            if self.camera_y - 150 < lane.y < self.camera_y + SCREEN_HEIGHT + 150:
                road_below = i + 1 < len(self.lanes) and self.lanes[i+1].type == "road"
                lane.draw(self.screen, self.camera_y, road_below)

    async def run(self):
        while True:
            self.common_update()
            if self.state == GameState.MENU:
                self.menu_loop()
            elif self.state == GameState.PLAYING:
                self.game_loop()
            elif self.state == GameState.PAUSED:
                self.pause_loop()
            elif self.state == GameState.GAME_OVER:
                self.game_over_loop()
            # Yield to the browser event loop once per frame (required by pygbag).
            await asyncio.sleep(0)

    def handle_volume_input(self, event): # helper function to handle volume in main and pause menu
        if event.key == pygame.K_RIGHT:
            cur = int(self.volume_input) if self.volume_input else 0
            self.volume_input = str(min(100, cur + 5))
            self.set_volume_from_input()
        elif event.key == pygame.K_LEFT:
            cur = int(self.volume_input) if self.volume_input else 0
            self.volume_input = str(max(0, cur - 5))
            self.set_volume_from_input()
        elif event.key == pygame.K_BACKSPACE:
            self.volume_input = self.volume_input[:-1]
            self.set_volume_from_input()
        elif event.unicode.isdigit():
            if not self.first_type_done:
                self.volume_input = ""
                self.first_type_done = True
            if len(self.volume_input) < 3:
                new_val = self.volume_input + event.unicode
                if int(new_val) <= 100:
                    self.volume_input = new_val
                    self.set_volume_from_input()

    def menu_loop(self):
        self.camera_y -= 0.5 
        self.draw_world()
        self.screen.blit(self.overlay, (0, 0)) 

        title = self.font_main.render("TRAFFIC CROSSER", True, COLOR_WHITE)
        start_txt = self.font_ui.render("Press SPACE to Start", True, COLOR_GOLD)
        display_vol = self.volume_input if self.volume_input else "0"
        vol_txt = self.font_ui.render(f"Volume: [{display_vol}]% (Type or Arrows)", True, COLOR_WHITE)
        high_txt = self.font_ui.render(f"Highscore: {self.highscore}", True, COLOR_XP)

        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
        self.screen.blit(high_txt, (SCREEN_WIDTH//2 - high_txt.get_width()//2, 280))
        self.screen.blit(start_txt, (SCREEN_WIDTH//2 - start_txt.get_width()//2, 450))
        self.screen.blit(vol_txt, (SCREEN_WIDTH//2 - vol_txt.get_width()//2, 500))

        pygame.display.flip()
        self.clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.set_state(GameState.PLAYING)
                else:
                    self.handle_volume_input(event)

    def pause_loop(self): # draw current game state first
        self.draw_world()
        self.player.draw(self.screen, self.camera_y)
        self.screen.blit(self.overlay, (0, 0))

        title = self.font_main.render("PAUSED", True, COLOR_WHITE)
        resume_txt = self.font_ui.render("Press SPACE or ESC to Resume", True, COLOR_GOLD)
        display_vol = self.volume_input if self.volume_input else "0"
        vol_txt = self.font_ui.render(f"Volume: [{display_vol}]% (Type or Arrows)", True, COLOR_WHITE)

        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 250))
        self.screen.blit(resume_txt, (SCREEN_WIDTH//2 - resume_txt.get_width()//2, 350))
        self.screen.blit(vol_txt, (SCREEN_WIDTH//2 - vol_txt.get_width()//2, 420))

        pygame.display.flip()
        self.clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    self.state = GameState.PLAYING
                else:
                    # pause menu volume handler
                    self.handle_volume_input(event)

    def game_loop(self):
        self.player.update()
        self.camera_y += (self.player.curr_y - 600 - self.camera_y) * 0.1
        
        new_score = max(self.score, int((SCREEN_HEIGHT - GRID_SIZE - self.player.grid_y) / GRID_SIZE))
        self.update_xp(new_score)
        self.highscore = max(self.highscore, self.score)

        for i, lane in enumerate(self.lanes):
            if self.player.get_rect().colliderect(pygame.Rect(0, lane.y, SCREEN_WIDTH, GRID_SIZE)):
                for v in lane.vehicles:
                    if self.player.get_rect().colliderect(pygame.Rect(v.x+8, v.y+8, v.config.width-16, v.config.height-16)):
                        self.set_state(GameState.GAME_OVER)

        self.draw_world()
        self.player.draw(self.screen, self.camera_y)
        self.screen.blit(self.font_ui.render(f"SCORE: {self.score}", True, COLOR_WHITE), (20, 20))
        self.screen.blit(self.font_ui.render(f"LEVEL: {self.level}", True, (100, 255, 100)), (20, 50))
        self.screen.blit(self.font_ui.render(f"XP: {self.xp_progress} / {self.xp_needed}", True, COLOR_XP), (20, 80))
        self.screen.blit(self.font_ui.render(f"HIGHSCORE: {self.highscore}", True, COLOR_GOLD), (SCREEN_WIDTH - 210, 20))
        
        pygame.display.flip()
        self.clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN: # pause menu
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    self.state = GameState.PAUSED
                    self.first_type_done = True 
                
                # movement
                if event.key in [pygame.K_w, pygame.K_UP]: self.player.move(0, -GRID_SIZE)
                if event.key in [pygame.K_s, pygame.K_DOWN]: self.player.move(0, GRID_SIZE)
                if event.key in [pygame.K_a, pygame.K_LEFT]: self.player.move(-GRID_SIZE, 0)
                if event.key in [pygame.K_d, pygame.K_RIGHT]: self.player.move(GRID_SIZE, 0)

    def game_over_loop(self):
        self.draw_world()
        self.player.draw(self.screen, self.camera_y)
        self.screen.blit(self.overlay, (0, 0))
        
        txt = self.font_main.render("CRASHED!", True, COLOR_WHITE)
        sub = self.font_ui.render("Press SPACE for Menu", True, COLOR_GOLD)
        self.screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        pygame.display.flip()
        self.clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.set_state(GameState.MENU)
                self.reset_game_logic()

async def main():
    await Game().run()


if __name__ == "__main__":
    asyncio.run(main())