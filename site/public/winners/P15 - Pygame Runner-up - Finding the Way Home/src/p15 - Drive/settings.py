import os

# Base directory — the folder where settings.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Asset paths ---
IMAGES_DIR = os.path.join(BASE_DIR, "assets", "images")
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")
FONTS_DIR  = os.path.join(BASE_DIR, "assets", "fonts")
DATA_DIR   = os.path.join(BASE_DIR, "data", "scenes")

# --- Resolution ---
# Render internally at 480x270, display at 3x = 1440x810
RENDER_W = 480
RENDER_H = 270

TILE_SIZE = 3                        # upscale factor
SCREEN_W  = RENDER_W * TILE_SIZE     # 1440
SCREEN_H  = RENDER_H * TILE_SIZE     # 810

FPS   = 60
TITLE = "Finding Home"

# --- Audio channels ---
CH_MUSIC   = 0
CH_AMBIENT = 1
CH_SFX     = 2

# --- Colours ---
BLACK      = (0,   0,   0)
WARM_WHITE = (245, 235, 220)
WARM_GOLD  = (230, 180,  80)

# --- Glitch intensity per chapter ---
GLITCH_LEVELS = {
    "prologue": 0.0,
    "ch1":      0.05,
    "ch2":      0.35,
    "ch3":      0.60,
    "ch4":      0.85,
}