"""
================================================================================
SISTEMA DE RENDERIZADO
================================================================================
Este archivo se encarga de DIBUJAR todo lo que se ve en pantalla:
    - El mapa de casillas (tiles).
    - Las entidades (jugador, barriles, puerta, placa...).
    - El HUD (información en la parte superior).
    - Las pantallas de fin de juego (victoria/derrota).
    - Los efectos de partículas.

CONSEJO PARA JUNIORS:
    - "Renderizar" = dibujar en pantalla.
    - Pygame dibuja por capas: primero el fondo, luego los objetos, luego el HUD.
    - Cada entidad tiene su propio método de dibujo (_draw_XXX).
    - Los colores se definen como tuplas RGB: (rojo, verde, azul) de 0 a 255.
"""
import pygame
from src.core.level import Level
from src.core.config import (
    TILE_SIZE, ROWS, COLS, PALETTE, WALL, WATER, FLOOR, FLOOR_DECO,
    CLR_PLATE_ON, CLR_PLATE_OFF, CLR_DOOR_OPEN, CLR_DOOR_CLOSED, CLR_WHITE,
    CLR_BARREL, CLR_BARREL_EDGE, CLR_BARREL_LOCKED, CLR_DEBRIS,
    CLR_PLAYER, CLR_PLAYER_EDGE, WON,
)
from src.rendering.particles import ParticleManager


class TileRenderer:
    """
    Dibuja el mapa de casillas (tiles) en la pantalla.
    Cada casilla se dibuja según su tipo (suelo, muro, agua...).
    """

    def draw(self, surface: pygame.Surface, grid: list[list[int]],
             dim: str, barrel_bridges: set):
        """
        Dibuja todas las casillas del mapa.

        Args:
            surface: Superficie de Pygame donde dibujar.
            grid: La cuadrícula del mapa (lista 2D de tipos de casilla).
            dim: Dimensión actual ("A" o "B") para elegir la paleta.
            barrel_bridges: Conjunto de posiciones donde hay puentes de barril.
        """
        pal = PALETTE[dim]

        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE,
                                   TILE_SIZE, TILE_SIZE)
                tile = grid[row][col]

                if tile == WALL:
                    # Muro: color sólido con borde sombreado
                    pygame.draw.rect(surface, pal[WALL], rect)
                    pygame.draw.rect(surface, pal["wall_shade"], rect, 1)

                elif tile == WATER:
                    if (col, row) in barrel_bridges:
                        # Puente de barril: se dibuja como suelo decorado
                        pygame.draw.rect(surface, pal[FLOOR_DECO], rect)
                        pygame.draw.rect(surface, pal["grid_line"], rect, 1)
                    else:
                        # Agua: color de agua con líneas onduladas
                        pygame.draw.rect(surface, pal[WATER], rect)
                        darker = tuple(max(0, v - 25) for v in pal[WATER])
                        y1 = rect.top + TILE_SIZE // 3
                        y2 = rect.top + 2 * TILE_SIZE // 3
                        pygame.draw.line(surface, darker,
                                         (rect.left, y1), (rect.right, y1), 1)
                        pygame.draw.line(surface, darker,
                                         (rect.left, y2), (rect.right, y2), 1)

                else:
                    # Suelo normal o decorado
                    color = pal[FLOOR_DECO] if tile == FLOOR_DECO else pal[FLOOR]
                    pygame.draw.rect(surface, color, rect)
                    pygame.draw.rect(surface, pal["grid_line"], rect, 1)
                    # Punto decorativo en casillas FLOOR_DECO
                    if tile == FLOOR_DECO:
                        dot_color = tuple(max(0, v - 30) for v in color)
                        pygame.draw.circle(surface, dot_color, rect.center, 1)


