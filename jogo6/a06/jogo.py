import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("The Last of Us 2D")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)

# Clock for FPS
clock = pygame.time.Clock()

class ParallaxLayer:
    def __init__(self, image_path, speed):
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            # Create a fallback colored surface if image not found
            self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.image.fill((50, 50, 50))
            print(f"Could not load image: {image_path}")
        
        self.speed = speed
        self.x = 0
        self.width = self.image.get_width()
    
    def update(self):
        self.x -= self.speed
        if self.x <= -self.width:
            self.x = 0
    
    def draw(self, surface):
        surface.blit(self.image, (self.x, 0))
        surface.blit(self.image, (self.x + self.width, 0))

class Menu:
    def __init__(self):
        self.font_title = pygame.font.Font(None, 84)
        self.font_option = pygame.font.Font(None, 56)
        self.options = ["NEW GAME", "EXIT"]
        self.selected = 0
        
        # Create parallax layers with your PNG files
        self.layers = [
            ParallaxLayer("jogo6/imagens/Postapocalypce1/Pale/clouds1.png", 0.2),           # Sky layer (slowest)
            ParallaxLayer("jogo6/imagens/Postapocalypce1/Pale/clouds2.png", 0.4),           # Cloud layer
            ParallaxLayer("jogo6/imagens/Postapocalypce1/Pale/ground&houses_bg.png", 0.6),  # Background buildings
            ParallaxLayer("jogo6/imagens/Postapocalypce1/Pale/ground&houses.png", 0.9),     # Main buildings
            ParallaxLayer("jogo6/imagens/Postapocalypce1/Pale/ground&houses2.png", 1.2),    # Additional buildings
            ParallaxLayer("jogo6/imagens/Postapocalypce1/Pale/fence.png", 1.5),             # Fence layer
            ParallaxLayer("jogo6/imagens/Postapocalypce1/Pale/road.png", 1.8),              # Road (fastest)
        ]
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.options[self.selected]
            elif event.key == pygame.K_ESCAPE:
                return "EXIT"
        return None
    
    def update(self):
        for layer in self.layers:
            layer.update()
    
    def draw(self, surface):
        # Draw parallax background layers
        for layer in self.layers:
            layer.draw(surface)
        
        # Draw semi-transparent overlay for better text visibility
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(120)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # Draw title with shadow effect
        title_shadow = self.font_title.render("THE LAST OF US 2D", True, BLACK)
        title_text = self.font_title.render("THE LAST OF US 2D", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        
        # Draw shadow slightly offset
        surface.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        surface.blit(title_text, title_rect)
        
        # Draw menu options
        for i, option in enumerate(self.options):
            if i == self.selected:
                color = ORANGE
                # Draw selection background
                option_text = self.font_option.render(option, True, color)
                option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 100))
                
                # Selection highlight
                highlight_rect = option_rect.inflate(40, 20)
                pygame.draw.rect(surface, DARK_RED, highlight_rect)
                pygame.draw.rect(surface, ORANGE, highlight_rect, 3)
            else:
                color = WHITE
                option_text = self.font_option.render(option, True, color)
                option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 100))
            
            # Draw option text shadow
            option_shadow = self.font_option.render(option, True, BLACK)
            surface.blit(option_shadow, (option_rect.x + 2, option_rect.y + 2))
            surface.blit(option_text, option_rect)
        
        # Draw controls hint
        hint_font = pygame.font.Font(None, 32)
        hint_text = hint_font.render("Use Arrow Keys to Navigate • Enter to Select • ESC to Exit", True, GRAY)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        surface.blit(hint_text, hint_rect)

def main():
    menu = Menu()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            result = menu.handle_event(event)
            if result == "NEW GAME":
                print("Starting new game...")
                # Here you would transition to your game
                # For now, we'll just continue showing the menu
                pass
            elif result == "EXIT":
                running = False
        
        # Update parallax layers
        menu.update()
        
        # Draw everything
        screen.fill(BLACK)
        menu.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
