import pygame

def run_pause_overlay(screen, events, mouse_pos, font_title, font_button):
    """Draws a blur-effect dimming layer and intercepts mouse selections while paused."""
    sw, sh = screen.get_size()
    
    # 1. Create a semi-transparent dark dimming layer over the current frozen gameplay frames
    dim_surface = pygame.Surface((sw, sh), pygame.SRCALPHA)
    dim_surface.fill((5, 5, 10, 185)) # 185/255 opacity darkness alpha
    screen.blit(dim_surface, (0, 0))

    # 2. Build the centralized pause menu dialog box container
    box_w, box_h = 420, 300
    box_rect = pygame.Rect((sw - box_w) // 2, (sh - box_h) // 2, box_w, box_h)
    pygame.draw.rect(screen, (28, 28, 38), box_rect, border_radius=14)
    pygame.draw.rect(screen, (90, 95, 125), box_rect, width=2, border_radius=14)

    # 3. Text Header Layout
    p_title = font_title.render("GAME PAUSED", True, (255, 230, 150))
    screen.blit(p_title, p_title.get_rect(center=(sw // 2, box_rect.y + 50)))

    # 4. Button Boundaries
    btn_w, btn_h = 320, 46
    resume_rect = pygame.Rect((sw - btn_w) // 2, box_rect.y + 120, btn_w, btn_h)
    quit_rect = pygame.Rect((sw - btn_w) // 2, box_rect.y + 190, btn_w, btn_h)

    # 5. Check button hovering modifications
    res_hover = resume_rect.collidepoint(mouse_pos)
    quit_hover = quit_rect.collidepoint(mouse_pos)

    pygame.draw.rect(screen, (55, 70, 100) if res_hover else (40, 45, 65), resume_rect, border_radius=6)
    pygame.draw.rect(screen, (110, 55, 55) if quit_hover else (70, 40, 45), quit_rect, border_radius=6)

    # Render Button Labels
    t_res = font_button.render("RESUME GAME [SPACEBAR]", True, (240, 240, 255))
    t_quit = font_button.render("QUIT TO SELECT TERMINAL", True, (240, 240, 255))
    
    screen.blit(t_res, t_res.get_rect(center=resume_rect.center))
    screen.blit(t_quit, t_quit.get_rect(center=quit_rect.center))

    # 6. Evaluate Mouse Interactions
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if resume_rect.collidepoint(mouse_pos):
                print("[PAUSE_ROUTER] Resuming active instance.")
                return "unpause"
            elif quit_rect.collidepoint(mouse_pos):
                print("[PAUSE_ROUTER] Abandoning timeline run.")
                return "quit"

    return "stay_paused"