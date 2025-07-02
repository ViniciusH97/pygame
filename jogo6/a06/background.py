import pygame

class Background:
    def __init__(self, layers, speeds):
        self.layers = layers
        self.speeds = speeds
        self.positions = [0] * len(layers)
    
    def update(self, dt, camera_x):
        for i in range(len(self.layers)):
            self.positions[i] = -camera_x * self.speeds[i]
    
    def draw(self, screen):
        window_width = screen.get_width()
        for i, layer in enumerate(self.layers):
            x = self.positions[i] % window_width
            screen.blit(layer, (x, 0))
            if x > 0:
                screen.blit(layer, (x - window_width, 0))
