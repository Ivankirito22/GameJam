"""
================================================================================
ENTIDAD: BARRIL
================================================================================
Los barriles son objetos que el jugador puede empujar.
Cuando un barril cae al agua, se convierte en un puente y ya NO se puede mover.

CONSEJO PARA JUNIORS:
    - "locked" significa que el barril está fijo en el agua (es un puente).
    - Una vez locked=True, el barril no se puede volver a mover nunca.
    - Cada barril tiene un "barrel_id" para poder distinguir uno de otro.
"""


class Barrel:
    """Representa un barril empujable que puede crear puentes sobre el agua."""

    def __init__(self, col: int, row: int, barrel_id: str):
        """
        Crea un barril en la posición indicada.

        Args:
            col: Columna inicial (posición horizontal).
            row: Fila inicial (posición vertical).
            barrel_id: Identificador único del barril (ej: "barrel_1").
        """
        self.col = col
        self.row = row
        self.barrel_id = barrel_id
        self.locked = False            # ¿Está fijo en el agua? (no se puede mover)
        self._start = (col, row)       # Posición inicial para el reset

    def lock(self):
        """
        Bloquea el barril en su posición actual.
        Se usa cuando cae al agua para convertirlo en puente.
        Una vez bloqueado, no se puede desbloquear (solo con reset).
        """
        self.locked = True

    def reset(self):
        """Reinicia el barril a su posición inicial (desbloqueado)."""
        self.col, self.row = self._start
        self.locked = False
