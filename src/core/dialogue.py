"""
Sistema de dialogos narrativos.
Muestra texto linea a linea con avance por tecla ENTER.
"""

# Dialogos de inicio de cada nivel (por indice 0-4)
LEVEL_DIALOGUES = {
    0: [
        ("???", "Algo... algo ha ido terriblemente mal."),
        ("???", "Puedo sentir como dos realidades se superponen."),
        ("???", "Las dimensiones estan conectadas aunque no sean lo mismo."),
        ("???", "Cada una tiene sus propias reglas, sus propios caminos..."),
        ("???", "Pero ahora se han fracturado entre si."),
        ("???", "Debo encontrar la salida. Pulsa ESPACIO para cambiar de dimension."),
    ],
    1: [
        ("Viajero", "La fractura se extiende... puedo ver los ecos de la otra dimension."),
        ("Viajero", "Los puentes entre realidades aparecen y desaparecen segun donde este."),
        ("Viajero", "Tengo que usar ambas dimensiones para avanzar."),
        ("Viajero", "Los botones de colores... cada barril debe llegar a su lugar."),
    ],
    2: [
        ("Viajero", "Este lugar es mas complejo. La fractura se profundiza."),
        ("Viajero", "Noto como los objetos existen en dimensiones distintas a la vez."),
        ("Viajero", "Si no reparo estas grietas, ambas realidades colapsaran."),
        ("Viajero", "Debo pensar bien cada movimiento antes de actuar."),
    ],
    3: [
        ("Viajero", "Estoy cada vez mas cerca del epicentro de la fractura."),
        ("Viajero", "Las paredes cambian segun la dimension... esto es un laberinto."),
        ("Viajero", "Puedo sentir la energia de ambos mundos convergiendo."),
        ("Viajero", "Un poco mas y podre llegar al origen del desastre."),
    ],
    4: [
        ("Viajero", "Este es el nucleo de la fractura. Aqui es donde todo empezo."),
        ("Viajero", "Las dos dimensiones vibran con una intensidad insoportable."),
        ("Viajero", "Necesito ayuda... no puedo cerrar esto solo."),
        ("Viajero", "Espera... hay alguien mas aqui. Pulsa E para hablar."),
    ],
}

# Dialogo de Jeffrey Epstein en nivel 5
JEFFRY_DIALOGUE = [
    ("???", "Eh, tu! Si, tu, el que va saltando entre dimensiones."),
    ("???", "No pongas esa cara. Se exactamente lo que esta pasando aqui."),
    ("Jeffrey Epstein", "Me llamo Jeffrey Epstein. Pero puedes llamarme Jeffrey. Encantado."),
    ("Jeffrey Epstein", "Veras, yo llevo observando esta fractura dimensional desde hace tiempo."),
    ("Jeffrey Epstein", "Tengo... digamos... recursos. Mucho poder social, politico, y sobre todo, dinero."),
    ("Jeffrey Epstein", "Con mi influencia puedo movilizar a los mejores cientificos de ambas dimensiones."),
    ("Jeffrey Epstein", "Y tu has demostrado tener el talento para navegar entre los dos mundos."),
    ("Jeffrey Epstein", "Juntos podemos sellar la fractura de una vez por todas."),
    ("Jeffrey Epstein", "Yo pondre los medios. Tu pon la voluntad."),
    ("Jeffrey Epstein", "Mira, ya he activado el portal de sellado. Solo tienes que cruzarlo."),
    ("Jeffrey Epstein", "Cuando lo hagas, las dimensiones se estabilizaran para siempre."),
    ("Jeffrey Epstein", "Adelante, heroe. Es hora de arreglar el mundo. Los dos mundos."),
]


class DialogueBox:
    """Gestiona el estado de un dialogo activo."""

    def __init__(self, lines: list[tuple[str, str]]):
        self.lines = lines
        self.current_index = 0
        self.finished = False

    @property
    def current_speaker(self) -> str:
        if self.current_index < len(self.lines):
            return self.lines[self.current_index][0]
        return ""

    @property
    def current_text(self) -> str:
        if self.current_index < len(self.lines):
            return self.lines[self.current_index][1]
        return ""

    def advance(self) -> bool:
        """Avanza al siguiente dialogo. Devuelve True si el dialogo ha terminado."""
        self.current_index += 1
        if self.current_index >= len(self.lines):
            self.finished = True
            return True
        return False
