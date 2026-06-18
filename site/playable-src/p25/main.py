import asyncio
import pygame
import random

pygame.init()

#Window size
WINDOW_SIZE = (500, 800)
screen = pygame.display.set_mode(WINDOW_SIZE)

#Clock
clock = pygame.time.Clock()

#Sound
hit_sound = pygame.mixer.Sound("hit.ogg") #temp rn
pickup_sound = pygame.mixer.Sound("pickup.ogg")
fail_sound = pygame.mixer.Sound("fail.ogg")
success_sound = pygame.mixer.Sound("success.ogg")


hit_sound.set_volume(0.5)
pickup_sound.set_volume(0.7)
fail_sound.set_volume(0.7)


pygame.mixer.music.load("bgm.ogg")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)


#OOP
#Player
class Player:
    def __init__(self, img):
        #coords, set at the bottom of the window
        self.x = WINDOW_SIZE[0] // 2 - 50
        self.y = WINDOW_SIZE[1] - 150
        
        #imgsc
        self.img = pygame.image.load(img).convert_alpha()
        self.img = pygame.transform.scale(self.img, (100, 100))

        #Collision
        self.rect = pygame.Rect(self.x, self.y, 100, 100)

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def update_rect(self): #Let rectangle for collision follow self
        self.rect.x = self.x
        self.rect.y = self.y

    def move(self, inverse, keys, p_speed):
        if inverse == False:
            if keys[pygame.K_LEFT]:
                self.x -= p_speed

            if keys[pygame.K_RIGHT]:
                self.x += p_speed

        if inverse == True:
            if keys[pygame.K_LEFT]:
                self.x += p_speed

            if keys[pygame.K_RIGHT]:
                self.x -= p_speed


    def border(self):
        #Keep player in the window, border around window
        self.x = max(50, self.x)
        self.x = min(self.x, WINDOW_SIZE[0] - 100 - 50)


#Uh. Need to avoid, make it a square for now
class Obstacle:
    def __init__(self, x, y):
        #coords
        self.x = x
        self.y = y
        
        #img
        self.img = pygame.image.load("phone.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (100, 100))

        #Collision
        self.rect = pygame.Rect(self.x, self.y, 100, 100)

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def update_rect(self): #Let rectangle for collision follow self
        self.rect.x = self.x
        self.rect.y = self.y

    def move(self, speed): 
        self.y += speed


class Plant:
    def __init__(self, imgPlant):
        #coords
        self.x = WINDOW_SIZE[0] // 2 - 200
        self.y = -400

        #plant img
        self.plant = pygame.image.load(imgPlant).convert_alpha()
        self.plant = pygame.transform.scale(self.plant, (400, 400))

        #Collision
        self.rect = pygame.Rect(self.x, self.y, 400, 300)


    def drawPlant(self, screen):
        screen.blit(self.plant, (self.x, self.y))
    
    def display_plant(self, screen):
        screen.blit(self.plant, (50, 250))

    def update_rect(self): #Let rectangle for collision follow self
        self.rect.x = self.x
        self.rect.y = self.y

    def move(self, speed): 
        self.y += speed 
        #Backup, if we cannot get the pickup range to be big enough
        if self.y > WINDOW_SIZE[1]: #so if it reaches the end
            self.y = -400 #reset the plant

    def update_img(self, img):
        self.plant = pygame.image.load(img).convert_alpha()
        self.plant = pygame.transform.scale(self.plant, (400, 400))


#Spawn stuff
def spawn_obstacle():
    start_x = random.choice([10, 110, 210, 310, 410])
    start_y = -50

    obstacles.append(Obstacle(start_x, start_y))


#level stuff
def next_level():
    global level, level_timer, curr_plant, spawn_timer #for assignment

    #Reset level
    level += 1
    level_timer = 20

    #Reset obstacles
    spawn_timer = 1
    obstacles.clear()

    cat.x = WINDOW_SIZE[0] // 2 - 50
    cat.y = WINDOW_SIZE[1] - 150

    #Plant
    curr_plant.y = -400


def reset():
    global level, level_timer, spawn_timer, curr_plant, plant_life #for assignment

    #Reset level
    level = 1
    level_timer = 20

    #Reset obstacles
    spawn_timer = 1
    obstacles.clear()

    cat.x = WINDOW_SIZE[0] // 2 - 50
    cat.y = WINDOW_SIZE[1] - 150

    #Reset plant
    curr_plant = Plant("flower_healthy.png") #Replace with healthy plant
    plant_life = 3


#Text functions
def display_text(text, x, y, font_size):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, (0, 0, 0)) #create text. parameters: (text, anti-aliasing, rgb)
    screen.blit(text_surface, (x, y))

