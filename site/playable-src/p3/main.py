import asyncio
import pygame
from random import randint
from Entities import *

pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Sticking Out")
WINDOW_SIZE = (1280, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

x = 0
hp = []
for i in range(15):
    hp.append(Health(x, 0))
    x += 50
player = Player("Assets/PlayerL1.png", 15)

speed = 10
gravity = 0.3
enemy_name = "Bottle"
tiles = []
walls = {"nofall": [], "Bottom": [], "Left": [], "Right": []}

def level_rect(amt_x, amt_y, x, y):
    start_x = x - (amt_x - 1) * 100
    platform_rect = pygame.Rect(start_x, y, amt_x * 100, 20)
    walls["nofall"].append(platform_rect)
    platform_rect = pygame.Rect(start_x, (y+100), amt_x * 100, 20)
    walls["Bottom"].append(platform_rect)

    
    for _ in range(amt_x):
        tiles.append(Tile("Assets/Tile_down.png", x, y))
        x -= 100
        
    spawn_enemy(50, "Assets/BottleL1.png")
    
    for enemy in enemies:
        if platform_rect.left <= enemy.x <= platform_rect.right:
            enemy.y = platform_rect.top - 100
            enemy.speed_y = 0
            enemy.ground_collision = True

def update_physics():
    if not player.ground_collision:
        player.speed_y += gravity

    if player.speed_y != 0:
        player_hitbox = pygame.Rect(player.x, player.y, 100, 100)
        for bottom in walls["Bottom"]:
            if player_hitbox.colliderect(bottom):
                player.speed_y = 0
                break
        for tile in tiles: tile.y -= player.speed_y
        for wall_list in walls.values():
            for rect in wall_list: 
                rect.y -= player.speed_y
        for bullet in nice_bullet_list:
            bullet.y -= player.speed_y
        for bullet in enemy_bullet_list:
            bullet.y -= player.speed_y
        for enemy in enemies:
            if not enemy.ground_collision:
                enemy.y -= player.speed_y

    player_hitbox = pygame.Rect(player.x, player.y, 100, 100)
    player_sensor = pygame.Rect(player.x, player.y + 100, 100, 2)
    player.ground_collision = False

    if player.speed_y >= 0:
        for base in walls["nofall"]:
            if player_sensor.colliderect(base) or player_hitbox.colliderect(base):
                correction = player_hitbox.bottom - base.top
                for tile in tiles:
                    tile.y += correction
                for wall_list in walls.values():
                    for rect in wall_list: 
                        rect.y += correction
                for bullet in nice_bullet_list:
                    bullet.y += correction
                for bullet in enemy_bullet_list:
                    bullet.y += correction
                for enemy in enemies:
                    if not enemy.ground_collision:
                        enemy.y += correction
                player.speed_y = 0
                player.ground_collision = True
                break


    for i, base in enumerate(walls["nofall"]):
        base.y = int(tiles[i * (len(tiles) // len(walls["nofall"]))].y)

    for enemy in enemies:
        on_ground = False
        enemy_bottom = enemy.y + 100

        for base in walls["nofall"]:
            if enemy.x + 100 > base.left and enemy.x < base.right:
                if enemy_bottom >= base.top:
                    enemy.y = base.top - 100
                    enemy.speed_y = 0
                    enemy.ground_collision = True
                    on_ground = True
                    break

        if not on_ground:
            enemy.ground_collision = False
            enemy.speed_y += gravity
            enemy.y += enemy.speed_y

def movement(keys, screen):
    player.movement(keys, screen)

    if keys[pygame.K_w] and player.ground_collision:
        player.speed_y = -12
        player.ground_collision = False

    if keys[pygame.K_a]:
        for enemy in enemies: 
            enemy.x += speed
        for tile in tiles: 
            tile.x += speed
        for wall_list in walls.values():
            for rect in wall_list: rect.x += speed
            
    if keys[pygame.K_d]:
        for enemy in enemies: enemy.x -= speed
        for tile in tiles: tile.x -= speed
        for wall_list in walls.values():
            for rect in wall_list: rect.x -= speed

def enemy_move():
    global state, enemy_name
    player_hitbox = pygame.Rect(player.x, player.y, 100, 100)
    for enemy in enemies:
        enemy_hitbox = pygame.Rect(enemy.x, enemy.y, 100, 100)
        if enemy_hitbox.colliderect(player_hitbox) and player.iframes < 1:
            player.hp -= 1
            if player.hp < 1:
                state = "died"
            else:
                hp.pop(player.hp)
                player.iframes = 120
        enemy.frame += 1
        if enemy.x > player.x:
            enemy.x -= randint(8, 10)
            enemy.img = pygame.image.load(f"Assets/{enemy_name}R{enemy.frame%4}.png").convert_alpha()
            enemy.img = pygame.transform.scale(enemy.img, (100, 100))
        else:
            enemy.x += randint(8, 10)
            enemy.img = pygame.image.load(f"Assets/{enemy_name}L{enemy.frame%4}.png").convert_alpha()
            enemy.img = pygame.transform.scale(enemy.img, (100, 100))

running = True
state = "menu"
nice_bullet_list = []
enemy_bullet_list = []


async def main():
    global running, state, enemy_name, enemies, nice_bullet_list, enemy_bullet_list

    pygame.mixer.music.load("Assets/bg_sound.ogg")
    pygame.mixer.music.play(-1)
    level_rect(50, 1, 320, 450)

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mousex = pygame.mouse.get_pos()[0]
                if mousex > player.x:
                    nice_bullet_list.append(Player_Bullet(10, player.x, player.y+25))
                else:
                    nice_bullet_list.append(Player_Bullet(-10, player.x, player.y+25))
        if state == "menu":
            img = pygame.image.load("Assets/Coverpage.png").convert_alpha()
            img = pygame.transform.scale(img, (1280, 720))
            screen.blit(img, (0, 0))
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                state = "playing"
        elif state == "playing":
            img = pygame.image.load("Assets/Wood background.png").convert_alpha()
            img = pygame.transform.scale(img, (1280, 720))
            screen.blit(img, (0, 0))

            keys = pygame.key.get_pressed()
            movement(keys, screen)
            update_physics()
            enemy_move()

            for heart in hp:
                heart.draw(screen)
            player.draw(screen)
            for index in range(len(nice_bullet_list)):
                bullet_hitbox = pygame.Rect(nice_bullet_list[index].x, nice_bullet_list[index].y, 100, 100)
                for enemy in enemies:
                    enemy_hitbox = pygame.Rect(enemy.x, enemy.y, 100, 100)
                    if bullet_hitbox.colliderect(enemy_hitbox) and enemy.iframes < 1:
                        if randint(1, 3) == 1:
                            enemy.hp -= 1
                            enemy.iframes = 60
            enemies = [enemy for enemy in enemies if enemy.hp > 0]
            to_pop = []
            for index in range(len(enemy_bullet_list))  :
                bullet_hitbox = pygame.Rect(enemy_bullet_list[index].x, enemy_bullet_list[index].y, 100, 100)
                player_hitbox = pygame.Rect(enemy.x, enemy.y, 100, 100)
                if bullet_hitbox.colliderect(player_hitbox) and player.iframes < 1:
                    player.hp -= 1
                    if player.hp < 1:
                        state = "died"
                    else:
                        hp.pop(player.hp)
                        player.iframes = 120
                    to_pop.append(index)
            for index in to_pop:
                enemy_bullet_list.pop(index)

            for bullet in nice_bullet_list:
                bullet.update()
                bullet.draw(screen)

            for enemy in enemies:
                enemy.iframes -= 1
                if enemy.hp > 0:
                    enemy.draw(screen)
            for tile in tiles:
                tile.draw(screen)

            # if enemy_name == "Boss ":
            #     if randint(1, 5) == "5":
            #         enemy_bullet_list.append(Enemy_Bullet(20, enemies[0].x, enemies[0].y, player.x, player.y))

            if len(enemies) == 0:
                enemies.append(Enemy("Assets/Boss L1.png", 50))
                enemy_name = "Boss "

            player.iframes -= 1
        elif state == "died":
            img = pygame.image.load("Assets/Death screen.png").convert_alpha()
            img = pygame.transform.scale(img, (1280, 720))
            screen.blit(img, (0, 0))

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())