import os
import pygame
import random
from pygame.locals import *

# Inicialização do pygame
pygame.init()

# Configurações da tela e do mundo
WINDOW_WIDTH = pygame.display.Info().current_w
WINDOW_HEIGHT = pygame.display.Info().current_h
WORLD_WIDTH = 3000  # Largura do mundo/fase
WORLD_HEIGHT = WINDOW_HEIGHT

# Tamanhos dos personagens (você pode alterar estes valores)
PLAYER_SIZE = (500, 500)  # Tamanho do jogador (reduzido de 150x150)
ENEMY_SIZE = (500, 500)     # Tamanho dos esqueletos (reduzido de 120x120)
ARCHER_SIZE = (500, 500)    # Tamanho dos arqueiros (reduzido de 120x120)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Dark Souls 2D")

# Diretórios das imagens
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
BG_DIR = os.path.join(IMAGES_DIR, "Battleground4", "Pale")
PLAYER_IDLE_DIR = os.path.join(IMAGES_DIR, "Knight_1", "idle")
PLAYER_WALK = os.path.join(IMAGES_DIR, "Knight_1", "walk")
PLAYER_ATTACK_DIR = os.path.join(IMAGES_DIR, "Knight_1", "attack")
PLAYER_DEFEND_DIR = os.path.join(IMAGES_DIR, "Knight_1", "defend")
PLAYER_HURT_DIR = os.path.join(IMAGES_DIR, "Knight_1", "hurt")
PLAYER_RUN_DIR = os.path.join(IMAGES_DIR, "Knight_1", "run")
PLAYER_DEAD_DIR = os.path.join(IMAGES_DIR, "Knight_1", "dead")
SKELETON_IDLE_DIR = os.path.join(IMAGES_DIR, "Skeleton_Warrior", "idle")
SKELETON_WALK = os.path.join(IMAGES_DIR, "Skeleton_Warrior", "walk")
SKELETON_ATTACK_DIR = os.path.join(IMAGES_DIR, "Skeleton_Warrior", "attack")
SKELETON_HURT_DIR = os.path.join(IMAGES_DIR, "Skeleton_Warrior", "hurt")
ARCHER_IDLE_DIR = os.path.join(IMAGES_DIR, "Skeleton_Archer", "idle")
ARCHER_WALK_DIR = os.path.join(IMAGES_DIR, "Skeleton_Archer", "walk")
ARCHER_ATTACK_DIR = os.path.join(IMAGES_DIR, "Skeleton_Archer", "attack")
ARCHER_SHOT_DIR = os.path.join(IMAGES_DIR, "Skeleton_Archer", "shot1")
ARCHER_HURT_DIR = os.path.join(IMAGES_DIR, "Skeleton_Archer", "hurt")
ARCHER_DEAD_DIR = os.path.join(IMAGES_DIR, "Skeleton_Archer", "dead")

# Carregar camadas do fundo e redimensionar para caber na janela
bg_layers = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(BG_DIR, filename)).convert_alpha(),
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )
    for filename in [
        "sky.png",        # index 0 (efeito parallax)
        "back_trees.png", # index 1 (efeito parallax)
        "graves.png",     # index 2 (efeito parallax)
        "crypt.png",      # index 3 (efeito parallax)
        "wall.png",       # index 4 (efeito parallax)
        "ground.png",     # index 5 (move com o player)
        "tree.png",       # index 6 (move com o player)
        "bones.png"       # index 7 (move com o player)
    ]
]

# Carregar animações do jogador (idle) e redimensionar
player_idle_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(PLAYER_IDLE_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        PLAYER_SIZE
    )
    for i in range(1, 5) # Ajustado para 4 frames de idle
]

# Carregar animações do jogador (walk) e redimensionar
player_walk_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(PLAYER_WALK, f"row-1-column-{i}.png")).convert_alpha(),
        PLAYER_SIZE
    )
    for i in range(1, 9) 
]

player_run_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(PLAYER_RUN_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        PLAYER_SIZE
    )
    for i in range(1, 8)
]

# Carregar animações do jogador (attack) e redimensionar
player_attack_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(PLAYER_ATTACK_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        PLAYER_SIZE
    )
    for i in range(1, 6) # Ajustado para 5 frames de ataque
]

