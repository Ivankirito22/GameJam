"""
================================================================================
CONFIGURACIÓN GLOBAL
================================================================================
Este archivo contiene todas las constantes y configuraciones del juego.
Modificar valores aquí afectará a todo el juego, permitiendo un ajuste
centralizado de sus características.
"""

# ============================================================================
# SECCIÓN 1: CONSTANTES DE JUEGO
# ============================================================================
TS = 64                          # Tamaño de cada baldosa en píxeles (64x64)
COLS, ROWS = 10, 10              # Número de baldosas (10x10)
WIDTH = TS * COLS                # Ancho de ventana: 640 píxeles
HEIGHT = TS * ROWS               # Alto de ventana: 640 píxeles
FPS = 60                         # Fotogramas por segundo

# Estados del juego
RUNNING = "running"
DEAD = "dead"
WON = "won"

# Tipos de baldosa
FLOOR = 0
WALL = 1
FLOOR_DECO = 2
WATER = 3

# ============================================================================
# SECCIÓN 2: PALETAS DE COLORES
# ============================================================================
PALETTE = {
    "A": {  # Dimensión A - Cálida
        FLOOR:       (194, 164, 120),
        WALL:        (101,  67,  33),
        FLOOR_DECO:  (180, 150, 108),
        WATER:       ( 90, 140, 110),
        "wall_shade": ( 78, 50, 22),
        "grid_line":  (175, 145, 102),
        "goal_zone":  (120, 185, 100),
        "hud_dim":    (255, 215, 100),
    },
    "B": {  # Dimensión B - Fría
        FLOOR:       (110, 125, 155),
        WALL:        ( 38,  50,  90),
        FLOOR_DECO:  ( 98, 112, 140),
        WATER:       ( 40,  75, 130),
        "wall_shade": ( 25, 35, 68),
        "grid_line":  ( 92, 107, 138),
        "goal_zone":  (170,  55,  55),
        "hud_dim":    (110, 165, 255),
    },
}

# Colores fijos para entidades
CLR_PLAYER = ( 55, 215,  75)
CLR_PLAYER_EDGE = ( 35, 155,  50)
CLR_BOX = (215, 135,  50)
CLR_BOX_EDGE = (165,  95,  30)
CLR_BARREL = (139,  69,  19)
CLR_BARREL_EDGE = (101,  50,  15)
CLR_DEBRIS = (101,  67,  33)
CLR_PLATE_ON = (255, 255,  50)
CLR_PLATE_OFF = (185, 185,  70)
CLR_DOOR_OPEN = ( 35, 200,  55)
CLR_DOOR_CLOSED = (195,  35,  35)
CLR_WHITE = (255, 255, 255)

# ============================================================================
# SECCIÓN 3: CONFIGURACIÓN DEL NIVEL 1
# ============================================================================
# Posiciones iniciales para el nivel por defecto.
# Para futuros niveles, esto podría cargarse desde un archivo de nivel.
PLAYER_START = (5, 2)
PLATE_POS = (5, 1)
DOOR_POS_1 = (4, 9)
DOOR_POS_2 = (5, 9)
BOX_START = (5, 1)
BARREL_START = (4, 6)
WATER_TO_DRY = {(2, 5), (3, 5), (3, 6)}