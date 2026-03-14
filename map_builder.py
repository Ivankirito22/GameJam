"""
================================================================================
GENERADOR DE MAPAS
================================================================================
Este archivo contiene funciones para generar los mapas del juego.
Actualmente, solo genera un mapa fijo, pero podría extenderse para cargar
mapas desde archivos o generarlos proceduralmente con más variedad.
"""
from config import COLS, ROWS, FLOOR, WALL, FLOOR_DECO, WATER

def build_map() -> list[list[int]]:
    """
    Genera el tilemap 10x10 del nivel.
    
    Retorna:
        Un array 2D donde cada valor es una constante de tipo de baldosa.
    """
    m = [[FLOOR] * COLS for _ in range(ROWS)]

    # Bordes exteriores
    for c in range(COLS):
        m[0][c] = WALL
        m[ROWS - 1][c] = WALL
    for r in range(ROWS):
        m[r][0] = WALL
        m[r][COLS - 1] = WALL

    # Baldosas decoradas
    for r in range(1, ROWS - 1):
        for c in range(1, COLS - 1):
            if m[r][c] == FLOOR and (r + c) % 3 == 0:
                m[r][c] = FLOOR_DECO

    # Agua
    m[5][2] = WATER
    m[5][3] = WATER
    m[6][3] = WATER

    # Escombros
    m[4][2] = WALL
    m[6][7] = WALL

    return m