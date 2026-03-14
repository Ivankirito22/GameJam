"""
Configuracion global del juego FRACTURE.
Constantes visuales, de rendimiento y auto-deteccion de niveles.
"""
import os as _os
import re as _re

# =============================================================================
# VENTANA Y RENDIMIENTO
# =============================================================================
TILE_SIZE = 64
FPS = 60

# =============================================================================
# ESTADOS DEL JUEGO
# =============================================================================
RUNNING = "running"
WON = "won"
MENU = "menu"

# =============================================================================
# NIVELES (auto-detectados desde assets/maps/)
# =============================================================================
_MAPS_DIR = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(
    _os.path.abspath(__file__)
))), "assets", "maps")


def get_levels() -> list[str]:
    """Escanea assets/maps/ y devuelve los archivos level*.tmx ordenados."""
    if not _os.path.isdir(_MAPS_DIR):
        return []
    files = []
    for f in _os.listdir(_MAPS_DIR):
        m = _re.match(r"^level(\d+)\.tmx$", f)
        if m:
            files.append((int(m.group(1)), f))
    files.sort()
    return [name for _, name in files]


# GIDs de tiles de agua en el tileset (para shader en dim B)
WATER_GIDS = {42}

# =============================================================================
# PALETA DE COLORES POR DIMENSION
# =============================================================================
PALETTE = {
    "A": {"hud_dim": (255, 215, 100)},
    "B": {"hud_dim": (110, 165, 255)},
}

# =============================================================================
# COLORES DE PARTICULAS
# =============================================================================
PARTICLE_WATER_COLOR  = (40, 120, 200)
PARTICLE_WATER_FADE   = (100, 180, 255)
PARTICLE_DIM_SWITCH_A = (255, 200, 80)
PARTICLE_DIM_SWITCH_B = (80, 140, 255)
PARTICLE_DIM_FADE_A   = (255, 240, 180)
PARTICLE_DIM_FADE_B   = (160, 200, 255)
PARTICLE_PUSH_COLOR   = (180, 140, 80)
PARTICLE_PUSH_FADE    = (220, 200, 160)
