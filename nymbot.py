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
        self.vision_data = np.zeros(self.genome.vision_resolution)
    
    def update_vision(self, environment):
        """Versión simplificada para probar"""
        # Vector hacia la comida
        food_vec = np.array(environment.food_pos) - np.array(self.position)
        food_dist = np.linalg.norm(food_vec)
        food_dir = math.atan2(food_vec[1], food_vec[0])
        
        # Diferencia angular entre visión y comida
        angle_diff = abs((food_dir - self.eye_angle + math.pi) % (2 * math.pi) - math.pi)
        
        # Comprobar si está en el campo de visión
        in_fov = angle_diff < math.radians(self.genome.fov / 2)
        
        # Actualizar datos de visión
        if in_fov:
            intensity = 1.0 - min(food_dist / 300, 1.0)
            self.vision_data.fill(intensity)
        else:
            self.vision_data.fill(0.0)
    
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