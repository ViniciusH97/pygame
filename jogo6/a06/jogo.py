import pygame
import sys

# Inicialização do Pygame
pygame.init()

# Constantes
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60

# Cores
WHITE = (255, 255, 255)

# Configurações da janela
tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dark Souls 2D")
clock = pygame.time.Clock()

# Carregando imagens
background = pygame.image.load("images/cenario_paralax.png").convert()
background = pygame.transform.scale(background, (1600, 600))
player_idle = pygame.image.load("images/player_idle.png").convert_alpha()
enemy_idle = pygame.image.load("images/enemy_idle.png").convert_alpha()

# Classe do Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_idle
        self.rect = self.image.get_rect()
        self.world_x = 400
        self.world_y = 450

    def update(self, keys):
        if keys[pygame.K_a]:
            self.world_x -= 5
        if keys[pygame.K_d]:
            self.world_x += 5

# Classe do Inimigo
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = enemy_idle
        self.rect = self.image.get_rect()
        self.world_x = x
        self.world_y = y

# Instanciando personagens
player = Player()
enemy = Enemy(1000, 450)  # inimigo fixo no "mundo"

# Loop principal
enquanto_rodando = True
while enquanto_rodando:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            enquanto_rodando = False

    # Atualização
    keys = pygame.key.get_pressed()
    player.update(keys)

    # Calcula a posição da "câmera" (centraliza o player na tela)
    camera_x = player.world_x - SCREEN_WIDTH // 2
    camera_y = 0  # sem movimento vertical por enquanto

    # Desenhar fundo
    tela.blit(background, (-camera_x, -camera_y))

    # Desenhar player no centro da tela
    player_screen_x = SCREEN_WIDTH // 2
    player_screen_y = player.world_y - camera_y
    tela.blit(player.image, (player_screen_x, player_screen_y))

    # Desenhar inimigo com base na posição do mundo
    enemy_screen_x = enemy.world_x - camera_x
    enemy_screen_y = enemy.world_y - camera_y
    tela.blit(enemy.image, (enemy_screen_x, enemy_screen_y))

    pygame.display.flip()

pygame.quit()
sys.exit()
