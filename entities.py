"""
================================================================================
ENTIDADES DEL JUEGO
================================================================================
Este archivo define las clases para todos los objetos interactivos o dinámicos
del juego, como el jugador, cajas, barriles, etc.
"""
from __future__ import annotations

class Player:
    """Representa al jugador del juego."""
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self._start = (col, row)
        self.facing_dir = (0, -1)

    def reset(self):
        """Reinicia el jugador a su posición inicial."""
        self.col, self.row = self._start
        self.facing_dir = (0, -1)

class Box:
    """Representa la caja empujable (solo visible en Dim B)."""
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self._start = (col, row)

    def reset(self):
        """Reinicia la caja a su posición inicial."""
        self.col, self.row = self._start

class Barrel:
    """Representa el barril empujable."""
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self._start = (col, row)
        self.active = False

    def reset(self):
        """Reinicia el barril a su posición inicial."""
        self.col, self.row = self._start
        self.active = False

class Debris:
    """Representa un obstáculo estático (escombro)."""
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row

class PressurePlate:
    """Representa la placa de presión."""
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row

    def is_pressed_by(self, player: Player, box: Box, dim: str) -> bool:
        """Comprueba si algo está presionando la placa."""
        on_player = (player.col == self.col and player.row == self.row)
        on_box = (dim == "B" and box.col == self.col and box.row == self.row)
        return on_player or on_box

class Door:
    """Representa la puerta doble."""
    def __init__(self, col1: int, row1: int, col2: int, row2: int):
        self.col1, self.row1 = col1, row1
        self.col2, self.row2 = col2, row2
        self.is_open = False

    def contains(self, col: int, row: int) -> bool:
        """Comprueba si una posición es parte de la puerta."""
        return (col == self.col1 and row == self.row1) or \
               (col == self.col2 and row == self.row2)