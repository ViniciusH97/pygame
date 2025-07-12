import os
import pygame
from pygame.locals import *
from background import Background
from player import Player
from zombie_spawner import ZombieSpawner
from score_manager import ScoreManager

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

def game(selected_character="Raider_1", display_manager=None):
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.get_surface()
    window_width = screen.get_width()
    window_height = screen.get_height()
    
    # Esconder o cursor do mouse durante o jogo
    pygame.mouse.set_visible(False)
    
    game_background = create_game_background()
    player = Player(100, 450, selected_character)
    zombie_spawner = ZombieSpawner()
    score_manager = ScoreManager()
    
    # Controle de câmera - só pode avançar, nunca voltar
    max_camera_x = 0
    
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
        
        score_manager.update(dt)
        zombie_spawner.update(player, dt, score_manager)
        zombie_spawner.check_player_attacks(player, score_manager)
        
        # Câmera só pode avançar, nunca voltar
        current_camera_x = max(0, player.world_x - window_width // 2)
        camera_x = max(max_camera_x, current_camera_x)
        max_camera_x = camera_x  
        
        game_background.update(dt, camera_x)
    
        screen.fill((0, 0, 0))
        game_background.draw(screen)
        
        # spawna os zumbie na tela
        zombie_spawner.draw(screen, camera_x)
        
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
        
        # mostra a barra de vida, stamina e a munição do player
        player.draw_health_bar(screen)
        player.draw_stamina_bar(screen)
        player.draw_ammo_counter(screen)
        
        # Desenhar pontuação e tempo no canto inferior direito
        window_width = screen.get_width()
        window_height = screen.get_height()
        
        try:
            score_font = pygame.font.SysFont("Impact", 30)  # Fonte um pouco menor
            debug_font = pygame.font.SysFont("Arial", 20)   # Fonte para debug
        except:
            score_font = pygame.font.SysFont("Arial", 24)
            debug_font = pygame.font.SysFont("Arial", 18)
        
        # Pontuação
        score_text = f"PONTUAÇÃO: {score_manager.score}"
        score_surface = score_font.render(score_text, True, (255, 255, 255))  # Branco
        
        # Informações de dificuldade baseada na pontuação
        # Sistema de debug removido
        
        score_x = window_width - score_surface.get_width() - 20
        score_y = window_height - score_surface.get_height() - 60  # Espaço para duas linhas
        screen.blit(score_surface, (score_x, score_y))
        
        # Tempo sobrevivido
        time_text = f"TEMPO: {score_manager.get_time_survived_formatted()}"
        time_surface = score_font.render(time_text, True, (255, 255, 255))  # Branco
        time_x = window_width - time_surface.get_width() - 20
        time_y = window_height - time_surface.get_height() - 20  # Logo abaixo da pontuação
        screen.blit(time_surface, (time_x, time_y))
        
        # Check if player died
        if player.is_dead:
            # Parar a contagem do tempo
            score_manager.set_game_over()
            
            # Criar fundo estático escuro para game over
            overlay = pygame.Surface((window_width, window_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(200)  # Semi-transparente
            screen.blit(overlay, (0, 0))
            
            # Título Game Over
            death_font = pygame.font.SysFont("Impact", 100)
            death_text = death_font.render("GAME OVER", True, (255, 0, 0))
            death_rect = death_text.get_rect(center=(window_width // 2, window_height // 4))
            screen.blit(death_text, death_rect)
            
            # Estatísticas finais
            stats = score_manager.get_stats()
            
            try:
                stats_font = pygame.font.SysFont("Impact", 50)  # Fonte do menu
                small_font = pygame.font.SysFont("Impact", 35)
            except:
                stats_font = pygame.font.SysFont("Arial", 40)
                small_font = pygame.font.SysFont("Arial", 28)
            
            # Pontuação final
            final_score = stats_font.render(f"PONTUAÇÃO FINAL: {stats['score']}", True, (255, 255, 0))
            final_score_rect = final_score.get_rect(center=(window_width // 2, window_height // 2 - 60))
            screen.blit(final_score, final_score_rect)
            
            # Estatísticas detalhadas
            stats_y = window_height // 2 + 20
            stats_list = [
                f"Tempo Sobrevivido: {stats['time_survived']}",
                f"Pontos por Zumbi: 10",
                f"Pontos por Minuto: 5"
            ]
            
            for i, stat in enumerate(stats_list):
                stat_surface = small_font.render(stat, True, (255, 255, 255))
                stat_rect = stat_surface.get_rect(center=(window_width // 2, stats_y + i * 40))
                screen.blit(stat_surface, stat_rect)
            
            # Instruções
            restart_font = pygame.font.SysFont("Impact", 24)
            restart_text = restart_font.render("Pressione ESC para voltar ao menu", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(window_width // 2, window_height - 100))
            screen.blit(restart_text, restart_rect)
        
        # Draw screen flash effect when player takes damage
        player.draw_screen_flash(screen)
        
        pygame.display.flip()
    
    # Mostrar o cursor do mouse novamente ao sair do jogo
    pygame.mouse.set_visible(True)
