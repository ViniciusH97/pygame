import pygame
import random
from zombie import Zombie
from ammo_pickup import AmmoPickup

class ZombieSpawner:
    def __init__(self):
        self.zombies = []
        self.last_spawn_x = 800  # Começar spawn mais à frente
        self.spawn_distance = 400  # Reduzir distância entre spawns para mais zumbis
        self.zombie_types = ["Zombie_1", "Zombie_2", "Zombie_3", "Zombie_4"] 
        self.ammo_pickups = []
        self.spawn_timer = 0  # Timer para controlar spawn contínuo
        self.spawn_interval = 3000  # Spawn a cada 3 segundos  
        
    def update(self, player, dt):
        self.spawn_timer += dt
        player_progress = player.world_x
        
        # Calcular quantos zumbis devem existir baseado no progresso do player
        # Mais longe = mais zumbis
        desired_zombie_count = min(15, 3 + int(player_progress / 1000))  # Máximo 15 zumbis
        
        # Spawn contínuo de zumbis vindos da direita
        if self.spawn_timer >= self.spawn_interval and len(self.zombies) < desired_zombie_count:
            self.spawn_timer = 0
            
            # Spawn bem mais à direita, totalmente fora da visão do player
            camera_x = max(0, player.world_x - 640)  # Assumindo tela de ~1280px
            spawn_x = camera_x + 1280 + random.randint(300, 800)  # Muito mais longe à direita
            
            # Spawnar próximo à altura do player mas com alguma variação
            spawn_y = player.world_y + random.randint(-30, 30)  # Pequena variação

            # Garantir que a posição Y esteja dentro de limites aceitáveis
            spawn_y = max(380, min(spawn_y, 520))  # Faixa um pouco mais ampla

            # Escolher tipo de zumbi - zumbis mais fortes aparecem conforme progresso
            if player_progress < 1000:
                zombie_type = random.choice(["Zombie_1", "Zombie_2"])
            elif player_progress < 2000:
                zombie_type = random.choice(["Zombie_1", "Zombie_2", "Zombie_3"])
            elif player_progress < 3000:
                zombie_type = random.choice(["Zombie_1", "Zombie_2", "Zombie_3", "Zombie_4"])
            else:
                zombie_type = random.choice(self.zombie_types)

            new_zombie = Zombie(spawn_x, spawn_y, zombie_type)
            # NÃO detectar o player inicialmente - deixar ele patrulhar
            new_zombie.player_detected = False  # Começar patrulhando
            new_zombie.facing_right = False  # Virar para a esquerda
            new_zombie.current_state = "walk"  # Começar andando
            self.zombies.append(new_zombie)

            # Reduzir intervalo de spawn conforme progresso (mais zumbis)
            base_interval = max(1500, 4000 - int(player_progress / 500))
            self.spawn_interval = base_interval + random.randint(-500, 500)
        
        # Atualizar zumbis existentes
        for zombie in self.zombies[:]:
            zombie.update(dt, player)
            
            # Forçar zumbis a seguirem o player quando detectado
            if zombie.player_detected and not zombie.is_dead:
                # Se o zumbi está perseguindo, permitir que siga o player em qualquer altura
                target_y = player.world_y
                
                # Mover gradualmente em direção ao player Y
                y_diff = target_y - zombie.world_y
                if abs(y_diff) > 5:  # Se diferença é significativa
                    move_speed = min(zombie.speed * dt / 1000, abs(y_diff))
                    if y_diff > 0:
                        zombie.world_y += move_speed
                    else:
                        zombie.world_y -= move_speed
                
                # Permitir faixa mais ampla durante perseguição
                zombie.world_y = max(250, min(zombie.world_y, 650))
            else:
                # Quando não está perseguindo, manter nos limites padrão mais restritivos
                zombie.world_y = max(380, min(zombie.world_y, 520))
            
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
        """Spawnar munição quando um zumbi morrer"""
        # 25% de chance de spawnar munição (reduzido de 40%)
        if random.randint(1, 100) <= 25:
            # Calcular centro visual correto do sprite do zumbi
            # Sprite base: 128x128 pixels, escala: 3.5
            sprite_width = int(128 * 3.5)
            sprite_height = int(128 * 3.5)
            
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
        attack_width = 80
        attack_height = 100
        attack_type = ""
        
        if player.current_state in ["attack_1", "attack_2"] and player.animation_timer < 1000:  
            is_attacking = True
            attack_type = player.current_state
            
            # Ajuste do ataque 2 (coronhada)
            if player.current_state == "attack_2":  # Coronhada
                attack_range = 100  # Aumentar alcance
                attack_width = 140  # Aumentar largura para melhor detecção
            else:  # attack_1 
                attack_range = 100
                attack_width = 100
            
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
                # Para ataques corpo a corpo quando olhando para esquerda, ajustar posição
                if attack_type in ["attack_1", "attack_2"]:
                    attack_x = player.world_x - attack_width - 20  # Usar largura do ataque em vez do alcance
                else:
                    attack_x = player.world_x - attack_range - 20  # Para tiros, usar alcance normal
                
            # Posicionamento Y melhorado para combinar melhor com a altura dos zumbis
            if attack_type in ["attack_1", "attack_2"]:  # Ataques corpo a corpo
                attack_y = player.world_y + 80  # Posição Y um pouco mais alta
                if attack_type == "attack_2":  # Coronhada tem hitbox maior
                    attack_height = 220  # Altura ainda maior para coronhada
                    attack_width = max(attack_width, 160)  # Largura ainda maior para coronhada
                else:
                    attack_height = 180  
                    attack_width = max(attack_width, 140)
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
