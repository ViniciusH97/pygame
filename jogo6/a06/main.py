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

def main():
    """Função principal do jogo"""
    pygame.init()

    # Configurar tela
    WINDOW_WIDTH = pygame.display.Info().current_w
    WINDOW_HEIGHT = pygame.display.Info().current_h

    # Definir em tela cheia
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
    
    pygame.display.set_caption("Survive If You Can")

    # Loop principal do jogo
    current_state = "menu"
    
    try:
        while True:
            if current_state == "menu":
                current_state = menu()
            elif current_state == "game":
                current_state = game("Raider_1")
            elif current_state == "instructions":
                current_state = instructions()
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
