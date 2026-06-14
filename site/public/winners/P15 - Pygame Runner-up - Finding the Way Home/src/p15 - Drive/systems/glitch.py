# systems/glitch.py
import pygame
import random

class GlitchSystem:
    def apply(self, surface, intensity=0.0):
        """
        intensity: 0.0 = clean, 1.0 = fully corrupted
        Call this on any surface before drawing it.
        """
        if intensity <= 0:
            return surface

        result = surface.copy()
        w, h = result.get_size()
        num_tears = int(intensity * 12)

        for _ in range(num_tears):
            y      = random.randint(0, h - 4)
            height = random.randint(1, max(1, int(intensity * 6)))
            offset = random.randint(-int(intensity * 20), int(intensity * 20))

            strip = surface.subsurface(pygame.Rect(0, y, w, height)).copy()
            result.blit(strip, (offset, y))

        return result

    def corrupt_text(self, text, intensity=0.0):
        """
        Replaces characters with glitch chars based on intensity.
        Use for the memory bubble text corruption effect.
        """
        if intensity <= 0:
            return text

        glitch_chars = "█▓▒░?#@$"
        result = []
        for char in text:
            if char != " " and random.random() < intensity * 0.4:
                result.append(random.choice(glitch_chars))
            else:
                result.append(char)
        return "".join(result)