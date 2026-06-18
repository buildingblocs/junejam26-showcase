import asyncio
import pygame
import sys
import os
is_dreaming = True
pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My Cosmic Game Hub")
clock = pygame.time.Clock()

# --- IMPORT ALL MODULES ---
import LevelSelect
import startscreen  # <-- Added new Start Screen link
import pause
import level1
import level2  
import level3  

current_state = "START_SCREEN"  # <-- Game now boots up here first!
title_sys = startscreen.TitleScreen() # <-- Instantiate the title logic
active_level_module = None  
title_timer = 0.0

async def main():
    global current_state, active_level_module, title_timer

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        title_timer += 0.05
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if current_state == "START_SCREEN":
            # Run title screen until player presses SPACEBAR
            start_signal = title_sys.run_cycle(screen, events, LevelSelect.font_title, LevelSelect.font_button, title_timer)
            if start_signal == "GO_TO_HUB":
                current_state = "LEVEL_SELECT"

        elif current_state == "LEVEL_SELECT":
            menu_signal = LevelSelect.run_level_select_cycle(screen, events, mouse_pos, title_timer)

            if menu_signal in ["LAUNCH_LEVEL_ONE", "LAUNCH_LEVEL_TWO", "LAUNCH_LEVEL_THREE"]:
                if menu_signal == "LAUNCH_LEVEL_ONE":
                    active_level_module = level1
                elif menu_signal == "LAUNCH_LEVEL_TWO":
                    active_level_module = level2
                elif menu_signal == "LAUNCH_LEVEL_THREE":
                    active_level_module = level3

                # --- UNIVERSAL RESET FOR THE SELECTED LEVEL ---
                active_level_module.page = 0
                active_level_module.is_paused = False
                active_level_module.has_moved = False
                active_level_module.has_fired = False
                active_level_module.bullets = []

                if hasattr(active_level_module, 'eyelids') and active_level_module.eyelids is not None:
                    active_level_module.eyelids.reset()
                if hasattr(active_level_module, 'health_sys') and active_level_module.health_sys is not None:
                    active_level_module.health_sys.reset()
                if hasattr(active_level_module, 'shop_sys') and active_level_module.shop_sys is not None:
                    active_level_module.shop_sys.reset()

                current_state = "GAMEPLAY_LOOP"

        elif current_state == "GAMEPLAY_LOOP":
            if not active_level_module.is_paused:
                active_level_module.handle_events(events)
                active_level_module.run_level_cycle(screen, LevelSelect.font_title, LevelSelect.font_button, SCREEN_WIDTH, SCREEN_HEIGHT, LevelSelect.COLOUR_TEXT)

                if hasattr(active_level_module, 'health_sys') and active_level_module.health_sys is not None:
                    if active_level_module.health_sys.check_negative_hp():
                        print(f"[GAME OVER] Defeated in active level timeline.")
                        LevelSelect.game_state = "level_select"
                        current_state = "LEVEL_SELECT"
            else:
                active_level_module.run_level_cycle(screen, LevelSelect.font_title, LevelSelect.font_button, SCREEN_WIDTH, SCREEN_HEIGHT, LevelSelect.COLOUR_TEXT)

                pause_signal = pause.run_pause_overlay(screen, events, mouse_pos, LevelSelect.font_title, LevelSelect.font_button)
                if pause_signal == "unpause":
                    active_level_module.is_paused = False
                elif pause_signal == "quit":
                    active_level_module.is_paused = False
                    LevelSelect.game_state = "level_select"
                    current_state = "LEVEL_SELECT"

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())