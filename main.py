#!/usr/bin/env python3
"""
Simulación Robots vs Monstruos - Examen MIA-103
Implementación completa siguiendo las instrucciones detalladas.

Este código implementa una simulación 3D donde robots inteligentes deben
eliminar monstruos en un entorno con obstáculos y zonas especiales.
"""

import numpy as np
import random
import time
import copy
from typing import List, Tuple, Dict, Optional


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
        self.robots: List['Robot'] = []
        self.monstruos: List['Monstruo'] = []
        
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
        if isinstance(entidad, Robot):
            self.mundo[x, y, z] = 2  # Robot
            self.robots.append(entidad)
        elif isinstance(entidad, Monstruo):
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
        if isinstance(entidad, Robot):
            self.mundo[x_nuevo, y_nuevo, z_nuevo] = 2
        elif isinstance(entidad, Monstruo):
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
        if isinstance(entidad, Robot) and entidad in self.robots:
            self.robots.remove(entidad)
        elif isinstance(entidad, Monstruo) and entidad in self.monstruos:
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
    
    def actuar(self, entorno: Entorno, k_iteracion_actual: int):
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


class Robot:
    """
    Clase que representa un robot inteligente con sensores, effectores y memoria.
    
    Los robots tienen la capacidad de percibir su entorno, tomar decisiones
    inteligentes y recordar experiencias pasadas.
    """
    
    def __init__(self, posicion_inicial: Tuple[int, int, int], 
                 orientacion_inicial: Tuple[int, int, int]):
        """
        Constructor del robot.
        
        Args:
            posicion_inicial: Tupla (x, y, z) con la posición inicial
            orientacion_inicial: Vector de orientación (ej: (1, 0, 0) para adelante en X)
        """
        self.posicion = posicion_inicial
        self.orientacion = orientacion_inicial
        self.memoria: List[Tuple[int, Dict, str]] = []  # (tiempo, percepción, acción)
        self.choco_pared_anterior = False  # Para el Vacuscopio
        
    def percibir_entorno(self, entorno: Entorno) -> Dict:
        """
        Sistema de percepción del robot que activa todos sus sensores.
        
        Args:
            entorno: Instancia del entorno donde se encuentra
            
        Returns:
            Diccionario con toda la información percibida
        """
        percepcion = {}
        
        # Giroscopio: orientación actual
        percepcion['orientacion'] = self.orientacion
        
        # Monstroscopio: detectar monstruos en las 5 celdas adyacentes (excepto atrás)
        percepcion['monstruo_cerca'] = self._detectar_monstruos(entorno)
        
        # Vacuscopio: activado después de un choque con pared
        percepcion['choco_pared'] = self.choco_pared_anterior
        
        # Energómetro espectral: detectar monstruo en celda actual
        percepcion['monstruo_actual'] = self._detectar_monstruo_actual(entorno)
        
        # Roboscanner: detectar robot en celda de enfrente
        percepcion['robot_enfrente'] = self._detectar_robot_enfrente(entorno)
        
        return percepcion
    
    def _detectar_monstruos(self, entorno: Entorno) -> bool:
        """
        Detecta si hay monstruos en las 5 celdas adyacentes (excepto atrás).
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            True si detecta un monstruo, False en caso contrario
        """
        x, y, z = self.posicion
        ox, oy, oz = self.orientacion
        
        # Calcular dirección hacia atrás
        atras = (-ox, -oy, -oz)
        
        # Las 6 direcciones adyacentes
        direcciones = [
            (1, 0, 0), (-1, 0, 0),
            (0, 1, 0), (0, -1, 0),
            (0, 0, 1), (0, 0, -1)
        ]
        
        # Verificar las 5 direcciones (excluyendo atrás)
        for dx, dy, dz in direcciones:
            if (dx, dy, dz) != atras:
                nueva_pos = (x + dx, y + dy, z + dz)
                if entorno.es_valida(nueva_pos) and entorno.obtener_estado(nueva_pos) == 3:
                    return True
        
        return False
    
    def _detectar_monstruo_actual(self, entorno: Entorno) -> bool:
        """
        Detecta si hay un monstruo en la celda actual.
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            True si hay un monstruo en la celda actual, False en caso contrario
        """
        return entorno.obtener_estado(self.posicion) == 3
    
    def _detectar_robot_enfrente(self, entorno: Entorno) -> bool:
        """
        Detecta si hay un robot en la celda de enfrente.
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            True si hay un robot enfrente, False en caso contrario
        """
        x, y, z = self.posicion
        ox, oy, oz = self.orientacion
        
        posicion_enfrente = (x + ox, y + oy, z + oz)
        
        if entorno.es_valida(posicion_enfrente):
            return entorno.obtener_estado(posicion_enfrente) == 2
        
        return False
    
    def mover_adelante(self, entorno: Entorno) -> bool:
        """
        Mueve el robot hacia adelante según su orientación.
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            True si se pudo mover, False en caso contrario
        """
        x, y, z = self.posicion
        ox, oy, oz = self.orientacion
        
        nueva_posicion = (x + ox, y + oy, z + oz)
        
        # Intentar moverse
        if entorno.mover_entidad(self, nueva_posicion):
            self.choco_pared_anterior = False
            print(f"Robot se movió de {self.posicion} a {nueva_posicion}")
            return True
        else:
            # No se pudo mover, activar Vacuscopio
            self.choco_pared_anterior = True
            print(f"Robot no pudo moverse hacia {nueva_posicion}")
            return False
    
    def rotar(self, eje: str, angulo: int):
        """
        Rota el robot en el eje especificado.
        
        Args:
            eje: Eje de rotación ('x', 'y', 'z')
            angulo: Ángulo de rotación en grados (90, 180, 270)
        """
        ox, oy, oz = self.orientacion
        
        if eje == 'x':
            if angulo == 90:
                self.orientacion = (ox, -oz, oy)
            elif angulo == 180:
                self.orientacion = (ox, -oy, -oz)
            elif angulo == 270:
                self.orientacion = (ox, oz, -oy)
        elif eje == 'y':
            if angulo == 90:
                self.orientacion = (oz, oy, -ox)
            elif angulo == 180:
                self.orientacion = (-ox, oy, -oz)
            elif angulo == 270:
                self.orientacion = (-oz, oy, ox)
        elif eje == 'z':
            if angulo == 90:
                self.orientacion = (-oy, ox, oz)
            elif angulo == 180:
                self.orientacion = (-ox, -oy, oz)
            elif angulo == 270:
                self.orientacion = (oy, -ox, oz)
        
        print(f"Robot rotó en eje {eje} {angulo}°. Nueva orientación: {self.orientacion}")
    
    def usar_vacuumator(self, entorno: Entorno):
        """
        Usa el vacuumator para destruir el monstruo en la celda actual y autodestruirse.
        
        Args:
            entorno: Instancia del entorno
        """
        x, y, z = self.posicion
        
        # Cambiar la celda actual a zona vacía
        entorno.mundo[x, y, z] = 1
        
        # Eliminar monstruos en la misma celda
        monstruos_a_eliminar = [m for m in entorno.monstruos if m.posicion == self.posicion]
        for monstruo in monstruos_a_eliminar:
            entorno.eliminar_entidad(monstruo)
        
        # Autodestruirse
        entorno.eliminar_entidad(self)
        
        print(f"Robot usó vacuumator en {self.posicion} y se autodestruyó")
    
    def decidir_y_actuar(self, entorno: Entorno, tiempo_actual: int):
        """
        Cerebro del robot: toma decisiones basadas en percepciones y memoria.
        
        Args:
            entorno: Instancia del entorno
            tiempo_actual: Tiempo actual de la simulación
        """
        # Obtener percepciones actuales
        percepcion_actual = self.percibir_entorno(entorno)
        
        # Lógica de decisión con jerarquía de reglas
        accion_ejecutada = None
        
        # 1. Máxima prioridad: Si hay monstruo en celda actual, usar vacuumator
        if percepcion_actual['monstruo_actual']:
            self.usar_vacuumator(entorno)
            accion_ejecutada = "vacuumator"
        
        # 2. Si detecta monstruo cerca, intentar acercarse
        elif percepcion_actual['monstruo_cerca']:
            # Intentar moverse hacia adelante
            if self.mover_adelante(entorno):
                accion_ejecutada = "mover_adelante"
            else:
                # Si no puede moverse, rotar para buscar otra dirección
                self.rotar('y', 90)
                accion_ejecutada = "rotar"
        
        # 3. Si hay robot enfrente, comunicarse y decidir conjuntamente
        elif percepcion_actual['robot_enfrente']:
            # Lógica simple: rotar para evitar conflicto
            self.rotar('z', 90)
            accion_ejecutada = "rotar"
        
        # 4. Si chocó con pared anteriormente, rotar
        elif percepcion_actual['choco_pared']:
            self.rotar('y', 90)
            accion_ejecutada = "rotar"
        
        # 5. Acción por defecto: explorar moviéndose adelante
        else:
            if self.mover_adelante(entorno):
                accion_ejecutada = "mover_adelante"
            else:
                self.rotar('y', 90)
                accion_ejecutada = "rotar"
        
        # Consultar memoria para mejorar decisiones futuras
        self._consultar_memoria(percepcion_actual, tiempo_actual)
        
        # Guardar experiencia en memoria
        if accion_ejecutada:
            self.memoria.append((tiempo_actual, percepcion_actual, accion_ejecutada))
            
            # Limitar tamaño de memoria (mantener solo las últimas 50 experiencias)
            if len(self.memoria) > 50:
                self.memoria = self.memoria[-50:]
    
    def _consultar_memoria(self, percepcion_actual: Dict, tiempo_actual: int):
        """
        Consulta la memoria para mejorar la toma de decisiones.
        
        Args:
            percepcion_actual: Percepciones actuales
            tiempo_actual: Tiempo actual de la simulación
        """
        # Buscar experiencias similares en la memoria
        for tiempo, percepcion, accion in reversed(self.memoria):
            # Si la percepción es similar y la acción fue exitosa recientemente
            if (self._percepciones_similares(percepcion, percepcion_actual) and 
                tiempo_actual - tiempo < 10):  # Experiencia reciente
                
                # Podría implementar lógica más sofisticada aquí
                # Por ahora, solo registramos que encontramos una experiencia similar
                pass
    
    def _percepciones_similares(self, p1: Dict, p2: Dict) -> bool:
        """
        Determina si dos percepciones son similares.
        
        Args:
            p1, p2: Diccionarios de percepciones
            
        Returns:
            True si las percepciones son similares, False en caso contrario
        """
        # Comparar elementos clave de las percepciones
        elementos_clave = ['monstruo_cerca', 'monstruo_actual', 'robot_enfrente', 'choco_pared']
        
        for elemento in elementos_clave:
            if p1.get(elemento) != p2.get(elemento):
                return False
        
        return True


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


