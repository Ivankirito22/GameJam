"""
================================================================================
SISTEMA DE PARTÍCULAS
================================================================================
Gestiona los efectos visuales de partículas usando la librería "particlepy".
Las partículas son pequeños elementos visuales que aparecen temporalmente
para dar feedback visual al jugador (splash de agua, cambio de dimensión, etc).

CONSEJO PARA JUNIORS:
    - Un "ParticleSystem" es como un contenedor que gestiona muchas partículas.
    - Cada partícula tiene posición, velocidad, tamaño y color.
    - "delta_radius" controla lo rápido que se encoge (y desaparece).
    - "emit" añade una partícula nueva al sistema.
    - Cada frame hay que llamar a update(), make_shape() y render().
"""
import random
import particlepy
from particlepy import particle as pp_particle
from particlepy import shape as pp_shape
from particlepy import math as pp_math

from src.core.config import (
    TILE_SIZE,
    PARTICLE_WATER_COLOR, PARTICLE_WATER_FADE,
    PARTICLE_DIM_SWITCH_A, PARTICLE_DIM_SWITCH_B,
    PARTICLE_DIM_FADE_A, PARTICLE_DIM_FADE_B,
    PARTICLE_PUSH_COLOR, PARTICLE_PUSH_FADE,
)


class ParticleManager:
    """
    Gestiona todos los efectos de partículas del juego.

    Uso básico:
        1. Llama a spawn_XXX() para crear un efecto (ej: spawn_water_splash).
        2. Llama a update(dt) cada frame para mover las partículas.
        3. Llama a draw(surface) cada frame para dibujarlas en pantalla.
    """

    def __init__(self):
        """Crea el sistema de partículas vacío."""
        self.system = pp_particle.ParticleSystem()

    def update(self, delta_time: float):
        """
        Actualiza todas las partículas activas.

        Args:
            delta_time: Tiempo transcurrido desde el último frame (en segundos).
        """
        self.system.update(delta_time=delta_time)

        # Aplicar efectos de color a cada partícula activa
        for p in self.system.particles:
            # Cada partícula guarda su color de destino en p.data
            if p.data and "fade_color" in p.data:
                pp_math.fade_color(p, p.data["fade_color"], p.inverted_progress)

    def draw(self, surface):
        """
        Dibuja todas las partículas en la superficie dada.

        Args:
            surface: La superficie de Pygame donde dibujar.
        """
        self.system.make_shape()
        self.system.render(surface)

    def spawn_water_splash(self, col: int, row: int):
        """
        Crea un efecto de splash cuando un barril cae al agua.

        Args:
            col: Columna donde ocurre el splash.
            row: Fila donde ocurre el splash.
        """
        # Calcular el centro de la casilla en píxeles
        center_x = col * TILE_SIZE + TILE_SIZE // 2
        center_y = row * TILE_SIZE + TILE_SIZE // 2

        # Crear 12 partículas con direcciones aleatorias
        for _ in range(12):
            speed_x = random.uniform(-120, 120)
            speed_y = random.uniform(-180, -30)

            self.system.emit(
                pp_particle.Particle(
                    shape=pp_shape.Circle(
                        radius=random.uniform(4, 8),
                        color=PARTICLE_WATER_COLOR,
                        alpha=220,
                    ),
                    position=(center_x, center_y),
                    velocity=(speed_x, speed_y),
                    delta_radius=random.uniform(0.08, 0.15),
                    data={"fade_color": PARTICLE_WATER_FADE},
                )
            )

    def spawn_dimension_switch(self, col: int, row: int, new_dim: str):
        """
        Crea un efecto visual al cambiar de dimensión.

        Args:
            col: Columna del jugador.
            row: Fila del jugador.
            new_dim: La nueva dimensión ("A" o "B").
        """
        center_x = col * TILE_SIZE + TILE_SIZE // 2
        center_y = row * TILE_SIZE + TILE_SIZE // 2

        # Elegir colores según la dimensión de destino
        if new_dim == "A":
            color = PARTICLE_DIM_SWITCH_A
            fade = PARTICLE_DIM_FADE_A
        else:
            color = PARTICLE_DIM_SWITCH_B
            fade = PARTICLE_DIM_FADE_B

        # Crear 8 partículas en forma de anillo
        for _ in range(8):
            speed_x = random.uniform(-100, 100)
            speed_y = random.uniform(-100, 100)

            self.system.emit(
                pp_particle.Particle(
                    shape=pp_shape.Rect(
                        radius=random.uniform(3, 6),
                        color=color,
                        alpha=200,
                    ),
                    position=(center_x, center_y),
                    velocity=(speed_x, speed_y),
                    delta_radius=random.uniform(0.06, 0.12),
                    data={"fade_color": fade},
                )
            )

    def spawn_push_effect(self, col: int, row: int):
        """
        Crea un efecto de polvo al empujar un barril.

        Args:
            col: Columna donde se empuja.
            row: Fila donde se empuja.
        """
        center_x = col * TILE_SIZE + TILE_SIZE // 2
        center_y = row * TILE_SIZE + TILE_SIZE // 2

        for _ in range(6):
            speed_x = random.uniform(-60, 60)
            speed_y = random.uniform(-60, 60)

            self.system.emit(
                pp_particle.Particle(
                    shape=pp_shape.Circle(
                        radius=random.uniform(2, 5),
                        color=PARTICLE_PUSH_COLOR,
                        alpha=180,
                    ),
                    position=(center_x, center_y),
                    velocity=(speed_x, speed_y),
                    delta_radius=random.uniform(0.05, 0.1),
                    data={"fade_color": PARTICLE_PUSH_FADE},
                )
            )
