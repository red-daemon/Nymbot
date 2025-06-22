# config.py
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (10, 10, 40)  # Azul oscuro

# Parámetros de simulación
MAX_STEPS = 1000
FPS = 60

# Parámetros iniciales nymbot
INITIAL_MAX_STEP = 0.5
INITIAL_MAX_BODY_ROT = 0.1
INITIAL_MAX_EYE_ROT = 0.05
INITIAL_FOV = 60  # Grados


# INITIAL_VISION_RESOLUTION = 64
# INITIAL_FOV = 120
FOOD_ENERGY = 15.0
BASE_ENERGY_COST = 0.01
MAX_RAY_DISTANCE = 1000  # Suficiente para alcanzar cualquier pared
FOV_ENERGY_COST_PER_DEGREE = 0.001  # Costo por grado de FOV

# Parámetros de visión