"""
================================================================================
ENTIDADES ESTÁTICAS
================================================================================
Objetos del juego que NO se mueven: escombros, placa de presión y puerta.

CONSEJO PARA JUNIORS:
    - "Estático" significa que su posición no cambia durante el juego.
    - La puerta tiene DOS posiciones porque ocupa dos casillas.
    - La placa de presión detecta si algo está encima de ella.
"""


class Debris:
    """
    Representa un escombro/obstáculo que bloquea el paso.
    Es simplemente una posición en el mapa que no se puede atravesar.
    """

    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row


class PressurePlate:
    """
    Representa la placa de presión del puzzle.
    Se activa cuando el jugador o un barril están encima.
    """

    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row

    def is_pressed_by(self, player, barrels: list, dim: str) -> bool:
        """
        Comprueba si algo está presionando la placa.

        Args:
            player: El objeto Player del juego.
            barrels: Lista de todos los barriles del juego.
            dim: Dimensión actual ("A" o "B").

        Returns:
            True si la placa está siendo presionada, False si no.
        """
        # ¿Está el jugador encima?
        if player.col == self.col and player.row == self.row:
            return True

        # ¿Hay algún barril encima? (solo en dimensión B)
        if dim == "B":
            for barrel in barrels:
                if barrel.col == self.col and barrel.row == self.row:
                    return True

        return False


class Door:
    """
    Representa la puerta doble del puzzle.
    Ocupa DOS casillas y puede estar abierta o cerrada.
    """

    def __init__(self, col1: int, row1: int, col2: int, row2: int):
        """
        Crea una puerta doble entre dos posiciones.

        Args:
            col1, row1: Posición de la primera mitad.
            col2, row2: Posición de la segunda mitad.
        """
        self.col1, self.row1 = col1, row1
        self.col2, self.row2 = col2, row2
        self.is_open = False

    def contains(self, col: int, row: int) -> bool:
        """Comprueba si una posición es parte de esta puerta."""
        return ((col == self.col1 and row == self.row1) or
                (col == self.col2 and row == self.row2))
