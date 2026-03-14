"""
Menu principal - FRACTURE
Estetica cinematografica oscura con efectos atmosfericos.
"""
import math
import random
import pygame
from src.core.config import get_levels
from src.core import save_manager

# --- Paleta ---
_BLACK = (4, 4, 8)
_BG_GRAD_TOP = (6, 6, 14)
_BG_GRAD_BOT = (10, 8, 18)
_CYAN = (0, 206, 209)
_CYAN_DIM = (0, 120, 130)
_CYAN_GLOW = (0, 255, 255)
_WHITE = (220, 220, 225)
_GREY = (90, 90, 100)
_DARK_GREY = (45, 45, 55)
_SELECTED_BG = (12, 30, 35)
_SELECTED_BORDER = (0, 180, 190)
_IDLE_BORDER = (35, 35, 45)
_INPUT_BG = (10, 10, 18)
_RED_SOFT = (180, 40, 40)


class _Particle:
    """Particula de polvo atmosferico."""
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "alpha")

    def __init__(self, w: int, h: int):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-12, -3)
        self.max_life = random.uniform(4, 10)
        self.life = random.uniform(0, self.max_life)
        self.size = random.choice([1, 1, 1, 2])
        self.alpha = 0

    def update(self, dt: float, w: int, h: int):
        self.life -= dt
        if self.life <= 0:
            self.__init__(w, h)
            self.life = self.max_life
            self.y = h + 5
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Fade in/out
        ratio = self.life / self.max_life
        self.alpha = int(50 * math.sin(ratio * math.pi))
        if self.x < 0:
            self.x = w
        elif self.x > w:
            self.x = 0


