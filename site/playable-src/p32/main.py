import asyncio
import pygame
pygame.init()

import random


WINDOW_X = 1600
WINDOW_Y = 1000
screen = pygame.display.set_mode((WINDOW_X, WINDOW_Y))


clock = pygame.time.Clock()
INVINCIBILITY_TIMER = 2
level_timer = 0


grounded = False
platform_grounded = False
no_fall = False

MAX_HEALTH = 3
health = 3
level = 0
stage_success = False

PLAYER_WIDTH = 15 * 7
PLAYER_HEIGHT = 27 * 7
PLAYER_X_POS = WINDOW_X/4
PLAYER_Y_POS = -PLAYER_HEIGHT + 100

GROUND_X_POS = 0
GROUND_Y_POS = WINDOW_Y / 5 * 4
GROUND_WIDTH = WINDOW_X
GROUND_HEIGHT = WINDOW_Y - GROUND_Y_POS

FINISH_WIDTH = 700
FINISH_HEIGHT = 700

ROAD_WIDTH = 700
ROAD_HEIGHT = 700


obstacle_data = { #name: x-pos, y-pos, width, height, file
    "Small Bin": [WINDOW_X, WINDOW_Y - 370, 105, 168, "Assets/Sprites/Small Bin.png"],
    "Big Bin": [WINDOW_X, WINDOW_Y - 400, 52*8, 37*8, "Assets/Sprites/Blank.png"],
    "Flowerpot": [WINDOW_X, WINDOW_Y - 200 - 144, 102, 144, "Assets/Sprites/Flowerpot.png"],
    "Flowerpot 2": [WINDOW_X, WINDOW_Y - 490 - 144, 102, 144, "Assets/Sprites/Flowerpot.png"]
    }

platform_data = { #name: x-pos, y-pos, width, height, file
    "Big Bin": [WINDOW_X, WINDOW_Y - 470, 52*8, 37*8, "Assets/Sprites/Big Bin.png"],
    "Walkway": [WINDOW_X, WINDOW_Y - 500, 700, 550, "Assets/Sprites/Walkway.png"],
    "Shophouse": [WINDOW_X, WINDOW_Y - 140 - 693, 777, 693, "Assets/Sprites/Shophouse.png"]
    }


SPEED = 14

y_velocity = 0
JUMP_FORCE = -30
Y_ACCELERATION = 1.5
TERMINAL_Y_VELOCITY = 20

SMALL_GAME_FONT = pygame.font.Font("Assets/Fonts/Big Bubble.TTF", 128)
BIG_GAME_FONT = pygame.font.Font("Assets/Fonts/Regular.ttf", 24)


invincible = False



state = "Menu"

music = None




    


obstacles = []
platforms = []
finishes = []
buses = []



class Player:
    def __init__(self):
        self.x = PLAYER_X_POS
        self.y = PLAYER_Y_POS
        self.invi_timer = INVINCIBILITY_TIMER
        self.img = pygame.image.load("Assets/Sprites/Girl.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (PLAYER_WIDTH, PLAYER_HEIGHT))

        self.rect = pygame.Rect(self.x + 40, self.y, PLAYER_WIDTH - 50, PLAYER_HEIGHT)

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        
    def update_rect(self):
        self.rect.x = self.x
        self.rect.y = self.y


class Ground:
    def __init__(self):
        self.rect = pygame.Rect(GROUND_X_POS, GROUND_Y_POS, GROUND_WIDTH, GROUND_HEIGHT)

    def draw(self, screen):
        #change this when assets
        pygame.draw.rect(screen, (0, 255, 0), (GROUND_X_POS, GROUND_Y_POS, GROUND_WIDTH, GROUND_HEIGHT))

    def update_rect(self):
        self.rect.x = self.x
        self.rect.y = self.y
        

class Obstacle:
    def __init__(self, x, y, width, height, img):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.img = pygame.image.load(img).convert_alpha()
        self.img = pygame.transform.scale(self.img, (self.width, self.height))
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update_rect(self):
        self.rect.x = self.x
        self.rect.y = self.y

    def moving(self):
        self.x -= SPEED
        self.update_rect()

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))


