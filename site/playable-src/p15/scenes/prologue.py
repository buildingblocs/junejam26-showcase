import pygame
import math
from scenes.base_scene import BaseScene
from settings import RENDER_W, RENDER_H, BLACK, WARM_WHITE

# All the text that appears line by line in scene 1
SCENE1_LINES = [
    "Everyday ends the same way.",
    "We leave school.",
    "We take the train.",
    "We walk the same path.",
    "And we go somewhere we know well.",
    "Home.",
]

# The unsettling text in scene 2
SCENE2_LINES = [
    "But what if the path",
    "doesn't stay the same forever?",
    "",
    "What if home becomes...",
    "unfamiliar?",
]

class PrologueScene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)

        self.scene_images = {
            "Everyday ends the same way.": self.assets.get_image("scenes/prologue_everyday"),
            "We take the train.":          self.assets.get_image("scenes/prologue_train"),
            "We walk the same path.":      self.assets.get_image("scenes/prologue_walking"),
            "Home.":                       self.assets.get_image("scenes/prologue_home"),
        }
        self.current_bg = None

        # Fonts
        self.font_main = self.assets.get_font(8)
        self.font_small = self.assets.get_font(6)

        # Background placeholders — coloured rectangles for now
        # Replace these with real images later via asset_manager
        self.bg_colors = [
            (40,  35,  60),   # evening purple — school
            (50,  40,  55),   # dusk — mrt crowd
            (35,  30,  50),   # darker — walking home
            (20,  18,  35),   # near night — evening sky
        ]

        # --- Scene state machine ---
        # "scene1" -> lines fading in one by one over background
        # "scene2" -> fade to black, unsettling text, heartbeat
        # "done"   -> transition to chapter 1
        self.phase        = "scene1"
        self.timer        = 0.0
        self.phase_timer  = 0.0   # timer that resets each phase

        # Scene 1 state
        self.current_line  = 0        # which line we're showing
        self.line_alpha    = 0.0      # alpha of current line fading in
        self.lines_shown   = []       # list of (text, alpha) already displayed
        self.bg_index      = 0        # which background colour we're on
        self.bg_alpha      = 255      # for crossfading backgrounds

        # Scene 2 state
        self.s2_line       = 0
        self.s2_alpha      = 0.0
        self.s2_lines_shown = []
        self.heartbeat_timer = 0.0
        self.screen_shake   = 0.0    # shake intensity for heartbeat moment

        # Overlay for fades
        self.overlay       = pygame.Surface((RENDER_W, RENDER_H))
        self.overlay.fill(BLACK)
        self.overlay_alpha = 255     # start black, fade in
        self.fading_out    = False

    # ------------------------------------------------------------------
    def handle_event(self, event):
        # Allow skipping with spacebar
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._go_to_chapter1()

    # ------------------------------------------------------------------
    def update(self, dt):
        self.timer      += dt
        self.phase_timer += dt

        # Fade in from black at the very start
        if self.overlay_alpha > 0 and not self.fading_out:
            self.overlay_alpha = max(0, self.overlay_alpha - 180 * dt)

        if self.phase == "scene1":
            self._update_scene1(dt)
        elif self.phase == "scene2":
            self._update_scene2(dt)

        # Fade out overlay when transitioning
        if self.fading_out:
            self.overlay_alpha = min(255, self.overlay_alpha + 150 * dt)
            if self.overlay_alpha >= 255:
                self.manager.replace_scene("ch1")

    # ------------------------------------------------------------------
    def _update_scene1(self, dt):
        # Fade in current line
        if self.current_line < len(SCENE1_LINES):
            self.line_alpha = min(255, self.line_alpha + 90 * dt)

            # Once fully visible, hold for 2s then move to next line
            if self.line_alpha >= 255:
                self.phase_timer += dt
                if self.phase_timer > 2.0:
                    # Save this line as shown and advance
                    self.lines_shown.append(SCENE1_LINES[self.current_line])
                    self.current_line += 1
                    self.line_alpha    = 0
                    self.phase_timer   = 0.0

                    # Change background every 2 lines
                    self.bg_index = min(
                        len(self.bg_colors) - 1,
                        self.current_line // 2
                    )
        else:
            # All lines shown — pause then move to scene 2
            if self.phase_timer > 2.0:
                self.phase       = "scene2"
                self.phase_timer = 0.0
                self.overlay_alpha = 0
                # Trigger fade to black before scene 2
                self._fade_to_black_then(self._start_scene2)

    def _start_scene2(self):
        self.phase       = "scene2_text"
        self.phase_timer = 0.0

    # ------------------------------------------------------------------
    def _update_scene2(self, dt):
        # Fade in scene 2 lines one by one
        if self.s2_line < len(SCENE2_LINES):
            if SCENE2_LINES[self.s2_line] == "":
                # Empty line = pause
                self.s2_lines_shown.append("")
                self.s2_line     += 1
                self.phase_timer  = 0.0
                return

            self.s2_alpha = min(255, self.s2_alpha + 70 * dt)

            if self.s2_alpha >= 255:
                self.phase_timer += dt
                if self.phase_timer > 2.5:
                    self.s2_lines_shown.append(SCENE2_LINES[self.s2_line])
                    self.s2_line     += 1
                    self.s2_alpha     = 0
                    self.phase_timer  = 0.0

                    # Heartbeat moment when "unfamiliar?" appears
                    if self.s2_line == len(SCENE2_LINES):
                        self.screen_shake = 8.0
        else:
            # All scene 2 lines shown — pause then go to chapter 1
            self.phase_timer += dt
            if self.phase_timer > 3.0:
                self._go_to_chapter1()

        # Decay screen shake
        self.screen_shake = max(0, self.screen_shake - 12 * dt)

    # ------------------------------------------------------------------
    def _fade_to_black_then(self, callback):
        """Quick helper — just sets overlay to fade out."""
        self.fading_out   = False
        self.overlay_alpha = 0
        self._pending_cb   = callback
        self._fading_to_black = True

    def _go_to_chapter1(self):
        self.fading_out = True

    # ------------------------------------------------------------------
    def draw(self, surface):
        if self.phase == "scene1":
            self._draw_scene1(surface)
        elif self.phase in ("scene2", "scene2_text"):
            self._draw_scene2(surface)

        # Draw fade overlay on top of everything
        if self.overlay_alpha > 0:
            self.overlay.set_alpha(int(self.overlay_alpha))
            surface.blit(self.overlay, (0, 0))

    def _draw_scene1(self, surface):
        # Show scene image if one matches the current or last shown line
        shown_texts = self.lines_shown + (
            [SCENE1_LINES[self.current_line]] if self.current_line < len(SCENE1_LINES) else []
        )
        bg_img = None
        for text in reversed(shown_texts):
            if text in self.scene_images:
                bg_img = self.scene_images[text]
                break

        if bg_img:
            bg = pygame.transform.scale(bg_img, (RENDER_W, RENDER_H))
            surface.blit(bg, (0, 0))
        else:
            surface.fill(self.bg_colors[self.bg_index])

        # Draw a simple pixel art horizon line
        pygame.draw.line(surface, (60, 50, 80), (0, 120), (RENDER_W, 120), 1)

        # Simple silhouette shapes — people walking
        self._draw_walkers(surface)

        # Scanlines for atmosphere
        self._draw_scanlines(surface)

        # Previously shown lines (fully visible, stacked)
        y_start = 20
        for i, line in enumerate(self.lines_shown):
            if line:
                txt = self.font_main.render(line, False, WARM_WHITE)
                surface.blit(txt, (RENDER_W//2 - txt.get_width()//2, y_start + i * 14))

        # Current fading-in line
        if self.current_line < len(SCENE1_LINES):
            line_text = SCENE1_LINES[self.current_line]
            # Last line "Home." gets special treatment — bigger, gold
            if line_text == "Home.":
                txt = self.assets.get_font(12).render(line_text, False, (255, 200, 100))
            else:
                txt = self.font_main.render(line_text, False, WARM_WHITE)
            txt.set_alpha(int(self.line_alpha))
            surface.blit(txt, (RENDER_W//2 - txt.get_width()//2,
                               y_start + len(self.lines_shown) * 14))

        # Skip hint
        skip = self.font_small.render("SPACE to skip", False, (80, 75, 90))
        surface.blit(skip, (RENDER_W - skip.get_width() - 4, RENDER_H - 10))

    def _draw_scene2(self, surface):
        # Pure black background
        surface.fill((5, 4, 8))

        # Screen shake offset
        shake_x = int(math.sin(self.timer * 40) * self.screen_shake)
        shake_y = int(math.cos(self.timer * 35) * self.screen_shake * 0.5)

        # Previously shown lines
        y_start = 50
        for i, line in enumerate(self.s2_lines_shown):
            if line:
                txt = self.font_main.render(line, False, (180, 170, 190))
                surface.blit(txt, (RENDER_W//2 - txt.get_width()//2 + shake_x,
                                   y_start + i * 16 + shake_y))

        # Current fading line
        if self.s2_line < len(SCENE2_LINES) and SCENE2_LINES[self.s2_line]:
            line_text = SCENE2_LINES[self.s2_line]
            # "unfamiliar?" gets a red tint
            color = (220, 100, 100) if "unfamiliar" in line_text else (180, 170, 190)
            txt = self.font_main.render(line_text, False, color)
            txt.set_alpha(int(self.s2_alpha))
            surface.blit(txt, (RENDER_W//2 - txt.get_width()//2 + shake_x,
                               y_start + len(self.s2_lines_shown) * 16 + shake_y))

    def _draw_walkers(self, surface):
        """Simple 2-pixel silhouettes walking across the bottom."""
        positions = [40, 90, 140, 200, 260, 300]
        for i, x in enumerate(positions):
            # Offset each walker slightly with timer for movement feel
            offset = int(math.sin(self.timer * 1.5 + i) * 1)
            pygame.draw.rect(surface, (20, 15, 30), (x + offset, 108, 4, 10))  # body
            pygame.draw.rect(surface, (20, 15, 30), (x + offset + 1, 104, 3, 4))  # head

    def _draw_scanlines(self, surface):
        scanline = pygame.Surface((RENDER_W, 1))
        scanline.fill((0, 0, 0))
        scanline.set_alpha(35)
        for y in range(0, RENDER_H, 2):
            surface.blit(scanline, (0, y))