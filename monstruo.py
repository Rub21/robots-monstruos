#!/usr/bin/env python3
"""
Clase Monstruo
Representa un monstruo simple con comportamiento aleatorio.
"""

import random
from typing import Tuple

# Códigos de colores ANSI para terminal


class Monstruo:
    """
    Clase que representa un monstruo simple con comportamiento aleatorio.
    
    Los monstruos se mueven aleatoriamente cada K iteraciones en una de las
    6 direcciones adyacentes posibles.
    """
    
    def __init__(self, posicion_inicial: Tuple[int, int, int]):
        """
        Constructor del monstruo.
        
        Args:
            posicion_inicial: Tupla (x, y, z) con la posición inicial
        """
        self.posicion = posicion_inicial
        self.K = 3  # Se mueve cada 3 iteraciones
    
    def actuar(self, entorno, k_iteracion_actual: int):
        """
        Lógica de comportamiento del monstruo.
        
        Args:
            entorno: Instancia del entorno donde se encuentra
            k_iteracion_actual: Número de iteración actual
        """
        # Solo actuar cada K iteraciones
        if k_iteracion_actual % self.K != 0:
            return
        
        # Definir las 6 direcciones adyacentes posibles
        direcciones = [
            (1, 0, 0),   # +X
            (-1, 0, 0),  # -X
            (0, 1, 0),   # +Y
            (0, -1, 0),  # -Y
            (0, 0, 1),   # +Z
            (0, 0, -1)   # -Z
        ]
        
        # Elegir una dirección aleatoria
        direccion = random.choice(direcciones)
        
        # Calcular nueva posición
        x, y, z = self.posicion
        dx, dy, dz = direccion
        nueva_posicion = (x + dx, y + dy, z + dz)
        
        # Intentar moverse
        if entorno.mover_entidad(self, nueva_posicion):
            print(f"Monstruo se movió de {self.posicion} a {nueva_posicion}")
