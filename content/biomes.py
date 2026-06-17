"""Таблица биомов подземелий.

СХЕМА ПОЛЕЙ:
    id              : str      уникальный ключ
    name            : str      название для HUD/лога
    depth_range     : tuple    (min, max) глубины появления
    tiles           : dict     wall/floor/stairs с char и color (имя цвета)
    generator       : str      rooms_corridors / cellular_automata / tunnels / bridges_lava / open_arena
    monster_tags    : list     хотя бы один тег монстра должен совпадать
    item_tags       : list     хотя бы один тег предмета должен совпадать
    hazards         : list     возможные опасности (id из world/hazards.py)
    hazard_density  : float    доля floor-клеток, заменяемых на hazard
    trap_density    : float    доля floor-клеток с ловушкой
    fov_modifier    : int      модификатор радиуса обзора (может быть отрицательным)
    ambient_color   : str      ключ цвета для общего тона
    description     : str      текст при входе
"""

from __future__ import annotations

BIOMES: dict[str, dict] = {
    "dungeon": {
        "id": "dungeon",
        "name": "Каменное подземелье",
        "depth_range": (1, 3),
        "tiles": {
            "wall": {"char": "#", "color": "white"},
            "floor": {"char": ".", "color": "grey"},
            "stairs_down": {"char": ">", "color": "cyan"},
        },
        "generator": "rooms_corridors",
        "monster_tags": ["dungeon", "humanoid", "undead", "beast"],
        "item_tags": ["common", "dungeon"],
        "hazards": [],
        "hazard_density": 0.0,
        "trap_density": 0.02,
        "fov_modifier": 0,
        "ambient_color": "white",
        "description": "Древние каменные коридоры, забытые временем.",
    },
    "caves": {
        "id": "caves",
        "name": "Пещеры",
        "depth_range": (4, 6),
        "tiles": {
            "wall": {"char": "#", "color": "brown"},
            "floor": {"char": ".", "color": "dark_green"},
            "stairs_down": {"char": ">", "color": "cyan"},
        },
        "generator": "cellular_automata",
        "monster_tags": ["cave", "beast", "humanoid", "flying"],
        "item_tags": ["common", "cave"],
        "hazards": ["water", "mud"],
        "hazard_density": 0.06,
        "trap_density": 0.03,
        "fov_modifier": 0,
        "ambient_color": "brown",
        "description": "Влажные пещеры, где вода капает с потолка, а тени шевелятся.",
    },
    "crypt": {
        "id": "crypt",
        "name": "Затопленный склеп",
        "depth_range": (7, 9),
        "tiles": {
            "wall": {"char": "#", "color": "cyan"},
            "floor": {"char": ".", "color": "blue"},
            "stairs_down": {"char": ">", "color": "cyan"},
        },
        "generator": "rooms_corridors",
        "monster_tags": ["crypt", "undead", "mage"],
        "item_tags": ["common", "crypt", "rare"],
        "hazards": ["water", "spikes"],
        "hazard_density": 0.08,
        "trap_density": 0.04,
        "fov_modifier": 0,
        "ambient_color": "blue",
        "description": "Холодный склеп поглощён водой. Здесь покоятся древние мертвецы.",
    },
    "mushroom_forest": {
        "id": "mushroom_forest",
        "name": "Грибной лес",
        "depth_range": (8, 10),
        "tiles": {
            "wall": {"char": "T", "color": "green"},
            "floor": {"char": ".", "color": "magenta"},
            "stairs_down": {"char": ">", "color": "cyan"},
        },
        "generator": "cellular_automata",
        "monster_tags": ["mushroom", "poisonous", "beast"],
        "item_tags": ["common", "mushroom", "rare"],
        "hazards": ["glowing_mushroom", "poison_gas"],
        "hazard_density": 0.07,
        "trap_density": 0.03,
        "fov_modifier": 1,
        "ambient_color": "magenta",
        "description": "Светящиеся грибы озаряют пещеру. В воздухе витает ядовитая пыльца.",
    },
    "hell_forge": {
        "id": "hell_forge",
        "name": "Кузница ада",
        "depth_range": (11, 13),
        "tiles": {
            "wall": {"char": "#", "color": "red"},
            "floor": {"char": ".", "color": "orange"},
            "stairs_down": {"char": ">", "color": "cyan"},
        },
        "generator": "bridges_lava",
        "monster_tags": ["hell", "demon", "fire", "mage"],
        "item_tags": ["rare", "hell", "fire_themed"],
        "hazards": ["lava", "fire_pit"],
        "hazard_density": 0.12,
        "trap_density": 0.05,
        "fov_modifier": 0,
        "ambient_color": "red",
        "description": "Жар волной бьёт в лицо. Расплавленная лава речками течёт между мостками.",
    },
    "deep_dark": {
        "id": "deep_dark",
        "name": "Тёмные глубины",
        "depth_range": (14, 99),
        "tiles": {
            "wall": {"char": "#", "color": "black"},
            "floor": {"char": ".", "color": "grey"},
            "stairs_down": {"char": ">", "color": "cyan"},
        },
        "generator": "open_arena",
        "monster_tags": ["deep", "undead", "aberration", "mage"],
        "item_tags": ["rare", "legendary", "deep"],
        "hazards": ["darkness", "void"],
        "hazard_density": 0.10,
        "trap_density": 0.06,
        "fov_modifier": -2,
        "ambient_color": "black",
        "description": "Здесь свет гаснет. В темноте что-то древнее наблюдает за каждым шагом.",
    },
}


def get_biome(biome_id: str) -> dict | None:
    return BIOMES.get(biome_id)


def biome_for_depth(depth: int, rng=None) -> dict:
    """Выбрать подходящий биом для глубины."""
    import random

    candidates = [
        b for b in BIOMES.values()
        if b["depth_range"][0] <= depth <= b["depth_range"][1]
    ]
    if not candidates:
        # Fallback: самый глубокий доступный биом
        candidates = list(BIOMES.values())
    if rng is None:
        rng = random.Random()
    return rng.choice(candidates)
