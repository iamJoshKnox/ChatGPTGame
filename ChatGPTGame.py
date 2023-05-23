import pygame
from pygame.locals import *
import pygame.mixer
import random
import sys

pygame.init()
pygame.mixer.init()

# Set up the game window
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up fonts
game_over_font = pygame.font.SysFont(None, 48)
score_font = pygame.font.SysFont(None, 24)
high_scores_font = pygame.font.SysFont(None, 24, bold=True)  # Set the font size to 24
user_high_score_font = pygame.font.SysFont(None, 28, bold=True)  # Larger font size for the user's score

# Theme music
pygame.mixer.music.load("theme.mp3")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Cursor Blink
cursor_visible = True
cursor_timer = 0

# High Score Blink
high_score_visible = True
high_score_timer = 0

# Game initialization
pygame.display.set_caption("TrumpRunner v2")
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
falling_objects = pygame.sprite.Group()
shooting_objects = pygame.sprite.Group() # Group to hold the shooting objects
building_objects = pygame.sprite.Group() # Group to hold the building objects

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.image = pygame.image.load("player.png")  # Load the player image
        self.image = pygame.transform.scale(self.image, (60, 60))  # Resize the image
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.centery = HEIGHT - 50  # Start lower on the screen
        self.speed = 5
        self.shooting = False  # Track if shooting key is pressed
        self.building = False  # Track if building key is pressed

        # Add the sprite to apropriate groups upon instantiation
        all_sprites.add(self)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.rect.x -= self.speed
        if keys[K_RIGHT]:
            self.rect.x += self.speed
        if keys[K_UP]:
            self.rect.y -= self.speed
        if keys[K_DOWN]:
            self.rect.y += self.speed

        # Keep the player within the screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        
        # Shoot the coin when 'a' key is pressed down
        if keys[K_a] and not self.shooting:
            self.shoot()
            self.shooting = True

        # Reset shooting flag when 'a' key is released
        if not keys[K_a] and self.shooting:
            self.shooting = False

        # Build wall when 'b' key is pressed down
        if keys[K_b] and not self.building:
            self.build()
            self.building = True
            buildawall_sound = pygame.mixer.Sound("buildawall.mp3")
            buildawall_sound.set_volume(.4)
            buildawall_sound.play()

        # Reset build wall flag when 'b' key is released
        if not keys[K_b] and self.building:
            self.building = False
    
    def shoot(self):
        shooting_object = ShootingObject(self.rect.centerx, self.rect.top)
        shooting_objects.add(shooting_object)
    
    def build(self):
        building_object = BuildingObject(self.rect.centerx, self.rect.top)
        building_objects.add(building_object)

