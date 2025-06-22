# main.py
import arcade
import math
# import numpy as np
import random
from nymbot import Nymbot
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, FOOD_ENERGY, MAX_STEPS

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
        
        # Dibujar dirección de la visión (línea central)
        end_eye_x = self.nymbot.position[0] + 25 * math.cos(self.nymbot.eye_angle)
        end_eye_y = self.nymbot.position[1] + 25 * math.sin(self.nymbot.eye_angle)
        arcade.draw_line(*self.nymbot.position, end_eye_x, end_eye_y, arcade.color.CYAN, 2)
        
        # Dibujar el cono de visión completo
        self.draw_vision_cone()
        
        # Dibujar barra de visión en la parte inferior
        self.draw_vision_bar()
        
        # Actualizar y dibujar texto
        self.info_text.text = f"Episodio: {self.current_episode} | Pasos: {self.total_steps} | Energía: {self.nymbot.energy:.1f} | FOV: {self.nymbot.genome.fov:.1f}°"
        self.info_text.draw()
    
    def draw_vision_cone(self):
        """Dibuja el cono de visión completo"""
        if not hasattr(self.nymbot, 'ray_endpoints') or len(self.nymbot.ray_endpoints) < 2:
            return
        
        # Crear puntos para el cono: posición del nymbot + puntos finales de los rayos
        points = [(self.nymbot.position[0], self.nymbot.position[1])]
        points.extend(self.nymbot.ray_endpoints)
        
        # Dibujar cono semitransparente
        arcade.draw_polygon_filled(points, (173, 216, 230, 50))  # Azul claro con transparencia
        
        # Dibujar bordes del cono
        arcade.draw_line(
            self.nymbot.position[0], self.nymbot.position[1],
            self.nymbot.ray_endpoints[0][0], self.nymbot.ray_endpoints[0][1],
            arcade.color.DARK_BLUE, 1
        )
        arcade.draw_line(
            self.nymbot.position[0], self.nymbot.position[1],
            self.nymbot.ray_endpoints[-1][0], self.nymbot.ray_endpoints[-1][1],
            arcade.color.DARK_BLUE, 1
        )
    
    def draw_vision_bar(self):
        """Dibuja la barra de visión en la parte inferior"""
        bar_y = 10
        pad_x = 10
        bar_height = 28 # (50 - 20)/2
        ray_count = self.nymbot.vision_resolution
        ray_width = (SCREEN_WIDTH - 2*pad_x) / ray_count
        
        for i in range(ray_count):
            intensity = int(self.nymbot.vision_data[i] * 255)
            
            if self.nymbot.ray_colors[i] == (0, 255, 0):  # Comida
                color = (0, intensity, 0)
            elif self.nymbot.ray_colors[i] == (255, 0, 0):  # Pared
                color = (intensity, 0, 0)
            else:
                color = (intensity, intensity, intensity)
            
            rect_cell= arcade.rect.LBWH(pad_x + i * ray_width, bar_y, ray_width, bar_height)
            
            arcade.draw_rect_filled(
                rect=rect_cell,
                color=color
            )
            
            arcade.draw_rect_outline(
                rect=rect_cell,
                color=(255, 255, 255)
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

        # Mostrar FOV actual en el texto
        self.info_text.text = (f"Episodio: {self.current_episode} | "
                              f"Pasos: {self.total_steps} | "
                              f"Energía: {self.nymbot.energy:.1f} | "
                              f"FOV: {self.nymbot.genome.fov:.1f}°")
    
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