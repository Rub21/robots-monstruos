#!/usr/bin/env python3
"""
Clase Robot
Representa un robot inteligente con sensores, effectores y memoria.
"""

from typing import List, Tuple, Dict

# Códigos de colores ANSI para terminal
class Colores:
    RESET = '\033[0m'
    ROJO = '\033[91m'      # Robots
    AMARILLO = '\033[93m'  # Advertencias
    CYAN = '\033[96m'      # Información


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
            orientacion_inicial: Vector que define la orientación del robot (hacia dónde "mira" su frente)
                                 Ej: (1, 0, 0) significa que su frente apunta hacia +X
        """
        self.posicion = posicion_inicial
        self.orientacion = orientacion_inicial  # Hacia dónde "mira" el robot
        self.direccion_movimiento = orientacion_inicial  # Dirección de movimiento actual
        self.memoria: List[Tuple[int, Dict, str]] = []  # (tiempo, percepción, acción)
        self.choco_pared_anterior = False  # Para el Vacuscopio
        self.destruido = False  # Estado de destrucción del robot
        
    def percibir_entorno(self, entorno) -> Dict:
        """
        Sistema de percepción del robot que activa todos sus sensores.
        
        Args:
            entorno: Instancia del entorno donde se encuentra
            
        Returns:
            Diccionario con toda la información percibida
        """
        percepcion = {}
        
        # Giroscopio: orientación actual (hacia dónde mira el robot)
        percepcion['orientacion'] = self.orientacion
        percepcion['direccion_movimiento'] = self.direccion_movimiento
        
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
        Detecta energía de monstruos en las 5 celdas adyacentes (excepto atrás según orientación).
        
        Los monstruos son entidades energéticas que irradian energía en los 6 lados.
        El Monstroscopio detecta esta energía irradiada, no necesariamente al monstruo directamente.
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            True si detecta energía de monstruo, False en caso contrario
        """
        x, y, z = self.posicion
        ox, oy, oz = self.orientacion
        
        # Calcular dirección hacia atrás según la orientación del robot
        atras = (-ox, -oy, -oz)
        
        # Las 6 direcciones adyacentes en el sistema global
        direcciones = [
            (1, 0, 0), (-1, 0, 0),  # +X, -X
            (0, 1, 0), (0, -1, 0),  # +Y, -Y
            (0, 0, 1), (0, 0, -1)   # +Z, -Z
        ]
        
        # Verificar las 5 direcciones (excluyendo atrás según orientación)
        for dx, dy, dz in direcciones:
            if (dx, dy, dz) != atras:
                nueva_pos = (x + dx, y + dy, z + dz)
                
                # Verificar si hay energía de monstruo en esta celda
                if self._detectar_energia_monstruo(entorno, nueva_pos):
                    return True
        
        return False
    
    def _detectar_energia_monstruo(self, entorno, posicion: Tuple[int, int, int]) -> bool:
        """
        Detecta si hay energía de monstruo en una posición específica.
        
        Los monstruos irradian energía en los 6 lados, por lo que:
        1. Si hay un monstruo directamente en la celda, se detecta energía
        2. Si hay un monstruo en cualquier celda adyacente a esta posición, 
           también se detecta energía (por la irradiación)
        
        Args:
            entorno: Instancia del entorno
            posicion: Posición a verificar
            
        Returns:
            True si detecta energía de monstruo, False en caso contrario
        """
        if not entorno.es_valida(posicion):
            return False
        
        # 1. Verificar si hay un monstruo directamente en esta celda
        if entorno.obtener_estado(posicion) == 3:  # Monstruo directo
            return True
        
        # 2. Verificar si hay un monstruo en las celdas adyacentes a esta posición
        # (que irradiaría energía hacia esta celda)
        px, py, pz = posicion
        
        # Las 6 direcciones adyacentes para buscar monstruos que irradien energía
        direcciones_irradiacion = [
            (1, 0, 0), (-1, 0, 0),  # +X, -X
            (0, 1, 0), (0, -1, 0),  # +Y, -Y
            (0, 0, 1), (0, 0, -1)   # +Z, -Z
        ]
        
        for dx, dy, dz in direcciones_irradiacion:
            pos_monstruo = (px + dx, py + dy, pz + dz)
            
            # Si hay un monstruo en una celda adyacente, irradia energía hacia la posición actual
            if (entorno.es_valida(pos_monstruo) and 
                entorno.obtener_estado(pos_monstruo) == 3):
                return True
        
        return False
    
    def _perseguir_monstruo_cercano(self, entorno) -> bool:
        """
        Intenta perseguir al monstruo más cercano detectado.
        
        Calcula la dirección hacia el monstruo más cercano y se mueve hacia él.
        Si no puede moverse directamente, intenta reorientarse.
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            True si se movió exitosamente, False en caso contrario
        """
        # Encontrar el monstruo más cercano
        monstruo_cercano = self._encontrar_monstruo_cercano(entorno)
        if not monstruo_cercano:
            return False
        
        # Calcular dirección hacia el monstruo
        direccion_hacia_monstruo = self._calcular_direccion_hacia(monstruo_cercano.posicion)
        
        # Intentar moverse en esa dirección
        if self._intentar_moverse_en_direccion(entorno, direccion_hacia_monstruo):
            return True
        
        # Si no puede moverse directamente, intentar reorientarse hacia el monstruo
        if self._reorientarse_hacia_monstruo(entorno, monstruo_cercano.posicion):
            return True
        
        return False
    
    def _encontrar_monstruo_cercano(self, entorno):
        """
        Encuentra el monstruo más cercano al robot.
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            El monstruo más cercano o None si no hay ninguno
        """
        if not entorno.monstruos:
            return None
        
        robot_pos = self.posicion
        monstruo_cercano = None
        distancia_minima = float('inf')
        
        for monstruo in entorno.monstruos:
            # Calcular distancia Manhattan
            distancia = sum(abs(a - b) for a, b in zip(robot_pos, monstruo.posicion))
            if distancia < distancia_minima:
                distancia_minima = distancia
                monstruo_cercano = monstruo
        
        return monstruo_cercano
    
    def _calcular_direccion_hacia(self, posicion_destino: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """
        Calcula la dirección hacia una posición específica.
        
        Args:
            posicion_destino: Posición objetivo
            
        Returns:
            Vector de dirección normalizado
        """
        robot_pos = self.posicion
        direccion = tuple(dest - orig for dest, orig in zip(posicion_destino, robot_pos))
        
        # Normalizar la dirección (mantener solo la dirección principal)
        direccion_normalizada = [0, 0, 0]
        max_abs = max(abs(d) for d in direccion)
        
        if max_abs > 0:
            for i, d in enumerate(direccion):
                if abs(d) == max_abs:
                    direccion_normalizada[i] = 1 if d > 0 else -1
                    break
        
        return tuple(direccion_normalizada)
    
    def _intentar_moverse_en_direccion(self, entorno, direccion: Tuple[int, int, int]) -> bool:
        """
        Intenta moverse en una dirección específica.
        
        Args:
            entorno: Instancia del entorno
            direccion: Dirección de movimiento
            
        Returns:
            True si se movió exitosamente, False en caso contrario
        """
        nueva_posicion = tuple(self.posicion[i] + direccion[i] for i in range(3))
        
        if entorno.es_valida(nueva_posicion):
            estado_celda = entorno.obtener_estado(nueva_posicion)
            
            # Puede moverse a celdas libres (0) o con monstruos (3)
            if estado_celda == 0 or estado_celda == 3:
                # Actualizar posición del robot
                self.posicion = nueva_posicion
                entorno.mover_entidad(self, nueva_posicion)
                return True
        
        return False
    
    def _reorientarse_hacia_monstruo(self, entorno, posicion_monstruo: Tuple[int, int, int]) -> bool:
        """
        Reorienta el robot hacia la posición del monstruo.
        
        Args:
            entorno: Instancia del entorno
            posicion_monstruo: Posición del monstruo
            
        Returns:
            True si se reorientó exitosamente, False en caso contrario
        """
        direccion_hacia_monstruo = self._calcular_direccion_hacia(posicion_monstruo)
        
        # Si ya está orientado hacia el monstruo, no hacer nada
        if self.orientacion == direccion_hacia_monstruo:
            return False
        
        # Reorientar hacia el monstruo
        self.orientacion = direccion_hacia_monstruo
        self.direccion_movimiento = direccion_hacia_monstruo
        
        print(f"{Colores.CYAN}   🔄 Reorientando hacia monstruo en {posicion_monstruo}{Colores.RESET}")
        return True
    
    def _validar_activacion_vacuumator(self, entorno) -> bool:
        """
        Valida que sea seguro activar el Vacuumator.
        
        Validaciones de seguridad:
        1. Debe haber un monstruo en la celda actual (confirmado por Energómetro espectral)
        2. El robot no debe estar ya destruido
        3. La celda debe ser válida
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            True si es seguro activar el Vacuumator, False en caso contrario
        """
        # Validación 1: Robot no debe estar destruido
        if hasattr(self, 'destruido') and self.destruido:
            print(f"{Colores.AMARILLO}⚠️  VALIDACIÓN FALLIDA: Robot ya está destruido{Colores.RESET}")
            return False
        
        # Validación 2: Debe haber un monstruo en la celda actual
        if not self._detectar_monstruo_actual(entorno):
            print(f"{Colores.AMARILLO}⚠️  VALIDACIÓN FALLIDA: No hay monstruo en la celda actual{Colores.RESET}")
            return False
        
        # Validación 3: La posición debe ser válida
        if not entorno.es_valida(self.posicion):
            print(f"{Colores.AMARILLO}⚠️  VALIDACIÓN FALLIDA: Posición inválida{Colores.RESET}")
            return False
        
        # Validación 4: Confirmar que el monstruo existe en la lista de monstruos
        monstruo_encontrado = False
        for monstruo in entorno.monstruos:
            if monstruo.posicion == self.posicion:
                monstruo_encontrado = True
                break
        
        if not monstruo_encontrado:
            print(f"{Colores.AMARILLO}⚠️  VALIDACIÓN FALLIDA: Monstruo no encontrado en lista de entidades{Colores.RESET}")
            return False
        
        print(f"{Colores.CYAN}✅ VALIDACIONES DE SEGURIDAD COMPLETADAS{Colores.RESET}")
        return True
    
    def obtener_info_deteccion_monstruos(self, entorno) -> Dict:
        """
        Obtiene información detallada sobre la detección de energía de monstruos.
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            Diccionario con información detallada de la detección
        """
        x, y, z = self.posicion
        ox, oy, oz = self.orientacion
        
        # Calcular dirección hacia atrás según la orientación del robot
        atras = (-ox, -oy, -oz)
        
        # Las 6 direcciones adyacentes en el sistema global
        direcciones = [
            (1, 0, 0), (-1, 0, 0),  # +X, -X
            (0, 1, 0), (0, -1, 0),  # +Y, -Y
            (0, 0, 1), (0, 0, -1)   # +Z, -Z
        ]
        
        info_deteccion = {
            'posicion_robot': self.posicion,
            'orientacion_robot': self.orientacion,
            'direccion_atras': atras,
            'celdas_verificadas': [],
            'energia_detectada': False,
            'fuentes_energia': []
        }
        
        # Verificar las 5 direcciones (excluyendo atrás según orientación)
        for dx, dy, dz in direcciones:
            if (dx, dy, dz) != atras:
                nueva_pos = (x + dx, y + dy, z + dz)
                
                celda_info = {
                    'posicion': nueva_pos,
                    'direccion': (dx, dy, dz),
                    'tiene_energia': False,
                    'fuentes': []
                }
                
                # Verificar si hay energía de monstruo en esta celda
                if self._detectar_energia_monstruo(entorno, nueva_pos):
                    celda_info['tiene_energia'] = True
                    info_deteccion['energia_detectada'] = True
                    
                    # Encontrar las fuentes de energía
                    px, py, pz = nueva_pos
                    direcciones_irradiacion = [
                        (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)
                    ]
                    
                    for dix, diy, diz in direcciones_irradiacion:
                        pos_monstruo = (px + dix, py + diy, pz + diz)
                        if (entorno.es_valida(pos_monstruo) and 
                            entorno.obtener_estado(pos_monstruo) == 3):
                            celda_info['fuentes'].append(pos_monstruo)
                            info_deteccion['fuentes_energia'].append(pos_monstruo)
                
                info_deteccion['celdas_verificadas'].append(celda_info)
        
        return info_deteccion
    
    def _detectar_monstruo_actual(self, entorno) -> bool:
        """
        Energómetro espectral: Detecta si hay un monstruo en la celda actual.
        
        Este sensor es crucial para la destrucción de monstruos. Solo se activa
        cuando el robot está en la misma celda que el monstruo, permitiendo
        la activación segura del Vacuumator.
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            True si hay un monstruo en la celda actual, False en caso contrario
        """
        estado_celda = entorno.obtener_estado(self.posicion)
        hay_monstruo = estado_celda == 3
        
        if hay_monstruo:
            print(f"{Colores.ROJO}🔬 Energómetro espectral: ¡MONSTRUO DETECTADO EN CELDA ACTUAL!{Colores.RESET}")
        
        return hay_monstruo
    
    def _detectar_robot_enfrente(self, entorno) -> bool:
        """
        Detecta si hay un robot en la celda de enfrente según la orientación del robot.
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            True si hay un robot enfrente, False en caso contrario
        """
        x, y, z = self.posicion
        ox, oy, oz = self.orientacion
        
        # La posición enfrente según la orientación del robot
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
        
        # Calcular nueva posición según la orientación del robot
        nueva_posicion = (x + ox, y + oy, z + oz)
        
        # Intentar moverse
        if entorno.mover_entidad(self, nueva_posicion):
            self.choco_pared_anterior = False
            print(f"{Colores.ROJO}Robot se movió de {self.posicion} a {nueva_posicion}{Colores.RESET}")
            return True
        else:
            # No se pudo mover, activar Vacuscopio
            self.choco_pared_anterior = True
            print(f"{Colores.AMARILLO}Robot no pudo moverse hacia {nueva_posicion}{Colores.RESET}")
            return False
    
    # EFECTORES: rotar, cambiar_direccion_movimiento, usar_vacuumator
    def rotar(self, eje: str, angulo: int):
        """
        Rota el robot en el eje especificado, cambiando su orientación.
        
        Args:
            eje: Eje de rotación ('x', 'y', 'z') - eje global alrededor del cual rotar
            angulo: Ángulo de rotación en grados (90, 180, 270)
        """
        ox, oy, oz = self.orientacion
        
        # Rotaciones alrededor de ejes globales
        if eje == 'x':  # Rotación alrededor del eje X global
            if angulo == 90:
                self.orientacion = (ox, -oz, oy)
            elif angulo == 180:
                self.orientacion = (ox, -oy, -oz)
            elif angulo == 270:
                self.orientacion = (ox, oz, -oy)
        elif eje == 'y':  # Rotación alrededor del eje Y global
            if angulo == 90:
                self.orientacion = (oz, oy, -ox)
            elif angulo == 180:
                self.orientacion = (-ox, oy, -oz)
            elif angulo == 270:
                self.orientacion = (-oz, oy, ox)
        elif eje == 'z':  # Rotación alrededor del eje Z global
            if angulo == 90:
                self.orientacion = (-oy, ox, oz)
            elif angulo == 180:
                self.orientacion = (-ox, -oy, oz)
            elif angulo == 270:
                self.orientacion = (oy, -ox, oz)
        
        # Actualizar también la dirección de movimiento para que coincida con la orientación
        self.direccion_movimiento = self.orientacion
        
        print(f"{Colores.CYAN}Robot rotó en eje {eje} {angulo}°. Nueva orientación: {self.orientacion}{Colores.RESET}")
    
    def cambiar_direccion_movimiento(self, nueva_direccion: Tuple[int, int, int]):
        """
        Cambia la dirección de movimiento sin cambiar la orientación del robot.
        
        Args:
            nueva_direccion: Nueva dirección de movimiento (x, y, z)
        """
        self.direccion_movimiento = nueva_direccion
        print(f"{Colores.CYAN}Robot cambió dirección de movimiento a: {nueva_direccion}{Colores.RESET}")
    
    def obtener_orientacion_texto(self) -> str:
        """
        Obtiene una representación textual de la orientación del robot.
        
        Returns:
            String que describe hacia dónde mira el robot
        """
        ox, oy, oz = self.orientacion
        
        if ox == 1:
            return "mira hacia +X"
        elif ox == -1:
            return "mira hacia -X"
        elif oy == 1:
            return "mira hacia +Y"
        elif oy == -1:
            return "mira hacia -Y"
        elif oz == 1:
            return "mira hacia +Z"
        elif oz == -1:
            return "mira hacia -Z"
        else:
            return f"orientación compleja: {self.orientacion}"
    
    def usar_vacuumator(self, entorno):
        """
        Vacuumator: Poderosa arma de destrucción que convierte la zona en Zona Vacía.
        
        Proceso de destrucción:
        1. Validaciones de seguridad
        2. Destruye completamente al monstruo en la celda actual
        3. Destruye completamente al robot (autodestrucción)
        4. Convierte la celda en Zona Vacía (obstáculo)
        
        Args:
            entorno: Instancia del entorno
            
        Returns:
            True si la destrucción fue exitosa, False si falló la validación
        """
        # VALIDACIONES DE SEGURIDAD
        if not self._validar_activacion_vacuumator(entorno):
            print(f"{Colores.AMARILLO}🚫 VACUUMATOR NO ACTIVADO: Validaciones de seguridad fallaron{Colores.RESET}")
            return False
        
        x, y, z = self.posicion
        
        print(f"{Colores.ROJO}💥 VACUUMATOR ACTIVADO!{Colores.RESET}")
        print(f"{Colores.ROJO}   🔥 Destruyendo monstruo en posición {self.posicion}{Colores.RESET}")
        print(f"{Colores.ROJO}   🤖 Autodestrucción del robot iniciada{Colores.RESET}")
        print(f"{Colores.ROJO}   ⚫ Convirtiendo celda en Zona Vacía{Colores.RESET}")
        
        # 1. Destruir monstruo (si existe en la celda)
        monstruo_encontrado = None
        for monstruo in entorno.monstruos:
            if monstruo.posicion == self.posicion:
                monstruo_encontrado = monstruo
                break
        
        if monstruo_encontrado:
            entorno.monstruos.remove(monstruo_encontrado)
            print(f"{Colores.ROJO}   👹 Monstruo eliminado del entorno{Colores.RESET}")
        
        # 2. Destruir robot (autodestrucción)
        if self in entorno.robots:
            entorno.robots.remove(self)
            print(f"{Colores.ROJO}   🤖 Robot eliminado del entorno{Colores.RESET}")
        
        # 3. Convertir celda en Zona Vacía (obstáculo)
        entorno.mundo[x, y, z] = 1
        
        # 4. Marcar robot como destruido
        self.destruido = True
        
        print(f"{Colores.ROJO}💀 MISIÓN CUMPLIDA: Monstruo y robot destruidos en {self.posicion}{Colores.RESET}")
        return True
    
    def decidir_y_actuar(self, entorno, tiempo_actual: int):
        """
        Cerebro del robot: toma decisiones basadas en percepciones y memoria.
        
        Args:
            entorno: Instancia del entorno
            tiempo_actual: Tiempo actual de la simulación
        """
        # Obtener percepciones actuales
        percepcion_actual = self.percibir_entorno(entorno)
        
        # ========================================================================
        # LÓGICA DE DECISIÓN CON TRES MODOS DE OPERACIÓN DEL ROBOT
        # ========================================================================
        accion_ejecutada = None
        
        # ========================================================================
        # MODO ATAQUE: Máxima prioridad - Destrucción de monstruos
        # ========================================================================
        # Cuando el robot entra en el mismo cubo que un monstruo:
        # 1. Se detiene el movimiento
        # 2. Confirma con el Energómetro espectral
        # 3. Activa el Vacuumator para autodestruirse y eliminar al monstruo
        if percepcion_actual['monstruo_actual']:
            print(f"{Colores.CYAN}💥 MODO ATAQUE ACTIVADO:{Colores.RESET}")
            print(f"{Colores.CYAN}   ✅ Paso 1: INGRESAR al cubo del monstruo - COMPLETADO{Colores.RESET}")
            print(f"{Colores.CYAN}   ✅ Paso 2: DETECTAR con Energómetro espectral - COMPLETADO{Colores.RESET}")
            print(f"{Colores.CYAN}   🚀 Paso 3: ACTIVAR Vacuumator - INICIANDO{Colores.RESET}")
            
            self.usar_vacuumator(entorno)
            accion_ejecutada = "vacuumator"
        
        # ========================================================================
        # MODO CAZA: Alta prioridad - Persecución de monstruos
        # ========================================================================
        # Cuando el Monstroscopio detecta energía en cubos adyacentes:
        # 1. Cambia su movimiento para dirigirse intencionalmente hacia esa fuente
        # 2. Navega activamente hacia el monstruo
        # 3. Se reorienta si encuentra obstáculos
        elif percepcion_actual['monstruo_cerca']:
            print(f"{Colores.CYAN}🎯 MODO CAZA ACTIVADO:{Colores.RESET}")
            print(f"{Colores.CYAN}   🚀 Dirigiendo hacia fuente de energía detectada{Colores.RESET}")
            
            # Intentar perseguir al monstruo más cercano
            if self._perseguir_monstruo_cercano(entorno):
                accion_ejecutada = "perseguir_monstruo"
                print(f"{Colores.CYAN}   📍 Persiguiendo monstruo{Colores.RESET}")
            else:
                # Si no puede moverse, rotar para buscar otra dirección
                print(f"{Colores.CYAN}   🔄 Obstáculo detectado, reorientando{Colores.RESET}")
                self.rotar('y', 90)
                accion_ejecutada = "rotar"
        
        # ========================================================================
        # COMPORTAMIENTOS AUXILIARES: Evitar conflictos y obstáculos
        # ========================================================================
        # Si hay robot enfrente, comunicarse y decidir conjuntamente
        elif percepcion_actual['robot_enfrente']:
            # Lógica simple: rotar alrededor del eje Z para cambiar orientación lateralmente
            self.rotar('z', 90)
            accion_ejecutada = "rotar"
        
        # Si chocó con pared anteriormente, rotar
        elif percepcion_actual['choco_pared']:
            # Rotar alrededor del eje Y para cambiar la dirección de movimiento
            self.rotar('y', 90)
            accion_ejecutada = "rotar"
        
        # ========================================================================
        # MODO EXPLORACIÓN: Acción por defecto - Búsqueda activa
        # ========================================================================
        # Cuando el robot no detecta energía de monstruo en su entorno inmediato:
        # 1. Se mueve por el mapa siguiendo un patrón sistemático
        # 2. Avanza hacia adelante según su orientación
        # 3. Rota cuando encuentra obstáculos para buscar nuevas direcciones
        else:
            print(f"{Colores.CYAN}🔍 MODO EXPLORACIÓN ACTIVADO:{Colores.RESET}")
            print(f"{Colores.CYAN}   🗺️ Explorando mapa en busca de monstruos{Colores.RESET}")
            
            if self.mover_adelante(entorno):
                accion_ejecutada = "mover_adelante"
            else:
                # Si no puede moverse adelante, rotar para buscar nueva dirección
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
