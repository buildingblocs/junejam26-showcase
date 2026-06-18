# ===== IMPORT LIBRARIES =====
import asyncio  # Required for pygbag (browser) async main loop
import pygame  # Game library for graphics, sound, and game logic
import random  # For random numbers (random sock positions, speeds, colors)
import sys     # For exiting the program when the game is closed
import os

basedir = os.path.dirname(__file__)
sock_image_path = os.path.join(basedir, "sock.png")


# ===== INITIALIZE PYGAME =====
# This starts the pygame library so we can use it
pygame.init()

# ===== GAME SETTINGS =====
# These are the SIZE of the game window (in pixels)
SCREEN_WIDTH = 800    # Width of the game window
SCREEN_HEIGHT = 600   # Height of the game window
FPS = 70              # FPS = Frames Per Second (how many times per second the game updates)

# ===== COLOR DEFINITIONS =====
# Colors are defined as RGB (Red, Green, Blue) values from 0-255
# For example: (255, 0, 0) = pure red, (0, 255, 0) = pure green, (0, 0, 255) = pure blue
WHITE = (255, 255, 255)      # White color (all colors at max)
BLACK = (0, 0, 0)            # Black color (no colors)
LIGHT_BLUE = (173, 216, 230) # Light blue (for the sky)
DARK_GRAY = (64, 64, 64)     # Dark gray (for washing machines)
RED = (255, 100, 100)        # Red sock color
BLUE = (100, 150, 255)       # Blue sock color
PINK = (255, 150, 200)       # Pink sock color
YELLOW = (255, 255, 100)     # Yellow sock color
GREEN = (150, 255, 150)      # Green sock color

# ===== GAME TIME SETTINGS =====
GAME_DURATION = 60  # How many seconds the game lasts (60 = 1 minute)
TIMER_TICK = 1000   # Milliseconds between timer updates (1000 = 1 second)

# ===== SOCK IMAGE LOADING (with built-in fallback) =====
# The game was designed to load sock.png / sock2.png / sock3.png (pixel art made
# in piskelapp.com). Those image files are not bundled with the submission, so we
# load them if present and otherwise draw a matching sock shape in code. This keeps
# the game fully playable in the browser while preserving the intended look.

# Sock body colors used by the drawn fallback (matching the three sock variants)
_SOCK_FALLBACK_COLORS = [
    (255, 100, 100),   # red sock
    (100, 150, 255),   # blue sock
    (255, 150, 200),   # pink sock
]

_sock_image_cache = []  # filled once, reused for every sock


def _make_drawn_sock(body_color):
    """Build a small sock-shaped surface in code (used when no PNG is available)."""
    w, h = 36, 48
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cuff = (245, 245, 245)
    # Cuff (top band of the sock)
    pygame.draw.rect(surf, cuff, (8, 0, 20, 8))
    # Leg (vertical part)
    pygame.draw.rect(surf, body_color, (8, 8, 20, 26))
    # Foot (horizontal part at the bottom)
    pygame.draw.rect(surf, body_color, (8, 28, 28, 14))
    # Rounded toe
    pygame.draw.circle(surf, body_color, (30, 35), 7)
    # Heel accent
    pygame.draw.circle(surf, body_color, (8, 34, ), 7)
    # Outline so it reads clearly on the light-blue background
    pygame.draw.rect(surf, (0, 0, 0), (8, 0, 20, 8), 2)
    pygame.draw.rect(surf, (0, 0, 0), (8, 8, 20, 26), 2)
    return surf


def get_sock_images():
    """Return the list of sock surfaces, loading PNGs if present, else drawing them."""
    global _sock_image_cache
    if _sock_image_cache:
        return _sock_image_cache
    filenames = ["sock.png", "sock2.png", "sock3.png"]
    images = []
    for i, name in enumerate(filenames):
        path = os.path.join(basedir, name)
        loaded = None
        if os.path.exists(path):
            try:
                loaded = pygame.image.load(path).convert_alpha()
            except Exception:
                loaded = None
        if loaded is None:
            loaded = _make_drawn_sock(_SOCK_FALLBACK_COLORS[i % len(_SOCK_FALLBACK_COLORS)])
        images.append(loaded)
    _sock_image_cache = images
    return _sock_image_cache

