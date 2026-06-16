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
# Fixed destination board — always in this order, never shuffled
# ---------------------------------------------------------------------------
DESTINATIONS = [
    "Pioneer",
    "Boon Lay",
    "Lakeside",
    "Chinese Garden",
]
GLITCHED_DESTINATIONS = ["???", "---", "█ █ █", "HOME?"]

# ---------------------------------------------------------------------------
# Puzzle data
# ---------------------------------------------------------------------------
CORRECT_ANSWERS = [
    "Wait for the train",
    "Board the train",
    "Check my stop",
    "Get off at home",
]

SLOT_STAGES = [
    # Slot 0 — "Wait for the train"
    [
        "Wait for the train",       # clean — just placed
        "I think I wait here?",     # after slot 1 filled
        "Do I take the train?",     # after slot 2 filled
        "Which platform...?",       # after slot 3 filled
    ],
    # Slot 1 — "Board the train"
    [
        "Board the train",          # clean
        "Was it this train?",       # after slot 2 filled
        "Which train was it?",      # after slot 3 filled
    ],
    # Slot 2 — "Check my stop"
    [
        "Check my stop",            # clean
        "What stop is home?",       # after slot 3 filled
    ],
    # Slot 3 — "Get off at home"
    [
        "Get off at home",          # clean
        "Is this my stop?",         # corruption begins
    ],
]

DECOY_BUBBLES = [
    "I'm already home",
    "I never left home",
    "I went past my stop",
]

INTRO_LINES = [
    "Now...",
    "it's time to go home.",
]

OUTRO_LINES = [
    "You're almost there.",
    "Just a little further.",
]

TRIGGER_TEXT = "was someone waiting for me?"

LEFT_X  = RENDER_W // 4
RIGHT_X = RENDER_W * 3 // 4
DIVIDER = RENDER_W // 2

BUBBLE_W = 150
BUBBLE_H = 22
SLOT_W   = 165
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


