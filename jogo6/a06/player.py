import os
import pygame
import time
from pygame.locals import *
from animated_sprite import AnimatedSprite

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
        self.gravity = 1200  # Aumentado para pulo mais realista
        self.jump_strength = -400  # Força de pulo ajustada
        self.ground_y = y  # Posição do chão
        self.on_ground = True  # Se está no chão
        self.horizontal_velocity = 0
        self.was_moving_when_jumped = False
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
        self.stamina_regen_rate = 20  
        self.run_stamina_cost = 35  
        
        # Movement tracking for zombie AI
        self.last_movement = 0
        
        self.zombie_attacks_received = {} 
    
        # Setup paths
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
        raider_dir = os.path.join(IMAGES_DIR, character)
        
        try:
            idle_path = os.path.join(raider_dir, "Idle.png")
            
            idle_sheet = pygame.image.load(idle_path).convert_alpha()
            self.animations = {
                "idle": AnimatedSprite(idle_path, 128, 128, 6, 200),
                "walk": AnimatedSprite(os.path.join(raider_dir, "Walk.png"), 128, 128, 8, 100),
                "run": AnimatedSprite(os.path.join(raider_dir, "Run.png"), 128, 128, 8, 80),
                "attack_1": AnimatedSprite(os.path.join(raider_dir, "Attack_1.png"), 128, 128, 6, 120),  
                "attack_2": AnimatedSprite(os.path.join(raider_dir, "Attack_2.png"), 128, 128, 3, 120),  
                "shot": AnimatedSprite(os.path.join(raider_dir, "Shot.png"), 128, 128, 12, 80),  
                "jump": AnimatedSprite(os.path.join(raider_dir, "Jump.png"), 128, 128, 11, 100),  
                "recharge": AnimatedSprite(os.path.join(raider_dir, "Recharge.png"), 128, 128, 12, 100),
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
        current_time = time.time() * 1000
        if not hasattr(self, '_last_cleanup_time'):
            self._last_cleanup_time = current_time
        
        if current_time - self._last_cleanup_time > 5000:  
            old_attacks = [zombie_id for zombie_id, attack_time in self.zombie_attacks_received.items() 
                          if current_time - attack_time > 10000]
            for zombie_id in old_attacks:
                del self.zombie_attacks_received[zombie_id]
            self._last_cleanup_time = current_time
        
        movement = 0
        is_moving = False
        is_running = False
        
        # Verificar se está correndo ANTES de calcular velocidade
        if keys[K_w] or keys[K_UP] or keys[K_s] or keys[K_DOWN] or keys[K_a] or keys[K_LEFT] or keys[K_d] or keys[K_RIGHT]:
            is_moving = True
            # Pode correr se: tem stamina E (stamina > 50% OU já estava correndo)
            can_run = self.current_stamina > 0 and (self.current_stamina > self.max_stamina / 2 or 
                     (hasattr(self, '_was_running') and self._was_running and self.current_stamina > 0))
            
            if (keys[K_LSHIFT] or keys[K_RSHIFT]) and can_run:
                is_running = True
                current_speed = self.run_speed
            else:
                is_running = False
                current_speed = self.speed
        else:
            current_speed = self.speed
            
        # Armazenar estado de corrida para próximo frame
        self._was_running = is_running
            
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
                else:
                    self.current_animation.update(dt)
            return movement
            
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 3 and self.current_state in ["idle", "walk", "run"]:  # Botão direito do mouse
                    if self.attack_combo == 0:
                        self.current_state = "attack_1"
                        self.attack_combo = 1
                    else:
                        self.current_state = "attack_2"
                        self.attack_combo = 0
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
                
                elif event.button == 1 and self.current_state in ["idle", "walk", "run"] and self.current_ammo > 0 and not self.is_reloading:  # Botão esquerdo do mouse
                    self.current_state = "shot"
                    self.current_ammo -= 1
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
            
            if event.type == KEYDOWN:
                if event.key == K_SPACE and self.current_state in ["idle", "walk", "run"] and self.on_ground:
                    self.current_state = "jump"
                    self.is_jumping = True
                    self.on_ground = False
                    self.jump_velocity = self.jump_strength
                    # Preservar movimento horizontal durante o pulo
                    if keys[K_a] or keys[K_LEFT] or keys[K_d] or keys[K_RIGHT]:
                        self.was_moving_when_jumped = True
                    else:
                        self.was_moving_when_jumped = False
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
                
                elif event.key == K_r and self.current_state in ["idle", "walk", "run"]:
                    # Sistema de recarga: transfere da reserva para o pente
                    if self.reserve_ammo > 0 and self.current_ammo < self.max_ammo and not self.is_reloading:
                        self.is_reloading = True
                        self.current_state = "recharge"
                        self.animation_timer = 0
                        self.animation_complete = False
                        self.current_animation.reset()
                    elif self.reserve_ammo == 0:
                        pass  # Sem munição na reserva
                    elif self.is_reloading:
                        # Se estava travado recarregando, resetar e tentar novamente
                        self.is_reloading = False
                    else:
                        pass  # Pente já está cheio
                    
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
                    # Permitir que o jogador complete o pulo naturalmente
                    pass  # A física do pulo será gerenciada separadamente
                elif self.current_state == "recharge":
                    # Finalizar recarga: transferir munição da reserva para o pente
                    ammo_needed = self.max_ammo - self.current_ammo
                    ammo_to_transfer = min(ammo_needed, self.reserve_ammo)
                    self.current_ammo += ammo_to_transfer
                    self.reserve_ammo -= ammo_to_transfer
                    self.is_reloading = False
                elif self.current_state == "hurt":
                    # Após animação de dano, voltar ao estado de idle
                    pass  # Continuará para o estado idle abaixo
                
                # Só mudar para idle se não estiver pulando
                if not self.is_jumping:
                    self.current_state = "idle"
                    self.animation_complete = True
                    self.animation_timer = 0
        
        # FÍSICA MELHORADA DO PULO
        if self.is_jumping:
            # Aplicar gravidade
            self.jump_velocity += self.gravity * dt / 1000
            
            # Atualizar posição Y
            old_y = self.world_y
            self.world_y += self.jump_velocity * dt / 1000
            
            # Verificar se aterrissou
            if self.world_y >= self.ground_y:
                self.world_y = self.ground_y
                self.is_jumping = False
                self.on_ground = True
                self.jump_velocity = 0
                
                # Se a animação de pulo terminou, voltar ao estado apropriado
                if self.current_state == "jump":
                    # Verificar se está se movendo para definir o próximo estado
                    is_currently_moving = (keys[K_a] or keys[K_LEFT] or 
                                         keys[K_d] or keys[K_RIGHT] or 
                                         keys[K_w] or keys[K_UP] or 
                                         keys[K_s] or keys[K_DOWN])
                    
                    if is_currently_moving:
                        # Verificar se está correndo
                        can_run = self.current_stamina > 0 and (self.current_stamina > self.max_stamina / 2 or 
                                 (hasattr(self, '_was_running') and self._was_running and self.current_stamina > 0))
                        
                        if (keys[K_LSHIFT] or keys[K_RSHIFT]) and can_run:
                            self.current_state = "run"
                        else:
                            self.current_state = "walk"
                    else:
                        self.current_state = "idle"
                    
                    self.animation_timer = 0
                    self.animation_complete = True
        
        # Gerenciar stamina - mover antes do movimento para sincronizar
        if is_running and is_moving and self.current_stamina > 0:
            # Consumir stamina ao correr
            self.current_stamina = max(0, self.current_stamina - self.run_stamina_cost * dt / 1000)
        elif not is_running or not is_moving:
            # Regenerar stamina quando não está correndo
            self.current_stamina = min(self.max_stamina, self.current_stamina + self.stamina_regen_rate * dt / 1000)
        
        # Handle movement - permitir movimento horizontal mesmo durante pulo
        horizontal_movement = 0
        if self.current_state in ["idle", "walk", "run"] or self.is_jumping:
            if keys[K_a] or keys[K_LEFT]:
                # Impedir movimento para a esquerda se já estiver no limite
                if self.world_x > 0:
                    horizontal_movement -= current_speed * dt / 1000
                    self.facing_right = False
                    is_moving = True
                
            if keys[K_d] or keys[K_RIGHT]:
                horizontal_movement += current_speed * dt / 1000
                self.facing_right = True
                is_moving = True
                
            # Movimento vertical apenas quando não está pulando
            if not self.is_jumping:
                if keys[K_w] or keys[K_UP]:
                    self.world_y -= current_speed * dt / 1000
                    is_moving = True
                    
                if keys[K_s] or keys[K_DOWN]:
                    self.world_y += current_speed * dt / 1000
                    is_moving = True
            
            # Aplicar movimento horizontal
            self.world_x += horizontal_movement
            movement = horizontal_movement
            
            # Garantir que o player não saia da borda esquerda
            if self.world_x < 0:
                self.world_x = 0
                movement = 0  # Cancelar movimento para a esquerda
            
            # Rastrear movimento para IA dos zumbis
            self.last_movement = movement
            
            # Definir estados de animação apenas se não estiver pulando
            if not self.is_jumping and self.current_state in ["idle", "walk", "run"]:
                if is_moving:
                    if is_running:
                        self.current_state = "run"
                    else:
                        self.current_state = "walk"
                else:
                    self.current_state = "idle"       
        self.world_x = max(0, self.world_x)
        
        # Ajustar ground_y baseado na posição atual quando não está pulando
        if not self.is_jumping:
            self.ground_y = max(200, min(self.world_y, 400))
            self.world_y = self.ground_y
        else:
            # Durante o pulo, manter limites para não sair da área de jogo
            self.world_y = max(50, min(self.world_y, 400))

        if self.is_reloading and self.current_state != "recharge":
            self.is_reloading = False

        self.current_animation = self.animations[self.current_state]
        self.current_animation.update(dt)
        return movement
        
    def take_damage(self, damage, zombie_id=None):
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
            self.death_animation_complete = False
            self.current_animation = self.animations[self.current_state]  
            self.current_animation.reset()
            return True
        else:
            # Ativar animação de dano se não estiver morto
            if self.current_state not in ["dead", "hurt"]:
                # Se estava recarregando quando tomou dano, resetar o estado de recarga
                if self.current_state == "recharge":
                    self.is_reloading = False
                
                self.current_state = "hurt"
                self.animation_timer = 0
                self.animation_complete = False
                self.current_animation.reset()
            
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
            fallback = pygame.Surface((int(128 * self.scale), int(128 * self.scale)))
            fallback.fill((255, 0, 255))  
            return fallback
    
    def draw_health_bar(self, screen):
        window_height = screen.get_height()
        
        bar_width = 20  
        bar_height = 200  
        bar_x = 20  
        bar_y = window_height - bar_height - 60  
        
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        health_percentage = self.health / self.max_health
        current_health_height = int(bar_height * health_percentage)
        health_y = bar_y + (bar_height - current_health_height)  
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, health_y, bar_width, current_health_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
    def draw_stamina_bar(self, screen):
        """Desenhar barra de stamina vertical ao lado da barra de vida"""
        window_height = screen.get_height()
        
        bar_width = 20  
        bar_height = 200  
        bar_x = 50  
        bar_y = window_height - bar_height - 60  
        
        pygame.draw.rect(screen, (0, 0, 100), (bar_x, bar_y, bar_width, bar_height))
    
        stamina_percentage = self.current_stamina / self.max_stamina
        current_stamina_height = int(bar_height * stamina_percentage)
        stamina_y = bar_y + (bar_height - current_stamina_height)  
        
        can_start_running = self.current_stamina > self.max_stamina / 2
        if can_start_running:
            stamina_color = (0, 150, 255)  # Azul claro (pode começar a correr)
        else:
            stamina_color = (255, 165, 0)  # Laranja (recuperando - não pode começar a correr)
            
        pygame.draw.rect(screen, stamina_color, (bar_x, stamina_y, bar_width, current_stamina_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
    def draw_ammo_counter(self, screen):
        """Desenhar contador de munição em texto ao lado das barras"""
        window_height = screen.get_height()
        
        text_x = 100  
        text_y = window_height - 140 
        
        # Fonte maior para o contador
        font = pygame.font.SysFont("Arial", 32)  
        ammo_text = f"{self.current_ammo}/{self.reserve_ammo}"
        
        if self.is_reloading:
            color = (255, 165, 0)  # Laranja enquanto estiver carregando
        elif self.current_ammo == 0:
            color = (255, 0, 0)    # Vermelho se estiver sem munição
        else:
            color = (255, 255, 255)  
        
        text_surface = font.render(ammo_text, True, color)
        
        # Centralizar o texto na posição
        text_rect_x = text_x - text_surface.get_width() // 2
        
        screen.blit(text_surface, (text_rect_x, text_y))

    def draw_screen_flash(self, screen):
        if self.screen_flash_timer > 0:
            # Create a red overlay that covers the entire screen
            window_width = screen.get_width()
            window_height = screen.get_height()
            flash_alpha = int(150 * (self.screen_flash_timer / self.screen_flash_duration))
            flash_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
            flash_surface.fill((255, 0, 0, flash_alpha))
            screen.blit(flash_surface, (0, 0))

    def get_current_spawn_rate(self):
        """Get current spawn rate based on score - mais agressivo a cada 100 pontos"""
        # Reduzir spawn rate mais drasticamente a cada 100 pontos
        points_per_level = 100
        current_level = self.score // points_per_level
        
        # Redução mais agressiva: 100ms por nível (cada 100 pontos)
        rate_decrease_per_level = 100
        current_rate = self.base_spawn_rate - (current_level * rate_decrease_per_level)
        
        return max(current_rate, self.min_spawn_rate)

    def draw_score_and_record(self, screen):
        """Draw score, high score, and record message"""
        font = pygame.font.SysFont("Arial", 24)
        
        # Draw current score
        score_text = f"Score: {self.score}"
        score_surface = font.render(score_text, True, (255, 255, 255))
        screen.blit(score_surface, (10, 10))
        
        # Draw high score
        high_score_text = f"High Score: {self.high_score}"
        high_score_surface = font.render(high_score_text, True, (255, 255, 0))
        screen.blit(high_score_surface, (10, 40))
        
        # Draw spawn level indicator - mostrar nível de dificuldade baseado em pontuação
        difficulty_level = self.score // 100
        level_text = f"Difficulty Level: {difficulty_level}"
        level_surface = font.render(level_text, True, (0, 255, 255))
        screen.blit(level_surface, (10, 70))
        
        # Mostrar número atual de zumbis (informativo)
        zombie_info_text = f"Zombie Target: {min(30, 3 + difficulty_level)}"
        zombie_info_surface = font.render(zombie_info_text, True, (255, 165, 0))
        screen.blit(zombie_info_surface, (10, 100))
        
        # Draw record broken message during gameplay
        if self.record_message_timer > 0:
            big_font = pygame.font.SysFont("Arial", 48, bold=True)
            record_text = "NEW RECORD!"
            record_surface = big_font.render(record_text, True, (255, 215, 0))  # Gold color
            
            # Center the message on screen
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            text_rect = record_surface.get_rect()
            text_rect.center = (screen_width // 2, screen_height // 3)
            
            # Add a background for better visibility
            background_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(screen, (0, 0, 0, 180), background_rect)
            pygame.draw.rect(screen, (255, 215, 0), background_rect, 3)
            
            screen.blit(record_surface, text_rect)
