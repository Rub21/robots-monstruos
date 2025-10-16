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
        - visualizar(self): (Opcional pero MUY recomendado) Un método simple que imprima una "rebanada" o capa del cubo para que puedas ver qué está pasando.

**Paso 2: Crear al Agente Simple (La Clase Monstruo)**
Empieza por el agente más fácil.

- **Crea una clase Monstruo:**
    - **__init__(self, posicion_inicial):** Solo necesita saber su posición.
    - **actuar(self, entorno, k_iteracion_actual):** Este es su "cerebro".
        - Recibe el entorno para poder "ver" a su alrededor.
        - Cada K iteraciones (puedes chequearlo con if k_iteracion_actual % K == 0:), el monstruo intenta moverse.
        - Elige una de las 6 direcciones adyacentes al azar.
        - Usa el método entorno.es_valida() para ver si se puede mover ahí.
        - Si puede, actualiza su propia posición.

**Paso 3: Construir al Agente Inteligente (La Clase Robot)**
Esta es la parte central del examen.

- **Crea una clase Robot:**
    1. **__init__(self, posicion_inicial, orientacion_inicial):** Necesita su posición y su orientación (puedes representarla con un vector, como (1, 0, 0) para "adelante en X").
    2. **Atributo memoria:** Crea una lista vacía self.memoria = [] para guardar las tuplas de (tiempo, percepcion, accion).
- **Implementa los Sensores (como métodos):**
    1. percibir_entorno(self, entorno): Este método principal llamará a todos los sensores "físicos".
        - **Giroscopio:** Ya conoces tu orientación.
        - **Monstroscopio:** Revisa las 5 celdas adyacentes (todas menos la de atrás) en el entorno. Devuelve True si detecta un monstruo, False si no.
        - **Vacuscopio:** Este se activa *después* de un intento de movimiento fallido. Lo manejaremos en la lógica principal.
        - **Energómetro espectral:** Revisa la celda *actual* en el entorno.
        - **Roboscanner:** Revisa la celda de *enfrente*.
    2. El método percibir_entorno debe devolver un resumen de todo lo que percibió, por ejemplo, un diccionario: {"monstruo_cerca": True, "robot_enfrente": False, ...}.
- **Implementa los Efectores (como métodos):**
    1. mover_adelante(self, entorno): Calcula la nueva posición según su orientación. Si entorno.es_valida() es False, no se mueve y activa la percepción del "Vacuscopio" para la siguiente iteración.
    2. rotar(self, eje, angulo): Cambia su vector de orientación.
    3. usar_vacuumator(self, entorno): Cambia la celda actual en el entorno a "Zona Vacía" y se autodestruye.
- **Implementa el Cerebro (el método decidir_y_actuar):**
    1. Llama a percibir_entorno() para obtener el estado actual (percepcion_actual).
    2. **Lógica de Decisión:** Aquí implementas las reglas. Usa una serie de if/elif/else:
        - if self.percibe_con_energometro(): self.usar_vacuumator() (Máxima prioridad: si estás con un monstruo, destrúyelo).
        - elif self.percibe_monstruo_cerca(): ... (Decide si rotar o avanzar para buscarlo).
        - elif self.percibe_robot_enfrente(): ... (Implementa la lógica de comunicación y decisión conjunta).
        - elif self.choco_con_pared_antes(): ... (Usa la memoria del Vacuscopio para decidir rotar).
        - else: ... (Acción por defecto: explorar, por ejemplo, moverse adelante).
    3. **Consulta la Memoria:** Antes de tomar la decisión final, revisa self.memoria. Si una percepción pasada es igual a la actual y llevó a un buen resultado, podrías priorizar esa acción (esta es la parte de "jerarquía de reglas").
    4. Una vez elegida la accion, llama al método efector correspondiente (self.mover_adelante(), self.rotar(), etc.).
    5. **Guarda en Memoria:** Al final, añade la experiencia a la memoria: self.memoria.append((tiempo_actual, percepcion_actual, accion_ejecutada)).

**Paso 4: El Simulador (El Bucle Principal)**
Este es el script que une todo.

1. Crea una instancia del Entorno.
2. Crea N robots y M monstruos y añádelos al entorno en posiciones aleatorias.
3. Inicia un bucle principal: for t in range(max_iteraciones):
    - Dentro del bucle, recorre tu lista de robots y llama a robot.decidir_y_actuar(entorno, t).
    - Recorre tu lista de monstruos y llama a monstruo.actuar(entorno, t).
    - Actualiza el estado del entorno (por ejemplo, elimina robots y monstruos destruidos de las listas).
    - Llama a entorno.visualizar() para ver qué pasó en esa iteración.
    - time.sleep(1) para que la simulación corra a 1 segundo por iteración.

Con este plan, puedes ir desarrollando y probando cada parte de forma independiente. ¡Mucho éxito con el examen
Credits Used: 32.72


