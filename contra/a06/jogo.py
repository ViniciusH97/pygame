# Jogo estilo Contra com Pygame
# Estrutura base com menu, seleção de dificuldade, inimigos, fases e HUD

import pygame
import random
import sys

# Inicializa Pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Contra Style Game")

# Clock para controlar FPS
clock = pygame.time.Clock()
FPS = 60

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Fontes
font = pygame.font.SysFont("Arial", 28)

# Variáveis globais
fase_atual = 1
pontuacao = 0
vida_jogador = 5
nivel_dificuldade = 1

# Carregar imagens (coloque na pasta jogo/images/)
jogador_img = pygame.image.load("contra/images/player.png")
inimigo_img = pygame.image.load("contra/images/enemy.png")
boss_img = pygame.image.load("contra/images/boss.png")
tiro_img = pygame.image.load("contra/images/bullet.png")
fundo_img = pygame.image.load("contra/images/background.png")

# Classes
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = jogador_img
        self.rect = self.image.get_rect(midbottom=(WIDTH//2, HEIGHT-10))
        self.velocidade = 5
        self.tiros = pygame.sprite.Group()

    def update(self, teclas):
        if teclas[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.velocidade
        if teclas[pygame.K_d] and self.rect.right < WIDTH:
            self.rect.x += self.velocidade
        if teclas[pygame.K_SPACE]:
            self.atirar()
        self.tiros.update()

    def atirar(self):
        if len(self.tiros) < 5:
            tiro = Tiro(self.rect.centerx, self.rect.top)
            self.tiros.add(tiro)

    def desenhar_tiros(self, tela):
        self.tiros.draw(tela)

class Tiro(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = tiro_img
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidade = -10

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.bottom < 0:
            self.kill()

class Inimigo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = inimigo_img
        self.rect = self.image.get_rect(midtop=(random.randint(0, WIDTH-50), -50))
        self.velocidade = 2 + fase_atual

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.top > HEIGHT:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = boss_img
        self.rect = self.image.get_rect(midtop=(WIDTH//2, -100))
        self.vida = 20 + fase_atual * 10

    def update(self):
        if self.rect.top < 50:
            self.rect.y += 2

# Funções de jogo
def desenhar_hud():
    texto_vida = font.render(f"Vida: {vida_jogador}", True, WHITE)
    texto_pontos = font.render(f"Pontos: {pontuacao}", True, WHITE)
    screen.blit(texto_vida, (10, 10))
    screen.blit(texto_pontos, (10, 40))

def menu():
    global nivel_dificuldade
    while True:
        screen.fill(BLACK)
        titulo = font.render("CONTRA STYLE - Pressione 1, 2 ou 3 para dificuldade", True, WHITE)
        screen.blit(titulo, (WIDTH//2 - titulo.get_width()//2, HEIGHT//2 - 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    nivel_dificuldade = int(event.unicode)
                    return

def jogar():
    global vida_jogador, pontuacao, fase_atual
    jogador = Jogador()
    inimigos = pygame.sprite.Group()
    boss = None
    boss_ativo = False
    tempo_spawn = 0

    while True:
        clock.tick(FPS)
        teclas = pygame.key.get_pressed()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(fundo_img, (0, 0))

        jogador.update(teclas)
        jogador.tiros.update()
        inimigos.update()

        # Spawn de inimigos
        if not boss_ativo:
            tempo_spawn += 1
            if tempo_spawn > 30 - (nivel_dificuldade * 5):
                inimigos.add(Inimigo())
                tempo_spawn = 0
            if pontuacao >= fase_atual * 10:
                boss = Boss()
                boss_ativo = True

        if boss_ativo and boss:
            boss.update()
            screen.blit(boss.image, boss.rect)
            for tiro in jogador.tiros:
                if boss.rect.colliderect(tiro.rect):
                    boss.vida -= 1
                    tiro.kill()
                    if boss.vida <= 0:
                        boss.kill()
                        fase_atual += 1
                        boss_ativo = False

        # Colisões
        for inimigo in inimigos:
            if jogador.rect.colliderect(inimigo.rect):
                vida_jogador -= 1
                inimigo.kill()
            for tiro in jogador.tiros:
                if inimigo.rect.colliderect(tiro.rect):
                    pontuacao += 1
                    inimigo.kill()
                    tiro.kill()

        screen.blit(jogador.image, jogador.rect)
        jogador.desenhar_tiros(screen)
        inimigos.draw(screen)
        desenhar_hud()
        pygame.display.flip()

        if vida_jogador <= 0:
            return

# Loop principal
menu()
jogar()
