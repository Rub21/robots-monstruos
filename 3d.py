#!/usr/bin/env python3
"""
Simulación Robots vs Monstruos - Prueba con Visualización 3D
Archivo de prueba que usa la visualización 3D para mostrar el mundo completo.
"""

import random
import time
from entorno import Entorno, crear_posicion_aleatoria_libre
from monstruo import Monstruo
from robot import Robot
from visualizador_3d import Visualizador3D


def simulacion_con_3d():
    """
    Función principal que ejecuta la simulación con visualización 3D.
    """
    print("=== SIMULACIÓN ROBOTS VS MONSTRUOS CON VISUALIZACIÓN 3D ===")
    print("Iniciando simulación...")
    
    # Parámetros de la simulación
    N = 5  # Cubo más pequeño para mejor visualización 3D
    p_free = 0.9  # 70% de celdas libres
    p_soft = 0  # 20% de celdas vacías (obstáculos)
    num_robots = 4
    num_monstruos = 4
    max_iteraciones = 20
    
    # Crear el entorno
    entorno = Entorno(N, p_free, p_soft)
    print(f"Entorno creado: {N}x{N}x{N} con {p_free*100}% libres y {p_soft*100}% vacías")
    
    # Crear el visualizador 3D
    visualizador = Visualizador3D()
    
    # Crear robots
    print(f"\nCreando {num_robots} robots...")
    for i in range(num_robots):
        posicion = crear_posicion_aleatoria_libre(entorno)
        if posicion:
            orientacion = random.choice([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)])
            robot = Robot(posicion, orientacion)
            entorno.agregar_entidad(robot, posicion)
            print(f"Robot {i+1} creado en posición {posicion} - {robot.obtener_orientacion_texto()}")
    
    # Crear monstruos
    print(f"\nCreando {num_monstruos} monstruos...")
    for i in range(num_monstruos):
        posicion = crear_posicion_aleatoria_libre(entorno)
        if posicion:
            monstruo = Monstruo(posicion)
            entorno.agregar_entidad(monstruo, posicion)
            print(f"Monstruo {i+1} creado en posición {posicion}")
    
    # Mostrar estadísticas iniciales
    print(f"\n📊 ESTADÍSTICAS INICIALES:")
    print(f"   Robots: {len(entorno.robots)}")
    print(f"   Monstruos: {len(entorno.monstruos)}")
    
    # Contar celdas manualmente
    libres = sum(1 for x in range(entorno.N) for y in range(entorno.N) for z in range(entorno.N) if entorno.mundo[x, y, z] == 0)
    vacias = sum(1 for x in range(entorno.N) for y in range(entorno.N) for z in range(entorno.N) if entorno.mundo[x, y, z] == 1)
    print(f"   Zonas libres: {libres}")
    print(f"   Zonas vacías: {vacias}")
    
    # Mostrar estado inicial en 3D
    visualizador.visualizar_mundo(entorno, 0)
    
    # Bucle principal de simulación
    print(f"\nIniciando simulación por {max_iteraciones} iteraciones...")
    print("Presiona Ctrl+C para detener la simulación")
    
    try:
        for t in range(max_iteraciones):
            print(f"\n--- ITERACIÓN {t+1} ---")
            
            # Actuar con todos los robots
            robots_activos = entorno.robots.copy()
            for robot in robots_activos:
                if robot in entorno.robots:
                    robot.decidir_y_actuar(entorno, t)
            
            # Actuar con todos los monstruos
            monstruos_activos = entorno.monstruos.copy()
            for monstruo in monstruos_activos:
                if monstruo in entorno.monstruos:
                    monstruo.actuar(entorno, t)
            
            # Mostrar estado del mundo en 3D
            visualizador.visualizar_mundo(entorno, t+1)
            
            # Verificar condiciones de fin de juego
            if len(entorno.monstruos) == 0:
                print("\n🎉 ¡VICTORIA! Todos los monstruos han sido eliminados!")
                break
            elif len(entorno.robots) == 0:
                print("\n💀 DERROTA: Todos los robots han sido destruidos!")
                break
            
            # Pausa para visualización
            time.sleep(2)
    
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
    
    # Mantener la ventana abierta
    print("\nPresiona Enter para cerrar la visualización 3D...")
    input()


if __name__ == "__main__":
    # Ejecutar la simulación con visualización 3D
    simulacion_con_3d()