# Shooting object class
class ShootingObject(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(ShootingObject, self).__init__()
        self.image = pygame.image.load("coin.png")  # Load the "coin.png" image
        self.image = pygame.transform.scale(self.image, (30, 30))  # Resize the image if needed
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 5

        # Add the sprite to appropriate groups upon instantiation
        all_sprites.add(self)
        shooting_objects.add(self)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()  # Remove the shooting object if it goes off the screen

        # Check for collisions with falling objects
        collisions = pygame.sprite.spritecollide(self, falling_objects, True)
        for obj in collisions:
            if isinstance(obj, FallingDocumentsObject):
                
                # Play the sound effect
                fired_sound = pygame.mixer.Sound("fired.mp3")
                fired_sound.set_volume(.4)
                fired_sound.play()
                
                #remove falling object and shooting object
                obj.kill()
                self.kill()

# Building object class
class BuildingObject(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(BuildingObject, self).__init__()
        self.image = pygame.image.load("wall.png")  # Load the "wall.png" image
        self.image = pygame.transform.scale(self.image, (60, 60))  # Resize the image if needed
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 5

        # Add the sprite to appropriate groups upon instantiation
        all_sprites.add(self)
        building_objects.add(self)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()  # Remove the shooting object if it goes off the screen

        # Check for collisions with falling objects
        collisions = pygame.sprite.spritecollide(self, falling_objects, True)
        for obj in collisions:
            if isinstance(obj, FallingDocumentsObject):
                
                # Play the sound effect
                fired_sound = pygame.mixer.Sound("wall.mp3")
                fired_sound.set_volume(.4)
                fired_sound.play()
                
                #remove falling object and shooting object
                obj.kill()
                self.kill()

# Falling object class
class FallingObject(pygame.sprite.Sprite):
    """
    Creates a uniformly sized falling object sprite from an image file.
    The falling speed will be a random int between 1-5, unless specificied.

    Treat this superclass as abstract, and only call the subclasses directly.
    """

    def __init__(self, image_path, speed=random.randint(1, 5)):
        super(FallingObject, self).__init__()
        image = pygame.image.load(image_path)  # Load the specified image
        self.image = pygame.transform.scale(image, (40, 40))  # Resize the image if needed
        self.speed = speed

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        
        # Add the sprite to apropriate groups upon instantiation
        falling_objects.add(self)
        all_sprites.add(self)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()  # Remove the object when it goes off the screen

class FallingMoneyObject(FallingObject):
    """ Subclass of `FallingObject` for the 'money' sprite. """
    def __init__(self):
        super(FallingMoneyObject, self).__init__("money.png")

class FallingDocumentsObject(FallingObject):
    """ Subclass of `FallingObject` for the 'document' sprite. """
    def __init__(self):
        super(FallingDocumentsObject, self).__init__("documents.png")

class FallingPowerUpObject(FallingObject):
    """
    Subclass of `FallingObject` for the 'power-up' sprite.
    
    Note the speed is always maxed out to make it special.
    """
    def __init__(self):
        super(FallingPowerUpObject, self).__init__("coin.png", 5)


def create_random_falling_object(difficulty=50):
    """
    Randomly returns either a `FallingMoneyObject` or a `FallingDocumentsObject`.
    
    `difficulty` should be a number between 0-100 and represents the percentage
    chance of returning a `FallingDocumentsObject`.
    """
    if (difficulty > random.randrange(0, 100)):
        return FallingDocumentsObject()
    else:
        return FallingMoneyObject()

player = Player()

game_over = False
score = 0
level = 0
powerup_count = 0
initials = ""
input_active = True  # Flips to false if score is too low OR if already entered.

game_over_font = pygame.font.SysFont(None, 60)  # Increase the game over text size
restart_font = pygame.font.SysFont(None, 24)
restart_text = restart_font.render("Press SPACE to restart", True, WHITE)
restart_text_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))  # Adjust the position of the restart text

