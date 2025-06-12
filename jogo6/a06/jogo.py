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
        self.attack_combo = 0  # 0 for attack_1, 1 for attack_2
        self.animation_timer = 0
        self.current_state = "idle"
        self.animation_complete = True
        self.character = character
        self.is_jumping = False
        self.jump_start_y = y
        self.jump_velocity = 0
        self.gravity = 800
        self.jump_strength = -300
    
        raider_dir = os.path.join(IMAGES_DIR, character)
        
        try:
            idle_path = os.path.join(raider_dir, "Idle.png")
            print(f"Loading idle sprite from: {idle_path}")
        
            idle_sheet = pygame.image.load(idle_path).convert_alpha()
            print(f"Idle spritesheet size: {idle_sheet.get_size()}")
            
            self.animations = {
                "idle": AnimatedSprite(idle_path, 128, 128, 6, 200),
                "walk": AnimatedSprite(os.path.join(raider_dir, "Walk.png"), 128, 128, 8, 100),
                "run": AnimatedSprite(os.path.join(raider_dir, "Run.png"), 128, 128, 8, 80),
                "attack_1": AnimatedSprite(os.path.join(raider_dir, "Attack_1.png"), 128, 128, 6, 120),  # 768x128 = 6 frames
                "attack_2": AnimatedSprite(os.path.join(raider_dir, "Attack_2.png"), 128, 128, 3, 120),  # 384x128 = 3 frames
                "shot": AnimatedSprite(os.path.join(raider_dir, "Shot.png"), 128, 128, 12, 80),  # 1536x128 = 12 frames
                "jump": AnimatedSprite(os.path.join(raider_dir, "Jump.png"), 128, 128, 11, 100),  # 1408x128 = 11 frames
                "recharge": AnimatedSprite(os.path.join(raider_dir, "Recharge.png"), 128, 128, 12, 150),  # 1536x128 = 12 frames
            }
            
            fallback_surface = pygame.Surface((128, 128), pygame.SRCALPHA)
            fallback_surface.fill((0, 255, 0)) 
            
            fallback_anim = AnimatedSprite.__new__(AnimatedSprite)
            fallback_anim.frames = [fallback_surface]
            fallback_anim.current_frame = 0
            fallback_anim.frame_timer = 0
            fallback_anim.frame_count = 1
            fallback_anim.frame_duration = 200
            
            for anim_name in ["hurt", "dead"]:
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
        
        # Handle events for attacks and actions
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3 and self.current_state in ["idle", "walk", "run"]:  # Right mouse button
                    if self.attack_combo == 0:
                        self.current_state = "attack_1"
                        self.attack_combo = 1
                    else:
                        self.current_state = "attack_2"
                        self.attack_combo = 0
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
                
                elif event.button == 1 and self.current_state in ["idle", "walk", "run"]:  # Left mouse button
                    self.current_state = "shot"
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
            
            if event.type == KEYDOWN:
                if event.key == K_SPACE and self.current_state in ["idle", "walk", "run"] and not self.is_jumping:
                    self.current_state = "jump"
                    self.is_jumping = True
                    self.jump_start_y = self.world_y
                    self.jump_velocity = self.jump_strength
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
                
                elif event.key == K_r and self.current_state in ["idle", "walk", "run"]:
                    self.current_state = "recharge"
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
        
        # Handle action animations
        if self.current_state in ["attack_1", "attack_2", "shot", "recharge", "jump"]:
            self.animation_timer += dt
            
            animation_duration = len(self.current_animation.frames) * self.current_animation.frame_duration
            if self.animation_timer >= animation_duration:
                if self.current_state == "jump":
                    self.is_jumping = False
                    self.world_y = self.jump_start_y  # Reset to ground
                self.current_state = "idle"
                self.animation_complete = True
                self.animation_timer = 0
        
        # Handle jumping physics
        if self.is_jumping:
            self.jump_velocity += self.gravity * dt / 1000
            self.world_y += self.jump_velocity * dt / 1000
            
            # Land when back to ground level
            if self.world_y >= self.jump_start_y:
                self.world_y = self.jump_start_y
                self.is_jumping = False
                if self.current_state == "jump":
                    self.current_state = "idle"
        
        # Handle movement only if not performing actions
        if self.current_state in ["idle", "walk", "run"]:
            # Check if SHIFT is pressed for running
            if keys[K_LSHIFT] or keys[K_RSHIFT]:
                is_running = True
                current_speed = self.run_speed
            else:
                current_speed = self.speed
            
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
            
            # Determine movement animation state
            if is_moving:
                if is_running:
                    self.current_state = "run"
                else:
                    self.current_state = "walk"
            else:
                self.current_state = "idle"
        
        # Keep player within bounds
        self.world_y = max(375, min(self.world_y, 500))
        
        # Update current animation
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

