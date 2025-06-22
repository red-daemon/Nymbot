# main.py
import arcade
import math
import numpy as np
import random
from nymbot import Nymbot
from config import *

class Simulation(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Nymbot Simulator")
        arcade.set_background_color(BACKGROUND_COLOR)
        
        # Entorno
        self.walls = [
            [(50, 50), (750, 50)],   # Inferior
            [(750, 50), (750, 550)], # Derecha
            [(750, 550), (50, 550)], # Superior
            [(50, 550), (50, 50)]    # Izquierda
        ]
        self.food_pos = self._random_position()
        
        # Nymbot
        self.nymbot = Nymbot(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.total_steps = 0
        self.current_episode = 0
        
        # Texto
        self.info_text = arcade.Text(
            text="",
            x=10,
            y=SCREEN_HEIGHT - 30,
            color=arcade.color.WHITE,
            font_size=14
        )
    
    def _random_position(self):
        return (
            random.randint(100, SCREEN_WIDTH - 100),
            random.randint(100, SCREEN_HEIGHT - 100)
        )
    
    def reset_food(self):
        self.food_pos = self._random_position()
    
    def check_food_collision(self, pos, radius):
        return math.sqrt((pos[0] - self.food_pos[0])**2 + 
                         (pos[1] - self.food_pos[1])**2) < radius + 8
    
    def on_draw(self):
        """Método de dibujo principal"""
        # Limpiar completamente la pantalla
        self.clear()
        
        # Dibujar paredes
        for start, end in self.walls:
            arcade.draw_line(start[0], start[1], end[0], end[1], arcade.color.WHITE, 2)
        
        # Dibujar comida
        arcade.draw_circle_filled(*self.food_pos, 8, arcade.color.APPLE_GREEN)
        
        # Dibujar nymbot
        arcade.draw_circle_filled(*self.nymbot.position, 10, arcade.color.BLUE)
        
        # Dibujar dirección del cuerpo
        end_x = self.nymbot.position[0] + 20 * math.cos(self.nymbot.body_angle)
        end_y = self.nymbot.position[1] + 20 * math.sin(self.nymbot.body_angle)
        arcade.draw_line(*self.nymbot.position, end_x, end_y, arcade.color.RED, 2)
        
        # Dibujar rayos de visión
        for i, end_point in enumerate(self.nymbot.ray_endpoints):
            # Color del rayo según lo detectado
            ray_color = self.nymbot.ray_colors[i]
            arcade.draw_line(
                self.nymbot.position[0], self.nymbot.position[1],
                end_point[0], end_point[1],
                ray_color,
                1
            )
        
        # Dibujar barra de visión en la parte inferior
        self.draw_vision_bar()
        
        # Actualizar y dibujar texto
        self.info_text.text = f"Episodio: {self.current_episode} | Pasos: {self.total_steps} | Energía: {self.nymbot.energy:.1f}"
        self.info_text.draw()
    
    def draw_vision_bar(self):
        """Dibuja una representación de lo que el nymbot está viendo"""
        bar_height = 50
        bar_y = 10  # Parte inferior de la pantalla
        ray_count = self.nymbot.vision_resolution
        ray_width = SCREEN_WIDTH / ray_count
        
        for i in range(ray_count):
            # Calcular intensidad (0-255)
            intensity = int(self.nymbot.vision_data[i] * 255)
            
            # Crear color basado en lo detectado
            if self.nymbot.ray_colors[i] == (0, 255, 0):  # Comida
                color = (0, intensity, 0)
            else:  # Otros objetos (por ahora gris)
                color = (intensity, intensity, intensity)
            
            # Calcular posición del rectángulo
            x = i * ray_width
            y = bar_y
            width = ray_width
            height = bar_height
            
            # Dibujar segmento de visión con draw_rect_filled
            arcade.draw_rect_filled(
                rect=arcade.rect.XYWH(x, y, width, height),
                color=color
            )
    
    def on_update(self, delta_time):
        """Lógica de actualización del juego"""
        # Actualizar visión
        self.nymbot.update_vision(self)
        
        # Obtener acción del cerebro (array de 3 valores)
        action_array = self.nymbot.genome.brain.get_action(self.nymbot.vision_data)
        
        # Mover nymbot con la acción continua
        self.nymbot.move(action_array)
        
        # Actualizar energía
        is_alive = self.nymbot.update_energy()
        
        # Comprobar colisión con comida
        if self.check_food_collision(self.nymbot.position, 10):
            self.nymbot.energy += FOOD_ENERGY
            self.reset_food()
        
        # Comprobar fin de episodio
        self.total_steps += 1
        if not is_alive or self.total_steps >= MAX_STEPS:
            self.reset_episode()
    
    def reset_episode(self):
        # Posición y orientación aleatorias
        self.nymbot.position = [
            random.randint(100, SCREEN_WIDTH - 100),
            random.randint(100, SCREEN_HEIGHT - 100)
        ]
        self.nymbot.body_angle = random.uniform(0, 2 * math.pi)
        self.nymbot.eye_angle = random.uniform(0, 2 * math.pi)
        self.nymbot.energy = 100.0
        self.reset_food()
        self.total_steps = 0
        self.current_episode += 1

def main():
    sim = Simulation()
    arcade.run()

if __name__ == "__main__":
    main()