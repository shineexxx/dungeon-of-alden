"""Статические опасности на карте (hazards).

СХЕМА ПОЛЕЙ:
    id              : str      уникальный ключ
    char            : str      символ на карте
    color           : str      имя цвета curses
    walkable        : bool     можно ли войти (True — вход возможен, но есть эффект)
    blocks_movement : bool     блокирует ли движение (альтернатива walkable)
    blocks_sight    : bool     блокирует ли линию видимости
    on_enter        : str      эффект при входе (None если нет)
    on_enter_power  : tuple/int параметры эффекта
    description     : str
"""

from __future__ import annotations

HAZARDS: dict[str, dict] = {
    "lava": {
        "id": "lava",
        "unicode_char": "🔥",
        "char": "~",
        "color": "red",
        "walkable": False,
        "blocks_movement": True,
        "blocks_sight": False,
        "on_enter": "damage_fire",
        "on_enter_power": (8, 15),
        "description": "Расплавленный камень. Нельзя ступить, но можно обойти.",
    },
    "water": {
        "id": "water",
        "unicode_char": "≈",
        "char": "=",
        "color": "blue",
        "walkable": True,
        "blocks_movement": False,
        "blocks_sight": False,
        "on_enter": "slow",
        "on_enter_power": 1,
        "description": "Вода замедляет движение.",
    },
    "mud": {
        "id": "mud",
        "unicode_char": "▒",
        "char": ",",
        "color": "brown",
        "walkable": True,
        "blocks_movement": False,
        "blocks_sight": False,
        "on_enter": "slow",
        "on_enter_power": 1,
        "description": "Грязь цепляет ноги.",
    },
    "ice": {
        "id": "ice",
        "unicode_char": "❄",
        "char": "*",
        "color": "cyan",
        "walkable": True,
        "blocks_movement": False,
        "blocks_sight": False,
        "on_enter": "slide",
        "on_enter_power": 2,
        "description": "Лёд скользкий: несёт тебя на 2 клетки вперёд.",
    },
    "spikes": {
        "id": "spikes",
        "unicode_char": "▲",
        "char": "^",
        "color": "white",
        "walkable": True,
        "blocks_movement": False,
        "blocks_sight": False,
        "on_enter": "damage_physical",
        "on_enter_power": (1, 3),
        "description": "Острые шипы торчат из пола.",
    },
    "poison_gas": {
        "id": "poison_gas",
        "unicode_char": "☣",
        "char": "%",
        "color": "green",
        "walkable": True,
        "blocks_movement": False,
        "blocks_sight": True,
        "on_enter": "poison",
        "on_enter_power": 5,
        "description": "Ядовитые испарения.",
    },
    "web": {
        "id": "web",
        "unicode_char": "🕸",
        "char": "&",
        "color": "white",
        "walkable": True,
        "blocks_movement": False,
        "blocks_sight": False,
        "on_enter": "web_stuck",
        "on_enter_power": 2,
        "description": "Липкая паутина.",
    },
    "glowing_mushroom": {
        "id": "glowing_mushroom",
        "unicode_char": "🍄",
        "char": ";",
        "color": "magenta",
        "walkable": True,
        "blocks_movement": False,
        "blocks_sight": False,
        "on_enter": "light",
        "on_enter_power": 1,
        "description": "Светящийся гриб слегка увеличивает обзор.",
    },
    "fire_pit": {
        "id": "fire_pit",
        "unicode_char": "🔥",
        "char": "0",
        "color": "red",
        "walkable": True,
        "blocks_movement": False,
        "blocks_sight": False,
        "on_enter": "damage_fire",
        "on_enter_power": (3, 6),
        "description": "Жаровня с тлеющим огнём.",
    },
    "darkness": {
        "id": "darkness",
        "unicode_char": "▓",
        "char": " ",
        "color": "black",
        "walkable": True,
        "blocks_movement": False,
        "blocks_sight": False,
        "on_enter": "darkness",
        "on_enter_power": 1,
        "description": "Поглощающий свет туман.",
    },
    "void": {
        "id": "void",
        "unicode_char": "∅",
        "char": "·",
        "color": "black",
        "walkable": True,
        "blocks_movement": False,
        "blocks_sight": False,
        "on_enter": "confusion",
        "on_enter_power": 3,
        "description": "Пустота искажает разум.",
    },
}


def get_hazard(hazard_id: str) -> dict | None:
    return HAZARDS.get(hazard_id)
