"""
================================================================================
LÓGICA DE RENDERIZADO
================================================================================
Este archivo contiene las clases y funciones responsables de dibujar
todos los elementos del juego en la pantalla.
"""
import pygame
from level import Level
from config import (
    TS, ROWS, COLS, PALETTE, WALL, WATER, FLOOR, FLOOR_DECO,
    CLR_PLATE_ON, CLR_PLATE_OFF, CLR_DOOR_OPEN, CLR_DOOR_CLOSED, CLR_WHITE,
    CLR_BOX, CLR_BOX_EDGE, CLR_BARREL, CLR_BARREL_EDGE, CLR_DEBRIS,
    CLR_PLAYER, CLR_PLAYER_EDGE, WON
)

class TileRenderer:
    """Dibuja el tilemap (mapa de baldosas) en la pantalla."""
    def draw(self, surface: pygame.Surface, grid: list[list[int]],
             dim: str, barrel_bridges: set = None):
        if barrel_bridges is None:
            barrel_bridges = set()
        
        pal = PALETTE[dim]

        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(c * TS, r * TS, TS, TS)
                tile = grid[r][c]

                if tile == WALL:
                    pygame.draw.rect(surface, pal[WALL], rect)
                    pygame.draw.rect(surface, pal["wall_shade"], rect, 1)
                elif tile == WATER:
                    if (c, r) in barrel_bridges:
                        clr = pal[FLOOR_DECO]
                        pygame.draw.rect(surface, clr, rect)
                        pygame.draw.rect(surface, pal["grid_line"], rect, 1)
                    else:
                        pygame.draw.rect(surface, pal[WATER], rect)
                        darker = tuple(max(0, v - 25) for v in pal[WATER])
                        pygame.draw.line(surface, darker, (rect.left, rect.top + TS // 3), (rect.right, rect.top + TS // 3), 1)
                        pygame.draw.line(surface, darker, (rect.left, rect.top + 2 * TS // 3), (rect.right, rect.top + 2 * TS // 3), 1)
                else:  # FLOOR o FLOOR_DECO
                    clr = pal[FLOOR_DECO] if tile == FLOOR_DECO else pal[FLOOR]
                    pygame.draw.rect(surface, clr, rect)
                    pygame.draw.rect(surface, pal["grid_line"], rect, 1)
                    if tile == FLOOR_DECO:
                        dot_c = tuple(max(0, v - 30) for v in clr)
                        pygame.draw.circle(surface, dot_c, rect.center, 1)

class GameRenderer:
    """Renderiza el estado completo del juego, incluyendo entidades y HUD."""
    def __init__(self):
        self.tile_renderer = TileRenderer()
        self.font_big = pygame.font.SysFont("Arial", 42, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 22)
        self.font_small = pygame.font.SysFont("Arial", 16)

    def draw(self, surface: pygame.Surface, lv: Level, game_state: str, death_reason: str):
        """Dibuja un frame completo del juego."""
        pal = PALETTE[lv.dim]
        surface.fill(pal["wall_shade"])
        self.tile_renderer.draw(surface, lv.grid, lv.dim, lv.barrel_bridges)
        self._draw_plate(surface, lv)
        self._draw_door(surface, lv)
        if lv.dim == "B":
            self._draw_box(surface, lv)
            self._draw_barrel(surface, lv)
        self._draw_debris(surface, lv)
        self._draw_player(surface, lv)
        self._draw_hud(surface, lv, pal)
        if game_state != "running":
            self._draw_overlay(surface, game_state, death_reason)
        pygame.display.flip()

    def _draw_plate(self, surface: pygame.Surface, lv: Level):
        plate = lv.plate
        pressed = plate.is_pressed_by(lv.player, lv.box, lv.dim)
        clr = CLR_PLATE_ON if pressed else CLR_PLATE_OFF
        cx, cy = plate.col * TS + TS // 2, plate.row * TS + TS // 2
        r = TS // 2 - 8
        pygame.draw.circle(surface, clr, (cx, cy), r)
        edge = tuple(max(0, v - 55) for v in clr)
        pygame.draw.circle(surface, edge, (cx, cy), r, 2)

    def _draw_door(self, surface: pygame.Surface, lv: Level):
        door = lv.door
        for col, row in [(door.col1, door.row1), (door.col2, door.row2)]:
            rect = pygame.Rect(col * TS, row * TS, TS, TS)
            if door.is_open:
                pygame.draw.rect(surface, CLR_DOOR_OPEN, rect)
                pygame.draw.rect(surface, (25, 160, 40), rect, 1)
            else:
                pygame.draw.rect(surface, CLR_DOOR_CLOSED, rect)
                pygame.draw.rect(surface, (150, 25, 25), rect, 1)
                pygame.draw.line(surface, CLR_WHITE, (rect.left + 1, rect.top + 1), (rect.right - 1, rect.bottom - 1), 1)
                pygame.draw.line(surface, CLR_WHITE, (rect.right - 1, rect.top + 1), (rect.left + 1, rect.bottom - 1), 1)

    def _draw_box(self, surface: pygame.Surface, lv: Level):
        box = lv.box
        sr = pygame.Rect(box.col * TS + 1, box.row * TS + 1, TS - 1, TS - 1)
        pygame.draw.rect(surface, (60, 40, 20), sr)
        rect = pygame.Rect(box.col * TS + 1, box.row * TS + 1, TS - 2, TS - 2)
        pygame.draw.rect(surface, CLR_BOX, rect)
        pygame.draw.rect(surface, CLR_BOX_EDGE, rect, 1)

    def _draw_barrel(self, surface: pygame.Surface, lv: Level):
        barrel = lv.barrel
        sr = pygame.Rect(barrel.col * TS + 1, barrel.row * TS + 1, TS - 1, TS - 1)
        pygame.draw.rect(surface, (60, 40, 20), sr)
        cx, cy = barrel.col * TS + TS // 2, barrel.row * TS + TS // 2
        r = TS // 2 - 8
        pygame.draw.circle(surface, CLR_BARREL, (cx, cy), r)
        pygame.draw.circle(surface, CLR_BARREL_EDGE, (cx, cy), r, 1)

    def _draw_debris(self, surface: pygame.Surface, lv: Level):
        for debris in lv.debris:
            rect = pygame.Rect(debris.col * TS, debris.row * TS, TS, TS)
            pygame.draw.rect(surface, CLR_DEBRIS, rect)
            pygame.draw.rect(surface, (70, 50, 25), rect, 1)

    def _draw_player(self, surface: pygame.Surface, lv: Level):
        px, py = lv.player.col * TS + TS // 2, lv.player.row * TS + TS // 2
        r = TS // 2 - 8
        pygame.draw.circle(surface, (40, 35, 30), (px + 2, py + 3), r)
        pygame.draw.circle(surface, CLR_PLAYER, (px, py), r)
        pygame.draw.circle(surface, CLR_PLAYER_EDGE, (px, py), r, 2)
        pygame.draw.circle(surface, (25, 85, 25), (px - 3, py - 3), 2)
        pygame.draw.circle(surface, (25, 85, 25), (px + 3, py - 3), 2)

    def _draw_hud(self, surface: pygame.Surface, lv: Level, pal: dict):
        bar = pygame.Surface((surface.get_width(), 40), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 150))
        surface.blit(bar, (0, 0))
        
        dim_text = "Dimension A  (Original)" if lv.dim == "A" else "Dimension B  (Opuesta)"
        surf = self.font_med.render(dim_text, True, pal["hud_dim"])
        surface.blit(surf, (8, 3))
        
        st = "Abierta" if lv.door.is_open else "Cerrada"
        info = self.font_small.render(f"Puerta: {st}  |  ESPACIO: cambiar dim  |  E: empujar", True, (180, 180, 180))
        surface.blit(info, (8, 22))

    def _draw_overlay(self, surface: pygame.Surface, game_state: str, death_reason: str):
        ov = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 175))
        surface.blit(ov, (0, 0))
        
        cx, cy = surface.get_width() // 2, surface.get_height() // 2
        
        if game_state == WON:
            title, t_clr = "Has ganado!", (55, 255, 80)
            sub = "Has resuelto el puzzle dimensional."
        else:
            title, t_clr = "Has muerto", (255, 65, 65)
            sub = death_reason
        
        ts = self.font_big.render(title, True, t_clr)
        ss = self.font_med.render(sub, True, (200, 200, 200))
        rs = self.font_med.render("Pulsa R para reiniciar", True, (160, 160, 160))
        
        surface.blit(ts, ts.get_rect(center=(cx, cy - 40)))
        surface.blit(ss, ss.get_rect(center=(cx, cy + 10)))
        surface.blit(rs, rs.get_rect(center=(cx, cy + 45)))