class Zombie:
    def __init__(self, x, y):
        self.world_x = x
        self.world_y = y
        self.scale = 2.5
        self.speed = 50
        self.health = 100
        self.facing_right = False
        self.current_state = "idle"
        
        # Smaller hitbox for zombie
        hitbox_width = int(128 * self.scale * 0.3)
        hitbox_height = int(128 * self.scale * 0.4)
        self.rect = pygame.Rect(x, y, hitbox_width, hitbox_height)
        
        zombie_dir = os.path.join(IMAGES_DIR, "Zombie_1")
        
        try:
            idle_path = os.path.join(zombie_dir, "Idle.png")
            print(f"Loading zombie idle sprite from: {idle_path}")
            
            # Zombie idle animation - 768x128 means 6 frames of 128x128 each
            self.animations = {
                "idle": AnimatedSprite(idle_path, 128, 128, 6, 300),  # 6 frames, slower animation
            }
            
        except Exception as e:
            print(f"Error loading zombie sprites: {e}")
            # Create a simple fallback
            fallback_surface = pygame.Surface((128, 128))
            fallback_surface.fill((0, 150, 0))  # Green for zombie
            
            fallback_anim = AnimatedSprite.__new__(AnimatedSprite)
            fallback_anim.frames = [fallback_surface]
            fallback_anim.current_frame = 0
            fallback_anim.frame_timer = 0
            fallback_anim.frame_count = 1
            fallback_anim.frame_duration = 300
            fallback_anim.update = lambda dt: None
            fallback_anim.get_current_frame = lambda: fallback_surface
            
            self.animations = {"idle": fallback_anim}
        
        self.current_animation = self.animations["idle"]
    
    def update(self, dt, player):
        # Simple AI: move towards player
        if abs(self.world_x - player.world_x) > 50:  # Only move if not too close
            if self.world_x < player.world_x:
                self.world_x += self.speed * dt / 1000
                self.facing_right = True
            else:
                self.world_x -= self.speed * dt / 1000
                self.facing_right = False
        
        # Keep zombie within same Y bounds as player
        self.world_y = max(375, min(self.world_y, 500))
        
        # Update animation
        self.current_animation.update(dt)
        
        # Update hitbox position
        hitbox_offset_x = (int(128 * self.scale) - self.rect.width) // 2
        hitbox_offset_y = int(128 * self.scale) - self.rect.height - 20
        
        self.rect.x = self.world_x + hitbox_offset_x
        self.rect.y = self.world_y + hitbox_offset_y
    
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
                fallback.fill((0, 150, 0))
                return fallback
        except Exception as e:
            print(f"Error getting zombie image: {e}")
            fallback = pygame.Surface((int(128 * self.scale), int(128 * self.scale)))
            fallback.fill((0, 150, 0))
            return fallback