# ---------------------------------------------------------------------------
class Slot:
    def __init__(self, x, y, index):
        self.x            = x
        self.y            = y
        self.index        = index
        self.filled       = False
        self.stage_index  = 0
        self.text         = ""
        self.w            = SLOT_W
        self.h            = SLOT_H
        self.flash        = 0.0
        self.glitching    = False
        self.glitch_timer = 0.0

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2,
                           self.w, self.h)

    def advance_stage(self):
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
class Chapter3Scene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)

        self.font_label  = self.assets.get_font(12)
        self.font_body   = self.assets.get_font(8)
        self.font_hint   = self.assets.get_font(6)

        self.bg = self.assets.get_image("backgrounds/mrt_station")
        self.img_now    = self.assets.get_image("scenes/ch3_now")
        self.img_almost = self.assets.get_image("scenes/ch3_almost")

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

        self.bubbles       = []
        self.slots         = []
        self.dragged       = None
        self.solved        = False
        self.wrong_flash   = 0.0
        self.correct_count = 0

        # Glitch
        self.glitch_flash       = 0.0
        self.glitch_flash_color = (80, 30, 160)
        self.bg_flicker         = 0.0

        # Destination board — fixed order, glitch level rises with placements
        self.dest_entries = list(DESTINATIONS)

        # Ghost trigger — blocking version
        self.show_trigger    = False
        self.trigger_alpha   = 0.0
        self.trigger_timer   = 0.0
        self.trigger_done    = False
        self.trigger_waiting = False   # True = blocks screen until clicked

        # Outro
        self.outro_line  = 0
        self.outro_alpha = 0.0
        self.outro_shown = []
        self.solve_timer = 0.0

    # -----------------------------------------------------------------------
    def handle_event(self, event):
        # Trigger bubble blocks ALL input until player clicks it
        if self.trigger_waiting:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.trigger_waiting = False
                self.show_trigger    = False
                self.trigger_done    = True
            return

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
                self.manager.replace_scene("ch4")
            return

        self.wrong_flash  = max(0, self.wrong_flash  - 200 * dt)
        self.glitch_flash = max(0, self.glitch_flash - 130 * dt)
        self.bg_flicker   = max(0, self.bg_flicker   - 250 * dt)

        for slot in self.slots:
            slot.update_glitch(dt)

        # Trigger bubble fades in while waiting for click
        if self.show_trigger and self.trigger_waiting:
            self.trigger_alpha = min(255, self.trigger_alpha + 150 * dt)

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

        all_bubbles = [{"text": a, "is_decoy": False} for a in CORRECT_ANSWERS]
        all_bubbles += [{"text": t, "is_decoy": True}  for t in DECOY_BUBBLES]
        random.shuffle(all_bubbles)

        total    = len(all_bubbles)
        top_pad  = 58
        usable_h = RENDER_H - top_pad - 20
        gap      = usable_h // total

        for i, data in enumerate(all_bubbles):
            y = top_pad + i * gap + gap // 2
            self.bubbles.append(Bubble(
                text     = data["text"],
                x        = LEFT_X,
                y        = y,
                is_decoy = data["is_decoy"],
            ))

        num_slots = len(CORRECT_ANSWERS)
        s_top     = 58
        s_bot     = RENDER_H - 24
        s_gap     = (s_bot - s_top) // num_slots

        for i in range(num_slots):
            y = s_top + i * s_gap + s_gap // 2
            self.slots.append(Slot(RIGHT_X, y, i))

    def _update_puzzle(self, dt):
        for bubble in self.bubbles:
            if bubble.alive:
                bubble.update(dt, self.timer)

        if not self.solved and all(s.filled for s in self.slots):
            self.solved      = True
            self.phase       = "solve_pause"
            self.phase_timer = 0.0
            self.solve_timer = 0.0

    def _update_solve_pause(self, dt):
        self.solve_timer += dt
        if self.solve_timer >= 3.0:
            self.phase       = "outro"
            self.phase_timer = 0.0

    def _update_outro(self, dt):
        if self.outro_line < len(OUTRO_LINES):
            self.outro_alpha = min(255, self.outro_alpha + 80 * dt)
            if self.outro_alpha >= 255:
                self.phase_timer += dt
                if self.phase_timer > 2.5:
                    self.outro_shown.append(OUTRO_LINES[self.outro_line])
                    self.outro_line  += 1
                    self.outro_alpha  = 0
                    self.phase_timer  = 0.0
        else:
            if self.phase_timer > 2.0:
                self.fading_out = True

    # -----------------------------------------------------------------------
    def _try_place_bubble(self, bubble, mx, my):
        for slot in self.slots:
            if slot.get_rect().collidepoint(mx, my) and not slot.filled:
                if bubble.text == CORRECT_ANSWERS[slot.index]:
                    # Correct placement
                    slot.filled      = True
                    slot.stage_index = 0
                    slot.text        = SLOT_STAGES[slot.index][0]
                    slot.flash       = 1.0
                    bubble.placed    = True
                    bubble.alive     = False
                    self.correct_count += 1

                    # Corrupt every previously placed slot by one stage
                    for other in self.slots:
                        if other.filled and other.index != slot.index:
                            other.advance_stage()

                    # Scramble destination board — intensity tied to count
                    self._scramble_destinations()

                    # Glitch flash from 2nd placement onward
                    if self.correct_count >= 2:
                        self._trigger_glitch()

                    # Blocking trigger bubble on 3rd correct placement
                    if self.correct_count == 3 and not self.trigger_done:
                        self.show_trigger    = True
                        self.trigger_waiting = True
                        self.trigger_alpha   = 0.0
                        self.trigger_timer   = 0.0
                else:
                    slot.flash       = -1.0
                    self.wrong_flash = 255
                    bubble.x         = bubble.start_x
                    bubble.y         = bubble.start_y
                return
        bubble.x = bubble.start_x
        bubble.y = bubble.start_y

    def _trigger_glitch(self):
        self.glitch_flash = 220
        self.bg_flicker   = 1.0

    def _scramble_destinations(self):
        """Glitch intensity tied to correct_count.
        0 placements = all clean green.
        Each placement increases the chance a station glitches."""
        for i in range(len(self.dest_entries)):
            glitch_chance = self.correct_count * 0.22  # 22%, 44%, 66%, 88%
            if random.random() < glitch_chance:
                self.dest_entries[i] = random.choice(GLITCHED_DESTINATIONS)
            else:
                self.dest_entries[i] = DESTINATIONS[i]  # restore fixed order

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
            s.set_alpha(int(self.glitch_flash * 0.4))
            surface.blit(s, (0, 0))

        # Trigger bubble drawn last so it's always on top
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
            f.fill((160, 140, 200))
            f.set_alpha(int(self.bg_flicker * 140))
            bg.blit(f, (0, 0))
        surface.blit(bg, (0, 0))
        self._draw_destination_board(surface)
        self._draw_scanlines(surface)

    def _draw_destination_board(self, surface):
        """Full-width MRT arrivals board across the very top."""
        board_rect = pygame.Rect(0, 0, RENDER_W, 26)
        pygame.draw.rect(surface, (20, 18, 30), board_rect)
        pygame.draw.rect(surface, (60, 55, 80), board_rect, 1)

        font    = self.assets.get_font(8)
        spacing = RENDER_W // 4
        for i, dest in enumerate(self.dest_entries[:4]):
            color = (220, 80, 80) if dest in GLITCHED_DESTINATIONS \
                    else (160, 220, 160)
            txt = font.render(dest, False, color)
            x   = i * spacing + spacing // 2 - txt.get_width() // 2
            surface.blit(txt, (x, 6))

    def _draw_intro(self, surface):
        bg = pygame.transform.scale(self.img_now, (RENDER_W, RENDER_H))
        surface.blit(bg, (0, 0))
        y_start = RENDER_H // 2 - 16
        for i, line in enumerate(self.lines_shown):
            txt = self.font_body.render(line, False, WARM_WHITE)
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + i * 18))
        if self.current_line < len(INTRO_LINES):
            txt = self.font_body.render(INTRO_LINES[self.current_line],
                                        False, WARM_WHITE)
            txt.set_alpha(int(self.line_alpha))
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + len(self.lines_shown) * 18))

    def _draw_puzzle(self, surface):
        # Panel labels — below the destination board
        lbl_l = self.font_label.render("Memories", False, (140, 135, 155))
        surface.blit(lbl_l, (LEFT_X - lbl_l.get_width() // 2, 36))

        lbl_r = self.font_label.render("Getting home", False, (140, 135, 155))
        surface.blit(lbl_r, (RIGHT_X - lbl_r.get_width() // 2, 36))

        pygame.draw.line(surface, (60, 55, 75),
                         (DIVIDER, 30), (DIVIDER, RENDER_H - 8), 1)

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
                # Green → yellow → orange → red as corruption worsens
                if slot.glitching:
                    t      = slot.glitch_timer
                    tcolor = (220, 80, 80) if int(t * 12) % 2 == 0 \
                             else (160, 220, 160)
                else:
                    stage  = slot.stage_index
                    tcolor = (160, 220, 160) if stage == 0 else \
                             (220, 200, 80)  if stage == 1 else \
                             (220, 130, 60)  if stage == 2 else \
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
                color  = (60, 30, 35);  border = (140, 70, 75);  tcolor = (200, 140, 145)
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
        surface.blit(hint, (RENDER_W // 2 - hint.get_width() // 2, RENDER_H - 10))

    def _draw_trigger_bubble(self, surface):
        if self.trigger_waiting:
            # Dim everything behind it
            overlay = pygame.Surface((RENDER_W, RENDER_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            # Big centred bubble
            w, h = 260, 60
            x    = RENDER_W // 2 - w // 2
            y    = RENDER_H // 2 - h // 2

            bs = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(bs, (180, 160, 220, 180), bs.get_rect(), border_radius=10)
            pygame.draw.rect(bs, (220, 200, 255, 255), bs.get_rect(), 2,
                             border_radius=10)
            bs.set_alpha(int(self.trigger_alpha))
            surface.blit(bs, (x, y))

            txt = self.font_body.render(TRIGGER_TEXT, False, (240, 230, 255))
            txt.set_alpha(int(self.trigger_alpha))
            surface.blit(txt, (x + w // 2 - txt.get_width() // 2,
                               y + h // 2 - txt.get_height() // 2 - 8))

            hint = self.font_hint.render("[ click to continue ]", False,
                                         (180, 170, 200))
            hint.set_alpha(int(self.trigger_alpha))
            surface.blit(hint, (x + w // 2 - hint.get_width() // 2,
                                y + h // 2 + 10))

    def _draw_outro(self, surface):
        dark = pygame.Surface((RENDER_W, RENDER_H))
        dark.fill(BLACK)
        dark.set_alpha(180)
        surface.blit(dark, (0, 0))

        bg = pygame.transform.scale(self.img_almost, (RENDER_W, RENDER_H))
        bg.set_alpha(60)
        surface.blit(bg, (0, 0))

        y_start = RENDER_H // 2 - 18
        for i, line in enumerate(self.outro_shown):
            txt = self.font_body.render(line, False, WARM_WHITE)
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + i * 20))
        if self.outro_line < len(OUTRO_LINES):
            txt = self.font_body.render(OUTRO_LINES[self.outro_line],
                                        False, WARM_WHITE)
            txt.set_alpha(int(self.outro_alpha))
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + len(self.outro_shown) * 20))

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