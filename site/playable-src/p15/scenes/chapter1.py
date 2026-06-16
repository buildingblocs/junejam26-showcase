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

CORRECT_BUBBLES = [
    "Wake up",
    "Get dressed",
    "Eat breakfast",
    "Leave home",
]

DECOY_BUBBLES = [
    "Go to sleep",
    "Stay inside",
    "It's evening",
]

INTRO_LINES = [
    "A normal morning.",
    "At least...",
    "it should be.",
]

OUTRO_LINES = [
    "You step outside.",
    "You've walked this path before.",
    "Haven't you?",
]

# Layout constants
LEFT_X  = RENDER_W // 4
RIGHT_X = RENDER_W * 3 // 4
DIVIDER = RENDER_W // 2

BUBBLE_W = 140
BUBBLE_H = 22
SLOT_W   = 150
SLOT_H   = 22


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
        self.x       = x
        self.y       = y
        self.index   = index
        self.filled  = False
        self.content = None
        self.w       = SLOT_W
        self.h       = SLOT_H
        self.flash   = 0.0

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2,
                           self.w, self.h)


class Chapter1Scene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)

        self.font_header = self.assets.get_font(16)
        self.font_label  = self.assets.get_font(12)
        self.font_body   = self.assets.get_font(8)
        self.font_hint   = self.assets.get_font(6)

        self.bg              = self.assets.get_image("backgrounds/bedroom")
        self.img_morning     = self.assets.get_image("scenes/ch1_morning")
        self.img_outside     = self.assets.get_image("scenes/ch1_outside")
        self.img_path        = self.assets.get_image("scenes/ch1_path")
        self.img_livingroom  = self.assets.get_image("backgrounds/living_room")
        self.img_frame_photo = self.assets.get_image("ui/frame_photo")

        self.phase       = "intro"
        self.timer       = 0.0
        self.phase_timer = 0.0

        self.morning_alpha = 0.0

        self.current_line = 0
        self.line_alpha   = 0.0
        self.lines_shown  = []

        self.overlay       = pygame.Surface((RENDER_W, RENDER_H))
        self.overlay.fill(BLACK)
        self.overlay_alpha = 255
        self.fading_out    = False

        # Blur starts at 0 during intro — only kicks in at puzzle start
        self.blur_alpha  = 0
        self.frame_alpha = 0.0
        self.frame_rect  = pygame.Rect(RENDER_W - 55, 24, 48, 54)

        self.bubbles     = []
        self.slots       = []
        self.dragged     = None
        self.solved      = False
        self.wrong_flash = 0.0

        self.outro_line  = 0
        self.outro_alpha = 0.0
        self.outro_shown = []

    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    def update(self, dt):
        self.timer       += dt
        self.phase_timer += dt

        if self.overlay_alpha > 0 and not self.fading_out:
            self.overlay_alpha = max(0, self.overlay_alpha - 150 * dt)

        if self.fading_out:
            self.overlay_alpha = min(255, self.overlay_alpha + 150 * dt)
            if self.overlay_alpha >= 255:
                self.manager.replace_scene("ch2")
            return

        # Blur fades IN when puzzle starts, clears during livingroom and outro
        if self.phase == "puzzle":
            self.blur_alpha = min(180, self.blur_alpha + 80 * dt)
        elif self.phase in ("livingroom", "outro"):
            self.blur_alpha = max(0, self.blur_alpha - 60 * dt)

        self.frame_alpha = min(200, self.frame_alpha + 40 * dt)
        self.wrong_flash = max(0, self.wrong_flash - 200 * dt)

        if self.phase == "intro":
            self._update_intro(dt)
        elif self.phase == "puzzle":
            self._update_puzzle(dt)
        elif self.phase == "livingroom":
            self._update_livingroom(dt)
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

        all_texts = list(CORRECT_BUBBLES) + list(DECOY_BUBBLES)
        random.shuffle(all_texts)

        total    = len(all_texts)
        top_pad  = 36
        bot_pad  = 20
        usable_h = RENDER_H - top_pad - bot_pad
        gap      = usable_h // total

        for i, text in enumerate(all_texts):
            is_decoy = text in DECOY_BUBBLES
            y = top_pad + i * gap + gap // 2
            self.bubbles.append(Bubble(text, LEFT_X, y, is_decoy=is_decoy))

        num_slots = len(CORRECT_BUBBLES)
        s_top     = 50
        s_bot     = RENDER_H - 24
        s_usable  = s_bot - s_top
        s_gap     = s_usable // num_slots

        for i in range(num_slots):
            y = s_top + i * s_gap + s_gap // 2
            self.slots.append(Slot(RIGHT_X, y, i))

    def _update_puzzle(self, dt):
        self.morning_alpha = min(255, self.morning_alpha + 80 * dt)

        for bubble in self.bubbles:
            if bubble.alive:
                bubble.update(dt, self.timer)

        if not self.solved and all(s.filled for s in self.slots):
            self.solved      = True
            self.phase       = "livingroom"
            self.phase_timer = 0.0

    def _update_livingroom(self, dt):
        # Show living room for 3 seconds, then move to outro
        if self.phase_timer > 3.0:
            self.phase       = "outro"
            self.phase_timer = 0.0

    def _update_outro(self, dt):
        if self.outro_line < len(OUTRO_LINES):
            self.outro_alpha = min(255, self.outro_alpha + 80 * dt)
            if self.outro_alpha >= 255:
                self.phase_timer += dt
                if self.phase_timer > 2.0:
                    self.outro_shown.append(OUTRO_LINES[self.outro_line])
                    self.outro_line  += 1
                    self.outro_alpha  = 0
                    self.phase_timer  = 0.0
        else:
            if self.phase_timer > 2.0:
                self.fading_out = True

    def _try_place_bubble(self, bubble, mx, my):
        for slot in self.slots:
            if slot.get_rect().collidepoint(mx, my) and not slot.filled:
                if bubble.text == CORRECT_BUBBLES[slot.index]:
                    slot.filled   = True
                    slot.content  = bubble
                    slot.flash    = 1.0
                    bubble.placed = True
                    bubble.alive  = False
                else:
                    slot.flash       = -1.0
                    self.wrong_flash = 255
                    bubble.x         = bubble.start_x
                    bubble.y         = bubble.start_y
                return
        bubble.x = bubble.start_x
        bubble.y = bubble.start_y

    # ------------------------------------------------------------------
    def draw(self, surface):
        self._draw_background(surface)

        if self.phase == "intro":
            self._draw_intro(surface)
        elif self.phase == "puzzle":
            self._draw_puzzle(surface)
        elif self.phase == "livingroom":
            self._draw_livingroom(surface)
        elif self.phase == "outro":
            self._draw_outro(surface)

        if self.wrong_flash > 0:
            flash_surf = pygame.Surface((RENDER_W, RENDER_H))
            flash_surf.fill((180, 30, 30))
            flash_surf.set_alpha(int(self.wrong_flash * 0.4))
            surface.blit(flash_surf, (0, 0))

        if self.overlay_alpha > 0:
            self.overlay.set_alpha(int(self.overlay_alpha))
            surface.blit(self.overlay, (0, 0))

    def _draw_background(self, surface):
        # Layer 1: bedroom — always shown (visible alone during intro)
        bg = pygame.transform.scale(self.bg, (RENDER_W, RENDER_H))
        surface.blit(bg, (0, 0))

        # Layer 2: img_morning fades in when puzzle starts only
        if self.phase == "puzzle" and self.morning_alpha > 0:
            morning = pygame.transform.scale(self.img_morning, (RENDER_W, RENDER_H))
            morning.set_alpha(int(self.morning_alpha))
            surface.blit(morning, (0, 0))

        # Layer 3: blur overlay — only during puzzle (fades in at start)
        if self.blur_alpha > 0:
            blur = pygame.Surface((RENDER_W, RENDER_H))
            blur.fill((200, 195, 210))
            blur.set_alpha(int(self.blur_alpha))
            surface.blit(blur, (0, 0))

        # Layer 4: photo frame with image — fades in throughout
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

    def _draw_intro(self, surface):
        # Dark overlay so text is readable over bedroom
        dark = pygame.Surface((RENDER_W, RENDER_H))
        dark.fill(BLACK)
        dark.set_alpha(110)
        surface.blit(dark, (0, 0))

        y_start  = RENDER_H // 2 - 24
        line_gap = 20

        for i, line in enumerate(self.lines_shown):
            txt = self.font_body.render(line, False, WARM_WHITE)
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + i * line_gap))
        if self.current_line < len(INTRO_LINES):
            txt = self.font_body.render(INTRO_LINES[self.current_line],
                                        False, WARM_WHITE)
            txt.set_alpha(int(self.line_alpha))
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + len(self.lines_shown) * line_gap))

    def _draw_puzzle(self, surface):
        # Panel labels
        lbl_left = self.font_label.render("Memories", False, (140, 135, 155))
        surface.blit(lbl_left, (LEFT_X - lbl_left.get_width() // 2, 10))

        lbl_right = self.font_label.render("This morning...", False, (140, 135, 155))
        surface.blit(lbl_right, (RIGHT_X - lbl_right.get_width() // 2, 10))

        pygame.draw.line(surface, (60, 55, 75),
                         (DIVIDER, 8), (DIVIDER, RENDER_H - 8), 1)

        # Slots
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

            if slot.filled and slot.content:
                txt = self.font_body.render(slot.content.text, False, WARM_GOLD)
                surface.blit(txt, (rect.x + 16,
                                   rect.centery - txt.get_height() // 2))

        # Bubbles
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

            bubble_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(bubble_surf, (*color, 220),
                             bubble_surf.get_rect(), border_radius=4)
            pygame.draw.rect(bubble_surf, (*border, 255),
                             bubble_surf.get_rect(), 1, border_radius=4)
            bubble_surf.set_alpha(int(bubble.alpha))
            surface.blit(bubble_surf, rect)

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

    def _draw_livingroom(self, surface):
        # Full-screen living room image for 3 seconds before outro
        bg = pygame.transform.scale(self.img_livingroom, (RENDER_W, RENDER_H))
        surface.blit(bg, (0, 0))
        self._draw_scanlines(surface)

    def _draw_outro(self, surface):
        # Pick image based on which outro line we're on
        if len(self.outro_shown) >= 2 or self.outro_line >= 2:
            bg = pygame.transform.scale(self.img_path, (RENDER_W, RENDER_H))
        else:
            bg = pygame.transform.scale(self.img_outside, (RENDER_W, RENDER_H))
        surface.blit(bg, (0, 0))

        dark = pygame.Surface((RENDER_W, RENDER_H))
        dark.fill(BLACK)
        dark.set_alpha(160)
        surface.blit(dark, (0, 0))

        y_start  = RENDER_H // 2 - 24
        line_gap = 20
        for i, line in enumerate(self.outro_shown):
            txt = self.font_body.render(line, False, WARM_WHITE)
            surface.blit(txt, (RENDER_W // 2 - txt.get_width() // 2,
                               y_start + i * line_gap))
        if self.outro_line < len(OUTRO_LINES):
            txt = self.font_body.render(OUTRO_LINES[self.outro_line],
                                        False, WARM_WHITE)
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