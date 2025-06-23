# headless_simulator.py
import numpy as np
import math
from nymbot import Nymbot
from config import MAX_STEPS, FOOD_ENERGY, INITIAL_FOV, INITIAL_MAX_STEP, INITIAL_MAX_BODY_ROT, INITIAL_MAX_EYE_ROT

class HeadlessSimulator:
    def __init__(self, initial_conditions=None, random_seed=None):
        """
        Inicializa el simulador headless con condiciones iniciales específicas.
        
        Args:
            initial_conditions (dict): Estado inicial completo del sistema
            random_seed (int): Semilla para reproducibilidad
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Condiciones iniciales predeterminadas si no se proporcionan
        self.initial_conditions = initial_conditions or self.default_initial_conditions()
        
        # Configurar entorno
        self.walls = self.initial_conditions['walls']
        self.food_pos = self.initial_conditions['food_pos']
        
        # Crear nymbot con condiciones iniciales
        self.nymbot = self.create_nymbot()
        
        # Estado de simulación
        self.current_step = 0
        self.total_food_collected = 0
        self.history = []

    def default_initial_conditions(self):
        """Genera condiciones iniciales predeterminadas"""
        return {
            'nymbot': {
                'x': 400,
                'y': 300,
                'body_angle': 0.0,
                'eye_angle': 0.0,
                'energy': 100.0
            },
            'food_pos': (200, 150),
            'walls': [
                [(50, 50), (750, 50)],   # Inferior
                [(750, 50), (750, 550)],  # Derecha
                [(750, 550), (50, 550)],  # Superior
                [(50, 550), (50, 50)]     # Izquierda
            ],
            'genome_params': {
                'vision_resolution': INITIAL_FOV,
                'fov': INITIAL_FOV,
                'max_step_size': INITIAL_MAX_STEP,
                'max_body_rotation': INITIAL_MAX_BODY_ROT,
                'max_eye_rotation': INITIAL_MAX_EYE_ROT
            }
        }

    def create_nymbot(self):
        """Crea una instancia de Nymbot con las condiciones iniciales"""
        nymbot = Nymbot(
            x=self.initial_conditions['nymbot']['x'],
            y=self.initial_conditions['nymbot']['y'],
            walls=self.walls,
            food_pos=self.food_pos
        )
        
        # Configurar estado inicial
        nymbot.body_angle = self.initial_conditions['nymbot']['body_angle']
        nymbot.eye_angle = self.initial_conditions['nymbot']['eye_angle']
        nymbot.energy = self.initial_conditions['nymbot']['energy']
        
        # Configurar parámetros del genoma
        genome_params = self.initial_conditions['genome_params']
        nymbot.genome.vision_resolution = genome_params['vision_resolution']
        nymbot.genome.fov = genome_params['fov']
        nymbot.genome.max_step_size = genome_params['max_step_size']
        nymbot.genome.max_body_rotation = genome_params['max_body_rotation']
        nymbot.genome.max_eye_rotation = genome_params['max_eye_rotation']
        
        return nymbot

    def run_step(self, action=None):
        """
        Ejecuta un único paso de simulación.
        
        Args:
            action (array, optional): Acción a ejecutar. Si es None, se usa la red neuronal.
        
        Returns:
            dict: Estado actual del sistema
        """
        # Actualizar visión
        vision_data = self.nymbot.update_vision()
        
        # Obtener acción si no se proporciona
        if action is None:
            action = self.nymbot.genome.brain.get_action(vision_data)
        
        # Mover nymbot
        self.nymbot.move(action)
        
        # Actualizar energía
        is_alive = self.nymbot.update_energy()
        
        # Verificar colisión con comida
        food_collected = 0
        if self.nymbot.check_food_collision():
            self.nymbot.energy += FOOD_ENERGY
            food_collected = 1
            self.total_food_collected += 1
            # Reposicionar comida
            self.food_pos = (
                np.random.randint(100, 700),
                np.random.randint(100, 500)
            )
        
        # Guardar estado actual
        state = {
            'step': self.current_step,
            'position': tuple(self.nymbot.position),
            'body_angle': self.nymbot.body_angle,
            'eye_angle': self.nymbot.eye_angle,
            'energy': self.nymbot.energy,
            'vision': vision_data.copy(),
            'food_pos': tuple(self.food_pos),
            'food_collected': food_collected,
            'is_alive': is_alive
        }
        self.history.append(state)
        
        # Avanzar contador
        self.current_step += 1
        
        return state, not is_alive

    def run_episode(self, max_steps=MAX_STEPS):
        """
        Ejecuta un episodio completo de simulación.
        
        Args:
            max_steps (int): Número máximo de pasos
        
        Returns:
            dict: Resultados del episodio
        """
        self.reset()
        
        done = False
        while self.current_step < max_steps and not done:
            _, done = self.run_step()
        
        return {
            'total_steps': self.current_step,
            'final_energy': self.nymbot.energy,
            'food_collected': self.total_food_collected,
            'history': self.history
        }

    def reset(self):
        """Reinicia la simulación a las condiciones iniciales"""
        self.nymbot = self.create_nymbot()
        self.food_pos = self.initial_conditions['food_pos']
        self.current_step = 0
        self.total_food_collected = 0
        self.history = []

    def get_current_state(self):
        """Devuelve el estado actual del simulador"""
        return {
            'nymbot': {
                'position': tuple(self.nymbot.position),
                'body_angle': self.nymbot.body_angle,
                'eye_angle': self.nymbot.eye_angle,
                'energy': self.nymbot.energy
            },
            'food_pos': tuple(self.food_pos),
            'step': self.current_step
        }

    def save_snapshot(self, file_path):
        """Guarda un snapshot completo del estado actual"""
        snapshot = {
            'initial_conditions': self.initial_conditions,
            'current_state': self.get_current_state(),
            'history': self.history,
            'total_food_collected': self.total_food_collected,
            # Agregar pesos de la red neuronal si es necesario
        }
        np.save(file_path, snapshot, allow_pickle=True)

    def load_snapshot(self, file_path):
        """Carga un snapshot guardado"""
        snapshot = np.load(file_path, allow_pickle=True).item()
        self.initial_conditions = snapshot['initial_conditions']
        self.reset()
        # Restaurar estado desde snapshot
        # (Implementación detallada dependerá de la estructura de datos)