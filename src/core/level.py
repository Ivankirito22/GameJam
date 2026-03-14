"""
================================================================================
LÓGICA DEL NIVEL
================================================================================
La clase Level es el "cerebro" del juego. Controla:
    - Las posiciones de todas las entidades (jugador, barriles, puerta...).
    - Las reglas del puzzle (qué se puede empujar, cuándo mueres, cuándo ganas).
    - El cambio entre dimensiones A y B.

CONSEJO PARA JUNIORS:
    - "dim" es la dimensión actual: "A" (cálida) o "B" (fría).
    - Los barriles solo se ven y se empujan en la dimensión B.
    - Si un barril cae al agua, se bloquea (locked=True) y ya no se puede mover.
    - La puerta se abre/cierra según la placa de presión y la dimensión.

REGLAS IMPORTANTES:
    - El jugador muere si pisa agua sin puente.
    - El jugador gana si llega al borde inferior en dimensión A.
    - El jugador muere si llega al borde inferior en dimensión B.
    - Un barril en el agua se convierte en puente y NO se puede mover más.
"""
from src.core.config import (
    COLS, ROWS, FLOOR, WALL, WATER, DEAD, WON,
    PLAYER_START, PLATE_POS, DOOR_POS_1, DOOR_POS_2,
    BARREL_1_START, BARREL_2_START, WATER_TO_DRY,
)
from src.entities.player import Player
from src.entities.barrel import Barrel
from src.entities.static_objects import Debris, PressurePlate, Door
from src.map.builder import build_map


