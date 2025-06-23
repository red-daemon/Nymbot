# genome.py
import random
import numpy as np
import torch
from brain import NymbotBrain
from config import INITIAL_FOV, INITIAL_MAX_BODY_ROT, INITIAL_MAX_EYE_ROT, INITIAL_MAX_STEP, FOV_ENERGY_COST_PER_DEGREE, BASE_ENERGY_COST

class NymbotGenome:
    def __init__(self):
        # Parámetros sensoriales
        # self.vision_resolution = INITIAL_FOV
        self.fov = INITIAL_FOV
        
        # Parámetros motores
        self.max_step_size = INITIAL_MAX_STEP
        self.max_body_rotation = INITIAL_MAX_BODY_ROT
        self.max_eye_rotation = INITIAL_MAX_EYE_ROT
        
        # Red neuronal
        self.brain_architecture = [32, 16]
        self.brain = None

        self.fov = INITIAL_FOV
        
        # Inicializar cerebro
        self.initialize_brain()  # Esto llama al método de abajo
    
    def initialize_brain(self):
        input_size = self.fov
        # Ahora solo pasamos input_size y brain_architecture
        self.brain = NymbotBrain(input_size, self.brain_architecture)

    def mutate(self, mutation_rate=0.1):
        # Mutar parámetros sensoriales/motores
        params = [
            'vision_resolution', 'fov', 
            'max_step_size', 'max_body_rotation', 'max_eye_rotation'
        ]
        
        for param in params:
            if random.random() < mutation_rate:
                current = getattr(self, param)
                mutated = current * random.uniform(0.8, 1.2)
                setattr(self, param, type(current)(mutated))
        
        # Mutar pesos de la red neuronal
        if random.random() < mutation_rate:
            state_dict = self.brain.state_dict()
            for key in state_dict:
                noise = torch.randn_like(state_dict[key]) * 0.1
                state_dict[key] += noise
            self.brain.load_state_dict(state_dict)

        # Mutar FOV
        if random.random() < mutation_rate:
            self.fov = np.clip(self.fov * random.uniform(0.9, 1.1), 10, 360)
    
    def complexity_cost(self):  # XXX Cambiar para que el costo de la energia sea correspondiente a su uso y no sus rangos
        """Calcula el costo energético de la complejidad"""
        fov_cost = 0.0001 * self.fov
        step_cost = 0.005 * self.max_step_size
        rot_cost = 0.003 * (self.max_body_rotation + self.max_eye_rotation)
        
        # Costo cerebral (simplificado)
        brain_cost = 0.0001 * sum(self.brain_architecture)

        # Costo por FOV (más amplio = más costoso)
        fov_cost = FOV_ENERGY_COST_PER_DEGREE * self.fov
        
        return BASE_ENERGY_COST + step_cost + rot_cost + brain_cost + fov_cost