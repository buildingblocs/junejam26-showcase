# Math Garden — team P5 (BuildingBloCS June Jam 2026).
#
# The submitted game.py had the real game accidentally nested inside a leftover
# "Pygame Sample" bouncing-ball loop, and used pyttsx3 for text-to-speech. For
# the browser build the bouncing-ball wrapper is removed (it was never part of
# the game) and pyttsx3 is dropped (not available in the WASM runtime; the
# original already degraded to silent when it was missing). Game logic is
# otherwise unchanged, with the main loop made async for pygbag.

import asyncio
import pygame
import random
import time

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Math Garden")

FONT = pygame.font.SysFont("arial", 32)
SMALL = pygame.font.SysFont("arial", 22)
BIG = pygame.font.SysFont("arial", 45)

WHITE = (255, 254, 238)
GREEN = (0, 255, 0)
BLUE = (70, 130, 255)
YELLOW = (255, 220, 50)
BLACK = (0, 0, 0)
BROWN = (255, 254, 238)
PURPLE = (137, 69, 133)

# pyttsx3 isn't available in the browser runtime; the original game already
# treated text-to-speech as optional, so it stays off here.
TTS = False


class QuestionGenerator:
    def __init__(self, level=1):
        self.level = level

    def generate(self):
        ops = ["+", "-"]
        if self.level >= 2:
            ops.append("*")
        if self.level >= 4:
            ops.append("/")

        op = random.choice(ops)

        if op == "+":
            a = random.randint(0, 10 + self.level * 5)
            b = random.randint(0, 10 + self.level * 5)
            ans = a + b
        elif op == "-":
            a = random.randint(0, 20 + self.level * 5)
            b = random.randint(0, a)
            ans = a - b
        elif op == "*":
            a = random.randint(1, 5 + self.level)
            b = random.randint(1, 5 + self.level)
            ans = a * b
        else:
            b = random.randint(1, 5)
            ans = random.randint(1, 10 + self.level)
            a = ans * b

        text = f"{a} {op} {b} = ?"

        choices = [ans]
        while len(choices) < 4:
            x = ans + random.randint(-10, 10)
            if x >= 0 and x not in choices:
                choices.append(x)
        random.shuffle(choices)

        return text, ans, choices


class Garden:
    def __init__(self):
        self.flowers = 0

    def grow(self):
        self.flowers += 1

    def draw(self):
        pygame.draw.rect(screen, BROWN, (0, 500, 900, 100))
        for i in range(self.flowers):
            x = 50 + (i % 12) * 70
            y = 470 - (i // 12) * 60
            pygame.draw.line(screen, GREEN, (x, y), (x, y + 40), 5)
            pygame.draw.circle(screen, YELLOW, (x, y), 15)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect, border_radius=12)
        t = FONT.render(self.text, True, WHITE)
        screen.blit(t, (self.rect.x + 20, self.rect.y + 20))

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class Game:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.streak = 0

        self.time_limit = 20
        self.start_time = time.time()

        self.generator = QuestionGenerator()
        self.garden = Garden()

        self.question = ""
        self.answer = 0
        self.choices = []
        self.buttons = []
        self.new_question()

        self.tts = None

    def speak(self, text):
        # Text-to-speech is unavailable in the browser build; no-op.
        return

    def new_question(self):
        self.question, self.answer, self.choices = self.generator.generate()
        self.start_time = time.time()
        self.buttons = []
        for i, c in enumerate(self.choices):
            self.buttons.append(
                Button(100 + i % 2 * 350, 250 + i // 2 * 100, 250, 70, f"{i+1}. {c}")
            )

    def correct(self):
        self.streak += 1
        points = 10 + self.streak * 2
        self.score += points
        self.garden.grow()
        if self.streak % 5 == 0:
            self.level = min(10, self.level + 1)
            self.generator.level = self.level

    def wrong(self):
        self.streak = 0
        self.score = max(0, self.score - 5)

    def draw(self):
        screen.fill(WHITE)
        title = BIG.render(" Math Garden", True, PURPLE)
        screen.blit(title, (30, 20))

        stats = SMALL.render(
            f"Level {self.level}   Score {self.score}   Streak {self.streak}",
            True, BLACK,
        )
        screen.blit(stats, (40, 90))

        q = FONT.render(self.question, True, BLACK)
        screen.blit(q, (475, 71))

        remaining = max(0, self.time_limit - (time.time() - self.start_time))
        pygame.draw.rect(screen, BLACK, (400, 41, 300, 20))
        pygame.draw.rect(screen, GREEN, (400, 41, 300 * remaining / self.time_limit, 20))

        for b in self.buttons:
            b.draw()

        self.garden.draw()

    async def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, b in enumerate(self.buttons):
                        if b.clicked(event.pos):
                            if self.choices[i] == self.answer:
                                self.correct()
                            else:
                                self.wrong()
                            self.new_question()

            if time.time() - self.start_time > self.time_limit:
                self.wrong()
                self.new_question()

            self.draw()
            pygame.display.update()
            clock.tick(60)
            await asyncio.sleep(0)

        pygame.quit()


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
