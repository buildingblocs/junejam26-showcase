import sys
import asyncio
import pygame
from core.game import Game


async def main() -> None:
    # Pre-init mixer before pygame.init() so the sample format is set correctly
    # for programmatic sound generation in core/audio.py.
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.init()
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
