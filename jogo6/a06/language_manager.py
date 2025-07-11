import json
import os

class LanguageManager:
    def __init__(self):
        self.current_language = "pt"  # Padrão português
        self.texts = {
            "pt": {
                # Menu
                "game_title": "Survive If You Can",
                "play": "JOGAR",
                "instructions": "INSTRUÇÕES",
                "language": "IDIOMA",
                "exit": "SAIR",
                
                # Instruções
                "instructions_title": "INSTRUÇÕES",
                "controls": "CONTROLES:",
                "move": "A/D ou Setas - Mover",
                "jump": "ESPAÇO - Pular",
                "run": "SHIFT - Correr (gasta stamina)",
                "attack1": "Clique Esquerdo - Tiro (gasta munição)",
                "attack2": "Clique Direito - Ataque corpo a corpo",
                "reload": "R - Recarregar",
                "objective": "OBJETIVO:",
                "survive": "Sobreviva o máximo possível!",
                "kill_zombies": "Mate zumbis para ganhar pontos",
                "collect_ammo": "Colete munição dos zumbis mortos",
                "back_menu": "Pressione ESC para voltar ao menu",
                
                # Jogo
                "score": "PONTUAÇÃO",
                "time": "TEMPO",
                "ammo": "MUNIÇÃO",
                "health": "VIDA",
                "stamina": "STAMINA",
                "game_over": "GAME OVER",
                "final_score": "PONTUAÇÃO FINAL",
                "zombies_killed": "Zumbis Mortos",
                "time_survived": "Tempo Sobrevivido",
                "points_per_zombie": "Pontos por Zumbi",
                "points_per_minute": "Pontos por Minuto",
                "press_esc": "Pressione ESC para voltar ao menu",
                
                # Sistema de munição
                "shot_fired": "Tiro disparado! Munição restante",
                "reloading": "Recarregando... Pente",
                "reserve_ammo": "Reserva",
                "no_reserve_ammo": "Sem munição na reserva! Colete mais munição.",
                "magazine_full": "Pente já está cheio!",
                "reload_complete": "Recarga completa",
                "magazine": "Pente",
                "ammo_collected": "Munição coletada! Reserva",
                "max_reserve": "Reserva de munição máxima já atingida!",
                "ammo_spawned": "MUNIÇÃO SPAWNADA",
                "active_ammo": "Munições ativas no mapa",
                
                # Debug
                "zombie_spawned": "Spawned",
                "zombie_died": "Zumbi morreu!",
                "zombie_removed": "Removed dead zombie after 10 seconds to prevent system overload"
            },
            "en": {
                # Menu
                "game_title": "Survive If You Can",
                "play": "PLAY",
                "instructions": "INSTRUCTIONS",
                "language": "LANGUAGE",
                "exit": "EXIT",
                
                # Instructions
                "instructions_title": "INSTRUCTIONS",
                "controls": "CONTROLS:",
                "move": "A/D or Arrows - Move",
                "jump": "SPACE - Jump",
                "run": "SHIFT - Run (uses stamina)",
                "attack1": "Left Click - Shoot (uses ammo)",
                "attack2": "Right Click - Melee attack",
                "reload": "R - Reload",
                "objective": "OBJECTIVE:",
                "survive": "Survive as long as possible!",
                "kill_zombies": "Kill zombies to earn points",
                "collect_ammo": "Collect ammo from dead zombies",
                "back_menu": "Press ESC to return to menu",
                
                # Game
                "score": "SCORE",
                "time": "TIME",
                "ammo": "AMMO",
                "health": "HEALTH",
                "stamina": "STAMINA",
                "game_over": "GAME OVER",
                "final_score": "FINAL SCORE",
                "zombies_killed": "Zombies Killed",
                "time_survived": "Time Survived",
                "points_per_zombie": "Points per Zombie",
                "points_per_minute": "Points per Minute",
                "press_esc": "Press ESC to return to menu",
                
                # Ammo system
                "shot_fired": "Shot fired! Ammo remaining",
                "reloading": "Reloading... Magazine",
                "reserve_ammo": "Reserve",
                "no_reserve_ammo": "No reserve ammo! Collect more ammo.",
                "magazine_full": "Magazine is already full!",
                "reload_complete": "Reload complete",
                "magazine": "Magazine",
                "ammo_collected": "Ammo collected! Reserve",
                "max_reserve": "Maximum reserve ammo already reached!",
                "ammo_spawned": "AMMO SPAWNED",
                "active_ammo": "Active ammo on map",
                
                # Debug
                "zombie_spawned": "Spawned",
                "zombie_died": "Zombie died!",
                "zombie_removed": "Removed dead zombie after 10 seconds to prevent system overload"
            }
        }
        
    def get_text(self, key):
        """Obter texto no idioma atual"""
        return self.texts[self.current_language].get(key, key)
    
    def set_language(self, language):
        """Definir idioma atual"""
        if language in self.texts:
            self.current_language = language
            return True
        return False
    
    def get_current_language(self):
        """Obter idioma atual"""
        return self.current_language
    
    def toggle_language(self):
        """Alternar entre português e inglês"""
        if self.current_language == "pt":
            self.current_language = "en"
        else:
            self.current_language = "pt"
        return self.current_language

# Instância global do gerenciador de idiomas
language_manager = LanguageManager()
