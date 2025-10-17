# Guía de Desarrollo: Robots vs. Monstruos (Examen MIA-103)
Este plan está diseñado para que construyas la simulación de forma ordenada, desde la base (el mundo) hasta la inteligencia de los agentes.

**Paso 1: Construir el Mundo (La Clase Entorno)**
Antes de tener robots o monstruos, necesitas un lugar donde puedan existir.

- **Crea una clase Entorno:**
    - **__init__(self, N, p_free, p_soft):** El constructor debe crear el mundo.
        - Usa una lista de listas de listas en Python, o mejor aún, un array de 3 dimensiones de NumPy (np.zeros((N, N, N))) para representar el espacio de N³ cubos.
        - Rellena el espacio aleatoriamente según los porcentajes p_free y p_soft. Puedes asignar números para cada tipo de zona: 0 para libre, 1 para vacía.
        - Guarda también una lista para los robots y otra para los monstruos que existirán en el entorno.
    - **Métodos útiles:**
        - agregar_entidad(self, entidad, posicion): Para colocar un robot o monstruo en una posición inicial aleatoria (y libre).
        - es_valida(self, posicion): Para verificar si una coordenada (x, y, z) está dentro de los límites y no es una "Zona Vacía".
        - obtener_estado(self, posicion): Devuelve qué hay en una coordenada específica.
        - visualizar_compacto(self): Método que muestra tres vistas ortogonales (XY, XZ, YZ) del cubo 3D para visualización completa.

**Paso 2: Crear al Agente Simple (La Clase Monstruo)**

- **Crea una clase Monstruo:**
    - **__init__(self, posicion_inicial, K=3):** Necesita su posición y K (frecuencia de movimiento, por defecto cada 3 iteraciones).
    - **actuar(self, entorno, k_iteracion_actual):** Este es su "cerebro".
        - Recibe el entorno para poder "ver" a su alrededor.
        - Cada K iteraciones (if k_iteracion_actual % K == 0:), el monstruo intenta moverse.
        - Elige una de las 6 direcciones adyacentes al azar.
        - Usa el método entorno.es_valida() para ver si se puede mover ahí.
        - Si puede, actualiza su propia posición.
    - **Propiedad especial:** Los monstruos irradian energía en su entorno inmediato (6 lados), detectable por el Monstroscopio.

**Paso 3: Construir al Agente Inteligente (La Clase Robot)**

- **Crea una clase Robot:**
    1. **__init__(self, posicion_inicial, orientacion_inicial):** Necesita su posición y su orientación (vector como (1, 0, 0) para "adelante en X").
    2. **Atributos importantes:**
        - memoria: Lista para guardar experiencias (tiempo, percepcion, accion).
        - orientacion: Vector que define hacia dónde "mira" el robot (su frente).
        - direccion_movimiento: Dirección actual de movimiento (puede diferir de orientación).
        - choco_pared_anterior: Flag para el Vacuscopio.
        - destruido: Estado de destrucción del robot.

- **Implementa los Sensores (como métodos):**
    1. **percibir_entorno(self, entorno):** Método principal que llama a todos los sensores.
        - **Giroscopio:** Conoce su orientación actual.
        - **Monstroscopio:** Detecta energía irradiada por monstruos en las 5 celdas adyacentes (excluyendo la trasera según orientación).
        - **Vacuscopio:** Se activa después de un movimiento fallido (detecta obstáculos).
        - **Energómetro espectral:** Detecta monstruos directamente en la celda actual.
        - **Roboscanner:** Detecta robots en la celda de enfrente según orientación.
    2. Devuelve un diccionario con todas las percepciones: {"monstruo_cerca": True, "monstruo_actual": False, "robot_enfrente": False, ...}.

