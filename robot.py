#!/usr/bin/env python3
"""
Clase Robot
Representa un robot inteligente con sensores, effectores y memoria.
"""

from typing import List, Tuple, Dict


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
        
    def percibir_entorno(self, entorno) -> Dict:
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
    
    def _detectar_monstruos(self, entorno) -> bool:
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
    
    def _detectar_monstruo_actual(self, entorno) -> bool:
        """
        Detecta si hay un monstruo en la celda actual.
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            True si hay un monstruo en la celda actual, False en caso contrario
        """
        return entorno.obtener_estado(self.posicion) == 3
    
    def _detectar_robot_enfrente(self, entorno) -> bool:
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
    
    def mover_adelante(self, entorno) -> bool:
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
    
    def usar_vacuumator(self, entorno):
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
    
    def decidir_y_actuar(self, entorno, tiempo_actual: int):
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
