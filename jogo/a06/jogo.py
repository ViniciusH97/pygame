import pygame
import os
import sys
import random

# Inicialização
pygame.init()

# Tela
WIDTH, HEIGHT = 960, 540
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mini Hitman - Visão de Cima")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (50, 50, 50)

# Fonte
FONT = pygame.font.SysFont("arial", 24)

# Clock e FPS
FPS = 60
clock = pygame.time.Clock()

# Diretórios
IMG_DIR = "jogo/animation/images"

# Carregar imagem
def load_img(name):
    path = os.path.join(IMG_DIR, name)
    return pygame.transform.scale(pygame.image.load(path), (64, 64))

# Player Sprites (Idle, Walk, Run, Crouch)
player_sprites = {
    "idle": load_img("player_idle.png"),
    "walk": load_img("player_walk.png"),
    "run": load_img("player_run.png"),
    "crouch": load_img("player_crouch.png")
}

# Inimigos
enemy_sprites = [load_img(f"enemy{i}.png") for i in range(1, 4)]
target_sprite = load_img("target.png")

# Armas
weapons = {1: "Mãos", 2: "Pistola", 3: "Sedativo", 4: "Garrote"}

# Classe Jogador
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.state = "idle"
        self.weapon = 1
        self.health = 100
        self.image = player_sprites[self.state]
        self.rect = pygame.Rect(self.x, self.y, 64, 64)

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
        self.rect.topleft = (self.x, self.y)

        for i in range(1, 5):
            if keys[getattr(pygame, f"K_{i}")]:
                self.weapon = i

    def update_image(self):
        self.image = player_sprites[self.state]

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

    def attack(self, enemies):
        for enemy in enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, 64, 64)
            if self.rect.colliderect(enemy_rect):
                if self.weapon == 1:
                    return enemy.hit("melee")
                elif self.weapon == 2:
                    return enemy.hit("pistol")
                elif self.weapon == 3:
                    return enemy.hit("sedative")
                elif self.weapon == 4:
                    return enemy.hit("garrote")
        return None

# Classe Inimigo
class Enemy:
    def __init__(self, x, y, is_target=False):
        self.x = x
        self.y = y
        self.is_target = is_target
        self.alive = True
        self.sprite = target_sprite if is_target else random.choice(enemy_sprites)
        self.rect = pygame.Rect(self.x, self.y, 64, 64)
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.move_timer = pygame.time.get_ticks()

    def draw(self, win):
        if self.alive:
            win.blit(self.sprite, (self.x, self.y))

    def update(self):
        if not self.alive:
            return
        now = pygame.time.get_ticks()
        if now - self.move_timer > 1000:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.move_timer = now
        dx, dy = self.direction
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)

    def hit(self, weapon):
        if weapon == "sedative":
            self.alive = False
            return (self.is_target, "sedated")
        elif weapon in ["melee", "pistol", "garrote"]:
            self.alive = False
            return (self.is_target, "killed")
        return None

# HUD
def draw_hud(win, points, weapon, time_left, health):
    hud_text = FONT.render(f"Pontos: {points}  |  Arma: {weapons[weapon]}  |  Tempo: {int(time_left)}s", True, BLACK)
    win.blit(hud_text, (10, 10))
    pygame.draw.rect(win, GRAY, (WIDTH - 40, HEIGHT - 110, 20, 100))
    pygame.draw.rect(win, RED, (WIDTH - 40, HEIGHT - 10 - health, 20, health))

# Fase
class Phase:
    def __init__(self, number):
        self.number = number
        self.enemies = [Enemy(100 * i, 100, is_target=(i == 2)) for i in range(1, 4)]
        self.completed = False
        self.start_time = pygame.time.get_ticks()
        self.max_time = 300000
        self.points = 0

    def draw(self, win):
        for enemy in self.enemies:
            enemy.draw(win)

    def update(self):
        for enemy in self.enemies:
            enemy.update()
        if not any(e.is_target and e.alive for e in self.enemies):
            self.completed = True

    def check_victory(self):
        return self.completed

    def handle_attack(self, player):
        result = player.attack(self.enemies)
        if result:
            is_target, method = result
            if is_target:
                self.points += 100 if method == "killed" else 50
            else:
                self.points -= 25

# Menu
def menu():
    while True:
        WIN.fill(WHITE)
        title = FONT.render("Mini Hitman - Pressione Enter para Jogar", True, BLACK)
        WIN.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 20))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

# Main Game
player = Player(WIDTH//2, HEIGHT//2)
def main():
    fases = [Phase(i) for i in range(1, 4)]
    fase_atual = 0
    run = True

    while run and fase_atual < len(fases):
        clock.tick(FPS)
        fase = fases[fase_atual]
        time_elapsed = pygame.time.get_ticks() - fase.start_time
        time_left = max(0, (fase.max_time - time_elapsed) // 1000)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                fase.handle_attack(player)

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update_image()

        fase.update()

        WIN.fill(WHITE)
        fase.draw(WIN)
        player.draw(WIN)
        draw_hud(WIN, fase.points, player.weapon, time_left, player.health)
        pygame.display.update()

        if time_left <= 0 or fase.check_victory():
            fase_atual += 1

    pygame.quit()

if __name__ == '__main__':
    menu()
    main()
