# nymbot.py (versión headless)
import numpy as np
import random
import math
from genome import NymbotGenome
from config import MAX_RAY_DISTANCE, SCREEN_HEIGHT, SCREEN_WIDTH

class Nymbot:
    def __init__(self, walls, food_pos):
        self.position = self._random_position()
        self.body_angle = 0.0
        self.eye_angle = 0.0
        self.energy = 1000.0
        self.genome = NymbotGenome()
        
        # Entorno (ahora pasado como parámetro)
        self.walls = walls
        self.food_pos = food_pos
        
        # Visión
        self.fov = self.genome.fov
        self.vision_data = np.zeros(self.fov)
        self.ray_endpoints = [(0, 0)] * self.fov

    def update_vision(self):
        # Limpiar datos previos
        self.vision_data.fill(0.0)
        
        # Ángulos de los rayos (mismo cálculo)
        start_angle = self.eye_angle - math.radians(self.fov / 2)
        angle_step = math.radians(self.fov) / self.fov
        
        # Detectar colisiones para cada rayo
        for i in range(self.fov):
            ray_angle = start_angle + i * angle_step
            ray_end, hit_object = self.cast_ray(ray_angle)
            self.ray_endpoints[i] = ray_end
            
            # Si chocó con algo, registrar el tipo
            if hit_object == "food":
                self.vision_data[i] = 1.0
            elif hit_object == "wall":
                # dist = math.dist(self.position, ray_end)
                #self.vision_data[i] = max(0, 1.0 - dist/300)
                self.vision_data[i] = 0.0
        
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
        
        # Normalizar ángulos para quedar entre (0, 2*Pi)
        self.body_angle %= 2 * math.pi
        self.eye_angle %= 2 * math.pi

    def update_energy(self):
        """Actualizar energía y verificar si sigue vivo"""
        energy_cost = self.genome.complexity_cost()
        self.energy -= energy_cost
        return self.energy > 0

    def cast_ray(self, angle):
        """Lanza un rayo hasta chocar con un objeto o alcanzar distancia máxima"""
        direction = (math.cos(angle), math.sin(angle))
        current_pos = list(self.position)
        step_size = 5  # Tamaño del paso para el ray casting
        
        # Avanzar el rayo hasta MAX_RAY_DISTANCE
        for _ in range(0, MAX_RAY_DISTANCE, step_size):
            current_pos[0] += direction[0] * step_size
            current_pos[1] += direction[1] * step_size
            
            # Detección de comida (versión matemática)
            if math.dist(current_pos, self.food_pos) < 8:
                return (current_pos[0], current_pos[1]), "food"
            
            # Detección de paredes (versión matemática)
            if self.check_wall_collision(current_pos):
                return (current_pos[0], current_pos[1]), "wall"
        
        # Si no chocó con nada
        end_pos = (
            self.position[0] + direction[0] * MAX_RAY_DISTANCE,
            self.position[1] + direction[1] * MAX_RAY_DISTANCE
        )
        return end_pos, None

    def check_wall_collision(self, point):
        """Comprueba si un punto colisiona con alguna pared"""
        # Implementación matemática de detección de colisión con paredes
        for wall in self.walls:
            line_start, line_end = wall
            if self.point_near_line(point, line_start, line_end, 5):
                return True
        return False

    def point_near_line(self, point, line_start, line_end, threshold):
        """Comprueba si un punto está cerca de una línea"""
        # Vector de la línea
        line_vec = (line_end[0]-line_start[0], line_end[1]-line_start[1])
        line_len = math.sqrt(line_vec[0]**2 + line_vec[1]**2)
        
        # Vector del punto al inicio de la línea
        point_vec = (point[0]-line_start[0], point[1]-line_start[1])
        
        # Proyección del punto sobre la línea
        t = max(0, min(1, (point_vec[0]*line_vec[0] + point_vec[1]*line_vec[1]) / line_len**2))
        
        # Punto más cercano en la línea
        projection = (
            line_start[0] + t * line_vec[0],
            line_start[1] + t * line_vec[1]
        )
        
        # Distancia al punto
        dist = math.dist(point, projection)
        return dist <= threshold

    def check_food_collision(self, radius=10):
        # Versión matemática de detección de comida
        return math.dist(self.position, self.food_pos) < 8 + radius
    
    def _random_position(self):
        return [
            random.randint(100, SCREEN_WIDTH - 100),
            random.randint(100, SCREEN_HEIGHT - 100)
        ]