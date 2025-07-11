#!/usr/bin/env python3
"""
Survive If You Can - Main Game Entry Point

Como rodar:
1. Certifique-se de que o pygame está instalado: pip install pygame
2. Execute este arquivo: python main.py
3. Ou dê permissão de execução: chmod +x main.py && ./main.py

Estrutura dos arquivos:
- main.py (este arquivo): Ponto de entrada principal
- game.py: Lógica principal do jogo
- menu.py: Sistema de menu
- player.py: Classe do jogador
- zombie.py: Classe dos zumbis
- zombie_spawner.py: Sistema de spawn dos zumbis
- animated_sprite.py: Sistema de animação
- background.py: Sistema de background com paralaxe

Para adicionar novos recursos:
- Novos inimigos: Edite zombie.py e zombie_spawner.py
- Novos personagens: Edite player.py
- Novos níveis: Edite game.py e background.py
- Novos menus: Edite menu.py
"""

import pygame
from pygame.locals import *
from menu import menu, instructions
from game import game

class DisplayManager:
    def __init__(self):
        self.is_fullscreen = True
        self.windowed_sizes = [(1600, 900), (1920, 1080)]
        self.current_windowed_size = 0
        self.screen = None
        
    def toggle_fullscreen(self):
        if self.is_fullscreen:
            #muda para o modo janela
            self.is_fullscreen = False
            width, height = self.windowed_sizes[self.current_windowed_size]
            self.screen = pygame.display.set_mode((width, height))
        else:
            self.is_fullscreen = True
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        return self.screen
    
    def cycle_windowed_size(self):
        if not self.is_fullscreen:
            self.current_windowed_size = (self.current_windowed_size + 1) % len(self.windowed_sizes)
            width, height = self.windowed_sizes[self.current_windowed_size]
            self.screen = pygame.display.set_mode((width, height))
        return self.screen
    
    def get_screen(self):
        return self.screen
    
    def initialize_display(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        return self.screen

display_manager = DisplayManager()

def main():
    pygame.init()

    # Configurar tela inicial em fullscreen
    screen = display_manager.initialize_display()
    pygame.display.set_caption("Survive If You Can")

    # Loop principal do jogo
    current_state = "menu"
    
    try:
        while True:
            if current_state == "menu":
                current_state = menu(display_manager)
            elif current_state == "game":
                current_state = game("Raider_1", display_manager)
            elif current_state == "instructions":
                current_state = instructions(display_manager)
            elif current_state == "exit":
                break
    except KeyboardInterrupt:
        print("\nJogo interrompido pelo usuário")
    except Exception as e:
        print(f"Erro no jogo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        print("Jogo encerrado")

if __name__ == "__main__":
    main()