class ZombieSpawner:
    def __init__(self):
        self.zombies = []
        self.spawn_points = []
        self.last_spawn_x = 0
        self.spawn_distance = 800  # Distance between spawn points
        
    def update(self, player, dt):
        # Check if we need to spawn more zombies
        player_progress = player.world_x
        
        # Create spawn points ahead of player
        while self.last_spawn_x < player_progress + 2000:  # Keep spawns 2000 units ahead
            self.last_spawn_x += self.spawn_distance
            # Random Y position within bounds
            spawn_y = 375 + (500 - 375) * (hash(self.last_spawn_x) % 100) / 100
            self.spawn_points.append((self.last_spawn_x, spawn_y))
        
        # Spawn zombies from spawn points that are close to player
        for spawn_point in self.spawn_points[:]:
            spawn_x, spawn_y = spawn_point
            if abs(spawn_x - player_progress) < 1000 and spawn_x > player_progress - 500:
                # Check if there's already a zombie near this spawn point
                zombie_exists = any(abs(zombie.world_x - spawn_x) < 100 for zombie in self.zombies)
                if not zombie_exists:
                    new_zombie = Zombie(spawn_x, spawn_y)
                    self.zombies.append(new_zombie)
                    self.spawn_points.remove(spawn_point)
        
        # Update all zombies
        for zombie in self.zombies[:]:
            zombie.update(dt, player)
            
            # Remove zombies that are too far behind player
            if zombie.world_x < player_progress - 1500:
                self.zombies.remove(zombie)
    
    def draw(self, screen, camera_x):
        for zombie in self.zombies:
            zombie_screen_x = zombie.world_x - camera_x
            zombie_screen_y = zombie.world_y
            
            # Only draw zombies that are on screen
            if -200 < zombie_screen_x < WINDOW_WIDTH + 200:
                zombie_image = zombie.get_image()
                screen.blit(zombie_image, (zombie_screen_x, zombie_screen_y))
                
                # Draw zombie hitbox for debugging
                hitbox_screen_x = zombie.rect.x - camera_x
                hitbox_screen_y = zombie.rect.y
                pygame.draw.rect(screen, (0, 255, 0), (hitbox_screen_x-1, hitbox_screen_y-1, zombie.rect.width+2, zombie.rect.height+2), 1)

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
    zombie_spawner = ZombieSpawner()
    
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
        
        # Update zombie spawner
        zombie_spawner.update(player, dt)
        
        camera_x = max(0, player.world_x - WINDOW_WIDTH // 2)
        game_background.update(dt, camera_x)
    
        screen.fill((0, 0, 0))
        game_background.draw(screen)
        
        # Draw zombies
        zombie_spawner.draw(screen, camera_x)
        
        player_screen_x = player.world_x - camera_x
        player_screen_y = player.world_y
        
        # Aplicar offset visual durante a animação de shot
        if player.current_state == "shot":
            shot_offset = 70  # Pixels para frente durante o tiro
            if player.facing_right:
                player_screen_x += shot_offset  # Move sprite para a direita
            else:
                player_screen_x -= shot_offset  # Move sprite para a esquerda
        
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
            f"Attack Combo: {player.attack_combo}",
            f"Zombies: {len(zombie_spawner.zombies)}",
            f"Jumping: {player.is_jumping}"
        ]
        
        for i, info in enumerate(ui_info):
            text = font.render(info, True, (255, 255, 255))
            screen.blit(text, (10, 10 + i * 20))
        
        instructions = [
            "WASD - Move, SHIFT - Run",
            "Right Click - Attack, Left Click - Shoot",
            "SPACE - Jump, R - Reload",
            "ESC - Back to Menu"
        ]
        instruction_font = pygame.font.SysFont("Arial", 16)
        for i, instruction in enumerate(instructions):
            inst_text = instruction_font.render(instruction, True, (255, 255, 255))
            screen.blit(inst_text, (10, 130 + i * 20))
        
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
                        return "game"
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
    
    while True:
        if current_state == "menu":
            current_state = menu()
        elif current_state == "game":
            current_state = game("Raider_1")
        elif current_state == "exit":
            break
    
    pygame.quit()