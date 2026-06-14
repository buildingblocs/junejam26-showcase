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
# ---------------------------------------------------------------------------
CORRECT_ANSWERS = [
    "Leaving home",
    "Buying groceries",
    "Taking the MRT",
    "Finding home",
]

BUBBLE_STAGES = [
    # Bubble 0 — "Leaving home"
    [
        "Leaving home",
        "Left home?",
        "Did I leave?",
        "Finding home",
    ],
    # Bubble 1 — "Buying groceries"
    [
        "Buying groceries",
        "Did I buy something?",
        "What did I buy?",
    ],
    # Bubble 2 — "Taking the MRT"
    [
        "Taking the MRT",
        "Which train?",
        "Am I on the train?",
    ],
    # Bubble 3 — "Finding home"
    [
        "Finding home",
        "Is this home?",
    ],
]

SLOT_STAGES = [
    ["Leaving home",     "Left home?",          "Did I leave?",        "Finding home"],
    ["Buying groceries", "Did I buy something?", "What did I buy?"],
    ["Taking the MRT",   "Which train?",         "Am I on the train?"],
    ["Finding home",     "Is this home?"],
]

DECOY_BUBBLES = [
    "I never left",
    "I'm already here",
]

DOOR_LINES = [
    "Have I always lived here?",
]

ENTER_LINES = [
    "This is my home.",
    "I always come back here.",
    "Wait...",
    "I think I live here.",
    "This isn't familiar.",
    "I don't remember.",
]

OUTRO_LINES = [
    "Is this home?",
    "",
    "I think it is.",
]

ENDING_LINES = [
    "Everyday, millions of people",
    "find their way home without thinking.",
    "",
    "But for some,",
    "finding the way home",
    "is an ongoing battle they must face",
    "again and again.",
]

LEFT_X  = RENDER_W // 4
RIGHT_X = RENDER_W * 3 // 4
DIVIDER = RENDER_W // 2

BUBBLE_W = 160
BUBBLE_H = 22
SLOT_W   = 175
SLOT_H   = 22

GLITCH_CHARS = "█▓▒░?#@"


