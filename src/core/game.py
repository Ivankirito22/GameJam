"""
================================================================================
CLASE PRINCIPAL DEL JUEGO
================================================================================
Game es la clase que lo une todo. Se encarga de:
    1. Crear la ventana del juego.
    2. Escuchar las teclas que pulsa el jugador.
    3. Pedir al Level que procese la lógica.
    4. Pedir al Renderer que dibuje todo en pantalla.

CONSEJO PARA JUNIORS:
    - El "bucle principal" (game loop) es un while True que se repite 60 veces/seg.
    - Cada iteración: lee teclas → actualiza lógica → dibuja → repite.
    - "delta_time" mide cuánto tiempo pasó entre frames (para animaciones suaves).
"""
import pygame
import sys
from src.core.config import WIDTH, HEIGHT, FPS, RUNNING, DEAD, WON, ROWS
from src.core.level import Level
from src.rendering.renderer import GameRenderer


class Game:
    """Clase principal que controla el flujo del juego."""

    # Mapeo de teclas a direcciones de movimiento (columna, fila)
    # Ejemplo: W o flecha arriba = mover 0 columnas, -1 fila (hacia arriba)
    MOVEMENT_KEYS = {
        pygame.K_w: (0, -1),    pygame.K_UP:    (0, -1),   # Arriba
        pygame.K_s: (0,  1),    pygame.K_DOWN:  (0,  1),   # Abajo
        pygame.K_a: (-1, 0),    pygame.K_LEFT:  (-1, 0),   # Izquierda
        pygame.K_d: (1,  0),    pygame.K_RIGHT: (1,  0),   # Derecha
    }

    def __init__(self):
        """Inicializa Pygame, la ventana, el nivel y el renderizador."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dimension Puzzle")
        self.clock = pygame.time.Clock()

        # Configurar repetición de teclas (150ms delay, 90ms intervalo)
        # Esto permite mantener pulsada una tecla para moverse continuamente
        pygame.key.set_repeat(150, 90)

        # Crear el nivel (lógica) y el renderizador (gráficos)
        self.level = Level()
        self.renderer = GameRenderer()

        # Estado del juego
        self.state = RUNNING
        self.death_reason = ""

    def run(self):
        """
        Inicia el bucle principal del juego.
        Se ejecuta hasta que el jugador cierra la ventana.
        """
        while True:
            # Calcular delta_time (tiempo entre frames en segundos)
            # Esto es necesario para que las partículas se muevan a velocidad constante
            delta_time = self.clock.tick(FPS) / 1000.0

            self._handle_events()
            self._render(delta_time)

    def _handle_events(self):
        """
        Procesa todos los eventos de entrada del jugador.
        Eventos = teclas pulsadas, cierre de ventana, etc.
        """
        for event in pygame.event.get():
            # Cerrar el juego con la X de la ventana o con ESC
            if (event.type == pygame.QUIT or
                    (event.type == pygame.KEYDOWN and
                     event.key == pygame.K_ESCAPE)):
                pygame.quit()
                sys.exit()

            # Solo nos interesan las teclas pulsadas
            if event.type != pygame.KEYDOWN:
                continue

            if self.state == RUNNING:
                self._handle_gameplay_input(event.key)
            else:
                # Si estamos muertos o hemos ganado, solo R para reiniciar
                if event.key == pygame.K_r:
                    self.level.reset()
                    self.state = RUNNING

    def _handle_gameplay_input(self, key: int):
        """
        Procesa una tecla durante el gameplay activo.

        Args:
            key: El código de la tecla pulsada.
        """
        result = None

        if key == pygame.K_SPACE:
            # Cambiar de dimensión
            self.level.toggle_dimension()
        elif key == pygame.K_e:
            # Intentar empujar un barril
            result = self.level.try_interact()
        elif key in self.MOVEMENT_KEYS:
            # Intentar moverse
            dc, dr = self.MOVEMENT_KEYS[key]
            result = self.level.try_move(dc, dr)

        # ¿El resultado indica victoria o derrota?
        if result is not None:
            self.state = result
            self._determine_death_reason()

    def _determine_death_reason(self):
        """Determina el texto que se muestra al morir."""
        if self.state != DEAD:
            return

        pc = self.level.player.col
        pr = self.level.player.row

        if self.level._is_water(pc, pr):
            self.death_reason = "Has caido al agua."
        elif pr == ROWS - 1 and self.level.dim == "B":
            self.death_reason = "Cruzar la puerta en la dimension opuesta es mortal."
        else:
            self.death_reason = "Has muerto."

    def _render(self, delta_time: float):
        """
        Pide al renderizador que dibuje todo en pantalla.

        Args:
            delta_time: Tiempo desde el último frame (segundos).
        """
        self.renderer.draw(self.screen, self.level, self.state,
                           self.death_reason, delta_time)
