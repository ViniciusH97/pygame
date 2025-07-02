import os
import pygame
from pygame.locals import *

pygame.init()

WINDOW_WIDTH = pygame.display.Info().current_w
WINDOW_HEIGHT = pygame.display.Info().current_h

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Survive If You Can")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "imagens")

class AnimatedSprite:
    def __init__(self, spritesheet_path, frame_width, frame_height, frame_count, frame_duration=100):
        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame_count = frame_count
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.frame_timer = 0
        self.frames = []

        for i in range(frame_count):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(self.spritesheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
            self.frames.append(frame)
    
    def update(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.frame_timer = 0
    
    def get_current_frame(self):
        return self.frames[self.current_frame]
    
    def reset(self):
        self.current_frame = 0
        self.frame_timer = 0

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

class Player:
    def __init__(self, x, y, character="Raider_1"):
        self.world_x = x
        self.world_y = y
        self.speed = 200
        self.run_speed = 350
        self.scale = 3.0  
        hitbox_width = int(128 * self.scale * 0.2)
        hitbox_height = int(128 * self.scale * 0.4)
        self.rect = pygame.Rect(x, y, hitbox_width, hitbox_height)
        self.facing_right = True
        self.attack_combo = 0  # 0 for attack_1, 1 for attack_2
        self.animation_timer = 0
        self.current_state = "idle"
        self.animation_complete = True
        self.character = character
        self.is_jumping = False
        self.jump_start_y = y
        self.jump_velocity = 0
        self.gravity = 800
        self.jump_strength = -300
        self.horizontal_velocity = 0  # Para manter velocidade horizontal durante o pulo
        self.was_moving_when_jumped = False  # Para saber se estava se movendo quando pulou
        self.max_health = 100
        self.health = self.max_health
        self.is_dead = False
        self.death_animation_complete = False
        self.invulnerability_timer = 0
        self.invulnerability_duration = 1000  # 1 second of invulnerability after taking damage
        self.screen_flash_timer = 0  # Timer for screen flash effect
        self.screen_flash_duration = 300  # Duration of screen flash in milliseconds
        
        # Ammunition system
        self.max_ammo = 5
        self.current_ammo = self.max_ammo
        self.is_reloading = False
    
        raider_dir = os.path.join(IMAGES_DIR, character)
        try:
            idle_path = os.path.join(raider_dir, "Idle.png")
            print(f"Loading idle sprite from: {idle_path}")
            
            idle_sheet = pygame.image.load(idle_path).convert_alpha()
            print(f"Idle spritesheet size: {idle_sheet.get_size()}")
            self.animations = {
                "idle": AnimatedSprite(idle_path, 128, 128, 6, 200),
                "walk": AnimatedSprite(os.path.join(raider_dir, "Walk.png"), 128, 128, 8, 100),
                "run": AnimatedSprite(os.path.join(raider_dir, "Run.png"), 128, 128, 8, 80),
                "attack_1": AnimatedSprite(os.path.join(raider_dir, "Attack_1.png"), 128, 128, 6, 120),  # 768x128 = 6 frames
                "attack_2": AnimatedSprite(os.path.join(raider_dir, "Attack_2.png"), 128, 128, 3, 120),  # 384x128 = 3 frames
                "shot": AnimatedSprite(os.path.join(raider_dir, "Shot.png"), 128, 128, 12, 80),  # 1536x128 = 12 frames
                "jump": AnimatedSprite(os.path.join(raider_dir, "Jump.png"), 128, 128, 11, 100),  # 1408x128 = 11 frames
                "recharge": AnimatedSprite(os.path.join(raider_dir, "Recharge.png"), 128, 128, 12, 150),  # 1536x128 = 12 frames
                "dead": AnimatedSprite(os.path.join(raider_dir, "Dead.png"), 128, 128, 4, 200),  # 512x128 = 4 frames
                "hurt": AnimatedSprite(os.path.join(raider_dir, "Hurt.png"), 128, 128, 2, 150),  # 256x128 = 2 frames
            }
            
            fallback_surface = pygame.Surface((128, 128), pygame.SRCALPHA)
            fallback_surface.fill((0, 255, 0)) 
            
            fallback_anim = AnimatedSprite.__new__(AnimatedSprite)
            fallback_anim.frames = [fallback_surface]
            fallback_anim.current_frame = 0
            fallback_anim.frame_timer = 0            
            fallback_anim.frame_count = 1
            fallback_anim.frame_duration = 200
            # Não precisamos mais de fallback para hurt já que carregamos a animação real
            
        except Exception as e:
            print(f"Error loading sprites: {e}")
            fallback_surface = pygame.Surface((128, 128))
            fallback_surface.fill((255, 0, 0))  
            
            fallback_anim = AnimatedSprite.__new__(AnimatedSprite)
            fallback_anim.frames = [fallback_surface]
            fallback_anim.current_frame = 0
            fallback_anim.frame_timer = 0
            fallback_anim.frame_count = 1
            fallback_anim.frame_duration = 200
            fallback_anim.update = lambda dt: None
            fallback_anim.get_current_frame = lambda: fallback_surface
            
            self.animations = {"idle": fallback_anim}
            for anim_name in ["walk", "run", "attack_1", "attack_2", "shot", "recharge", "hurt", "dead", "jump"]:
                self.animations[anim_name] = fallback_anim        
                self.current_animation = self.animations["idle"]
        
    def update(self, keys, dt, mouse_buttons, events):
        movement = 0
        is_moving = False
        is_running = False
          # Calcular velocidade de movimento antes de processar eventos
        current_speed = self.run_speed if (keys[K_LSHIFT] or keys[K_RSHIFT]) else self.speed
        current_horizontal_velocity = 0
        
        # Verificar movimento atual para capturar durante o pulo
        if keys[K_a] or keys[K_LEFT]:
            current_horizontal_velocity = -current_speed
            is_moving = True
        if keys[K_d] or keys[K_RIGHT]:
            current_horizontal_velocity = current_speed
            is_moving = True
            
        # Atualizar timer de invulnerabilidade
        if self.invulnerability_timer > 0:
            self.invulnerability_timer -= dt
          # Atualizar timer de flash da tela
        if self.screen_flash_timer > 0:
            self.screen_flash_timer -= dt
          # Se o jogador estiver morto, não processar nenhuma entrada
        if self.is_dead:
            # Atualizar apenas animação de morte se não estiver completa
            if not self.death_animation_complete:
                self.current_animation = self.animations[self.current_state]
                self.animation_timer += dt
                
                # Verificar se a animação de morte foi concluída
                animation_duration = len(self.current_animation.frames) * self.current_animation.frame_duration
                if self.animation_timer >= animation_duration:
                    # Animação de morte completa - permanecer no último frame
                    self.death_animation_complete = True
                    self.current_animation.current_frame = len(self.current_animation.frames) - 1
                    print("Animação de morte completa - permanecendo no último frame")
                else:
                    self.current_animation.update(dt)
            return movement
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3 and self.current_state in ["idle", "walk", "run"]:  # Botão direito do mouse
                    if self.attack_combo == 0:
                        self.current_state = "attack_1"
                        self.attack_combo = 1
                        print("Attack_1 ativado!")
                    else:
                        self.current_state = "attack_2"
                        self.attack_combo = 0
                        print("Attack_2 (coronhada) ativado!")
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
                
                elif event.button == 1 and self.current_state in ["idle", "walk", "run"] and self.current_ammo > 0 and not self.is_reloading:  # Botão esquerdo do mouse
                    self.current_state = "shot"
                    self.current_ammo -= 1
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
                    print(f"Tiro disparado! Munição restante: {self.current_ammo}/{self.max_ammo}")
            
            if event.type == KEYDOWN:
                if event.key == K_SPACE and self.current_state in ["idle", "walk", "run"] and not self.is_jumping:
                    self.current_state = "jump"
                    self.is_jumping = True
                    self.jump_start_y = self.world_y
                    self.jump_velocity = self.jump_strength
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
                
                elif event.key == K_r and self.current_state in ["idle", "walk", "run"] and self.current_ammo < self.max_ammo:
                    self.current_state = "recharge"
                    self.is_reloading = True
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
                    print("Recarregando...")
          # Gerenciar animações de ação
        if self.current_state in ["attack_1", "attack_2", "shot", "recharge", "jump", "dead", "hurt"]:
            self.animation_timer += dt
            
            animation_duration = len(self.current_animation.frames) * self.current_animation.frame_duration
            if self.animation_timer >= animation_duration:
                if self.current_state == "dead":
                    # Animação de morte completa - permanecer no último frame
                    self.death_animation_complete = True
                    self.current_animation.current_frame = len(self.current_animation.frames) - 1
                    return movement  # Não mudar estado, permanecer morto
                elif self.current_state == "jump":
                    self.is_jumping = False
                    self.world_y = self.jump_start_y  # Resetar para o chão
                elif self.current_state == "recharge":
                    self.current_ammo = self.max_ammo
                    self.is_reloading = False
                    print(f"Recarga completa! Munição: {self.current_ammo}/{self.max_ammo}")
                elif self.current_state == "hurt":
                    # Após animação de dano, voltar ao estado apropriado
                    pass  # Continuará para o estado idle abaixo
                self.current_state = "idle"
                self.animation_complete = True
                self.animation_timer = 0
        
        # Handle jumping physics
        if self.is_jumping:
            self.jump_velocity += self.gravity * dt / 1000
            self.world_y += self.jump_velocity * dt / 1000
            
            # Land when back to ground level
            if self.world_y >= self.jump_start_y:
                self.world_y = self.jump_start_y
                self.is_jumping = False
                if self.current_state == "jump":
                    self.current_state = "idle"
        
        # Handle movement only if not performing actions
        if self.current_state in ["idle", "walk", "run"]:
            # Check if SHIFT is pressed for running
            if keys[K_LSHIFT] or keys[K_RSHIFT]:
                is_running = True
                current_speed = self.run_speed
            else:
                current_speed = self.speed
            
            if keys[K_a] or keys[K_LEFT]:
                movement -= current_speed * dt / 1000
                self.facing_right = False
                is_moving = True
                
            if keys[K_d] or keys[K_RIGHT]:
                movement += current_speed * dt / 1000
                self.facing_right = True
                is_moving = True
            if keys[K_w] or keys[K_UP]:
                self.world_y -= current_speed * dt / 1000
                is_moving = True
                
            if keys[K_s] or keys[K_DOWN]:
                self.world_y += current_speed * dt / 1000
                is_moving = True
                
            self.world_x += movement
            
            if is_moving:
                if is_running:
                    self.current_state = "run"
                else:
                    self.current_state = "walk"
            else:
                self.current_state = "idle"        # Manter o jogador dentro dos limites do mundo
        self.world_x = max(0, self.world_x)  # Não ir abaixo de x=0
        self.world_y = max(380, min(self.world_y, 500))

        self.current_animation = self.animations[self.current_state]
        self.current_animation.update(dt)
        return movement
        
    def take_damage(self, damage):
        """Fazer o jogador receber dano"""
        if self.invulnerability_timer > 0 or self.is_dead:
            return False
        
        self.health -= damage
        self.invulnerability_timer = self.invulnerability_duration
        self.screen_flash_timer = self.screen_flash_duration  # Ativar flash na tela
        
        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.current_state = "dead"
            self.animation_timer = 0
            self.animation_complete = False
            self.death_animation_complete = False  # Certificar que a animação de morte vai rodar
            self.current_animation = self.animations[self.current_state]  # Definir animação de morte
            self.current_animation.reset()
            print("Jogador morreu!")
            return True
        else:
            # Ativar animação de dano se não estiver morto
            if self.current_state not in ["dead", "hurt"]:
                self.current_state = "hurt"
                self.animation_timer = 0
                self.animation_complete = False
                self.current_animation.reset()
            print(f"Jogador recebeu {damage} de dano! Vida: {self.health}/{self.max_health}")
            return False

    def get_image(self):
        try:
            image = self.current_animation.get_current_frame()
            if image and image.get_width() > 0 and image.get_height() > 0:
                # Define scaled_size first
                scaled_size = (int(128 * self.scale), int(128 * self.scale))
                
                if not self.facing_right:
                    image = pygame.transform.flip(image, True, False)
                
                image = pygame.transform.scale(image, scaled_size)
                return image
            else:
                fallback = pygame.Surface((int(128 * self.scale), int(128 * self.scale)))
                fallback.fill((255, 255, 0))  
                return fallback
        except Exception as e:
            print(f"Error getting player image: {e}")
            fallback = pygame.Surface((int(128 * self.scale), int(128 * self.scale)))
            fallback.fill((255, 0, 255))  
            return fallback
    
    def draw_health_bar(self, screen):
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = 20
        
        # Background (dark red)
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Health (bright red)
        health_percentage = self.health / self.max_health
        health_width = int(bar_width * health_percentage)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Health text
        font = pygame.font.SysFont("Arial", 16)
        health_text = f"HP: {self.health}/{self.max_health}"
        text_surface = font.render(health_text, True, (255, 255, 255))
        screen.blit(text_surface, (bar_x + bar_width + 10, bar_y + 2))
    def draw_ammo_counter(self, screen):
        """Desenhar contador de munição na tela"""
        ammo_x = 20
        ammo_y = 50
        
        font = pygame.font.SysFont("Arial", 18)
        ammo_text = f"Munição: {self.current_ammo}/{self.max_ammo}"
        if self.is_reloading:
            ammo_text += " (Recarregando...)"
        elif self.current_ammo == 0:
            ammo_text += " - Pressione R para recarregar"
        
        color = (255, 255, 255) if self.current_ammo > 0 else (255, 0, 0)
        text_surface = font.render(ammo_text, True, color)
        screen.blit(text_surface, (ammo_x, ammo_y))

    def draw_screen_flash(self, screen):
        """Draw screen flash effect when player takes damage"""
        if self.screen_flash_timer > 0:
            # Create a red overlay that covers the entire screen
            flash_alpha = int(150 * (self.screen_flash_timer / self.screen_flash_duration))
            flash_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((255, 0, 0, flash_alpha))
            screen.blit(flash_surface, (0, 0))

class Zombie:
    def __init__(self, x, y, zombie_type="Zombie_1"):
        self.world_x = x
        self.world_y = y
        self.scale = 2.5
        self.speed = 180  # Aumentado de 120 para 180 - zumbis mais rápidos
        self.max_health = 100
        self.health = self.max_health
        self.facing_right = False
        self.current_state = "idle"
        self.is_dead = False
        self.death_animation_complete = False  # Para controlar quando a animação de morte termina
        self.should_remove = False  # Para controlar quando remover o zumbi
        self.attack_timer = 0
        self.attack_cooldown = 800  # Reduzido de 2000 para 800ms - ataques mais frequentes
        self.attack_range = 120  # Aumentado de 80 para 120 - maior alcance de ataque
        self.attack_damage = 20
        self.animation_timer = 0
        self.animation_complete = True
        self.zombie_type = zombie_type  # Tipo do zumbi (Zombie_1, Zombie_2, etc.)
          # Hitbox menor para ataques corpo a corpo (melee)
        melee_hitbox_width = int(128 * self.scale * 0.5)
        melee_hitbox_height = int(128 * self.scale * 0.5)
        self.melee_rect = pygame.Rect(x, y, melee_hitbox_width, melee_hitbox_height)
        
        # Hitbox maior para ataques à distância (ranged/shot) - aumentada para melhor jogabilidade
        ranged_hitbox_width = int(128 * self.scale * 1.2)  # Aumentado de 0.4 para 0.6
        ranged_hitbox_height = int(128 * self.scale * 0.7)  # Aumentado de 0.5 para 0.7
        self.ranged_rect = pygame.Rect(x, y, ranged_hitbox_width, ranged_hitbox_height)
        
        # Manter rect principal para compatibilidade (usar o melee como padrão)
        self.rect = self.melee_rect
        
        zombie_dir = os.path.join(IMAGES_DIR, zombie_type)
        
        try:
            # Configurações específicas para cada tipo de zumbi
            if zombie_type == "Zombie_1":
                self.animations = {
                    "idle": AnimatedSprite(os.path.join(zombie_dir, "Idle.png"), 128, 128, 6, 300),
                    "walk": AnimatedSprite(os.path.join(zombie_dir, "Walk.png"), 128, 128, 10, 150),  # 1280x128 = 10 frames
                    "attack": AnimatedSprite(os.path.join(zombie_dir, "Attack.png"), 128, 128, 5, 200),  # 640x128 = 5 frames
                    "hurt": AnimatedSprite(os.path.join(zombie_dir, "Hurt.png"), 128, 128, 4, 150),  # 512x128 = 4 frames
                    "dead": AnimatedSprite(os.path.join(zombie_dir, "Dead.png"), 128, 128, 5, 200),  # 640x128 = 5 frames
                }
            elif zombie_type == "Zombie_2":
                self.animations = {
                    "idle": AnimatedSprite(os.path.join(zombie_dir, "Idle.png"), 128, 128, 6, 300),  # 768x128 = 6 frames
                    "walk": AnimatedSprite(os.path.join(zombie_dir, "Walk.png"), 128, 128, 10, 150),  # 1280x128 = 10 frames
                    "attack": AnimatedSprite(os.path.join(zombie_dir, "Attack.png"), 128, 128, 5, 200),  # 640x128 = 5 frames
                    "hurt": AnimatedSprite(os.path.join(zombie_dir, "Hurt.png"), 128, 128, 4, 150),  # 512x128 = 4 frames
                    "dead": AnimatedSprite(os.path.join(zombie_dir, "Dead.png"), 128, 128, 5, 200),  # 640x128 = 5 frames
                }
                # Zombie_2 pode ter características diferentes
                self.speed = 160  # Ligeiramente mais lento que Zombie_1
                self.attack_damage = 25  # Mais dano que Zombie_1
                self.max_health = 120  # Mais vida que Zombie_1
                self.health = self.max_health
            
        except Exception as e:
            print(f"Error loading zombie sprites: {e}")
            # Create a simple fallback
            fallback_surface = pygame.Surface((128, 128))
            fallback_surface.fill((0, 150, 0))  # Green for zombie
            
            fallback_anim = AnimatedSprite.__new__(AnimatedSprite)
            fallback_anim.frames = [fallback_surface]
            fallback_anim.current_frame = 0
            fallback_anim.frame_timer = 0
            fallback_anim.frame_count = 1
            fallback_anim.frame_duration = 300
            fallback_anim.update = lambda dt: None
            fallback_anim.get_current_frame = lambda: fallback_surface
            
            self.animations = {
                "idle": fallback_anim,
                "walk": fallback_anim,
                "attack": fallback_anim,
                "hurt": fallback_anim,
                "dead": fallback_anim
            }
        
        self.current_animation = self.animations["idle"]
    def update(self, dt, player):
        if self.is_dead and self.death_animation_complete:
            return  # Zumbi morto, não precisa mais atualizar
        
        self.attack_timer += dt
        
        # Handle action animations (attack, hurt, dead)
        if self.current_state in ["attack", "hurt", "dead"]:
            self.animation_timer += dt
            
            animation_duration = len(self.current_animation.frames) * self.current_animation.frame_duration
            if self.animation_timer >= animation_duration:
                if self.current_state == "dead":
                    self.is_dead = True
                    self.death_animation_complete = True
                    # Manter o último frame da animação de morte
                    self.current_animation.current_frame = len(self.current_animation.frames) - 1
                    return
                elif self.current_state == "hurt":
                    # After hurt animation, go back to appropriate state
                    distance = abs(self.world_x - player.world_x)
                    if distance <= self.attack_range + 50:  # Um pouco mais de distância para evitar oscilação
                        self.current_state = "idle"
                    else:
                        self.current_state = "walk"
                elif self.current_state == "attack":
                    # Check if attack hit the player
                    distance = abs(self.world_x - player.world_x)
                    if distance <= self.attack_range:
                        player.take_damage(self.attack_damage)
                    
                    # After attack animation, check if still in range
                    if distance <= self.attack_range:
                        self.current_state = "idle"                    
                    else:
                        self.current_state = "walk"
                        self.animation_complete = True
                self.animation_timer = 0
        else:
            # IA melhorada - perseguir o jogador agressivamente sem limitações
            distance_x = player.world_x - self.world_x
            distance_y = player.world_y - self.world_y
            total_distance = (distance_x**2 + distance_y**2)**0.5
            
            # Sempre atacar quando estiver ao alcance e cooldown estiver pronto
            if total_distance <= self.attack_range and self.attack_timer >= self.attack_cooldown:
                # Próximo o suficiente para atacar e cooldown pronto
                self.current_state = "attack"
                self.attack_timer = 0
                self.animation_timer = 0
                self.animation_complete = False
                self.current_animation.reset()
                
            elif total_distance > self.attack_range:  # Buffer reduzido para ataques mais frequentes
                # Mover em direção ao jogador - perseguição direta e agressiva
                self.current_state = "walk"
                
                # Movimento em X - direto ao jogador
                if abs(distance_x) > 5:  # Limiar menor para movimento mais responsivo
                    if distance_x > 0:
                        self.world_x += self.speed * dt / 1000
                        self.facing_right = True
                    else:
                        self.world_x -= self.speed * dt / 1000
                        self.facing_right = False
                
                # Movimento em Y - direto ao jogador
                if abs(distance_y) > 5:  # Limiar menor para movimento mais responsivo
                    if distance_y > 0:
                        self.world_y += self.speed * dt / 1000
                    else:                        self.world_y -= self.speed * dt / 1000
            else:                
                # Próximo ao jogador mas ainda não atacando - ficar idle e virar para o jogador
                self.current_state = "idle"
                self.facing_right = distance_x > 0
          
        # Manter zumbi dentro dos mesmos limites Y que o jogador
        self.world_y = max(380, min(self.world_y, 500))
          # Atualizar animação - mas não atualizar se animação de morte estiver completa
        self.current_animation = self.animations[self.current_state]
        if not (self.is_dead and self.death_animation_complete):
            self.current_animation.update(dt)
              # Atualizar posições de ambas as hitboxes
        # Hitbox melee (menor)
        melee_offset_x = (int(128 * self.scale) - self.melee_rect.width) // 2
        melee_offset_y = (int(128 * self.scale) - self.melee_rect.height) // 2
        
        self.melee_rect.x = self.world_x + melee_offset_x
        self.melee_rect.y = self.world_y + melee_offset_y
          # Hitbox à distância (maior)
        ranged_offset_x = (int(128 * self.scale) - self.ranged_rect.width) // 2
        ranged_offset_y = (int(128 * self.scale) - self.ranged_rect.height) // 2
        
        self.ranged_rect.x = self.world_x + ranged_offset_x
        self.ranged_rect.y = self.world_y + ranged_offset_y
        
        # Atualizar rect principal para usar hitbox melee por compatibilidade
        self.rect = self.melee_rect
    
    def take_damage(self, damage):
        if self.is_dead or self.current_state == "dead":
            return False
        
        self.health -= damage
        
        if self.health <= 0:
            self.health = 0
            self.current_state = "dead"
            self.animation_timer = 0
            self.animation_complete = False
            self.current_animation.reset()
            print(f"Zombie died!")
            return True  # Zombie died
        else:
            self.current_state = "hurt"
            self.animation_timer = 0
            self.animation_complete = False
            self.current_animation.reset()            
            print(f"Zombie took {damage} damage! Health: {self.health}/{self.max_health}")
            return False  # Zombie still alive
    
    def get_image(self):
        try:
            image = self.current_animation.get_current_frame()
            if image and image.get_width() > 0 and image.get_height() > 0:
                if not self.facing_right:
                    image = pygame.transform.flip(image, True, False)
                
                scaled_size = (int(128 * self.scale), int(128 * self.scale))
                image = pygame.transform.scale(image, scaled_size)
                return image
            else:
                fallback = pygame.Surface((int(128 * self.scale), int(128 * self.scale)))
                fallback.fill((0, 150, 0))
                return fallback
        except Exception as e:
            print(f"Error getting zombie image: {e}")
            fallback = pygame.Surface((int(128 * self.scale), int(128 * self.scale)))
            fallback.fill((0, 150, 0))
            return fallback
    
    def draw_health_bar(self, screen, camera_x):
        """Draw health bar above zombie"""
        if self.is_dead or self.health <= 0:
            return
        
        # Health bar position
        bar_width = 60
        bar_height = 6
        bar_x = self.world_x - camera_x + (int(128 * self.scale) - bar_width) // 2
        bar_y = self.world_y - 20
        
        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Health color based on zombie type
        if self.zombie_type == "Zombie_1":
            health_color = (0, 255, 0)  # Verde para Zombie_1
        elif self.zombie_type == "Zombie_2":
            health_color = (0, 255, 255)  # Ciano para Zombie_2
        else:
            health_color = (0, 255, 0)  # Verde padrão
        
        health_percentage = self.health / self.max_health
        health_width = int(bar_width * health_percentage)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Tipo do zumbi - pequeno texto acima da barra de vida
        if hasattr(pygame, 'font') and pygame.font.get_init():
            font = pygame.font.SysFont("Arial", 10)
            type_text = self.zombie_type.replace("Zombie_", "Z")  # Z1, Z2, etc.
            text_surface = font.render(type_text, True, (255, 255, 255))
            text_x = bar_x + (bar_width - text_surface.get_width()) // 2
            text_y = bar_y - 12
            screen.blit(text_surface, (text_x, text_y))

class ZombieSpawner:
    def __init__(self):
        self.zombies = []
        self.spawn_points = []
        self.last_spawn_x = 0
        self.spawn_distance = 800  # Distance between spawn points
        self.zombie_types = ["Zombie_1", "Zombie_2"]  # Tipos disponíveis de zumbis
        
    def update(self, player, dt):
        # Check if we need to spawn more zombies
        player_progress = player.world_x
        
        # Create spawn points ahead of player
        while self.last_spawn_x < player_progress + 2000:  # Keep spawns 2000 units ahead
            self.last_spawn_x += self.spawn_distance
            # Random Y position within bounds - same as player limits
            spawn_y = 380 + (500 - 380) * (hash(self.last_spawn_x) % 100) / 100
            self.spawn_points.append((self.last_spawn_x, spawn_y))
        
        # Spawn zombies from spawn points that are close to player
        for spawn_point in self.spawn_points[:]:
            spawn_x, spawn_y = spawn_point
            if abs(spawn_x - player_progress) < 1000 and spawn_x > player_progress - 500:
                # Check if there's already a zombie near this spawn point
                zombie_exists = any(abs(zombie.world_x - spawn_x) < 100 for zombie in self.zombies)
                if not zombie_exists:
                    # Escolher tipo de zumbi aleatoriamente
                    import random
                    zombie_type = random.choice(self.zombie_types)
                    new_zombie = Zombie(spawn_x, spawn_y, zombie_type)
                    self.zombies.append(new_zombie)
                    self.spawn_points.remove(spawn_point)
                    print(f"Spawned {zombie_type} at position ({spawn_x}, {spawn_y})")
          # Update all zombies
        for zombie in self.zombies[:]:
            zombie.update(dt, player)
            
            # Remove zombies that are too far behind player (but keep dead bodies visible)
            if zombie.world_x < player_progress - 2000:  # Increased distance for dead bodies
                # Only remove if very far away or if it's been dead for a long time
                if zombie.is_dead:
                    zombie.death_timer = getattr(zombie, 'death_timer', 0) + dt
                    if zombie.death_timer > 10000:  # 10 seconds after death before removal
                        self.zombies.remove(zombie)
                else:
                    self.zombies.remove(zombie)
    def draw(self, screen, camera_x):
        for zombie in self.zombies:
            zombie_screen_x = zombie.world_x - camera_x
            zombie_screen_y = zombie.world_y

            if -200 < zombie_screen_x < WINDOW_WIDTH + 200:
                zombie_image = zombie.get_image()
                screen.blit(zombie_image, (zombie_screen_x, zombie_screen_y))
                zombie.draw_health_bar(screen, camera_x)
                
    def check_player_attacks(self, player):
        """Check if player attacks hit any zombies"""
        is_attacking = False
        attack_range = 120
        attack_width = 80
        attack_height = 100
        attack_type = ""
        if player.current_state in ["attack_1", "attack_2"] and player.animation_timer < 1000:  # Janela maior para melee
            is_attacking = True
            attack_type = player.current_state
            # Adjust range for melee attacks
            if player.current_state == "attack_2":  # Coronhada
                attack_range = 90
                attack_width = 80
            else:  # attack_1 
                attack_range = 100
                attack_width = 90
            print(f"Melee attack detected: {attack_type}, Timer: {player.animation_timer}")
            
        # Check for shot attacks (left mouse button)  
        elif player.current_state == "shot" and player.animation_timer < 800:  # Janela maior para shot
            is_attacking = True
            attack_type = "shot"
            # Increase range for shot attacks
            attack_range = 250
            attack_width = 150
            print(f"Shot attack detected, Timer: {player.animation_timer}")
            
        if is_attacking:
            # Create attack hitbox in front of player - IMPROVED positioning
            if player.facing_right:
                attack_x = player.world_x + 80  # Position attack closer to player
            else:
                attack_x = player.world_x - attack_range - 20  # Position attack in front when facing left
              # Improved Y positioning to better match zombie height
            if attack_type in ["attack_1", "attack_2"]:  # Melee attacks
                # Melee attacks need better vertical coverage to match zombie hitbox
                attack_y = player.world_y + 100  # Adjust to match zombie melee hitbox position
                attack_height = 180  # Increase height for better coverage
                attack_width = max(attack_width, 140)  # Ensure minimum width for melee
            else:  # Shot attacks
                attack_y = player.world_y + 60  # Keep shot positioning
                
            attack_rect = pygame.Rect(attack_x, attack_y, attack_width, attack_height)
            hit_count = 0
            for zombie in self.zombies:
                if not zombie.is_dead:                    # Use appropriate hitbox based on attack type
                    if attack_type in ["attack_1", "attack_2"]:  # Melee attacks use smaller hitbox
                        target_hitbox = zombie.melee_rect
                        hitbox_type = "melee"
                    else:  # Ranged attacks (shot) use larger hitbox
                        target_hitbox = zombie.ranged_rect
                        hitbox_type = "ranged"
                    
                    if attack_rect.colliderect(target_hitbox):
                        # Prevent multiple hits during same animation - mais permissivo
                        hit_frame_id = f"{player.current_state}_{player.animation_timer // 300}"  # Frame windows maiores
                        if not hasattr(zombie, 'last_hit_frame') or zombie.last_hit_frame != hit_frame_id:
                            zombie.last_hit_frame = hit_frame_id
                              # Determine damage based on attack type
                            if attack_type == "shot":
                                damage = 30
                            elif attack_type == "attack_1":
                                damage = 10  
                            elif attack_type == "attack_2":
                                damage = 10 
                            else:
                                damage = 0
                            
                            print(f"HIT! {attack_type} hit zombie {hitbox_type} hitbox for {damage} damage!")
                            zombie_died = zombie.take_damage(damage)
                            hit_count += 1
                            
                            # Apply knockback ONLY for melee attacks (attack_1 and attack_2)
                            if attack_type in ["attack_1", "attack_2"]:
                                knockback_force = 100 if attack_type == "attack_1" else 150  # Mais knockback para attack_2
                                
                                # Push zombie away from player
                                if player.facing_right:
                                    zombie.world_x += knockback_force
                                    print(f"Zombie knocked to the right by {knockback_force} pixels")
                                else:
                                    zombie.world_x -= knockback_force
                                    print(f"Zombie knocked to the left by {knockback_force} pixels")
                                
                                # Special effect for attack_2 - additional upward knockback
                                if attack_type == "attack_2":
                                    zombie.world_y -= 20  # Upward movement for attack_2
                                    print(f"Attack_2 special effect! Zombie knocked upward!")
                            
                            # Shot attacks não causam knockback, apenas dano
                            if attack_type == "shot":
                                print(f"Shot hit - no knockback applied")
            
            if hit_count > 0:
                print(f"Total zombies hit: {hit_count}")
            else:
                print(f"Attack {attack_type} detected but no zombies hit")                # Debug: Print positions
                print(f"Player pos: {player.world_x}, {player.world_y}")
                print(f"Attack rect: {attack_rect}")
                for zombie in self.zombies:
                    if not zombie.is_dead:
                        distance = abs(zombie.world_x - player.world_x)
                        print(f"Zombie pos: {zombie.world_x}, {zombie.world_y}")
                        print(f"  Melee rect: {zombie.melee_rect}, distance: {distance}")
                        print(f"  Ranged rect: {zombie.ranged_rect}")

def game(selected_character="Raider_1"):
    clock = pygame.time.Clock()
    running = True
    
    game_layers = []
    game_speeds = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    GAME_BG_DIR = os.path.join(IMAGES_DIR, "Postapocalypce4", "Pale")
    game_layer_files = ["bg.png", "rail&wall.png", "train.png", "columns&floor.png", "infopost&wires.png", "wires.png"]
    
    for filename in game_layer_files:
        path = os.path.join(GAME_BG_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
            game_layers.append(img)
    
    game_background = Background(game_layers, game_speeds)
    # Corrigir posição inicial do player para estar dentro dos limites (380-500)
    player = Player(100, 450, selected_character)
    zombie_spawner = ZombieSpawner()
    
    while running:
        dt = clock.tick(60)
        events = pygame.event.get()
        
        for event in events:
            if event.type == QUIT:
                return "exit"
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "menu"
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        player.update(keys, dt, mouse_buttons, events)
        
        zombie_spawner.update(player, dt)
        
        zombie_spawner.check_player_attacks(player)
        
        camera_x = max(0, player.world_x - WINDOW_WIDTH // 2)
        game_background.update(dt, camera_x)
    
        screen.fill((0, 0, 0))
        game_background.draw(screen)
          # Draw zombies
        zombie_spawner.draw(screen, camera_x)
          # Draw debug hitboxes (optional - remove later)
        if True:  # Set to False to disable debug
            for zombie in zombie_spawner.zombies:
                if not zombie.is_dead:
                    # Draw melee hitbox in red
                    melee_rect_screen = pygame.Rect(
                        zombie.melee_rect.x - camera_x, 
                        zombie.melee_rect.y, 
                        zombie.melee_rect.width, 
                        zombie.melee_rect.height
                    )
                    pygame.draw.rect(screen, (255, 0, 0), melee_rect_screen, 2)  # Red for melee hitbox
                    
                    # Draw ranged hitbox in blue
                    ranged_rect_screen = pygame.Rect(
                        zombie.ranged_rect.x - camera_x, 
                        zombie.ranged_rect.y, 
                        zombie.ranged_rect.width, 
                        zombie.ranged_rect.height
                    )
                    pygame.draw.rect(screen, (0, 0, 255), ranged_rect_screen, 2)  # Blue for ranged hitbox
        
        player_screen_x = player.world_x - camera_x
        player_screen_y = player.world_y
        
        # Aplicar offset visual durante a animação de shot
        if player.current_state == "shot":
            shot_offset = 70  # Pixels para frente durante o tiro
            if player.facing_right:
                player_screen_x += shot_offset  # Move sprite para a direita
            else:
                player_screen_x -= shot_offset  # Move sprite para a esquerda
        
        player_image = player.get_image()
        
        # Update hitbox position - center it on the character
        hitbox_offset_x = (int(128 * player.scale) - player.rect.width) // 2
        hitbox_offset_y = int(128 * player.scale) - player.rect.height - 20  # 20 pixels from bottom
        
        player.rect.x = player.world_x + hitbox_offset_x
        player.rect.y = player.world_y + hitbox_offset_y
          # Draw player (removed red debug rectangle)
        screen.blit(player_image, (player_screen_x, player_screen_y))
        
        # Draw player health bar and ammo counter
        player.draw_health_bar(screen)
        player.draw_ammo_counter(screen)
        
        font = pygame.font.SysFont("Arial", 18)
        ui_info = [
            f"Position: {int(player.world_x)}, {int(player.world_y)}",
            f"State: {player.current_state}",
            f"Facing: {'Right' if player.facing_right else 'Left'}",
            f"Attack Combo: {player.attack_combo}",
            f"Zombies: {len(zombie_spawner.zombies)}",
            f"Jumping: {player.is_jumping}",
            f"Health: {player.health}/{player.max_health}",
            f"Invulnerable: {player.invulnerability_timer > 0}"
        ]
        for i, info in enumerate(ui_info):
            text = font.render(info, True, (255, 255, 255))
            screen.blit(text, (10, 80 + i * 20))
        
        instructions = [
            "WASD - Move, SHIFT - Run",
            "Right Click - Attack, Left Click - Shoot",
            "SPACE - Jump, R - Reload",
            "ESC - Back to Menu"
        ]
        instruction_font = pygame.font.SysFont("Arial", 16)
        for i, instruction in enumerate(instructions):
            inst_text = instruction_font.render(instruction, True, (255, 255, 255))
            screen.blit(inst_text, (10, 240 + i * 20))
        
        # Check if player died
        if player.is_dead:
            death_font = pygame.font.SysFont("Impact", 80)
            death_text = death_font.render("GAME OVER", True, (255, 0, 0))
            death_rect = death_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            screen.blit(death_text, death_rect)
            restart_font = pygame.font.SysFont("Arial", 24)
            restart_text = restart_font.render("Press ESC to return to menu", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
            screen.blit(restart_text, restart_rect)
        
        # Draw screen flash effect when player takes damage
        player.draw_screen_flash(screen)
        
        pygame.display.flip()

def menu():
    clock = pygame.time.Clock()
    running = True
    
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
    
    title_font = pygame.font.SysFont("Impact", 80)
    option_font = pygame.font.SysFont("Impact", 50)
    
    selected_option = 0
    options = ["New Game", "Exit"]

    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return "exit"
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == K_RETURN:
                    if selected_option == 0:  
                        return "game"
                    elif selected_option == 1:  
                        return "exit"
                elif event.key == K_ESCAPE:
                    return "exit"

        menu_background.update(dt, pygame.time.get_ticks() * 0.05)
        
        screen.fill((0, 0, 0))
        menu_background.draw(screen)
        
        title_text = "SURVIVE IF YOU CAN"
        title_y = 200
        
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:
                    border_text = title_font.render(title_text, True, (0, 0, 0))
                    screen.blit(border_text, (WINDOW_WIDTH // 2 - border_text.get_width() // 2 + dx, title_y + dy))
        
        main_title = title_font.render(title_text, True, (255, 255, 255))
        screen.blit(main_title, (WINDOW_WIDTH // 2 - main_title.get_width() // 2, title_y))
        
        # Menu options positioned lower and with red selection color
        for i, option in enumerate(options):
            color = (255, 0, 0) if i == selected_option else (150, 150, 150)
            option_text = option_font.render(option, True, color)
            screen.blit(option_text, (WINDOW_WIDTH // 2 - option_text.get_width() // 2, 450 + i * 80))
        
        instruction_font = pygame.font.SysFont("Arial", 24)
        instructions = "Use UP/DOWN arrows to navigate, ENTER to select, ESC to exit"
        inst_text = instruction_font.render(instructions, True, (200, 200, 200))
        screen.blit(inst_text, (WINDOW_WIDTH // 2 - inst_text.get_width() // 2, WINDOW_HEIGHT - 100))
        
        pygame.display.flip()

if __name__ == "__main__":
    current_state = "menu"
    
    while True:
        if current_state == "menu":
            current_state = menu()
        elif current_state == "game":
            current_state = game("Raider_1")
        elif current_state == "exit":
            break
    
    pygame.quit()