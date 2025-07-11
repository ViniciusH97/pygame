import pygame
import random
from zombie import Zombie
from ammo_pickup import AmmoPickup
from language_manager import language_manager

class ZombieSpawner:
    def __init__(self):
        self.zombies = []
        self.spawn_points = []
        self.last_spawn_x = 0
        self.spawn_distance = 800  
        self.zombie_types = ["Zombie_1", "Zombie_2", "Zombie_3", "Zombie_4"]  # Tipos disponíveis de zumbis
        self.ammo_pickups = []  # Lista de munições no mapa
        
    def update(self, player, dt):
        # verifica se precisa de mais zumbis
        player_progress = player.world_x
        
        # Create spawn points ahead of player
        while self.last_spawn_x < player_progress + 2000:  
            self.last_spawn_x += self.spawn_distance
            # Spawn zombies at the same Y position as the player, but ensure it's within valid bounds
            spawn_y = max(328, min(player.world_y, 550))  # Keep within map bounds
            self.spawn_points.append((self.last_spawn_x, spawn_y))
        
        # Clean up any existing spawn points that are outside bounds
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
                    print(f"{language_manager.get_text('zombie_spawned')} {zombie_type} at position ({spawn_x}, {spawn_y})")
                    
        for zombie in self.zombies[:]:
            zombie.update(dt, player)
            
            # Force all zombies to stay within bounds every frame
            zombie.world_y = max(328, min(zombie.world_y, 550))
            
            if zombie.world_x < player_progress - 2000:  
                if zombie.is_dead:
                    zombie.death_timer = getattr(zombie, 'death_timer', 0) + dt
                    if zombie.death_timer > 10000:  # 10 segundos
                        self.zombies.remove(zombie)
                        print(f"Removed dead zombie after 10 seconds to prevent system overload")
                else:
                    self.zombies.remove(zombie)
            
            # Remover zumbis mortos após 10 segundos independente da posição
            elif zombie.is_dead and zombie.death_animation_complete:
                zombie.death_timer = getattr(zombie, 'death_timer', 0) + dt
                if zombie.death_timer > 10000:  # 10 segundos
                    self.zombies.remove(zombie)
                    print(f"Removed dead zombie after 10 seconds to prevent system overload")
        
        # Atualizar munições
        for ammo in self.ammo_pickups[:]:
            ammo.update(dt)
            if ammo.check_collision(player):
                self.ammo_pickups.remove(ammo)
                print(f"Player coletou munição! Munição atual: {player.current_ammo}")
        
        # Debug: mostrar quantas munições estão no mapa
        if len(self.ammo_pickups) > 0:
            print(f"Munições ativas no mapa: {len(self.ammo_pickups)}")
        
        # Remover munições muito longe do player
        self.ammo_pickups = [ammo for ammo in self.ammo_pickups 
                            if not ammo.collected and abs(ammo.world_x - player_progress) < 2000]
    
    def spawn_ammo_pickup(self, zombie_x, zombie_y):
        """Spawnar munição quando um zumbi morrer"""
        # 60% de chance de spawnar munição (aumentada para testar)
        if random.randint(1, 100) <= 60:
            # Spawnar munição no chão, na mesma altura do player
            ammo_x = zombie_x + 30  # Pequeno offset para não ficar exatamente em cima
            ammo_y = 530  # Posição fixa no chão onde o player anda
            new_ammo = AmmoPickup(ammo_x, ammo_y)
            self.ammo_pickups.append(new_ammo)
            print(f"*** {language_manager.get_text('ammo_spawned')} *** em ({ammo_x}, {ammo_y}) após morte do zumbi em ({zombie_x}, {zombie_y})")
                    
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
            
            # ajuste do ataque 2 (coronhada)
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
                if not zombie.is_dead:
                    # Use appropriate hitbox based on attack type
                    if attack_type in ["attack_1", "attack_2"]:  # Melee attacks use smaller hitbox
                        target_hitbox = zombie.melee_rect
                        hitbox_type = "melee"
                    else:  # Ranged attacks (shot) use larger hitbox
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
                            
                            # Se o zumbi morreu, adicionar pontos e chance de spawnar munição
                            if zombie_died and score_manager:
                                score_manager.add_zombie_kill()
                                self.spawn_ammo_pickup(zombie.world_x, zombie.world_y)
                            
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
                print(f"Attack {attack_type} detected but no zombies hit")
                # Debug: Print positions
                print(f"Player pos: {player.world_x}, {player.world_y}")
                print(f"Attack rect: {attack_rect}")
                for zombie in self.zombies:
                    if not zombie.is_dead:
                        distance = abs(zombie.world_x - player.world_x)
                        print(f"Zombie pos: {zombie.world_x}, {zombie.world_y}")
                        print(f"  Melee rect: {zombie.melee_rect}, distance: {distance}")
                        print(f"  Ranged rect: {zombie.ranged_rect}")
