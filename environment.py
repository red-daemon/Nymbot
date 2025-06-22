import arcade
import numpy as np
from config import *

class Environment(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Nymbot Evolution")
        arcade.set_background_color(BACKGROUND_COLOR)
        
        # Paredes (caja)
        self.walls = [
            [(50, 50), (750, 50)],   # Inferior
            [(750, 50), (750, 550)], # Derecha
            [(750, 550), (50, 550)], # Superior
            [(50, 550), (50, 50)]    # Izquierda
        ]
        
        # Comida
        self.food_pos = self._random_position()
        
    def _random_position(self):
        return (
            np.random.randint(100, SCREEN_WIDTH - 100),
            np.random.randint(100, SCREEN_HEIGHT - 100)
        )
    
    def reset_food(self):
        self.food_pos = self._random_position()
    
    def draw_environment(self):
        """Dibuja los elementos del entorno"""
        # Dibujar paredes
        for start, end in self.walls:
            arcade.draw_line(start[0], start[1], end[0], end[1], arcade.color.WHITE, 2)
        
        # Dibujar comida
        arcade.draw_circle_filled(*self.food_pos, 8, arcade.color.APPLE_GREEN)
    
    def check_food_collision(self, pos, radius):
        return np.linalg.norm(np.array(pos) - np.array(self.food_pos)) < radius + 8