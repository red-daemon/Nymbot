# headless_simulator.py
import math
import random
from nymbot import Nymbot
from config import MAX_STEPS, FOOD_ENERGY, INITIAL_FOV, INITIAL_MAX_STEP, INITIAL_MAX_BODY_ROT, INITIAL_MAX_EYE_ROT

class HeadlessSimulator:
    def __init__(self, initial_conditions=None, random_seed=None):
        if random_seed is not None:
            random.seed(random_seed)
        
        # Configurar paredes fijas (como en visual_simulator)
        self.walls = [
            [(50, 50), (750, 50)],   # Inferior
            [(750, 50), (750, 550)],  # Derecha
            [(750, 550), (50, 550)],  # Superior
            [(50, 550), (50, 50)]     # Izquierda
        ]
        
        # Inicializar condiciones
        self.initial_conditions = initial_conditions or {}
        self.reset_simulation()
        
        # Estado de simulación
        self.current_step = 0
        self.current_episode = 0
        self.total_food_collected = 0

    def reset_simulation(self):
        """Inicializa o reinicia la simulación"""
        # Posición aleatoria de comida
        self.food_pos = self._random_position()
        
        # Crear nymbot con posición aleatoria
        self.nymbot = Nymbot(self.walls, self.food_pos)
        
        # Aplicar parámetros personalizados si existen
        if 'genome_params' in self.initial_conditions:
            genome_params = self.initial_conditions['genome_params']
            self.nymbot.genome.fov = genome_params.get('fov', INITIAL_FOV)
            self.nymbot.genome.max_step_size = genome_params.get('max_step_size', INITIAL_MAX_STEP)
            self.nymbot.genome.max_body_rotation = genome_params.get('max_body_rotation', INITIAL_MAX_BODY_ROT)
            self.nymbot.genome.max_eye_rotation = genome_params.get('max_eye_rotation', INITIAL_MAX_EYE_ROT)
        
        # Resetear contadores
        self.current_step = 0
        self.total_food_collected = 0

    def _random_position(self):
        """Genera posición aleatoria dentro del área válida"""
        return [
            random.randint(100, 700),  # SCREEN_WIDTH = 800
            random.randint(100, 500)   # SCREEN_HEIGHT = 600
        ]

    def run_step(self):
        """Ejecuta un único paso de simulación"""
        # Actualizar visión
        self.nymbot.update_vision()
        
        # Obtener acción del cerebro
        action = self.nymbot.genome.brain.get_action(self.nymbot.vision_data)
        
        # Mover nymbot
        self.nymbot.move(action)
        
        # Actualizar energía
        is_alive = self.nymbot.update_energy()
        
        # Verificar colisión con comida
        if self.check_food_collision():
            self.nymbot.energy += FOOD_ENERGY
            self.total_food_collected += 1
            self.food_pos = self._random_position()
        
        # Avanzar contador
        self.current_step += 1
        
        # Determinar si el episodio ha terminado
        done = not is_alive or self.current_step >= MAX_STEPS
        
        # Guardar estado actual
        state = {
            'step': self.current_step,
            'position': tuple(self.nymbot.position),
            'body_angle': self.nymbot.body_angle,
            'eye_angle': self.nymbot.eye_angle,
            'energy': self.nymbot.energy,
            'food_pos': self.food_pos,
            'done': done
        }
        
        return state, done

    def run_episode(self, max_steps=MAX_STEPS):
        """Ejecuta un episodio completo"""
        self.reset_simulation()
        
        history = []
        done = False
        
        while not done and self.current_step < max_steps:
            state, done = self.run_step()
            history.append(state)
        
        return {
            'total_steps': self.current_step,
            'final_energy': self.nymbot.energy,
            'food_collected': self.total_food_collected,
            'history': history
        }

    def check_food_collision(self):
        """Versión simplificada de detección de comida"""
        return math.dist(self.nymbot.position, self.food_pos) < 18  # Radio 10 + 8

    def reset_episode(self):
        """Reinicia el episodio manteniendo configuración"""
        self.nymbot.position = self._random_position()
        self.nymbot.body_angle = random.uniform(0, 2 * math.pi)
        self.nymbot.eye_angle = random.uniform(0, 2 * math.pi)
        self.nymbot.energy = 100.0
        self.food_pos = self._random_position()
        self.current_step = 0
        self.total_food_collected = 0
        self.current_episode += 1

    def get_current_state(self):
        """Devuelve el estado actual del simulador"""
        return {
            'nymbot': {
                'position': tuple(self.nymbot.position),
                'body_angle': self.nymbot.body_angle,
                'eye_angle': self.nymbot.eye_angle,
                'energy': self.nymbot.energy
            },
            'food_pos': self.food_pos,
            'step': self.current_step
        }
    
if __name__ == "__main__":
    # Ejemplo de uso
    # Configuración personalizada
    config = {
        'genome_params': {
            # 'vision_resolution': 64,
            'fov': 60,
            'max_step_size': 0.50,
            'max_body_rotation': 0.1,
            'max_eye_rotation': 0.05
        }
    }

    # Crear simulador
    simulator = HeadlessSimulator(initial_conditions=config, random_seed=69)

    # Ejecutar un episodio completo
    results = simulator.run_episode()
    print(f"Episodio terminado en {results['total_steps']} pasos")
    print(f"Energía final: {results['final_energy']}")
    print(f"Comida recolectada: {results['food_collected']}")

    # Ejecutar paso a paso
    simulator.reset_episode()
    for i in range(100):
        print(i)
        state, done = simulator.run_step()
        if done:
            break