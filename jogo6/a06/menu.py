import os
import pygame
from pygame.locals import *
from background import Background
from score_manager import ScoreManager

def create_menu_background():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
    
    menu_layers = []
    menu_speeds = [0.2, 0.4, 0.7, 1.0, 1.5, 2.0]
    MENU_BG_DIR = os.path.join(IMAGES_DIR, "Postapocalypce2", "Bright")
    menu_layer_files = ["sky.png", "houses&trees_bg.png", "houses.png", "car_trees_etc.png", "fence.png", "road.png"]
    
    window_width = pygame.display.get_surface().get_width()
    window_height = pygame.display.get_surface().get_height()
    
    for filename in menu_layer_files:
        path = os.path.join(MENU_BG_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (window_width, window_height))
            menu_layers.append(img)
    
    return Background(menu_layers, menu_speeds)

def menu(display_manager=None):
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.get_surface()
    window_width = screen.get_width()
    window_height = screen.get_height()
    
    menu_background = create_menu_background()
    
    title_font = pygame.font.Font("../imagens/fonts/Zombie_Holocaust.ttf", 130)
    option_font = pygame.font.SysFont("Impact", 50)

    selected_option = 0
    options = ["JOGAR", "INSTRUÇÕES", "RANKING", "SAIR"]

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
                        return "instructions"
                    elif selected_option == 2:  
                        return "ranking"
                    elif selected_option == 3:  
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
                    screen.blit(border_text, (window_width // 2 - border_text.get_width() // 2 + dx, title_y + dy))
        
        main_title = title_font.render(title_text, True, (255, 255, 255))
        screen.blit(main_title, (window_width // 2 - main_title.get_width() // 2, title_y))
        
        # Opções no menu
        for i, option in enumerate(options):
            color = (255, 0, 0) if i == selected_option else (150, 150, 150)
            option_text = option_font.render(option, True, color)
            screen.blit(option_text, (window_width // 2 - option_text.get_width() // 2, 450 + i * 80))
        
        instruction_font = pygame.font.SysFont("Arial", 24)
        instructions = "Use as setinhas para CIMA/BAIXO para navegar pelas opções, Pressione ENTER para selecionar ou ESC para sair"
        inst_text = instruction_font.render(instructions, True, (200, 200, 200))
        screen.blit(inst_text, (window_width // 2 - inst_text.get_width() // 2, window_height - 80))
        
        # Créditos do desenvolvedor
        credit_font = pygame.font.SysFont("Arial", 18)
        credit_text = "Criado por Vinicius Lima ©"
        credit_surface = credit_font.render(credit_text, True, (150, 150, 150))
        screen.blit(credit_surface, (window_width // 2 - credit_surface.get_width() // 2, window_height - 40))
        
        pygame.display.flip()

def instructions(display_manager=None):
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.get_surface()
    window_width = screen.get_width()
    window_height = screen.get_height()
    
    menu_background = create_menu_background()
    
    title_font = pygame.font.SysFont("Impact", 30)
    instruction_font = pygame.font.SysFont("Arial", 30)
    small_font = pygame.font.SysFont("Arial", 20)
    
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return "exit"
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_RETURN:
                    return "menu"
        
        menu_background.update(dt, pygame.time.get_ticks() * 0.05)
        
        screen.fill((0, 0, 0))
        menu_background.draw(screen)
        
        title_font = pygame.font.Font("../imagens/fonts/Zombie_Holocaust.ttf", 100)
        title_text = "DICAS"
        title_y = 50
        
        # Efeito de borda no título
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    border_text = title_font.render(title_text, True, (0, 0, 0))
                    screen.blit(border_text, (window_width // 2 - border_text.get_width() // 2 + dx, title_y + dy))
        
        main_title = title_font.render(title_text, True, (255, 255, 255))
        screen.blit(main_title, (window_width // 2 - main_title.get_width() // 2, title_y))
        
        # Criar fundo de bloco de anotações
        notepad_width = 900
        notepad_height = 700
        notepad_x = (window_width - notepad_width) // 2
        notepad_y = 150
        
        shadow_offset = 8
        shadow_rect = pygame.Rect(notepad_x + shadow_offset, notepad_y + shadow_offset, notepad_width, notepad_height)
        pygame.draw.rect(screen, (50, 50, 50), shadow_rect)
    
        notepad_rect = pygame.Rect(notepad_x, notepad_y, notepad_width, notepad_height)
        pygame.draw.rect(screen, (245, 245, 220), notepad_rect)
    
        pygame.draw.rect(screen, (180, 180, 160), notepad_rect, 3)
        
        line_spacing = 35
        for i in range(int(notepad_height // line_spacing)):
            line_y = notepad_y + 50 + i * line_spacing
            if line_y < notepad_y + notepad_height - 30:
                pygame.draw.line(screen, (200, 200, 200), 
                               (notepad_x + 30, line_y), 
                               (notepad_x + notepad_width - 30, line_y), 1)
        
        # Margem esquerda (linha vermelha)
        margin_x = notepad_x + 80
        pygame.draw.line(screen, (255, 150, 150), 
                        (margin_x, notepad_y + 30), 
                        (margin_x, notepad_y + notepad_height - 30), 2)
        
        hole_x = notepad_x + 25
        for i in range(3):
            hole_y = notepad_y + 150 + i * 150
            pygame.draw.circle(screen, (200, 200, 200), (hole_x, hole_y), 8)
            pygame.draw.circle(screen, (220, 220, 220), (hole_x, hole_y), 6)
        
        instructions_list = [
            "CONTROLES:",
            "",
            "  A/D ou Setas - Mover",
            "  SHIFT - Correr (gasta stamina)",
            "  ESPAÇO - Pular",
            "",
            "COMBATE:",
            "",
            "  Clique Direito - Ataque corpo a corpo",
            "  Clique Esquerdo - Tiro (gasta munição)",
            "  R - Recarregar",
            "",
            "OBJETIVO:",
            "",
            "  Sobreviva o máximo possível!",
            "  Mate zumbis para ganhar pontos",
            "  Colete munição dos zumbis mortos",
            "",
            "CONTROLES DO MENU:",
            "",
            "  Pressione ESC para voltar ao menu"
        ]
        
        start_y = notepad_y + 40
        line_height = 30
        text_x_offset = notepad_x + 100  
        
        current_line = 0
        for instruction in instructions_list:
            if instruction == "":
                current_line += 0.5 
                continue
                
            if instruction.startswith("  "): 
                color = (80, 80, 80) 
                font = small_font
                text_x = text_x_offset + 30  
            elif instruction.endswith(":"):  
                color = (180, 50, 50)  
                font = instruction_font
                text_x = text_x_offset
                current_line += 0.3  
            else: 
                color = (60, 60, 60)  
                font = instruction_font
                text_x = text_x_offset
            
            text_surface = font.render(instruction, True, color)
            text_y = start_y + current_line * line_height
            
            if text_y < notepad_y + notepad_height - 80:
                screen.blit(text_surface, (text_x, text_y))
            
            current_line += 1
        
        back_text = "Pressione ESC ou ENTER para voltar ao menu"
        back_surface = small_font.render(back_text, True, (200, 200, 200))
        screen.blit(back_surface, (window_width // 2 - back_surface.get_width() // 2, notepad_y + notepad_height + 30))
        
        pygame.display.flip()

def get_player_name(display_manager=None):
    """Tela para o jogador inserir seu nome após morrer"""
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.get_surface()
    window_width = screen.get_width()
    window_height = screen.get_height()
    
    menu_background = create_menu_background()
    
    player_name = ""
    max_name_length = 20
    
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return None
            if event.type == KEYDOWN:
                if event.key == K_RETURN and len(player_name.strip()) > 0:
                    return player_name.strip()
                elif event.key == K_ESCAPE:
                    return None
                elif event.key == K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    # Adicionar caractere se for alfanumérico ou espaço
                    if len(player_name) < max_name_length:
                        char = event.unicode
                        if char.isprintable() and (char.isalnum() or char == ' '):
                            player_name += char
        
        menu_background.update(dt, pygame.time.get_ticks() * 0.05)
        
        screen.fill((0, 0, 0))
        menu_background.draw(screen)
        
        # Overlay escuro
        overlay = pygame.Surface((window_width, window_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        
        # Título
        title_font = pygame.font.Font("../imagens/fonts/Zombie_Holocaust.ttf", 80)
        title_text = "DIGITE SEU NOME PARA SALVAR NO RANKING"
        title_y = 150
        
        # Efeito de borda no título
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    border_text = title_font.render(title_text, True, (0, 0, 0))
                    screen.blit(border_text, (window_width // 2 - border_text.get_width() // 2 + dx, title_y + dy))
        
        main_title = title_font.render(title_text, True, (255, 255, 255))
        screen.blit(main_title, (window_width // 2 - main_title.get_width() // 2, title_y))
        
        # Campo de entrada de nome
        input_box_width = 400
        input_box_height = 60
        input_box_x = (window_width - input_box_width) // 2
        input_box_y = 300
        
        # Desenhar caixa de entrada
        pygame.draw.rect(screen, (255, 255, 255), (input_box_x, input_box_y, input_box_width, input_box_height))
        pygame.draw.rect(screen, (0, 0, 0), (input_box_x, input_box_y, input_box_width, input_box_height), 3)
        
        # Desenhar texto do nome
        name_font = pygame.font.SysFont("Arial", 36)
        name_surface = name_font.render(player_name, True, (0, 0, 0))
        name_x = input_box_x + 10
        name_y = input_box_y + (input_box_height - name_surface.get_height()) // 2
        screen.blit(name_surface, (name_x, name_y))
        
        # Cursor piscante
        if (pygame.time.get_ticks() // 500) % 2:
            cursor_x = name_x + name_surface.get_width() + 2
            cursor_y = name_y
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + name_surface.get_height()), 2)
        
        # Instruções
        inst_font = pygame.font.SysFont("Arial", 24)
        inst_text = "Pressione ENTER para confirmar ou ESC para cancelar"
        inst_surface = inst_font.render(inst_text, True, (200, 200, 200))
        screen.blit(inst_surface, (window_width // 2 - inst_surface.get_width() // 2, 400))
        
        pygame.display.flip()
    
    return None

def ranking(display_manager=None):
    """Tela de ranking com paginação"""
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.get_surface()
    window_width = screen.get_width()
    window_height = screen.get_height()
    
    menu_background = create_menu_background()
    score_manager = ScoreManager()
    rankings = score_manager.rankings
    
    # Paginação
    items_per_page = 10
    current_page = 0
    total_pages = max(1, (len(rankings) + items_per_page - 1) // items_per_page)
    
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return "exit"
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_RETURN:
                    return "menu"
                elif event.key == K_LEFT and current_page > 0:
                    current_page -= 1
                elif event.key == K_RIGHT and current_page < total_pages - 1:
                    current_page += 1
        
        menu_background.update(dt, pygame.time.get_ticks() * 0.05)
        
        screen.fill((0, 0, 0))
        menu_background.draw(screen)
        
        # Título
        title_font = pygame.font.Font("../imagens/fonts/Zombie_Holocaust.ttf", 100)
        title_text = "RANKING"
        title_y = 50
        
        # Efeito de borda no título
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    border_text = title_font.render(title_text, True, (0, 0, 0))
                    screen.blit(border_text, (window_width // 2 - border_text.get_width() // 2 + dx, title_y + dy))
        
        main_title = title_font.render(title_text, True, (255, 255, 255))
        screen.blit(main_title, (window_width // 2 - main_title.get_width() // 2, title_y))
        
        # Criar fundo para o ranking
        ranking_width = 1000
        ranking_height = 550
        ranking_x = (window_width - ranking_width) // 2
        ranking_y = 150
        
        # Sombra
        shadow_offset = 8
        shadow_rect = pygame.Rect(ranking_x + shadow_offset, ranking_y + shadow_offset, ranking_width, ranking_height)
        pygame.draw.rect(screen, (50, 50, 50), shadow_rect)
        
        # Fundo principal
        ranking_rect = pygame.Rect(ranking_x, ranking_y, ranking_width, ranking_height)
        pygame.draw.rect(screen, (245, 245, 220), ranking_rect)
        pygame.draw.rect(screen, (180, 180, 160), ranking_rect, 3)
        
        # Cabeçalho
        header_font = pygame.font.SysFont("Impact", 28)
        header_y = ranking_y + 20
        
        # Posições das colunas
        pos_x = ranking_x + 50
        name_x = ranking_x + 100
        score_x = ranking_x + 400
        zombies_x = ranking_x + 600
        time_x = ranking_x + 800
        
        # Desenhar cabeçalhos
        pos_header = header_font.render("POS", True, (100, 100, 100))
        screen.blit(pos_header, (pos_x, header_y))
        
        name_header = header_font.render("NOME", True, (100, 100, 100))
        screen.blit(name_header, (name_x, header_y))
        
        score_header = header_font.render("PONTOS", True, (100, 100, 100))
        screen.blit(score_header, (score_x, header_y))
        
        zombies_header = header_font.render("ZUMBIS", True, (100, 100, 100))
        screen.blit(zombies_header, (zombies_x, header_y))
        
        time_header = header_font.render("TEMPO", True, (100, 100, 100))
        screen.blit(time_header, (time_x, header_y))
        
        # Linha separadora
        pygame.draw.line(screen, (150, 150, 150), 
                        (ranking_x + 20, header_y + 35), 
                        (ranking_x + ranking_width - 20, header_y + 35), 2)
        
        # Mostrar rankings da página atual
        start_index = current_page * items_per_page
        end_index = min(start_index + items_per_page, len(rankings))
        
        ranking_font = pygame.font.SysFont("Arial", 24)
        
        for i in range(start_index, end_index):
            rank_data = rankings[i]
            y_pos = header_y + 60 + (i - start_index) * 40
            
            # Posição
            pos_text = ranking_font.render(f"{i + 1}º", True, (80, 80, 80))
            screen.blit(pos_text, (pos_x, y_pos))
            
            # Nome
            name_text = ranking_font.render(rank_data['name'][:15], True, (60, 60, 60))
            screen.blit(name_text, (name_x, y_pos))
            
            # Pontuação 
            score_color = (255, 215, 0) if i == 0 and len(rankings) > 0 else (60, 60, 60)
            score_text = ranking_font.render(str(rank_data['score']), True, score_color)
            screen.blit(score_text, (score_x, y_pos))
            
            # Zumbis mortos
            zombies_text = ranking_font.render(str(rank_data['zombies_killed']), True, (60, 60, 60))
            screen.blit(zombies_text, (zombies_x, y_pos))
            
            # Tempo
            time_text = ranking_font.render(rank_data['time_survived'], True, (60, 60, 60))
            screen.blit(time_text, (time_x, y_pos))
        
        # Informações de paginação
        if total_pages > 1:
            page_font = pygame.font.SysFont("Arial", 20)
            page_text = f"Página {current_page + 1} de {total_pages}"
            page_surface = page_font.render(page_text, True, (100, 100, 100))
            screen.blit(page_surface, (window_width // 2 - page_surface.get_width() // 2, ranking_y + ranking_height + 10))
            
            # Instruções de navegação
            nav_text = "Use as setas ESQUERDA/DIREITA para navegar"
            nav_surface = page_font.render(nav_text, True, (100, 100, 100))
            screen.blit(nav_surface, (window_width // 2 - nav_surface.get_width() // 2, ranking_y + ranking_height + 35))
        
        # Instruções para voltar
        back_font = pygame.font.SysFont("Arial", 24)
        back_text = "Pressione ESC ou ENTER para voltar ao menu"
        back_surface = back_font.render(back_text, True, (200, 200, 200))
        screen.blit(back_surface, (window_width // 2 - back_surface.get_width() // 2, window_height - 60))
        
        pygame.display.flip()
