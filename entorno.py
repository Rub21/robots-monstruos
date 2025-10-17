#!/usr/bin/env python3
"""
Clase Entorno
Representa el mundo 3D donde se desarrolla la simulación.
"""

import numpy as np
import random
from typing import List, Tuple, Optional

# Códigos de colores ANSI para terminal
class Colores:
    RESET = '\033[0m'
    ROJO = '\033[91m'      # Robots
    VERDE = '\033[92m'     # Monstruos
    AMARILLO = '\033[93m'  # Obstáculos
    AZUL = '\033[94m'      # Libre
    MAGENTA = '\033[95m'   # Títulos
    CYAN = '\033[96m'      # Coordenadas


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
        Visualiza el estado actual del mundo mostrando tres caras del cubo simultáneamente.
        
        Args:
            capa: Capa específica a visualizar (si es None, muestra la capa central)
        """
        if capa is None:
            capa = self.N // 2
        
        print(f"\n=== VISUALIZACIÓN DEL MUNDO 3D (Capa {capa}) ===")
        print("Leyenda: . = libre, # = vacía (obstáculo), R = robot, M = monstruo")
        print()
        
        # Mostrar tres vistas del cubo: XY (cara frontal), XZ (cara lateral), YZ (cara superior)
        self._mostrar_vista_xy(capa)
        self._mostrar_vista_xz(capa)
        self._mostrar_vista_yz(capa)
        
        print(f"\nRobots activos: {len(self.robots)}")
        print(f"Monstruos activos: {len(self.monstruos)}")
        print("=" * 60)
    
    def _mostrar_vista_xy(self, capa_z: int):
        """
        Muestra la vista XY (cara frontal) del cubo en la capa Z especificada.
        """
        print("VISTA XY (Cara Frontal):")
        print("   ", end="")
        for y in range(self.N):
            print(f"{y:2}", end="")
        print()
        
        for x in range(self.N):
            print(f"{x:2} ", end="")
            for y in range(self.N):
                estado = self.mundo[x, y, capa_z]
                if estado == 0:
                    print(" .", end="")
                elif estado == 1:
                    print(" #", end="")
                elif estado == 2:
                    print(" R", end="")
                elif estado == 3:
                    print(" M", end="")
            print()
        print()
    
    def _mostrar_vista_xz(self, capa_y: int):
        """
        Muestra la vista XZ (cara lateral) del cubo en la capa Y especificada.
        """
        print("VISTA XZ (Cara Lateral):")
        print("   ", end="")
        for z in range(self.N):
            print(f"{z:2}", end="")
        print()
        
        for x in range(self.N):
            print(f"{x:2} ", end="")
            for z in range(self.N):
                estado = self.mundo[x, capa_y, z]
                if estado == 0:
                    print(" .", end="")
                elif estado == 1:
                    print(" #", end="")
                elif estado == 2:
                    print(" R", end="")
                elif estado == 3:
                    print(" M", end="")
            print()
        print()
    
    def _mostrar_vista_yz(self, capa_x: int):
        """
        Muestra la vista YZ (cara superior) del cubo en la capa X especificada.
        """
        print("VISTA YZ (Cara Superior):")
        print("   ", end="")
        for z in range(self.N):
            print(f"{z:2}", end="")
        print()
        
        for y in range(self.N):
            print(f"{y:2} ", end="")
            for z in range(self.N):
                estado = self.mundo[capa_x, y, z]
                if estado == 0:
                    print(" .", end="")
                elif estado == 1:
                    print(" #", end="")
                elif estado == 2:
                    print(" R", end="")
                elif estado == 3:
                    print(" M", end="")
            print()
        print()
    
    def visualizar_compacto(self, capa: int = None):
        """
        Visualiza el mundo 3D de forma compacta mostrando las tres vistas lado a lado.
        
        Args:
            capa: Capa específica a visualizar (si es None, muestra la capa central)
        """
        if capa is None:
            capa = self.N // 2
        
        print(f"\n{Colores.MAGENTA}=== VISUALIZACIÓN COMPACTA 3D (Capa {capa}) ==={Colores.RESET}")
        print(f"{Colores.AZUL}.{Colores.RESET} = libre, {Colores.AMARILLO}#{Colores.RESET} = vacía (obstáculo), {Colores.ROJO}R{Colores.RESET} = robot, {Colores.VERDE}M{Colores.RESET} = monstruo")
        print()
        
        # Preparar las tres vistas
        vista_xy = self._preparar_vista_xy(capa)
        vista_xz = self._preparar_vista_xz(capa)
        vista_yz = self._preparar_vista_yz(capa)
        
        # Mostrar encabezados
        print(f"{Colores.CYAN}VISTA XY (Frontal){Colores.RESET}    {Colores.CYAN}VISTA XZ (Lateral){Colores.RESET}    {Colores.CYAN}VISTA YZ (Superior){Colores.RESET}")
        print("=" * 60)
        
        # Mostrar las vistas lado a lado
        for i in range(self.N + 1):  # +1 para incluir las coordenadas
            linea_xy = vista_xy[i] if i < len(vista_xy) else ""
            linea_xz = vista_xz[i] if i < len(vista_xz) else ""
            linea_yz = vista_yz[i] if i < len(vista_yz) else ""
            
            print(f"{linea_xy:<20} {linea_xz:<20} {linea_yz}")
        
        print(f"\n{Colores.ROJO}Robots activos: {len(self.robots)}{Colores.RESET} | {Colores.VERDE}Monstruos activos: {len(self.monstruos)}{Colores.RESET}")
        print("=" * 60)
    
    def _preparar_vista_xy(self, capa_z: int):
        """
        Prepara la vista XY como lista de strings para mostrar lado a lado.
        """
        lineas = []
        # Encabezado de coordenadas Y
        encabezado = f"{Colores.CYAN}   "
        for y in range(self.N):
            encabezado += f"{y:2}"
        encabezado += f"{Colores.RESET}"
        lineas.append(encabezado)
        
        # Filas
        for x in range(self.N):
            linea = f"{Colores.CYAN}{x:2}{Colores.RESET} "
            for y in range(self.N):
                estado = self.mundo[x, y, capa_z]
                if estado == 0:
                    linea += f"{Colores.AZUL} .{Colores.RESET}"
                elif estado == 1:
                    linea += f"{Colores.AMARILLO} #{Colores.RESET}"
                elif estado == 2:
                    linea += f"{Colores.ROJO} R{Colores.RESET}"
                elif estado == 3:
                    linea += f"{Colores.VERDE} M{Colores.RESET}"
            lineas.append(linea)
        
        return lineas
    
    def _preparar_vista_xz(self, capa_y: int):
        """
        Prepara la vista XZ como lista de strings para mostrar lado a lado.
        """
        lineas = []
        # Encabezado de coordenadas Z
        encabezado = f"{Colores.CYAN}   "
        for z in range(self.N):
            encabezado += f"{z:2}"
        encabezado += f"{Colores.RESET}"
        lineas.append(encabezado)
        
        # Filas
        for x in range(self.N):
            linea = f"{Colores.CYAN}{x:2}{Colores.RESET} "
            for z in range(self.N):
                estado = self.mundo[x, capa_y, z]
                if estado == 0:
                    linea += f"{Colores.AZUL} .{Colores.RESET}"
                elif estado == 1:
                    linea += f"{Colores.AMARILLO} #{Colores.RESET}"
                elif estado == 2:
                    linea += f"{Colores.ROJO} R{Colores.RESET}"
                elif estado == 3:
                    linea += f"{Colores.VERDE} M{Colores.RESET}"
            lineas.append(linea)
        
        return lineas
    
    def _preparar_vista_yz(self, capa_x: int):
        """
        Prepara la vista YZ como lista de strings para mostrar lado a lado.
        """
        lineas = []
        # Encabezado de coordenadas Z
        encabezado = f"{Colores.CYAN}   "
        for z in range(self.N):
            encabezado += f"{z:2}"
        encabezado += f"{Colores.RESET}"
        lineas.append(encabezado)
        
        # Filas
        for y in range(self.N):
            linea = f"{Colores.CYAN}{y:2}{Colores.RESET} "
            for z in range(self.N):
                estado = self.mundo[capa_x, y, z]
                if estado == 0:
                    linea += f"{Colores.AZUL} .{Colores.RESET}"
                elif estado == 1:
                    linea += f"{Colores.AMARILLO} #{Colores.RESET}"
                elif estado == 2:
                    linea += f"{Colores.ROJO} R{Colores.RESET}"
                elif estado == 3:
                    linea += f"{Colores.VERDE} M{Colores.RESET}"
            lineas.append(linea)
        
        return lineas


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