class Level:
    """Gestiona todo el estado y la lógica del nivel."""

    def __init__(self):
        """Inicializa el nivel con todas sus entidades y el mapa."""
        # Generar el mapa (cuadrícula 2D)
        self.grid = build_map()

        # Dimensión actual (empieza en A)
        self.dim = "A"

        # Crear las entidades del juego
        self.player = Player(*PLAYER_START)
        self.plate = PressurePlate(*PLATE_POS)
        self.door = Door(*DOOR_POS_1, *DOOR_POS_2)

        # Lista de barriles (antes había una caja + un barril, ahora son 2 barriles)
        self.barrels = [
            Barrel(*BARREL_1_START, barrel_id="barrel_1"),
            Barrel(*BARREL_2_START, barrel_id="barrel_2"),
        ]

        # Puentes creados por barriles que cayeron al agua
        self.barrel_bridges = set()

        # Escombros (obstáculos estáticos generados desde los muros interiores)
        self.debris = []
        self._create_debris()

        # Hacer que las casillas de la puerta sean suelo (la puerta se dibuja aparte)
        self.grid[self.door.row1][self.door.col1] = FLOOR
        self.grid[self.door.row2][self.door.col2] = FLOOR

        # Actualizar el estado inicial de la puerta
        self._update_door()

        # Lista para almacenar eventos de partículas pendientes
        # (el rendering los leerá y los consumirá)
        self.pending_particle_events = []

    # =========================================================================
    # MÉTODOS INTERNOS (empiezan con _ porque son "privados")
    # =========================================================================

    def _create_debris(self):
        """Crea objetos Debris para cada muro que esté dentro del mapa (no bordes)."""
        for row in range(1, ROWS - 1):
            for col in range(1, COLS - 1):
                if self.grid[row][col] == WALL:
                    self.debris.append(Debris(col, row))

    def _tile_at(self, col: int, row: int) -> int:
        """
        Obtiene el tipo de casilla en una posición.
        Si la posición está fuera del mapa, devuelve WALL (bloqueante).
        """
        if not (0 <= col < COLS and 0 <= row < ROWS):
            return WALL
        return self.grid[row][col]

    def _is_blocked(self, col: int, row: int) -> bool:
        """
        Comprueba si una posición está bloqueada (no se puede caminar).
        Está bloqueada si: es muro, es puerta cerrada, o hay escombros.
        """
        if self._tile_at(col, row) == WALL:
            return True
        if self.door.contains(col, row) and not self.door.is_open:
            return True
        if any(d.col == col and d.row == row for d in self.debris):
            return True
        return False

    def _is_water(self, col: int, row: int) -> bool:
        """
        Comprueba si una posición es agua mortal.
        El agua NO es mortal si hay un puente de barril encima.
        """
        if self._tile_at(col, row) != WATER:
            return False
        # ¿Hay un puente de barril aquí?
        if (col, row) in self.barrel_bridges:
            return False
        # ¿Se ha secado esta agua? (en dimensión A, tras usar un barril)
        if self._any_barrel_locked() and self.dim == "A" and (col, row) in WATER_TO_DRY:
            return False
        return True

    def _any_barrel_locked(self) -> bool:
        """Comprueba si algún barril está bloqueado (en el agua)."""
        return any(b.locked for b in self.barrels)

    def _barrel_at(self, col: int, row: int) -> Barrel | None:
        """
        Busca un barril en la posición indicada.
        Solo devuelve barriles visibles (dimensión B) y que NO estén bloqueados.

        Returns:
            El barril encontrado, o None si no hay ninguno.
        """
        if self.dim != "B":
            return None
        for barrel in self.barrels:
            if barrel.col == col and barrel.row == row and not barrel.locked:
                return barrel
        return None

    def _update_door(self):
        """
        Actualiza si la puerta está abierta o cerrada.
        La lógica cambia según la dimensión:
            - Dim B: la puerta se abre si la placa está presionada.
            - Dim A: la puerta se abre si la placa NO está presionada por un barril.
        """
        plate_pressed = self.plate.is_pressed_by(self.player, self.barrels, self.dim)

        if self.dim == "B":
            self.door.is_open = plate_pressed
        else:
            # En dim A, la puerta se abre si NO hay barril en la placa, o si el jugador está
            barrel_on_plate = any(
                b.col == self.plate.col and b.row == self.plate.row
                for b in self.barrels
            )
            player_on_plate = (
                self.player.col == self.plate.col and
                self.player.row == self.plate.row
            )
            self.door.is_open = (not barrel_on_plate) or player_on_plate

    def _check_triggers(self) -> str | None:
        """
        Comprueba si el jugador ha ganado o muerto.

        Returns:
            WON si ganó, DEAD si murió, None si sigue jugando.
        """
        pc, pr = self.player.col, self.player.row

        # ¿Pisó agua?
        if self._is_water(pc, pr):
            return DEAD

        # ¿Llegó al borde inferior?
        if pr == ROWS - 1:
            return WON if self.dim == "A" else DEAD

        return None

    # =========================================================================
    # MÉTODOS PÚBLICOS (los que usa Game)
    # =========================================================================

    def toggle_dimension(self):
        """
        Cambia entre dimensión A y B.
        No permite cambiar si el jugador quedaría dentro de un barril.
        """
        new_dim = "B" if self.dim == "A" else "A"

        # Comprobar que el jugador no se superponga con un barril al cambiar a B
        if new_dim == "B":
            for barrel in self.barrels:
                if (self.player.col == barrel.col and
                        self.player.row == barrel.row and
                        not barrel.locked):
                    return  # No se puede cambiar, hay un barril aquí

        self.dim = new_dim
        self._update_door()

        # Si volvemos a dim A y hay barriles bloqueados, registrar que se usaron
        if new_dim == "A" and self._any_barrel_locked():
            pass  # Los puentes ya están registrados en barrel_bridges

        # Emitir evento de partículas para el cambio de dimensión
        self.pending_particle_events.append({
            "type": "dimension_switch",
            "col": self.player.col,
            "row": self.player.row,
            "new_dim": new_dim,
        })

    def try_move(self, dc: int, dr: int) -> str | None:
        """
        Intenta mover al jugador en una dirección.

        Args:
            dc: Cambio en columna (-1=izquierda, 1=derecha, 0=sin cambio).
            dr: Cambio en fila (-1=arriba, 1=abajo, 0=sin cambio).

        Returns:
            WON/DEAD si el movimiento causa victoria/derrota, None en otro caso.
        """
        # Actualizar la dirección a la que mira el jugador
        self.player.facing_dir = (dc, dr)

        # Calcular la nueva posición
        new_col = self.player.col + dc
        new_row = self.player.row + dr

        # ¿Hay un barril en el camino? (no se puede caminar sobre barriles)
        if self._barrel_at(new_col, new_row) is not None:
            return None

        # ¿Está bloqueada la casilla?
        if self._is_blocked(new_col, new_row):
            return None

        # Mover al jugador
        self.player.col = new_col
        self.player.row = new_row
        self._update_door()
        return self._check_triggers()

    def try_interact(self) -> str | None:
        """
        Intenta empujar un barril en la dirección que mira el jugador.
        Si el barril cae al agua, se bloquea y crea un puente.

        Returns:
            WON/DEAD si la interacción causa victoria/derrota, None en otro caso.
        """
        dc, dr = self.player.facing_dir
        target_col = self.player.col + dc
        target_row = self.player.row + dr

        # ¿Hay un barril delante del jugador?
        barrel = self._barrel_at(target_col, target_row)
        if barrel is None:
            return None

        # Calcular a dónde se movería el barril
        push_col = target_col + dc
        push_row = target_row + dr

        # ¿La casilla destino está bloqueada?
        if self._is_blocked(push_col, push_row):
            return None

        # ¿Hay otro barril en la casilla destino?
        if self._barrel_at(push_col, push_row) is not None:
            return None

        # Mover el barril
        barrel.col = push_col
        barrel.row = push_row

        # Emitir efecto de empujar
        self.pending_particle_events.append({
            "type": "push",
            "col": target_col,
            "row": target_row,
        })

        # ¿El barril cayó al agua?
        if self._tile_at(push_col, push_row) == WATER:
            barrel.lock()  # Bloquear el barril (ya no se puede mover)
            self.barrel_bridges.add((push_col, push_row))

            # Emitir efecto de splash
            self.pending_particle_events.append({
                "type": "water_splash",
                "col": push_col,
                "row": push_row,
            })

        self._update_door()
        return self._check_triggers()

    def reset(self):
        """Reinicia todo el nivel a su estado inicial."""
        self.player.reset()
        for barrel in self.barrels:
            barrel.reset()
        self.barrel_bridges.clear()
        self.dim = "A"
        self._update_door()
        self.pending_particle_events.clear()
