"""
Sistema de guardado de partidas en JSON.
Cada perfil guarda el nivel actual y los niveles completados.
"""
import json
import os

_SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
))), "saves")
_SAVE_FILE = os.path.join(_SAVE_DIR, "save_data.json")


def _load_all() -> dict:
    """Carga el JSON completo de guardado."""
    if not os.path.isfile(_SAVE_FILE):
        return {"profiles": {}}
    with open(_SAVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_all(data: dict):
    """Guarda el JSON completo."""
    os.makedirs(_SAVE_DIR, exist_ok=True)
    with open(_SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_profiles() -> list[str]:
    """Devuelve la lista de nombres de perfil existentes."""
    data = _load_all()
    return list(data["profiles"].keys())


def get_profile(name: str) -> dict | None:
    """Devuelve los datos de un perfil, o None si no existe."""
    data = _load_all()
    return data["profiles"].get(name)


def create_profile(name: str):
    """Crea un perfil nuevo (o lo reinicia si ya existe)."""
    data = _load_all()
    data["profiles"][name] = {
        "current_level": 0,
        "completed_levels": [],
    }
    _save_all(data)


def delete_profile(name: str):
    """Elimina un perfil."""
    data = _load_all()
    data["profiles"].pop(name, None)
    _save_all(data)


def save_progress(name: str, level_index: int, completed: bool):
    """
    Guarda el progreso de un perfil.
    Si completed=True, marca el nivel como completado y avanza al siguiente.
    """
    data = _load_all()
    profile = data["profiles"].get(name)
    if profile is None:
        return

    if completed and level_index not in profile["completed_levels"]:
        profile["completed_levels"].append(level_index)

    if completed:
        profile["current_level"] = level_index + 1
    else:
        profile["current_level"] = level_index

    _save_all(data)
