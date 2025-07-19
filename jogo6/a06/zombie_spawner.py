import pygame
import random
from zombie import Zombie
from ammo_pickup import AmmoPickup

class ZombieSpawner:
    def __init__(self):
        self.zombies = []
        self.last_spawn_x = 800  
        self.spawn_distance = 400  # Reduzir distância entre spawns para mais zumbis
        self.zombie_types = ["Zombie_1", "Zombie_2", "Zombie_3", "Zombie_4"] 
        self.ammo_pickups = []
        self.spawn_timer = 0  # Timer para controlar spawn contínuo
        self.spawn_interval = 3000  # Spawn a cada 3 segundos  
        
    def update(self, player, dt, score_manager=None):
        self.spawn_timer += dt
        player_progress = player.world_x
        
        # Calcular quantos zumbis devem existir baseado na pontuação do player
        # Mais pontos = mais zumbis
        if score_manager:
            player_score = score_manager.score
            zombies_killed = score_manager.zombies_killed
            time_survived = score_manager.time_survived
            
            # Sistema de dificuldade simplificado (menos dependente de kills)
            base_zombie_count = 3
            score_bonus = min(12, int(player_score / 30))  # Aumentado e mais fácil
            kill_bonus = min(3, int(zombies_killed / 15))  # Reduzido e mais difícil de alcançar
            time_bonus = min(10, int(time_survived / 45))   # Aumentado e mais fácil
            
            desired_zombie_count = min(25, base_zombie_count + score_bonus + kill_bonus + time_bonus)
        else:
            # Fallback para sistema antigo baseado em posição
            desired_zombie_count = min(15, 3 + int(player_progress / 1000))
        
        # Spawn contínuo de zumbis vindos da direita
        if self.spawn_timer >= self.spawn_interval and len(self.zombies) < desired_zombie_count:
            self.spawn_timer = 0
            
            # Spawn estratégico - alguns à frente, alguns atrás para cercar o player
            camera_x = max(0, player.world_x - 640)  # Assumindo tela de ~1280px
            
            # 70% chance de spawn à direita, 30% chance à esquerda (atrás do player)
            if random.randint(1, 100) <= 70:
                # Spawn à direita (normal)
                spawn_x = camera_x + 1280 + random.randint(200, 600)
            else:
                # Spawn à esquerda (atrás do player) para impedir fuga infinita
                spawn_x = max(0, player.world_x - random.randint(800, 1200))
            
            # Spawnar próximo à altura do player com variação mínima
            spawn_y = player.world_y + random.randint(-15, 15)  # Variação muito pequena

            # Garantir que a posição Y esteja próxima ao player (mais restritiva)
            spawn_y = max(player.world_y - 50, min(spawn_y, player.world_y + 50))  # Muito próximo ao player

            # Escolher tipo de zumbi aleatoriamente - todos com mesma frequência
            zombie_type = random.choice(self.zombie_types)

            new_zombie = Zombie(spawn_x, spawn_y, zombie_type)
            
            # Configurar comportamento baseado na posição de spawn
            if spawn_x < player.world_x:  # Zumbi spawnou atrás
                new_zombie.player_detected = True  # Detectar imediatamente
                new_zombie.facing_right = True  # Virar para a direita (em direção ao player)
                new_zombie.current_state = "walk"  # Começar perseguindo
            else:  # Zumbi spawnou à frente
                new_zombie.player_detected = False  # Começar patrulhando
                new_zombie.facing_right = False  # Virar para a esquerda
                new_zombie.current_state = "walk"  # Começar andando
                
            # Velocidade mantida padrão do tipo de zumbi (sem boost)
            self.zombies.append(new_zombie)

            # Reduzir intervalo de spawn conforme pontuação aumenta (mais zumbis)
            if score_manager:
                player_score = score_manager.score
                # Spawn mais rápido com pontuação maior
                base_interval = max(1000, 4000 - int(player_score / 10))  # Reduz 100ms a cada 10 pontos
                self.spawn_interval = base_interval + random.randint(-200, 200)
            else:
                # Fallback para sistema antigo
                base_interval = max(1500, 4000 - int(player_progress / 500))
                self.spawn_interval = base_interval + random.randint(-300, 300)
        
        # Atualizar zumbis existentes
        for zombie in self.zombies[:]:
            zombie.update(dt, player)
            
            # Apenas detectar o player se estiver próximo, mas não forçar movimento
            if not zombie.player_detected and not zombie.is_dead:
                distance_to_player = abs(zombie.world_x - player.world_x)
                if distance_to_player < 500:  # Range de detecção
                    zombie.player_detected = True
                    zombie.current_state = "walk"
            
            # Remover zumbis que saíram muito para a esquerda
            if zombie.world_x < player_progress - 1500:  
                if zombie.is_dead:
                    zombie.death_timer = getattr(zombie, 'death_timer', 0) + dt
                    if zombie.death_timer > 8000:  # 8 segundos
                        self.zombies.remove(zombie)
                else:
                    self.zombies.remove(zombie)
            
            # Remover zumbis mortos após tempo
            elif zombie.is_dead and zombie.death_animation_complete:
                zombie.death_timer = getattr(zombie, 'death_timer', 0) + dt
                if zombie.death_timer > 8000:  # 8 segundos
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

        if random.randint(1, 100) <= 70:
            # Calcular centro visual correto do sprite do zumbi
            # Sprite base: 128x128 pixels, escala: 4 (atualizada)
            sprite_width = int(128 * 4)
            sprite_height = int(128 * 4)
            
            # Posicionar munição no centro do sprite morto
            ammo_x = zombie_x + (sprite_width // 2)
            ammo_y = zombie_y + (sprite_height // 2) + 20  # Ligeiramente para baixo do centro
            
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
        attack_width = 120  # Aumentado de 80 para 120
        attack_height = 120  # Aumentado de 100 para 120
        attack_type = ""
        
        if player.current_state in ["attack_1", "attack_2"] and player.animation_timer < 1000:  
            is_attacking = True
            attack_type = player.current_state
            
            # Ajuste do ataque 2 (coronhada) - valores maiores
            if player.current_state == "attack_2":  # Coronhada
                attack_range = 130 
                attack_width = 180  
            else:  # attack_1 
                attack_range = 120
                attack_width = 150
            
        # Verificar ataques de tiro (botão esquerdo do mouse)  
        elif player.current_state == "shot" and player.animation_timer < 800:  
            is_attacking = True
            attack_type = "shot"
            
            attack_range = 250
            attack_width = 120
            
        if is_attacking:
            # Criar hitbox de ataque na frente do player - posicionamento melhorado
            if player.facing_right:
                if attack_type in ["attack_1", "attack_2"]:
                    attack_x = player.world_x + 40  # Mais próximo para ataques melee
                else:
                    attack_x = player.world_x + 80  # Posição normal para tiros
            else:
                # Para ataques corpo a corpo quando olhando para esquerda, ajustar posição
                if attack_type in ["attack_1", "attack_2"]:
                    attack_x = player.world_x - attack_width + 20  # Posição ajustada para esquerda
                else:
                    # Para tiros, usar largura em vez de alcance para posicionamento mais próximo
                    attack_x = player.world_x - attack_width - 40  # Posição mais próxima para tiros à esquerda
                
            # Posicionamento Y melhorado para combinar melhor com a altura dos zumbis
            if attack_type in ["attack_1", "attack_2"]:  # Ataques corpo a corpo
                attack_y = player.world_y + 40  # Posição Y mais baixa para pegar os zumbis
                if attack_type == "attack_2":  # Coronhada tem hitbox ainda maior
                    attack_height = 280  # Altura muito maior para coronhada
                    attack_width = max(attack_width, 200)  # Largura muito maior para coronhada
                    attack_range = 140  # Alcance maior para coronhada
                    attack_y = player.world_y + 20  # Posição ainda mais baixa para coronhada
                else:
                    attack_height = 220  # Altura maior para attack_1
                    attack_width = max(attack_width, 170)
                    attack_y = player.world_y + 30  # Posição ligeiramente mais baixa
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
                            if player.facing_right and zombie.world_x < player.world_x:
                                continue  # Zumbi está atrás do player, pular
                            elif not player.facing_right and zombie.world_x > player.world_x:
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
                                # Knockback melhorado e mais consistente
                                if attack_type == "attack_1":
                                    knockback_force = 120
                                else:  # attack_2 (coronhada)
                                    knockback_force = 180  # Força moderada mas visível
                                
                                # Empurrar zumbi para longe do player
                                if player.facing_right:
                                    zombie.world_x += knockback_force
                                else:
                                    zombie.world_x -= knockback_force
                                
                                # Efeito especial para attack_2 - knockback adicional para cima
                                if attack_type == "attack_2":
                                    zombie.world_y -= 25  # Movimento para cima mais suave mas visível