def display_day():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    if 1 <= level <= len(days):
        display_text(days[level - 1], 50, 100, 50)

def display_remarks():
    remarks = ["Tutorial", "You had coffee!", "How exhausting", "The obstacles had coffee!", "Everything", "", ""]
    if 1 <= level <= len(remarks):
        display_text(remarks[level - 1], 50, 150, 30)

def display_effects():
    effects = ["Effect: Normal", "Effect: Player Speed Up", "Effect: Inverse Controls", "Effect: Obstacles Speed Up", "Effect: Everything", "", ""]
    if 1 <= level <= len(effects):
        display_text(effects[level - 1], 50, 175, 30)

def display_p():
    p_str = "Press P to go to the next day"
    display_text(p_str, 50, 650, 30)


def display_menu():
    title_str = "Alice's Garden Journey"

    menu_lines = [
            "You are Alice!", 
            "You got a new flower from your mom", 
            "She says you have to water it everyday", 
            "after school",
            "How mundane...",
            "",
            "",
            "Press left and right to avoid",
            "the distractions (your phone)", 
            "to reach home on time!",
            "",
            "Collide with the plant at the end", 
            "to finish the level!",
            "",
            "Press p to play"
            ]
    
    y = 140

    display_text(title_str, 50, 50, 50)

    for line in menu_lines:
        display_text(line, 50, y, 30)
        y += 40

def display_break():
    break_lines = [
            "You reached home in time to water", 
            "your plant!", 
            "It's very happy!",
            "You can even see it grow a bit more."
            ]

    if level >= 5 and plant_life > 0:
        display_win()
        curr_plant.update_img("flower_bloom.png") #Bloom
        return

    y = 100

    for line in break_lines:
        display_text(line, 50, y, 30)
        y += 45

    curr_plant.display_plant(screen) #Draw healthy plant
    
    display_p()

def display_fail():
    fail_lines = [
            "You didn't make it home in time to water", 
            "your plant...",
            f"Well, it's fine, you just have to not miss {plant_life}",
            "more times!"
            ]
    
    y = 100

    for line in fail_lines:
        display_text(line, 50, y, 30)
        y += 45

    curr_plant.display_plant(screen) #Draw healthy plant

    display_p()

def display_win():
    win_lines = [
            "You reached home in time to water", 
            "your plant!", 
            "It's very happy!",
            "It has bloomed beautifully."
            ]

    win_lines_2 = [
            "Guess this watering routine",
            "isn't so bad.",
            "Press r to replay!"]
    
    y = 90

    for line in win_lines:
        display_text(line, 50, y, 30)
        y += 45

    curr_plant.display_plant(screen)
    
    y2 = 650

    for line_2 in win_lines_2:
        display_text(line_2, 50, y2, 30)
        y2 += 45

def display_game_over():
    lose_lines = [
            "You didn't make it home in time to water the", 
            "plant...",
            "You look at the withered leaves..."
            ]
    
    lose_line_2 = "Press r to restart"
    
    y = 100

    for line in lose_lines:
        display_text(line, 50, y, 30)
        y += 45

    curr_plant.display_plant(screen)

    display_text(lose_line_2, 50, 650, 30)

def display_fail_but_win():
    fail_but_win_lines = [
            "You didn't make it home",
            "in time to water the", 
            "plant...",
            "But due to your past efforts...",
            "It bloomed beautifully."
            ]

    fail_but_win_lines_2 = [
            "Guess this watering routine",
            "isn't so bad.",
            "Press r to replay!"]
    
    y = 100

    for line in fail_but_win_lines:
        display_text(line, 50, y, 30)
        y += 45

    curr_plant.display_plant(screen)
    
    y2 = 600

    for line_2 in fail_but_win_lines_2:
        display_text(line_2, 50, y2, 30)
        y2 += 45



#characters
cat = Player("player.png") #replace this with player sprite

obstacles = []

