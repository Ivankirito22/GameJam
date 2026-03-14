"""
Sistema de renderizado profesional para FRACTURE.
HUD cinematografico, dialogos estilo visual novel, efectos post-proceso.
"""
import math
import os
import random
import pygame
from src.core.level import Level
from src.core.config import TILE_SIZE, PALETTE, WON, DIALOGUE, GAME_COMPLETED
from src.rendering.particles import ParticleManager

# --- Paleta UI ---
_UI_BG = (6, 6, 14)
_UI_ACCENT_A = (255, 185, 60)
_UI_ACCENT_B = (60, 140, 255)
_UI_CYAN = (0, 210, 220)
_UI_CYAN_GLOW = (0, 255, 255)
_UI_GREEN = (40, 220, 80)
_UI_RED = (220, 50, 50)
_UI_GOLD = (255, 215, 0)
_UI_WHITE = (230, 230, 235)
_UI_GREY = (130, 130, 140)
_UI_DARK = (20, 20, 30)


def _load_sprite(relative_path: str, size: tuple[int, int]) -> pygame.Surface:
    path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", relative_path)
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)


def _rounded_rect(surface: pygame.Surface, rect: pygame.Rect,
                  color: tuple, border_radius: int = 8, alpha: int = 255):
    """Dibuja un rectangulo redondeado con alpha."""
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*color[:3], alpha), s.get_rect(), border_radius=border_radius)
    surface.blit(s, rect.topleft)


def _draw_text_shadow(surface: pygame.Surface, font: pygame.font.Font,
                      text: str, pos: tuple, color: tuple, shadow_color=(0, 0, 0)):
    """Dibuja texto con sombra sutil."""
    shadow = font.render(text, True, shadow_color)
    shadow.set_alpha(120)
    surface.blit(shadow, (pos[0] + 1, pos[1] + 1))
    main = font.render(text, True, color)
    surface.blit(main, pos)


