import os
import pygame
import random
import math

class AmmoPickup:
    def __init__(self, x, y):
        self.world_x = x
        self.world_y = y - 100  # Mudar este valor: negativo = mais alto, positivo = mais baixo
        self.scale = 0.09
        self.collected = False
        self.ammo_amount = 3  
    
        hitbox_size = 200
        self.rect = pygame.Rect(x - hitbox_size//2, y - 100 - hitbox_size//2, hitbox_size, hitbox_size)
        
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
        ammo_path = os.path.join(IMAGES_DIR, "municao.png")
        
      
        self.image = pygame.image.load(ammo_path).convert_alpha()
        new_width = int(self.image.get_width() * self.scale)
        new_height = int(self.image.get_height() * self.scale)
        self.image = pygame.transform.scale(self.image, (new_width, new_height))

        # Animação 
        self.float_timer = 0
        self.float_amplitude = 8  
        self.original_y = y - 100 # Ajustar também aqui
        
    def update(self, dt):
        if not self.collected:
            self.float_timer += dt
            float_offset = self.float_amplitude * math.sin(self.float_timer / 300)  
            self.world_y = self.original_y + float_offset
            # Atualizar hitbox junto com a posição
            self.rect.centerx = self.world_x
            self.rect.centery = self.world_y
    
    def check_collision(self, player):
        if not self.collected and self.rect.colliderect(player.rect):
            # Verificar se o player pode carregar mais munição na reserva
            if player.reserve_ammo < player.max_reserve_ammo:
                # Adicionar munição à reserva do player
                player.reserve_ammo = min(player.max_reserve_ammo, player.reserve_ammo + self.ammo_amount)
                self.collected = True
                return True
        return False
    
    def draw(self, screen, camera_x):
        if not self.collected:
            ammo_screen_x = self.world_x - camera_x - self.image.get_width() // 2
            ammo_screen_y = self.world_y - self.image.get_height() // 2 
         
            window_width = screen.get_width()
            if -100 < ammo_screen_x < window_width + 100:
                glow_radius = 20 + int(5 * math.sin(self.float_timer / 150))
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (255, 215, 0, 50), (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surface, (ammo_screen_x + self.image.get_width()//2 - glow_radius, 
                                         ammo_screen_y + self.image.get_height()//2 - glow_radius))
                
                screen.blit(self.image, (ammo_screen_x, ammo_screen_y))