# ---------------------------------------------------------------------------
class Bubble:
    def __init__(self, text, x, y, is_decoy=False, stages=None, bubble_index=0):
        self.stages       = stages or [text]
        self.stage_index  = 0
        self.text         = self.stages[0]
        self.correct_text = text
        self.start_x      = x
        self.start_y      = y
        self.x            = x
        self.y            = y
        self.is_decoy     = is_decoy
        self.bubble_index = bubble_index
        self.dragging     = False
        self.drag_ox      = 0
        self.drag_oy      = 0
        self.alpha        = 0
        self.alive        = True
        self.placed       = False
        self.w            = BUBBLE_W
        self.h            = BUBBLE_H
        self.float_offset = random.uniform(0, math.pi * 2)
        self.glitching    = False
        self.glitch_timer = 0.0

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2,
                           self.w, self.h)

    def corrupt(self):
        if self.stage_index < len(self.stages) - 1:
            self.stage_index += 1
            self.text         = self.stages[self.stage_index]
            self.glitching    = True
            self.glitch_timer = 0.0

    def update(self, dt, timer):
        self.alpha = min(255, self.alpha + 120 * dt)
        if not self.dragging and not self.placed:
            self.y = self.start_y + math.sin(timer * 1.2 + self.float_offset) * 2
        if self.glitching:
            self.glitch_timer += dt
            if self.glitch_timer > 0.5:
                self.glitching = False


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
class Chapter4Scene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)

        self.font_label  = self.assets.get_font(12)
        self.font_body   = self.assets.get_font(8)
        self.font_hint   = self.assets.get_font(6)
        self.font_ending = self.assets.get_font(8)

        self.bg_exterior     = self.assets.get_image("backgrounds/house_exterior")
        self.bg_interior     = self.assets.get_image("backgrounds/bedroom")
        self.bg_bedroom_dark = self.assets.get_image("backgrounds/bedroom_dark")
        self.img_livingroom  = self.assets.get_image("backgrounds/living_room")
        self.img_door        = self.assets.get_image("scenes/ch4_door")
        self.img_ishome      = self.assets.get_image("scenes/ch4_ishome")
        self.img_thinkitis   = self.assets.get_image("scenes/ch4_thinkitis")
        self.img_frame_photo = self.assets.get_image("ui/frame_photo_end")

        # phase flow:
        # "door" → "enter" → "livingroom" → "puzzle" → "solve_pause"
        #        → "outro" → "ending" → "done"
        self.phase       = "door"
        self.timer       = 0.0
        self.phase_timer = 0.0

        # Door phase
        self.door_line_alpha = 0.0
        self.door_shown      = False
        self.warm_light      = 0.0

        # Enter phase
        self.enter_index  = 0
        self.enter_alpha  = 0.0
        self.enter_shown  = []

        # Living room phase (after enter, before puzzle)
        self.livingroom_timer = 0.0

        # Overlay
        self.overlay       = pygame.Surface((RENDER_W, RENDER_H))
        self.overlay.fill(BLACK)
        self.overlay_alpha = 255
        self.fading_out    = False

        # Puzzle
        self.bubbles       = []
        self.slots         = []
        self.dragged       = None
        self.solved        = False
        self.wrong_flash   = 0.0
        self.correct_count = 0

        # Glitch
        self.glitch_flash       = 0.0
        self.glitch_flash_color = (60, 20, 140)
        self.bg_flicker         = 0.0
        self.crack_lines        = []
        self.screen_shake       = 0.0

        # Photo frame
        self.frame_alpha = 0.0
        self.frame_rect  = pygame.Rect(RENDER_W - 55, 24, 48, 54)

        # Warm light
        self.warm_alpha  = 0.0

        # Outro
        self.outro_index = 0
        self.outro_alpha = 0.0
        self.outro_shown = []

        # Ending crawl
        self.ending_index = 0
        self.ending_alpha = 0.0
        self.ending_shown = []
        self.end_darken   = 0.0

        self.solve_timer = 0.0

    # -----------------------------------------------------------------------
    def handle_event(self, event):
        if self.phase == "door":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._start_enter()
            return

        if self.phase == "enter":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._start_livingroom()
            return

        # Living room phase — no input needed, auto-advances
        if self.phase == "livingroom":
            return

        if self.phase != "puzzle":
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
            self.overlay_alpha = min(255, self.overlay_alpha + 80 * dt)
            if self.overlay_alpha >= 255:
                self.manager.replace_scene("menu")
            return

        self.wrong_flash  = max(0, self.wrong_flash  - 200 * dt)
        self.glitch_flash = max(0, self.glitch_flash - 100 * dt)
        self.bg_flicker   = max(0, self.bg_flicker   - 200 * dt)
        self.screen_shake = max(0, self.screen_shake - 8   * dt)

        for slot in self.slots:
            slot.update_glitch(dt)

        if self.phase == "door":
            self._update_door(dt)
        elif self.phase == "enter":
            self._update_enter(dt)
        elif self.phase == "livingroom":
            self._update_livingroom(dt)
        elif self.phase == "puzzle":
            self._update_puzzle(dt)
        elif self.phase == "solve_pause":
            self._update_solve_pause(dt)
        elif self.phase == "outro":
            self._update_outro(dt)
        elif self.phase == "ending":
            self._update_ending(dt)

    def _update_door(self, dt):
        self.warm_light      = min(160, self.warm_light + 40 * dt)
        self.door_line_alpha = min(255, self.door_line_alpha + 60 * dt)
        if self.phase_timer > 12.0:
            self._start_enter()

    def _start_enter(self):
        self.phase       = "enter"
        self.phase_timer = 0.0

    def _update_enter(self, dt):
        if self.enter_index < len(ENTER_LINES):
            self.enter_alpha = min(255, self.enter_alpha + 100 * dt)
            if self.enter_alpha >= 255:
                self.phase_timer += dt
                if self.phase_timer > 0.8:
                    self.enter_shown.append(ENTER_LINES[self.enter_index])
                    self.enter_index += 1
                    self.enter_alpha  = 0
                    self.phase_timer  = 0.0
        else:
            if self.phase_timer > 1.5:
                self._start_livingroom()

    def _start_livingroom(self):
        self.phase            = "livingroom"
        self.phase_timer      = 0.0
        self.livingroom_timer = 0.0

    def _update_livingroom(self, dt):
        self.livingroom_timer += dt
        # Show living room for 3 seconds, then go to puzzle
        if self.livingroom_timer > 3.0:
            self._start_puzzle()

    def _start_puzzle(self):
        self.phase       = "puzzle"
        self.phase_timer = 0.0

        correct_bubbles = []
        for i, answer in enumerate(CORRECT_ANSWERS):
            correct_bubbles.append({
                "text":    answer,
                "stages":  BUBBLE_STAGES[i],
                "index":   i,
                "is_decoy": False,
            })
        decoy_bubbles = [{"text": t, "stages": [t], "index": -1, "is_decoy": True}
                         for t in DECOY_BUBBLES]

        all_bubbles = correct_bubbles + decoy_bubbles
        random.shuffle(all_bubbles)

        total    = len(all_bubbles)
        top_pad  = 40
        usable_h = RENDER_H - top_pad - 20
        gap      = usable_h // total

        for i, data in enumerate(all_bubbles):
            y = top_pad + i * gap + gap // 2
            self.bubbles.append(Bubble(
                text         = data["text"],
                x            = LEFT_X,
                y            = y,
                is_decoy     = data["is_decoy"],
                stages       = data["stages"],
                bubble_index = data["index"],
            ))

        num_slots = len(CORRECT_ANSWERS)
        s_top     = 40
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
        self.warm_alpha   = min(60, self.warm_alpha + 20 * dt)
        self.frame_alpha  = min(220, self.frame_alpha + 30 * dt)
        if self.solve_timer >= 3.0:
            self.phase       = "outro"
            self.phase_timer = 0.0

    def _update_outro(self, dt):
        self.warm_alpha  = min(120, self.warm_alpha  + 15 * dt)
        self.frame_alpha = min(255, self.frame_alpha + 20 * dt)

        if self.outro_index < len(OUTRO_LINES):
            if OUTRO_LINES[self.outro_index] == "":
                self.outro_shown.append("")
                self.outro_index += 1
                self.phase_timer  = 0.0
                return
            self.outro_alpha = min(255, self.outro_alpha + 70 * dt)
            if self.outro_alpha >= 255:
                self.phase_timer += dt
                hold = 3.0 if self.outro_index == len(OUTRO_LINES) - 1 else 2.0
                if self.phase_timer > hold:
                    self.outro_shown.append(OUTRO_LINES[self.outro_index])
                    self.outro_index += 1
                    self.outro_alpha  = 0
                    self.phase_timer  = 0.0
        else:
            if self.phase_timer > 1.0:
                self.phase       = "ending"
                self.phase_timer = 0.0

    def _update_ending(self, dt):
        self.end_darken = min(255, self.end_darken + 40 * dt)

        if self.ending_index < len(ENDING_LINES):
            if ENDING_LINES[self.ending_index] == "":
                self.ending_shown.append("")
                self.ending_index += 1
                self.phase_timer   = 0.0
                return
            self.ending_alpha = min(255, self.ending_alpha + 60 * dt)
            if self.ending_alpha >= 255:
                self.phase_timer += dt
                if self.phase_timer > 2.0:
                    self.ending_shown.append(ENDING_LINES[self.ending_index])
                    self.ending_index += 1
                    self.ending_alpha  = 0
                    self.phase_timer   = 0.0
        else:
            if self.phase_timer > 3.0:
                self.fading_out = True

    # -----------------------------------------------------------------------
    def _try_place_bubble(self, bubble, mx, my):
        for slot in self.slots:
            if slot.get_rect().collidepoint(mx, my) and not slot.filled:
                if bubble.correct_text == CORRECT_ANSWERS[slot.index]:
                    slot.filled      = True
                    slot.stage_index = 0
                    slot.text        = SLOT_STAGES[slot.index][0]
                    slot.flash       = 1.0
                    bubble.placed    = True
                    bubble.alive     = False
                    self.correct_count += 1

                    for other in self.slots:
                        if other.filled and other.index != slot.index:
                            other.advance_stage()

                    for other_b in self.bubbles:
                        if other_b.alive and not other_b.placed \
                                and not other_b.is_decoy:
                            other_b.corrupt()

                    self._add_crack()
                    self._trigger_glitch()

                else:
                    slot.flash       = -1.0
                    self.wrong_flash = 255
                    bubble.x         = bubble.start_x
                    bubble.y         = bubble.start_y
                return
        bubble.x = bubble.start_x
        bubble.y = bubble.start_y

    def _trigger_glitch(self):
        intensity = 80 + self.correct_count * 50
        self.glitch_flash = min(255, intensity)
        self.bg_flicker   = 1.0
        self.screen_shake = 2 + self.correct_count * 1.5

    def _add_crack(self):
        num_cracks = 4 + self.correct_count * 3
        for _ in range(num_cracks):
            x1     = random.randint(0, RENDER_W)
            y1     = random.randint(0, RENDER_H)
            length = random.randint(60, 160)
            angle  = random.uniform(0, math.pi * 2)
            x2     = int(x1 + math.cos(angle) * length)
            y2     = int(y1 + math.sin(angle) * length)
            color  = random.choice([
                (180, 160, 220),
                (220, 180, 255),
                (140, 100, 200),
                (255, 255, 255),
            ])
            self.crack_lines.append((x1, y1, x2, y2, color))

    # -----------------------------------------------------------------------
    def draw(self, surface):
        shake_x = int(math.sin(self.timer * 40) * self.screen_shake)
        shake_y = int(math.cos(self.timer * 35) * self.screen_shake * 0.5)

        self._draw_background(surface, shake_x, shake_y)

        if self.phase == "door":
            self._draw_door(surface)
        elif self.phase == "enter":
            self._draw_enter(surface)
        elif self.phase == "livingroom":
            self._draw_livingroom(surface)
        elif self.phase in ("puzzle", "solve_pause"):
            self._draw_puzzle(surface)
        elif self.phase == "outro":
            self._draw_outro(surface)
        elif self.phase == "ending":
            self._draw_ending(surface)

        if self.phase in ("puzzle", "solve_pause", "outro"):
            self._draw_cracks(surface)

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

        if self.warm_alpha > 0:
            w = pygame.Surface((RENDER_W, RENDER_H))
            w.fill((255, 220, 120))
            w.set_alpha(int(self.warm_alpha))
            surface.blit(w, (0, 0))

        if self.overlay_alpha > 0:
            self.overlay.set_alpha(int(self.overlay_alpha))
            surface.blit(self.overlay, (0, 0))

    def _draw_background(self, surface, shake_x=0, shake_y=0):
        if self.phase == "door":
            bg = pygame.transform.scale(self.img_door, (RENDER_W, RENDER_H))
        elif self.phase == "livingroom":
            bg = pygame.transform.scale(self.img_livingroom, (RENDER_W, RENDER_H))
        else:
            bg = pygame.transform.scale(self.bg_interior, (RENDER_W, RENDER_H))

        if self.bg_flicker > 0:
            bg = bg.copy()
            f = pygame.Surface((RENDER_W, RENDER_H))
            f.fill((140, 100, 200))
            f.set_alpha(int(self.bg_flicker * 160))
            bg.blit(f, (0, 0))

        surface.blit(bg, (shake_x, shake_y))

        if self.phase == "door" and self.warm_light > 0:
            glow = pygame.Surface((RENDER_W, RENDER_H))
            glow.fill((255, 200, 80))
            glow.set_alpha(int(self.warm_light))
            surface.blit(glow, (0, 0))

        # Photo frame with image — reappears during resolution
        if self.frame_alpha > 0:
            photo = pygame.transform.scale(self.img_frame_photo,
                                           (self.frame_rect.w, self.frame_rect.h))
            photo.set_alpha(int(self.frame_alpha))
            surface.blit(photo, self.frame_rect)

            border_surf = pygame.Surface((self.frame_rect.w, self.frame_rect.h),
                                         pygame.SRCALPHA)
            pygame.draw.rect(border_surf, (*WARM_GOLD, int(self.frame_alpha)),
                             border_surf.get_rect(), 2)
            surface.blit(border_surf, self.frame_rect)

        self._draw_scanlines(surface)

    def _draw_door(self, surface):
        door_w, door_h = 40, 70
        door_x = RENDER_W // 2 - door_w // 2
        door_y = RENDER_H // 2 - door_h // 2 + 10

        pygame.draw.rect(surface, (60, 45, 30),
                         (door_x, door_y, door_w, door_h))
        pygame.draw.rect(surface, (100, 80, 50),
                         (door_x, door_y, door_w, door_h), 3)

        pygame.draw.circle(surface, WARM_GOLD,
                           (door_x + door_w - 6, door_y + door_h // 2), 3)

        if self.warm_light > 0:
            leak = pygame.Surface((door_w - 4, 3), pygame.SRCALPHA)
            leak.fill((255, 220, 100, int(self.warm_light)))
            surface.blit(leak, (door_x + 2, door_y + door_h - 2))

        if self.door_line_alpha > 0:
            txt = self.font_body.render(DOOR_LINES[0], False, WARM_WHITE)
            txt.set_alpha(int(self.door_line_alpha))
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               door_y - 20))

        hint = self.font_hint.render("SPACE to enter", False, (80, 75, 90))
        surface.blit(hint, (RENDER_W // 2 - hint.get_width() // 2, RENDER_H - 12))

    def _draw_enter(self, surface):
        dark = pygame.Surface((RENDER_W, RENDER_H))
        dark.fill(BLACK)
        dark.set_alpha(120)
        surface.blit(dark, (0, 0))

        y_start  = RENDER_H // 2 - len(ENTER_LINES) * 10
        line_gap = 16

        for i, line in enumerate(self.enter_shown):
            color = (200, 100, 100) if i >= 3 else WARM_WHITE
            txt   = self.font_body.render(line, False, color)
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + i * line_gap))

        if self.enter_index < len(ENTER_LINES):
            color = (200, 100, 100) if self.enter_index >= 3 else WARM_WHITE
            txt   = self.font_body.render(ENTER_LINES[self.enter_index],
                                          False, color)
            txt.set_alpha(int(self.enter_alpha))
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + len(self.enter_shown) * line_gap))

        hint = self.font_hint.render("SPACE to continue", False, (80, 75, 90))
        surface.blit(hint, (RENDER_W // 2 - hint.get_width() // 2, RENDER_H - 12))

    def _draw_livingroom(self, surface):
        # Living room is already drawn as the background in _draw_background.
        # Just add scanlines — background handles the image.
        pass

    def _draw_puzzle(self, surface):
        lbl_l = self.font_label.render("Memories", False, (140, 135, 155))
        surface.blit(lbl_l, (LEFT_X - lbl_l.get_width() // 2, 10))

        lbl_r = self.font_label.render("The journey", False, (140, 135, 155))
        surface.blit(lbl_r, (RIGHT_X - lbl_r.get_width() // 2, 10))

        pygame.draw.line(surface, (60, 55, 75),
                         (DIVIDER, 8), (DIVIDER, RENDER_H - 8), 1)

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

            if bubble.glitching:
                border = (220, 80, 80) if int(bubble.glitch_timer * 12) % 2 == 0 \
                         else (180, 170, 220)
                tcolor = (220, 130, 80)

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

    def _draw_cracks(self, surface):
        for x1, y1, x2, y2, color in self.crack_lines:
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), 1)
            mid_x = (x1 + x2) // 2
            mid_y = (y1 + y2) // 2
            pygame.draw.line(surface, color,
                             (mid_x, mid_y),
                             (mid_x + random.randint(-15, 15),
                              mid_y + random.randint(-10, 10)), 1)

    def _draw_outro(self, surface):
        # Background: dark bedroom after "Is this home?", thinkitis image last
        if "I think it is." in self.outro_shown:
            bg = pygame.transform.scale(self.img_thinkitis, (RENDER_W, RENDER_H))
        elif "Is this home?" in self.outro_shown or self.outro_index >= 1:
            bg = pygame.transform.scale(self.bg_bedroom_dark, (RENDER_W, RENDER_H))
        else:
            bg = pygame.transform.scale(self.img_ishome, (RENDER_W, RENDER_H))
        surface.blit(bg, (0, 0))

        dark = pygame.Surface((RENDER_W, RENDER_H))
        dark.fill(BLACK)
        dark.set_alpha(100)
        surface.blit(dark, (0, 0))

        y_start  = RENDER_H // 2 - 28
        line_gap = 22

        for i, line in enumerate(self.outro_shown):
            if not line:
                continue
            color = WARM_GOLD if line == "I think it is." else WARM_WHITE
            txt   = self.font_body.render(line, False, color)
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + i * line_gap))

        if self.outro_index < len(OUTRO_LINES):
            line = OUTRO_LINES[self.outro_index]
            if line:
                color = WARM_GOLD if line == "I think it is." else WARM_WHITE
                txt   = self.font_body.render(line, False, color)
                txt.set_alpha(int(self.outro_alpha))
                surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                                   y_start + len(self.outro_shown) * line_gap))

    def _draw_ending(self, surface):
        dark = pygame.Surface((RENDER_W, RENDER_H))
        dark.fill(BLACK)
        dark.set_alpha(int(self.end_darken))
        surface.blit(dark, (0, 0))

        y_start  = RENDER_H // 2 - len(ENDING_LINES) * 7
        line_gap = 14

        for i, line in enumerate(self.ending_shown):
            if not line:
                continue
            color = WARM_GOLD if i >= 4 else (180, 170, 190)
            txt   = self.font_ending.render(line, False, color)
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + i * line_gap))

        if self.ending_index < len(ENDING_LINES):
            line = ENDING_LINES[self.ending_index]
            if line:
                color = WARM_GOLD if self.ending_index >= 4 else (180, 170, 190)
                txt   = self.font_ending.render(line, False, color)
                txt.set_alpha(int(self.ending_alpha))
                surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                                   y_start + len(self.ending_shown) * line_gap))

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