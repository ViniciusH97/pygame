import os
import pygame
import time
from pygame.locals import *
from animated_sprite import AnimatedSprite
from language_manager import language_manager

class Player:
    def __init__(self, x, y, character="Raider_1"):
        self.world_x = x
        self.world_y = y
        self.speed = 200
        self.run_speed = 400
        self.scale = 4
        hitbox_width = int(128 * self.scale * 0.2)
        hitbox_height = int(128 * self.scale * 0.4)
        self.rect = pygame.Rect(x, y, hitbox_width, hitbox_height)
        self.facing_right = True
        self.attack_combo = 0 
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
        self.invulnerability_duration = 1000  
        self.screen_flash_timer = 0  
        self.screen_flash_duration = 300  
        
        # Sistema de munição
        self.max_ammo = 5  # Pente máximo
        self.current_ammo = self.max_ammo  # Começa com pente cheio
        self.max_reserve_ammo = 5  # Máximo na reserva
        self.reserve_ammo = self.max_reserve_ammo  # Começa com reserva cheia
        self.is_reloading = False
        
        # Sistema de stamina
        self.max_stamina = 100
        self.current_stamina = self.max_stamina
        self.stamina_regen_rate = 30  # Pontos por segundo
        self.run_stamina_cost = 50  # Pontos por segundo ao correr
        
        # Movement tracking for zombie AI
        self.last_movement = 0
        
        # Sistema para rastrear ataques de múltiplos zumbis
        self.zombie_attacks_received = {}  # {zombie_id: last_attack_time}
    
        # Setup paths
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
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
                "attack_1": AnimatedSprite(os.path.join(raider_dir, "Attack_1.png"), 128, 128, 6, 120),  
                "attack_2": AnimatedSprite(os.path.join(raider_dir, "Attack_2.png"), 128, 128, 3, 120),  
                "shot": AnimatedSprite(os.path.join(raider_dir, "Shot.png"), 128, 128, 12, 80),  
                "jump": AnimatedSprite(os.path.join(raider_dir, "Jump.png"), 128, 128, 11, 100),  
                "recharge": AnimatedSprite(os.path.join(raider_dir, "Recharge.png"), 128, 128, 12, 150),  
                "dead": AnimatedSprite(os.path.join(raider_dir, "Dead.png"), 128, 128, 4, 200),  
                "hurt": AnimatedSprite(os.path.join(raider_dir, "Hurt.png"), 128, 128, 2, 150),  
            }
            
            fallback_surface = pygame.Surface((128, 128), pygame.SRCALPHA)
            fallback_surface.fill((0, 255, 0)) 
            
            fallback_anim = AnimatedSprite.__new__(AnimatedSprite)
            fallback_anim.frames = [fallback_surface]
            fallback_anim.current_frame = 0
            fallback_anim.frame_timer = 0            
            fallback_anim.frame_count = 1
            fallback_anim.frame_duration = 200
            
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
        # Limpeza periódica de ataques antigos (a cada 5 segundos)
        current_time = time.time() * 1000
        if not hasattr(self, '_last_cleanup_time'):
            self._last_cleanup_time = current_time
        
        if current_time - self._last_cleanup_time > 5000:  # 5 segundos
            # Remover ataques antigos (mais de 10 segundos)
            old_attacks = [zombie_id for zombie_id, attack_time in self.zombie_attacks_received.items() 
                          if current_time - attack_time > 10000]
            for zombie_id in old_attacks:
                del self.zombie_attacks_received[zombie_id]
            self._last_cleanup_time = current_time
        
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
                    print(f"{language_manager.get_text('shot_fired')}: {self.current_ammo}/{self.max_ammo}")
            
            if event.type == KEYDOWN:
                if event.key == K_SPACE and self.current_state in ["idle", "walk", "run"] and not self.is_jumping:
                    self.current_state = "jump"
                    self.is_jumping = True
                    self.jump_start_y = self.world_y
                    self.jump_velocity = self.jump_strength
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
                
                elif event.key == K_r and self.current_state in ["idle", "walk", "run"] and not self.is_reloading:
                    # Sistema de recarga: transfere da reserva para o pente
                    if self.reserve_ammo > 0 and self.current_ammo < self.max_ammo:
                        self.is_reloading = True
                        self.current_state = "recharge"
                        self.animation_timer = 0
                        self.animation_complete = False
                        self.current_animation.reset()
                        print(f"{language_manager.get_text('reloading')}: {self.current_ammo}/{self.max_ammo}, {language_manager.get_text('reserve_ammo')}: {self.reserve_ammo}")
                    elif self.reserve_ammo == 0:
                        print(language_manager.get_text("no_reserve_ammo"))
                    else:
                        print(language_manager.get_text("magazine_full"))
                    
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
                    # Finalizar recarga: transferir munição da reserva para o pente
                    ammo_needed = self.max_ammo - self.current_ammo
                    ammo_to_transfer = min(ammo_needed, self.reserve_ammo)
                    self.current_ammo += ammo_to_transfer
                    self.reserve_ammo -= ammo_to_transfer
                    self.is_reloading = False
                    print(f"{language_manager.get_text('reload_complete')}! {language_manager.get_text('magazine')}: {self.current_ammo}/{self.max_ammo}, {language_manager.get_text('reserve_ammo')}: {self.reserve_ammo}")
                elif self.current_state == "hurt":
                    # Após animação de dano, voltar ao estado de idle
                    pass  # Continuará para o estado idle abaixo
                self.current_state = "idle"
                self.animation_complete = True
                self.animation_timer = 0
        
        # física do pulo do player 
        if self.is_jumping:
            self.jump_velocity += self.gravity * dt / 1000
            self.world_y += self.jump_velocity * dt / 1000
            
            # após o pulo ser realizado o personagem volta para a mesma posição
            if self.world_y >= self.jump_start_y:
                self.world_y = self.jump_start_y
                self.is_jumping = False
                if self.current_state == "jump":
                    self.current_state = "idle"
        
        # Gerenciar stamina
        if is_running and is_moving and self.current_stamina > 0:
            # Consumir stamina ao correr
            self.current_stamina = max(0, self.current_stamina - self.run_stamina_cost * dt / 1000)
        elif not is_running or not is_moving:
            # Regenerar stamina quando não está correndo
            self.current_stamina = min(self.max_stamina, self.current_stamina + self.stamina_regen_rate * dt / 1000)
        
        # Handle movement only if not performing actions
        if self.current_state in ["idle", "walk", "run"]:
            # Check if SHIFT is pressed for running and has stamina
            if (keys[K_LSHIFT] or keys[K_RSHIFT]) and self.current_stamina > 0:
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
            
            # Rastrear movimento para IA dos zumbis
            self.last_movement = movement
            
            if is_moving:
                if is_running:
                    self.current_state = "run"
                else:
                    self.current_state = "walk"
            else:
                self.current_state = "idle"       
        self.world_x = max(0, self.world_x)
        self.world_y = max(328, min(self.world_y, 550))

        self.current_animation = self.animations[self.current_state]
        self.current_animation.update(dt)
        return movement
        
    def take_damage(self, damage, zombie_id=None):
        """Fazer o jogador receber dano - modificado para permitir dano de múltiplos zumbis"""
        if self.is_dead:
            return False
        
        # Se zombie_id for fornecido, verificar se este zumbi específico pode causar dano
        if zombie_id is not None:
            current_time = time.time() * 1000
            
            # Verificar se este zumbi específico atacou recentemente
            if (zombie_id in self.zombie_attacks_received and 
                current_time - self.zombie_attacks_received[zombie_id] < 300):  # 300ms por zumbi - reduzido de 500ms
                return False
            
            # Registrar o ataque deste zumbi
            self.zombie_attacks_received[zombie_id] = current_time
        else:
            # Sistema antigo de invulnerabilidade para outros tipos de dano
            if self.invulnerability_timer > 0:
                return False
            
            self.invulnerability_timer = self.invulnerability_duration
        
        self.health -= damage
        self.screen_flash_timer = self.screen_flash_duration  
        
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
            
            zombie_info = f" (Zombie {zombie_id})" if zombie_id else ""
            print(f"Jogador recebeu {damage} de dano{zombie_info}! Vida: {self.health}/{self.max_health}")
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
        
    def draw_stamina_bar(self, screen):
        """Desenhar barra de stamina abaixo da vida"""
        bar_width = 200
        bar_height = 15
        bar_x = 20
        bar_y = 50  # Abaixo da barra de vida
        
        # Background (azul escuro)
        pygame.draw.rect(screen, (0, 0, 100), (bar_x, bar_y, bar_width, bar_height))
        
        # Stamina (azul claro)
        stamina_percentage = self.current_stamina / self.max_stamina
        stamina_width = int(bar_width * stamina_percentage)
        pygame.draw.rect(screen, (0, 150, 255), (bar_x, bar_y, stamina_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Stamina text
        font = pygame.font.SysFont("Arial", 14)
        stamina_text = f"STAMINA: {int(self.current_stamina)}"
        text_surface = font.render(stamina_text, True, (255, 255, 255))
        screen.blit(text_surface, (bar_x + bar_width + 10, bar_y + 1))
        
    def draw_ammo_counter(self, screen):
        """Desenhar contador de munição no canto superior direito com fonte de pixel"""
        window_width = screen.get_width()
        
        # Usar fonte de pixel (monospace)
        try:
            font = pygame.font.Font(None, 36)  # Fonte padrão do sistema em tamanho pixel
        except:
            font = pygame.font.SysFont("Courier", 24)  # Fallback para fonte monospace
        
        ammo_text = f"AMMO: {self.current_ammo}/{self.reserve_ammo}"
        
        if self.is_reloading:
            color = (255, 165, 0)  # Laranja para recarregando
        elif self.current_ammo == 0:
            color = (255, 0, 0)    # Vermelho para sem munição
        else:
            color = (255, 255, 255)  # Branco normal
        
        text_surface = font.render(ammo_text, True, color)
        
        # Posicionar no canto superior direito
        ammo_x = window_width - text_surface.get_width() - 20
        ammo_y = 20
        
        screen.blit(text_surface, (ammo_x, ammo_y))

    def draw_screen_flash(self, screen):
        if self.screen_flash_timer > 0:
            # Create a red overlay that covers the entire screen
            window_width = screen.get_width()
            window_height = screen.get_height()
            flash_alpha = int(150 * (self.screen_flash_timer / self.screen_flash_duration))
            flash_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
            flash_surface.fill((255, 0, 0, flash_alpha))
            screen.blit(flash_surface, (0, 0))
