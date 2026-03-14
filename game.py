"""
================================================================================
CLASE PRINCIPAL DEL JUEGO
================================================================================
Game gestiona el bucle principal, la ventana, los eventos de entrada y
coordina la lógica del nivel con el renderizado.
"""
import pygame
import sys
from config import WIDTH, HEIGHT, FPS, RUNNING, DEAD, WON, ROWS
from level import Level
from rendering import GameRenderer

class Game:
    """Clase principal que controla el flujo del juego."""
    
    _DIRS = {
        pygame.K_w: ( 0, -1), pygame.K_UP:    ( 0, -1),
        pygame.K_s: ( 0,  1), pygame.K_DOWN:  ( 0,  1),
        pygame.K_a: (-1,  0), pygame.K_LEFT:  (-1,  0),
        pygame.K_d: ( 1,  0), pygame.K_RIGHT: ( 1,  0),
    }
    
    def __init__(self):
        """Inicializa el juego y Pygame."""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Dimension Puzzle")
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(150, 90)
        
        self.level = Level()
        self.renderer = GameRenderer()
        
        self.state = RUNNING
        self.death_reason = ""
    
    def run(self):
        """Inicia el bucle principal del juego."""
        while True:
            self._handle_events()
            self._render()
            self.clock.tick(FPS)
    
    def _handle_events(self):
        """Procesa los eventos de entrada del jugador."""
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            if ev.type != pygame.KEYDOWN:
                continue
            
            if self.state == RUNNING:
                result = None
                if ev.key == pygame.K_SPACE:
                    self.level.toggle_dimension()
                elif ev.key == pygame.K_e:
                    result = self.level.try_interact()
                elif ev.key in self._DIRS:
                    result = self.level.try_move(*self._DIRS[ev.key])
                
                if result:
                    self.state = result
                    self._set_death_reason()
            else:
                if ev.key == pygame.K_r:
                    self.level.reset()
                    self.state = RUNNING
    
    def _set_death_reason(self):
        """Determina la razón de la muerte para mostrar en pantalla."""
        if self.state != DEAD:
            return
        
        pc, pr = self.level.player.col, self.level.player.row
        
        if self.level._is_water(pc, pr):
            self.death_reason = "Has caido al agua."
        elif pr == ROWS - 1 and self.level.dim == "B":
            self.death_reason = "Cruzar la puerta en la dimension opuesta es mortal."
        else:
            self.death_reason = "Has muerto."
    
    def _render(self):
        """Renderiza un frame del juego."""
        self.renderer.draw(self.screen, self.level, self.state, self.death_reason)