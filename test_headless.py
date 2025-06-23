# test_headless.py
import numpy as np
import math
from headless_simulator import HeadlessSimulator
from visual_simulator import Simulation  # Asumiendo que el visual está en main.py

def run_comparison_test():
    # Configuración inicial común
    config = {
        'nymbot': {'x': 400, 'y': 300, 'body_angle': 0.0, 'eye_angle': 0.5, 'energy': 100},
        'food_pos': (200, 150),
        'walls': [...]  # Mismas paredes
    }
    
    # Ejecutar simulador headless
    headless = HeadlessSimulator(initial_conditions=config, random_seed=42)
    headless_results = headless.run_episode(max_steps=100)
    
    # Ejecutar simulador visual
    visual_sim = Simulation()  # Necesita ser modificado para aceptar config inicial
    visual_sim.set_initial_conditions(config)
    visual_results = visual_sim.run_episode(max_steps=100)
    
    # Comparar resultados
    for step in range(100):
        headless_state = headless_results['history'][step]
        visual_state = visual_results['history'][step]
        
        # Verificar posición
        assert np.allclose(headless_state['position'], visual_state['position'], atol=1e-5)
        
        # Verificar ángulos
        assert math.isclose(headless_state['body_angle'], visual_state['body_angle'], abs_tol=1e-5)
        assert math.isclose(headless_state['eye_angle'], visual_state['eye_angle'], abs_tol=1e-5)
        
        # Verificar energía
        assert math.isclose(headless_state['energy'], visual_state['energy'], abs_tol=1e-5)
    
    print("¡Prueba de validación exitosa! Ambos simuladores producen resultados idénticos.")

if __name__ == "__main__":
    run_comparison_test()