import asyncio
import pygame

pygame.init()

sw = 800
sh = 600
size = sw, sh

s = pygame.display.set_mode(size)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 20)
state = 'game'
pygame.mouse.set_visible(False)
pygame.mixer.music.load("pygame track.ogg")
pygame.mixer.music.play(-1)

selected = []
collectables = {
    "paperclip": pygame.Rect(200, 0, 50, 50),
    "pencil": pygame.Rect(750, 0, 50, 50),
    "tape": pygame.Rect(750, 550, 50, 50)
}
inventory_visibility = False
craft_rect = pygame.Rect(sw/2-50, sh/2-50, 100, 100)
cupboard_rect = pygame.Rect(-50, 475, 1000, 50)

recipes = {
    ('paperclip',): 'lockpick',
    ('pencil', 'tape'): 'ladder'
}

crafted_message = ""
message_timer = 0

known_recipes = [
    "Paperclip -> Lockpick",
    "Pencil + Tape -> Ladder"
]

shelf_rect = pygame.Rect(-50, -50, 250, 700)

class Player():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xvel = 0
        self.yvel = 0
        self.inventory = []
    
    def move(self, key):
        ix = False
        iy = False
        if key[pygame.K_UP] or key[pygame.K_w]:
            self.yvel -= 3
            iy = True
        if key[pygame.K_DOWN] or key[pygame.K_s]:
            self.yvel += 3
            iy = True
        if key[pygame.K_LEFT] or key[pygame.K_a]:
            self.xvel -= 3
            ix = True
        if key[pygame.K_RIGHT] or key[pygame.K_d]:
            self.xvel += 3
            ix = True

        if not ix:
            self.xvel *= 0.5
        if not iy:
            self.yvel *= 0.5
        
        self.xvel = max(-10, min(10, self.xvel))
        self.yvel = max(-10, min(10, self.yvel))

        self.x += self.xvel
        self.y += self.yvel
    
    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y, 50, 50))
    
    def collide(self, collectables, craft_rect, cupboard_rect, shelf_rect, key):
        global state, selected
        collected = []
        rect = pygame.Rect(self.x, self.y, 50, 50)
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        if self.x > 750:
            self.x = 750
        if self.y > 550:
            self.y = 550

        for name, item_rect in collectables.items():
            if rect.colliderect(item_rect):
                if len(self.inventory) < 5:
                    collected.append(name)
                    self.inventory.append(name)
                    self.inventory.sort()
        
        if rect.colliderect(craft_rect):
            if key[pygame.K_c]:
                state = 'craft'
                selected.clear()
        if rect.colliderect(cupboard_rect):
            if not ('lockpick' in self.inventory):
                self.yvel = 0
                self.y = 425 
        if rect.colliderect(shelf_rect):
            if "ladder" not in self.inventory:
                self.x = shelf_rect.right
                self.xvel = 0

        
        return(collected)
        
p1 = Player(sw/2 - 25, sh/2 - 25)


async def main():
    global state, selected, inventory_visibility, crafted_message, message_timer
    running = True

    while running:
        mouse1 = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    inventory_visibility = not inventory_visibility
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse1 = True
        s.fill((0, 0, 0))

        keys = pygame.key.get_pressed()
        mousex, mousey = pygame.mouse.get_pos()
        mouse_rect = pygame.Rect(mousex, mousey, 10, 20)

        if state == 'game':
            for name, rect in collectables.items():
                pygame.draw.rect(s, (255, 255, 0), rect)
        
            pygame.draw.rect(s, (180, 105, 0), craft_rect)
            pygame.draw.rect(s, (130, 55, 0), cupboard_rect)
            pygame.draw.rect(s, (120,80,40), shelf_rect)
            

            p1.move(keys)
            for item in p1.collide(
                collectables,
                craft_rect,
                cupboard_rect,
                shelf_rect,
                keys
            ):
                del collectables[str(item)]
            p1.draw(s)

            # ui
            if inventory_visibility:
                for i, item in enumerate(p1.inventory):
                    text = font.render(item, True, (255, 255, 255))
                    s.blit(text, (10, 10 + i * 30))
        elif state == 'craft':
            if keys[pygame.K_ESCAPE]:
                state = 'game'
                for item in selected:
                    p1.inventory.append(item)
                    p1.inventory.sort()
                selected.clear()

            recipe_title = font.render(
                "Known Recipes:",
                True,
                (255,255,255)
            )

            s.blit(recipe_title, (10,100))

            for i, recipe in enumerate(known_recipes):

                txt = font.render(
                    recipe,
                    True,
                    (200,200,200)
                )

                s.blit(
                    txt,
                    (10,130 + i * 25)
                )
            
            for i, item in enumerate(p1.inventory[:]):
                text = font.render(item, True, (255, 255, 255))
                text_rect = pygame.Rect(10 + i * 100, 10, text.get_width(), text.get_height())
                s.blit(text, (10 + i * 100, 10))
                if text_rect.colliderect(mouse_rect):
                    if mouse1:
                        selected.append(item)
                        p1.inventory.remove(item)

            start_x = sw/2 - (len(selected) * 50)

            for i, item in enumerate(selected):
                text = font.render(item, True, (255,255,255))

                text_rect = pygame.Rect(
                    start_x + i * 100,
                    sh/2,
                    text.get_width(),
                    text.get_height()
                )

                s.blit(
                    text,
                    (start_x + i * 100, sh/2)
                )

                if text_rect.colliderect(mouse_rect):
                    if mouse1:
                        selected.remove(item)
                        p1.inventory.append(item)
                        p1.inventory.sort()
        
            finish_rect = pygame.Rect(400, 500, 75, 25)
            pygame.draw.rect(s, (255, 255, 255), finish_rect)

            if finish_rect.colliderect(mouse_rect):
                if mouse1:

                    key = tuple(sorted(selected))

                    if key in recipes:

                        crafted_item = recipes[key]

                        p1.inventory.append(crafted_item)
                        p1.inventory.sort()

                        crafted_message = f"Created {crafted_item}!"
                        message_timer = 180

                    else:

                        for item in selected:
                            p1.inventory.append(item)

                        p1.inventory.sort()

                        crafted_message = "Nothing happened..."
                        message_timer = 180

                    selected.clear()
        

            if message_timer > 0:

                msg = font.render(
                    crafted_message,
                    True,
                    (255,255,0)
                )

                s.blit(
                    msg,
                    (
                        sw//2 - msg.get_width()//2,
                        50
                    )
                )

                message_timer -= 1
        
        pygame.draw.rect(s, (255, 255, 255), mouse_rect)

        pygame.display.flip()

        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
