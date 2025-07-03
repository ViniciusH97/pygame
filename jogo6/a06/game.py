import os
import pygame
from pygame.locals import *
from background import Background
from player import Player
from zombie_spawner import ZombieSpawner

def create_game_background():
    """Create and return game background"""
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
    
    game_layers = []
    game_speeds = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    GAME_BG_DIR = os.path.join(IMAGES_DIR, "Postapocalypce4", "Pale")
    game_layer_files = ["bg.png", "rail&wall.png", "train.png", "columns&floor.png", "wires.png"]
    
    window_width = pygame.display.get_surface().get_width()
    window_height = pygame.display.get_surface().get_height()
    
    for filename in game_layer_files:
        path = os.path.join(GAME_BG_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (window_width, window_height))
            game_layers.append(img)
    
    return Background(game_layers, game_speeds)

def game(selected_character="Raider_1"):
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.get_surface()
    window_width = screen.get_width()
    window_height = screen.get_height()
    
    game_background = create_game_background()
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
        
        zombie_spawner.update(player, dt)
        zombie_spawner.check_player_attacks(player)
        
        camera_x = max(0, player.world_x - window_width // 2)
        game_background.update(dt, camera_x)
    
        screen.fill((0, 0, 0))
        game_background.draw(screen)
        
        # spawna os zumbie na tela
        zombie_spawner.draw(screen, camera_x)
        
        # plot os hitboxes na tela
        if True:  
            for zombie in zombie_spawner.zombies:
                if not zombie.is_dead:
                    melee_rect_screen = pygame.Rect(
                        zombie.melee_rect.x - camera_x, 
                        zombie.melee_rect.y, 
                        zombie.melee_rect.width, 
                        zombie.melee_rect.height
                    )
                    pygame.draw.rect(screen, (255, 0, 0), melee_rect_screen, 2)  # definição de cor vermelha
                    
                    # Draw ranged hitbox in blue
                    ranged_rect_screen = pygame.Rect(
                        zombie.ranged_rect.x - camera_x, 
                        zombie.ranged_rect.y, 
                        zombie.ranged_rect.width, 
                        zombie.ranged_rect.height
                    )
                    pygame.draw.rect(screen, (0, 0, 255), ranged_rect_screen, 2)  # definição de cor azul
        
        player_screen_x = player.world_x - camera_x
        player_screen_y = player.world_y
        
        # Aplicar offset visual durante a animação de shot
        if player.current_state == "shot":
            shot_offset = 70  # Pixels para frente durante o tiro
            if player.facing_right:
                player_screen_x += shot_offset  
            else:
                player_screen_x -= shot_offset  
        
        player_image = player.get_image()
        
        
        hitbox_offset_x = (int(128 * player.scale) - player.rect.width) // 2
        hitbox_offset_y = int(128 * player.scale) - player.rect.height - 20  
        
        player.rect.x = player.world_x + hitbox_offset_x
        player.rect.y = player.world_y + hitbox_offset_y
        
        # mostra o player na tela
        screen.blit(player_image, (player_screen_x, player_screen_y))
        
        # mostra a barra de vida e a munição do player
        player.draw_health_bar(screen)
        player.draw_ammo_counter(screen)
        
        # Draw UI info
        font = pygame.font.SysFont("Arial", 18)
        ui_info = [
            f"Position: {int(player.world_x)}, {int(player.world_y)}",
            f"State: {player.current_state}",
            f"Facing: {'Right' if player.facing_right else 'Left'}",
            f"Attack Combo: {player.attack_combo}",
            f"Zombies: {len(zombie_spawner.zombies)}",
            f"Jumping: {player.is_jumping}",
            f"Health: {player.health}/{player.max_health}",
            f"Invulnerable: {player.invulnerability_timer > 0}"
        ]
        for i, info in enumerate(ui_info):
            text = font.render(info, True, (255, 255, 255))
            screen.blit(text, (10, 80 + i * 20))
        
        # Draw instructions
        instructions = [
            "WASD - Move, SHIFT - Run",
            "Right Click - Attack, Left Click - Shoot",
            "SPACE - Jump, R - Reload",
            "ESC - Back to Menu"
        ]
        instruction_font = pygame.font.SysFont("Arial", 16)
        for i, instruction in enumerate(instructions):
            inst_text = instruction_font.render(instruction, True, (255, 255, 255))
            screen.blit(inst_text, (10, 240 + i * 20))
        
        # Check if player died
        if player.is_dead:
            death_font = pygame.font.SysFont("Impact", 80)
            death_text = death_font.render("GAME OVER", True, (255, 0, 0))
            death_rect = death_text.get_rect(center=(window_width // 2, window_height // 2))
            screen.blit(death_text, death_rect)
            restart_font = pygame.font.SysFont("Arial", 24)
            restart_text = restart_font.render("Press ESC to return to menu", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(window_width // 2, window_height // 2 + 100))
            screen.blit(restart_text, restart_rect)
        
        # Draw screen flash effect when player takes damage
        player.draw_screen_flash(screen)
        
        pygame.display.flip()