class Platform:
    def __init__(self, x, y, width, height, img):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.img = pygame.image.load(img).convert_alpha()
        self.img = pygame.transform.scale(self.img, (self.width, self.height))
        

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update_rect(self):
        self.rect.x = self.x
        self.rect.y = self.y

    def moving(self):
        self.x -= SPEED
        self.update_rect()

    def draw(self, screen):
        
        screen.blit(self.img, (self.x, self.y))
        

class Finish():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.img = pygame.image.load("Assets/Sprites/Bus Stop.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (700, 700))

        self.rect = pygame.Rect(self.x + self.width/5*2, 0, 10, WINDOW_Y)

    def update_rect(self):
        self.rect.x = self.x + self.width/5*2
        self.rect.y = 0

    def moving(self):
        self.x -= SPEED
        self.update_rect()

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

class Text():
    def __init__(self, x, y, width, height, colour):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect)


class Road:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = pygame.image.load("Assets/Sprites/Road.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (ROAD_WIDTH, ROAD_HEIGHT))

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

class Bus:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = pygame.image.load("Assets/Sprites/Bus.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (1600, 800))

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

class Clouds:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = pygame.image.load("Assets/Sprites/Cloud.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (400, 200))
        
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        

ground = Ground()
player = Player()


    
def spawn_obstacle(obstacle_type, time, dt):
    if level_timer > time - dt/2 and level_timer < time + dt/2:
        obstacles.append(Obstacle(obstacle_data[obstacle_type][0], obstacle_data[obstacle_type][1], obstacle_data[obstacle_type][2], obstacle_data[obstacle_type][3], obstacle_data[obstacle_type][4]))
    
def spawn_platform(platform_type, time, dt):
    if level_timer > time - dt/2 and level_timer < time + dt/2:
        platforms.append(Platform(platform_data[platform_type][0], platform_data[platform_type][1], platform_data[platform_type][2], platform_data[platform_type][3], platform_data[platform_type][4]))

def spawn_finish(time, dt):
    if level_timer > time - dt/2 and level_timer < time + dt/2:
        finishes.append(Finish(WINDOW_X, WINDOW_Y - FINISH_HEIGHT, FINISH_HEIGHT, WINDOW_Y))

def spawn_bus(time, dt):
    if level_timer > time - dt/2 and level_timer < time + dt/2:
        buses.append(Bus(WINDOW_X, WINDOW_Y - 700))

def spawn_clouds(time, dt):
    if level_timer > time - dt/2 and level_timer < time + dt/2:
        clouds.append(Cloud(WINDOW_X, random.randint (100, 300)))

    

def music_change(to_be_played, playing):
    music_file = f"Assets/Music/{to_be_played}.ogg"
    pygame.mixer.init()
    if to_be_played != playing:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1)
    


  




roads = [Road(0, WINDOW_Y - 700), Road(700, WINDOW_Y - 700), Road(1400, WINDOW_Y - 700), Road(2100, WINDOW_Y - 700)]
clouds = [Clouds(random.randint(0, 400), random.randint(40, 300)), Clouds(random.randint(500, 900), random.randint(40, 300)), Clouds(random.randint(1000, 1400), random.randint(40, 300)), Clouds(random.randint(1500, 2400), random.randint(40, 300)), Clouds(random.randint(2000, 2900), random.randint(40, 300))]


async def main():
    global health, level, level_timer, state, stage_success
    global invincible, y_velocity, music

    running = True
    while running:
        dt = clock.tick(60)/1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((135,206,250))

        ground.draw(screen)

        if invincible:
            player.img = pygame.image.load("Assets/Sprites/Girl Falling.png").convert_alpha()
            player.img = pygame.transform.scale(player.img, (20*7, 25*7))
        else:
            player.img = pygame.image.load("Assets/Sprites/Girl.png").convert_alpha()
            player.img = pygame.transform.scale(player.img, (PLAYER_WIDTH, PLAYER_HEIGHT))

        #### CLOUDS ####



        for cloud in clouds:
            cloud.x -= 4
            cloud.draw(screen)
            if cloud.x <= -700:
                cloud.x += random.randint(2600, 2800)




        #### KEY ALLOCATIONS ####
        keys = pygame.key.get_pressed()
        jump_press = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]

        if keys[pygame.K_s]:
            print(state)





        #### PHYSICS SIMULATION + JUMPING ####


        grounded = False
        platform_grounded = False

        if state == "Level select" or state == "Menu":
            no_fall = True
        else: no_fall = False



        if player.rect.colliderect(ground.rect) or player.y == GROUND_Y_POS - PLAYER_HEIGHT:    
            grounded = True




        for platform in platforms[:]:
            if player.rect.colliderect(platform.rect):
                if y_velocity >= 0 and player.y + PLAYER_HEIGHT < platform.y + TERMINAL_Y_VELOCITY:
                    platform_grounded = True




        if not grounded and not platform_grounded and no_fall == False:
            player.y += y_velocity
            if y_velocity < TERMINAL_Y_VELOCITY:
                y_velocity += Y_ACCELERATION   
            else:
                y_velocity = TERMINAL_Y_VELOCITY

        elif state == "Play":
            y_velocity = 0
            if jump_press:
                player.y -= 2
                y_velocity = JUMP_FORCE
                grounded = False

                pygame.mixer.Channel(1).play(pygame.mixer.Sound("Assets/Sound Effects/Jump.ogg"))


        if player.y > GROUND_Y_POS - PLAYER_HEIGHT:
            player.y = GROUND_Y_POS - PLAYER_HEIGHT

        for platform in platforms[:]:
            if player.rect.colliderect(platform.rect):
                if y_velocity >= 0 and player.y + PLAYER_HEIGHT < platform.y + TERMINAL_Y_VELOCITY:
                    player.y = platform.y - PLAYER_HEIGHT 






        #### PLATFORMS ####


        for platform in platforms[:]:
            platform.moving()
            platform.draw(screen)
            if platform.x < -platform.width:
                platforms.remove(platform)

            platform.update_rect()



        ####  FINISH LINE ####


        for finish in finishes[:]:
            finish.moving()
            finish.draw(screen)
            if finish.x < -finish.width:
                finishes.remove(finish)
            if finish.rect.colliderect(player.rect):
                stage_success = True
                state = "Game over"


            finish.update_rect()

        #### OBSTACLES ####



        for obstacle in obstacles[:]:
            obstacle.moving()
            obstacle.draw(screen)
            if obstacle.x < -obstacle.width:
                obstacles.remove(obstacle)

            if obstacle.rect.colliderect(player.rect) and not invincible:
                pygame.mixer.Channel(2).play(pygame.mixer.Sound("Assets/Sound Effects/Hit.ogg"))
                health -= 1

                if health == 0:
                    stage_success = False
                    state = "Game over"

                invincible = True

            obstacle.update_rect()

        if invincible == True:
            player.invi_timer -= dt
        if player.invi_timer <= 0:
            invincible = False
            player.invi_timer = INVINCIBILITY_TIMER

        #### ROAD DRAWING ####

        for road in roads[:]:
            road.x -= SPEED
            road.draw(screen)
            if road.x <= -700:
                road.x += 2800



        #### BUS ####
        for bus in buses[:]:

            if state != "Game over":
                bus.x -= SPEED
            else:
                bus.x += SPEED


            bus.draw(screen)



        #### UI & STATES ####


        if state == "Menu":



            start_text = SMALL_GAME_FONT.render("CATCHING", True, (0, 170, 76))
            screen.blit(start_text, (350, 300))

            start_text1 = SMALL_GAME_FONT.render("THE BUS!", True, (0, 170, 76))
            screen.blit(start_text1, (390, 430))

            start_text2 = BIG_GAME_FONT.render("press <spacebar> to begin!", True, (255, 255, 255))
            screen.blit(start_text2, (500, 580))

            music_change("Title Theme", music)
            music = "Title Theme"

            if keys[pygame.K_SPACE]:
                player.x = PLAYER_X_POS
                player.y = PLAYER_Y_POS
                level_timer = 0
                health = 3
                level = 1
                state = "Play"





        if state == "Play":



            win_text = BIG_GAME_FONT.render("Health: " + str(health), True, (255, 255, 255))
            screen.blit(win_text, (20, 20))

            music_change("Hurry Up!!!", music)
            music = "Hurry Up!!!"


            level_timer += dt



            #########  LEVEL 1  #########


            if level == 1:


                spawn_obstacle("Flowerpot", 1, dt)

                spawn_obstacle("Small Bin", 2.5, dt)

                spawn_obstacle("Flowerpot", 3.5, dt)
                spawn_obstacle("Small Bin", 3.65, dt)

                spawn_platform("Shophouse", 4, dt)



                spawn_obstacle("Flowerpot", 5, dt)
                spawn_platform("Shophouse", 6, dt)



                spawn_platform("Walkway", 7.7, dt)
                spawn_obstacle("Flowerpot", 8, dt)

                spawn_platform("Walkway", 9.2, dt)
                spawn_obstacle("Flowerpot 2", 9.5, dt)

                spawn_platform("Walkway", 10.7, dt)
                spawn_obstacle("Flowerpot 2", 10.8, dt)
                spawn_platform("Walkway", 10.7 + 700/SPEED/60, dt)
                spawn_obstacle("Big Bin", 10.8 + 700/SPEED/60, dt)
                spawn_platform("Big Bin", 10.8 + 700/SPEED/60, dt)
                spawn_obstacle("Flowerpot 2", 10.8 + 2*700/SPEED/60-0.3, dt)

                spawn_platform("Walkway", 12, dt)
                spawn_obstacle("Small Bin", 12.1, dt)
                spawn_obstacle("Big Bin", 12.8, dt)
                spawn_platform("Big Bin", 12.8, dt)
                spawn_platform("Walkway", 13.4, dt)


                spawn_obstacle("Flowerpot 2", 13.7, dt)
                spawn_obstacle("Flowerpot 2", 13.9, dt)




                spawn_platform("Shophouse", 15.5, dt)

                spawn_obstacle("Small Bin", 15, dt)


                spawn_platform("Walkway", 16, dt)
                spawn_platform("Shophouse", 16 + 700/SPEED/60, dt)
                spawn_obstacle("Small Bin", 16 + 700/SPEED/60, dt)

                spawn_obstacle("Big Bin", 18.5, dt)
                spawn_platform("Big Bin", 18.5, dt)






                spawn_finish(20, dt)
                spawn_bus(20, dt)










        if state == "Game over": 
            if player.x >= -30*7:
                player.x -= SPEED


            music_change("Title Theme", music)
            music = "Title Theme"

            if stage_success == True:

                win_text = BIG_GAME_FONT.render("you win! (still missed the bus tho)", True, (255, 255, 255))
                screen.blit(win_text, (WINDOW_X/4, WINDOW_Y/4 + 100))


            elif stage_success == False:

                y_velocity = JUMP_FORCE/2

                lose_text = BIG_GAME_FONT.render("too bad!", True, (255, 255, 255))
                screen.blit(lose_text, (WINDOW_X/4, WINDOW_Y/4 + 100))

            option_text = BIG_GAME_FONT.render("<r> to restart, <m> to main menu", True, (255, 255, 255))
            screen.blit(option_text, (WINDOW_X/3, WINDOW_Y/3 + 100))

            if keys[pygame.K_r]:
                player.x = PLAYER_X_POS
                player.y = PLAYER_Y_POS
                level_timer = 0
                health = 3
                state = "Play"
            if keys[pygame.K_s]:
                state = "Level Select"
            if keys[pygame.K_m]:
                state = "Menu"


        player.update_rect()

        player.draw(screen)



        pygame.display.update()

        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
