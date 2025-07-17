import os
import pygame
import time
from animated_sprite import AnimatedSprite

class Zombie:
    # Contador de IDs para zumbis únicos
    _id_counter = 0
    
    def __init__(self, x, y, zombie_type="Zombie_1"):
        # ID único para cada zumbi
        Zombie._id_counter += 1
        self.zombie_id = Zombie._id_counter
        
        self.world_x = x
        self.world_y = y  # Usar a posição Y fornecida inicialmente
        self.scale = 3.7
        self.speed = 200
        self.max_health = 100
        self.health = self.max_health
        self.facing_right = False
        self.current_state = "idle"
        self.is_dead = False
        self.death_animation_complete = False  
        self.death_timer = 0  # Timer para controlar quando remover o zumbi morto
        self.attack_timer = 0
        self.attack_cooldown = 400  # Reduzir cooldown para ataques mais frequentes
        self.attack_range = 100  # Aumentar alcance de ataque
        self.attack_damage = 20
        self.animation_timer = 0
        self.animation_complete = True
        self.zombie_type = zombie_type 
        
        # Sistema de detecção do player
        self.detection_range = 400 
        self.player_detected = False
        
        # Sistema de perseguição mais realista
        self.target_x = x  # Posição alvo para onde o zumbi está indo
        self.target_y = y  # Posição Y alvo
        self.reaction_timer = 0  # Timer para delay de reação
        self.reaction_delay = 800  # Delay aumentado para ser mais natural
        self.last_player_x = 0  # Última posição conhecida do player
        self.last_player_y = 0 
        self.path_update_timer = 0  # Timer para atualizar o caminho
        self.path_update_interval = 300  # Atualizar caminho a cada 300ms para movimento mais natural 
        
        melee_hitbox_width = int(128 * self.scale * 0.5)
        melee_hitbox_height = int(128 * self.scale * 0.5)
        self.melee_rect = pygame.Rect(x, y, melee_hitbox_width, melee_hitbox_height)
        
        ranged_hitbox_width = int(128 * self.scale * 1.2)  
        ranged_hitbox_height = int(128 * self.scale * 0.7)  
        self.ranged_rect = pygame.Rect(x, y, ranged_hitbox_width, ranged_hitbox_height)
        
        self.rect = self.melee_rect
        
        # define os caminhos das sprites
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
        zombie_dir = os.path.join(IMAGES_DIR, zombie_type)
        
        try:
            if zombie_type == "Zombie_1":
                self.animations = {
                    "idle": AnimatedSprite(os.path.join(zombie_dir, "Idle.png"), 128, 128, 6, 300),
                    "walk": AnimatedSprite(os.path.join(zombie_dir, "Walk.png"), 128, 128, 10, 150),  
                    "attack": AnimatedSprite(os.path.join(zombie_dir, "Attack.png"), 128, 128, 5, 150),  
                    "hurt": AnimatedSprite(os.path.join(zombie_dir, "Hurt.png"), 128, 128, 4, 150),  
                    "dead": AnimatedSprite(os.path.join(zombie_dir, "Dead.png"), 128, 128, 5, 200),  
                }


            elif zombie_type == "Zombie_2":
                self.animations = {
                    "idle": AnimatedSprite(os.path.join(zombie_dir, "Idle.png"), 128, 128, 6, 300),  
                    "walk": AnimatedSprite(os.path.join(zombie_dir, "Walk.png"), 128, 128, 10, 120),  # Reduzido de 200 para 120 (mais rápido)
                    "attack": AnimatedSprite(os.path.join(zombie_dir, "Attack.png"), 128, 128, 5, 150),  
                    "hurt": AnimatedSprite(os.path.join(zombie_dir, "Hurt.png"), 128, 128, 4, 150),  
                    "dead": AnimatedSprite(os.path.join(zombie_dir, "Dead.png"), 128, 128, 5, 200),
                }
                
                self.speed = 500 # Aumentado de 700 para 400 (mais equilibrado)
                self.attack_damage = 25
                self.max_health = 130
                self.health = self.max_health
                self.attack_cooldown = 400  

            elif zombie_type == "Zombie_3":
                self.animations = {
                    "idle": AnimatedSprite(os.path.join(zombie_dir, "Idle.png"), 128, 128, 6, 300),    
                    "walk": AnimatedSprite(os.path.join(zombie_dir, "Walk.png"), 128, 128, 10, 150),   
                    "attack": AnimatedSprite(os.path.join(zombie_dir, "Attack.png"), 128, 128, 4, 150), 
                    "hurt": AnimatedSprite(os.path.join(zombie_dir, "Hurt.png"), 128, 128, 4, 150),    
                    "dead": AnimatedSprite(os.path.join(zombie_dir, "Dead.png"), 128, 128, 5, 200),    
                }
                
                self.speed = 300 # Aumentado significativamente de 300 para 500
                self.attack_damage = 30
                self.max_health = 150
                self.health = self.max_health
                self.attack_range = 100 
                self.attack_cooldown = 450  

            elif zombie_type == "Zombie_4":
                self.animations = {
                    "idle": AnimatedSprite(os.path.join(zombie_dir, "Idle.png"), 128, 128, 7, 300),     
                    "walk": AnimatedSprite(os.path.join(zombie_dir, "Walk.png"), 128, 128, 12, 150),    
                    "attack": AnimatedSprite(os.path.join(zombie_dir, "Attack.png"), 128, 128, 10, 100), 
                    "hurt": AnimatedSprite(os.path.join(zombie_dir, "Hurt.png"), 128, 128, 4, 150),     
                    "dead": AnimatedSprite(os.path.join(zombie_dir, "Dead.png"), 128, 128, 5, 200),     
                }
                
                self.speed = 350 
                self.attack_damage = 40  
                self.max_health = 200  
                self.health = self.max_health
                self.attack_range = 120  
                self.attack_cooldown = 300  

        except Exception as e:
            fallback_surface = pygame.Surface((128, 128))
            fallback_surface.fill((0, 150, 0))  
            
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
            return  
        
        self.attack_timer += dt
        self.reaction_timer += dt
    
        if self.current_state in ["attack", "hurt", "dead"]:
            self.animation_timer += dt
            
            animation_duration = len(self.current_animation.frames) * self.current_animation.frame_duration
            if self.animation_timer >= animation_duration:
                if self.current_state == "dead":
                    self.is_dead = True
                    self.death_animation_complete = True
                    self.death_timer = 0  # Inicializar timer quando animação de morte termina
                    # Manter o último frame da animação de morte
                    self.current_animation.current_frame = len(self.current_animation.frames) - 1
                    return
                elif self.current_state == "hurt":
                    distance = abs(self.world_x - player.world_x)
                    if distance <= self.attack_range + 50:  
                        self.current_state = "idle"
                    else:
                        self.current_state = "walk"
                elif self.current_state == "attack":
                    distance_x = abs(self.world_x - player.world_x)
                    distance_y = abs(self.world_y - player.world_y)
                    # Ataque funciona se estiver perto horizontal E verticalmente
                    if distance_x <= self.attack_range and distance_y <= 40:
                        player.take_damage(self.attack_damage, self.zombie_id)
                    
                    if distance_x <= self.attack_range + 20:
                        self.current_state = "idle"                    
                    else:
                        self.current_state = "walk"
                        self.animation_complete = True
                self.animation_timer = 0
        else:
            distance_x = player.world_x - self.world_x
            distance_y = player.world_y - self.world_y
            total_distance = (distance_x**2 + distance_y**2)**0.5
            
            # Verificar se o player está dentro do alcance de detecção
            if total_distance <= self.detection_range:
                self.player_detected = True
            
            # Comportamento baseado na detecção do player
            if self.player_detected:
                self.path_update_timer += dt
                
                # Atualizar alvo de forma mais natural com delay
                if self.reaction_timer >= self.reaction_delay or self.path_update_timer >= self.path_update_interval:
                    self.target_x = player.world_x
                    self.target_y = player.world_y
                    self.last_player_x = player.world_x
                    self.last_player_y = player.world_y
                    self.reaction_timer = 0  # Resetar timer
                    self.path_update_timer = 0  # Resetar timer de atualização
                
                # Se não temos alvo válido, usar posição atual do player
                if not hasattr(self, 'target_x') or self.target_x == 0:
                    self.target_x = player.world_x
                    self.target_y = player.world_y
                
                # Movimento em direção ao alvo (não diretamente ao player)
                distance_to_target_x = self.target_x - self.world_x
                distance_to_target_y = self.target_y - self.world_y
                distance_to_target = (distance_to_target_x**2 + distance_to_target_y**2)**0.5
                
                # Distância real para o player (para ataque)
                distance_to_player_x = player.world_x - self.world_x
                distance_to_player_y = player.world_y - self.world_y
                distance_horizontal = abs(distance_to_player_x)
                distance_vertical = abs(distance_to_player_y)
                
                # Pode atacar se estiver perto horizontalmente E verticalmente do player real
                can_attack = (distance_horizontal <= self.attack_range and 
                             distance_vertical <= 40 and  # Tolerância maior para altura
                             self.attack_timer >= self.attack_cooldown)
                
                if can_attack:
                    self.current_state = "attack"
                    self.attack_timer = 0
                    self.animation_timer = 0
                    self.animation_complete = False
                    self.current_animation.reset()
                    
                elif distance_to_target > 20:  # Usar distância ao alvo, não ao player
                    self.current_state = "walk"
                    
                    # Movimento mais natural em direção ao alvo
                    if distance_to_target > 10:  # Evitar tremulação quando muito próximo
                        move_x = (distance_to_target_x / distance_to_target) * self.speed * dt / 1000
                        
                        # Movimento Y mais suave
                        y_diff = distance_to_target_y
                        
                        # Mover em Y com velocidade reduzida para movimento mais natural
                        if abs(y_diff) > 15:  # Tolerância maior
                            move_y = (y_diff / abs(y_diff)) * min(self.speed * dt / 1500, abs(y_diff))  # Movimento Y mais lento
                            self.world_y += move_y
                        
                        self.world_x += move_x
                        self.facing_right = move_x > 0
                else:                
                    # Próximo ao alvo mas ainda não atacando
                    self.current_state = "idle"  # Ficar parado quando próximo ao alvo
                    self.facing_right = distance_to_player_x > 0
            else:
                # Player não detectado - patrulhar andando para a esquerda
                self.current_state = "walk"
                self.world_x -= self.speed * dt / 1000  # Usar mesma velocidade base
                self.facing_right = False  # Virar para a esquerda
                
                # Impedir que o zumbi saia do mapa pela esquerda
                self.world_x = max(0, self.world_x)
        
        # Manter zumbis dentro dos limites do mapa com flexibilidade para perseguição
        # Ajustar limites baseados na posição do player para melhor alinhamento
        min_y = max(230, player.world_y - 100)  
        max_y = min(550, player.world_y + 100)  
        self.world_y = max(min_y, min(self.world_y, max_y))
        
        self.current_animation = self.animations[self.current_state]
        if not (self.is_dead and self.death_animation_complete):
            self.current_animation.update(dt)
            
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
            return True  
        else:
            self.current_state = "hurt"
            self.animation_timer = 0
            self.animation_complete = False
            self.current_animation.reset()            
            return False  
    
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
            fallback = pygame.Surface((int(128 * self.scale), int(128 * self.scale)))
            fallback.fill((0, 150, 0))
            return fallback
    
    def draw_health_bar(self, screen, camera_x):
        if self.is_dead or self.health <= 0:
            return
        
        bar_width = 60
        bar_height = 6
        bar_x = self.world_x - camera_x + (int(128 * self.scale) - bar_width) // 2
        bar_y = self.world_y - 20
        
        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Definição de cores para distinguir os tipos de zumbis
        if self.zombie_type == "Zombie_1":
            health_color = (0, 255, 0)  
        elif self.zombie_type == "Zombie_2":
            health_color = (0, 255, 255)  
        elif self.zombie_type == "Zombie_3":
            health_color = (255, 255, 0)  
        elif self.zombie_type == "Zombie_4":
            health_color = (255, 0, 255)  
        else:
            health_color = (0, 255, 0)  
        
        health_percentage = self.health / self.max_health
        health_width = int(bar_width * health_percentage)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

        # Status de vida no zuombie
        if hasattr(pygame, 'font') and pygame.font.get_init():
            font = pygame.font.SysFont("Arial", 10)
            type_text = self.zombie_type.replace("Zombie_", "Z")  
            text_surface = font.render(type_text, True, (255, 255, 255))
            text_x = bar_x + (bar_width - text_surface.get_width()) // 2
            text_y = bar_y - 12
            screen.blit(text_surface, (text_x, text_y))
    
    def _move_directly_to_player(self, distance_x, distance_y, dt):
        # Movimento horizontal
        if abs(distance_x) > 5:
            if distance_x > 0:
                self.world_x += self.speed * dt / 1000
                self.facing_right = True
            else:
                self.world_x -= self.speed * dt / 1000
                self.facing_right = False
        
        # Movimento vertical para seguir o player
        if abs(distance_y) > 5:
            if distance_y > 0:
                self.world_y += self.speed * dt / 1000
            else:
                self.world_y -= self.speed * dt / 1000