- **Implementa los Efectores (como métodos):**
    1. **mover_adelante(self, entorno):** Se mueve según su orientación actual.
        - Calcula nueva posición basada en orientación.
        - Puede moverse a celdas libres (0) o con monstruos (3).
        - Si falla, activa el Vacuscopio para la siguiente iteración.
    2. **rotar(self, eje, angulo):** Cambia su orientación en ejes globales (X, Y, Z).
        - Actualiza tanto orientacion como direccion_movimiento.
    3. **usar_vacuumator(self, entorno):** Arma de destrucción final.
        - Requiere validaciones de seguridad.
        - Destruye monstruo en celda actual.
        - Autodestruye el robot.
        - Convierte la celda en Zona Vacía (obstáculo).

- **Implementa el Cerebro con Tres Modos de Operación:**
    El método **decidir_y_actuar(self, entorno, tiempo)** implementa una jerarquía de modos:

    1. **💥 MODO ATAQUE (Máxima Prioridad):**
        - Se activa cuando `monstruo_actual` es True.
        - Ejecuta la secuencia completa de destrucción:
            - ✅ Paso 1: INGRESAR al cubo del monstruo (ya completado)
            - ✅ Paso 2: DETECTAR con Energómetro espectral (ya completado)
            - 🚀 Paso 3: ACTIVAR Vacuumator
        - Resultado: Robot y monstruo destruidos, celda convertida en Zona Vacía.

    2. **🎯 MODO CAZA (Alta Prioridad):**
        - Se activa cuando `monstruo_cerca` es True (energía irradiada detectada).
        - Implementa persecución inteligente:
            - Encuentra el monstruo más cercano usando distancia Manhattan.
            - Calcula dirección hacia el monstruo.
            - Intenta moverse directamente hacia él.
            - Si no puede moverse, reorienta hacia el monstruo.
        - Permite movimiento hacia celdas ocupadas por monstruos.

    3. **🔍 MODO EXPLORACIÓN (Prioridad por Defecto):**
        - Se activa cuando no hay monstruos detectados.
        - Implementa exploración básica:
            - Intenta moverse hacia adelante.
            - Si encuentra obstáculo, rota para cambiar dirección.
            - Usa memoria del Vacuscopio para evitar bucles.

- **Sistema de Memoria y Aprendizaje:**
    - Guarda cada experiencia: (tiempo, percepcion, accion).
    - Consulta memoria antes de decisiones críticas.
    - Implementa jerarquía de reglas basada en experiencias pasadas.

**Paso 4: El Simulador (El Bucle Principal)**
Este es el script que une todo.

1. Crea una instancia del Entorno con parámetros configurables.
2. Crea N robots y M monstruos y añádelos al entorno en posiciones aleatorias.
3. Inicia un bucle principal: for t in range(max_iteraciones):
    - Dentro del bucle, recorre tu lista de robots y llama a robot.decidir_y_actuar(entorno, t).
    - Recorre tu lista de monstruos y llama a monstruo.actuar(entorno, t).
    - Actualiza el estado del entorno (elimina entidades destruidas).
    - Llama a entorno.visualizar_compacto() para ver el estado.
    - time.sleep(1) para control de velocidad.

**Paso 5: Visualización 3D (Opcional pero Recomendado)**
- Implementa visualización 3D usando matplotlib.
- Muestra robots con vectores de orientación.
- Muestra monstruos con energía irradiada (cubos verdes suaves).
- Incluye leyenda detallada con emojis.
- Permite seguimiento en tiempo real de la simulación.

**Características Implementadas:**
- ✅ Distinción clara entre orientación y dirección de movimiento.
- ✅ Sistema de sensores completo y realista.
- ✅ Tres modos de operación con jerarquía de prioridades.
- ✅ Persecución inteligente de monstruos.
- ✅ Sistema de destrucción completo (Vacuumator).
- ✅ Memoria y aprendizaje básico.
- ✅ Visualización 2D compacta y 3D completa.
- ✅ Manejo de obstáculos y zonas vacías.
- ✅ Frecuencias de movimiento diferenciadas (robots: 100%, monstruos: 33%).
