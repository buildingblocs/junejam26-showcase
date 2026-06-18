import pygame

# --- THE STORY SCRIPT DATA ---
DIALOGUE = [
    "....",
    "Where... where am I?",
    "Everything is pitch black.",
    "???: Hello.",
    "AAAA Who are you?",
    "and why can't I see you??",
    "???: I am you. You are in bed right now.",
    "Okay... that explains the darkness, but why can't I open my eyes??",
    "???: well...because im not letting you.",
    "...",
    "Well then let me!",
    "???: Look. There are things outside that want to hurt you.",
    "???: Before you awaken, you must learn to defend yourself in this dark space.",
    "???: Try moving your conscious spark around with W, A, S, D.",
    "???: Good. Now click your mouse to fire a burst of pure willpower.",
    "???: Destroying nightmares drops fragments. I've manifest some for you.",
    "???: Spend your fragments on upgrades before we break the sleep barrier.",
    "???: Your mind is armed. Now... it is time to wake up.",
    "FIGHT THE SLEEP LAYER! (SPAM SPACEBAR)"
]

def get_prompt_text(page, has_moved, has_fired, has_shopped, time_elapsed, cooldown):
    """Calculates exactly what structural objective instruction to show at the bottom."""
    if page == 13 and not has_moved:
        return "[ MOVE WITH WASD TO PROGRESS ]", (255, 165, 0)
    elif page == 14 and not has_fired:
        return "[ CLICK ANYWHERE TO FIRE SHOT ]", (255, 100, 100)
    elif page == 16 and not has_shopped:
        return "[ PURCHASE AN UPGRADE TO COMPLETE TRAINING ]", (255, 215, 0)
    elif time_elapsed < cooldown:
        return "... PLEASE WAIT ...", (80, 90, 100)
    elif page < len(DIALOGUE) - 1:
        return "PRESS ENTER TO CONTINUE", (110, 120, 150)
    else:
        return "[ PRESS SPACEBAR TO WAKE UP ]", (100, 255, 100)

def can_advance_page(page, has_moved, has_fired, has_shopped):
    """Guards the dialogue so players cannot skip ahead without doing the actions."""
    if page == 13 and not has_moved: 
        return False
    if page == 14 and not has_fired: 
        return False
    if page == 16 and not has_shopped: 
        return False
    if page >= len(DIALOGUE) - 1: 
        return False
    return True