# Carregar animações do jogador (defend) e redimensionar
player_defend_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(PLAYER_DEFEND_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        PLAYER_SIZE
    )
    for i in range(1, 6)
]

# Carregar animações do jogador (hurt) e redimensionar
player_hurt_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(PLAYER_HURT_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        PLAYER_SIZE
    )
    for i in range(1, 3)
]

# Carregar animações do jogador (dead) e redimensionar
player_dead_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(PLAYER_DEAD_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        PLAYER_SIZE
    )
    for i in range(1, 7)
]

enemy_idle_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(SKELETON_IDLE_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        ENEMY_SIZE
    )
    for i in range(1, 8)
]

enemy_walk_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(SKELETON_WALK, f"row-1-column-{i}.png")).convert_alpha(),
        ENEMY_SIZE
    )
    for i in range(1, 8)
]

# Carregar animações do esqueleto guerreiro (attack) e redimensionar
enemy_attack_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(SKELETON_ATTACK_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        ENEMY_SIZE
    )
    for i in range(1, 6)
]

# Carregar animações do esqueleto guerreiro (hurt) e redimensionar
enemy_hurt_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(SKELETON_HURT_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        ENEMY_SIZE
    )
    for i in range(1, 3)
]

# Carregar animações do esqueleto guerreiro (dead) e redimensionar
SKELETON_DEAD_DIR = os.path.join(IMAGES_DIR, "Skeleton_Warrior", "dead")
enemy_dead_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(SKELETON_DEAD_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        ENEMY_SIZE
    )
    for i in range(1, 5)
]

# Carregar animações do arqueiro (idle) e redimensionar
archer_idle_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(ARCHER_IDLE_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        ARCHER_SIZE
    )
    for i in range(1, 8)
]

# Carregar animações do arqueiro (walk) e redimensionar
archer_walk_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(ARCHER_WALK_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        ARCHER_SIZE
    )
    for i in range(1, 9)
]

# Carregar animações do arqueiro (attack) e redimensionar
archer_attack_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(ARCHER_ATTACK_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        ARCHER_SIZE
    )
    for i in range(1, 6)
]

# Carregar animações do arqueiro (shot) e redimensionar
archer_shot_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(ARCHER_SHOT_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        ARCHER_SIZE
    )
    for i in range(1, 16)
]

# Carregar animações do arqueiro (hurt) e redimensionar
archer_hurt_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(ARCHER_HURT_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        ARCHER_SIZE
    )
    for i in range(1, 3)
]

# Carregar animações do arqueiro (dead) e redimensionar
archer_dead_animations = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(ARCHER_DEAD_DIR, f"row-1-column-{i}.png")).convert_alpha(),
        ARCHER_SIZE
    )
    for i in range(1, 6)
]

# Classe para flecha
class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed=8):
        super().__init__()
        # Carregar sprite da flecha
        self.original_image = pygame.image.load(os.path.join(IMAGES_DIR, "Skeleton_Archer", "Arrow.png")).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (50, 20))
        
        # Rotacionar baseado na direção
        if direction == -1:  # Indo para esquerda
            self.image = pygame.transform.flip(self.original_image, True, False)
        else:  # Indo para direita
            self.image = self.original_image
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = speed * direction
        self.damage = 20
        
    def update(self):
        self.rect.x += self.speed
        # Remove flecha se sair da tela
        if self.rect.x < -100 or self.rect.x > WORLD_WIDTH + 100:
            self.kill()

# Classe para o fundo com paralaxe
class Background:
    def __init__(self, layers, speeds, direction="horizontal"):
        self.layers = layers
        self.speeds = speeds
        self.positions = [0] * len(layers)
        self.direction = direction

    def update(self, dt, camera_x=0):
        for i in range(len(self.layers)):
            self.positions[i] = -camera_x * self.speeds[i]

    def draw(self, screen):
        for i, layer in enumerate(self.layers):
            pos = self.positions[i]
            layer_width = layer.get_width()
            pos = pos % layer_width
            if pos > 0:
                pos -= layer_width
            x = pos
            while x < screen.get_width():
                screen.blit(layer, (x, 0))
                x += layer_width

