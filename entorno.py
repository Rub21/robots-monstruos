#!/usr/bin/env python3
"""
Clase Entorno
Representa el mundo 3D donde se desarrolla la simulación.
"""

import numpy as np
import random
import time
from typing import List, Tuple, Optional

# Códigos de colores ANSI para terminal


class Entorno:
    """
    Clase que representa el mundo 3D donde se desarrolla la simulación.

    El entorno es un cubo de NxNxN celdas donde:
    - 0: Zona libre (transitable)
    - 1: Zona vacía (obstáculo)
    - 2: Robot
    - 3: Monstruo
    """

    def __init__(self, N: int, p_free: float, p_soft: float, seed: int = None):
        """
        Constructor del entorno.

        Args:
            N: Tamaño del cubo (NxNxN)
            p_free: Porcentaje de celdas libres
            p_soft: Porcentaje de celdas vacías (obstáculos)
            seed: Semilla para el generador aleatorio (opcional)
        """
        self.N = N
        self.p_free = p_free
        self.p_soft = p_soft

        # Configurar semilla aleatoria para mejor randomización
        if seed is None:
            # Usar tiempo actual y process id para mayor entropía
            seed = int(time.time() * 1000000) % (2**32)

        # Configurar generadores aleatorios
        random.seed(seed)
        np.random.seed(seed)
        self.rng = np.random.RandomState(seed)

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
        Usa múltiples técnicas para garantizar máxima aleatoriedad.
        """
        total_celdas = self.N ** 3
        celdas_libres = int(total_celdas * self.p_free)
        celdas_vacias = int(total_celdas * self.p_soft)

        # Método 1: Usar numpy para generar posiciones más aleatorias
        # Generar todas las coordenadas usando numpy
        coords_x = np.repeat(np.arange(self.N), self.N * self.N)
        coords_y = np.tile(np.repeat(np.arange(self.N), self.N), self.N)
        coords_z = np.tile(np.arange(self.N), self.N * self.N)

        # Crear array de posiciones y mezclarlo con numpy
        posiciones = np.column_stack((coords_x, coords_y, coords_z))
        self.rng.shuffle(posiciones)

        # Método alternativo usando permutación aleatoria de índices
        indices = self.rng.permutation(total_celdas)

        # Asignar celdas libres usando los índices permutados
        for i in range(celdas_libres):
            idx = indices[i]
            pos = posiciones[idx]
            x, y, z = pos
            self.mundo[x, y, z] = 0  # Zona libre

        # Asignar celdas vacías (obstáculos)
        for i in range(celdas_libres, celdas_libres + celdas_vacias):
            idx = indices[i]
            pos = posiciones[idx]
            x, y, z = pos
            self.mundo[x, y, z] = 1  # Zona vacía

        # Aplicar ruido adicional para mejorar distribución
        self._aplicar_ruido_aleatorio()

        # El resto permanece como 0 (zona libre por defecto)

    def _aplicar_ruido_aleatorio(self):
        """
        Aplica ruido aleatorio adicional para mejorar la distribución.
        Intercambia aleatoriamente algunas celdas para evitar patrones.
        """
        # Realizar intercambios aleatorios entre celdas
        num_intercambios = max(10, self.N ** 2)  # Más intercambios para mundos más grandes

        for _ in range(num_intercambios):
            # Seleccionar dos posiciones aleatorias
            pos1 = (self.rng.randint(0, self.N),
                   self.rng.randint(0, self.N),
                   self.rng.randint(0, self.N))
            pos2 = (self.rng.randint(0, self.N),
                   self.rng.randint(0, self.N),
                   self.rng.randint(0, self.N))

            # Intercambiar los valores
            x1, y1, z1 = pos1
            x2, y2, z2 = pos2
            self.mundo[x1, y1, z1], self.mundo[x2, y2, z2] = \
                self.mundo[x2, y2, z2], self.mundo[x1, y1, z1]

    def regenerar_mundo(self, nueva_semilla: int = None):
        """
        Regenera el mundo con una nueva distribución aleatoria.

        Args:
            nueva_semilla: Nueva semilla para el generador aleatorio
        """
        # Limpiar entidades existentes
        self.robots.clear()
        self.monstruos.clear()

        # Configurar nueva semilla si se proporciona
        if nueva_semilla is not None:
            random.seed(nueva_semilla)
            np.random.seed(nueva_semilla)
            self.rng = np.random.RandomState(nueva_semilla)
        else:
            # Usar tiempo actual para nueva semilla
            nueva_semilla = int(time.time() * 1000000) % (2**32)
            random.seed(nueva_semilla)
            np.random.seed(nueva_semilla)
            self.rng = np.random.RandomState(nueva_semilla)

        # Limpiar el mundo
        self.mundo.fill(0)

        # Regenerar
        self._generar_mundo()

    def obtener_posiciones_aleatorias_libres(self, cantidad: int) -> List[Tuple[int, int, int]]:
        """
        Obtiene múltiples posiciones aleatorias libres usando el generador interno.

        Args:
            cantidad: Número de posiciones a obtener

        Returns:
            Lista de posiciones libres
        """
        posiciones_libres = []
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    if self.mundo[x, y, z] == 0:
                        posiciones_libres.append((x, y, z))

        if len(posiciones_libres) < cantidad:
            return posiciones_libres

        # Usar el generador interno para mejor aleatoriedad
        indices = self.rng.choice(len(posiciones_libres),
                                size=cantidad,
                                replace=False)
        return [posiciones_libres[i] for i in indices]

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

        print(f"\n=== VISUALIZACIÓN COMPACTA 3D (Capa {capa}) ===")
        print(". = libre, # = vacía (obstáculo), R = robot, M = monstruo")
        print()

        # Preparar las tres vistas
        vista_xy = self._preparar_vista_xy(capa)
        vista_xz = self._preparar_vista_xz(capa)
        vista_yz = self._preparar_vista_yz(capa)

        # Mostrar encabezados
        print("VISTA XY (Frontal)    VISTA XZ (Lateral)    VISTA YZ (Superior)")
        print("=" * 60)

        # Mostrar las vistas lado a lado
        for i in range(self.N + 1):  # +1 para incluir las coordenadas
            linea_xy = vista_xy[i] if i < len(vista_xy) else ""
            linea_xz = vista_xz[i] if i < len(vista_xz) else ""
            linea_yz = vista_yz[i] if i < len(vista_yz) else ""

            print(f"{linea_xy:<20} {linea_xz:<20} {linea_yz}")

        print(f"\nRobots activos: {len(self.robots)} | Monstruos activos: {len(self.monstruos)}")
        print("=" * 60)

    def _preparar_vista_xy(self, capa_z: int):
        """
        Prepara la vista XY como lista de strings para mostrar lado a lado.
        """
        lineas = []
        # Encabezado de coordenadas Y
        encabezado = "   "
        for y in range(self.N):
            encabezado += f"{y:2}"
        lineas.append(encabezado)

        # Filas
        for x in range(self.N):
            linea = f"{x:2} "
            for y in range(self.N):
                estado = self.mundo[x, y, capa_z]
                if estado == 0:
                    linea += " ."
                elif estado == 1:
                    linea += " #"
                elif estado == 2:
                    linea += " R"
                elif estado == 3:
                    linea += " M"
            lineas.append(linea)

        return lineas

    def _preparar_vista_xz(self, capa_y: int):
        """
        Prepara la vista XZ como lista de strings para mostrar lado a lado.
        """
        lineas = []
        # Encabezado de coordenadas Z
        encabezado = "   "
        for z in range(self.N):
            encabezado += f"{z:2}"
        lineas.append(encabezado)

        # Filas
        for x in range(self.N):
            linea = f"{x:2} "
            for z in range(self.N):
                estado = self.mundo[x, capa_y, z]
                if estado == 0:
                    linea += " ."
                elif estado == 1:
                    linea += " #"
                elif estado == 2:
                    linea += " R"
                elif estado == 3:
                    linea += " M"
            lineas.append(linea)

        return lineas

    def _preparar_vista_yz(self, capa_x: int):
        """
        Prepara la vista YZ como lista de strings para mostrar lado a lado.
        """
        lineas = []
        # Encabezado de coordenadas Z
        encabezado = "   "
        for z in range(self.N):
            encabezado += f"{z:2}"
        lineas.append(encabezado)

        # Filas
        for y in range(self.N):
            linea = f"{y:2} "
            for z in range(self.N):
                estado = self.mundo[capa_x, y, z]
                if estado == 0:
                    linea += " ."
                elif estado == 1:
                    linea += " #"
                elif estado == 2:
                    linea += " R"
                elif estado == 3:
                    linea += " M"
            lineas.append(linea)

        return lineas


def crear_posicion_aleatoria_libre(entorno: Entorno) -> Optional[Tuple[int, int, int]]:
    """
    Encuentra una posición aleatoria libre en el entorno usando métodos optimizados.

    Args:
        entorno: Instancia del entorno

    Returns:
        Tupla con posición libre o None si no se encuentra
    """
    # Método 1: Buscar posiciones libres directamente
    posiciones_libres = []
    for x in range(entorno.N):
        for y in range(entorno.N):
            for z in range(entorno.N):
                if entorno.obtener_estado((x, y, z)) == 0:
                    posiciones_libres.append((x, y, z))

    if not posiciones_libres:
        return None

    # Usar numpy para selección aleatoria más robusta
    if hasattr(entorno, 'rng'):
        idx = entorno.rng.randint(0, len(posiciones_libres))
    else:
        # Fallback si no hay rng disponible
        idx = random.randint(0, len(posiciones_libres) - 1)

    return posiciones_libres[idx]


def crear_posiciones_aleatorias_libres(entorno: Entorno, cantidad: int) -> List[Tuple[int, int, int]]:
    """
    Encuentra múltiples posiciones aleatorias libres en el entorno de forma eficiente.

    Args:
        entorno: Instancia del entorno
        cantidad: Número de posiciones a encontrar

    Returns:
        Lista de tuplas con posiciones libres
    """
    # Obtener todas las posiciones libres
    posiciones_libres = []
    for x in range(entorno.N):
        for y in range(entorno.N):
            for z in range(entorno.N):
                if entorno.obtener_estado((x, y, z)) == 0:
                    posiciones_libres.append((x, y, z))

    if len(posiciones_libres) < cantidad:
        return posiciones_libres  # Devolver todas las disponibles

    # Usar numpy para selección aleatoria sin reemplazo
    if hasattr(entorno, 'rng'):
        indices = entorno.rng.choice(len(posiciones_libres),
                                   size=cantidad,
                                   replace=False)
        return [posiciones_libres[i] for i in indices]
    else:
        # Fallback usando random estándar
        return random.sample(posiciones_libres, cantidad)
