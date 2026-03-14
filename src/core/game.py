"""
Clase principal del juego.
Gestiona el menu, el gameplay y el autoguardado.
"""
import os
import pygame
import sys
from src.core.config import TILE_SIZE, FPS, RUNNING, WON, MENU, get_levels
from src.core.level import Level
from src.core.menu import Menu
from src.core import save_manager
from src.rendering.renderer import GameRenderer

_AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
))), "assets", "audio")

# Tamanio fijo de la ventana del menu
_MENU_WIDTH = 640
_MENU_HEIGHT = 480


class Game:
    """Clase principal que controla el flujo del juego."""

    MOVEMENT_KEYS = {
        pygame.K_w: (0, -1),    pygame.K_UP:    (0, -1),
        pygame.K_s: (0,  1),    pygame.K_DOWN:  (0,  1),
        pygame.K_a: (-1, 0),    pygame.K_LEFT:  (-1, 0),
        pygame.K_d: (1,  0),    pygame.K_RIGHT: (1,  0),
    }

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("FRACTURE")
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(150, 90)

        # Sonidos
        self.snd_step = pygame.mixer.Sound(os.path.join(_AUDIO_DIR, "step.wav"))
        self.snd_step.set_volume(0.5)
        self.snd_push = pygame.mixer.Sound(os.path.join(_AUDIO_DIR, "push.wav"))
        self.snd_victory = pygame.mixer.Sound(os.path.join(_AUDIO_DIR, "victory.mp3"))
        self.snd_dimension = pygame.mixer.Sound(os.path.join(_AUDIO_DIR, "cambio4.mp3"))

        # Estado
        self.state = MENU
        self.death_reason = ""

        # Menu
        self.menu = Menu(self.screen)

        # Gameplay (se inicializan al empezar partida)
        self.level = None
        self.renderer = None
        self.profile_name = ""
        self.level_index = 0

    def run(self):
        """Bucle principal del juego."""
        while True:
            delta_time = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._render(delta_time)

    def _start_level(self, profile: str, level_index: int):
        """Carga un nivel y redimensiona la ventana."""
        self.profile_name = profile
        levels = get_levels()
        self.level_index = min(level_index, len(levels) - 1)
        tmx_file = levels[self.level_index]

        self.level = Level(tmx_file)
        width = self.level.cols * TILE_SIZE
        height = self.level.rows * TILE_SIZE
        self.screen = pygame.display.set_mode((width, height))

        if self.renderer is None:
            self.renderer = GameRenderer()

        self.state = RUNNING
        self.death_reason = ""

    def _back_to_menu(self):
        """Vuelve al menu principal."""
        self.screen = pygame.display.set_mode((_MENU_WIDTH, _MENU_HEIGHT))
        self.menu = Menu(self.screen)
        self.state = MENU
        self.level = None

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state == MENU:
                self._handle_menu_event(event)
            elif event.type == pygame.KEYDOWN:
                if self.state == RUNNING:
                    if event.key == pygame.K_ESCAPE:
                        self._back_to_menu()
                    elif event.key == pygame.K_r:
                        self.level.reset()
                    else:
                        self._handle_gameplay_input(event.key)
                else:
                    self._handle_endscreen_input(event.key)

    def _handle_menu_event(self, event: pygame.event.Event):
        result = self.menu.handle_event(event)
        if result is None:
            return
        if result["action"] == "quit":
            pygame.quit()
            sys.exit()
        elif result["action"] == "play":
            self._start_level(result["profile"], result["level_index"])

    def _handle_endscreen_input(self, key: int):
        if key == pygame.K_r:
            self.level.reset()
            self.state = RUNNING
        elif key == pygame.K_ESCAPE:
            self._back_to_menu()
        elif key == pygame.K_RETURN and self.state == WON:
            # Siguiente nivel
            next_idx = self.level_index + 1
            if next_idx < len(get_levels()):
                self._start_level(self.profile_name, next_idx)
            else:
                self._back_to_menu()

    def _handle_gameplay_input(self, key: int):
        result = None

        if key == pygame.K_SPACE:
            old_dim = self.level.dim
            self.level.toggle_dimension()
            if self.level.dim != old_dim:
                self.snd_dimension.play()
        elif key in self.MOVEMENT_KEYS:
            dc, dr = self.MOVEMENT_KEYS[key]
            old_col, old_row = self.level.player.col, self.level.player.row
            result, pushed = self.level.try_move(dc, dr)
            if (self.level.player.col, self.level.player.row) != (old_col, old_row):
                self.snd_step.play()
                if pushed:
                    self.snd_push.play()

        if result is not None:
            self.state = result
            if result == WON:
                self.snd_victory.play()
                save_manager.save_progress(self.profile_name, self.level_index, completed=True)

    def _render(self, delta_time: float):
        if self.state == MENU:
            self.menu.draw()
        else:
            self.renderer.draw(self.screen, self.level, self.state,
                               self.death_reason, delta_time)