curr_plant = Plant("flower_healthy.png")


#Timers
spawn_timer = 1 #To handle how frequently the obstacles spawn
level_timer = 20 #Handle how long a level takes

#Set up
state = "menu"
level = 1
plant_life = 3


#Game
async def main():
    global state, level, plant_life, spawn_timer, level_timer, curr_plant
    running = True
    while running:
        dt = clock.tick(60) / 1000
        #Add bg sound

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    state = "menu"

                if event.key == pygame.K_p:
                    if state == "menu":
                        state = "play"

                    elif state == "break":
                        next_level()
                        state = "play"


                    elif state == "fail":
                        next_level()
                        state = "play"
            
                if event.key == pygame.K_r:
                    if state == "game over" or state == "win" or state == "fail but win":
                        reset()
                        state = "menu"


        if state == "menu":
            screen.fill((161, 209, 80))
            display_menu()


        elif state == "play":
            #Level rules
            if level == 1: #default
                obs_speed = 7
                spawn_speed = 0.8
                p_speed = 5
                inverse = False
            elif level == 2: #Character speed up
                obs_speed = 7
                spawn_speed = 0.7
                p_speed = 12
                inverse = False
            elif level == 3: #Inverse
                obs_speed = 7
                spawn_speed = 0.6
                p_speed = 5
                inverse = True
            elif level == 4: #Obs speed up
                obs_speed = 13
                spawn_speed = 0.5
                p_speed = 5
                inverse = False
            elif level == 5: #All
                obs_speed = 15
                spawn_speed = 0.5
                p_speed = 12
                inverse = True
            else:
                state = "win"


            #Actual gameplay
            #obstacles move down regardless
            for obstacle in obstacles:
                obstacle.move(obs_speed)


            #keys
            keys = pygame.key.get_pressed()
            cat.move(inverse, keys, p_speed) #can change this per level
            cat.border()

            #collisions
            cat.update_rect()


            #Handle level changes 
            if level_timer <= 0: #If level time runs out/level over, and we have not spawned the thing in yet
                curr_plant.move(obs_speed) #Move plant down
                curr_plant.update_rect() #Move collision down

                if cat.rect.colliderect(curr_plant.rect):
                
                    if level >= 5: #Specific only to win condition 
                        success_sound.play()
                        curr_plant.update_img("flower_bloom.png") #bloom
                        state = "win"

                    else:
                        pickup_sound.play()
                        state = "break"

            else: #So timer still going
                level_timer -= dt

                #spawning mechanism
                spawn_timer -= dt

                if spawn_timer <= 0:
                    spawn_obstacle()
                    spawn_timer = spawn_speed #Can change per level


            for obstacle in obstacles:
                obstacle.update_rect()

                if cat.rect.colliderect(obstacle.rect):
                    hit_sound.play()
                    #Do the game over or fail logic here

                    plant_life -= 1 

                    if plant_life <= 0:
                        curr_plant.update_img("flower_wither.png") #Wither
                        fail_sound.play()
                        state = "game over"

                    elif level >= 5 and plant_life > 0: #so if we fail at last level but have health left
                        success_sound.play()
                        curr_plant.update_img("flower_bloom.png") #Bloom
                        state = "fail but win"

                    else:
                        state = "fail"

            
                if obstacle.y > WINDOW_SIZE[1]: #so if it reaches the end
                    obstacles.remove(obstacle) #rmv

        
            #Background
            screen.fill((161, 209, 80)) #green

            #Draw
            cat.draw(screen)

            #text, render and change text here
            #Can have a class for text, and put functions in them, and 
            if level - 1 < 5:
                display_day()
                display_remarks()
                display_effects()
        
            if curr_plant != None: #If we have a current plant
                curr_plant.drawPlant(screen)

            for obstacle in obstacles:
                obstacle.draw(screen)

        elif state == "break":
            screen.fill((161, 209, 80))
            display_break()
    

        elif state == "win":
            screen.fill((161, 209, 80))
            display_win()


        elif state ==  "fail":
            screen.fill((161, 209, 80))
            display_fail()

        elif state == "fail but win":
            screen.fill((161, 209, 80))
            display_fail_but_win()


        elif state == "game over":
            screen.fill((161, 209, 80))
            display_game_over()
        

        pygame.display.update()

        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
