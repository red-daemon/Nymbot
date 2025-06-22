# brain.py
import torch
import torch.nn as nn

class NymbotBrain(nn.Module):
    def __init__(self, input_size, hidden_layers):  # Solo 2 argumentos ahora
        super().__init__()
        layers = []
        prev_size = input_size
        
        for size in hidden_layers:
            layers.append(nn.Linear(prev_size, size))
            layers.append(nn.ReLU())
            prev_size = size
        
        # Capa de salida: 3 neuronas (movimiento, rot_cuerpo, rot_ojo)
        layers.append(nn.Linear(prev_size, 3))
        layers.append(nn.Tanh())  # Para salida en [-1, 1]
        
        self.net = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.net(x)
    
    def get_action(self, state):
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state)
            # Devuelve un array de 3 valores en [-1, 1]
            return self.forward(state_tensor).numpy()