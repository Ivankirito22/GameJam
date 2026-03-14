"""
================================================================================
LÓGICA DEL NIVEL
================================================================================
La clase Level es el "cerebro" del juego. Gestiona el estado del nivel,
las entidades, las colisiones y la lógica del puzzle.
"""
from config import (
    COLS, ROWS, FLOOR, WALL, WATER, DEAD, WON, PLAYER_START, PLATE_POS,
    DOOR_POS_1, DOOR_POS_2, BOX_START, BARREL_START, WATER_TO_DRY
)
from entities import Player, Box, Barrel, Debris, PressurePlate, Door
from map_builder import build_map

class Level:
    """Gestiona todo lo relacionado con el nivel del juego."""
    
    def __init__(self):
        """Inicializa el nivel con todas sus entidades."""
        self.grid = build_map()
        self.dim = "A"
        
        self.player = Player(*PLAYER_START)
        self.plate = PressurePlate(*PLATE_POS)
        self.door = Door(*DOOR_POS_1, *DOOR_POS_2)
        self.box = Box(*BOX_START)
        self.barrel = Barrel(*BARREL_START)
        
        self.debris = []
        self._create_debris()
        
        self.barrel_used = False
        self.barrel_bridges = set()
        
        self.grid[self.door.row1][self.door.col1] = FLOOR
        self.grid[self.door.row2][self.door.col2] = FLOOR
        
        self._update_door()
    
    def _create_debris(self):
        """Crea objetos Debris para cada muro interior."""
        for r in range(1, ROWS - 1):
            for c in range(1, COLS - 1):
                if self.grid[r][c] == WALL:
                    self.debris.append(Debris(c, r))
    
    def _tile_at(self, c: int, r: int) -> int:
        """Obtiene el tipo de baldosa en una posición."""
        if not (0 <= c < COLS and 0 <= r < ROWS):
            return WALL
        return self.grid[r][c]
    
    def _is_blocked(self, c: int, r: int) -> bool:
        """Comprueba si una posición es bloqueante."""
        if self._tile_at(c, r) == WALL:
            return True
        if self.door.contains(c, r) and not self.door.is_open:
            return True
        if any(d.col == c and d.row == r for d in self.debris):
            return True
        return False
    
    def _is_water(self, c: int, r: int) -> bool:
        """Comprueba si una posición es agua (letal)."""
        if self._tile_at(c, r) != WATER:
            return False
        if (c, r) in self.barrel_bridges:
            return False
        if self.barrel_used and self.dim == "A" and (c, r) in WATER_TO_DRY:
            return False
        return True
    
    def _box_at(self, c: int, r: int) -> bool:
        """Comprueba si la caja está en una posición (Solo en Dim B)."""
        return self.dim == "B" and self.box.col == c and self.box.row == r
    
    def _barrel_at(self, c: int, r: int) -> bool:
        """Comprueba si el barril está en una posición (Solo en Dim B)."""
        return (self.dim == "B" and not self.barrel.active and
                self.barrel.col == c and self.barrel.row == r)
    
    def _update_door(self):
        """Actualiza el estado de la puerta según la dimensión."""
        box_on_plate = (self.box.col == self.plate.col and self.box.row == self.plate.row)
        player_on_plate = (self.player.col == self.plate.col and self.player.row == self.plate.row)
        
        if self.dim == "B":
            self.door.is_open = box_on_plate or player_on_plate
        else:
            self.door.is_open = (not box_on_plate) or player_on_plate
    
    def _check_triggers(self) -> str | None:
        """Comprueba condiciones de victoria o derrota."""
        pc, pr = self.player.col, self.player.row
        if self._is_water(pc, pr):
            return DEAD
        if pr == ROWS - 1:
            return WON if self.dim == "A" else DEAD
        return None
    
    def toggle_dimension(self):
        """Cambia entre dimensión A y B."""
        new_dim = "B" if self.dim == "A" else "A"
        if new_dim == "B":
            if ((self.player.col == self.box.col and self.player.row == self.box.row) or
                (self.player.col == self.barrel.col and self.player.row == self.barrel.row)):
                return
        
        self.dim = new_dim
        self._update_door()
        
        if new_dim == "A" and self.barrel.active:
            self.barrel_used = True
    
    def try_move(self, dc: int, dr: int) -> str | None:
        """Intenta mover al jugador."""
        self.player.facing_dir = (dc, dr)
        nc, nr = self.player.col + dc, self.player.row + dr
        
        if self._box_at(nc, nr) or self._barrel_at(nc, nr):
            return None
        if self._is_blocked(nc, nr):
            return None
            
        self.player.col, self.player.row = nc, nr
        self._update_door()
        return self._check_triggers()
    
    def try_interact(self) -> str | None:
        """Intenta empujar un objeto."""
        dc, dr = self.player.facing_dir
        nc, nr = self.player.col + dc, self.player.row + dr
        
        # Empujar caja
        if self._box_at(nc, nr):
            bc, br = nc + dc, nr + dr
            if self._is_blocked(bc, br) or self._box_at(bc, br) or self._is_water(bc, br):
                return None
            self.box.col, self.box.row = bc, br
            self._update_door()
            return self._check_triggers()
        
        # Empujar barril
        elif self._barrel_at(nc, nr):
            bc, br = nc + dc, nr + dr
            if self._is_blocked(bc, br) or self._barrel_at(bc, br):
                return None
            
            self.barrel.col, self.barrel.row = bc, br
            if self._tile_at(bc, br) == WATER:
                self.barrel_bridges.add((bc, br))
                self.barrel_used = True
            
            self._update_door()
            return self._check_triggers()
        
        return None
    
    def reset(self):
        """Reinicia el nivel a su estado inicial."""
        self.player.reset()
        self.box.reset()
        self.barrel.reset()
        self.barrel_used = False
        self.barrel_bridges.clear()
        self.dim = "A"
        self._update_door()