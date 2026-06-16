# systems/transition.py
import pygame
from settings import RENDER_W, RENDER_H, BLACK

class Transition:
    def __init__(self):
        self._overlay = pygame.Surface((RENDER_W, RENDER_H))
        self._overlay.fill(BLACK)
        self.alpha     = 255       # start fully black (fade IN)
        self.target    = 0
        self.speed     = 120       # alpha units per second
        self.callback  = None      # called when fade-out finishes

    def fade_in(self, speed=120):
        """Screen fades from black to clear."""
        self.alpha  = 255
        self.target = 0
        self.speed  = speed

    def fade_out(self, speed=120, callback=None):
        """Screen fades to black, then calls callback."""
        self.alpha    = 0
        self.target   = 255
        self.speed    = speed
        self.callback = callback

    def update(self, dt):
        if self.alpha != self.target:
            step = self.speed * dt
            if self.alpha < self.target:
                self.alpha = min(self.target, self.alpha + step)
            else:
                self.alpha = max(self.target, self.alpha - step)

            if self.alpha == self.target and self.callback:
                self.callback()
                self.callback = None

    def draw(self, surface):
        if self.alpha > 0:
            self._overlay.set_alpha(int(self.alpha))
            surface.blit(self._overlay, (0, 0))