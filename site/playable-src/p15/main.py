# main.py — browser (pygbag) port of "Finding the Way Home" (P15).
# Identical to the submitted entrypoint except for the async wrapper and the
# per-frame `await asyncio.sleep(0)` required to cooperate with the browser
# event loop. All gameplay, scenes and assets are unchanged.
import asyncio
import pygame
from settings import SCREEN_W, SCREEN_H, RENDER_W, RENDER_H, FPS, TITLE
from core.game_manager import GameManager


async def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    screen         = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    render_surface = pygame.Surface((RENDER_W, RENDER_H))
    pygame.display.set_caption(TITLE)

    clock   = pygame.time.Clock()
    manager = GameManager(render_surface)
    manager.push_scene("menu")

    running = True
    while running:
        await asyncio.sleep(0)
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.handle_event(event)

        manager.update(dt)
        manager.draw()

        pygame.transform.scale(render_surface, (SCREEN_W, SCREEN_H), screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
