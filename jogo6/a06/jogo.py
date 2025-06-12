import os
import pygame
from pygame.locals import *

pygame.init()

WINDOW_WIDTH = pygame.display.Info().current_w
WINDOW_HEIGHT = pygame.display.Info().current_h

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Survive If You Can")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "imagens")

class AnimatedSprite:
    def __init__(self, spritesheet_path, frame_width, frame_height, frame_count, frame_duration=100):
        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_count = frame_count
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.frame_timer = 0
        self.frames = []

        for i in range(frame_count):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(self.spritesheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
            self.frames.append(frame)
    
    def update(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.frame_timer = 0
    
    def get_current_frame(self):
        return self.frames[self.current_frame]
    
    def reset(self):
        self.current_frame = 0
        self.frame_timer = 0

class Background:
    def __init__(self, layers, speeds):
        self.layers = layers
        self.speeds = speeds
        self.positions = [0] * len(layers)
    
    def update(self, dt, camera_x):
        for i in range(len(self.layers)):
            self.positions[i] = -camera_x * self.speeds[i]
    
    def draw(self, screen):
        for i, layer in enumerate(self.layers):
            x = self.positions[i] % WINDOW_WIDTH
            screen.blit(layer, (x, 0))
            if x > 0:
                screen.blit(layer, (x - WINDOW_WIDTH, 0))

class Player:
    def __init__(self, x, y, character="Raider_1"):
        self.world_x = x
        self.world_y = y
        self.speed = 200
        self.run_speed = 350
        self.scale = 3.0  
        hitbox_width = int(128 * self.scale * 0.2)
        hitbox_height = int(128 * self.scale * 0.4)
        self.rect = pygame.Rect(x, y, hitbox_width, hitbox_height)
        self.facing_right = True
        self.attack_combo = 0
        self.animation_timer = 0
        self.current_state = "idle"
        self.animation_complete = True
        self.character = character
    
        raider_dir = os.path.join(IMAGES_DIR, character)
        
        try:
            idle_path = os.path.join(raider_dir, "Idle.png")
            print(f"Loading idle sprite from: {idle_path}")
        
            idle_sheet = pygame.image.load(idle_path).convert_alpha()
            print(f"Idle spritesheet size: {idle_sheet.get_size()}")
            
            self.animations = {
                "idle": AnimatedSprite(idle_path, 128, 128, 6, 200),  # 6 frames, 128x128 each
                "walk": AnimatedSprite(os.path.join(raider_dir, "Walk.png"), 128, 128, 8, 100),
                "run": AnimatedSprite(os.path.join(raider_dir, "Run.png"), 128, 128, 8, 80),
                # "attack_1": AnimatedSprite(os.path.join(raider_dir, "Attack_1.png"), 128, 128, 4, 150),
                # "attack_2": AnimatedSprite(os.path.join(raider_dir, "Attack_2.png"), 128, 128, 4, 150),
                # "shot": AnimatedSprite(os.path.join(raider_dir, "Shot.png"), 128, 128, 4, 120),
                # "recharge": AnimatedSprite(os.path.join(raider_dir, "Recharge.png"), 128, 128, 4, 200),
                # "hurt": AnimatedSprite(os.path.join(raider_dir, "Hurt.png"), 128, 128, 3, 150),
                # "dead": AnimatedSprite(os.path.join(raider_dir, "Dead.png"), 128, 128, 4, 200),
                # "jump": AnimatedSprite(os.path.join(raider_dir, "Jump.png"), 128, 128, 4, 150)
            }
            
            fallback_surface = pygame.Surface((128, 128), pygame.SRCALPHA)
            fallback_surface.fill((0, 255, 0)) 
            
            fallback_anim = AnimatedSprite.__new__(AnimatedSprite)
            fallback_anim.frames = [fallback_surface]
            fallback_anim.current_frame = 0
            fallback_anim.frame_timer = 0
            fallback_anim.frame_count = 1
            fallback_anim.frame_duration = 200
            
            for anim_name in ["attack_1", "attack_2", "shot", "recharge", "hurt", "dead", "jump"]:
                self.animations[anim_name] = fallback_anim
            
        except Exception as e:
            print(f"Error loading sprites: {e}")
            # Create a simple fallback
            fallback_surface = pygame.Surface((128, 128))
            fallback_surface.fill((255, 0, 0))  
            
            fallback_anim = AnimatedSprite.__new__(AnimatedSprite)
            fallback_anim.frames = [fallback_surface]
            fallback_anim.current_frame = 0
            fallback_anim.frame_timer = 0
            fallback_anim.frame_count = 1
            fallback_anim.frame_duration = 200
            fallback_anim.update = lambda dt: None
            fallback_anim.get_current_frame = lambda: fallback_surface
            
            self.animations = {"idle": fallback_anim}
            for anim_name in ["walk", "run", "attack_1", "attack_2", "shot", "recharge", "hurt", "dead", "jump"]:
                self.animations[anim_name] = fallback_anim
        
        self.current_animation = self.animations["idle"]
        
    def update(self, keys, dt, mouse_buttons, events):
        movement = 0
        is_moving = False
        is_running = False
        
        if self.current_state in ["attack_1", "attack_2", "shot", "recharge"]:
            self.animation_timer += dt
            if self.animation_timer >= len(self.current_animation.frames) * self.current_animation.frame_duration:
                self.current_state = "idle"
                self.animation_complete = True
                self.animation_timer = 0
        
        # Check if SHIFT is pressed for running
        if keys[K_LSHIFT] or keys[K_RSHIFT]:
            is_running = True
            current_speed = self.run_speed
        else:
            current_speed = self.speed
        
        if self.current_state in ["idle", "walk", "run"]:
            if keys[K_a] or keys[K_LEFT]:
                movement -= current_speed * dt / 1000
                self.facing_right = False
                is_moving = True
                
            if keys[K_d] or keys[K_RIGHT]:
                movement += current_speed * dt / 1000
                self.facing_right = True
                is_moving = True
            
            if keys[K_w] or keys[K_UP]:
                self.world_y -= current_speed * dt / 1000
                is_moving = True
                
            if keys[K_s] or keys[K_DOWN]:
                self.world_y += current_speed * dt / 1000
                is_moving = True
        
        self.world_x += movement
        
        self.world_y = max(375, min(self.world_y, 500))
      
        # Determine animation state based on movement and running
        if is_moving:
            if is_running:
                self.current_state = "run"
            else:
                self.current_state = "walk"
        else:
            self.current_state = "idle"
        
        self.current_animation = self.animations[self.current_state]
        self.current_animation.update(dt)
        
        return movement
    
    def get_image(self):
        try:
            image = self.current_animation.get_current_frame()
            if image and image.get_width() > 0 and image.get_height() > 0:
                if not self.facing_right:
                    image = pygame.transform.flip(image, True, False)
                
                scaled_size = (int(128 * self.scale), int(128 * self.scale))
                image = pygame.transform.scale(image, scaled_size)
                return image
            else:
                
                fallback = pygame.Surface((int(128 * self.scale), int(128 * self.scale)))
                fallback.fill((255, 255, 0))  
                return fallback
        except Exception as e:
            print(f"Error getting player image: {e}")
            fallback = pygame.Surface((int(128 * self.scale), int(128 * self.scale)))
            fallback.fill((255, 0, 255))  
            return fallback

def character_selection():
    clock = pygame.time.Clock()
    running = True
    
    # Character options
    characters = ["Raider_1", "Raider_2", "Raider_3"]
    selected_character = 0
    
    # Load character animations for preview
    character_previews = {}
    for char in characters:
        try:
            char_dir = os.path.join(IMAGES_DIR, char)
            idle_path = os.path.join(char_dir, "Idle.png")
            if os.path.exists(idle_path):
                character_previews[char] = AnimatedSprite(idle_path, 128, 128, 6, 200)
            else:
                # Fallback
                fallback_surface = pygame.Surface((128, 128))
                fallback_surface.fill((100, 100, 100))
                fallback_anim = AnimatedSprite.__new__(AnimatedSprite)
                fallback_anim.frames = [fallback_surface]
                fallback_anim.current_frame = 0
                fallback_anim.frame_timer = 0
                fallback_anim.frame_count = 1
                fallback_anim.frame_duration = 200
                fallback_anim.update = lambda dt: None
                fallback_anim.get_current_frame = lambda: fallback_surface
                character_previews[char] = fallback_anim
        except Exception as e:
            print(f"Error loading {char}: {e}")
            # Create fallback
            fallback_surface = pygame.Surface((128, 128))
            fallback_surface.fill((100, 100, 100))
            fallback_anim = AnimatedSprite.__new__(AnimatedSprite)
            fallback_anim.frames = [fallback_surface]
            fallback_anim.current_frame = 0
            fallback_anim.frame_timer = 0
            fallback_anim.frame_count = 1
            fallback_anim.frame_duration = 200
            fallback_anim.update = lambda dt: None
            fallback_anim.get_current_frame = lambda: fallback_surface
            character_previews[char] = fallback_anim
    
    title_font = pygame.font.SysFont("Impact", 80)
    instruction_font = pygame.font.SysFont("Arial", 24)

    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return "exit", None
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    selected_character = (selected_character - 1) % len(characters)
                elif event.key == K_RIGHT:
                    selected_character = (selected_character + 1) % len(characters)
                elif event.key == K_RETURN:
                    return "game", characters[selected_character]
                elif event.key == K_ESCAPE:
                    return "menu", None

        # Update character animations
        for char_anim in character_previews.values():
            char_anim.update(dt)
        
        # Black background
        screen.fill((0, 0, 0))
        
        title_text = title_font.render("SELECT CHARACTER", True, (255, 255, 255))
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 150))
        
        # Character previews (larger size)
        char_spacing = WINDOW_WIDTH // 4
        char_y = WINDOW_HEIGHT // 2 - 200
        char_size = 320  # Increased from 256
        
        for i, char in enumerate(characters):
            char_x = char_spacing * (i + 1) - char_size // 2
            
            # Character preview
            char_image = character_previews[char].get_current_frame()
            scaled_char = pygame.transform.scale(char_image, (char_size, char_size))
            
            # Selection border (red color)
            if i == selected_character:
                pygame.draw.rect(screen, (255, 0, 0), (char_x - 5, char_y - 5, char_size + 10, char_size + 10), 4)
            else:
                pygame.draw.rect(screen, (100, 100, 100), (char_x - 5, char_y - 5, char_size + 10, char_size + 10), 2)
            
            screen.blit(scaled_char, (char_x, char_y))
        
        # Instructions
        instructions = [
            "Use LEFT/RIGHT arrows to select character",
            "ENTER to confirm selection, ESC to go back"
        ]
        for i, instruction in enumerate(instructions):
            inst_text = instruction_font.render(instruction, True, (200, 200, 200))
            screen.blit(inst_text, (WINDOW_WIDTH // 2 - inst_text.get_width() // 2, WINDOW_HEIGHT - 100 + i * 30))
        
        pygame.display.flip()

def game(selected_character="Raider_1"):
    clock = pygame.time.Clock()
    running = True
    
    game_layers = []
    game_speeds = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    GAME_BG_DIR = os.path.join(IMAGES_DIR, "Postapocalypce4", "Pale")
    game_layer_files = ["bg.png", "rail&wall.png", "train.png", "columns&floor.png", "infopost&wires.png", "wires.png"]
    
    for filename in game_layer_files:
        path = os.path.join(GAME_BG_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
            game_layers.append(img)
    
    game_background = Background(game_layers, game_speeds)
    player = Player(100, 450, selected_character)
    
    while running:
        dt = clock.tick(60)
        events = pygame.event.get()
        
        for event in events:
            if event.type == QUIT:
                return "exit"
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "menu"
        
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        player.update(keys, dt, mouse_buttons, events)
        
        camera_x = max(0, player.world_x - WINDOW_WIDTH // 2)
        game_background.update(dt, camera_x)
    
        screen.fill((0, 0, 0))
        game_background.draw(screen)
        
        player_screen_x = player.world_x - camera_x
        player_screen_y = player.world_y
        player_image = player.get_image()
        
        # Update hitbox position - center it on the character
        hitbox_offset_x = (int(128 * player.scale) - player.rect.width) // 2
        hitbox_offset_y = int(128 * player.scale) - player.rect.height - 20  # 20 pixels from bottom
        
        player.rect.x = player.world_x + hitbox_offset_x
        player.rect.y = player.world_y + hitbox_offset_y
        
        # Draw smaller hitbox for debugging (red border shows actual collision area)
        hitbox_screen_x = player.rect.x - camera_x
        hitbox_screen_y = player.rect.y
        pygame.draw.rect(screen, (255, 0, 0), (hitbox_screen_x-2, hitbox_screen_y-2, player.rect.width+4, player.rect.height+4), 2)
        
        screen.blit(player_image, (player_screen_x, player_screen_y))
        
        font = pygame.font.SysFont("Arial", 18)
        ui_info = [
            f"Position: {int(player.world_x)}, {int(player.world_y)}",
            f"State: {player.current_state}",
            f"Facing: {'Right' if player.facing_right else 'Left'}",
            f"Current Frame: {player.current_animation.current_frame}",
            f"Image Size: {player_image.get_size()}",
            f"Scale: {player.scale}x"
        ]
        
        for i, info in enumerate(ui_info):
            text = font.render(info, True, (255, 255, 255))
            screen.blit(text, (10, 10 + i * 20))
        
        instructions = [
            "WASD - Move (Basic movement for testing)",
            "ESC - Back to Menu"
        ]
        instruction_font = pygame.font.SysFont("Arial", 16)
        for i, instruction in enumerate(instructions):
            inst_text = instruction_font.render(instruction, True, (255, 255, 255))
            screen.blit(inst_text, (10, 120 + i * 20))
        
        pygame.display.flip()

def menu():
    clock = pygame.time.Clock()
    running = True
    
    menu_layers = []
    menu_speeds = [0.2, 0.4, 0.7, 1.0, 1.5, 2.0]
    MENU_BG_DIR = os.path.join(IMAGES_DIR, "Postapocalypce2", "Bright")
    menu_layer_files = ["sky.png", "houses&trees_bg.png", "houses.png", "car_trees_etc.png", "fence.png", "road.png"]
    
    for filename in menu_layer_files:
        path = os.path.join(MENU_BG_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
            menu_layers.append(img)
    
    menu_background = Background(menu_layers, menu_speeds)
    
    title_font = pygame.font.SysFont("Impact", 80)
    option_font = pygame.font.SysFont("Impact", 50)
    
    selected_option = 0
    options = ["New Game", "Exit"]

    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return "exit"
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == K_RETURN:
                    if selected_option == 0:  
                        return "character_selection"
                    elif selected_option == 1:  
                        return "exit"
                elif event.key == K_ESCAPE:
                    return "exit"

        menu_background.update(dt, pygame.time.get_ticks() * 0.05)
        
        screen.fill((0, 0, 0))
        menu_background.draw(screen)
        
        title_text = "SURVIVE IF YOU CAN"
        title_y = 200
        
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    border_text = title_font.render(title_text, True, (0, 0, 0))
                    screen.blit(border_text, (WINDOW_WIDTH // 2 - border_text.get_width() // 2 + dx, title_y + dy))
        
        main_title = title_font.render(title_text, True, (255, 255, 255))
        screen.blit(main_title, (WINDOW_WIDTH // 2 - main_title.get_width() // 2, title_y))
        
        # Menu options positioned lower and with red selection color
        for i, option in enumerate(options):
            color = (255, 0, 0) if i == selected_option else (150, 150, 150)
            option_text = option_font.render(option, True, color)
            screen.blit(option_text, (WINDOW_WIDTH // 2 - option_text.get_width() // 2, 450 + i * 80))
        
        instruction_font = pygame.font.SysFont("Arial", 24)
        instructions = "Use UP/DOWN arrows to navigate, ENTER to select, ESC to exit"
        inst_text = instruction_font.render(instructions, True, (200, 200, 200))
        screen.blit(inst_text, (WINDOW_WIDTH // 2 - inst_text.get_width() // 2, WINDOW_HEIGHT - 100))
        
        pygame.display.flip()

if __name__ == "__main__":
    current_state = "menu"
    selected_character = "Raider_1"
    
    while True:
        if current_state == "menu":
            current_state = menu()
        elif current_state == "character_selection":
            current_state, selected_character = character_selection()
            if selected_character is None:
                selected_character = "Raider_1"
        elif current_state == "game":
            current_state = game(selected_character)
        elif current_state == "exit":
            break
    
    pygame.quit()