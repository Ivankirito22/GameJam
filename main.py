"""
================================================================================
PUNTO DE ENTRADA
================================================================================
Este es el archivo principal que se debe ejecutar para iniciar el juego.
"""
from game import Game

if __name__ == "__main__":
    """
    Punto de entrada del programa.
    Crea una instancia de Game y comienza el bucle principal.
    """
    game_instance = Game()
    game_instance.run()