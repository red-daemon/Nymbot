# test_consistency.py
from headless_simulator import HeadlessSimulator
from visual_simulator import Simulation
import math

def test_single_step():
    # Configuración común
    config = {
        'genome_params': {
            'fov': 90,
            'max_step_size': 0.6,
            'max_body_rotation': 0.15,
            'max_eye_rotation': 0.1
        }
    }
    
    # Headless - Paso 1
    headless = HeadlessSimulator(initial_conditions=config, random_seed=42)
    headless_state1, _ = headless.run_step()
    
    # Visual - Paso 1
    visual = Simulation(initial_conditions=config)
    visual.nymbot.position = list(headless.nymbot.position)  # Misma posición inicial
    visual.nymbot.body_angle = headless.nymbot.body_angle
    visual.nymbot.eye_angle = headless.nymbot.eye_angle
    visual.food_pos = headless.food_pos
    visual.on_update(1/60)  # Simular un paso
    
    # Comparar
    assert math.isclose(visual.nymbot.position[0], headless_state1['position'][0], abs_tol=0.001)
    assert math.isclose(visual.nymbot.position[1], headless_state1['position'][1], abs_tol=0.001)
    assert math.isclose(visual.nymbot.body_angle, headless_state1['body_angle'], abs_tol=0.001)
    assert math.isclose(visual.nymbot.eye_angle, headless_state1['eye_angle'], abs_tol=0.001)
    assert math.isclose(visual.nymbot.energy, headless_state1['energy'], abs_tol=0.001)
    
    print("¡Prueba de consistencia exitosa!")

if __name__ == "__main__":
    test_single_step()