# ===== SOCK CLASS =====
# A "Class" is like a blueprint for creating sock objects
# Think of it like a recipe that tells us everything about a sock
class Sock:
    """Represents a falling sock in the game"""
    
    # The __init__ function runs ONCE when we create a new sock
    # It sets up all the starting values for that sock
    def __init__(self):
        # X position = random spot left to right (between 50 and 750 pixels)
        # This makes socks appear at different horizontal positions
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        
        # Y position = -20 (above the screen, so it falls in from the top)
        self.y = -20

        # How big the sock is (we'll use the image size for this)
        # Pick one of the three sock images (loaded from PNG if available,
        # otherwise a sock drawn in code) so the game runs with no asset files.
        self.sock_image = random.choice(get_sock_images())
        self.width = self.sock_image.get_width()
        self.height = self.sock_image.get_height()
        
        # How fast the sock falls (random speed between 2 and 5 pixels per frame)
        # Higher number = falls faster
        self.speed = random.randint(2, 5)
        
        # Pick a random color for this sock from our list of colors
        self.color = random.choice([RED, BLUE, PINK, YELLOW, GREEN])
    
    # The update function is called EVERY FRAME to move the sock
    # It makes the sock fall down the screen
    def update(self):
        """Make the sock fall down the screen"""
        # Add the speed to the Y position (Y increases = going down)
        self.y += self.speed
    
    # The draw function is called EVERY FRAME to show the sock
    def draw(self, screen):
        """Draw the sock as an image"""
        screen.blit(self.sock_image, (self.x, self.y))
    
    # Check if the sock has fallen off the bottom of the screen
    def is_off_screen(self):
        """Check if the sock has fallen off the bottom"""
        # If Y position is greater than screen height, it's off the bottom
        # If this is True, the player missed the sock!
        return self.y > SCREEN_HEIGHT


# ===== PLAYER CLASS =====
# The Player class is the basket that catches the socks
class Player:
    """Represents the basket/container for catching socks"""
    
    # __init__ runs when we first create the player
    def __init__(self):
        # Start the basket in the middle of the screen horizontally
        # SCREEN_WIDTH // 2 = middle of screen, minus 35 to center the basket
        self.x = SCREEN_WIDTH // 2 - 35
        
        # Y position = near the bottom of the screen (60 pixels from bottom)
        self.y = SCREEN_HEIGHT - 60
        
        # The basket is 70 pixels wide and 50 pixels tall
        self.width = 70
        self.height = 50
        
        # How fast the basket moves when you press arrow keys (8 pixels per frame)
        self.speed = 8
    
    # This function is called EVERY FRAME to handle player input (arrow keys)
    def update(self, keys):
        """Move the basket left and right based on arrow keys"""
        # pygame.K_LEFT = left arrow key
        # If left arrow is pressed, move left (subtract from X)
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        
        # pygame.K_RIGHT = right arrow key
        # If right arrow is pressed, move right (add to X)
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        
        # Keep the basket on screen - DON'T let it go off the left side
        if self.x < 0:
            self.x = 0  # Push it back to the left edge
        
        # DON'T let it go off the right side
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width  # Push it back to the right edge
    
    # This function is called EVERY FRAME to draw the basket
    def draw(self, screen):
        """Draw the basket as a rectangle with a handle"""
        # Draw the main basket body (a gray rectangle)
        pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height))
        
        # Draw a handle on top (an arc = curved line)
        # This makes it look like a real basket
        pygame.draw.arc(screen, BLACK, (self.x + 5, self.y - 10, self.width - 10, 20), 0, 3.14, 3)
        
        # Draw a black border around the basket (thickness = 3 pixels)
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)
    
    # This function returns a rectangle shape that we use for collision detection
    def get_rect(self):
        """Return a rectangle for collision detection"""
        # Collision detection = checking if the sock touches the basket
        # pygame.Rect creates a rectangle object that's easy to check collisions with
        return pygame.Rect(self.x, self.y, self.width, self.height)


