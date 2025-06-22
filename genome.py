# genome.py
import random
import numpy as np
import torch
from brain import NymbotBrain
from config import *

class NymbotGenome:
    def __init__(self):
        # Parámetros sensoriales
        self.vision_resolution = INITIAL_VISION_RESOLUTION
        self.fov = INITIAL_FOV
        
        # Parámetros motores
        self.max_step_size = INITIAL_MAX_STEP
        self.max_body_rotation = INITIAL_MAX_BODY_ROT
        self.max_eye_rotation = INITIAL_MAX_EYE_ROT
        
        # Red neuronal
        self.brain_architecture = [32, 16]
        self.brain = None
        
        # Inicializar cerebro
        self.initialize_brain()  # Esto llama al método de abajo
    
    def initialize_brain(self):
        input_size = self.vision_resolution
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
    
    def complexity_cost(self):
        """Calcula el costo energético de la complejidad"""
        vision_cost = 0.002 * self.vision_resolution
        fov_cost = 0.0001 * self.fov
        step_cost = 0.005 * self.max_step_size
        rot_cost = 0.003 * (self.max_body_rotation + self.max_eye_rotation)
        
        # Costo cerebral (simplificado)
        brain_cost = 0.0001 * sum(self.brain_architecture)
        
        return BASE_ENERGY_COST + vision_cost + fov_cost + step_cost + rot_cost + brain_cost