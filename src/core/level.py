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

# Datos de objetos por nivel (fallback cuando el TMX no tiene objectgroup).
# Clave: nombre del archivo TMX.
_LEVEL_OBJECTS = {
    "level1.tmx": {
        "barrels": [
            {"col": 2, "row": 7, "dim": "B", "type": "green"},
        ],
        "door": (9, 3),
        "npcs": [],
    },
    "level2.tmx": {
        "barrels": [
            {"col": 6, "row": 3, "dim": "A", "type": "green"},
            {"col": 3, "row": 8, "dim": "B", "type": "yellow"},
        ],
        "door": (2, 0),
        "npcs": [],
    },
    "level3.tmx": {
        "barrels": [
            {"col": 2, "row": 5, "dim": "A", "type": "green"},
            {"col": 8, "row": 4, "dim": "B", "type": "green"},
        ],
        "door": (7, 0),
        "npcs": [],
    },
    "level4.tmx": {
        "barrels": [
            {"col": 1, "row": 3, "dim": "B", "type": "yellow"},
        ],
        "door": (2, 0),
        "npcs": [],
    },
    "level5.tmx": {
        "barrels": [],
        "door": (2, 9),
        "npcs": [
            {"col": 5, "row": 3, "type": "jeffry"},
        ],
        # Posiciones caminables (fallback si el TMX no tiene capa "paths")
        "walkable": [
            # Sala superior (filas 1-4)
            *[(c, 1) for c in range(2, 8)],
            *[(c, 2) for c in range(2, 8)],
            *[(c, 3) for c in range(2, 8)],
            *[(c, 4) for c in range(3, 7)],
            # Sala inferior (filas 7-8)
            (1, 7), (2, 7), (3, 7), (6, 7), (7, 7),
            (1, 8), (2, 8), (3, 8),
        ],
        "start": (3, 1),
    },
}


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

        # Si no hay paths del TMX, usar walkable del fallback
        fallback = _LEVEL_OBJECTS.get(self.tmx_filename, {})
        if not self._path_set and "walkable" in fallback:
            self._path_set = set(fallback["walkable"])

        self._bridge_sets = {}
        for dim_key, bridge in self.bridges.items():
            self._bridge_sets[dim_key] = {(x, y) for x, y, _ in bridge["tiles"]}

        # Barriles, puerta y NPCs: primero del TMX, si no del fallback en codigo
        tmx_barrels = data.get("barrels", [])
        tmx_door = data.get("door", None)
        tmx_npcs = data.get("npcs", [])

        # Usar datos del TMX si existen, si no usar fallback
        barrel_src = tmx_barrels if tmx_barrels else fallback.get("barrels", [])
        self.barrels = []
        for b in barrel_src:
            self.barrels.append({
                "col": b["col"], "row": b["row"],
                "dim": b["dim"], "type": b.get("type", "green"),
            })

        self.door_pos = tmx_door if tmx_door else fallback.get("door", None)
        self.door_open = False

        npc_src = tmx_npcs if tmx_npcs else fallback.get("npcs", [])
        self.npcs = []
        for npc in npc_src:
            self.npcs.append({
                "col": npc["col"], "row": npc["row"],
                "type": npc["type"], "talked": False,
            })

        # Jugador: empieza en posicion definida o primer path
        if "start" in fallback:
            start_x, start_y = fallback["start"]
        elif self.paths:
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
        """Abre o cierra la puerta segun el estado de los botones.
        Si Jeffry ya ha sido hablado, la puerta queda abierta."""
        # Si Jeffry ya abrio la puerta, no la cerramos
        for npc in self.npcs:
            if npc["type"] == "jeffry" and npc["talked"]:
                self.door_open = True
                return
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

    def try_interact(self) -> dict | None:
        """Interaccion con E. Devuelve info del NPC si hay uno adyacente."""
        pcol, prow = self.player.col, self.player.row
        for npc in self.npcs:
            dx = abs(npc["col"] - pcol)
            dy = abs(npc["row"] - prow)
            if dx + dy <= 1:  # Adyacente (incluye misma casilla)
                return npc
        return None

    def mark_npc_talked(self, npc: dict):
        """Marca un NPC como hablado y abre la puerta si es Jeffry."""
        npc["talked"] = True
        if npc["type"] == "jeffry":
            self.door_open = True

    def reset(self):
        """Reinicia el nivel."""
        self._load(self.tmx_path)
