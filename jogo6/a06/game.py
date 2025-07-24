import os
import pygame
from pygame.locals import *
from background import Background
from player import Player
from zombie_spawner import ZombieSpawner
from score_manager import ScoreManager
from menu import get_player_name

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
    paused = False  # Variável para controlar o estado da pausa
    screen = pygame.display.get_surface()
    window_width = screen.get_width()
    window_height = screen.get_height()
    
    # Esconder o cursor do mouse durante o jogo
    pygame.mouse.set_visible(False)
    
    game_background = create_game_background()
    player = Player(100, 450, selected_character)
    zombie_spawner = ZombieSpawner()
    score_manager = ScoreManager()
    
    max_camera_x = 0
    game_over_state = False  # Flag para controlar estado do game over
    name_saved = False  # Flag para controlar se o nome já foi salvo no ranking
    show_name_input = False  # Flag para controlar quando mostrar a entrada de nome
    
    while running:
        dt = clock.tick(60)
        events = pygame.event.get()
        
        for event in events:
            if event.type == QUIT:
                return "exit"
            if event.type == KEYDOWN:
                # Controles de pausa (apenas quando não está game over)
                if not game_over_state and not player.is_dead:
                    if event.key == K_ESCAPE or event.key == K_RETURN:
                        paused = not paused  # Alternar estado da pausa
                        continue
                
                if event.key == K_ESCAPE and not paused:
                    return "menu"
                # Controles da tela de game over
                elif game_over_state and player.is_dead:
                    if event.key == K_RETURN:
                        if not show_name_input:
                            # Primeira vez pressionando ENTER - mostrar entrada de nome
                            show_name_input = True
                        else:
                            # Segunda vez (após salvar nome) - reiniciar jogo
                            return "game"
                    elif event.key == K_ESCAPE:
                        return "menu"  # Voltar ao menu
                    
        # Só atualizar o jogo se não estiver pausado
        if not paused:
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
        else:
            # Quando pausado, manter a câmera na posição atual
            camera_x = max_camera_x
    
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
        
        # CORRIGIR: Ajustar hitbox para ficar no centro-base do player visual
        # O hitbox precisa estar onde o player realmente está na tela
        sprite_width = int(128 * player.scale)
        sprite_height = int(128 * player.scale)
        
        # Centralizar horizontalmente e posicionar na base do sprite
        hitbox_offset_x = (sprite_width - player.rect.width) // 2
        hitbox_offset_y = sprite_height - player.rect.height - 30  # Na base do personagem
        
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
        
        score_x = window_width - score_surface.get_width() - 20
        score_y = window_height - score_surface.get_height() - 60  # Espaço para duas linhas
        screen.blit(score_surface, (score_x, score_y))
        
        # Tempo sobrevivido
        time_text = f"TEMPO: {score_manager.get_time_survived_formatted()}"
        time_surface = score_font.render(time_text, True, (255, 255, 255))  # Branco
        time_x = window_width - time_surface.get_width() - 20
        time_y = window_height - time_surface.get_height() - 20  # Logo abaixo da pontuação
        screen.blit(time_surface, (time_x, time_y))
        
        if player.is_dead: 
            # Parar a contagem do tempo
            score_manager.set_game_over()
            game_over_state = True
            
            # Verificar se precisa obter o nome do jogador (apenas quando solicitado)
            if show_name_input and not name_saved:
                # Salvar temporariamente o estado atual
                pygame.mouse.set_visible(True)
                player_name = get_player_name()
                pygame.mouse.set_visible(False)
                
                if player_name:
                    score_manager.add_score_to_ranking(player_name)
                name_saved = True
                show_name_input = False  # Resetar flag
            
            # Criar fundo estático escuro para game over
            overlay = pygame.Surface((window_width, window_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(200)
            screen.blit(overlay, (0, 0))
            
            # Título na tela de game over
            death_font = pygame.font.SysFont("Impact", 100)
            death_text = death_font.render("GAME OVER", True, (255, 0, 0))
            death_rect = death_text.get_rect(center=(window_width // 2, window_height // 4))
            screen.blit(death_text, death_rect)
            
            # Estatísticas finais
            stats = score_manager.get_stats()
            
            try:
                stats_font = pygame.font.SysFont("Impact", 50)  
                small_font = pygame.font.SysFont("Impact", 35)
                medium_font = pygame.font.SysFont("Impact", 40)
                record_font = pygame.font.SysFont("Impact", 60)  
            except:
                stats_font = pygame.font.SysFont("Arial", 40)
                small_font = pygame.font.SysFont("Arial", 28)
                medium_font = pygame.font.SysFont("Arial", 32)
                record_font = pygame.font.SysFont("Arial", 48) 
            
            # Record com nome do jogador
            if stats['high_score_name']:
                record_text = record_font.render(f"RECORD: {stats['high_score']} - {stats['high_score_name']}", True, (255, 215, 0))
            else:
                record_text = record_font.render(f"RECORD: {stats['high_score']}", True, (255, 215, 0))
            record_rect = record_text.get_rect(center=(window_width // 2, window_height // 2 - 100))
            screen.blit(record_text, record_rect)

            # Pontuação atual (abaixo do record)
            current_score = stats_font.render(f"PONTUAÇÃO ATUAL: {stats['score']}", True, (255, 255, 255))
            current_score_rect = current_score.get_rect(center=(window_width // 2, window_height // 2 - 30))
            screen.blit(current_score, current_score_rect)

            # Tempo sobrevivido
            stats_y = window_height // 2 + 30
            time_text = f"Tempo Sobrevivido: {stats['time_survived']}"
            time_surface = small_font.render(time_text, True, (255, 255, 255))
            time_rect = time_surface.get_rect(center=(window_width // 2, stats_y))
            screen.blit(time_surface, time_rect)
            
            # Instruções de controle
            restart_font = pygame.font.SysFont("Impact", 28)
            if not name_saved:
                restart_text = restart_font.render("Pressione ENTER para salvar no ranking e jogar novamente", True, (200, 200, 200))
            else:
                restart_text = restart_font.render("Pressione ENTER para jogar novamente", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(window_width // 2, window_height - 120))
            screen.blit(restart_text, restart_rect)
            
            menu_text = restart_font.render("Pressione ESC para voltar ao menu", True, (200, 200, 200))
            menu_rect = menu_text.get_rect(center=(window_width // 2, window_height - 80))
            screen.blit(menu_text, menu_rect)
        
        # Tela de pausa
        if paused and not game_over_state and not player.is_dead:
            # Criar overlay escuro
            overlay = pygame.Surface((window_width, window_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(150)  # Semi-transparente
            screen.blit(overlay, (0, 0))
            
            # Carregar fonte personalizada para "JOGO PAUSADO"
            try:
                BASE_DIR = os.path.dirname(os.path.dirname(__file__))
                font_path = os.path.join(BASE_DIR, "imagens", "fonts", "Zombie_Holocaust.ttf")
                pause_font = pygame.font.Font(font_path, 100)
            except:
                pause_font = pygame.font.SysFont("Impact", 100)
            
            pause_text = pause_font.render("JOGO PAUSADO", True, (255, 0, 0))  # Vermelho
            pause_rect = pause_text.get_rect(center=(window_width // 2, window_height // 2))
            screen.blit(pause_text, pause_rect)
            
            # Instruções para despausar
            instruction_font = pygame.font.SysFont("Arial", 30)
            instruction_text = instruction_font.render("Pressione ENTER ou ESC para continuar", True, (255, 255, 255))
            instruction_rect = instruction_text.get_rect(center=(window_width // 2, window_height // 2 + 100))
            screen.blit(instruction_text, instruction_rect)
        
        player.draw_screen_flash(screen)
        
        pygame.display.flip()
    
    # Mostrar o cursor do mouse novamente ao sair do jogo
    pygame.mouse.set_visible(True)
