"""
Sistema de renderizado basado en capas TMX.
Dibuja: walls, paths, bridges (segun dimension), buttons, barrels, door, player, HUD.
Tambien: dialogos, NPCs, pantalla de victoria final.
"""
import math
import os
import pygame
from src.core.level import Level
from src.core.config import TILE_SIZE, PALETTE, WON, DIALOGUE, GAME_COMPLETED
from src.rendering.particles import ParticleManager


def _load_sprite(relative_path: str, size: tuple[int, int]) -> pygame.Surface:
    """Carga un sprite y lo escala al tamano indicado."""
    path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", relative_path)
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)


class GameRenderer:
    """Renderizador principal del juego."""

    def __init__(self):
        self.particle_manager = ParticleManager()
        self.font_big = pygame.font.SysFont("Arial", 42, bold=True)
        self.font_med = pygame.font.SysFont("Arial", 22)
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_dialogue_name = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_dialogue_text = pygame.font.SysFont("Arial", 16)
        self.font_title_big = pygame.font.SysFont("Consolas", 48, bold=True)

        sprite_size = (TILE_SIZE, TILE_SIZE)
        self.player_sprites = {
            (0, -1): _load_sprite(os.path.join("player", "backfronton 1.png"), sprite_size),
            (0,  1): _load_sprite(os.path.join("player", "frontfronton 1.png"), sprite_size),
            (-1, 0): _load_sprite(os.path.join("player", "leftfronton 1.png"), sprite_size),
            (1,  0): _load_sprite(os.path.join("player", "rightfronton 1.png"), sprite_size),
        }
        self.barrel_sprites = {
            "green": _load_sprite("barril verde.png", sprite_size),
            "yellow": _load_sprite("barril amarillo.png", sprite_size),
            "red": _load_sprite("barril rojo.png", sprite_size),
        }

        # Sprite de Jeffry
        jeffry_path = os.path.join("Jeff", "jeffry.png")
        self.jeffry_sprite = _load_sprite(jeffry_path, sprite_size)

        # Overlays cacheados
        self._btn_pressed_overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self._btn_pressed_overlay.fill((0, 255, 0, 60))

    def draw(self, surface: pygame.Surface, level: Level,
             game_state: str, death_reason: str, delta_time: float,
             dialogue_box=None, level_index: int = 0):
        surface.fill((0, 0, 0))

        # Dibujar capas en orden
        self._draw_layer_tiles(surface, level.walls)
        self._draw_layer_tiles(surface, level.paths)
        self._draw_bridges(surface, level)
        self._draw_buttons(surface, level)
        self._draw_door(surface, level)

        # Tinte dimensional
        self._apply_dimension_tint(surface, level)

        # Barriles y jugador
        self._draw_barrels(surface, level)
        self._draw_npcs(surface, level)
        self._draw_player(surface, level)

        # Particulas
        self._process_particle_events(level)
        self.particle_manager.update(delta_time)
        self.particle_manager.draw(surface)

        # HUD
        self._draw_hud(surface, level)

        # Indicador de interaccion con E
        self._draw_interact_hint(surface, level)

        # Alerta
        level.update_alert(delta_time)
        if level.alert_message:
            self._draw_alert(surface, level.alert_message, level.alert_timer)

        # Dialogo
        if game_state == DIALOGUE and dialogue_box:
            self._draw_dialogue(surface, dialogue_box)

        # Overlay de fin
        if game_state == GAME_COMPLETED:
            self._draw_game_completed(surface)
        elif game_state not in ("running", DIALOGUE):
            self._draw_overlay(surface, game_state, death_reason)

        pygame.display.flip()

    def _draw_layer_tiles(self, surface: pygame.Surface, tiles: list):
        """Dibuja una lista de tiles (x, y, surface)."""
        for x, y, tile_surf in tiles:
            surface.blit(tile_surf, (x * TILE_SIZE, y * TILE_SIZE))

    def _draw_bridges(self, surface: pygame.Surface, level: Level):
        """Dibuja los puentes de la dimension actual."""
        for dim_key, bridge in level.bridges.items():
            if dim_key == level.dim:
                for x, y, tile_surf in bridge["tiles"]:
                    surface.blit(tile_surf, (x * TILE_SIZE, y * TILE_SIZE))

    def _draw_buttons(self, surface: pygame.Surface, level: Level):
        """Dibuja los botones con su sprite del tileset."""
        for btn in level.buttons:
            x, y = btn["pos"]
            surface.blit(btn["surface"], (x * TILE_SIZE, y * TILE_SIZE))
            if btn.get("pressed", False):
                surface.blit(self._btn_pressed_overlay, (x * TILE_SIZE, y * TILE_SIZE))

    def _draw_door(self, surface: pygame.Surface, level: Level):
        """Dibuja la puerta de salida."""
        if level.door_pos is None:
            return
        dx, dy = level.door_pos
        rect = pygame.Rect(dx * TILE_SIZE, dy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if level.door_open:
            pygame.draw.rect(surface, (35, 200, 55), rect)
            # Borde
            pygame.draw.rect(surface, (25, 150, 40), rect, 3)
        else:
            pygame.draw.rect(surface, (195, 35, 35), rect)
            pygame.draw.rect(surface, (140, 25, 25), rect, 3)

    def _draw_barrels(self, surface: pygame.Surface, level: Level):
        """Dibuja los barriles de la dimension actual con su color."""
        for barrel in level.barrels:
            if barrel["dim"] == level.dim:
                x = barrel["col"] * TILE_SIZE
                y = barrel["row"] * TILE_SIZE
                sprite = self.barrel_sprites.get(
                    barrel.get("type", "green"),
                    self.barrel_sprites["green"],
                )
                surface.blit(sprite, (x, y))

    def _draw_npcs(self, surface: pygame.Surface, level: Level):
        """Dibuja los NPCs del nivel."""
        for npc in level.npcs:
            x = npc["col"] * TILE_SIZE
            y = npc["row"] * TILE_SIZE
            if npc["type"] == "jeffry":
                surface.blit(self.jeffry_sprite, (x, y))
            # Indicador de nombre sobre el NPC
            name = "Jeffrey Epstein" if npc["type"] == "jeffry" else npc["type"].capitalize()
            name_surf = self.font_small.render(name, True, (255, 255, 200))
            name_rect = name_surf.get_rect(centerx=x + TILE_SIZE // 2, bottom=y - 2)
            surface.blit(name_surf, name_rect)

    def _draw_interact_hint(self, surface: pygame.Surface, level: Level):
        """Muestra '[E] Hablar' cuando el jugador esta cerca de un NPC."""
        npc = level.try_interact()
        if npc and not npc.get("talked", False):
            px = level.player.col * TILE_SIZE + TILE_SIZE // 2
            py = level.player.row * TILE_SIZE - 8
            hint = self.font_small.render("[E] Hablar", True, (255, 255, 100))
            hint_rect = hint.get_rect(centerx=px, bottom=py)
            surface.blit(hint, hint_rect)

    def _apply_dimension_tint(self, surface: pygame.Surface, level: Level):
        tint = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        if level.dim == "A":
            tint.fill((255, 200, 100, 25))
        else:
            tint.fill((80, 120, 255, 35))
        surface.blit(tint, (0, 0))

        # Shader rojo sangre en agua para dim B
        if level.dim == "B" and level.water_positions:
            self._draw_blood_water(surface, level)

    def _draw_blood_water(self, surface: pygame.Surface, level: Level):
        """Aplica un efecto rojo sangre sobre tiles de agua en dim B."""
        pulse = int(80 + 25 * math.sin(pygame.time.get_ticks() / 400.0))
        overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        overlay.fill((180, 15, 15, pulse))
        for wx, wy in level.water_positions:
            surface.blit(overlay, (wx * TILE_SIZE, wy * TILE_SIZE))

    def _process_particle_events(self, level: Level):
        for event in level.pending_particle_events:
            if event["type"] == "dimension_switch":
                self.particle_manager.spawn_dimension_switch(
                    event["col"], event["row"], event["new_dim"])
        level.pending_particle_events.clear()

    def _draw_player(self, surface: pygame.Surface, level: Level):
        x = level.player.col * TILE_SIZE
        y = level.player.row * TILE_SIZE
        facing = level.player.facing_dir
        sprite = self.player_sprites.get(facing, self.player_sprites[(0, 1)])
        surface.blit(sprite, (x, y))

    def _draw_hud(self, surface: pygame.Surface, level: Level):
        pal = PALETTE[level.dim]
        bar = pygame.Surface((surface.get_width(), 40), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 150))
        surface.blit(bar, (0, 0))

        dim_text = ("Dimension A" if level.dim == "A" else "Dimension B")
        surf = self.font_med.render(dim_text, True, pal["hud_dim"])
        surface.blit(surf, (8, 3))

        # Contar botones
        pressed = sum(1 for b in level.buttons if b.get("pressed", False))
        total = len(level.buttons)
        door_status = "ABIERTA" if level.door_open else "CERRADA"
        info_text = f"Botones: {pressed}/{total}  |  Puerta: {door_status}  |  ESPACIO: cambiar dim"
        info = self.font_small.render(info_text, True, (180, 180, 180))
        surface.blit(info, (8, 22))

    def _draw_dialogue(self, surface: pygame.Surface, dialogue_box):
        """Dibuja la caja de dialogo en la parte inferior de la pantalla."""
        w = surface.get_width()
        h = surface.get_height()

        # Fondo semitransparente
        box_h = 100
        box_y = h - box_h - 10
        box_surf = pygame.Surface((w - 20, box_h), pygame.SRCALPHA)
        box_surf.fill((0, 0, 0, 210))
        surface.blit(box_surf, (10, box_y))

        # Borde cyan
        box_rect = pygame.Rect(10, box_y, w - 20, box_h)
        pygame.draw.rect(surface, (0, 180, 200), box_rect, 2)

        # Nombre del hablante
        speaker = dialogue_box.current_speaker
        speaker_color = (0, 220, 255) if speaker != "Jeffrey Epstein" else (255, 215, 0)
        name_surf = self.font_dialogue_name.render(speaker, True, speaker_color)
        surface.blit(name_surf, (22, box_y + 8))

        # Texto del dialogo (con word wrap basico)
        text = dialogue_box.current_text
        max_width = w - 50
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = current_line + (" " if current_line else "") + word
            if self.font_dialogue_text.size(test)[0] <= max_width:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines):
            line_surf = self.font_dialogue_text.render(line, True, (220, 220, 220))
            surface.blit(line_surf, (22, box_y + 32 + i * 20))

        # Indicador de avance
        pulse = int(180 + 60 * math.sin(pygame.time.get_ticks() / 300.0))
        hint = self.font_small.render("[ENTER] continuar", True, (pulse, pulse, pulse))
        surface.blit(hint, (w - hint.get_width() - 20, box_y + box_h - 22))

    def _draw_alert(self, surface: pygame.Surface, message: str, timer: float):
        """Dibuja un mensaje de alerta en la parte inferior."""
        alpha = min(255, int(timer * 200))
        w = surface.get_width()
        h = surface.get_height()
        alert_surf = pygame.Surface((w, 36), pygame.SRCALPHA)
        alert_surf.fill((180, 30, 30, alpha))
        surface.blit(alert_surf, (0, h - 36))
        text = self.font_small.render(message, True, (255, 255, 255))
        text.set_alpha(alpha)
        surface.blit(text, text.get_rect(center=(w // 2, h - 18)))

    def _draw_overlay(self, surface: pygame.Surface, game_state: str,
                      death_reason: str):
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        surface.blit(overlay, (0, 0))

        center_x = surface.get_width() // 2
        center_y = surface.get_height() // 2

        if game_state == WON:
            title = "Nivel completado!"
            title_color = (55, 255, 80)
            subtitle = "Has abierto la puerta y escapado."
            controls = "ENTER: Siguiente nivel  |  R: Repetir  |  ESC: Menu"
        else:
            title = "Has muerto"
            title_color = (255, 65, 65)
            subtitle = death_reason
            controls = "R: Reintentar  |  ESC: Menu"

        title_surf = self.font_big.render(title, True, title_color)
        sub_surf = self.font_med.render(subtitle, True, (200, 200, 200))
        ctrl_surf = self.font_small.render(controls, True, (160, 160, 160))

        surface.blit(title_surf,
                     title_surf.get_rect(center=(center_x, center_y - 40)))
        surface.blit(sub_surf,
                     sub_surf.get_rect(center=(center_x, center_y + 10)))
        surface.blit(ctrl_surf,
                     ctrl_surf.get_rect(center=(center_x, center_y + 45)))

    def _draw_game_completed(self, surface: pygame.Surface):
        """Pantalla de victoria final: juego completado."""
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        cx = surface.get_width() // 2
        cy = surface.get_height() // 2

        # Titulo pulsante
        pulse = int(220 + 35 * math.sin(pygame.time.get_ticks() / 500.0))
        title_color = (pulse, 255, pulse)
        title = self.font_title_big.render("FRACTURE", True, title_color)
        surface.blit(title, title.get_rect(center=(cx, cy - 80)))

        sub = self.font_big.render("Juego Completado!", True, (55, 255, 120))
        surface.blit(sub, sub.get_rect(center=(cx, cy - 25)))

        # Texto narrativo final
        lines = [
            "Gracias a tu valentia y la ayuda de Jeffrey Epstein,",
            "las dos dimensiones se han estabilizado.",
            "La fractura ha sido sellada para siempre.",
        ]
        for i, line in enumerate(lines):
            line_surf = self.font_med.render(line, True, (200, 200, 220))
            surface.blit(line_surf, line_surf.get_rect(center=(cx, cy + 25 + i * 28)))

        ctrl = self.font_small.render("ENTER o ESC: Volver al menu", True, (140, 140, 140))
        surface.blit(ctrl, ctrl.get_rect(center=(cx, cy + 120)))
