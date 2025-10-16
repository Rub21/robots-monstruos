#!/usr/bin/env python3
"""
Visualización 3D - Simulación Robots vs Monstruos
Archivo para mostrar el mundo 3D usando matplotlib.
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from typing import List, Tuple


class Visualizador3D:
    """
    Clase para visualizar el mundo 3D de la simulación.
    """
    
    def __init__(self):
        """
        Inicializa el visualizador 3D.
        """
        self.fig = None
        self.ax = None
        self.setup_plot()
    
    def setup_plot(self):
        """
        Configura el gráfico 3D.
        """
        self.fig = plt.figure(figsize=(12, 10))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Configurar la vista
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('Simulación Robots vs Monstruos - Vista 3D')
    
    def visualizar_mundo(self, entorno, iteracion: int = 0):
        """
        Visualiza el mundo 3D completo.
        
        Args:
            entorno: Instancia del entorno
            iteracion: Número de iteración actual
        """
        # Limpiar el gráfico anterior
        self.ax.clear()
        
        # Configurar límites del cubo
        self.ax.set_xlim(0, entorno.N)
        self.ax.set_ylim(0, entorno.N)
        self.ax.set_zlim(0, entorno.N)
        
        # Dibujar el cubo principal
        self._dibujar_cubo_principal(entorno.N)
        
        # Dibujar obstáculos (zonas vacías)
        self._dibujar_obstaculos(entorno)
        
        # Dibujar robots
        self._dibujar_robots(entorno)
        
        # Dibujar monstruos
        self._dibujar_monstruos(entorno)
        
        # Actualizar título
        self.ax.set_title(f'Iteración {iteracion} - Robots: {len(entorno.robots)}, Monstruos: {len(entorno.monstruos)}')
        
        # Configurar vista
        self.ax.view_init(elev=20, azim=45)
        
        # Mostrar el gráfico
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.1)  # Pausa corta para actualizar
    
    def _dibujar_cubo_principal(self, N: int):
        """
        Dibuja el contorno del cubo principal.
        
        Args:
            N: Tamaño del cubo
        """
        # Definir los vértices del cubo
        vertices = np.array([
            [0, 0, 0], [N, 0, 0], [N, N, 0], [0, N, 0],  # Cara inferior
            [0, 0, N], [N, 0, N], [N, N, N], [0, N, N]   # Cara superior
        ])
        
        # Definir las caras del cubo
        caras = [
            [0, 1, 2, 3],  # Cara inferior
            [4, 5, 6, 7],  # Cara superior
            [0, 1, 5, 4],  # Cara frontal
            [2, 3, 7, 6],  # Cara trasera
            [0, 3, 7, 4],  # Cara izquierda
            [1, 2, 6, 5]   # Cara derecha
        ]
        
        # Dibujar las caras del cubo
        for cara in caras:
            puntos = vertices[cara]
            # Crear una cara cerrada
            puntos = np.vstack([puntos, puntos[0]])
            self.ax.plot(puntos[:, 0], puntos[:, 1], puntos[:, 2], 'k-', alpha=0.3, linewidth=1)
    
    def _dibujar_obstaculos(self, entorno):
        """
        Dibuja los obstáculos (zonas vacías) como cubos pequeños.
        
        Args:
            entorno: Instancia del entorno
        """
        obstaculos = []
        
        # Encontrar todas las posiciones con obstáculos
        for x in range(entorno.N):
            for y in range(entorno.N):
                for z in range(entorno.N):
                    if entorno.mundo[x, y, z] == 1:  # Zona vacía
                        obstaculos.append((x, y, z))
        
        # Dibujar obstáculos como cubos pequeños
        for x, y, z in obstaculos:
            self._dibujar_cubo_pequeno(x, y, z, color='yellow', alpha=0.7)
    
    def _dibujar_robots(self, entorno):
        """
        Dibuja los robots como cubos rojos con orientación.
        
        Args:
            entorno: Instancia del entorno
        """
        for robot in entorno.robots:
            x, y, z = robot.posicion
            # Dibujar el robot como un cubo rojo
            self._dibujar_cubo_pequeno(x, y, z, color='red', alpha=0.8)
            
            # Dibujar la orientación como una flecha
            self._dibujar_flecha_orientacion(x, y, z, robot.orientacion, color='darkred')
    
    def _dibujar_monstruos(self, entorno):
        """
        Dibuja los monstruos como cubos verdes.
        
        Args:
            entorno: Instancia del entorno
        """
        for monstruo in entorno.monstruos:
            x, y, z = monstruo.posicion
            # Dibujar el monstruo como un cubo verde
            self._dibujar_cubo_pequeno(x, y, z, color='green', alpha=0.8)
    
    def _dibujar_cubo_pequeno(self, x: int, y: int, z: int, color: str = 'blue', alpha: float = 0.5):
        """
        Dibuja un cubo pequeño en la posición especificada.
        
        Args:
            x, y, z: Coordenadas del cubo
            color: Color del cubo
            alpha: Transparencia
        """
        # Definir los vértices del cubo pequeño
        vertices = np.array([
            [x, y, z], [x+1, y, z], [x+1, y+1, z], [x, y+1, z],  # Cara inferior
            [x, y, z+1], [x+1, y, z+1], [x+1, y+1, z+1], [x, y+1, z+1]  # Cara superior
        ])
        
        # Definir las caras del cubo pequeño
        caras = [
            [0, 1, 2, 3],  # Cara inferior
            [4, 5, 6, 7],  # Cara superior
            [0, 1, 5, 4],  # Cara frontal
            [2, 3, 7, 6],  # Cara trasera
            [0, 3, 7, 4],  # Cara izquierda
            [1, 2, 6, 5]   # Cara derecha
        ]
        
        # Dibujar las caras del cubo pequeño
        for cara in caras:
            puntos = vertices[cara]
            # Crear una cara cerrada
            puntos = np.vstack([puntos, puntos[0]])
            self.ax.plot(puntos[:, 0], puntos[:, 1], puntos[:, 2], color=color, alpha=alpha, linewidth=2)
    
    def _dibujar_flecha_orientacion(self, x: int, y: int, z: int, orientacion: Tuple[int, int, int], color: str = 'darkred'):
        """
        Dibuja una flecha que indica la orientación del robot.
        
        Args:
            x, y, z: Posición del robot
            orientacion: Vector de orientación
            color: Color de la flecha
        """
        # Calcular el punto final de la flecha
        ox, oy, oz = orientacion
        x_end = x + 0.5 + ox * 0.3
        y_end = y + 0.5 + oy * 0.3
        z_end = z + 0.5 + oz * 0.3
        
        # Dibujar la flecha
        self.ax.plot([x + 0.5, x_end], [y + 0.5, y_end], [z + 0.5, z_end], 
                    color=color, linewidth=3, alpha=0.8)
        
        # Dibujar la punta de la flecha
        self.ax.scatter([x_end], [y_end], [z_end], color=color, s=50, alpha=0.8)
    
    def mostrar_estadisticas(self, entorno):
        """
        Muestra estadísticas del mundo en texto.
        
        Args:
            entorno: Instancia del entorno
        """
        print(f"\n📊 ESTADÍSTICAS DEL MUNDO:")
        print(f"   Tamaño del cubo: {entorno.N}x{entorno.N}x{entorno.N}")
        print(f"   Total de celdas: {entorno.N**3}")
        print(f"   Robots activos: {len(entorno.robots)}")
        print(f"   Monstruos activos: {len(entorno.monstruos)}")
        
        # Mostrar posiciones de robots
        if entorno.robots:
            print(f"\n🤖 POSICIONES DE ROBOTS:")
            for i, robot in enumerate(entorno.robots):
                print(f"   Robot {i+1}: Posición {robot.posicion} - {robot.obtener_orientacion_texto()}")
        
        # Mostrar posiciones de monstruos
        if entorno.monstruos:
            print(f"\n👹 POSICIONES DE MONSTRUOS:")
            for i, monstruo in enumerate(entorno.monstruos):
                print(f"   Monstruo {i+1}: Posición {monstruo.posicion}")
    
    def cerrar(self):
        """
        Cierra la ventana de visualización.
        """
        plt.close(self.fig)


def crear_visualizador_3d():
    """
    Crea una instancia del visualizador 3D.
    
    Returns:
        Instancia de Visualizador3D
    """
    return Visualizador3D()
