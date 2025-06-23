# visual_simulator.py (versión modificada)
import arcade
import math
import random
# import numpy as np
from nymbot import Nymbot
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BACKGROUND_COLOR, FOOD_ENERGY, MAX_STEPS

class Simulation(arcade.Window):
    def __init__(self, initial_conditions=None, playback_mode=False, playback_snapshot=None):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Nymbot Simulator")
        arcade.set_background_color(BACKGROUND_COLOR)
        
        # Modo de reproducción (carga un estado guardado)
        self.playback_mode = playback_mode
        self.playback_snapshot = playback_snapshot
        
        # Inicializar con condiciones iniciales dadas o por defecto
        self.initial_conditions = initial_conditions
        self.reset_simulation()
        
        # Texto
        self.info_text = arcade.Text(
            text="",
            x=10,
            y=SCREEN_HEIGHT - 30,
            color=arcade.color.WHITE,
            font_size=14
        )
    
    def reset_simulation(self):
        """Inicializa o reinicia la simulación con condiciones iniciales."""
        # Paredes (si no se proporcionan, usar las por defecto)
        # if self.initial_conditions and 'walls' in self.initial_conditions:
        #     self.walls = self.initial_conditions['walls']
        # else:
        self.walls = [
            [(50, 50), (750, 50)],   # Inferior
            [(750, 50), (750, 550)], # Derecha
            [(750, 550), (50, 550)], # Superior
            [(50, 550), (50, 50)]    # Izquierda
        ]
        
        # Comida
        # if self.initial_conditions and 'food_pos' in self.initial_conditions:
        #     self.food_pos = self.initial_conditions['food_pos']
        # else:
        self.food_pos = self._random_position()
        
        # Nymbot
        if self.initial_conditions and 'nymbot' in self.initial_conditions:
            pass
            # nymbot_initial = self.initial_conditions['nymbot']
            # self.nymbot = Nymbot(
            #     # nymbot_initial['x'],
            #     # nymbot_initial['y'],
            #     self.walls,
            #     self.food_pos
            # )
            # # Configurar estado inicial del nymbot
            # self.nymbot.body_angle = nymbot_initial.get('body_angle', 0.0)
            # self.nymbot.eye_angle = nymbot_initial.get('eye_angle', 0.0)
            # self.nymbot.energy = nymbot_initial.get('energy', 100.0)
            
            # Configurar parámetros del genoma si se proporcionan
            if 'genome_params' in self.initial_conditions:
                genome_params = self.initial_conditions['genome_params']
                self.nymbot.genome.vision_resolution = genome_params['vision_resolution']
                self.nymbot.genome.fov = genome_params['fov']
                self.nymbot.genome.max_step_size = genome_params['max_step_size']
                self.nymbot.genome.max_body_rotation = genome_params['max_body_rotation']
                self.nymbot.genome.max_eye_rotation = genome_params['max_eye_rotation']
        else:
            # self.nymbot = Nymbot(
            # SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.walls, self.food_pos)
            self.nymbot = Nymbot(self.walls, self.food_pos)
        
        # Si estamos en modo reproducción, cargamos el snapshot
        if self.playback_mode and self.playback_snapshot:
            self.load_playback_snapshot(self.playback_snapshot)
        
        self.total_steps = 0
        self.current_episode = 0
        self.total_food_collected = 0
    
    def _random_position(self):
        return (
            random.randint(100, SCREEN_WIDTH - 100),
            random.randint(100, SCREEN_HEIGHT - 100)
        )
    
    def reset_food(self):
        self.food_pos = self._random_position()
    
    def check_food_collision(self, pos, radius):
        return math.sqrt((pos[0] - self.food_pos[0])**2 + 
                         (pos[1] - self.food_pos[1])**2) < radius + 8
    
    def on_draw(self):
        """Método de dibujo principal"""
        self.clear()
        
        # Dibujar paredes
        for start, end in self.walls:
            arcade.draw_line(start[0], start[1], end[0], end[1], arcade.color.WHITE, 2)
        
        # Dibujar comida
        arcade.draw_circle_filled(*self.food_pos, 8, arcade.color.APPLE_GREEN)
        
        # Dibujar nymbot
        arcade.draw_circle_filled(*self.nymbot.position, 10, arcade.color.BLUE)
        
        # Dibujar dirección del cuerpo
        end_x = self.nymbot.position[0] + 20 * math.cos(self.nymbot.body_angle)
        end_y = self.nymbot.position[1] + 20 * math.sin(self.nymbot.body_angle)
        arcade.draw_line(*self.nymbot.position, end_x, end_y, arcade.color.RED, 2)
        
        # Dibujar dirección de la visión (línea central)
        end_eye_x = self.nymbot.position[0] + 25 * math.cos(self.nymbot.eye_angle)
        end_eye_y = self.nymbot.position[1] + 25 * math.sin(self.nymbot.eye_angle)
        arcade.draw_line(*self.nymbot.position, end_eye_x, end_eye_y, arcade.color.CYAN, 2)
        
        # Dibujar el cono de visión completo
        self.draw_vision_cone()
        
        # Dibujar barra de visión en la parte inferior
        self.draw_vision_bar()
        
        # Actualizar y dibujar texto
        self.info_text.text = f"Episodio: {self.current_episode} | Pasos: {self.total_steps} | Energía: {self.nymbot.energy:.1f} | FOV: {self.nymbot.genome.fov:.1f}°"
        self.info_text.draw()
    
    def draw_vision_cone(self):
        """Dibuja el cono de visión completo"""
        if not hasattr(self.nymbot, 'ray_endpoints') or len(self.nymbot.ray_endpoints) < 2:
            return
        
        # Crear puntos para el cono: posición del nymbot + puntos finales de los rayos
        points = [(self.nymbot.position[0], self.nymbot.position[1])]
        points.extend(self.nymbot.ray_endpoints)
        
        # Dibujar cono semitransparente
        arcade.draw_polygon_filled(points, (173, 216, 230, 50))  # Azul claro con transparencia
        
        # Dibujar bordes del cono
        arcade.draw_line(
            self.nymbot.position[0], self.nymbot.position[1],
            self.nymbot.ray_endpoints[0][0], self.nymbot.ray_endpoints[0][1],
            arcade.color.DARK_BLUE, 1
        )
        arcade.draw_line(
            self.nymbot.position[0], self.nymbot.position[1],
            self.nymbot.ray_endpoints[-1][0], self.nymbot.ray_endpoints[-1][1],
            arcade.color.DARK_BLUE, 1
        )
    
    def draw_vision_bar(self):
        """Dibuja la barra de visión en la parte inferior"""
        bar_height = 28 # (50 - 20)/2
        bar_y = 10
        pad_x = 10
        ray_count = self.nymbot.fov
        ray_width = (SCREEN_WIDTH - 2*pad_x) / ray_count    
        
        for i in range(ray_count):
            intensity = int(self.nymbot.vision_data[i] * 255)
            
            # Determinar color basado en lo detectado (simplificado)
            if self.nymbot.vision_data[i] ==  1.0:  # Comida
                color = (0, intensity, 0)
            elif self.nymbot.vision_data[i] == 0.0:  # Pared
                color = (intensity, 0, 0)
            else:
                color = (intensity, intensity, intensity)
            
            rect_cell= arcade.rect.LBWH(pad_x + i * ray_width, bar_y, ray_width, bar_height)
            
            arcade.draw_rect_filled(
                rect=rect_cell,
                color=color
            )
            
            arcade.draw_rect_outline(
                rect=rect_cell,
                color=(255, 255, 255)
            )
    
    def load_playback_snapshot(self, snapshot):
        """Carga un snapshot para reproducción."""
        # Cargar estado del nymbot
        nymbot_state = snapshot['nymbot']
        self.nymbot.position = list(nymbot_state['position'])
        self.nymbot.body_angle = nymbot_state['body_angle']
        self.nymbot.eye_angle = nymbot_state['eye_angle']
        self.nymbot.energy = nymbot_state['energy']
        
        # Cargar comida
        self.food_pos = snapshot['food_pos']
        
        # Cargar pasos
        self.total_steps = snapshot.get('step', 0)
        
        # Si el snapshot incluye el cerebro, cargarlo
        if 'brain' in snapshot:
            self.nymbot.genome.brain.load_state_dict(snapshot['brain'])
    
    def on_update(self, delta_time):
        """Lógica de actualización del juego"""
        if self.playback_mode:
            # En modo reproducción, solo actualizamos la visión para renderizar
            self.nymbot.update_vision(self)
            self.info_text.text = (
                f"Modo Reproducción | Paso: {self.total_steps} | "
                f"Energía: {self.nymbot.energy:.1f}"
            )
            return
        
        # Actualizar visión
        self.nymbot.update_vision()
        
        # Obtener acción del cerebro
        action_array = self.nymbot.genome.brain.get_action(self.nymbot.vision_data)
        
        # Mover nymbot
        self.nymbot.move(action_array)
        
        # Actualizar energía
        is_alive = self.nymbot.update_energy()
        
        # Comprobar colisión con comida
        if self.check_food_collision(self.nymbot.position, 10):
            self.nymbot.energy += FOOD_ENERGY
            self.total_food_collected += 1
            self.reset_food()
        
        # Actualizar contador de pasos
        self.total_steps += 1
        
        # Comprobar fin de episodio
        if not is_alive or self.total_steps >= MAX_STEPS:
            self.reset_episode()
        
        # Actualizar texto informativo
        self.info_text.text = (
            f"Episodio: {self.current_episode} | "
            f"Pasos: {self.total_steps} | "
            f"Energía: {self.nymbot.energy:.1f} | "
            f"FOV: {self.nymbot.genome.fov:.1f}° | "
            f"Comida: {self.total_food_collected}"
        )
    
    def reset_episode(self):
        """Reinicia el episodio manteniendo las condiciones iniciales"""
        if self.initial_conditions and 'nymbot' in self.initial_conditions:
            nymbot_initial = self.initial_conditions['nymbot']
            self.nymbot.position = [nymbot_initial['x'], nymbot_initial['y']]
            self.nymbot.body_angle = nymbot_initial.get('body_angle', 0.0)
            self.nymbot.eye_angle = nymbot_initial.get('eye_angle', 0.0)
            self.nymbot.energy = nymbot_initial.get('energy', 100.0)
        else:
            # Posición y orientación aleatorias
            self.nymbot.position = self.nymbot._random_position()
            self.nymbot.body_angle = random.uniform(0, 2 * math.pi)
            self.nymbot.eye_angle = random.uniform(0, 2 * math.pi)
            self.nymbot.energy = 100.0
        
        # Reposicionar comida
        self.reset_food()
        self.total_steps = 0
        self.current_episode += 1
        self.total_food_collected = 0

def main():
    # Ejemplo: modo normal con condiciones iniciales personalizadas
    custom_init = {
        # 'nymbot': {
            # 'x': 400,
            # 'y': 300,
            # 'body_angle': 0.0,
            # 'eye_angle': 0.5,
            # 'energy': 100.0
        # },
        # 'food_pos': (200, 150),
        # 'walls': [
        #     [(50, 50), (750, 50)],
        #     [(750, 50), (750, 550)],
        #     [(750, 550), (50, 550)],
        #     [(50, 550), (50, 50)]
        # ],
        'genome_params': {
            # 'vision_resolution': 64,
            'fov': 60,
            'max_step_size': 0.50,
            'max_body_rotation': 0.1,
            'max_eye_rotation': 0.05
        }
    }
    sim = Simulation(initial_conditions=custom_init)
    arcade.run()

    # Ejemplo: modo reproducción
    # snapshot = np.load('snapshot.npy', allow_pickle=True).item()
    # sim = Simulation(playback_mode=True, playback_snapshot=snapshot)
    # arcade.run()

if __name__ == "__main__":
    main()