class GameRenderer:
    """Renderizador principal del juego con interfaz profesional."""

    def __init__(self):
        self.particle_manager = ParticleManager()
        self._time = 0.0

        # Fuentes
        self.f_hud_title = pygame.font.SysFont("Consolas", 15, bold=True)
        self.f_hud_info = pygame.font.SysFont("Consolas", 12)
        self.f_hud_key = pygame.font.SysFont("Consolas", 11, bold=True)
        self.f_hud_label = pygame.font.SysFont("Consolas", 10)

        self.f_dlg_name = pygame.font.SysFont("Consolas", 16, bold=True)
        self.f_dlg_text = pygame.font.SysFont("Segoe UI", 15)
        self.f_dlg_hint = pygame.font.SysFont("Consolas", 11)

        self.f_overlay_title = pygame.font.SysFont("Consolas", 38, bold=True)
        self.f_overlay_sub = pygame.font.SysFont("Segoe UI", 18)
        self.f_overlay_ctrl = pygame.font.SysFont("Consolas", 13)
        self.f_overlay_small = pygame.font.SysFont("Segoe UI", 14)

        self.f_alert = pygame.font.SysFont("Segoe UI", 13, bold=True)

        self.f_npc_name = pygame.font.SysFont("Consolas", 11, bold=True)
        self.f_interact = pygame.font.SysFont("Consolas", 12, bold=True)

        self.f_completed_title = pygame.font.SysFont("Consolas", 52, bold=True)
        self.f_completed_sub = pygame.font.SysFont("Consolas", 28, bold=True)
        self.f_completed_text = pygame.font.SysFont("Segoe UI", 16)
        self.f_completed_ctrl = pygame.font.SysFont("Consolas", 12)

        # Sprites
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
        self.jeffry_sprite = _load_sprite(os.path.join("Jeff", "jeffry.png"), sprite_size)

        # Overlays cacheados
        self._btn_pressed_overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        self._btn_pressed_overlay.fill((0, 255, 0, 60))

        # Cache de vignette por tamanio
        self._vignette_cache = {}

    # =====================================================================
    # MAIN DRAW
    # =====================================================================

    def draw(self, surface: pygame.Surface, level: Level,
             game_state: str, death_reason: str, delta_time: float,
             dialogue_box=None, level_index: int = 0):
        self._time += delta_time
        surface.fill((0, 0, 0))

        # Capas del mapa
        self._draw_layer_tiles(surface, level.walls)
        self._draw_layer_tiles(surface, level.paths)
        self._draw_bridges(surface, level)
        self._draw_buttons(surface, level)
        self._draw_door(surface, level)

        # Tinte dimensional
        self._apply_dimension_tint(surface, level)

        # Entidades
        self._draw_barrels(surface, level)
        self._draw_npcs(surface, level)
        self._draw_player(surface, level)

        # Particulas
        self._process_particle_events(level)
        self.particle_manager.update(delta_time)
        self.particle_manager.draw(surface)

        # Post-proceso: vignette
        self._draw_vignette(surface)

        # HUD
        self._draw_hud(surface, level, level_index)

        # Indicador interaccion
        self._draw_interact_hint(surface, level)

        # Alerta
        level.update_alert(delta_time)
        if level.alert_message:
            self._draw_alert(surface, level.alert_message, level.alert_timer)

        # Dialogo
        if game_state == DIALOGUE and dialogue_box:
            self._draw_dialogue(surface, dialogue_box)

        # Overlays
        if game_state == GAME_COMPLETED:
            self._draw_game_completed(surface)
        elif game_state not in ("running", DIALOGUE):
            self._draw_overlay(surface, game_state, death_reason, level_index)

        pygame.display.flip()

    # =====================================================================
    # MAP LAYERS
    # =====================================================================

    def _draw_layer_tiles(self, surface: pygame.Surface, tiles: list):
        for x, y, tile_surf in tiles:
            surface.blit(tile_surf, (x * TILE_SIZE, y * TILE_SIZE))

    def _draw_bridges(self, surface: pygame.Surface, level: Level):
        for dim_key, bridge in level.bridges.items():
            if dim_key == level.dim:
                for x, y, tile_surf in bridge["tiles"]:
                    surface.blit(tile_surf, (x * TILE_SIZE, y * TILE_SIZE))

    def _draw_buttons(self, surface: pygame.Surface, level: Level):
        for btn in level.buttons:
            x, y = btn["pos"]
            surface.blit(btn["surface"], (x * TILE_SIZE, y * TILE_SIZE))
            if btn.get("pressed", False):
                surface.blit(self._btn_pressed_overlay, (x * TILE_SIZE, y * TILE_SIZE))

    def _draw_door(self, surface: pygame.Surface, level: Level):
        if level.door_pos is None:
            return
        dx, dy = level.door_pos
        cx = dx * TILE_SIZE + TILE_SIZE // 2
        cy = dy * TILE_SIZE + TILE_SIZE // 2
        t = self._time

        if level.door_open:
            # Portal abierto: anillo giratorio verde con glow
            for i in range(3):
                angle_off = t * (1.5 + i * 0.3) + i * 2.09
                r = TILE_SIZE // 2 - 4 + i * 2
                alpha = 140 - i * 35
                s = pygame.Surface((TILE_SIZE + 8, TILE_SIZE + 8), pygame.SRCALPHA)
                scx, scy = s.get_width() // 2, s.get_height() // 2
                points = []
                for j in range(6):
                    a = angle_off + j * (math.pi * 2 / 6)
                    px = scx + int(r * math.cos(a))
                    py = scy + int(r * math.sin(a))
                    points.append((px, py))
                pygame.draw.polygon(s, (40, 255, 100, alpha), points, 2)
                surface.blit(s, (cx - s.get_width() // 2, cy - s.get_height() // 2))

            # Centro con brillo
            glow_r = int(12 + 4 * math.sin(t * 4))
            glow_s = pygame.Surface((glow_r * 4, glow_r * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_s, (40, 255, 100, 60), (glow_r * 2, glow_r * 2), glow_r * 2)
            pygame.draw.circle(glow_s, (150, 255, 180, 100), (glow_r * 2, glow_r * 2), glow_r)
            surface.blit(glow_s, (cx - glow_r * 2, cy - glow_r * 2))
        else:
            # Portal cerrado: X roja pulsante
            rect = pygame.Rect(dx * TILE_SIZE + 4, dy * TILE_SIZE + 4,
                                TILE_SIZE - 8, TILE_SIZE - 8)
            pulse = int(160 + 40 * math.sin(t * 2))
            pygame.draw.rect(surface, (pulse, 25, 25), rect, border_radius=4)
            pygame.draw.rect(surface, (100, 15, 15), rect, 2, border_radius=4)
            # Icono candado
            lock_s = self.f_hud_key.render("X", True, (60, 10, 10))
            surface.blit(lock_s, lock_s.get_rect(center=(cx, cy)))

    def _draw_barrels(self, surface: pygame.Surface, level: Level):
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
        for npc in level.npcs:
            x = npc["col"] * TILE_SIZE
            y = npc["row"] * TILE_SIZE
            if npc["type"] == "jeffry":
                surface.blit(self.jeffry_sprite, (x, y))

            # Nombre con fondo pill
            name = "Jeffrey" if npc["type"] == "jeffry" else npc["type"].capitalize()
            name_surf = self.f_npc_name.render(name, True, _UI_WHITE)
            nw, nh = name_surf.get_size()
            pill_w, pill_h = nw + 10, nh + 4
            pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
            pygame.draw.rect(pill, (0, 0, 0, 160), pill.get_rect(), border_radius=6)
            pill.blit(name_surf, (5, 2))
            pill_x = x + TILE_SIZE // 2 - pill_w // 2
            pill_y = y - pill_h - 3
            # Animacion flotante
            pill_y += int(2 * math.sin(self._time * 2.5))
            surface.blit(pill, (pill_x, pill_y))

    def _draw_interact_hint(self, surface: pygame.Surface, level: Level):
        npc = level.try_interact()
        if npc and not npc.get("talked", False):
            px = level.player.col * TILE_SIZE + TILE_SIZE // 2
            py = level.player.row * TILE_SIZE

            # Pill animada
            bounce = int(3 * math.sin(self._time * 4))
            label = self.f_interact.render("E", True, _UI_DARK)
            text = self.f_hud_label.render("HABLAR", True, _UI_CYAN)

            total_w = label.get_width() + 8 + text.get_width() + 16
            total_h = 22
            pill = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
            # Key badge
            key_rect = pygame.Rect(4, 3, label.get_width() + 8, total_h - 6)
            pygame.draw.rect(pill, (0, 210, 220, 220), key_rect, border_radius=4)
            pill.blit(label, (8, 4))
            pill.blit(text, (key_rect.right + 6, 4))

            bg_pill = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
            pygame.draw.rect(bg_pill, (0, 0, 0, 180), bg_pill.get_rect(), border_radius=6)
            surface.blit(bg_pill, (px - total_w // 2, py - total_h - 6 + bounce))
            surface.blit(pill, (px - total_w // 2, py - total_h - 6 + bounce))

    def _apply_dimension_tint(self, surface: pygame.Surface, level: Level):
        tint = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        if level.dim == "A":
            tint.fill((255, 200, 100, 20))
        else:
            tint.fill((60, 100, 255, 28))
        surface.blit(tint, (0, 0))

        if level.dim == "B" and level.water_positions:
            self._draw_blood_water(surface, level)

    def _draw_blood_water(self, surface: pygame.Surface, level: Level):
        pulse = int(80 + 25 * math.sin(self._time * 2.5))
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

    # =====================================================================
    # POST-PROCESO
    # =====================================================================

    def _draw_vignette(self, surface: pygame.Surface):
        size = surface.get_size()
        if size not in self._vignette_cache:
            w, h = size
            vig = pygame.Surface((w, h), pygame.SRCALPHA)
            cx, cy = w // 2, h // 2
            max_dist = math.hypot(cx, cy)
            for ring in range(0, int(max_dist), 6):
                t = ring / max_dist
                alpha = int(t * t * 90)
                if alpha > 0:
                    pygame.draw.circle(vig, (0, 0, 0, min(alpha, 255)),
                                       (cx, cy), int(max_dist - ring), 6)
            self._vignette_cache[size] = vig
        surface.blit(self._vignette_cache[size], (0, 0))

    # =====================================================================
    # HUD PROFESIONAL
    # =====================================================================

    def _draw_hud(self, surface: pygame.Surface, level: Level, level_index: int):
        w = surface.get_width()
        pal = PALETTE[level.dim]
        accent = _UI_ACCENT_A if level.dim == "A" else _UI_ACCENT_B

        # Barra superior con gradiente
        bar_h = 36
        bar = pygame.Surface((w, bar_h), pygame.SRCALPHA)
        for y in range(bar_h):
            a = int(200 * (1 - y / bar_h))
            pygame.draw.line(bar, (4, 4, 10, a), (0, y), (w, y))
        surface.blit(bar, (0, 0))

        # Separador inferior
        sep = pygame.Surface((w, 1), pygame.SRCALPHA)
        sep.fill((*accent, 80))
        surface.blit(sep, (0, bar_h))

        # Dimension badge (izquierda)
        dim_label = f"DIM {level.dim}"
        badge_surf = self.f_hud_title.render(dim_label, True, accent)
        bw, bh = badge_surf.get_size()
        badge_bg = pygame.Surface((bw + 16, bh + 6), pygame.SRCALPHA)
        pygame.draw.rect(badge_bg, (*accent, 35), badge_bg.get_rect(), border_radius=4)
        pygame.draw.rect(badge_bg, (*accent, 120), badge_bg.get_rect(), 1, border_radius=4)
        badge_bg.blit(badge_surf, (8, 3))
        surface.blit(badge_bg, (8, 6))

        # Nivel (centro-izquierda)
        lvl_text = f"NIVEL {level_index + 1}"
        lvl_surf = self.f_hud_info.render(lvl_text, True, _UI_GREY)
        surface.blit(lvl_surf, (bw + 36, 11))

        # Botones: iconos circulares (derecha)
        pressed = sum(1 for b in level.buttons if b.get("pressed", False))
        total = len(level.buttons)
        btn_x = w - 12
        for i in range(total):
            btn_x -= 18
            is_pressed = i < pressed
            color = _UI_GREEN if is_pressed else (60, 60, 70)
            glow = (*_UI_GREEN, 60) if is_pressed else (0, 0, 0, 0)
            pygame.draw.circle(surface, glow, (btn_x, 18), 8)
            pygame.draw.circle(surface, color, (btn_x, 18), 6)
            if is_pressed:
                pygame.draw.circle(surface, (255, 255, 255, 100), (btn_x, 18), 3)
            pygame.draw.circle(surface, (*color, 180), (btn_x, 18), 6, 1)

        # Label botones
        btn_label = self.f_hud_label.render(f"{pressed}/{total}", True, _UI_GREY)
        btn_x -= btn_label.get_width() + 6
        surface.blit(btn_label, (btn_x, 12))

        # Puerta status
        door_x = btn_x - 10
        if level.door_open:
            door_icon = self.f_hud_label.render("PORTAL ABIERTO", True, _UI_GREEN)
        else:
            door_icon = self.f_hud_label.render("PORTAL CERRADO", True, (100, 50, 50))
        door_x -= door_icon.get_width()
        surface.blit(door_icon, (door_x, 12))

        # Keybind hint (esquina inferior izquierda, sutil)
        hint = self.f_hud_label.render("ESPACIO: cambiar dim  |  R: reiniciar  |  ESC: menu", True, (40, 40, 50))
        surface.blit(hint, (6, surface.get_height() - 16))

    # =====================================================================
    # DIALOGO (estilo visual novel)
    # =====================================================================

    def _draw_dialogue(self, surface: pygame.Surface, dialogue_box):
        w = surface.get_width()
        h = surface.get_height()

        # Oscurecer ligeramente el fondo
        dim = pygame.Surface((w, h), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 80))
        surface.blit(dim, (0, 0))

        # Caja de dialogo
        margin = 12
        box_h = 110
        box_y = h - box_h - margin
        box_w = w - margin * 2
        box_rect = pygame.Rect(margin, box_y, box_w, box_h)

        # Fondo con gradiente sutil
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        for y in range(box_h):
            a = int(220 - y * 0.3)
            pygame.draw.line(box_surf, (8, 10, 20, a), (0, y), (box_w, y))
        surface.blit(box_surf, box_rect.topleft)

        # Bordes
        pygame.draw.rect(surface, (0, 0, 0, 200), box_rect, 1, border_radius=6)
        # Linea accent superior
        accent_line = pygame.Surface((box_w - 2, 2), pygame.SRCALPHA)
        accent_line.fill((*_UI_CYAN, 180))
        surface.blit(accent_line, (margin + 1, box_y))

        # Nombre con badge
        speaker = dialogue_box.current_speaker
        is_jeffrey = speaker == "Jeffrey"
        name_color = _UI_GOLD if is_jeffrey else _UI_CYAN
        name_bg_color = (40, 35, 10) if is_jeffrey else (10, 30, 35)

        name_surf = self.f_dlg_name.render(speaker, True, name_color)
        nw, nh = name_surf.get_size()
        name_pill = pygame.Surface((nw + 20, nh + 8), pygame.SRCALPHA)
        pygame.draw.rect(name_pill, (*name_bg_color, 230), name_pill.get_rect(), border_radius=4)
        pygame.draw.rect(name_pill, (*name_color, 120), name_pill.get_rect(), 1, border_radius=4)
        name_pill.blit(name_surf, (10, 4))
        surface.blit(name_pill, (margin + 12, box_y - (nh + 8) // 2))

        # Texto con word wrap
        text = dialogue_box.current_text
        max_text_w = box_w - 40
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test = current_line + (" " if current_line else "") + word
            if self.f_dlg_text.size(test)[0] <= max_text_w:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines):
            line_surf = self.f_dlg_text.render(line, True, (210, 212, 220))
            surface.blit(line_surf, (margin + 20, box_y + 22 + i * 22))

        # Indicador de avance pulsante
        tri_x = margin + box_w - 24
        tri_y = box_y + box_h - 20 + int(3 * math.sin(self._time * 5))
        pulse_a = int(150 + 80 * math.sin(self._time * 4))
        tri_s = pygame.Surface((12, 10), pygame.SRCALPHA)
        pygame.draw.polygon(tri_s, (*_UI_CYAN, pulse_a),
                            [(0, 0), (12, 0), (6, 8)])
        surface.blit(tri_s, (tri_x, tri_y))

    # =====================================================================
    # ALERTA
    # =====================================================================

    def _draw_alert(self, surface: pygame.Surface, message: str, timer: float):
        w = surface.get_width()
        h = surface.get_height()
        alpha = min(255, int(timer * 300))

        alert_w = min(w - 40, self.f_alert.size(message)[0] + 40)
        alert_h = 32
        ax = w // 2 - alert_w // 2
        ay = h - 52

        bg = pygame.Surface((alert_w, alert_h), pygame.SRCALPHA)
        pygame.draw.rect(bg, (140, 20, 20, min(alpha, 200)), bg.get_rect(), border_radius=6)
        pygame.draw.rect(bg, (200, 40, 40, min(alpha, 150)), bg.get_rect(), 1, border_radius=6)
        surface.blit(bg, (ax, ay))

        # Icono warning
        icon = self.f_hud_key.render("!", True, (255, 200, 200))
        icon.set_alpha(alpha)
        surface.blit(icon, (ax + 10, ay + 8))

        text = self.f_alert.render(message, True, (255, 220, 220))
        text.set_alpha(alpha)
        surface.blit(text, text.get_rect(midleft=(ax + 24, ay + alert_h // 2)))

    # =====================================================================
    # OVERLAY NIVEL COMPLETADO / MUERTE
    # =====================================================================

    def _draw_overlay(self, surface: pygame.Surface, game_state: str,
                      death_reason: str, level_index: int = 0):
        w = surface.get_width()
        h = surface.get_height()

        # Fondo oscuro animado
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        cx = w // 2
        cy = h // 2

        if game_state == WON:
            # Lineas decorativas
            line_a = int(100 + 40 * math.sin(self._time * 2))
            line_w = int(180 + 40 * math.sin(self._time * 1.5))
            line_s = pygame.Surface((line_w, 1), pygame.SRCALPHA)
            line_s.fill((*_UI_GREEN, line_a))
            surface.blit(line_s, (cx - line_w // 2, cy - 65))
            surface.blit(line_s, (cx - line_w // 2, cy + 62))

            # Titulo
            _draw_text_shadow(surface, self.f_overlay_title, "NIVEL COMPLETADO",
                              self.f_overlay_title.render("NIVEL COMPLETADO", True, _UI_GREEN)
                              .get_rect(center=(cx, cy - 38)).topleft, _UI_GREEN)

            # Subtitulo
            sub = f"Has completado el nivel {level_index + 1}"
            sub_surf = self.f_overlay_sub.render(sub, True, (180, 200, 180))
            surface.blit(sub_surf, sub_surf.get_rect(center=(cx, cy + 8)))

            # Controles con key badges
            self._draw_key_hint(surface, cx, cy + 48,
                                [("ENTER", "Siguiente"), ("R", "Repetir"), ("ESC", "Menu")])
        else:
            # Muerte
            _draw_text_shadow(surface, self.f_overlay_title, "HAS MUERTO",
                              self.f_overlay_title.render("HAS MUERTO", True, _UI_RED)
                              .get_rect(center=(cx, cy - 38)).topleft, _UI_RED)

            if death_reason:
                sub_surf = self.f_overlay_sub.render(death_reason, True, (200, 160, 160))
                surface.blit(sub_surf, sub_surf.get_rect(center=(cx, cy + 8)))

            self._draw_key_hint(surface, cx, cy + 48,
                                [("R", "Reintentar"), ("ESC", "Menu")])

    def _draw_key_hint(self, surface: pygame.Surface, cx: int, y: int,
                       keys: list[tuple[str, str]]):
        """Dibuja hints de teclas con estilo badge."""
        total_w = 0
        items = []
        for key, label in keys:
            key_surf = self.f_hud_key.render(key, True, _UI_DARK)
            label_surf = self.f_overlay_ctrl.render(label, True, _UI_GREY)
            kw = key_surf.get_width() + 10
            item_w = kw + label_surf.get_width() + 8
            items.append((key_surf, label_surf, kw, item_w))
            total_w += item_w + 16

        x = cx - total_w // 2
        for key_surf, label_surf, kw, item_w in items:
            # Key badge
            badge = pygame.Surface((kw, 18), pygame.SRCALPHA)
            pygame.draw.rect(badge, (80, 80, 90, 220), badge.get_rect(), border_radius=3)
            pygame.draw.rect(badge, (120, 120, 130, 150), badge.get_rect(), 1, border_radius=3)
            badge.blit(key_surf, (5, 3))
            surface.blit(badge, (x, y))
            surface.blit(label_surf, (x + kw + 4, y + 2))
            x += item_w + 16

    # =====================================================================
    # PANTALLA FINAL: JUEGO COMPLETADO
    # =====================================================================

    def _draw_game_completed(self, surface: pygame.Surface):
        w = surface.get_width()
        h = surface.get_height()

        # Fondo negro con lineas animadas
        surface.fill((4, 4, 10))

        # Lineas de energia
        for i in range(8):
            lx = int(w * 0.5 + math.cos(self._time * 0.8 + i * 0.8) * w * 0.4)
            ly = int(h * 0.5 + math.sin(self._time * 0.6 + i * 1.1) * h * 0.4)
            la = int(20 + 15 * math.sin(self._time * 2 + i))
            line_s = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.line(line_s, (40, 255, 100, la), (w // 2, h // 2), (lx, ly), 1)
            surface.blit(line_s, (0, 0))

        cx = w // 2
        cy = h // 2

        # Titulo FRACTURE con glow
        pulse = int(200 + 55 * math.sin(self._time * 1.2))
        glow_color = (pulse, 255, pulse)
        # Sombra
        shadow = self.f_completed_title.render("FRACTURE", True, (0, 40, 20))
        surface.blit(shadow, shadow.get_rect(center=(cx + 2, cy - 78)))
        title = self.f_completed_title.render("FRACTURE", True, glow_color)
        surface.blit(title, title.get_rect(center=(cx, cy - 80)))

        # Linea decorativa
        line_w = title.get_width() + 30
        line_s = pygame.Surface((line_w, 2), pygame.SRCALPHA)
        line_s.fill((*_UI_GREEN, int(120 + 40 * math.sin(self._time * 3))))
        surface.blit(line_s, (cx - line_w // 2, cy - 52))

        # Subtitulo
        sub = self.f_completed_sub.render("JUEGO COMPLETADO", True, _UI_GREEN)
        surface.blit(sub, sub.get_rect(center=(cx, cy - 30)))

        # Narrativa final
        lines = [
            "Gracias a tu valentia y la ayuda de Jeffrey,",
            "las dos dimensiones se han estabilizado.",
            "La fractura ha sido sellada para siempre.",
        ]
        for i, line in enumerate(lines):
            a = int(180 + 30 * math.sin(self._time * 1.5 + i * 0.5))
            line_surf = self.f_completed_text.render(line, True, (a, a + 10, a + 20))
            surface.blit(line_surf, line_surf.get_rect(center=(cx, cy + 15 + i * 24)))

        # Separador inferior
        sep_w = 160
        sep_s = pygame.Surface((sep_w, 1), pygame.SRCALPHA)
        sep_s.fill((*_UI_GREY, 60))
        surface.blit(sep_s, (cx - sep_w // 2, cy + 90))

        # Control
        ctrl = self.f_completed_ctrl.render("Pulsa ENTER o ESC para volver al menu", True, (70, 70, 80))
        surface.blit(ctrl, ctrl.get_rect(center=(cx, cy + 108)))

        # Vignette
        self._draw_vignette(surface)
