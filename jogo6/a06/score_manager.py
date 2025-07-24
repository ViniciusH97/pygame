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
        self.points_per_zombie = 100
        self.points_per_10_seconds = 5
        
        # Sistema de records
        self.high_score_data = self.load_high_score()
        self.high_score = self.high_score_data.get('score', 0)
        self.high_score_name = self.high_score_data.get('name', '')
        self.rankings = self.load_rankings()
        
    def add_zombie_kill(self):
        self.zombies_killed += 1
        self.score += self.points_per_zombie
        
    def update(self, dt):
        if not self.game_over:  # Só atualizar se o jogo não acabou
            current_time = time.time()
            self.time_survived = current_time - self.start_time
            
            # Dar pontos a cada 10 segundos
            ten_seconds_survived = int(self.time_survived // 10)
            if ten_seconds_survived > self.last_time_bonus:
                self.score += self.points_per_10_seconds
                self.last_time_bonus = ten_seconds_survived
    
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
    
    def add_score_to_ranking(self, player_name):
        """Adiciona a pontuação atual ao ranking"""
        score_entry = {
            'name': player_name,
            'score': self.score,
            'zombies_killed': self.zombies_killed,
            'time_survived': self.get_time_survived_formatted(),
            'time_survived_seconds': int(self.time_survived)
        }
        
        self.rankings.append(score_entry)
        # Ordenar por pontuação (maior primeiro)
        self.rankings.sort(key=lambda x: x['score'], reverse=True)
        # Manter apenas os top 100
        self.rankings = self.rankings[:100]
        self.save_rankings()
        
        # Atualizar high score se necessário
        if self.score > self.high_score:
            self.high_score = self.score
            self.high_score_name = player_name
            self.save_high_score()
    
    def load_rankings(self):
        try:
            script_dir = os.path.dirname(__file__)
            rankings_file = os.path.join(script_dir, "rankings.json")
            
            if os.path.exists(rankings_file):
                with open(rankings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_rankings(self):
        try:
            script_dir = os.path.dirname(__file__)
            rankings_file = os.path.join(script_dir, "rankings.json")
            
            with open(rankings_file, 'w', encoding='utf-8') as f:
                json.dump(self.rankings, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def load_high_score(self):
        try:
            # Usar o diretório do script para salvar o arquivo
            script_dir = os.path.dirname(__file__)
            score_file = os.path.join(script_dir, "high_score.json")
            
            if os.path.exists(score_file):
                with open(score_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
        except:
            pass
        return {'score': 0, 'name': ''}
    
    def save_high_score(self):
        try:
            # Usar o diretório do script para salvar o arquivo
            script_dir = os.path.dirname(__file__)
            score_file = os.path.join(script_dir, "high_score.json")
            
            with open(score_file, 'w', encoding='utf-8') as f:
                json.dump({'score': self.high_score, 'name': self.high_score_name}, f, ensure_ascii=False)
        except:
            pass
    
    def get_time_survived_formatted(self):
        minutes = int(self.time_survived // 60)
        seconds = int(self.time_survived % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_stats(self):
        # Obter o nome do recordista do topo do ranking (se existir)
        record_name = ''
        if self.rankings and len(self.rankings) > 0:
            record_name = self.rankings[0]['name']
        elif self.high_score_name:
            record_name = self.high_score_name
            
        return {
            'score': self.score,
            'high_score': self.high_score,
            'high_score_name': record_name,
            'zombies_killed': self.zombies_killed,
            'time_survived': self.get_time_survived_formatted(),
            'time_survived_seconds': int(self.time_survived)
        }
