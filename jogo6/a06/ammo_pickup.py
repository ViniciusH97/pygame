import os
import pygame
import random
import math
from language_manager import language_manager

class AmmoPickup:
    def __init__(self, x, y):
        self.world_x = x
        self.world_y = y
        self.scale = 0.08 
        self.collected = False
        self.ammo_amount = 3  
        
        # Hitbox grande para facilitar coleta, centralizada na munição
        self.rect = pygame.Rect(x - 40, y - 40, 80, 80)
        
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        IMAGES_DIR = os.path.join(BASE_DIR, "imagens")
        ammo_path = os.path.join(IMAGES_DIR, "municao.png")
        
        try:
            self.image = pygame.image.load(ammo_path).convert_alpha()
            new_width = int(self.image.get_width() * self.scale)
            new_height = int(self.image.get_height() * self.scale)
            self.image = pygame.transform.scale(self.image, (new_width, new_height))
        except Exception as e:
            print(f"Erro ao carregar imagem da munição: {e}")
            self.image = pygame.Surface((16, 16))
            self.image.fill((255, 255, 0))
        
        # Animação de flutuação
        self.float_timer = 0
        self.float_amplitude = 5
        self.original_y = y
        
    def update(self, dt):
        """Atualizar animação de flutuação"""
        if not self.collected:
            self.float_timer += dt
            float_offset = self.float_amplitude * math.sin(self.float_timer / 200)
            self.world_y = self.original_y + float_offset
            # Atualizar hitbox para acompanhar a posição (centralizada na munição)
            self.rect.x = self.world_x - 40  # Hitbox centralizada
            self.rect.y = self.world_y - 40
    
    def check_collision(self, player):
        """Verificar colisão com o player"""
        if not self.collected and self.rect.colliderect(player.rect):
            # Verificar se o player pode carregar mais munição na reserva
            if player.reserve_ammo < player.max_reserve_ammo:
                # Adicionar munição à reserva do player
                old_reserve = player.reserve_ammo
                player.reserve_ammo = min(player.max_reserve_ammo, player.reserve_ammo + self.ammo_amount)
                self.collected = True
                print(f"{language_manager.get_text('ammo_collected')}: {old_reserve} -> {player.reserve_ammo}")
                return True
            else:
                print(language_manager.get_text("max_reserve"))
        return False
    
    def draw(self, screen, camera_x):
        """Desenhar a munição na tela"""
        if not self.collected:
            ammo_screen_x = self.world_x - camera_x
            ammo_screen_y = self.world_y
            
            # Só desenhar se estiver na tela
            window_width = screen.get_width()
            if -50 < ammo_screen_x < window_width + 50:
                screen.blit(self.image, (ammo_screen_x, ammo_screen_y))
