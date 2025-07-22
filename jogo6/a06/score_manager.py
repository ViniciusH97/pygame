import pygame
import time
import os
import json

class ScoreManager:
    def __init__(self):
        self.score = 0
        self.zombies_killed = 0
        self.time_survived = 0
        self.start_time = time.time()
        self.last_time_bonus = 0
        self.game_over = False  
        
        # Pontuação
        self.points_per_zombie = 10
        self.points_per_minute = 50
        
        # Sistema de records
        self.high_score = self.load_high_score()
        
    def add_zombie_kill(self):
        self.zombies_killed += 1
        self.score += self.points_per_zombie
        
    def update(self, dt):
        if not self.game_over:  # Só atualizar se o jogo não acabou
            current_time = time.time()
            self.time_survived = current_time - self.start_time
            
            # Dar pontos a cada minuto
            minutes_survived = int(self.time_survived // 60)
            if minutes_survived > self.last_time_bonus:
                self.score += self.points_per_minute
                self.last_time_bonus = minutes_survived
    
    def set_game_over(self):
        if not self.game_over:
            self.game_over = True
            # Congelar o tempo no momento da morte
            current_time = time.time()
            self.time_survived = current_time - self.start_time
            
            # Verificar se é um novo recorde
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
    
    def load_high_score(self):
        try:
            # Usar o diretório do script para salvar o arquivo
            script_dir = os.path.dirname(__file__)
            score_file = os.path.join(script_dir, "high_score.json")
            
            if os.path.exists(score_file):
                with open(score_file, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        try:
            # Usar o diretório do script para salvar o arquivo
            script_dir = os.path.dirname(__file__)
            score_file = os.path.join(script_dir, "high_score.json")
            
            with open(score_file, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def get_time_survived_formatted(self):
        minutes = int(self.time_survived // 60)
        seconds = int(self.time_survived % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_stats(self):
        return {
            'score': self.score,
            'high_score': self.high_score,
            'zombies_killed': self.zombies_killed,
            'time_survived': self.get_time_survived_formatted(),
            'time_survived_seconds': int(self.time_survived)
        }
