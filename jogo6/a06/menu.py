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

def menu():
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.get_surface()
    window_width = screen.get_width()
    window_height = screen.get_height()
    
    menu_background = create_menu_background()
    
    title_font = pygame.font.SysFont("Impact", 100)
    option_font = pygame.font.SysFont("Impact", 70)
    
    selected_option = 0
    options = ["Novo Jogo", "Tutorial", "Sair"]

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
        
        # opções no menu e de cor no menu
        for i, option in enumerate(options):
            color = (255, 0, 0) if i == selected_option else (150, 150, 150)
            option_text = option_font.render(option, True, color)
            screen.blit(option_text, (window_width // 2 - option_text.get_width() // 2, 450 + i * 80))
        
        instruction_font = pygame.font.SysFont("Arial", 24)
        instructions = "Use as setinhas para CIMA/BAIXO para navegar pelas opções, Pressione ENTER para selecionar ou ESC para sair"
        inst_text = instruction_font.render(instructions, True, (200, 200, 200))
        screen.blit(inst_text, (window_width // 2 - inst_text.get_width() // 2, window_height - 100))
        
        pygame.display.flip()

def instructions():
    """Tela de instruções do jogo"""
    clock = pygame.time.Clock()
    running = True
    screen = pygame.display.get_surface()
    window_width = screen.get_width()
    window_height = screen.get_height()
    
    menu_background = create_menu_background()
    
    title_font = pygame.font.SysFont("Impact", 60)
    instruction_font = pygame.font.SysFont("Arial", 30)
    small_font = pygame.font.SysFont("Arial", 30)
    
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
        
        # Título
        title_text = "INSTRUÇÕES"
        title_y = 100
        
        # Efeito de borda no título
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    border_text = title_font.render(title_text, True, (0, 0, 0))
                    screen.blit(border_text, (window_width // 2 - border_text.get_width() // 2 + dx, title_y + dy))
        
        main_title = title_font.render(title_text, True, (255, 255, 255))
        screen.blit(main_title, (window_width // 2 - main_title.get_width() // 2, title_y))
        
        # Instruções do jogo
        instructions_list = [
            "MOVIMENTAÇÃO:",
            "",
            "  WASD ou Setas - Mover o personagem",
            "  SHIFT - Correr",
            "  SPACE - Pular",
            "",
            "COMBATE:",
            "",
            "  Botão Direito do Mouse - Ataque corpo a corpo",
            "  Botão Esquerdo do Mouse - Atirar",
            "  R - Recarregar munição",
            "",
            "OBJETIVO:",
            "",
            "  Sobreviva o máximo possível aos ataques dos zumbis",
            "  Elimine os zumbis para pontuar",
            "  Cuidado com sua vida e munição!",
            "",
            "CONTROLES DO MENU:",
            "",
            "  ESC - Voltar ao menu principal",
            "  ENTER ou ESC - Voltar"
        ]
        
        start_y = 200
        line_height = 30
        
        for i, instruction in enumerate(instructions_list):
            if instruction.startswith("  "):  
                color = (200, 200, 200)
                font = small_font
            elif instruction == "":
                continue
            elif instruction.endswith(":"): 
                color = (255, 255, 0)
                font = instruction_font
            else:  # Texto normal
                color = (255, 255, 255)
                font = instruction_font
            
            text_surface = font.render(instruction, True, color)
            screen.blit(text_surface, (window_width // 2 - text_surface.get_width() // 2, start_y + i * line_height))
        
        # Instrução para voltar
        back_text = "Pressione ESC ou ENTER para voltar ao menu"
        back_surface = small_font.render(back_text, True, (150, 150, 150))
        screen.blit(back_surface, (window_width // 2 - back_surface.get_width() // 2, window_height - 50))
        
        pygame.display.flip()
