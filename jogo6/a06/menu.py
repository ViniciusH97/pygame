import os
import pygame
from pygame.locals import *
from background import Background

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
    options = ["JOGAR", "INSTRUÇÕES", "SAIR"]

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
        screen.blit(inst_text, (window_width // 2 - inst_text.get_width() // 2, window_height - 50))
        
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
