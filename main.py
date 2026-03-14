"""
================================================================================
PUNTO DE ENTRADA DEL JUEGO - Dimension Puzzle
================================================================================
Este es el archivo que debes ejecutar para iniciar el juego:
    python main.py

El juego se organiza así:
    src/
        core/       → Configuración, lógica del nivel y clase Game
        entities/   → Clases de los objetos del juego (jugador, barril...)
        map/        → Generación del mapa del nivel
        rendering/  → Todo lo que se dibuja en pant alla + partículas
"""
from src.core.game import Game

if __name__ == "__main__":
    game = Game()
    game.run()

