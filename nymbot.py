# nymbot.py
import numpy as np
import math
from genome import NymbotGenome
from config import MAX_RAY_DISTANCE

class Nymbot:
    def __init__(self, x, y):
        self.position = [x, y]
        self.body_angle = 0.0
        self.eye_angle = 0.0
        self.energy = 100.0
        self.genome = NymbotGenome()
        
        # Datos de visión
        self.vision_resolution = self.genome.vision_resolution
        self.vision_data = np.zeros(self.vision_resolution)
        self.ray_colors = [(0, 0, 0)] * self.vision_resolution
        self.ray_endpoints = [(0, 0)] * self.vision_resolution
    
    def update_vision(self, environment):
        # Limpiar datos previos
        self.vision_data.fill(0.0)
        self.ray_colors = [(0, 0, 0)] * self.vision_resolution
        
        # Ángulos de los rayos
        start_angle = self.eye_angle - math.radians(self.genome.fov / 2)
        angle_step = math.radians(self.genome.fov) / self.vision_resolution
        
        # Detectar colisiones para cada rayo
        for i in range(self.vision_resolution):
            ray_angle = start_angle + i * angle_step
            ray_end, hit_object = self.cast_ray(environment, ray_angle)
            self.ray_endpoints[i] = ray_end
            
            # Si chocó con algo, registrar el tipo
            if hit_object == "food":
                self.vision_data[i] = 1.0  # Máxima intensidad
                self.ray_colors[i] = (0, 255, 0)  # Verde para comida
            elif hit_object == "wall":
                # Calcular distancia (para intensidad)
                dist = math.sqrt((self.position[0]-ray_end[0])**2 + 
                                (self.position[1]-ray_end[1])**2)
                self.vision_data[i] = max(0, 1.0 - dist/300)  # Más cerca = más intenso
                self.ray_colors[i] = (255, 0, 0)  # Rojo para paredes
        
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
    
    def cast_ray(self, environment, angle):
        """Lanza un rayo hasta chocar con un objeto o alcanzar distancia máxima"""
        direction = (math.cos(angle), math.sin(angle))
        current_pos = list(self.position)
        step_size = 5  # Tamaño del paso para el ray casting
        
        # Avanzar el rayo hasta MAX_RAY_DISTANCE
        for _ in range(0, MAX_RAY_DISTANCE, step_size):
            current_pos[0] += direction[0] * step_size
            current_pos[1] += direction[1] * step_size
            
            # Comprobar colisión con comida
            if environment.check_food_collision(current_pos, 0):
                return (current_pos[0], current_pos[1]), "food"
            
            # Comprobar colisión con paredes
            if self.check_wall_collision(environment, current_pos):
                return (current_pos[0], current_pos[1]), "wall"
        
        # Si no chocó con nada, devolver punto máximo
        end_pos = (
            self.position[0] + direction[0] * MAX_RAY_DISTANCE,
            self.position[1] + direction[1] * MAX_RAY_DISTANCE
        )
        return end_pos, None
    
    def check_wall_collision(self, environment, point):
        """Comprueba si un punto colisiona con alguna pared"""
        for wall in environment.walls:
            if self.point_near_line(point, wall[0], wall[1], 5):
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
        dist = math.sqrt((point[0]-projection[0])**2 + (point[1]-projection[1])**2)
        return dist <= threshold