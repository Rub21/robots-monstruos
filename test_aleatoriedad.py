#!/usr/bin/env python3
"""
Script de prueba para verificar la mejora en la aleatoriedad del entorno.
"""

from entorno import Entorno, crear_posicion_aleatoria_libre, crear_posiciones_aleatorias_libres
import time

def test_aleatoriedad():
    """
    Prueba la aleatoriedad de la generación del entorno.
    """
    print("=== PRUEBA DE ALEATORIEDAD MEJORADA ===\n")

    # Crear varios entornos con diferentes semillas
    entornos = []
    for i in range(3):
        print(f"Creando entorno {i+1}...")
        entorno = Entorno(N=8, p_free=0.6, p_soft=0.2)
        entornos.append(entorno)

        # Mostrar información del entorno
        total_libres = sum(1 for x in range(entorno.N)
                          for y in range(entorno.N)
                          for z in range(entorno.N)
                          if entorno.obtener_estado((x, y, z)) == 0)

        total_obstaculos = sum(1 for x in range(entorno.N)
                              for y in range(entorno.N)
                              for z in range(entorno.N)
                              if entorno.obtener_estado((x, y, z)) == 1)

        print(f"  Celdas libres: {total_libres}")
        print(f"  Obstáculos: {total_obstaculos}")
        print(f"  Total: {entorno.N**3}")

        # Visualizar una capa
        print(f"\nVisualización del entorno {i+1} (capa central):")
        entorno.visualizar_compacto()

        # Probar posiciones aleatorias
        print(f"\nPosiciones aleatorias generadas para entorno {i+1}:")
        for j in range(5):
            pos = crear_posicion_aleatoria_libre(entorno)
            print(f"  Posición {j+1}: {pos}")

        print("-" * 60)
        time.sleep(0.1)  # Pequeña pausa para cambiar la semilla

    # Probar regeneración de mundo
    print("\n=== PRUEBA DE REGENERACIÓN ===")
    entorno_test = entornos[0]
    print("Regenerando el primer entorno...")
    entorno_test.regenerar_mundo()
    entorno_test.visualizar_compacto()

    # Probar función de múltiples posiciones
    print("\n=== PRUEBA DE MÚLTIPLES POSICIONES ===")
    posiciones_multiples = crear_posiciones_aleatorias_libres(entorno_test, 10)
    print("10 posiciones aleatorias:")
    for i, pos in enumerate(posiciones_multiples):
        print(f"  {i+1}: {pos}")

if __name__ == "__main__":
    test_aleatoriedad()
