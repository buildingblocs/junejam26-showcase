import pygame
import math
import random
from scenes.base_scene import BaseScene
from settings import RENDER_W, RENDER_H, BLACK, WARM_WHITE, WARM_GOLD

# Font size standards:
# 16 = chapter headers
# 12 = panel labels
#  8 = body / narration / bubble text
#  6 = hints, slot numbers

# ---------------------------------------------------------------------------
# Puzzle data
# Each slot has a fixed sequence of corruption stages tied to WHEN other
# bubbles get placed. Stage 0 = clean, shown right after placement.
# The stage a slot shows depends on how many TOTAL correct placements
# have been made AFTER it was placed.
# ---------------------------------------------------------------------------

# The 4 correct answers in order (slot 0 → 3)
CORRECT_ANSWERS = [
    "Grab a basket",
    "Get milk",
    "Pick up medicine",
    "Pay at the counter",
]

# Per-slot corruption stages indexed by how many placements happened AFTER
# this slot was filled.  stages[0] = freshly placed (clean).
SLOT_STAGES = [
    # Slot 0 — "Grab a basket"
    [
        "Grab a basket",           # just placed — clean
        "I think I need a basket", # after slot 1 filled
        "What am I holding?",      # after slot 2 filled  (disappears at slot 3)
        "Huh...",                        # after slot 3 filled — text gone / forgotten
    ],
    # Slot 1 — "Get milk"
    [
        "Get milk",                # just placed — clean
        "Was it milk?",            # after slot 2 filled
        "Something from the shelf...", # after slot 3 filled
    ],
    # Slot 2 — "Pick up medicine"
    [
        "Pick up medicine",        # just placed — clean
        "What was I here for?",    # after slot 3 filled
    ],
    # Slot 3 — "Pay at the counter"
    [
        "Pay at the counter",      # just placed — clean
        "How do I leave?",         # corruption after a moment's delay
    ],
]

DECOY_BUBBLES = [
    "I already came here",
    "I should go home",
    "Why am I here?",
]

INTRO_LINES = [
    "Just a quick stop.",
    "Something you always do.",
]

OUTRO_LINES = [
    "Shopping complete.",
    "That should be everything.",
    "Right...?",
]

TRIGGER_TEXT = "someone is waiting for me..."

LEFT_X  = RENDER_W // 4
RIGHT_X = RENDER_W * 3 // 4
DIVIDER = RENDER_W // 2

BUBBLE_W = 160
BUBBLE_H = 22
SLOT_W   = 175
SLOT_H   = 22


# ---------------------------------------------------------------------------
class Bubble:
    def __init__(self, text, x, y, is_decoy=False):
        self.text         = text
        self.start_x      = x
        self.start_y      = y
        self.x            = x
        self.y            = y
        self.is_decoy     = is_decoy
        self.dragging     = False
        self.drag_ox      = 0
        self.drag_oy      = 0
        self.alpha        = 0
        self.alive        = True
        self.placed       = False
        self.w            = BUBBLE_W
        self.h            = BUBBLE_H
        self.float_offset = random.uniform(0, math.pi * 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2,
                           self.w, self.h)

    def update(self, dt, timer):
        self.alpha = min(255, self.alpha + 120 * dt)
        if not self.dragging and not self.placed:
            self.y = self.start_y + math.sin(timer * 1.2 + self.float_offset) * 2


class Slot:
    def __init__(self, x, y, index):
        self.x            = x
        self.y            = y
        self.index        = index
        self.filled       = False
        self.filled_at    = -1   # which placement number filled this slot
        self.stage_index  = 0    # which corruption stage we're currently showing
        self.text         = ""   # current display text
        self.w            = SLOT_W
        self.h            = SLOT_H
        self.flash        = 0.0
        # glitch flash when text changes
        self.glitching    = False
        self.glitch_timer = 0.0

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2,
                           self.w, self.h)

    def advance_stage(self):
        """Move to next corruption stage if available."""
        stages = SLOT_STAGES[self.index]
        if self.stage_index < len(stages) - 1:
            self.stage_index += 1
            self.text         = stages[self.stage_index]
            self.glitching    = True
            self.glitch_timer = 0.0

    def update_glitch(self, dt):
        if self.glitching:
            self.glitch_timer += dt
            if self.glitch_timer > 0.5:
                self.glitching = False


