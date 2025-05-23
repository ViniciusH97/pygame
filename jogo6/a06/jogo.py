import os
import pygame
from pygame.locals import *

# Inicialização do pygame
pygame.init()

# Configurações da tela
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dark Souls 2D")

# Diretórios das imagens
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
BG_DIR = os.path.join(IMAGES_DIR, "Battleground4", "Pale")
PLAYER_IDLE_DIR = os.path.join(IMAGES_DIR, "Knight_1", "idle")
ENEMY_IDLE_DIR = os.path.join(IMAGES_DIR, "Skeleton_Warrior", "idle")

# Carregar camadas do fundo e redimensionar para caber na janela
bg_layers = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(BG_DIR, filename)).convert_alpha(),
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )
    for filename in [
        "sky.png",
        "back_trees.png",
        "tree.png",
        "wall.png",
        "ground.png",
        "bones.png",
        "graves.png",
        "crypt.png",
        "Battleground4.png",  # Adicionado o chão
    ]
]

# Carregar animações do jogador (idle) e redimensionar
player_idle_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(PLAYER_IDLE_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        (100, 150)  # Aumentar o tamanho do jogador
    )
    for i in range(1, 5)
]

# Carregar animações do inimigo (idle) e redimensionar
enemy_idle_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(ENEMY_IDLE_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        (100, 150)  # Aumentar o tamanho do inimigo
    )
    for i in range(1, 8)
]

# Classe para o fundo com paralaxe
class Background:
    def __init__(self, layers, speeds):
        self.layers = layers
        self.speeds = speeds
        self.positions = [0] * len(layers)

    def update(self, player_speed):
        for i in range(len(self.layers)):
            self.positions[i] -= self.speeds[i] * player_speed
            if self.positions[i] < -WINDOW_WIDTH:
                self.positions[i] += WINDOW_WIDTH
            elif self.positions[i] > WINDOW_WIDTH:
                self.positions[i] -= WINDOW_WIDTH

    def draw(self, screen):
        for i, layer in enumerate(self.layers):
            pos = self.positions[i]
            screen.blit(layer, (pos, 0))
            screen.blit(layer, (pos + WINDOW_WIDTH, 0))

# Classe para o jogador
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.idle_animations = player_idle_animations
        self.image_index = 0
        self.image = self.idle_animations[self.image_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 5
        self.animation_timer = 0

    def update(self, keys, dt):
        # Atualizar animação de idle
        self.animation_timer += dt
        if self.animation_timer > 150:  # Troca de frame a cada 150ms
            self.image_index = (self.image_index + 1) % len(self.idle_animations)
            self.image = self.idle_animations[self.image_index]
            self.animation_timer = 0

        # Movimentação com WASD
        movement = 0
        if keys[K_w]:
            self.rect.y -= self.speed
        if keys[K_s]:
            self.rect.y += self.speed
        if keys[K_a]:
            self.rect.x -= self.speed
            movement = -self.speed
        if keys[K_d]:
            self.rect.x += self.speed
            movement = self.speed

        # Limitar o jogador à tela
        self.rect.clamp_ip(screen.get_rect())
        return movement

# Classe para o inimigo
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.idle_animations = enemy_idle_animations
        self.image_index = 0
        self.image = self.idle_animations[self.image_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_timer = 0

    def update(self, dt):
        # Atualizar animação de idle
        self.animation_timer += dt
        if self.animation_timer > 150:  # Troca de frame a cada 150ms
            self.image_index = (self.image_index + 1) % len(self.idle_animations)
            self.image = self.idle_animations[self.image_index]
            self.animation_timer = 0

# Função para renderizar texto com borda
def render_with_border(text, font, text_color, border_color, border_width):
    """
    Renderiza texto com uma borda colorida ao redor.
    :param text: Texto a ser renderizado.
    :param font: Fonte do texto.
    :param text_color: Cor do texto.
    :param border_color: Cor da borda.
    :param border_width: Largura da borda.
    :return: Superfície com o texto renderizado.
    """
    # Renderizar o texto principal
    text_surface = font.render(text, True, text_color)

    # Criar uma superfície para a borda
    surface = pygame.Surface(
        (text_surface.get_width() + border_width * 2, text_surface.get_height() + border_width * 2),
        pygame.SRCALPHA
    )

    # Renderizar a borda ao redor do texto
    for dx in [-border_width, 0, border_width]:
        for dy in [-border_width, 0, border_width]:
            if dx != 0 or dy != 0:
                border_surface = font.render(text, True, border_color)
                surface.blit(border_surface, (dx + border_width, dy + border_width))

    # Renderizar o texto principal no centro
    surface.blit(text_surface, (border_width, border_width))
    return surface

# Função para o menu inicial
def menu():
    clock = pygame.time.Clock()
    running = True

    # Fundo do menu
    menu_background = Background(bg_layers, [0.05 * (i + 1) for i in range(len(bg_layers))])  # Velocidade reduzida

    # Fonte personalizada para o título e opções
    title_font = pygame.font.Font(pygame.font.match_font("timesnewroman"), 72)  # Fonte personalizada
    option_font = pygame.font.Font(pygame.font.match_font("arial"), 36)  # Fonte personalizada

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
        menu_background.update(1)

        # Desenhar fundo e texto
        screen.fill((0, 0, 0))
        menu_background.draw(screen)

        # Título do jogo com borda
        title_text = render_with_border("Dark Souls 2D", title_font, (255, 255, 255), (0, 0, 0), 3)
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Opções do menu
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (150, 150, 150)
            option_text = render_with_border(option, option_font, color, (0, 0, 0), 2)
            screen.blit(option_text, (WINDOW_WIDTH // 2 - option_text.get_width() // 2, 300 + i * 50))

        pygame.display.flip()

# Função principal do jogo
def main():
    # Inicializar objetos do jogo
    background = Background(bg_layers, [0.05 * (i + 1) for i in range(len(bg_layers))])  # Velocidade reduzida
    player = Player(50, WINDOW_HEIGHT - 200)  # Spawn no canto esquerdo
    enemy = Enemy(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 200)  # Spawn no canto direito

    # Grupo de sprites
    all_sprites = pygame.sprite.Group(player, enemy)

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
        player_movement = player.update(keys, dt)
        enemy.update(dt)
        background.update(player_movement)

        # Desenhar
        screen.fill((0, 0, 0))
        background.draw(screen)
        all_sprites.draw(screen)

        pygame.display.flip()

    pygame.quit()

# Executar o menu e o jogo
menu()
main()