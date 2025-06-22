import numpy as np
import math
from genome import NymbotGenome

class Nymbot:
    def __init__(self, x, y):
        self.position = [x, y]
        self.body_angle = 0.0
        self.eye_angle = 0.0
        self.energy = 100.0
        self.genome = NymbotGenome()
        
        # Datos de visión por rayo
        self.vision_resolution = self.genome.vision_resolution
        self.vision_data = np.zeros(self.vision_resolution)  # Intensidad
        self.ray_colors = [(0, 0, 0)] * self.vision_resolution  # Color RGB
        
        # Solo almacenamos los puntos finales de los rayos extremos
        self.left_ray_end = (0, 0)
        self.right_ray_end = (0, 0)
    
    def update_vision(self, environment):
        """Simulación simplificada que detecta comida y paredes"""
        # Limpiar datos previos
        self.vision_data.fill(0.0)
        self.ray_colors = [(0, 0, 0)] * self.vision_resolution
        
        # Vector hacia la comida
        food_vec = np.array(environment.food_pos) - np.array(self.position)
        food_dist = np.linalg.norm(food_vec)
        food_dir = math.atan2(food_vec[1], food_vec[0])
        
        # Ángulo de inicio y paso
        start_angle = self.eye_angle - math.radians(self.genome.fov / 2)
        end_angle = self.eye_angle + math.radians(self.genome.fov / 2)
        angle_step = math.radians(self.genome.fov) / self.vision_resolution
        
        # Calcular puntos finales de los rayos extremos (siempre visibles)
        max_dist = 300  # Distancia máxima del rayo
        
        # Rayo izquierdo (inicio del FOV)
        self.left_ray_end = (
            self.position[0] + max_dist * math.cos(start_angle),
            self.position[1] + max_dist * math.sin(start_angle)
        )
        
        # Rayo derecho (fin del FOV)
        self.right_ray_end = (
            self.position[0] + max_dist * math.cos(end_angle),
            self.position[1] + max_dist * math.sin(end_angle)
        )
        
        # Simular rayos para la barra de visión
        for i in range(self.vision_resolution):
            ray_angle = start_angle + i * angle_step
            
            # Comprobar si este rayo apunta a la comida
            angle_diff = abs((food_dir - ray_angle + math.pi) % (2 * math.pi) - math.pi)
            if angle_diff < math.radians(5):  # Tolerancia de 5 grados
                dist_factor = 1.0 - min(food_dist / max_dist, 1.0)
                self.vision_data[i] = dist_factor
                self.ray_colors[i] = (0, 255, 0)  # Verde para comida
        
        return self.vision_data
    
    def move(self, action):
        """Mover según la acción seleccionada (ahora 3 valores continuos)"""
        # action[0]: movimiento (adelante/atrás)
        step = action[0] * self.genome.max_step_size
        self.position[0] += step * math.cos(self.body_angle)
        self.position[1] += step * math.sin(self.body_angle)
        
        # action[1]: rotación del cuerpo
        self.body_angle += action[1] * self.genome.max_body_rotation
        
        # action[2]: rotación del ojo
        self.eye_angle += action[2] * self.genome.max_eye_rotation
        
        # Normalizar ángulos
        self.body_angle %= 2 * math.pi
        self.eye_angle %= 2 * math.pi
    
    def update_energy(self):
        """Actualizar energía y verificar si sigue vivo"""
        energy_cost = self.genome.complexity_cost()
        self.energy -= energy_cost
        return self.energy > 0