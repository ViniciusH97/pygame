import os
import pygame
from pygame.locals import *

pygame.init()

WINDOW_WIDTH = pygame.display.Info().current_w
WINDOW_HEIGHT = pygame.display.Info().current_h

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Dark Souls 2D")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "imagens")

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

def menu():
    clock = pygame.time.Clock()
    running = True
    
    # Load background layers
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
    
    # Fonts
    title_font = pygame.font.SysFont("Times New Roman", 72, bold=True)
    option_font = pygame.font.SysFont("Arial", 50)
    
    # Menu options
    selected_option = 0
    options = ["New Game", "Exit"]

    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == K_RETURN:
                    if selected_option == 0:  # New Game
                        print("Starting new game...")
                        # Add your game start code here
                    elif selected_option == 1:  # Exit
                        pygame.quit()
                        exit()
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    exit()

        # Update background with parallax effect
        menu_background.update(dt, pygame.time.get_ticks() * 0.05)
        
        # Draw everything
        screen.fill((0, 0, 0))
        menu_background.draw(screen)
        
        # Draw title
        title_text = title_font.render("SURVIVE IF YOU CAN", True, (255, 255, 255))
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 200))
        
        # Draw menu options
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected_option else (150, 150, 150)
            option_text = option_font.render(option, True, color)
            screen.blit(option_text, (WINDOW_WIDTH // 2 - option_text.get_width() // 2, 350 + i * 80))
        
        # Draw instructions
        instruction_font = pygame.font.SysFont("Arial", 24)
        instructions = "Use UP/DOWN arrows to navigate, ENTER to select, ESC to exit"
        inst_text = instruction_font.render(instructions, True, (200, 200, 200))
        screen.blit(inst_text, (WINDOW_WIDTH // 2 - inst_text.get_width() // 2, WINDOW_HEIGHT - 100))
        
        pygame.display.flip()

if __name__ == "__main__":
    menu()
    pygame.quit()