class GameRenderer:
    """
    Renderizador principal del juego.
    Coordina el dibujo de todos los elementos: tiles, entidades, HUD y partículas.
    """

    def __init__(self):
        """Inicializa las fuentes de texto y los sub-renderizadores."""
        self.tile_renderer = TileRenderer()
        self.particle_manager = ParticleManager()
        self.font_big = pygame.font.SysFont("Arial", 42, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 22)
        self.font_small = pygame.font.SysFont("Arial", 16)

    def draw(self, surface: pygame.Surface, level: Level,
             game_state: str, death_reason: str, delta_time: float):
        """
        Dibuja un frame completo del juego.

        Args:
            surface: Superficie de Pygame donde dibujar.
            level: El objeto Level con todo el estado del juego.
            game_state: Estado actual ("running", "dead", "won").
            death_reason: Texto explicando la causa de la muerte.
            delta_time: Tiempo desde el último frame (para partículas).
        """
        pal = PALETTE[level.dim]

        # Paso 1: Rellenar el fondo
        surface.fill(pal["wall_shade"])

        # Paso 2: Dibujar las casillas del mapa
        self.tile_renderer.draw(surface, level.grid, level.dim,
                                level.barrel_bridges)

        # Paso 3: Dibujar las entidades
        self._draw_plate(surface, level)
        self._draw_door(surface, level)
        if level.dim == "B":
            self._draw_barrels(surface, level)
        self._draw_debris(surface, level)
        self._draw_player(surface, level)

        # Paso 4: Procesar eventos de partículas pendientes
        self._process_particle_events(level)

        # Paso 5: Actualizar y dibujar partículas
        self.particle_manager.update(delta_time)
        self.particle_manager.draw(surface)

        # Paso 6: Dibujar el HUD (encima de todo)
        self._draw_hud(surface, level, pal)

        # Paso 7: Dibujar pantalla de fin si no estamos jugando
        if game_state != "running":
            self._draw_overlay(surface, game_state, death_reason)

        # Paso 8: Actualizar la pantalla
        pygame.display.flip()

    def _process_particle_events(self, level: Level):
        """
        Lee los eventos de partículas pendientes del nivel y los ejecuta.
        Después de procesarlos, limpia la lista.
        """
        for event in level.pending_particle_events:
            if event["type"] == "water_splash":
                self.particle_manager.spawn_water_splash(
                    event["col"], event["row"])
            elif event["type"] == "dimension_switch":
                self.particle_manager.spawn_dimension_switch(
                    event["col"], event["row"], event["new_dim"])
            elif event["type"] == "push":
                self.particle_manager.spawn_push_effect(
                    event["col"], event["row"])

        level.pending_particle_events.clear()

    # =========================================================================
    # MÉTODOS DE DIBUJO DE ENTIDADES
    # =========================================================================

    def _draw_plate(self, surface: pygame.Surface, level: Level):
        """Dibuja la placa de presión (amarilla si activada, apagada si no)."""
        plate = level.plate
        pressed = plate.is_pressed_by(level.player, level.barrels, level.dim)
        color = CLR_PLATE_ON if pressed else CLR_PLATE_OFF

        center_x = plate.col * TILE_SIZE + TILE_SIZE // 2
        center_y = plate.row * TILE_SIZE + TILE_SIZE // 2
        radius = TILE_SIZE // 2 - 8

        pygame.draw.circle(surface, color, (center_x, center_y), radius)
        edge_color = tuple(max(0, v - 55) for v in color)
        pygame.draw.circle(surface, edge_color, (center_x, center_y), radius, 2)

    def _draw_door(self, surface: pygame.Surface, level: Level):
        """Dibuja la puerta doble (verde si abierta, roja con X si cerrada)."""
        door = level.door
        for col, row in [(door.col1, door.row1), (door.col2, door.row2)]:
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE,
                               TILE_SIZE, TILE_SIZE)
            if door.is_open:
                pygame.draw.rect(surface, CLR_DOOR_OPEN, rect)
                pygame.draw.rect(surface, (25, 160, 40), rect, 1)
            else:
                pygame.draw.rect(surface, CLR_DOOR_CLOSED, rect)
                pygame.draw.rect(surface, (150, 25, 25), rect, 1)
                # Dibujar una X para indicar que está cerrada
                pygame.draw.line(surface, CLR_WHITE,
                                 (rect.left + 1, rect.top + 1),
                                 (rect.right - 1, rect.bottom - 1), 1)
                pygame.draw.line(surface, CLR_WHITE,
                                 (rect.right - 1, rect.top + 1),
                                 (rect.left + 1, rect.bottom - 1), 1)

    def _draw_barrels(self, surface: pygame.Surface, level: Level):
        """Dibuja todos los barriles (marrones normales, grises si bloqueados)."""
        for barrel in level.barrels:
            center_x = barrel.col * TILE_SIZE + TILE_SIZE // 2
            center_y = barrel.row * TILE_SIZE + TILE_SIZE // 2
            radius = TILE_SIZE // 2 - 8

            # Sombra del barril
            shadow_rect = pygame.Rect(
                barrel.col * TILE_SIZE + 1,
                barrel.row * TILE_SIZE + 1,
                TILE_SIZE - 1, TILE_SIZE - 1,
            )
            pygame.draw.rect(surface, (60, 40, 20), shadow_rect)

            # Color según si está bloqueado o no
            if barrel.locked:
                body_color = CLR_BARREL_LOCKED
                edge_color = (60, 60, 60)
            else:
                body_color = CLR_BARREL
                edge_color = CLR_BARREL_EDGE

            pygame.draw.circle(surface, body_color, (center_x, center_y), radius)
            pygame.draw.circle(surface, edge_color, (center_x, center_y), radius, 1)

    def _draw_debris(self, surface: pygame.Surface, level: Level):
        """Dibuja los escombros (obstáculos marrones)."""
        for debris in level.debris:
            rect = pygame.Rect(debris.col * TILE_SIZE, debris.row * TILE_SIZE,
                               TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, CLR_DEBRIS, rect)
            pygame.draw.rect(surface, (70, 50, 25), rect, 1)

    def _draw_player(self, surface: pygame.Surface, level: Level):
        """Dibuja al jugador (círculo verde con ojos)."""
        px = level.player.col * TILE_SIZE + TILE_SIZE // 2
        py = level.player.row * TILE_SIZE + TILE_SIZE // 2
        radius = TILE_SIZE // 2 - 8

        # Sombra
        pygame.draw.circle(surface, (40, 35, 30), (px + 2, py + 3), radius)
        # Cuerpo
        pygame.draw.circle(surface, CLR_PLAYER, (px, py), radius)
        # Borde
        pygame.draw.circle(surface, CLR_PLAYER_EDGE, (px, py), radius, 2)
        # Ojos
        pygame.draw.circle(surface, (25, 85, 25), (px - 3, py - 3), 2)
        pygame.draw.circle(surface, (25, 85, 25), (px + 3, py - 3), 2)

    # =========================================================================
    # HUD Y PANTALLAS DE FIN
    # =========================================================================

    def _draw_hud(self, surface: pygame.Surface, level: Level, pal: dict):
        """Dibuja la barra de información superior."""
        # Fondo semitransparente
        bar = pygame.Surface((surface.get_width(), 40), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 150))
        surface.blit(bar, (0, 0))

        # Texto de dimensión actual
        dim_text = ("Dimension A  (Original)" if level.dim == "A"
                    else "Dimension B  (Opuesta)")
        surf = self.font_med.render(dim_text, True, pal["hud_dim"])
        surface.blit(surf, (8, 3))

        # Controles e información
        door_state = "Abierta" if level.door.is_open else "Cerrada"
        info_text = (f"Puerta: {door_state}  |  "
                     f"ESPACIO: cambiar dim  |  E: empujar")
        info = self.font_small.render(info_text, True, (180, 180, 180))
        surface.blit(info, (8, 22))

    def _draw_overlay(self, surface: pygame.Surface, game_state: str,
                      death_reason: str):
        """Dibuja la pantalla de victoria o derrota."""
        # Fondo oscuro semitransparente
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        surface.blit(overlay, (0, 0))

        center_x = surface.get_width() // 2
        center_y = surface.get_height() // 2

        # Elegir textos según el estado
        if game_state == WON:
            title = "Has ganado!"
            title_color = (55, 255, 80)
            subtitle = "Has resuelto el puzzle dimensional."
        else:
            title = "Has muerto"
            title_color = (255, 65, 65)
            subtitle = death_reason

        # Renderizar textos
        title_surf = self.font_big.render(title, True, title_color)
        sub_surf = self.font_med.render(subtitle, True, (200, 200, 200))
        restart_surf = self.font_med.render("Pulsa R para reiniciar",
                                            True, (160, 160, 160))

        # Colocar textos centrados
        surface.blit(title_surf,
                     title_surf.get_rect(center=(center_x, center_y - 40)))
        surface.blit(sub_surf,
                     sub_surf.get_rect(center=(center_x, center_y + 10)))
        surface.blit(restart_surf,
                     restart_surf.get_rect(center=(center_x, center_y + 45)))
