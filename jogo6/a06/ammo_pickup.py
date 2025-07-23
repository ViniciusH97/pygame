import os
import pygame
import random
import math

class AmmoPickup:
    def __init__(self, x, y):
        self.world_x = x
        self.world_y = y
        self.scale = 0.08 
        self.collected = False
        self.ammo_amount = 3  
    
        hitbox_size = 60 
        self.rect = pygame.Rect(x - hitbox_size//2, y - hitbox_size//2, hitbox_size, hitbox_size)
        
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
        ammo_path = os.path.join(IMAGES_DIR, "municao.png")
        
        try:
            self.image = pygame.image.load(ammo_path).convert_alpha()
            new_width = int(self.image.get_width() * self.scale)
            new_height = int(self.image.get_height() * self.scale)
            self.image = pygame.transform.scale(self.image, (new_width, new_height))
        except Exception as e:
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 215, 0), (25, 25), 20)
            pygame.draw.circle(self.image, (139, 69, 19), (25, 25), 15)
            pygame.draw.circle(self.image, (139, 69, 19), (30, 30), 15)

        self.float_timer = 0
        self.float_amplitude = 8 
        self.original_y = y 
        
    def update(self, dt):
        if not self.collected:
            self.float_timer += dt
            float_offset = self.float_amplitude * math.sin(self.float_timer / 400)  
            self.world_y = self.original_y + float_offset
            
            self.rect.centerx = self.world_x
            self.rect.centery = self.world_y
    
    def check_collision(self, player):
        if self.collected:
            return False
        
        # Verificar se o player pode carregar mais munição
        can_collect = (player.current_ammo < player.max_ammo) or (player.reserve_ammo < player.max_reserve_ammo)
        
        if not can_collect:
            return False
            
        hitbox_collision = self.rect.colliderect(player.rect)
        
        if hitbox_collision:
            player.reserve_ammo = min(player.max_reserve_ammo, player.reserve_ammo + self.ammo_amount)
            self.collected = True
            return True
            
        distance_x = abs(self.world_x - player.world_x)
        distance_y = abs(self.world_y - player.world_y)
        total_distance = (distance_x**2 + distance_y**2)**0.5
        
        if total_distance < 80: 
            player.reserve_ammo = min(player.max_reserve_ammo, player.reserve_ammo + self.ammo_amount)
            self.collected = True
            return True
            
        return False
    
    def draw(self, screen, camera_x):
        if not self.collected:
            ammo_screen_x = self.world_x - camera_x - self.image.get_width() // 2
            ammo_screen_y = self.world_y - self.image.get_height() // 2 
         
            window_width = screen.get_width()
            if -100 < ammo_screen_x < window_width + 200:
                screen.blit(self.image, (ammo_screen_x, ammo_screen_y))
