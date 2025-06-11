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
    def __init__(self, x, y):
        self.world_x = x
        self.world_y = y
        self.speed = 200
        self.run_speed = 350
        self.scale = 2.0  
        self.rect = pygame.Rect(x, y, 128 * self.scale, 128 * self.scale)  
        self.facing_right = True
        self.attack_combo = 0
        self.animation_timer = 0
        self.current_state = "idle"
        self.animation_complete = True
    
        raider_dir = os.path.join(IMAGES_DIR, "Raider_1")
        
        try:
            idle_path = os.path.join(raider_dir, "Idle.png")
            print(f"Loading idle sprite from: {idle_path}")
        
            idle_sheet = pygame.image.load(idle_path).convert_alpha()
            print(f"Idle spritesheet size: {idle_sheet.get_size()}")
            
            self.animations = {
                "idle": AnimatedSprite(idle_path, 128, 128, 6, 200),  # 6 frames, 128x128 each
                # Temporarily comment out other animations to focus on idle
                # "walk": AnimatedSprite(os.path.join(raider_dir, "Walk.png"), 128, 128, 8, 100),
                # "run": AnimatedSprite(os.path.join(raider_dir, "Run.png"), 128, 128, 8, 80),
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
            
            for anim_name in ["walk", "run", "attack_1", "attack_2", "shot", "recharge", "hurt", "dead", "jump"]:
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
        
        if self.current_state in ["idle", "walk", "run"]:
            if keys[K_a] or keys[K_LEFT]:
                movement -= self.speed * dt / 1000
                self.facing_right = False
                is_moving = True
                
            if keys[K_d] or keys[K_RIGHT]:
                movement += self.speed * dt / 1000
                self.facing_right = True
                is_moving = True
            
            if keys[K_w] or keys[K_UP]:
                self.world_y -= self.speed * dt / 1000
                is_moving = True
                
            if keys[K_s] or keys[K_DOWN]:
                self.world_y += self.speed * dt / 1000
                is_moving = True
        
        self.world_x += movement
        
        self.world_y = max(0, min(self.world_y, 635))
      
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

def game():
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
    player = Player(100, 500)
    
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
        
        border_size = int(128 * player.scale)
        pygame.draw.rect(screen, (255, 0, 0), (player_screen_x-2, player_screen_y-2, border_size+4, border_size+4), 2)
        
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
    
    title_font = pygame.font.SysFont("Times New Roman", 72, bold=True)
    option_font = pygame.font.SysFont("Arial", 50)
    
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
                    if selected_option == 0:  # New Game
                        return "game"
                    elif selected_option == 1:  # Exit
                        return "exit"
                elif event.key == K_ESCAPE:
                    return "exit"

        menu_background.update(dt, pygame.time.get_ticks() * 0.05)
        
        screen.fill((0, 0, 0))
        menu_background.draw(screen)
        
        title_text = title_font.render("SURVIVE IF YOU CAN", True, (255, 255, 255))
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 200))
        
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected_option else (150, 150, 150)
            option_text = option_font.render(option, True, color)
            screen.blit(option_text, (WINDOW_WIDTH // 2 - option_text.get_width() // 2, 350 + i * 80))
        
        instruction_font = pygame.font.SysFont("Arial", 24)
        instructions = "Use UP/DOWN arrows to navigate, ENTER to select, ESC to exit"
        inst_text = instruction_font.render(instructions, True, (200, 200, 200))
        screen.blit(inst_text, (WINDOW_WIDTH // 2 - inst_text.get_width() // 2, WINDOW_HEIGHT - 100))
        
        pygame.display.flip()

if __name__ == "__main__":
    current_state = "menu"
    
    while True:
        if current_state == "menu":
            current_state = menu()
        elif current_state == "game":
            current_state = game()
        elif current_state == "exit":
            break
    
    pygame.quit()