# Classe para o jogador
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Animações
        self.idle_animations = player_idle_animations
        self.walk_animations = player_walk_animations
        self.run_animations = player_run_animations
        self.attack_animations = player_attack_animations
        self.defend_animations = player_defend_animations
        self.hurt_animations = player_hurt_animations
        self.dead_animations = player_dead_animations
        
        # Estados
        self.state = "idle"  # idle, walk, run, attack, defend, hurt, dead
        self.image_index = 0
        self.image = self.idle_animations[self.image_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_timer = 0
        self.world_x = x
        self.world_y = y
        self.facing_right = True
        
        # Atributos de combate
        self.max_health = 100
        self.health = self.max_health
        self.attack_damage = 30
        self.attack_range = 100
        self.is_defending = False
        self.hurt_timer = 0
        self.attack_timer = 0
        self.dead = False
        self.death_animation_complete = False
        
        # Velocidades
        self.walk_speed = 3
        self.run_speed = 6
        
        # Hitbox para ataques
        self.attack_hitbox = pygame.Rect(0, 0, 150, 100)

    def take_damage(self, damage):
        if not self.is_defending and self.state != "hurt" and not self.dead:
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.dead = True
                self.state = "dead"
                self.image_index = 0
                self.death_animation_complete = False
            else:
                self.state = "hurt"
                self.hurt_timer = 500  # 500ms de animação de dano
                self.image_index = 0

    def attack(self):
        if self.state not in ["attack", "hurt", "dead"]:
            self.state = "attack"
            self.attack_timer = 900  # Tempo maior para completar a animação
            self.image_index = 0
            return True
        return False

    def defend(self, defending):
        if self.state not in ["attack", "hurt", "dead"]:
            self.is_defending = defending
            if defending and self.state != "defend":
                self.state = "defend"
                self.image_index = 0

    def get_attack_hitbox(self):
        if self.state == "attack" and self.image_index >= 2:  # Frame do meio da animação
            if self.facing_right:
                self.attack_hitbox.centerx = self.world_x + 100
            else:
                self.attack_hitbox.centerx = self.world_x - 50
            self.attack_hitbox.centery = self.world_y + 50
            return self.attack_hitbox
        return None

    def update(self, keys, dt, mouse_buttons):
        if self.dead and self.death_animation_complete:
            return 0
            
        self.animation_timer += dt
        
        # Reduzir timers
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.state = "idle"
                
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0 and self.state == "attack":
                self.state = "idle"

        # Controles de combate
        if mouse_buttons[0]:  # Botão esquerdo - defender
            self.defend(True)
        else:
            self.defend(False)
            
        if keys[K_SPACE]:  # Espaço - atacar
            self.attack()

        # Detectar movimento apenas se não estiver atacando/ferido
        movement = 0
        if self.state not in ["attack", "hurt", "dead"]:
            is_moving = keys[K_a] or keys[K_d] or keys[K_w] or keys[K_s]
            is_running = keys[K_LSHIFT] or keys[K_RSHIFT]
            
            # Definir velocidade
            current_speed = self.run_speed if is_running else self.walk_speed
            
            # Movimento horizontal
            if keys[K_a] and self.world_x > 0:
                self.world_x -= current_speed
                movement = -current_speed
                self.facing_right = False
                if not self.is_defending:
                    self.state = "run" if is_running else "walk"
            elif keys[K_d]:
                self.world_x += current_speed
                movement = current_speed
                self.facing_right = True
                if not self.is_defending:
                    self.state = "run" if is_running else "walk"
            
            # Movimento vertical
            if keys[K_w]:
                self.world_y -= current_speed
                if not self.is_defending and not (keys[K_a] or keys[K_d]):
                    self.state = "run" if is_running else "walk"
            elif keys[K_s]:
                self.world_y += current_speed
                if not self.is_defending and not (keys[K_a] or keys[K_d]):
                    self.state = "run" if is_running else "walk"
            
            # Voltar para idle se não estiver se movendo e não defendendo
            if not is_moving and not self.is_defending:
                self.state = "idle"
                
        # Limitar posição no mundo
        self.world_x = max(0, min(self.world_x, WORLD_WIDTH - self.rect.width))
        self.world_y = max(0, min(self.world_y, WORLD_HEIGHT - self.rect.height))

        # Atualizar animação
        self.update_animation()        
        return movement

    def update_animation(self):
        # Escolher animações baseadas no estado
        if self.state == "idle":
            current_animations = self.idle_animations
            animation_speed = 150
        elif self.state == "walk":
            current_animations = self.walk_animations
            animation_speed = 100        
        elif self.state == "run":
            current_animations = self.run_animations
            animation_speed = 80
        elif self.state == "attack":
            current_animations = self.attack_animations
            animation_speed = 180  # Velocidade ajustada para melhor visualização dos frames
        elif self.state == "defend":
            current_animations = self.defend_animations
            animation_speed = 200
        elif self.state == "hurt":
            current_animations = self.hurt_animations
            animation_speed = 150
        elif self.state == "dead":
            current_animations = self.dead_animations
            animation_speed = 200  # Animação de morte mais lenta
        else:
            current_animations = self.idle_animations
            animation_speed = 150
        
        # Atualizar frame da animação
        if self.animation_timer > animation_speed:
            if self.state == "dead":
                if self.image_index < len(current_animations) - 1:
                    self.image_index += 1
                else:
                    # Ficar no último frame da animação de morte
                    self.image_index = len(current_animations) - 1
                    self.death_animation_complete = True
            elif self.state == "attack":
                if self.image_index < len(current_animations) - 1:
                    self.image_index += 1
                else:
                    # Completou a animação de ataque, voltar para idle
                    self.state = "idle"
                    self.image_index = 0
                    self.attack_timer = 0
            else:
                self.image_index = (self.image_index + 1) % len(current_animations)
            
            # Aplicar sprite baseado na direção
            sprite = current_animations[self.image_index]
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            self.image = sprite
            
            self.animation_timer = 0

# Classe para o inimigo esqueleto guerreiro
class Enemy(pygame.sprite.Sprite):    
    def __init__(self, x, y):
        super().__init__()
        # Animações
        self.idle_animations = enemy_idle_animations
        self.walk_animations = enemy_walk_animations
        self.attack_animations = enemy_attack_animations
        self.hurt_animations = enemy_hurt_animations
        self.dead_animations = enemy_dead_animations
        
        # Estados
        self.state = "idle"  # idle, walk, attack, hurt, dead
        self.image_index = 0
        self.image = self.idle_animations[self.image_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_timer = 0
        self.world_x = x
        self.world_y = y
        self.facing_right = True
          # Atributos de combate
        self.max_health = 60
        self.health = self.max_health
        self.attack_damage = 25
        self.attack_range = 80
        self.speed = 2
        self.chase_distance = 400
        self.attack_distance = 80
        self.attack_timer = 0
        self.hurt_timer = 0
        self.dead = False
        self.death_animation_complete = False
        self.has_seen_player = False
        self.persistent_chase = False
          # Hitbox para ataques
        self.attack_hitbox = pygame.Rect(0, 0, 120, 80)

    def take_damage(self, damage):
        if self.state != "hurt" and not self.dead:
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.dead = True
                self.state = "dead"
                self.image_index = 0
                self.death_animation_complete = False
                return True  # Morreu
            else:
                self.state = "hurt"
                self.hurt_timer = 400
                self.image_index = 0
        return False

    def attack_player(self):
        if self.state not in ["attack", "hurt", "dead"]:
            self.state = "attack"
            self.attack_timer = 800
            self.image_index = 0
            return True
        return False

    def get_attack_hitbox(self):
        if self.state == "attack" and self.image_index >= 3:  
            if self.facing_right:
                self.attack_hitbox.centerx = self.world_x + 80
            else:
                self.attack_hitbox.centerx = self.world_x - 20
            self.attack_hitbox.centery = self.world_y + 50
            return self.attack_hitbox
        return None

    def update(self, dt, player_x=None, player_y=None):
        if self.dead:
            return
            
        self.animation_timer += dt
        
        # Reduzir timers
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.state = "idle"
                
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.state = "idle"
        
        # IA para seguir e atacar o player
        if player_x is not None and player_y is not None and self.state not in ["attack", "hurt"]:
            distance_x = abs(player_x - self.world_x)
            distance_y = abs(player_y - self.world_y)
            total_distance = (distance_x**2 + distance_y**2)**0.5
            
            # Atacar se estiver perto o suficiente
            if total_distance < self.attack_distance:
                self.attack_player()
            # Perseguir se estiver na distância de chase
            elif total_distance < self.chase_distance:
                self.state = "walk"
                
                # Mover em direção ao player
                if player_x > self.world_x:
                    self.world_x += self.speed
                    self.facing_right = True
                elif player_x < self.world_x:
                    self.world_x -= self.speed
                    self.facing_right = False
                
                if player_y > self.world_y:
                    self.world_y += self.speed
                elif player_y < self.world_y:
                    self.world_y -= self.speed
                
                # Manter dentro dos limites do mundo
                self.world_x = max(0, min(self.world_x, WORLD_WIDTH - self.rect.width))
                self.world_y = max(0, min(self.world_y, WORLD_HEIGHT - self.rect.height))
            else:
                self.state = "idle"
        
        # Atualizar animação
        self.update_animation()

    def update_animation(self):
        # Escolher animações baseadas no estado
        if self.state == "idle":
            current_animations = self.idle_animations
            animation_speed = 150
        elif self.state == "walk":
            current_animations = self.walk_animations
            animation_speed = 120
        elif self.state == "attack":
            current_animations = self.attack_animations
            animation_speed = 100
        elif self.state == "hurt":
            current_animations = self.hurt_animations
            animation_speed = 150
        elif self.state == "dead":
            # Usar idle como placeholder para morto
            current_animations = self.idle_animations
            animation_speed = 200
        else:
            current_animations = self.idle_animations
            animation_speed = 150
          # Atualizar frame da animação
        if self.animation_timer > animation_speed:
            if self.state == "dead":
                if self.image_index < len(current_animations) - 1:
                    self.image_index += 1
                else:
                    self.image_index = len(current_animations) - 1
            else:
                self.image_index = (self.image_index + 1) % len(current_animations)
            
            # Aplicar sprite baseado na direção
            sprite = current_animations[self.image_index]
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            self.image = sprite
            
            self.animation_timer = 0

# Classe para o arqueiro esqueleto
class Archer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Animações
        self.idle_animations = archer_idle_animations
        self.walk_animations = archer_walk_animations
        self.attack_animations = archer_attack_animations
        self.shot_animations = archer_shot_animations
        self.hurt_animations = archer_hurt_animations
        self.dead_animations = archer_dead_animations
        
        # Estados
        self.state = "idle"  # idle, walk, attack, shot, hurt, dead
        self.image_index = 0
        self.image = self.idle_animations[self.image_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_timer = 0
        self.world_x = x
        self.world_y = y
        self.facing_right = True
        
        # Atributos de combate
        self.max_health = 40
        self.health = self.max_health
        self.speed = 1.5
        self.chase_distance = 500
        self.attack_distance = 300
        self.min_distance = 150  # Distância mínima do player
        self.shoot_timer = 0
        self.shoot_cooldown = 2000  # 2 segundos entre tiros
        self.hurt_timer = 0
        self.dead = False
        self.arrow_ready = False  # Para sincronização da flecha
        self.arrow_direction = 1  # Direção da flecha

    def take_damage(self, damage):
        if self.state != "hurt" and not self.dead:
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.dead = True
                self.state = "dead"
                self.image_index = 0
                return True
            else:
                self.state = "hurt"
                self.hurt_timer = 400
                self.image_index = 0
        return False

    def shoot_arrow(self):
        if self.state not in ["shot", "hurt", "dead"] and self.shoot_timer <= 0:
            self.state = "shot"
            self.shoot_timer = self.shoot_cooldown
            self.image_index = 0
            return True
        return False

    def update(self, dt, player_x=None, player_y=None):
        if self.dead:
            return None
            
        self.animation_timer += dt
        self.shoot_timer -= dt
        
        # Reduzir timer de dano
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.state = "idle"
        
        arrow = None
        
        # IA do arqueiro
        if player_x is not None and player_y is not None and self.state not in ["shot", "hurt"]:
            distance_x = abs(player_x - self.world_x)
            distance_y = abs(player_y - self.world_y)
            total_distance = (distance_x**2 + distance_y**2)**0.5
            
            # Atirar se estiver na distância de ataque
            if total_distance < self.attack_distance and total_distance > self.min_distance:
                if self.shoot_arrow():
                    # Definir direção do tiro
                    direction = 1 if player_x > self.world_x else -1
                    self.facing_right = direction == 1
                    # Salvar dados da flecha para disparar no frame correto
                    self.arrow_direction = direction
                    self.arrow_ready = True
            
            # Manter distância mínima do player
            elif total_distance < self.min_distance:
                self.state = "walk"
                # Fugir do player
                if player_x > self.world_x:
                    self.world_x -= self.speed
                    self.facing_right = False
                else:
                    self.world_x += self.speed
                    self.facing_right = True
                    
                if player_y > self.world_y:
                    self.world_y -= self.speed
                else:
                    self.world_y += self.speed
                    
                # Manter dentro dos limites
                self.world_x = max(0, min(self.world_x, WORLD_WIDTH - self.rect.width))
                self.world_y = max(0, min(self.world_y, WORLD_HEIGHT - self.rect.height))
            
            # Perseguir se muito longe
            elif total_distance > self.chase_distance:
                self.state = "walk"
                # Aproximar do player
                if player_x > self.world_x:
                    self.world_x += self.speed
                    self.facing_right = True
                else:
                    self.world_x -= self.speed
                    self.facing_right = False
                    
                if player_y > self.world_y:
                    self.world_y += self.speed
                else:
                    self.world_y -= self.speed
                    
                # Manter dentro dos limites
                self.world_x = max(0, min(self.world_x, WORLD_WIDTH - self.rect.width))
                self.world_y = max(0, min(self.world_y, WORLD_HEIGHT - self.rect.height))
            else:
                self.state = "idle"
        
        # Verificar se deve disparar flecha no frame correto da animação
        if (self.state == "shot" and self.arrow_ready and 
            self.image_index >= len(self.shot_animations) - 3):  # Alguns frames antes do final
            # Calcular posição da flecha baseada na posição e direção do arqueiro
            arrow_x = self.world_x + (200 if self.facing_right else -50)  # Posição à frente do arqueiro
            arrow_y = self.world_y + 150  # Altura do peito do arqueiro
            arrow = Arrow(arrow_x, arrow_y, self.arrow_direction)
            self.arrow_ready = False
        
        # Atualizar animação
        self.update_animation()
        
        return arrow

    def update_animation(self):
        # Escolher animações baseadas no estado
        if self.state == "idle":
            current_animations = self.idle_animations
            animation_speed = 150
        elif self.state == "walk":
            current_animations = self.walk_animations
            animation_speed = 120
        elif self.state == "attack":
            current_animations = self.attack_animations
            animation_speed = 100
        elif self.state == "shot":
            current_animations = self.shot_animations
            animation_speed = 120  # Animação de tiro mais rápida
        elif self.state == "hurt":
            current_animations = self.hurt_animations
            animation_speed = 150
        elif self.state == "dead":
            current_animations = self.dead_animations
            animation_speed = 150
        else:
            current_animations = self.idle_animations
            animation_speed = 150
          # Atualizar frame da animação
        if self.animation_timer > animation_speed:
            if self.state == "dead":
                if self.image_index < len(current_animations) - 1:
                    self.image_index += 1
                else:
                    # Ficar no último frame da animação de morte
                    self.image_index = len(current_animations) - 1
            elif self.state == "shot":
                if self.image_index < len(current_animations) - 1:
                    self.image_index += 1
                else:
                    # Mostrar o último frame antes de voltar para idle
                    self.state = "idle"
                    self.image_index = 0
            else:
                self.image_index = (self.image_index + 1) % len(current_animations)
            
            # Aplicar sprite baseado na direção
            sprite = current_animations[self.image_index]
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
            self.image = sprite
            
            self.animation_timer = 0

# Função para o menu inicial
def menu():
    clock = pygame.time.Clock()
    running = True
    menu_layers = []
    menu_speeds = [0.2, 0.4, 0.7, 1.0, 1.5, 2.0, 2.5]
    MENU_BG_DIR = os.path.join(IMAGES_DIR, "Battleground1", "Pale")
    menu_layer_files = ["sky.png", "ruins_bg.png", "hills&trees.png", "stones&grass.png", "ruins.png", "ruins2.png", "statue.png"]
    for filename in menu_layer_files:
        path = os.path.join(MENU_BG_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
            menu_layers.append(img)
    menu_background = Background(menu_layers, menu_speeds)
    title_font = pygame.font.SysFont("Times New Roman", 72, bold=True)
    option_font = pygame.font.SysFont("Arial", 36)
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
                if event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                if event.key == K_RETURN:
                    if selected_option == 0:
                        running = False
                    elif selected_option == 1:
                        pygame.quit()
                        exit()

        menu_background.update(dt, pygame.time.get_ticks() * 0.05)
        screen.fill((0, 0, 0))
        menu_background.draw(screen)
        title_text = title_font.render("Dark Souls 2D", True, (255, 255, 255))
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected_option else (150, 150, 150)
            option_text = option_font.render(option, True, color)
            screen.blit(option_text, (WINDOW_WIDTH // 2 - option_text.get_width() // 2, 300 + i * 50))
        pygame.display.flip()

# Função para desenhar a barra de vida
def draw_health_bar(screen, x, y, current_health, max_health, width=200, height=20):
    # Borda preta
    border_rect = pygame.Rect(x - 2, y - 2, width + 4, height + 4)
    pygame.draw.rect(screen, (0, 0, 0), border_rect)
    
    # Fundo vermelho (vida perdida)
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, (139, 0, 0), bg_rect)
    
    # Vida atual (verde)
    if current_health > 0:
        health_width = int((current_health / max_health) * width)
        health_rect = pygame.Rect(x, y, health_width, height)
        pygame.draw.rect(screen, (0, 139, 0), health_rect)

# Função para tela de morte
def death_screen():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Times New Roman", 100, bold=True)
    subtitle_font = pygame.font.SysFont("Arial", 40)
    
    fade_alpha = 0
    text_alpha = 0
    show_restart = False
    
    while True:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_r and show_restart:
                    return "menu"  # Voltar para o menu
                if event.key == K_ESCAPE:
                    pygame.quit()
                    exit()
        
        # Efeito de fade gradual
        if fade_alpha < 255:
            fade_alpha += 3
        elif text_alpha < 255:
            text_alpha += 4
        elif not show_restart:
            show_restart = True
        
        # Desenhar tela preta
        screen.fill((0, 0, 0))
        
        # Overlay preto com fade
        if fade_alpha > 0:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(fade_alpha)
            overlay.fill((0, 0, 0))  # Preto
            screen.blit(overlay, (0, 0))
        
        # Texto "YOU DIED" em vermelho
        if text_alpha > 0:
            death_text = font.render("YOU DIED", True, (255, 0, 0))  # Vermelho
            death_text.set_alpha(text_alpha)
            text_x = WINDOW_WIDTH // 2 - death_text.get_width() // 2
            text_y = WINDOW_HEIGHT // 2 - death_text.get_height() // 2
            screen.blit(death_text, (text_x, text_y))
        
        # Opções de reiniciar em branco
        if show_restart:
            restart_text = subtitle_font.render("Press R to return to menu or ESC to exit", True, (200, 200, 200))
            restart_x = WINDOW_WIDTH // 2 - restart_text.get_width() // 2
            restart_y = text_y + 150
            screen.blit(restart_text, (restart_x, restart_y))
        
        pygame.display.flip()

# Função principal do jogo
def main():
    # Parallax apenas nas camadas de fundo (0 a 4), os elementos visuais próximos ao jogador não devem ter paralaxe
    paralax_speeds = [0.1, 0.12, 0.15, 0.2, 0.25, 0.5, 0.5, 0.5]  # Árvore, chão e ossos sem paralaxe
    background = Background(bg_layers, paralax_speeds)    
    player = Player(50, WINDOW_HEIGHT - 400)
    enemy = Enemy(300, WINDOW_HEIGHT - 400)
    archer = Archer(600, WINDOW_HEIGHT - 400)
    
    # Grupos de sprites
    arrows = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    enemies.add(enemy)
    archers = pygame.sprite.Group()
    archers.add(archer)

    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
        
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        
        # Atualizar player
        player_movement = player.update(keys, dt, mouse_buttons)
        
        # Verificar se player morreu e completou a animação de morte
        if player.dead and player.death_animation_complete:
            if death_screen() == "menu":
                return "menu"  # Voltar para o menu
            else:
                running = False
            continue
        
        # Atualizar inimigos
        enemy.update(dt, player.world_x, player.world_y)
        
        # Atualizar arqueiros
        new_arrow = archer.update(dt, player.world_x, player.world_y)
        if new_arrow:
            arrows.add(new_arrow)
        
        # Atualizar flechas
        arrows.update()
        
        # Verificar colisões de ataque do player
        player_hitbox = player.get_attack_hitbox()
        if player_hitbox:
            # Atacar esqueletos guerreiros
            for enemy_sprite in enemies.copy():
                if player_hitbox.colliderect(pygame.Rect(enemy_sprite.world_x, enemy_sprite.world_y, 
                                                       enemy_sprite.rect.width, enemy_sprite.rect.height)):
                    if enemy_sprite.take_damage(player.attack_damage):
                        enemies.remove(enemy_sprite)
            
            # Atacar arqueiros
            for archer_sprite in archers.copy():
                if player_hitbox.colliderect(pygame.Rect(archer_sprite.world_x, archer_sprite.world_y, 
                                                        archer_sprite.rect.width, archer_sprite.rect.height)):
                    if archer_sprite.take_damage(player.attack_damage):
                        archers.remove(archer_sprite)
        
        # Verificar colisões de ataque dos inimigos
        enemy_hitbox = enemy.get_attack_hitbox()
        if enemy_hitbox:
            player_rect = pygame.Rect(player.world_x, player.world_y, player.rect.width, player.rect.height)
            if enemy_hitbox.colliderect(player_rect):
                player.take_damage(enemy.attack_damage)
        
        # Verificar colisões das flechas com o player
        for arrow in arrows.copy():
            player_rect = pygame.Rect(player.world_x, player.world_y, player.rect.width, player.rect.height)
            arrow_rect = pygame.Rect(arrow.rect.x, arrow.rect.y, arrow.rect.width, arrow.rect.height)
            if arrow_rect.colliderect(player_rect):
                player.take_damage(arrow.damage)
                arrows.remove(arrow)
        
        # Atualizar câmera
        camera_x = max(0, player.world_x - WINDOW_WIDTH // 2)
        camera_y = 0
        background.update(dt, camera_x)
        
        # Desenhar tudo
        screen.fill((0, 0, 0))
        background.draw(screen)
        
        # Posições na tela
        player_screen_x = player.world_x - camera_x
        player_screen_y = player.world_y - camera_y
        enemy_screen_x = enemy.world_x - camera_x
        enemy_screen_y = enemy.world_y - camera_y
        
        # Desenhar sprites
        screen.blit(player.image, (player_screen_x, player_screen_y))
        if not enemy.dead:
            screen.blit(enemy.image, (enemy_screen_x, enemy_screen_y))
        if not archer.dead:
            screen.blit(archer.image, (archer.world_x - camera_x, archer.world_y - camera_y))
        
        # Desenhar flechas
        for arrow in arrows:
            arrow_screen_x = arrow.rect.x - camera_x
            arrow_screen_y = arrow.rect.y
            screen.blit(arrow.image, (arrow_screen_x, arrow_screen_y))
        
        # Desenhar UI
        # Barra de vida do player (canto inferior direito)
        health_x = WINDOW_WIDTH - 220
        health_y = WINDOW_HEIGHT - 40
        draw_health_bar(screen, health_x, health_y, player.health, player.max_health)
        
        # Texto da vida
        font = pygame.font.SysFont("Arial", 16)
        health_text = font.render(f"HP: {player.health}/{player.max_health}", True, (255, 255, 255))
        screen.blit(health_text, (health_x, health_y - 20))
        
        # Instruções de controle (canto superior esquerdo)
        instructions = [
            "WASD - Mover",
            "SHIFT - Correr", 
            "ESPAÇO - Atacar",
            "Mouse Left - Defender",
            "ESC - Sair"
        ]
        instruction_font = pygame.font.SysFont("Arial", 14)
        for i, instruction in enumerate(instructions):
            inst_text = instruction_font.render(instruction, True, (255, 255, 255))
            screen.blit(inst_text, (10, 10 + i * 20))
        
        pygame.display.flip()

if __name__ == "__main__":
    while True:
        menu()
        result = main()
        if result != "menu":
            break
    pygame.quit()
