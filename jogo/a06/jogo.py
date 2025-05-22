import pygame
import os

# Inicializa o Pygame
pygame.init()

# Constantes de tela
WIDTH, HEIGHT = 960, 540
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Hitman Isométrico")

# Cores
WHITE = (255, 255, 255)

# FPS e relógio
FPS = 60
clock = pygame.time.Clock()

# Pasta de imagens
IMG_DIR = "images"

# Carregar sprites do personagem
player_idle = pygame.image.load(os.path.join(IMG_DIR, "player_idle.png"))
player_walk = pygame.image.load(os.path.join(IMG_DIR, "player_walk.png"))
player_crouch = pygame.image.load(os.path.join(IMG_DIR, "player_crouch.png"))
player_run = pygame.image.load(os.path.join(IMG_DIR, "player_run.png"))

# Redimensionar se necessário
player_idle = pygame.transform.scale(player_idle, (64, 64))
player_walk = pygame.transform.scale(player_walk, (64, 64))
player_crouch = pygame.transform.scale(player_crouch, (64, 64))
player_run = pygame.transform.scale(player_run, (64, 64))

# Classe do jogador
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.state = "idle"
        self.image = player_idle

    def handle_input(self, keys):
        dx, dy = 0, 0
        self.state = "idle"

        if keys[pygame.K_LCTRL]:
            self.state = "crouch"
            self.speed = 1
        elif keys[pygame.K_LSHIFT]:
            self.state = "run"
            self.speed = 4
        else:
            self.speed = 2

        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed

        if dx != 0 or dy != 0:
            if self.state not in ["crouch", "run"]:
                self.state = "walk"

        self.x += dx
        self.y += dy

    def update_image(self):
        if self.state == "idle":
            self.image = player_idle
        elif self.state == "walk":
            self.image = player_walk
        elif self.state == "crouch":
            self.image = player_crouch
        elif self.state == "run":
            self.image = player_run

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

# Instancia jogador
player = Player(WIDTH//2, HEIGHT//2)

# Loop principal
def main():
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update_image()

        WIN.fill(WHITE)
        player.draw(WIN)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()