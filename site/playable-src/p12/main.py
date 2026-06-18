import math
import random
import asyncio
import pygame

pygame.init()
game_state = "menu"
async def run_game():

    pygame.mixer.init()
    #channel = None

    global game_state
    # -------Sound Effects--------
    dropbox_sound = pygame.mixer.Sound("bloop.ogg")
    dropbox_sound.set_volume(1)
    plate_sound = pygame.mixer.Sound("platesound.ogg")
    oven_sound = pygame.mixer.Sound("oven.ogg")
    oven_sound.set_volume(0.5)
    OVEN_SOUND_FINISHED = pygame.USEREVENT + 1
    smack_sound = pygame.mixer.Sound("smack.ogg")
    smack_sound.set_volume(0.5)
    wipe_sound = pygame.mixer.Sound("wipe.ogg")
    wipe_sound.set_volume(0.5)
    background_music = pygame.mixer.Sound("background_music.ogg")
    background_music.set_volume(0.4)
    # -------Game Setup--------
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((900, 500))
    screen_colour = (151, 186, 232)
    screen.fill(screen_colour)

    hand_img = pygame.image.load("hand.png")
    hand_img = pygame.transform.scale(hand_img, (500, 400))
    hand_rect = hand_img.get_rect()

    closed_hand = pygame.image.load("handclosed.png")
    closed_hand = pygame.transform.scale(closed_hand, (500, 400))

    current_hand = hand_img

    max_time = 45
    game_timer = 45     

    font = pygame.font.Font(None, 50)

    timerbar_img = pygame.image.load("timerbar.png")
    timerbar_img = pygame.transform.scale(timerbar_img, (205, 200))
    timerbar_rect = timerbar_img.get_rect()
    timerbar_rect.center = (85, 55)

    dropbox_img = pygame.image.load("dropbox.png")
    dropbox_img = pygame.transform.scale(dropbox_img, (150, 150))
    dropbox_rect = dropbox_img.get_rect()
    dropbox_rect.center = (825, 425)

    cloth_img = pygame.image.load("cloth.png")
    cloth_img = pygame.transform.scale(cloth_img, (100, 100))
    cloth_rect = cloth_img.get_rect()
    cloth_rect.center = (450, 450)

    plates = []
    dropbox_item_list = []
    plate_types = ["plate.png", "plate(1).png", "plate(2).png", "plate(3).png"]

    plates_stolen = 0

    class Plates:

        def __init__(self):
            self.carried_by_baby = None
            self.dropbox_display_offset = 5
            self.is_dragging = False
            self.drag_speed = 30
            self.img = pygame.image.load(plate_types[random.randint(0, 3)])
            self.img = pygame.transform.scale(self.img, (100, 100))
            self.pos_x = random.randint(50, 850)
            self.pos_y = random.randint(50, 450)
            while (750 < self.pos_x < 900) and (350 < self.pos_y < 500):
                self.pos_x = random.randint(50, 850)
                self.pos_y = random.randint(50, 450)
            self.rect = self.img.get_rect()
            self.rect.center = (self.pos_x, self.pos_y)
            plates.append(self)

        def drop_into_dropbox(self, dropbox_rect, dropbox_item_list):
            if not self.is_dragging and self.rect.colliderect(dropbox_rect):
                if self not in dropbox_item_list:
                    dropbox_item_list.append(self)
                    if self in plates:
                        plates.remove(self)
          
                    dropbox_sound.play()
                    plate_sound.play()
                    if len(dropbox_item_list) < 9:
                        self.pos_x = dropbox_rect.center[0] - self.dropbox_display_offset * (len(dropbox_item_list) - 1)
                        self.pos_y = dropbox_rect.center[1] - self.dropbox_display_offset * (len(dropbox_item_list) - 1)
                    else:
                        self.pos_x = dropbox_rect.center[0] + self.dropbox_display_offset * (len(dropbox_item_list) - 1) + 3
                        self.pos_y = dropbox_rect.center[1] + self.dropbox_display_offset * (len(dropbox_item_list) - 1) + 3
                    self.rect.center = (self.pos_x, self.pos_y)
            if self.rect.colliderect(dropbox_rect):
                self.is_dragging = False
            return dropbox_item_list

        def follow_baby_hand(self, babyhand):

            if self in dropbox_item_list:
                return
            if self != babyhand.target_plate:
                return

            if self.carried_by_baby is None:
                if self.rect.colliderect(babyhand.babyhand_rect):
                    self.carried_by_baby = babyhand
                    babyhand.direction = "backward"

            if self.carried_by_baby == babyhand:
                if isinstance(babyhand, FBabyHand):
                    self.pos_x = babyhand.babyhand_rect.right - 80
                else:
                    self.pos_x = babyhand.babyhand_rect.left + 80

                self.pos_y = babyhand.babyhand_rect.centery
                self.rect.center = (self.pos_x, self.pos_y)

    for _ in range(random.randint(15,23)):
        Plates()
    starting_plate_count = len(plates)

    stain_types = ["stain.png", "stain(1).png", "stain(2).png"]
    stains = []

    STAINSPAWN_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(STAINSPAWN_EVENT, 2000)

    class Stain:

        def __init__(self): 
            self.stain_timer = 3
            self.img = pygame.image.load(stain_types[random.randint(0, 2)])
            self.img = pygame.transform.scale(self.img, (100, 100))
            self.pos_x = random.randint(50, 850)
            self.pos_y = random.randint(50, 450)
            while (750 < self.pos_x < 900) and (350 < self.pos_y < 500):
                self.pos_x = random.randint(50, 850)
                self.pos_y = random.randint(50, 450)
            self.rect = self.img.get_rect()
            self.rect.center = (self.pos_x, self.pos_y)
            stains.append(self)


    for _ in range(5):
        Stain()

    babyhands = []


    class FBabyHand:

        def __init__(self, target_plate, game_timer, max_time=120):
            self.condition = "pickup"
            self.direction = "forward"
            self.baby_hand_speed = (max_time - game_timer) * 0.2 + 2
            self.target_plate = target_plate
            self.babyhand_img = pygame.image.load("babyhand.png")
            self.babyhand_img = pygame.transform.scale(self.babyhand_img, (800,200))
            self.babyhand_img = pygame.transform.flip(self.babyhand_img, True, False)
            self.babyhand_rect = self.babyhand_img.get_rect()
            self.babyhand_rect.center = (-100, target_plate.pos_y)
            babyhands.append(self)

        def move(self, plates_stolen, plates=plates):

            if self.direction == "forward":
                self.babyhand_rect.x += self.baby_hand_speed
            elif self.direction == "backward":
                self.babyhand_rect.x -= self.baby_hand_speed

            if self.direction == "backward" and self.babyhand_rect.right < 0:
                babyhands.remove(self)
                plates_stolen += 1
                if self.target_plate in plates:
                    plates.remove(self.target_plate)
            return plates_stolen

    class BBabyHand:

        def __init__(self, target_plate, game_timer, max_time=120):
            self.condition = "pickup"
            self.direction = "forward"
            self.baby_hand_speed = (max_time - game_timer) * 0.2 + 2
            self.target_plate = target_plate
            self.babyhand_img = pygame.image.load("babyhand.png")
            self.babyhand_img = pygame.transform.scale(self.babyhand_img, (800,200))
            self.babyhand_rect = self.babyhand_img.get_rect()
            self.babyhand_rect.center = (1000, target_plate.pos_y)
            babyhands.append(self) 

        def move(self, plates_stolen, plates=plates):

            if self.direction == "forward":
                self.babyhand_rect.x -= self.baby_hand_speed
            elif self.direction == "backward":
                self.babyhand_rect.x += self.baby_hand_speed

            if self.direction == "backward" and self.babyhand_rect.left > 900:
                babyhands.remove(self) 
                plates_stolen += 1
                if self.target_plate in plates:
                    plates.remove(self.target_plate)
            return plates_stolen


    hand_spawn_timer = 0


    def execute_baby_hand(plates, dt):
        nonlocal hand_spawn_timer
        hand_spawn_timer += dt
        if hand_spawn_timer > 3.0: 
            hand_spawn_timer = 0
            active_plates = [
        p for p in plates
        if p not in dropbox_item_list
        and p.carried_by_baby is None
        and not p.is_dragging
    ]
            if active_plates and len(babyhands) == 0:
                selected_plate = random.choice(active_plates)
                if selected_plate.pos_x <= 450:
                    FBabyHand(selected_plate, game_timer, max_time)
                else:
                    BBabyHand(selected_plate, game_timer, max_time)

    def reset_game():
        nonlocal plates, stains, babyhands, plates_stolen, game_timer, dropbox_item_list
        nonlocal starting_plate_count
        starting_plate_count = len(plates)
    plates = []
    stains = []
    babyhands = []
    dropbox_item_list = []
    plates_stolen = 0
    game_timer = 45

    for _ in range(random.randint(15,23)):
        Plates()

    for _ in range(5):
        Stain()


    reset_game()
    if game_state == "menu":
        screen.fill((72,209,204))
        menu_text = font.render("Press I for instructions", True, (255, 255, 255))
        menu_text2 = font.render("Press S to start", True, (255, 255, 255))
        logo_img = pygame.image.load("logo.png") 
        logo_img = pygame.transform.scale(logo_img, (900, 800)) 
 
    while game_state == "menu":
        screen.blit(menu_text, (250, 330))
        screen.blit(menu_text2, (300, 380))
        screen.blit(logo_img, (-30, -200))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    game_state = "Instructions"
                elif event.key == pygame.K_s:
                    game_state = "Playing"
        await asyncio.sleep(0)

    while game_state == "Instructions":
        smaller_font = pygame.font.Font(None, 25)
        hand = pygame.image.load("hand.png")
        hand = pygame.transform.scale(hand, (1000,1000))
        plate = pygame.image.load("plate.png")
        plate = pygame.transform.scale(plate, (400, 400))
        screen.fill((72,209,204)) 
        screen.blit(plate, (500, 25))
        screen.blit(hand, (100, -150))
        instructions = [
            "The baby runs rampant again!",
            "1) Your goal is to clean up all the plates ",
            "before the brownies in the oven burn.",
            "",
            "2) Use your mouse to drag and drop plates ",
            "into the dropbox.(green box at bottom right)",
            "",
            "3) Beware of the baby using his hands and trying to steal ",
            "the plates(click to slap away)!",
            "if he steals 3 plates u lose :(",
            "but you will get a leeway of 1 plate stolen.",
            "",
            "4) Hold Shift to pick up cloth to wipe stains.",
            "",
            "5) Take note of the oven timer at the top left",
            " - if it runs out, the brownies will burn!",
            "Good luck and have fun!",
            "Press M to return to menu"
        ]
        for i, line in enumerate(instructions):
            instruction_text = smaller_font.render(line, True, (255, 255, 255))
            screen.blit(instruction_text, (25, 50 + i * 20))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    game_state = "menu"
                    #run_game()
        await asyncio.sleep(0)




    if game_state == "Playing":
        for plate in plates:
            if plate.rect.colliderect(dropbox_rect):
             print(
            "in box",
            plate in dropbox_item_list,
            plate.is_dragging
        )
        for plate in plates:
            if plate not in dropbox_item_list:
                pygame.draw.rect(screen, (255,0,0), plate.rect, 2)
        if len(dropbox_item_list) != len(set(dropbox_item_list)):
            print("DUPLICATE DETECTED!")
        background_music.play(-1)
    while game_state == "Playing":
        dt = clock.tick(60) / 1000.0
        is_clicking = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_clicking = True

                    for plate in plates:
                        if plate.rect.collidepoint(mouse_pos) and plate not in dropbox_item_list:
                            if not plate.is_dragging:
                                plate_sound.play()
                                plate.is_dragging = True
                            break

                    for babyhand in babyhands[:]:
                        if babyhand.babyhand_rect.collidepoint(mouse_pos):
                            smack_sound.play()
                            for plate in plates:
                                if plate.carried_by_baby == babyhand:
                                    plate.carried_by_baby = None

                                    if isinstance(babyhand, FBabyHand):
                                        plate.pos_x = babyhand.babyhand_rect.right - 80
                                    else:
                                        plate.pos_x = babyhand.babyhand_rect.left + 80

                                    plate.pos_y = babyhand.babyhand_rect.centery
                                    plate.rect.center = (plate.pos_x, plate.pos_y)

                            babyhands.remove(babyhand)
                            break

            elif event.type == OVEN_SOUND_FINISHED:
                game_state = "no time end screen"
                #if channel:
                   # channel.set_endevent(pygame.NOEVENT) 

            if not pygame.mouse.get_pressed()[0]:
                for plate in plates:
                    plate.is_dragging = False


            if event.type == STAINSPAWN_EVENT:
                if len(stains) < 15 and  (starting_plate_count -len(dropbox_item_list) ) and game_timer > 15:
                    Stain()


        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or mouse_buttons[0]:
            current_hand = closed_hand
        else:
            current_hand = hand_img

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            for stain in stains[:]:  
                if stain.rect.colliderect(cloth_rect):
                    wipe_sound.play()
                    stain.stain_timer -= dt * 10
                    if stain.stain_timer <= 0:
                        stains.remove(stain)
            if cloth_rect.collidepoint(mouse_pos):
                cloth_rect.center = mouse_pos

        for plate in plates:
            if plate.is_dragging:
                dx = mouse_pos[0] - plate.pos_x
                dy = mouse_pos[1] - plate.pos_y
                distance = math.hypot(dx, dy)
                if distance > 0:
                    if distance < plate.drag_speed:
                        plate.pos_x = mouse_pos[0]
                        plate.pos_y = mouse_pos[1]
                    else:
                        plate.pos_x += (dx / distance) * plate.drag_speed
                        plate.pos_y += (dy / distance) * plate.drag_speed
            plate.rect.center = (plate.pos_x, plate.pos_y)
            dropbox_item_list = plate.drop_into_dropbox(dropbox_rect, dropbox_item_list)

        if game_timer > 0:
            game_timer -= dt
            if game_timer <= 0:
                oven_sound.play()
                game_state = "no time end screen"
                background_music.stop()
                game_state = "no time end screen"

        minutes, seconds = divmod(int(max(0, game_timer)), 60)
        time_string = f"{minutes:02d}:{seconds:02d}"
        game_timer_text_surface = font.render(time_string, True, (255, 255, 255))
        game_timer_text_rect = game_timer_text_surface.get_rect(topleft=(17, 48))

        hand_rect = current_hand.get_rect(center=mouse_pos)
        if current_hand == closed_hand:
            hand_rect.x -= 180
            hand_rect.y -= 15


        execute_baby_hand(plates, dt)

        for babyhand in babyhands[:]:
            plates_stolen = babyhand.move(plates_stolen)


            for plate in plates:
                plate.follow_baby_hand(babyhand)
  

        cleaned = len(dropbox_item_list)
        lost = plates_stolen
        total = starting_plate_count

        if len(stains) == 0 and cleaned + lost >= total and plates_stolen <= 3:
            game_state = "win screen"

            game_state = "win screen"
            print("win")
            oven_sound.stop() 
            background_music.stop()
            
            game_state = "win screen" 

        if plates_stolen > 3:
            game_state = "baby stole too many plates end screen"
            background_music.stop()
        screen.fill(screen_colour)

        screen.fill(screen_colour)
        screen.blit(timerbar_img, timerbar_rect)
        screen.blit(dropbox_img, dropbox_rect)


        for stain in stains:
            screen.blit(stain.img, stain.rect)

        screen.blit(cloth_img, cloth_rect)
        screen.blit(game_timer_text_surface, game_timer_text_rect)
        for babyhand in babyhands:
            screen.blit(babyhand.babyhand_img, babyhand.babyhand_rect)
        for plate in plates:
            screen.blit(plate.img, plate.rect)
        for plate in dropbox_item_list:
            screen.blit(plate.img, plate.rect)
        screen.blit(current_hand, hand_rect)
        pygame.display.update()
        await asyncio.sleep(0)

    if game_state == "win screen":
        brownie_original = pygame.image.load("brownie.png")
        brownie_original = pygame.transform.scale(brownie_original, (200, 150))
        angle = 0
        clock.tick(60)
    while game_state == "win screen":
        screen.fill((152,251,152)) 
        end_text = font.render("Yay you cleaned up in time!", True, (255, 255, 255))
        end_text2 = font.render("Enjoy your brownies!", True, (255, 255, 255))
        end_text3 = font.render("press r to retry", True, (255, 255, 255))
        screen.blit(end_text, (225, 180))
        screen.blit(end_text2, (225, 230))
        screen.blit(end_text3, (225, 280))
        angle += 1

        brownie_img = pygame.transform.rotate(brownie_original, angle)

        screen.blit(brownie_img, (350, 300))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "quit"
                background_music.stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    pygame.event.clear(OVEN_SOUND_FINISHED)
                    game_state = "Playing"
                    oven_sound.stop()
                    reset_game()
                    return
                    #run_game()
        await asyncio.sleep(0)
    if game_state == "no time end screen":
        
        brownie_original = pygame.image.load("burnt_brownie.png")
        brownie_original = pygame.transform.scale(brownie_original, (200, 150))
        angle = 0 
        clock.tick(60)
    
    while game_state == "no time end screen":
        screen.fill((178,34,34))
        end_text = font.render("Time's Up! The brownies burned", True, (255, 255, 255))
        end_text2 = font.render("press r to restart", True, (255, 255, 255))
        screen.blit(end_text, (200, 230))
        screen.blit(end_text2, (250, 280))
        angle += 1

        brownie_img = pygame.transform.rotate(brownie_original, angle)

        brownie_rect = brownie_img.get_rect(center=(450, 350))

        screen.blit(brownie_img, (325, 250))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "quit"
                background_music.stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    pygame.event.clear()
                    game_state = "Playing"
                    oven_sound.stop()
                    reset_game()
                    return
        await asyncio.sleep(0)


    if game_state == "baby stole too many plates end screen":
            broken_plate = pygame.image.load("broken_plate.png")
            broken_plate = pygame.transform.scale(broken_plate, (150, 150))
    while game_state == "baby stole too many plates end screen":
            screen.fill((178,34,34))
            end_text = font.render(" The baby stole and broke too many plates!", True, (255, 255, 255))
            end_text2 = font.render("press r to restart", True, (255, 255, 255))
            screen.blit(end_text, (150, 230))
            screen.blit(end_text2, (250, 280))
            screen.blit(broken_plate, (325, 100))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state = "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game_state = "Playing"
                        oven_sound.stop()
                        reset_game()
                        return
                        #run_game()
            await asyncio.sleep(0)


async def main():
    while game_state != "quit":
        await run_game()
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())