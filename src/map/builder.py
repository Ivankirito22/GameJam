"""
================================================================================
GENERADOR DE MAPAS
================================================================================
Genera el mapa del nivel como una cuadrícula 2D.
Cada posición contiene un número que indica el tipo de casilla.

CONSEJO PARA JUNIORS:
    - El mapa es una lista de listas (como una tabla de Excel).
    - Se accede con: mapa[fila][columna]
    - Los valores posibles están definidos en config.py (FLOOR, WALL, WATER...).
"""
from src.core.config import COLS, ROWS, FLOOR, WALL, FLOOR_DECO, WATER


def build_map() -> list[list[int]]:
    """
    Genera el mapa 10x10 del nivel.

    El mapa tiene:
        - Bordes de muros alrededor del perímetro
        - Casillas decoradas en patrón alternado
        - Una zona de agua (3 casillas)
        - Dos escombros como obstáculos internos

    Returns:
        Una lista 2D donde cada valor es un tipo de casilla (FLOOR, WALL, etc).
    """
    # Paso 1: Crear un mapa vacío (todo suelo)
    grid = [[FLOOR] * COLS for _ in range(ROWS)]

    # Paso 2: Poner muros en los bordes (perímetro)
    for col in range(COLS):
        grid[0][col] = WALL            # Borde superior
        grid[ROWS - 1][col] = WALL     # Borde inferior
    for row in range(ROWS):
        grid[row][0] = WALL            # Borde izquierdo
        grid[row][COLS - 1] = WALL     # Borde derecho

    # Paso 3: Añadir decoración al suelo (patrón cada 3 casillas)
    for row in range(1, ROWS - 1):
        for col in range(1, COLS - 1):
            if grid[row][col] == FLOOR and (row + col) % 3 == 0:
                grid[row][col] = FLOOR_DECO

    # Paso 4: Colocar agua (zona de peligro)
    grid[5][2] = WATER
    grid[5][3] = WATER
    grid[6][3] = WATER

    # Paso 5: Colocar muros internos (se convertirán en escombros)
    grid[4][2] = WALL
    grid[6][7] = WALL

    return grid