# ===== GAME CLASS =====
# This is the main class that controls the entire game
class Game:
    """Main game logic and state"""
    
    # __init__ sets up the game when it starts
    def __init__(self):
        # Create the game window with the size we specified earlier
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # Set the title that appears at the top of the window
        pygame.display.set_caption("🧦 Sock Frenzy 🧦")
        
        # Create a clock object to control the FPS (frames per second)
        self.clock = pygame.time.Clock()
        
        # Create different font sizes for text
        # Font size 72 = very large (for titles)
        self.font_large = pygame.font.Font(None, 72)
        # Font size 48 = medium (for important text)
        self.font_medium = pygame.font.Font(None, 48)
        # Font size 36 = small (for regular text)
        self.font_small = pygame.font.Font(None, 36)
        
        # The game has 3 states:
        # 'start' = showing the start screen
        # 'playing' = currently playing the game
        # 'game_over' = game finished, showing score
        self.state = 'start'
        
        # Create the player's basket
        self.player = Player()
        
        # Create an empty list to store all the socks
        # We'll add socks to this list as they appear
        self.socks = []
        
        # The player's score (how many socks they caught)
        self.score = 0
        
        # How many seconds are left in the game
        self.time_left = GAME_DURATION
        
        # A counter for when to spawn new socks
        # This prevents socks from spawning every frame (too many!)
        self.spawn_timer = 0
        
        # How many frames to wait before spawning a new sock
        # Lower number = socks spawn faster
        # We decrease this number as the game goes on to make it harder
        self.spawn_rate = 40
    
    # This function handles all player input (keyboard, mouse, closing window)
    def handle_events(self):
        """Handle user input and window events"""
        # pygame.event.get() gives us a list of all events that happened
        # Examples: key pressed, mouse click, window closed, etc.
        for event in pygame.event.get():
            
            # Check if the player clicked the X button to close the window
            if event.type == pygame.QUIT:
                return False  # Return False to stop the game loop
            
            # Check if a key was pressed
            if event.type == pygame.KEYDOWN:
                # Check if SPACE was pressed
                if event.key == pygame.K_SPACE:
                    # If we're on the start screen, start the game
                    if self.state == 'start':
                        self.start_game()
                    # If the game is over, restart it
                    elif self.state == 'game_over':
                        self.reset_game()
        
        # Return True to keep the game running
        return True
    
    # This function starts a new game
    def start_game(self):
        """Start a new game"""
        # Change state to 'playing' so the game loop knows to run the game
        self.state = 'playing'
        # Reset the score to 0
        self.score = 0
        # Reset the timer to 60 seconds
        self.time_left = GAME_DURATION
        # Clear the socks list (remove all socks)
        self.socks = []
        # Reset the spawn timer
        self.spawn_timer = 0
    
    # This function resets everything for a new game
    def reset_game(self):
        """Reset everything for a new game"""
        # Go back to the start screen
        self.state = 'start'
        # Reset score
        self.score = 0
        # Reset timer
        self.time_left = GAME_DURATION
        # Clear all socks
        self.socks = []
        # Reset spawn timer
        self.spawn_timer = 0
    
    # This is the most important function - it updates the game every frame
    def update(self):
        """Update game logic"""
        # Only update the game if we're currently playing (not on start/game_over screens)
        if self.state == 'playing':
            # Get which keys are currently being pressed
            # This returns a list of True/False for each key
            keys = pygame.key.get_pressed()
            
            # Update the player's position based on arrow key presses
            self.player.update(keys)
            
            # ===== SPAWN NEW SOCKS =====
            # Increase the spawn timer by 1 each frame
            self.spawn_timer += 1
            
            # When the spawn timer reaches spawn_rate, create a new sock
            if self.spawn_timer >= self.spawn_rate:
                # Create a new Sock object and add it to the socks list
                self.socks.append(Sock())
                # Reset the timer back to 0
                self.spawn_timer = 0
                
                # Make the game harder by spawning socks faster over time
                # Decrease spawn_rate by 0.5 (so socks appear more often)
                # But don't go below 15 (so it doesn't get IMPOSSIBLE)
                if self.spawn_rate > 15:
                    self.spawn_rate -= 0.5
            
            # ===== UPDATE ALL SOCKS =====
            # Loop through every sock in the list and make it fall
            for sock in self.socks:
                sock.update()  # This increases the sock's Y position (makes it fall)
            
            # ===== CHECK FOR COLLISIONS (CATCHING SOCKS) =====
            # Get the basket's rectangle for collision checking
            player_rect = self.player.get_rect()
            
            # [:] means we're making a copy of the list to safely remove items from it
            # We can't remove items while looping, so we loop through a copy
            for sock in self.socks[:]:
                # Create a rectangle around this sock
                sock_rect = pygame.Rect(sock.x, sock.y, sock.width, sock.height)
                
                # Check if the basket rectangle touches the sock rectangle
                if player_rect.colliderect(sock_rect):
                    # The basket caught a sock!
                    self.score += 1  # Increase score by 1
                    self.socks.remove(sock)  # Remove the sock from the list
            
            # ===== REMOVE SOCKS THAT FELL OFF THE SCREEN =====
            # Keep only socks that are still on screen
            # (This removes socks the player missed)
            self.socks = [sock for sock in self.socks if not sock.is_off_screen()]
            
            # ===== UPDATE THE TIMER =====
            # Subtract a small amount of time each frame
            # (1 second / 60 FPS = 0.0167 seconds per frame)
            self.time_left -= 1 / FPS
            
            # ===== CHECK IF TIME IS UP =====
            # If the timer reaches 0, the game is over
            if self.time_left <= 0:
                self.time_left = 0  # Make sure it doesn't go negative
                self.state = 'game_over'  # Change to game over screen
    
    # ===== DRAWING FUNCTIONS =====
    # These functions draw different parts of the game on the screen
    
    def draw_background(self):
        """Draw the game background"""
        # Fill the screen with light blue (the sky)
        self.screen.fill(LIGHT_BLUE)
        
        # Draw the ground at the bottom
        # pygame.draw.rect(screen, color, (x, y, width, height))
        pygame.draw.rect(self.screen, (200, 200, 200), (0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80))
        
        # Draw a clothesline where socks fall from
        # pygame.draw.line(screen, color, start_position, end_position, thickness)
        pygame.draw.line(self.screen, BLACK, (20, 40), (SCREEN_WIDTH - 20, 40), 3)
        
        # Draw clothesline pegs (the clips that hold the socks)
        # We draw them every 100 pixels along the line
        for i in range(0, SCREEN_WIDTH, 100):
            pygame.draw.circle(self.screen, BLACK, (i, 40), 5)
    
    def draw_washing_machines(self):
        """Draw washing machines in the background (decoration)"""
        # Left washing machine (outline)
        pygame.draw.rect(self.screen, DARK_GRAY, (30, 120, 100, 100), 5)
        # Circular door in the middle
        pygame.draw.circle(self.screen, WHITE, (80, 170), 30)
        
        # Right washing machine (outline)
        pygame.draw.rect(self.screen, DARK_GRAY, (SCREEN_WIDTH - 130, 120, 100, 100), 5)
        # Circular door in the middle
        pygame.draw.circle(self.screen, WHITE, (SCREEN_WIDTH - 80, 170), 30)
    
    def draw_start_screen(self):
        """Draw the start/welcome screen"""
        # Draw the title "SOCK FRENZY" in large text
        title = self.font_large.render("SOCK FRENZY", True, BLACK)
        # Render creates the text image
        # True = anti-aliased (smoother looking)
        # BLACK = the color of the text
        
        # Draw it on screen, centered horizontally
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Draw subtitle
        subtitle = self.font_small.render("Save the socks!", True, BLACK)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 140))
        
        # Draw instructions (three lines)
        instruct1 = self.font_small.render("Arrow Keys to Move", True, BLACK)
        instruct2 = self.font_small.render("Catch falling socks!", True, BLACK)
        instruct3 = self.font_small.render("You have 60 seconds!", True, BLACK)
        self.screen.blit(instruct1, (SCREEN_WIDTH // 2 - instruct1.get_width() // 2, 250))
        self.screen.blit(instruct2, (SCREEN_WIDTH // 2 - instruct2.get_width() // 2, 310))
        self.screen.blit(instruct3, (SCREEN_WIDTH // 2 - instruct3.get_width() // 2, 370))
        
        # Draw the "Press Space to Start" message in red (to make it stand out)
        start_text = self.font_medium.render("PRESS SPACE TO START", True, RED)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 480))
    
    def draw_game_over_screen(self):
        """Draw the game over screen"""
        # Create a dark overlay so we can see the game over text better
        # This makes a semi-transparent black square over the whole screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)  # 200 = mostly opaque (can still see through a bit)
        overlay.fill(BLACK)  # Fill it with black
        self.screen.blit(overlay, (0, 0))  # Draw it on screen
        
        # Draw "TIME'S UP!" message in red
        gameover = self.font_large.render("TIME'S UP!", True, RED)
        self.screen.blit(gameover, (SCREEN_WIDTH // 2 - gameover.get_width() // 2, 100))
        
        # Draw the final score
        score_text = self.font_medium.render(f"Socks Saved: {self.score}", True, WHITE)
        # The f-string (f"...") lets us put variables inside the text
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 250))
        
        # Draw "Play again" message in yellow
        again_text = self.font_small.render("PRESS SPACE TO PLAY AGAIN", True, YELLOW)
        self.screen.blit(again_text, (SCREEN_WIDTH // 2 - again_text.get_width() // 2, 400))
    
    def draw_hud(self):
        """Draw the score and timer during gameplay (HUD = Head Up Display)"""
        # Draw score in top left corner
        score_text = self.font_small.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (20, 10))
        
        # Draw timer in top right corner
        # int() converts the decimal time to a whole number
        timer_text = self.font_small.render(f"Time: {int(self.time_left)}s", True, BLACK)
        self.screen.blit(timer_text, (SCREEN_WIDTH - 250, 10))
    
    # This is the main draw function - it calls all other drawing functions
    def draw(self):
        """Draw everything on screen"""
        # Check which state we're in and draw accordingly
        
        if self.state == 'start':
            # Draw the starting/welcome screen
            self.draw_background()
            self.draw_washing_machines()
            self.draw_start_screen()
        
        elif self.state == 'playing':
            # Draw the actual gameplay
            self.draw_background()
            self.draw_washing_machines()
            
            # Draw all the falling socks
            for sock in self.socks:
                sock.draw(self.screen)
            
            # Draw the player's basket
            self.player.draw(self.screen)
            
            # Draw the score and timer (HUD)
            self.draw_hud()
        
        elif self.state == 'game_over':
            # Draw the game over screen
            self.draw_background()
            self.draw_washing_machines()
            
            # Draw all remaining socks (frozen in place)
            for sock in self.socks:
                sock.draw(self.screen)
            
            # Draw the game over screen with score
            self.draw_game_over_screen()
        
        # pygame.display.flip() updates the entire screen to show what we drew
        pygame.display.flip()
    
    # This is the main game loop - it keeps the game running
    async def run(self):
        """Main game loop (async so it yields to the browser each frame)"""
        # Set running to True (the game is running)
        running = True

        # This loop keeps running until the player closes the game
        while running:
            # Check for events (keyboard, mouse, window close)
            # handle_events returns False if the window was closed
            running = self.handle_events()

            # Update all game logic (move objects, check collisions, etc.)
            self.update()

            # Draw everything on screen
            self.draw()

            # Limit the frame rate to FPS (60 frames per second)
            # This prevents the game from running as fast as the computer can
            self.clock.tick(FPS)

            # Yield to the browser exactly once per frame (required by pygbag)
            await asyncio.sleep(0)

        # When the loop ends, clean up pygame (let the loop end; no sys.exit here)
        pygame.quit()


# ===== RUN THE GAME =====
# This code only runs if you run this file directly (not if you import it)
# if __name__ == "__main__": is a special Python check that means
# "only run this code if this file was executed, not imported"
async def main():
    # Create a new Game object (this initializes everything)
    game = Game()

    # Call the run() coroutine to start the game loop
    # This will keep running until the player closes the window
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())