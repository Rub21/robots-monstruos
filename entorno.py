#!/usr/bin/env python3
"""
Clase Entorno
Representa el mundo 3D donde se desarrolla la simulación.
"""

import numpy as np
import random
from typing import List, Tuple, Optional


class Entorno:
    """
    Clase que representa el mundo 3D donde se desarrolla la simulación.
    
    El entorno es un cubo de NxNxN celdas donde:
    - 0: Zona libre (transitable)
    - 1: Zona vacía (obstáculo)
    - 2: Robot
    - 3: Monstruo
    """
    
    def __init__(self, N: int, p_free: float, p_soft: float):
        """
        Constructor del entorno.
        
        Args:
            N: Tamaño del cubo (NxNxN)
            p_free: Porcentaje de celdas libres
            p_soft: Porcentaje de celdas vacías (obstáculos)
        """
        self.N = N
        self.p_free = p_free
        self.p_soft = p_soft
        
        # Crear el mundo 3D usando numpy array
        self.mundo = np.zeros((N, N, N), dtype=int)
        
        # Listas para mantener registro de entidades
        self.robots: List = []
        self.monstruos: List = []
        
        # Generar el mundo aleatoriamente
        self._generar_mundo()
        
    def _generar_mundo(self):
        """
        Genera el mundo aleatoriamente según los porcentajes especificados.
        """
        total_celdas = self.N ** 3
        celdas_libres = int(total_celdas * self.p_free)
        celdas_vacias = int(total_celdas * self.p_soft)
        
        # Crear lista de todas las posiciones posibles
        posiciones = [(x, y, z) for x in range(self.N) 
                     for y in range(self.N) 
                     for z in range(self.N)]
        
        # Mezclar aleatoriamente
        random.shuffle(posiciones)
        
        # Asignar celdas libres
        for i in range(celdas_libres):
            x, y, z = posiciones[i]
            self.mundo[x, y, z] = 0  # Zona libre
        
        # Asignar celdas vacías (obstáculos)
        for i in range(celdas_libres, celdas_libres + celdas_vacias):
            x, y, z = posiciones[i]
            self.mundo[x, y, z] = 1  # Zona vacía
        
        # El resto permanece como 0 (zona libre por defecto)
    
    def agregar_entidad(self, entidad, posicion: Tuple[int, int, int]) -> bool:
        """
        Coloca una entidad (robot o monstruo) en una posición específica.
        
        Args:
            entidad: Instancia de Robot o Monstruo
            posicion: Tupla (x, y, z) con la posición
            
        Returns:
            True si se pudo colocar, False en caso contrario
        """
        x, y, z = posicion
        
        # Verificar que la posición sea válida y esté libre
        if not self.es_valida(posicion) or self.obtener_estado(posicion) != 0:
            return False
        
        # Colocar la entidad en el mundo
        # Usar nombres de clase como strings para evitar importaciones circulares
        if entidad.__class__.__name__ == 'Robot':
            self.mundo[x, y, z] = 2  # Robot
            self.robots.append(entidad)
        elif entidad.__class__.__name__ == 'Monstruo':
            self.mundo[x, y, z] = 3  # Monstruo
            self.monstruos.append(entidad)
        
        # Actualizar posición de la entidad
        entidad.posicion = posicion
        return True
    
    def es_valida(self, posicion: Tuple[int, int, int]) -> bool:
        """
        Verifica si una posición está dentro de los límites del mundo.
        
        Args:
            posicion: Tupla (x, y, z) con la posición
            
        Returns:
            True si la posición es válida, False en caso contrario
        """
        x, y, z = posicion
        return (0 <= x < self.N and 
                0 <= y < self.N and 
                0 <= z < self.N)
    
    def obtener_estado(self, posicion: Tuple[int, int, int]) -> int:
        """
        Obtiene el estado de una celda específica.
        
        Args:
            posicion: Tupla (x, y, z) con la posición
            
        Returns:
            Estado de la celda (0=libre, 1=vacía, 2=robot, 3=monstruo)
        """
        if not self.es_valida(posicion):
            return -1  # Posición inválida
        
        x, y, z = posicion
        return self.mundo[x, y, z]
    
    def mover_entidad(self, entidad, nueva_posicion: Tuple[int, int, int]) -> bool:
        """
        Mueve una entidad de su posición actual a una nueva posición.
        
        Args:
            entidad: Instancia de Robot o Monstruo
            nueva_posicion: Tupla (x, y, z) con la nueva posición
            
        Returns:
            True si se pudo mover, False en caso contrario
        """
        if not self.es_valida(nueva_posicion):
            return False
        
        # Verificar que la nueva posición esté libre
        if self.obtener_estado(nueva_posicion) != 0:
            return False
        
        # Limpiar posición anterior
        x_ant, y_ant, z_ant = entidad.posicion
        self.mundo[x_ant, y_ant, z_ant] = 0
        
        # Colocar en nueva posición
        x_nuevo, y_nuevo, z_nuevo = nueva_posicion
        if entidad.__class__.__name__ == 'Robot':
            self.mundo[x_nuevo, y_nuevo, z_nuevo] = 2
        elif entidad.__class__.__name__ == 'Monstruo':
            self.mundo[x_nuevo, y_nuevo, z_nuevo] = 3
        
        # Actualizar posición de la entidad
        entidad.posicion = nueva_posicion
        return True
    
    def eliminar_entidad(self, entidad):
        """
        Elimina una entidad del mundo.
        
        Args:
            entidad: Instancia de Robot o Monstruo a eliminar
        """
        x, y, z = entidad.posicion
        self.mundo[x, y, z] = 0  # Liberar la celda
        
        # Remover de las listas
        if entidad.__class__.__name__ == 'Robot' and entidad in self.robots:
            self.robots.remove(entidad)
        elif entidad.__class__.__name__ == 'Monstruo' and entidad in self.monstruos:
            self.monstruos.remove(entidad)
    
    def visualizar(self, capa: int = None):
        """
        Visualiza el estado actual del mundo.
        
        Args:
            capa: Capa específica a visualizar (si es None, muestra la capa central)
        """
        if capa is None:
            capa = self.N // 2
        
        print(f"\n=== VISUALIZACIÓN DEL MUNDO (Capa {capa}) ===")
        print("Leyenda: . = libre, # = vacía, R = robot, M = monstruo")
        print()
        
        # Imprimir coordenadas Y
        print("   ", end="")
        for y in range(self.N):
            print(f"{y:2}", end="")
        print()
        
        # Imprimir cada fila
        for x in range(self.N):
            print(f"{x:2} ", end="")
            for y in range(self.N):
                estado = self.mundo[x, y, capa]
                if estado == 0:
                    print(" .", end="")
                elif estado == 1:
                    print(" #", end="")
                elif estado == 2:
                    print(" R", end="")
                elif estado == 3:
                    print(" M", end="")
            print()
        
        print(f"\nRobots activos: {len(self.robots)}")
        print(f"Monstruos activos: {len(self.monstruos)}")
        print("=" * 40)


def crear_posicion_aleatoria_libre(entorno: Entorno) -> Optional[Tuple[int, int, int]]:
    """
    Encuentra una posición aleatoria libre en el entorno.
    
    Args:
        entorno: Instancia del entorno
        
    Returns:
        Tupla con posición libre o None si no se encuentra
    """
    intentos = 0
    max_intentos = 1000
    
    while intentos < max_intentos:
        x = random.randint(0, entorno.N - 1)
        y = random.randint(0, entorno.N - 1)
        z = random.randint(0, entorno.N - 1)
        
        posicion = (x, y, z)
        if entorno.es_valida(posicion) and entorno.obtener_estado(posicion) == 0:
            return posicion
        
        intentos += 1
    
    return None
