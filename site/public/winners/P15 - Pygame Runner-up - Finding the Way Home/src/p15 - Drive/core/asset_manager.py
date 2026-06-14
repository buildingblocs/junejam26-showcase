# core/asset_manager.py
import pygame
import os
from settings import IMAGES_DIR, SOUNDS_DIR, FONTS_DIR

class AssetManager:
    def __init__(self):
        self._images = {}
        self._sounds = {}
        self._fonts  = {}

    def get_image(self, path):
        """path e.g. 'backgrounds/bedroom' """
        if path not in self._images:
            full = os.path.join(IMAGES_DIR, path + ".png")
            print(f"Looking for image at: {os.path.abspath(full)}")  # DEBUG
            print(f"Exists: {os.path.exists(full)}")                  # DEBUG
            if os.path.exists(full):
                self._images[path] = pygame.image.load(full).convert_alpha()
            else:
                surf = pygame.Surface((320, 180))
                surf.fill((30, 20, 40))
                self._images[path] = surf
        return self._images[path]

    def get_sound(self, path):
        """path e.g. 'sfx/heartbeat' """
        if path not in self._sounds:
            full = os.path.join(SOUNDS_DIR, path + ".ogg")
            if os.path.exists(full):
                self._sounds[path] = pygame.mixer.Sound(full)
            else:
                self._sounds[path] = None
        return self._sounds[path]

    def get_font(self, size):
        if size not in self._fonts:
            import os
            path = os.path.join(FONTS_DIR, "pixel_font.ttf")
            print(f"Looking for font at: {os.path.abspath(path)}")  # add this
            if os.path.exists(path):
                print("Font found!")                                  # add this
                self._fonts[size] = pygame.font.Font(path, size)
            else:
                print("Font NOT found, using fallback")               # add this
                self._fonts[size] = pygame.font.SysFont("monospace", size)
        return self._fonts[size]