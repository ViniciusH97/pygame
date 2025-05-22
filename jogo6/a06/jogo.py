import os
import pygame
from pygame.locals import *

# Inicialização do pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dark Souls 2D")

# Diretórios das imagens
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
BG_DIR = os.path.join(IMAGES_DIR, "Battleground1", "Pale")
PLAYER_DIR = os.path.join(IMAGES_DIR, "Knight_1")
ENEMY_DIR = os.path.join(IMAGES_DIR, "Gorgon_1")

# Carregar imagens de fundo (paralaxe para o menu e jogo)
menu_bg_layers = [
    pygame.image.load(os.path.join(BG_DIR, filename)).convert_alpha()
    for filename in [
        "sky.png",
        "ruins_bg.png",
        "hills&trees.png",
        "stones&grass.png",
    ]
]

# Carregar imagens do jogador
player_image = pygame.image.load(os.path.join(PLAYER_DIR, "Idle.png")).convert_alpha()

# Carregar imagens do inimigo
enemy_image = pygame.image.load(os.path.join(ENEMY_DIR, "Idle.png")).convert_alpha()

# Classe para o fundo com paralaxe
class Background:
    def __init__(self, layers, speeds, direction="vertical"):
        self.layers = layers
        self.speeds = speeds
        self.positions = [0] * len(layers)
        self.direction = direction

    def update(self, dt):
        for i in range(len(self.layers)):
            if self.direction == "vertical":
                self.positions[i] += self.speeds[i] * dt / 16
                if self.positions[i] > self.layers[i].get_height():
                    self.positions[i] -= self.layers[i].get_height()
            elif self.direction == "horizontal":
                self.positions[i] -= self.speeds[i] * dt / 16
                if self.positions[i] < -self.layers[i].get_width():
                    self.positions[i] += self.layers[i].get_width()

    def draw(self, screen):
        for i, layer in enumerate(self.layers):
            if self.direction == "vertical":
                pos = self.positions[i]
                screen.blit(layer, (0, pos))
                screen.blit(layer, (0, pos - layer.get_height()))
            elif self.direction == "horizontal":
                pos = self.positions[i]
                screen.blit(layer, (pos, 0))
                screen.blit(layer, (pos + layer.get_width(), 0))

# Função para o menu inicial
def menu():
    clock = pygame.time.Clock()
    running = True

    # Fundo do menu
    menu_background = Background(menu_bg_layers, [1, 2, 3, 4], direction="horizontal")

    # Fonte personalizada para o título
    title_font = pygame.font.SysFont("Times New Roman", 72, bold=True)
    option_font = pygame.font.SysFont("Arial", 36)

    selected_option = 0
    options = ["Novo Jogo", "Sair"]

    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_option = (selected_option - 1) % len(options)
                if event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                if event.key == K_RETURN:
                    if selected_option == 0:  # Novo Jogo
                        running = False
                    elif selected_option == 1:  # Sair
                        pygame.quit()
                        exit()

        # Atualizar fundo
        menu_background.update(dt)

        # Desenhar fundo e texto
        screen.fill((0, 0, 0))
        menu_background.draw(screen)

        # Título do jogo
        title_text = title_font.render("Dark Souls 2D", True, (255, 255, 255))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Opções do menu
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (150, 150, 150)
            option_text = option_font.render(option, True, color)
            screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, 300 + i * 50))

        pygame.display.flip()

# Função principal do jogo
def main():
    # Inicializar objetos do jogo
    game_background = Background(menu_bg_layers, [1, 2, 3, 4])
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    enemies = pygame.sprite.Group(
        Enemy(200, -50),
        Enemy(400, -150),
        Enemy(600, -250)
    )

    # Grupo de sprites
    all_sprites = pygame.sprite.Group(player, *enemies)

    # Loop principal do jogo
    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Atualizar
        keys = pygame.key.get_pressed()
        player.update(keys)
        enemies.update()
        game_background.update(dt)

        # Desenhar
        screen.fill((0, 0, 0))
        game_background.draw(screen)
        all_sprites.draw(screen)

        pygame.display.flip()

    pygame.quit()

# Classe para o jogador
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def update(self, keys):
        if keys[K_UP]:
            self.rect.y -= self.speed
        if keys[K_DOWN]:
            self.rect.y += self.speed
        if keys[K_LEFT]:
            self.rect.x -= self.speed
        if keys[K_RIGHT]:
            self.rect.x += self.speed

        # Limitar o jogador à tela
        self.rect.clamp_ip(screen.get_rect())

# Classe para os inimigos
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.bottom = 0

# Executar o menu e o jogo
menu()
main()