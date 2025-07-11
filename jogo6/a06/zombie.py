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
        self.world_y = max(328, min(y, 550))  # Force spawn within bounds
        self.scale = 3.5
        self.speed = 250  
        self.max_health = 100
        self.health = self.max_health
        self.facing_right = False
        self.current_state = "idle"
        self.is_dead = False
        self.death_animation_complete = False  
        self.death_timer = 0  # Timer para controlar quando remover o zumbi morto
        self.attack_timer = 0
        self.attack_cooldown = 500  
        self.attack_range = 80  
        self.attack_damage = 20
        self.animation_timer = 0
        self.animation_complete = True
        self.zombie_type = zombie_type 
        
        melee_hitbox_width = int(128 * self.scale * 0.5)
        melee_hitbox_height = int(128 * self.scale * 0.5)
        self.melee_rect = pygame.Rect(x, max(328, min(y, 550)), melee_hitbox_width, melee_hitbox_height)
        
        ranged_hitbox_width = int(128 * self.scale * 1.2)  
        ranged_hitbox_height = int(128 * self.scale * 0.7)  
        self.ranged_rect = pygame.Rect(x, max(328, min(y, 550)), ranged_hitbox_width, ranged_hitbox_height)
        
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
                    "walk": AnimatedSprite(os.path.join(zombie_dir, "Walk.png"), 128, 128, 10, 150),  
                    "attack": AnimatedSprite(os.path.join(zombie_dir, "Attack.png"), 128, 128, 5, 150),  
                    "hurt": AnimatedSprite(os.path.join(zombie_dir, "Hurt.png"), 128, 128, 4, 150),  
                    "dead": AnimatedSprite(os.path.join(zombie_dir, "Dead.png"), 128, 128, 5, 200),
                }
                
                self.speed = 550  
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
                
                self.speed = 300  
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
                
                self.speed = 200  
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
                    distance = abs(self.world_x - player.world_x)
                    if distance <= self.attack_range:
                        player.take_damage(self.attack_damage, self.zombie_id)
                    
                    if distance <= self.attack_range:
                        self.current_state = "idle"                    
                    else:
                        self.current_state = "walk"
                        self.animation_complete = True
                self.animation_timer = 0
        else:
            distance_x = player.world_x - self.world_x
            distance_y = player.world_y - self.world_y
            total_distance = (distance_x**2 + distance_y**2)**0.5
            
            if total_distance <= self.attack_range and self.attack_timer >= self.attack_cooldown:
                self.current_state = "attack"
                self.attack_timer = 0
                self.animation_timer = 0
                self.animation_complete = False
                self.current_animation.reset()
                
            elif total_distance > self.attack_range:
                self.current_state = "walk"
                
                player_movement = abs(getattr(player, 'last_movement', 0))
                
                if player_movement > 100: 
                    if player.last_movement > 0: 
                        if self.world_x < player.world_x - 50:
                            prediction_factor = min(300, player_movement * 2)
                            target_x = player.world_x + prediction_factor
                            target_y = player.world_y
                            
                            intercept_x = target_x - self.world_x
                            intercept_y = target_y - self.world_y
                            intercept_distance = (intercept_x**2 + intercept_y**2)**0.5
                            
                            if intercept_distance > 0:
                                speed_multiplier = 1.3
                                move_x = (intercept_x / intercept_distance) * self.speed * speed_multiplier * dt / 1000
                                move_y = (intercept_y / intercept_distance) * self.speed * speed_multiplier * dt / 1000
                                
                                self.world_x += move_x
                                self.world_y += move_y
                                # Ensure zombie stays within map bounds
                                self.world_y = max(328, min(self.world_y, 550))
                                self.facing_right = move_x > 0
                        else:
                            self._move_directly_to_player(distance_x, distance_y, dt)
                    elif player.last_movement < 0:  
                        if self.world_x > player.world_x + 50:
                            prediction_factor = min(300, abs(player_movement) * 2)
                            target_x = player.world_x - prediction_factor
                            target_y = player.world_y
                            
                            intercept_x = target_x - self.world_x
                            intercept_y = target_y - self.world_y
                            intercept_distance = (intercept_x**2 + intercept_y**2)**0.5
                            
                            if intercept_distance > 0:
                                speed_multiplier = 1.3
                                move_x = (intercept_x / intercept_distance) * self.speed * speed_multiplier * dt / 1000
                                move_y = (intercept_y / intercept_distance) * self.speed * speed_multiplier * dt / 1000
                                
                                self.world_x += move_x
                                self.world_y += move_y
                                # Ensure zombie stays within map bounds
                                self.world_y = max(328, min(self.world_y, 550))
                                self.facing_right = move_x > 0
                        else:
                            # Zumbi está na frente ou lateral, movimento direto
                            self._move_directly_to_player(distance_x, distance_y, dt)
                    else:
                        # Player movendo verticalmente
                        self._move_directly_to_player(distance_x, distance_y, dt)
                else:
                    # Player parado ou movendo devagar
                    self._move_directly_to_player(distance_x, distance_y, dt)
            else:                
                # Próximo ao jogador mas ainda não atacando, fica em idle e vira para o jogador
                self.current_state = "idle"
                self.facing_right = distance_x > 0
        
        self.world_y = max(328, min(self.world_y, 550))
        
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
            print(f"Zombie died!")
            return True  
        else:
            self.current_state = "hurt"
            self.animation_timer = 0
            self.animation_complete = False
            self.current_animation.reset()            
            print(f"Zombie took {damage} damage! Health: {self.health}/{self.max_health}")
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
            print(f"Error getting zombie image: {e}")
            fallback = pygame.Surface((int(128 * self.scale), int(128 * self.scale)))
            fallback.fill((0, 150, 0))
            return fallback
    
    def draw_health_bar(self, screen, camera_x):
        if self.is_dead or self.health <= 0:
            return
        
        # posição da barrsa de vida
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
        if abs(distance_x) > 5:
            if distance_x > 0:
                self.world_x += self.speed * dt / 1000
                self.facing_right = True
            else:
                self.world_x -= self.speed * dt / 1000
                self.facing_right = False
        
        if abs(distance_y) > 5:
            if distance_y > 0:
                self.world_y += self.speed * dt / 1000
            else:
                self.world_y -= self.speed * dt / 1000
        
        # Ensure zombie stays within map bounds after movement
        self.world_y = max(328, min(self.world_y, 550))
