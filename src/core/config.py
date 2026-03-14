"""
================================================================================
CONFIGURACIÓN GLOBAL DEL JUEGO
================================================================================
Aquí se definen TODAS las constantes del juego en un solo lugar.
Si quieres cambiar algo (tamaño de ventana, colores, posiciones iniciales...),
solo tienes que modificar este archivo.

CONSEJO PARA JUNIORS:
    - Las constantes se escriben en MAYÚSCULAS para distinguirlas de variables.
    - Tener toda la config en un archivo facilita ajustar el juego sin tocar lógica.
"""

# =============================================================================
# VENTANA Y RENDIMIENTO
# =============================================================================
TILE_SIZE = 64                    # Tamaño de cada casilla en píxeles (64x64)
COLS = 10                         # Número de columnas del mapa
ROWS = 10                         # Número de filas del mapa
WIDTH = TILE_SIZE * COLS          # Ancho total de la ventana (640px)
HEIGHT = TILE_SIZE * ROWS         # Alto total de la ventana (640px)
FPS = 60                          # Fotogramas por segundo (fluidez del juego)

# =============================================================================
# ESTADOS DEL JUEGO
# =============================================================================
# El juego siempre está en UNO de estos tres estados:
RUNNING = "running"               # El jugador está jugando
DEAD = "dead"                     # El jugador ha muerto
WON = "won"                       # El jugador ha ganado

# =============================================================================
# TIPOS DE CASILLA (TILES)
# =============================================================================
# Cada casilla del mapa tiene un tipo numérico:
FLOOR = 0                         # Suelo normal (se puede caminar)
WALL = 1                          # Muro (bloquea el paso)
FLOOR_DECO = 2                    # Suelo decorado (igual que FLOOR pero con dibujo)
WATER = 3                         # Agua (mortal si pisas sin puente)

# =============================================================================
# PALETAS DE COLORES POR DIMENSIÓN
# =============================================================================
# Cada dimensión tiene su propia paleta de colores para que el jugador
# vea claramente en qué dimensión está.
PALETTE = {
    "A": {  # Dimensión A - Tonos cálidos (marrones/dorados)
        FLOOR:       (194, 164, 120),
        WALL:        (101,  67,  33),
        FLOOR_DECO:  (180, 150, 108),
        WATER:       ( 90, 140, 110),
        "wall_shade": ( 78, 50, 22),
        "grid_line":  (175, 145, 102),
        "goal_zone":  (120, 185, 100),
        "hud_dim":    (255, 215, 100),
    },
    "B": {  # Dimensión B - Tonos fríos (azules/grises)
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

# =============================================================================
# COLORES DE LAS ENTIDADES
# =============================================================================
# Colores fijos que no cambian con la dimensión.
CLR_PLAYER       = ( 55, 215,  75)   # Verde brillante (cuerpo del jugador)
CLR_PLAYER_EDGE  = ( 35, 155,  50)   # Verde oscuro (borde del jugador)
CLR_BARREL       = (139,  69,  19)   # Marrón (cuerpo del barril)
CLR_BARREL_EDGE  = (101,  50,  15)   # Marrón oscuro (borde del barril)
CLR_BARREL_LOCKED = (80,  80,  80)   # Gris (barril bloqueado en agua)
CLR_DEBRIS       = (101,  67,  33)   # Marrón terroso (escombros)
CLR_PLATE_ON     = (255, 255,  50)   # Amarillo brillante (placa activada)
CLR_PLATE_OFF    = (185, 185,  70)   # Amarillo apagado (placa sin activar)
CLR_DOOR_OPEN    = ( 35, 200,  55)   # Verde (puerta abierta)
CLR_DOOR_CLOSED  = (195,  35,  35)   # Rojo (puerta cerrada)
CLR_WHITE        = (255, 255, 255)   # Blanco puro

# =============================================================================
# COLORES DE PARTÍCULAS
# =============================================================================
# Colores usados para los efectos de partículas en distintas situaciones.
PARTICLE_WATER_COLOR      = (40, 120, 200)    # Azul agua (splash al caer barril)
PARTICLE_WATER_FADE       = (100, 180, 255)   # Azul claro (fade del splash)
PARTICLE_DIM_SWITCH_A     = (255, 200, 80)    # Dorado (cambiar a dim A)
PARTICLE_DIM_SWITCH_B     = (80, 140, 255)    # Azul (cambiar a dim B)
PARTICLE_DIM_FADE_A       = (255, 240, 180)   # Dorado claro (fade dim A)
PARTICLE_DIM_FADE_B       = (160, 200, 255)   # Azul claro (fade dim B)
PARTICLE_PUSH_COLOR       = (180, 140, 80)    # Marrón claro (empujar barril)
PARTICLE_PUSH_FADE        = (220, 200, 160)   # Beige (fade empujar)

# =============================================================================
# POSICIONES INICIALES DEL NIVEL
# =============================================================================
# Formato: (columna, fila) - columna es X, fila es Y
PLAYER_START  = (5, 2)            # Donde aparece el jugador
PLATE_POS     = (5, 1)            # Donde está la placa de presión
DOOR_POS_1    = (4, 9)            # Primera mitad de la puerta doble
DOOR_POS_2    = (5, 9)            # Segunda mitad de la puerta doble
BARREL_1_START = (5, 1)           # Primer barril (reemplaza la antigua caja)
BARREL_2_START = (4, 6)           # Segundo barril
WATER_TO_DRY  = {(2, 5), (3, 5), (3, 6)}  # Casillas de agua que se secan