# ---------------------------------------------------------------------------
class Chapter2Scene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)

        self.font_label  = self.assets.get_font(12)
        self.font_body   = self.assets.get_font(8)
        self.font_hint   = self.assets.get_font(6)

        self.bg = self.assets.get_image("backgrounds/supermarket")

        self.phase       = "intro"
        self.timer       = 0.0
        self.phase_timer = 0.0

        self.current_line = 0
        self.line_alpha   = 0.0
        self.lines_shown  = []

        self.overlay       = pygame.Surface((RENDER_W, RENDER_H))
        self.overlay.fill(BLACK)
        self.overlay_alpha = 255
        self.fading_out    = False

        self.bubbles        = []
        self.slots          = []
        self.dragged        = None
        self.solved         = False
        self.wrong_flash    = 0.0
        self.correct_count  = 0  # increments each time a correct bubble is placed

        # Glitch screen flash
        self.glitch_flash       = 0.0
        self.glitch_flash_color = (100, 50, 180)
        self.bg_flicker         = 0.0

        # Ghost trigger bubble
        self.show_trigger  = False
        self.trigger_alpha = 0.0
        self.trigger_timer = 0.0
        self.trigger_done  = False

        # Outro
        self.outro_line   = 0
        self.outro_alpha  = 0.0
        self.outro_shown  = []
        self.outro_darken = 0.0

        # Delay before transitioning after puzzle solve
        # so player sees the final corruption state
        self.solve_timer  = 0.0
        self.solve_delay  = 3.5   # seconds to show final state before outro

    # -----------------------------------------------------------------------
    def handle_event(self, event):
        if self.phase != "puzzle":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.fading_out = True
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = self._scale_mouse(pygame.mouse.get_pos())
            for bubble in reversed(self.bubbles):
                if not bubble.alive or bubble.placed:
                    continue
                if bubble.is_decoy and bubble.get_rect().collidepoint(mx, my):
                    bubble.alive = False
                    break
                if not bubble.is_decoy and bubble.get_rect().collidepoint(mx, my):
                    bubble.dragging = True
                    bubble.drag_ox  = bubble.x - mx
                    bubble.drag_oy  = bubble.y - my
                    self.dragged    = bubble
                    break

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragged:
                mx, my = self._scale_mouse(pygame.mouse.get_pos())
                self._try_place_bubble(self.dragged, mx, my)
                self.dragged.dragging = False
                self.dragged          = None

        if event.type == pygame.MOUSEMOTION:
            if self.dragged:
                mx, my         = self._scale_mouse(pygame.mouse.get_pos())
                self.dragged.x = mx + self.dragged.drag_ox
                self.dragged.y = my + self.dragged.drag_oy

    # -----------------------------------------------------------------------
    def update(self, dt):
        self.timer       += dt
        self.phase_timer += dt

        if self.overlay_alpha > 0 and not self.fading_out:
            self.overlay_alpha = max(0, self.overlay_alpha - 150 * dt)

        if self.fading_out:
            self.overlay_alpha = min(255, self.overlay_alpha + 150 * dt)
            if self.overlay_alpha >= 255:
                self.manager.replace_scene("ch3")
            return

        self.wrong_flash  = max(0, self.wrong_flash  - 200 * dt)
        self.glitch_flash = max(0, self.glitch_flash - 150 * dt)
        self.bg_flicker   = max(0, self.bg_flicker   - 300 * dt)

        # Update per-slot glitch flashes
        for slot in self.slots:
            slot.update_glitch(dt)

        # Ghost trigger bubble fade in/out
        if self.show_trigger:
            self.trigger_timer += dt
            if self.trigger_timer < 1.0:
                self.trigger_alpha = min(180, self.trigger_alpha + 150 * dt)
            elif self.trigger_timer > 3.5:
                self.trigger_alpha = max(0, self.trigger_alpha - 80 * dt)
                if self.trigger_alpha <= 0:
                    self.show_trigger = False
                    self.trigger_done = True

        if self.phase == "intro":
            self._update_intro(dt)
        elif self.phase == "puzzle":
            self._update_puzzle(dt)
        elif self.phase == "solve_pause":
            self._update_solve_pause(dt)
        elif self.phase == "outro":
            self._update_outro(dt)

    def _update_intro(self, dt):
        if self.current_line < len(INTRO_LINES):
            self.line_alpha = min(255, self.line_alpha + 90 * dt)
            if self.line_alpha >= 255:
                self.phase_timer += dt
                if self.phase_timer > 2.0:
                    self.lines_shown.append(INTRO_LINES[self.current_line])
                    self.current_line += 1
                    self.line_alpha    = 0
                    self.phase_timer   = 0.0
        else:
            if self.phase_timer > 1.5:
                self._start_puzzle()

    def _start_puzzle(self):
        self.phase       = "puzzle"
        self.phase_timer = 0.0

        # Build bubble list
        all_bubbles = [{"text": a, "is_decoy": False} for a in CORRECT_ANSWERS]
        all_bubbles += [{"text": t, "is_decoy": True}  for t in DECOY_BUBBLES]
        random.shuffle(all_bubbles)

        total    = len(all_bubbles)
        top_pad  = 36
        bot_pad  = 20
        usable_h = RENDER_H - top_pad - bot_pad
        gap      = usable_h // total

        for i, data in enumerate(all_bubbles):
            y = top_pad + i * gap + gap // 2
            self.bubbles.append(Bubble(
                text     = data["text"],
                x        = LEFT_X,
                y        = y,
                is_decoy = data["is_decoy"],
            ))

        # 4 slots on the right
        num_slots = len(CORRECT_ANSWERS)
        s_top     = 50
        s_bot     = RENDER_H - 24
        s_gap     = (s_bot - s_top) // num_slots

        for i in range(num_slots):
            y = s_top + i * s_gap + s_gap // 2
            self.slots.append(Slot(RIGHT_X, y, i))

    def _update_puzzle(self, dt):
        for bubble in self.bubbles:
            if bubble.alive:
                bubble.update(dt, self.timer)

        # All slots filled → enter solve_pause before outro
        if not self.solved and all(s.filled for s in self.slots):
            self.solved      = True
            self.phase       = "solve_pause"
            self.phase_timer = 0.0
            self.solve_timer = 0.0

    def _update_solve_pause(self, dt):
        """Show the final corruption state for solve_delay seconds."""
        self.solve_timer += dt
        if self.solve_timer >= self.solve_delay:
            self.phase       = "outro"
            self.phase_timer = 0.0

    def _update_outro(self, dt):
        if self.outro_line < len(OUTRO_LINES):
            self.outro_alpha = min(255, self.outro_alpha + 80 * dt)
            if self.outro_alpha >= 255:
                self.phase_timer += dt
                hold = 3.5 if self.outro_line == len(OUTRO_LINES) - 1 else 2.0
                if self.phase_timer > hold:
                    self.outro_shown.append(OUTRO_LINES[self.outro_line])
                    self.outro_line  += 1
                    self.outro_alpha  = 0
                    self.phase_timer  = 0.0
                    if self.outro_line == len(OUTRO_LINES):
                        self.outro_darken = 200
        else:
            self.outro_darken = min(240, self.outro_darken + 60 * dt)
            if self.phase_timer > 3.0:
                self.fading_out = True

    # -----------------------------------------------------------------------
    def _try_place_bubble(self, bubble, mx, my):
        for slot in self.slots:
            if slot.get_rect().collidepoint(mx, my) and not slot.filled:
                if bubble.text == CORRECT_ANSWERS[slot.index]:
                    # --- Correct placement ---
                    slot.filled      = True
                    slot.filled_at   = self.correct_count   # record when it was placed
                    slot.stage_index = 0
                    slot.text        = SLOT_STAGES[slot.index][0]
                    slot.flash       = 1.0
                    bubble.placed    = True
                    bubble.alive     = False
                    self.correct_count += 1

                    # Corrupt every slot that was placed BEFORE this one
                    # (they've been sitting there longer, so they decay further)
                    for other in self.slots:
                        if other.filled and other.index != slot.index:
                            other.advance_stage()

                    # Glitch flash only from 2nd placement onward
                    if self.correct_count >= 2:
                        self._trigger_glitch()

                    # Ghost trigger on 2nd placement
                    if self.correct_count == 2 and not self.trigger_done:
                        self.show_trigger  = True
                        self.trigger_timer = 0.0
                        self.trigger_alpha = 0.0
                else:
                    slot.flash       = -1.0
                    self.wrong_flash = 255
                    bubble.x         = bubble.start_x
                    bubble.y         = bubble.start_y
                return
        bubble.x = bubble.start_x
        bubble.y = bubble.start_y

    def _trigger_glitch(self):
        self.glitch_flash = 180
        self.bg_flicker   = 1.0

    # -----------------------------------------------------------------------
    def draw(self, surface):
        self._draw_background(surface)

        if self.phase == "intro":
            self._draw_intro(surface)
        elif self.phase in ("puzzle", "solve_pause"):
            self._draw_puzzle(surface)
        elif self.phase == "outro":
            self._draw_outro(surface)

        if self.wrong_flash > 0:
            s = pygame.Surface((RENDER_W, RENDER_H))
            s.fill((180, 30, 30))
            s.set_alpha(int(self.wrong_flash * 0.4))
            surface.blit(s, (0, 0))

        if self.glitch_flash > 0:
            s = pygame.Surface((RENDER_W, RENDER_H))
            s.fill(self.glitch_flash_color)
            s.set_alpha(int(self.glitch_flash * 0.35))
            surface.blit(s, (0, 0))

        if self.show_trigger and self.trigger_alpha > 0:
            self._draw_trigger_bubble(surface)

        if self.overlay_alpha > 0:
            self.overlay.set_alpha(int(self.overlay_alpha))
            surface.blit(self.overlay, (0, 0))

    def _draw_background(self, surface):
        bg = pygame.transform.scale(self.bg, (RENDER_W, RENDER_H))
        if self.bg_flicker > 0:
            bg = bg.copy()
            f = pygame.Surface((RENDER_W, RENDER_H))
            f.fill((180, 160, 200))
            f.set_alpha(int(self.bg_flicker * 120))
            bg.blit(f, (0, 0))
        surface.blit(bg, (0, 0))
        self._draw_scanlines(surface)

    def _draw_intro(self, surface):
        y_start  = RENDER_H // 2 - 24
        line_gap = 20
        for i, line in enumerate(self.lines_shown):
            txt = self.font_body.render(line, False, WARM_WHITE)
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + i * line_gap))
        if self.current_line < len(INTRO_LINES):
            txt = self.font_body.render(INTRO_LINES[self.current_line], False, WARM_WHITE)
            txt.set_alpha(int(self.line_alpha))
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + len(self.lines_shown) * line_gap))

    def _draw_puzzle(self, surface):
        # Panel labels
        lbl_l = self.font_label.render("Memories", False, (140, 135, 155))
        surface.blit(lbl_l, (LEFT_X - lbl_l.get_width() // 2, 10))

        lbl_r = self.font_label.render("Shopping list", False, (140, 135, 155))
        surface.blit(lbl_r, (RIGHT_X - lbl_r.get_width() // 2, 10))

        pygame.draw.line(surface, (60, 55, 75),
                         (DIVIDER, 8), (DIVIDER, RENDER_H - 8), 1)

        # --- Slots ---
        for slot in self.slots:
            color  = (50, 45, 65)
            border = (100, 90, 120)

            if slot.flash > 0:
                color  = (30, 80, 50);  border = (60, 180, 80)
                slot.flash = max(0, slot.flash - 0.05)
            elif slot.flash < 0:
                color  = (80, 30, 30);  border = (180, 60, 60)
                slot.flash = min(0, slot.flash + 0.05)

            rect = slot.get_rect()
            pygame.draw.rect(surface, color, rect, border_radius=4)
            pygame.draw.rect(surface, border, rect, 1, border_radius=4)

            num = self.font_hint.render(str(slot.index + 1), False, (100, 95, 115))
            surface.blit(num, (rect.x + 4, rect.centery - num.get_height() // 2))

            if slot.filled and slot.text:
                # Colour based on corruption stage
                if slot.glitching:
                    t      = slot.glitch_timer
                    tcolor = (220, 80, 80) if int(t * 12) % 2 == 0 else WARM_WHITE
                else:
                    stage  = slot.stage_index
                    tcolor = WARM_GOLD          if stage == 0 else \
                             (220, 150, 80)     if stage == 1 else \
                             (220, 80,  80)

                txt = self.font_body.render(slot.text, False, tcolor)
                surface.blit(txt, (rect.x + 16,
                                   rect.centery - txt.get_height() // 2))

        # --- Bubbles ---
        for bubble in self.bubbles:
            if not bubble.alive:
                continue
            rect = bubble.get_rect()

            if bubble.is_decoy:
                color  = (60, 30, 35);  border = (140, 70, 75);   tcolor = (200, 140, 145)
            else:
                color  = (40, 38, 60);  border = (120, 110, 150); tcolor = WARM_WHITE

            if bubble.dragging:
                color  = (70, 65, 95);  border = (180, 170, 220)

            bs = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(bs, (*color, 220), bs.get_rect(), border_radius=4)
            pygame.draw.rect(bs, (*border, 255), bs.get_rect(), 1, border_radius=4)
            bs.set_alpha(int(bubble.alpha))
            surface.blit(bs, rect)

            txt = self.font_body.render(bubble.text, False, tcolor)
            txt.set_alpha(int(bubble.alpha))
            surface.blit(txt, (rect.centerx - txt.get_width() // 2,
                               rect.centery - txt.get_height() // 2))

            if bubble.is_decoy:
                x_txt = self.font_hint.render("x", False, (200, 100, 100))
                surface.blit(x_txt, (rect.right - 10, rect.top + 2))

        hint = self.font_hint.render(
            "Drag correct bubbles to slots  |  Click red to dismiss",
            False, (100, 95, 115))
        surface.blit(hint, (RENDER_W // 2 - hint.get_width() // 2, RENDER_H - 12))

    def _draw_trigger_bubble(self, surface):
        drift_x = int(math.sin(self.timer * 0.8) * 3)
        drift_y = int(math.cos(self.timer * 0.6) * 2)
        w, h    = 200, 22
        x       = RENDER_W - w - 2 + drift_x
        y       = 28 + drift_y

        bs = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(bs, (180, 160, 220, 60),  bs.get_rect(), border_radius=5)
        pygame.draw.rect(bs, (200, 180, 240, 120), bs.get_rect(), 1, border_radius=5)
        bs.set_alpha(int(self.trigger_alpha))
        surface.blit(bs, (x, y))

        txt = self.font_hint.render(TRIGGER_TEXT, False, (220, 210, 240))
        txt.set_alpha(int(self.trigger_alpha))
        surface.blit(txt, (x + w // 2 - txt.get_width() // 2,
                           y + h // 2 - txt.get_height() // 2))

    def _draw_outro(self, surface):
        dark = pygame.Surface((RENDER_W, RENDER_H))
        dark.fill(BLACK)
        dark.set_alpha(int(self.outro_darken))
        surface.blit(dark, (0, 0))

        y_start  = RENDER_H // 2 - 30
        line_gap = 22
        for i, line in enumerate(self.outro_shown):
            color = (200, 100, 100) if line == "Right...?" else WARM_WHITE
            txt   = self.font_body.render(line, False, color)
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + i * line_gap))

        if self.outro_line < len(OUTRO_LINES):
            color = (200, 100, 100) \
                if OUTRO_LINES[self.outro_line] == "Right...?" else WARM_WHITE
            txt = self.font_body.render(OUTRO_LINES[self.outro_line], False, color)
            txt.set_alpha(int(self.outro_alpha))
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + len(self.outro_shown) * line_gap))

    def _draw_scanlines(self, surface):
        scanline = pygame.Surface((RENDER_W, 1))
        scanline.fill((0, 0, 0))
        scanline.set_alpha(35)
        for y in range(0, RENDER_H, 2):
            surface.blit(scanline, (0, y))

    def _scale_mouse(self, pos):
        mx, my  = pos
        scale_x = RENDER_W / pygame.display.get_surface().get_width()
        scale_y = RENDER_H / pygame.display.get_surface().get_height()
        return (int(mx * scale_x), int(my * scale_y))