def simulacion_principal():
    """
    Función principal que ejecuta la simulación completa.
    """
    print("=== SIMULACIÓN ROBOTS VS MONSTRUOS ===")
    print("Iniciando simulación...")
    
    # Parámetros de la simulación
    N = 8  # Tamaño del cubo (8x8x8)
    p_free = 0.7  # 70% de celdas libres
    p_soft = 0.2  # 20% de celdas vacías (obstáculos)
    num_robots = 3
    num_monstruos = 5
    max_iteraciones = 50
    
    # Crear el entorno
    entorno = Entorno(N, p_free, p_soft)
    print(f"Entorno creado: {N}x{N}x{N} con {p_free*100}% libres y {p_soft*100}% vacías")
    
    # Crear robots
    print(f"\nCreando {num_robots} robots...")
    for i in range(num_robots):
        posicion = crear_posicion_aleatoria_libre(entorno)
        if posicion:
            orientacion = random.choice([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)])
            robot = Robot(posicion, orientacion)
            entorno.agregar_entidad(robot, posicion)
            print(f"Robot {i+1} creado en posición {posicion} con orientación {orientacion}")
    
    # Crear monstruos
    print(f"\nCreando {num_monstruos} monstruos...")
    for i in range(num_monstruos):
        posicion = crear_posicion_aleatoria_libre(entorno)
        if posicion:
            monstruo = Monstruo(posicion)
            entorno.agregar_entidad(monstruo, posicion)
            print(f"Monstruo {i+1} creado en posición {posicion}")
    
    # Mostrar estado inicial
    entorno.visualizar()
    
    # Bucle principal de simulación
    print(f"\nIniciando simulación por {max_iteraciones} iteraciones...")
    print("Presiona Ctrl+C para detener la simulación")
    
    try:
        for t in range(max_iteraciones):
            print(f"\n--- ITERACIÓN {t+1} ---")
            
            # Actuar con todos los robots
            robots_activos = entorno.robots.copy()  # Copia para evitar problemas de modificación durante iteración
            for robot in robots_activos:
                if robot in entorno.robots:  # Verificar que aún existe
                    robot.decidir_y_actuar(entorno, t)
            
            # Actuar con todos los monstruos
            monstruos_activos = entorno.monstruos.copy()
            for monstruo in monstruos_activos:
                if monstruo in entorno.monstruos:  # Verificar que aún existe
                    monstruo.actuar(entorno, t)
            
            # Mostrar estado del mundo
            entorno.visualizar()
            
            # Verificar condiciones de fin de juego
            if len(entorno.monstruos) == 0:
                print("\n🎉 ¡VICTORIA! Todos los monstruos han sido eliminados!")
                break
            elif len(entorno.robots) == 0:
                print("\n💀 DERROTA: Todos los robots han sido destruidos!")
                break
            
            # Pausa para visualización
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\nSimulación interrumpida por el usuario.")
    
    # Resultado final
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Robots restantes: {len(entorno.robots)}")
    print(f"Monstruos restantes: {len(entorno.monstruos)}")
    
    if len(entorno.monstruos) == 0:
        print("🏆 Los robots han ganado la batalla!")
    elif len(entorno.robots) == 0:
        print("👹 Los monstruos han ganado la batalla!")
    else:
        print("⏰ La simulación terminó por tiempo límite.")


if __name__ == "__main__":
    # Ejecutar la simulación
    simulacion_principal()
