"""
Cargador de niveles TMX.
Lee archivos .tmx con capas nombradas:
    - "walls": tiles no caminables
    - "paths" / "path": tiles caminables
    - "btn": botones con propiedad "type" (green, yellow...)
    - "bridge-X": puentes dimensionales (dimension A o B)
"""
import pygame
import pytmx
from pytmx.util_pygame import load_pygame
from src.core.config import TILE_SIZE, WATER_GIDS


def _scale_surface(surface: pygame.Surface) -> pygame.Surface:
    """Escala una superficie del tileset (16x16) al tamano de juego (TILE_SIZE)."""
    if surface is None:
        return None
    w, h = surface.get_size()
    if w == TILE_SIZE and h == TILE_SIZE:
        return surface
    return pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))


def load_level(filepath: str) -> dict:
    """Load a .tmx file and return structured level data."""
    tmx = load_pygame(filepath)

    level = {
        "tmx": tmx,
        "tile_size": (tmx.tilewidth, tmx.tileheight),
        "map_size": (tmx.width, tmx.height),
        "walls": [],
        "paths": [],
        "buttons": [],
        "bridges": {},
        "water": [],
        "barrels": [],
        "door": None,
    }

    for layer in tmx.visible_layers:
        if not isinstance(layer, pytmx.TiledTileLayer):
            continue

        props = layer.properties
        name = layer.name

        if name == "walls":
            for x in range(tmx.width):
                for y in range(tmx.height):
                    gid = layer.data[y][x]
                    if gid:
                        surface = tmx.get_tile_image_by_gid(gid)
                        if surface:
                            scaled = _scale_surface(surface)
                            level["walls"].append((x, y, scaled))
                            if gid in WATER_GIDS:
                                level["water"].append((x, y))

        elif name in ("paths", "path"):
            for x, y, surface in layer.tiles():
                if surface:
                    level["paths"].append((x, y, _scale_surface(surface)))

        elif name == "btn":
            btn_type = props.get("type", "green")
            for x, y, surface in layer.tiles():
                if surface:
                    level["buttons"].append({
                        "pos": (x, y),
                        "type": btn_type,
                        "surface": _scale_surface(surface),
                    })

        elif name.startswith("bridge-"):
            dimension = props.get("dimension", name[-1].upper())
            walkable = props.get("walkable", True)
            visible = layer.visible

            tiles = []
            for x in range(tmx.width):
                for y in range(tmx.height):
                    gid = layer.data[y][x]
                    if gid:
                        surface = tmx.get_tile_image_by_gid(gid)
                        if surface:
                            tiles.append((x, y, _scale_surface(surface)))

            level["bridges"][dimension] = {
                "tiles": tiles,
                "walkable": walkable,
                "visible": visible,
            }

    # Leer objetos (barriles, puerta) desde objectgroups
    for layer in tmx.layers:
        if not isinstance(layer, pytmx.TiledObjectGroup):
            continue
        for obj in layer:
            col = int(obj.x // tmx.tilewidth)
            row = int(obj.y // tmx.tileheight)
            if obj.name == "barrel":
                props = obj.properties if obj.properties else {}
                level["barrels"].append({
                    "col": col,
                    "row": row,
                    "dim": props.get("dim", "A"),
                    "type": props.get("color", "green"),
                })
            elif obj.name == "door":
                level["door"] = (col, row)

    # Buscar capas bridge- no visibles (no aparecen en visible_layers)
    for layer in tmx.layers:
        if (isinstance(layer, pytmx.TiledTileLayer)
                and layer.name.startswith("bridge-")
                and not layer.visible):
            props = layer.properties
            dimension = props.get("dimension", layer.name[-1].upper())
            walkable = props.get("walkable", True)

            if dimension in level["bridges"]:
                continue

            tiles = []
            for x in range(tmx.width):
                for y in range(tmx.height):
                    gid = layer.data[y][x]
                    if gid:
                        surface = tmx.get_tile_image_by_gid(gid)
                        if surface:
                            tiles.append((x, y, _scale_surface(surface)))

            level["bridges"][dimension] = {
                "tiles": tiles,
                "walkable": walkable,
                "visible": False,
            }

    return level