def load_high_scores():
    high_scores = []
    try:
        with open("high_scores.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                score, initials = line.strip().split(",")
                high_scores.append({"score": int(score), "initials": initials.upper()})
    except FileNotFoundError:
        pass
    return high_scores

def update_high_scores():
    high_scores = load_high_scores()
    high_scores.append({"score": score, "initials": initials.upper()})
    high_scores.sort(key=lambda x: x["score"], reverse=True)
    high_scores = high_scores[:5]  # Keep only the top 5 scores
    with open("high_scores.txt", "w") as file:
        for entry in high_scores:
            file.write(f"{entry['score']},{entry['initials']}\n")

# Draw the powerup inidcator
def draw_powerup_indicator():
    power_up_image = pygame.image.load("coin.png")
    power_up_image = pygame.transform.scale(power_up_image, (30, 30))
    power_up_spacing = 5
    for i in range(powerup_count):
        power_up_x = WIDTH - (i + 1) * (power_up_image.get_width() + power_up_spacing)
        power_up_y = power_up_spacing * 2
        screen.blit(power_up_image, (power_up_x, power_up_y))

# Turn on music
pygame.mixer.music.play(-1)  #Plays music on infinite loop

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
                    
        elif game_over:
            if event.type == KEYDOWN and event.key == K_SPACE:
                # Reset game entities
                game_over = False
                all_sprites.empty()
                all_sprites.add(player)
                # Reset scoreboard logic
                input_active = True # Flips to false if score is too low OR if already entered.
                score = 0
                level = 0
                powerup_count = 0
                initials = ""
                # Reset music
                pygame.mixer.music.play(-1)  #Plays music on infinite loop

                # Reset falling objects
                falling_objects.empty()

            elif event.type == KEYDOWN and input_active:
                if event.key == K_RETURN:
                    # Save initials and update high scores
                    if initials != "":
                        update_high_scores()
                        input_active = False
                elif event.key == K_BACKSPACE:
                    # Remove the last character from initials
                    initials = initials[:-1]
                elif len(initials) < 3:
                    # Append the pressed key to initials until there are 3 characters
                    initials += event.unicode

    if not game_over:
        # Add falling falling_objects
        object_chance = random.randint(1, 100)
        if object_chance <= 5:
            # TODO: Use the `difficulty` parameter (based on the time passed, perhaps)
            #Level ideas:
            #One gold coin falls
            #Money falls
            #Money and documents begin to fall
            #More documents
            #less random documents (maybe add some diagonal shapes which will force user side-to-side)


            #Level Timing:
            #0:03 Super Easy Mode
            #0:21 Baby Mode
            #0:39 Easy Mode
            #0:53 Normal Mode
            #1:02 Left Hand Workout Mode
            #1:08 Hard Mode
            #1:14 Right Hand Workout mode
            #1:20 Right Hand Workout mode+
            #1:26 Dual Hand Challenge Mode
            #1:38 Tetris Mode
            #1:51 Extra Russian Mode
            #2:08 Advanced Tetris Mode
            #2:13 Tetris Master Mode
            #2:20 Tetris Master Mode+
            #2:25 Deceptive Mode
            #2:35 Elite Mode
            #2:47 Champion Mode
            #2:56 Ultra Mega Death Mode+++
            #3:03 Apocalypse Mode
            #3:09 ?!?!??!?!!??!? Mode
            #3:23 END

            create_random_falling_object()

        all_sprites.update()

        # Spawn power-ups
        if score % 1000 == 0:
            new_power_up = FallingPowerUpObject()

        # Check for collisions with falling falling_objects
        collisions = pygame.sprite.spritecollide(player, falling_objects, True)
        for obj in collisions:
            if isinstance(obj, FallingDocumentsObject):
                game_over = True
                #TODO: Early Return
            if isinstance(obj, FallingMoneyObject):
                score += 100
                #TODO: I'm not sure why the shooting object kills the money
            if isinstance(obj, FallingPowerUpObject):
                #TODO: Give this a better name.
                powerup_count += 1

        # Increase the score
        score += 1

    screen.fill(BLACK)

    # Draw sprites
    all_sprites.draw(screen)

    if game_over:
        pygame.mixer.music.stop()  # Stop the music if the game is over
        game_over_text = game_over_font.render("Game Over", True, YELLOW)
        game_over_text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

        screen.blit(game_over_text, game_over_text_rect)
        screen.blit(restart_text, restart_text_rect)

        high_scores = load_high_scores()

        # Check if the player achieved a high score
        if input_active and ((len(high_scores) < 5 or score > high_scores[-1]['score'])):
            input_rect = pygame.Rect(300, 250, 45, 32)  # Adjust the position and size of the input box
        else:
            input_active = False

        # Draw the high scores
        high_scores_text = high_scores_font.render("HIGH SCORES:", True, WHITE)
        high_scores_text_rect = high_scores_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 75))
        screen.blit(high_scores_text, high_scores_text_rect)

        y_offset = 0
        for i, entry in enumerate(high_scores):
            ranking = f"#{i+1}"  # Calculate the ranking
            old_initials = entry["initials"]
            old_score = entry["score"]
            high_score_text = score_font.render(f"{ranking}: {old_initials}: {old_score}", True, WHITE)
            high_score_text_rect = high_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 105 + y_offset))
            screen.blit(high_score_text, high_score_text_rect)
            y_offset += 28

        # Draw the input box if active
        if input_active:
                       
            high_score_label = game_over_font.render("HIGH SCORE!", True, WHITE)
            high_score_label_rect = high_score_label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 150))
            screen.blit(high_score_label, high_score_label_rect)

            if len(initials) == 3 or not cursor_visible:
                player_score_text = game_over_font.render(str(score), True, WHITE)
                player_score_text_rect = player_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
                screen.blit(player_score_text, player_score_text_rect)

            pygame.draw.rect(screen, WHITE, input_rect, 2)
            initials_text = score_font.render(initials.upper(), True, WHITE)
            screen.blit(initials_text, input_rect.move(5, 8))

            # Draw the blinking cursor if the length of initials is less than 3
            if len(initials) < 3 and cursor_visible:
                cursor_rect = pygame.Rect(input_rect.x + initials_text.get_width() + 2, input_rect.y + input_rect.height // 2 - 10, 12, input_rect.height - 14)
                pygame.draw.rect(screen, WHITE, cursor_rect)
            
            # Update the cursor timer
            cursor_timer += 1
            if cursor_timer >= 30:
                cursor_visible = not cursor_visible
                cursor_timer = 0  # Reset the timer

    # Draw the score
    score_text = score_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Draw the level
    level_text = score_font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (13, 30))

    draw_powerup_indicator()

    pygame.display.flip()
    clock.tick(60)
