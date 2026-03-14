"""
================================================================================
ENTIDAD: JUGADOR
================================================================================
El jugador es el personaje que controla el usuario.
Se mueve por el mapa y puede empujar barriles.

CONSEJO PARA JUNIORS:
    - "col" y "row" son la posición en la cuadrícula (no en píxeles).
    - "_start" guarda la posición inicial para poder reiniciar el nivel.
    - "facing_dir" indica hacia dónde mira el jugador (para saber qué empujar).
"""


class Player:
    """Representa al jugador del juego."""

    def __init__(self, col: int, row: int):
        """
        Crea un jugador en la posición indicada.

        Args:
            col: Columna inicial (posición horizontal).
            row: Fila inicial (posición vertical).
        """
        self.col = col
        self.row = row
        self._start = (col, row)       # Guardamos la posición para el reset
        self.facing_dir = (0, -1)      # Empieza mirando hacia arriba

    def reset(self):
        """Reinicia al jugador a su posición y dirección inicial."""
        self.col, self.row = self._start
        self.facing_dir = (0, -1)
