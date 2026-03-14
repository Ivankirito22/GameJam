"""
Logica del nivel basada en capas TMX.
Capas: walls, paths, btn, bridge-X.
Mecanicas: barriles empujables, botones por peso, puerta de salida.
"""
import os
from src.core.config import TILE_SIZE
from src.entities.player import Player
from src.map.tmx_loader import load_level


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))


class Level:
    """Gestiona el estado y la logica del nivel."""

    def __init__(self, tmx_filename: str = "level1.tmx"):
        self.tmx_filename = tmx_filename
        self.tmx_path = os.path.join(_PROJECT_ROOT, "assets", "maps", tmx_filename)
        self._load(self.tmx_path)

    def _load(self, filepath: str):
        data = load_level(filepath)

        self.cols, self.rows = data["map_size"]
        self.dim = "A"

        # Capas visuales
        self.walls = data["walls"]
        self.paths = data["paths"]
        self.bridges = data["bridges"]

        # Botones: cada uno tiene pos, type, surface
        # pressed se calcula dinamicamente segun si hay barril encima
        self.buttons = []
        for btn in data["buttons"]:
            self.buttons.append({
                "pos": btn["pos"],
                "type": btn["type"],
                "surface": btn["surface"],
            })

        # Posiciones de agua (para shader dim B)
        self.water_positions = data.get("water", [])

        # Construir sets de posiciones para colision
        self._wall_set = {(x, y) for x, y, _ in self.walls}
        self._path_set = {(x, y) for x, y, _ in self.paths}
        self._bridge_sets = {}
        for dim_key, bridge in self.bridges.items():
            self._bridge_sets[dim_key] = {(x, y) for x, y, _ in bridge["tiles"]}

        # Barriles y puerta (leidos directamente del TMX)
        self.barrels = []
        for b in data.get("barrels", []):
            self.barrels.append({
                "col": b["col"], "row": b["row"],
                "dim": b["dim"], "type": b.get("type", "green"),
            })

        self.door_pos = data.get("door", None)
        self.door_open = False

        # Jugador: empieza en el primer path
        if self.paths:
            start_x, start_y = self.paths[0][0], self.paths[0][1]
        else:
            start_x, start_y = 1, 1
        self.player = Player(start_x, start_y)

        # Particulas y alertas
        self.pending_particle_events = []
        self.alert_message = ""
        self.alert_timer = 0.0

    # =========================================================================
    # COLISION
    # =========================================================================

    def _is_walkable(self, col: int, row: int) -> bool:
        """Comprueba si una posicion es caminable (sin considerar barriles)."""
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return False

        pos = (col, row)

        # Puerta abierta es caminable
        if self.door_open and pos == self.door_pos:
            return True

        # Paths siempre son caminables
        if pos in self._path_set:
            return True

        # Bridges de la dimension actual son caminables
        if self.dim in self._bridge_sets and pos in self._bridge_sets[self.dim]:
            return True

        # Buttons son caminables
        for btn in self.buttons:
            if btn["pos"] == pos:
                return True

        return False

    def _barrel_at(self, col: int, row: int) -> dict | None:
        """Devuelve el barril en (col, row) de la dimension actual, o None."""
        for barrel in self.barrels:
            if barrel["col"] == col and barrel["row"] == row and barrel["dim"] == self.dim:
                return barrel
        return None

    def _any_barrel_at(self, col: int, row: int) -> bool:
        """Comprueba si hay algun barril en (col, row) en cualquier dimension."""
        for barrel in self.barrels:
            if barrel["col"] == col and barrel["row"] == row:
                return True
        return False

    def _check_buttons(self):
        """Actualiza el estado de los botones segun si hay barril encima."""
        for btn in self.buttons:
            bx, by = btn["pos"]
            btn["pressed"] = self._any_barrel_at(bx, by)

    def _all_buttons_pressed(self) -> bool:
        """Comprueba si todos los botones estan activados."""
        if not self.buttons:
            return False
        return all(btn["pressed"] for btn in self.buttons)

    def _update_door(self):
        """Abre o cierra la puerta segun el estado de los botones."""
        self.door_open = self._all_buttons_pressed()

    # =========================================================================
    # METODOS PUBLICOS
    # =========================================================================

    def update_alert(self, dt: float):
        """Actualiza el temporizador de la alerta."""
        if self.alert_timer > 0:
            self.alert_timer -= dt
            if self.alert_timer <= 0:
                self.alert_message = ""
                self.alert_timer = 0.0

    def toggle_dimension(self):
        """Cambia entre dimension A y B."""
        new_dim = "B" if self.dim == "A" else "A"

        # Comprobar si hay un barril de la otra dimension en la posicion del jugador
        pcol, prow = self.player.col, self.player.row
        for barrel in self.barrels:
            if barrel["col"] == pcol and barrel["row"] == prow and barrel["dim"] == new_dim:
                self.alert_message = "Hay un objeto bloqueando el cambio dimensional"
                self.alert_timer = 2.0
                return

        # Verificar que el jugador no quede en posicion no caminable
        old_dim = self.dim
        self.dim = new_dim
        if not self._is_walkable(self.player.col, self.player.row):
            self.dim = old_dim
            return

        self.pending_particle_events.append({
            "type": "dimension_switch",
            "col": self.player.col,
            "row": self.player.row,
            "new_dim": new_dim,
        })

    def try_move(self, dc: int, dr: int) -> tuple[str | None, bool]:
        """Intenta mover al jugador.

        Returns:
            (resultado, pushed): resultado es 'won' si gana, None si no.
            pushed indica si se empujo un barril.
        """
        self.player.facing_dir = (dc, dr)
        new_col = self.player.col + dc
        new_row = self.player.row + dr
        pushed = False

        # Comprobar si hay barril en la posicion destino (dimension actual)
        barrel = self._barrel_at(new_col, new_row)
        if barrel is not None:
            # Intentar empujar el barril
            barrel_dest_col = new_col + dc
            barrel_dest_row = new_row + dr
            # El barril solo se puede mover a posicion caminable sin otro barril
            if (self._is_walkable(barrel_dest_col, barrel_dest_row)
                    and self._barrel_at(barrel_dest_col, barrel_dest_row) is None):
                barrel["col"] = barrel_dest_col
                barrel["row"] = barrel_dest_row
                pushed = True
            else:
                # No se puede empujar, no se mueve
                return (None, False)

        # Mover jugador (si no hay barril bloqueando)
        if not self._is_walkable(new_col, new_row):
            return (None, False)

        # Verificar que no haya barril en la nueva posicion (tras posible empuje)
        if self._barrel_at(new_col, new_row) is not None:
            return (None, False)

        self.player.col = new_col
        self.player.row = new_row

        # Actualizar botones y puerta
        self._check_buttons()
        self._update_door()

        # Comprobar victoria: jugador pisa la puerta abierta
        if self.door_open and (self.player.col, self.player.row) == self.door_pos:
            return ("won", pushed)

        return (None, pushed)

    def try_interact(self) -> str | None:
        """Interaccion con E (reservado para futuras mecanicas)."""
        return None

    def reset(self):
        """Reinicia el nivel."""
        self._load(self.tmx_path)