class Menu:
    """Menu principal del juego."""

    GAME_TITLE = "FRACTURE"

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.time = 0.0

        # Fonts
        self.f_title = pygame.font.SysFont("Consolas", 64, bold=True)
        self.f_tagline = pygame.font.SysFont("Consolas", 13)
        self.f_option = pygame.font.SysFont("Segoe UI", 20)
        self.f_hint = pygame.font.SysFont("Segoe UI", 12)
        self.f_input = pygame.font.SysFont("Consolas", 20)
        self.f_section = pygame.font.SysFont("Consolas", 32, bold=True)
        self.f_profile_name = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.f_profile_info = pygame.font.SysFont("Segoe UI", 13)

        # State
        self.state = "main"
        self.selected = 0
        self.input_text = ""
        self.main_options = ["NUEVA PARTIDA", "CONTINUAR", "SALIR"]
        self.profiles = []
        self._refresh_profiles()

        # Particles
        w, h = screen.get_size()
        self._particles = [_Particle(w, h) for _ in range(45)]

        # Cached surfaces
        self._bg = self._make_bg(w, h)
        self._vignette = self._make_vignette(w, h)
        self._scanlines = self._make_scanlines(w, h)

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_bg(w: int, h: int) -> pygame.Surface:
        bg = pygame.Surface((w, h))
        for y in range(h):
            t = y / max(h - 1, 1)
            r = int(_BG_GRAD_TOP[0] + (_BG_GRAD_BOT[0] - _BG_GRAD_TOP[0]) * t)
            g = int(_BG_GRAD_TOP[1] + (_BG_GRAD_BOT[1] - _BG_GRAD_TOP[1]) * t)
            b = int(_BG_GRAD_TOP[2] + (_BG_GRAD_BOT[2] - _BG_GRAD_TOP[2]) * t)
            pygame.draw.line(bg, (r, g, b), (0, y), (w, y))
        return bg

    @staticmethod
    def _make_vignette(w: int, h: int) -> pygame.Surface:
        vig = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2
        max_dist = math.hypot(cx, cy)
        for ring in range(0, int(max_dist), 4):
            t = ring / max_dist
            alpha = int(t * t * 120)
            if alpha > 0:
                pygame.draw.circle(vig, (0, 0, 0, min(alpha, 255)), (cx, cy),
                                   int(max_dist - ring), 4)
        return vig

    @staticmethod
    def _make_scanlines(w: int, h: int) -> pygame.Surface:
        sl = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, 3):
            pygame.draw.line(sl, (0, 0, 0, 18), (0, y), (w, y))
        return sl

    def _refresh_profiles(self):
        self.profiles = save_manager.get_profiles()

    # ------------------------------------------------------------------
    # Drawing primitives
    # ------------------------------------------------------------------

    def _draw_particles(self, dt: float):
        w, h = self.screen.get_size()
        for p in self._particles:
            p.update(dt, w, h)
            if p.alpha > 0:
                c = (*_CYAN_DIM, p.alpha)
                s = pygame.Surface((p.size * 2, p.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, c, (p.size, p.size), p.size)
                self.screen.blit(s, (int(p.x), int(p.y)))

    def _draw_separator(self, y: int, w: int):
        """Linea horizontal fina con fade lateral."""
        line = pygame.Surface((w, 1), pygame.SRCALPHA)
        hw = w // 2
        for x in range(w):
            dist = abs(x - hw) / hw
            a = int(40 * (1 - dist * dist))
            line.set_at((x, 0), (*_CYAN_DIM, max(a, 0)))
        self.screen.blit(line, (0, y))

    def _draw_option(self, text: str, cx: int, y: int, w: int, h: int,
                     selected: bool, danger: bool = False):
        """Dibuja una opcion de menu minimalista."""
        rect = pygame.Rect(cx - w // 2, y, w, h)

        if selected:
            # Fondo sutil
            bg = pygame.Surface((w, h), pygame.SRCALPHA)
            bg.fill((*_SELECTED_BG[0:3], 200))
            self.screen.blit(bg, rect.topleft)
            # Borde izquierdo accent
            pygame.draw.line(self.screen, _CYAN, (rect.left, rect.top),
                             (rect.left, rect.bottom - 1), 2)
            # Borde fino
            pygame.draw.rect(self.screen, _SELECTED_BORDER, rect, 1)
            color = _CYAN_GLOW if not danger else _RED_SOFT
        else:
            pygame.draw.rect(self.screen, _IDLE_BORDER, rect, 1)
            color = _GREY

        txt = self.f_option.render(text, True, color)
        self.screen.blit(txt, txt.get_rect(midleft=(rect.left + 20, rect.centery)))

    # ------------------------------------------------------------------
    # Title
    # ------------------------------------------------------------------

    def _draw_title(self, w: int, base_y: int):
        # Glitch offset
        glitch_x = 0
        glitch_phase = math.sin(self.time * 0.7) * math.sin(self.time * 3.1)
        if abs(glitch_phase) > 0.92:
            glitch_x = random.choice([-3, -2, 2, 3])

        # Shadow / echo (cyan desplazado)
        shadow = self.f_title.render(self.GAME_TITLE, True, (0, 60, 65))
        self.screen.blit(shadow, shadow.get_rect(center=(w // 2 + 3 + glitch_x, base_y + 2)))

        # Titulo principal
        glow = int(210 + 30 * math.sin(self.time * 1.8))
        title_color = (glow, glow, glow)
        title = self.f_title.render(self.GAME_TITLE, True, title_color)
        self.screen.blit(title, title.get_rect(center=(w // 2 + glitch_x, base_y)))

        # Accent line bajo el titulo
        lw = title.get_width() + 40
        lx = w // 2 - lw // 2
        pulse = int(140 + 60 * math.sin(self.time * 2.5))
        pygame.draw.line(self.screen, (*_CYAN[0:2], min(pulse, 255)),
                         (lx, base_y + 38), (lx + lw, base_y + 38), 1)

        # Tagline
        tag = self.f_tagline.render("SHIFT BETWEEN REALITIES", True, _DARK_GREY)
        self.screen.blit(tag, tag.get_rect(center=(w // 2, base_y + 54)))

    # ------------------------------------------------------------------
    # Event handling (sin cambios logicos)
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> dict | None:
        if event.type != pygame.KEYDOWN:
            return None
        if self.state == "main":
            return self._handle_main(event.key)
        elif self.state == "profiles":
            return self._handle_profiles(event.key)
        elif self.state == "new_profile":
            return self._handle_new_profile(event)
        return None

    def _handle_main(self, key: int) -> dict | None:
        if key in (pygame.K_w, pygame.K_UP):
            self.selected = (self.selected - 1) % len(self.main_options)
        elif key in (pygame.K_s, pygame.K_DOWN):
            self.selected = (self.selected + 1) % len(self.main_options)
        elif key in (pygame.K_RETURN, pygame.K_e):
            option = self.main_options[self.selected]
            if option == "NUEVA PARTIDA":
                self.state = "new_profile"
                self.input_text = ""
            elif option == "CONTINUAR":
                self._refresh_profiles()
                if self.profiles:
                    self.state = "profiles"
                    self.selected = 0
            elif option == "SALIR":
                return {"action": "quit"}
        return None

    def _handle_profiles(self, key: int) -> dict | None:
        total = len(self.profiles) + 1
        if key in (pygame.K_w, pygame.K_UP):
            self.selected = (self.selected - 1) % total
        elif key in (pygame.K_s, pygame.K_DOWN):
            self.selected = (self.selected + 1) % total
        elif key == pygame.K_DELETE and self.selected < len(self.profiles):
            name = self.profiles[self.selected]
            save_manager.delete_profile(name)
            self._refresh_profiles()
            if self.selected >= len(self.profiles):
                self.selected = max(0, len(self.profiles) - 1)
        elif key in (pygame.K_RETURN, pygame.K_e):
            if self.selected >= len(self.profiles):
                self.state = "main"
                self.selected = 1
            else:
                name = self.profiles[self.selected]
                profile = save_manager.get_profile(name)
                level_idx = profile["current_level"]
                if level_idx >= len(get_levels()):
                    level_idx = len(get_levels()) - 1
                return {"action": "play", "profile": name, "level_index": level_idx}
        elif key == pygame.K_ESCAPE:
            self.state = "main"
            self.selected = 1
        return None

    def _handle_new_profile(self, event: pygame.event.Event) -> dict | None:
        key = event.key
        if key == pygame.K_ESCAPE:
            self.state = "main"
            self.selected = 0
        elif key == pygame.K_RETURN:
            name = self.input_text.strip()
            if name:
                save_manager.create_profile(name)
                return {"action": "play", "profile": name, "level_index": 0}
        elif key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        else:
            if event.unicode and event.unicode.isprintable() and len(self.input_text) < 16:
                self.input_text += event.unicode
        return None

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self):
        dt = 1 / 60.0
        self.time += dt
        w, h = self.screen.get_size()

        # Base
        self.screen.blit(self._bg, (0, 0))
        self._draw_particles(dt)

        if self.state == "main":
            self._draw_main(w, h)
        elif self.state == "profiles":
            self._draw_profiles(w, h)
        elif self.state == "new_profile":
            self._draw_new_profile(w, h)

        # Post-processing
        self.screen.blit(self._vignette, (0, 0))
        self.screen.blit(self._scanlines, (0, 0))

        # Footer
        ver = self.f_hint.render("FRACTURE v0.1  //  GameJam 2026", True, (30, 30, 38))
        self.screen.blit(ver, (w - ver.get_width() - 10, h - 18))

        pygame.display.flip()

    # ------------------------------------------------------------------
    # Screens
    # ------------------------------------------------------------------

    def _draw_main(self, w: int, h: int):
        self._draw_title(w, h * 0.22)

        btn_w = 260
        btn_h = 40
        start_y = int(h * 0.48)
        gap = 52

        for i, opt in enumerate(self.main_options):
            self._draw_option(opt, w // 2, start_y + i * gap, btn_w, btn_h,
                              i == self.selected, danger=(opt == "SALIR"))

        self._draw_separator(h - 55, w)
        hint = self.f_hint.render("[W/S]  navegar     [ENTER]  seleccionar", True, _DARK_GREY)
        self.screen.blit(hint, hint.get_rect(center=(w // 2, h - 35)))

    def _draw_profiles(self, w: int, h: int):
        title = self.f_section.render("PERFILES", True, _WHITE)
        self.screen.blit(title, title.get_rect(center=(w // 2, 50)))
        self._draw_separator(75, w)

        btn_w = 380
        card_h = 56
        start_y = 100
        gap = 64

        for i, name in enumerate(self.profiles):
            profile = save_manager.get_profile(name)
            completed = len(profile["completed_levels"])
            total = len(get_levels())
            sel = (i == self.selected)

            rect = pygame.Rect(w // 2 - btn_w // 2, start_y + i * gap, btn_w, card_h)
            bg_color = _SELECTED_BG if sel else _BLACK
            border_color = _SELECTED_BORDER if sel else _IDLE_BORDER

            bg = pygame.Surface((btn_w, card_h), pygame.SRCALPHA)
            bg.fill((*bg_color, 200))
            self.screen.blit(bg, rect.topleft)
            pygame.draw.rect(self.screen, border_color, rect, 1)
            if sel:
                pygame.draw.line(self.screen, _CYAN, (rect.left, rect.top),
                                 (rect.left, rect.bottom - 1), 2)

            # Nombre
            nc = _CYAN_GLOW if sel else _WHITE
            ns = self.f_profile_name.render(name.upper(), True, nc)
            self.screen.blit(ns, (rect.left + 18, rect.top + 8))

            # Info
            progress = f"Nivel {profile['current_level'] + 1}/{total}"
            ic = _CYAN_DIM if sel else _DARK_GREY
            info_s = self.f_profile_info.render(
                f"{progress}   {completed} completados", True, ic)
            self.screen.blit(info_s, (rect.left + 18, rect.top + 32))

            # Progress bar
            bar_w = 80
            bar_h = 4
            bar_x = rect.right - bar_w - 15
            bar_y = rect.centery - 2
            pygame.draw.rect(self.screen, _IDLE_BORDER,
                             (bar_x, bar_y, bar_w, bar_h), border_radius=2)
            fill = int(bar_w * (completed / max(total, 1)))
            if fill > 0:
                pygame.draw.rect(self.screen, _CYAN,
                                 (bar_x, bar_y, fill, bar_h), border_radius=2)

        # Volver
        back_idx = len(self.profiles)
        self._draw_option("VOLVER", w // 2, start_y + back_idx * gap,
                          btn_w, 40, self.selected == back_idx)

        self._draw_separator(h - 50, w)
        hint = self.f_hint.render(
            "[ENTER] jugar   [DEL] borrar   [ESC] volver", True, _DARK_GREY)
        self.screen.blit(hint, hint.get_rect(center=(w // 2, h - 30)))

    def _draw_new_profile(self, w: int, h: int):
        title = self.f_section.render("NUEVA PARTIDA", True, _WHITE)
        self.screen.blit(title, title.get_rect(center=(w // 2, h * 0.25)))
        self._draw_separator(int(h * 0.25) + 25, w)

        label = self.f_option.render("Identificador:", True, _GREY)
        self.screen.blit(label, label.get_rect(center=(w // 2, h // 2 - 35)))

        # Input field
        cursor = "|" if int(self.time * 2.5) % 2 == 0 else ""
        display = self.input_text + cursor
        inp = self.f_input.render(display if display else cursor, True, _WHITE)
        inp_rect = inp.get_rect(center=(w // 2, h // 2 + 5))
        bg_rect = inp_rect.inflate(50, 18)
        pygame.draw.rect(self.screen, _INPUT_BG, bg_rect, border_radius=4)

        # Animated border
        pulse = int(60 + 30 * math.sin(self.time * 3))
        bc = (0, pulse + 60, pulse + 70)
        pygame.draw.rect(self.screen, bc, bg_rect, 1, border_radius=4)
        self.screen.blit(inp, inp_rect)

        # Character count
        count = self.f_hint.render(f"{len(self.input_text)}/16", True, _DARK_GREY)
        self.screen.blit(count, (bg_rect.right - count.get_width() - 5,
                                 bg_rect.bottom + 5))

        self._draw_separator(h - 50, w)
        hint = self.f_hint.render("[ENTER] confirmar     [ESC] cancelar", True, _DARK_GREY)
        self.screen.blit(hint, hint.get_rect(center=(w // 2, h - 30)))
