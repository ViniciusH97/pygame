import pygame
import random
from zombie import Zombie

class ZombieSpawner:
    def __init__(self):
        self.zombies = []
        self.spawn_points = []
        self.last_spawn_x = 0
        self.spawn_distance = 800  # Distancia do spawn dos zombis
        self.zombie_types = ["Zombie_1", "Zombie_2"]  # Tipos disponíveis de zumbis
        
    def update(self, player, dt):
        # verifica se precisa de mais zumbis
        player_progress = player.world_x
        
        # Create spawn points ahead of player
        while self.last_spawn_x < player_progress + 2000:  # Keep spawns 2000 units ahead
            self.last_spawn_x += self.spawn_distance
            spawn_y = 328 + (500 - 328) * (hash(self.last_spawn_x) % 100) / 100
            self.spawn_points.append((self.last_spawn_x, spawn_y))
        
        # Spawn zombies from spawn points that are close to player
        for spawn_point in self.spawn_points[:]:
            spawn_x, spawn_y = spawn_point
            if abs(spawn_x - player_progress) < 1000 and spawn_x > player_progress - 500:
                # Check if there's already a zombie near this spawn point
                zombie_exists = any(abs(zombie.world_x - spawn_x) < 100 for zombie in self.zombies)
                if not zombie_exists:
                    # Escolher tipo de zumbi aleatoriamente
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
        window_width = screen.get_width()
        for zombie in self.zombies:
            zombie_screen_x = zombie.world_x - camera_x
            zombie_screen_y = zombie.world_y

            if -200 < zombie_screen_x < window_width + 200:
                zombie_image = zombie.get_image()
                screen.blit(zombie_image, (zombie_screen_x, zombie_screen_y))
                zombie.draw_health_bar(screen, camera_x)
                
    def check_player_attacks(self, player):
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
