import pygame
import random
from zombie import Zombie
from ammo_pickup import AmmoPickup

class ZombieSpawner:
    def __init__(self):
        self.zombies = []
        self.spawn_points = []
        self.last_spawn_x = 0
        self.spawn_distance = 800  
        self.zombie_types = ["Zombie_1", "Zombie_2", "Zombie_3", "Zombie_4"]  # Tipos disponíveis de zumbis
        self.ammo_pickups = []  # Lista de munições no mapa
        
    def update(self, player, dt):
        # Verificar se precisa de mais zumbis
        player_progress = player.world_x
        
        # Criar pontos de spawn à frente do player
        while self.last_spawn_x < player_progress + 2000:  
            self.last_spawn_x += self.spawn_distance
            # Spawnar zumbis na mesma altura do player, mas dentro dos limites válidos
            spawn_y = max(328, min(player.world_y, 550))  # Manter dentro dos limites do mapa
            self.spawn_points.append((self.last_spawn_x, spawn_y))
        
        # Limpar pontos de spawn que estão fora dos limites
        self.spawn_points = [(x, max(328, min(y, 550))) for x, y in self.spawn_points]
        
        for spawn_point in self.spawn_points[:]:
            spawn_x, spawn_y = spawn_point
            if abs(spawn_x - player_progress) < 1000 and spawn_x > player_progress - 500:
                zombie_exists = any(abs(zombie.world_x - spawn_x) < 100 for zombie in self.zombies)
                if not zombie_exists:
                    # Escolher tipo de zumbi aleatoriamente
                    zombie_type = random.choice(self.zombie_types)
                    new_zombie = Zombie(spawn_x, spawn_y, zombie_type)
                    self.zombies.append(new_zombie)
                    self.spawn_points.remove(spawn_point)
                    
        for zombie in self.zombies[:]:
            zombie.update(dt, player)
            
            # Forçar todos os zumbis a ficarem dentro dos limites a cada frame
            zombie.world_y = max(328, min(zombie.world_y, 550))
            
            if zombie.world_x < player_progress - 2000:  
                if zombie.is_dead:
                    zombie.death_timer = getattr(zombie, 'death_timer', 0) + dt
                    if zombie.death_timer > 10000:  # 10 segundos
                        self.zombies.remove(zombie)
                else:
                    self.zombies.remove(zombie)
            
            # Remover zumbis mortos após 10 segundos independente da posição
            elif zombie.is_dead and zombie.death_animation_complete:
                zombie.death_timer = getattr(zombie, 'death_timer', 0) + dt
                if zombie.death_timer > 10000:  # 10 segundos
                    self.zombies.remove(zombie)
        
        # Atualizar munições
        for ammo in self.ammo_pickups[:]:
            ammo.update(dt)
            if ammo.check_collision(player):
                self.ammo_pickups.remove(ammo)
        
        # Remover munições muito longe do player
        self.ammo_pickups = [ammo for ammo in self.ammo_pickups 
                            if not ammo.collected and abs(ammo.world_x - player_progress) < 2000]
    
    def spawn_ammo_pickup(self, zombie_x, zombie_y):
        """Spawnar munição quando um zumbi morrer"""
        # 60% de chance de spawnar munição
        if random.randint(1, 100) <= 60:
            # Spawnar munição no chão, na mesma altura do player
            ammo_x = zombie_x + 30  # Pequeno offset para não ficar exatamente em cima
            ammo_y = 530  # Posição fixa no chão onde o player anda
            new_ammo = AmmoPickup(ammo_x, ammo_y)
            self.ammo_pickups.append(new_ammo)
                    
    def draw(self, screen, camera_x):
        window_width = screen.get_width()
        
        # Desenhar zumbis
        for zombie in self.zombies:
            zombie_screen_x = zombie.world_x - camera_x
            zombie_screen_y = zombie.world_y

            if -200 < zombie_screen_x < window_width + 200:
                zombie_image = zombie.get_image()
                screen.blit(zombie_image, (zombie_screen_x, zombie_screen_y))
        
        # Desenhar munições
        for ammo in self.ammo_pickups:
            ammo.draw(screen, camera_x)
                
    def check_player_attacks(self, player, score_manager=None):
        is_attacking = False
        attack_range = 120
        attack_width = 80
        attack_height = 100
        attack_type = ""
        
        if player.current_state in ["attack_1", "attack_2"] and player.animation_timer < 1000:  
            is_attacking = True
            attack_type = player.current_state
            
            # Ajuste do ataque 2 (coronhada)
            if player.current_state == "attack_2":  # Coronhada
                attack_range = 90
                attack_width = 80
            else:  # attack_1 
                attack_range = 100
                attack_width = 90
            
        # Verificar ataques de tiro (botão esquerdo do mouse)  
        elif player.current_state == "shot" and player.animation_timer < 800:  # Janela maior para shot
            is_attacking = True
            attack_type = "shot"
            # Aumentar alcance para ataques de tiro
            attack_range = 250
            attack_width = 150
            
        if is_attacking:
            # Criar hitbox de ataque na frente do player - posicionamento melhorado
            if player.facing_right:
                attack_x = player.world_x + 80  # Posicionar ataque mais próximo do player
            else:
                attack_x = player.world_x - attack_range - 20  # Posicionar ataque na frente quando olhando para esquerda
                
            # Posicionamento Y melhorado para combinar melhor com a altura dos zumbis
            if attack_type in ["attack_1", "attack_2"]:  # Ataques corpo a corpo
                # Ataques corpo a corpo precisam de melhor cobertura vertical para combinar com hitbox dos zumbis
                attack_y = player.world_y + 100  # Ajustar para combinar com posição da hitbox de corpo a corpo dos zumbis
                attack_height = 180  # Aumentar altura para melhor cobertura
                attack_width = max(attack_width, 140)  # Garantir largura mínima para corpo a corpo
            else:  # Ataques de tiro
                attack_y = player.world_y + 60  # Manter posicionamento de tiro
                
            attack_rect = pygame.Rect(attack_x, attack_y, attack_width, attack_height)
            hit_count = 0
            
            for zombie in self.zombies:
                if not zombie.is_dead:
                    # Usar hitbox apropriada baseada no tipo de ataque
                    if attack_type in ["attack_1", "attack_2"]:  # Ataques corpo a corpo usam hitbox menor
                        target_hitbox = zombie.melee_rect
                        hitbox_type = "melee"
                    else:  # Ataques à distância (tiro) usam hitbox maior
                        target_hitbox = zombie.ranged_rect
                        hitbox_type = "ranged"
                    
                    if attack_rect.colliderect(target_hitbox):
                        # Para ataques de tiro, verificar se o zumbi está na frente do player
                        if attack_type == "shot":
                            # Verificar se o zumbi está na direção que o player está olhando
                            if player.facing_right and zombie.world_x <= player.world_x:
                                continue  # Zumbi está atrás do player, pular
                            elif not player.facing_right and zombie.world_x >= player.world_x:
                                continue  # Zumbi está atrás do player, pular
                        
                        # Prevenir múltiplos acertos durante a mesma animação - mais permissivo
                        hit_frame_id = f"{player.current_state}_{player.animation_timer // 300}"  # Janelas de frame maiores
                        if not hasattr(zombie, 'last_hit_frame') or zombie.last_hit_frame != hit_frame_id:
                            zombie.last_hit_frame = hit_frame_id
                            
                            # Determinar dano baseado no tipo de ataque
                            if attack_type == "shot":
                                damage = 30
                            elif attack_type == "attack_1":
                                damage = 10  
                            elif attack_type == "attack_2":
                                damage = 10 
                            else:
                                damage = 0
                            
                            zombie_died = zombie.take_damage(damage)
                            hit_count += 1
                            
                            # Se o zumbi morreu, adicionar pontos e chance de spawnar munição
                            if zombie_died and score_manager:
                                score_manager.add_zombie_kill()
                                self.spawn_ammo_pickup(zombie.world_x, zombie.world_y)
                            
                            # Aplicar knockback APENAS para ataques corpo a corpo (attack_1 e attack_2)
                            if attack_type in ["attack_1", "attack_2"]:
                                knockback_force = 100 if attack_type == "attack_1" else 150  # Mais knockback para attack_2
                                
                                # Empurrar zumbi para longe do player
                                if player.facing_right:
                                    zombie.world_x += knockback_force
                                else:
                                    zombie.world_x -= knockback_force
                                
                                # Efeito especial para attack_2 - knockback adicional para cima
                                if attack_type == "attack_2":
                                    zombie.world_y -= 20  # Movimento para cima no attack_2
