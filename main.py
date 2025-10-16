#!/usr/bin/env python3
"""
Simulación Robots vs Monstruos
Archivo principal de ejecución de la simulación.

Este archivo contiene únicamente la lógica de ejecución de la simulación,
importando las clases necesarias desde sus respectivos módulos.
"""

import random
import time
from entorno import Entorno, crear_posicion_aleatoria_libre
from monstruo import Monstruo
from robot import Robot


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
            print(f"Robot {i+1} creado en posición {posicion} - {robot.obtener_orientacion_texto()}")
    
    # Crear monstruos
    print(f"\nCreando {num_monstruos} monstruos...")
    for i in range(num_monstruos):
        posicion = crear_posicion_aleatoria_libre(entorno)
        if posicion:
            monstruo = Monstruo(posicion)
            entorno.agregar_entidad(monstruo, posicion)
            print(f"Monstruo {i+1} creado en posición {posicion}")
    
    # Mostrar estado inicial
    entorno.visualizar_compacto()
    
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
            entorno.visualizar_compacto()
            
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