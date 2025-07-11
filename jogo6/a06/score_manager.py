import pygame
import time

class ScoreManager:
    def __init__(self):
        self.score = 0
        self.zombies_killed = 0
        self.time_survived = 0
        self.start_time = time.time()
        self.last_time_bonus = 0
        self.game_over = False  # Flag para parar o tempo
        
        # Pontuação
        self.points_per_zombie = 10
        self.points_per_minute = 5
        
    def add_zombie_kill(self):
        """Adicionar pontos por matar um zumbi"""
        self.zombies_killed += 1
        self.score += self.points_per_zombie
        
    def update(self, dt):
        """Atualizar tempo sobrevivido e bônus de tempo"""
        if not self.game_over:  # Só atualizar se o jogo não acabou
            current_time = time.time()
            self.time_survived = current_time - self.start_time
            
            # Dar pontos a cada minuto
            minutes_survived = int(self.time_survived // 60)
            if minutes_survived > self.last_time_bonus:
                self.score += self.points_per_minute
                self.last_time_bonus = minutes_survived
    
    def set_game_over(self):
        """Parar a contagem do tempo quando o jogo acabar"""
        if not self.game_over:
            self.game_over = True
            # Congelar o tempo no momento da morte
            current_time = time.time()
            self.time_survived = current_time - self.start_time
    
    def get_time_survived_formatted(self):
        """Retornar tempo sobrevivido formatado"""
        minutes = int(self.time_survived // 60)
        seconds = int(self.time_survived % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_stats(self):
        """Retornar estatísticas completas"""
        return {
            'score': self.score,
            'zombies_killed': self.zombies_killed,
            'time_survived': self.get_time_survived_formatted(),
            'time_survived_seconds': int(self.time_survived)
        }
