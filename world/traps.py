"""Ловушки — скрытые элементы карты.

СХЕМА ПОЛЕЙ:
    id              : str      уникальный ключ
    char_hidden     : str      как выглядит до обнаружения
    char_revealed   : str      как выглядит после
    color_revealed  : str      имя цвета curses
    trigger         : str      on_step / on_search
    effect          : str      ключ эффекта в systems/effects.py или спец-эффект
    effect_power    : tuple/int параметры
    detect_chance   : float    базовый шанс обнаружения при поиске
    one_time        : bool     срабатывает один раз
    depth_min       : int      минимальная глубина
    description     : str
"""

from __future__ import annotations

TRAPS: dict[str, dict] = {
    "spike_trap": {
        "id": "spike_trap",
        "char_hidden": ".",
        "char_revealed": "^",
        "color_revealed": "white",
        "trigger": "on_step",
        "effect": "damage_physical",
        "effect_power": (5, 10),
        "detect_chance": 0.35,
        "one_time": True,
        "depth_min": 1,
        "description": "Стальные шипы выскакивают из пола.",
    },
    "poison_needle": {
        "id": "poison_needle",
        "char_hidden": ".",
        "char_revealed": "^",
        "color_revealed": "green",
        "trigger": "on_step",
        "effect": "poison",
        "effect_power": 5,
        "detect_chance": 0.30,
        "one_time": True,
        "depth_min": 2,
        "description": "Игла впрыскивает яд.",
    },
    "fire_plate": {
        "id": "fire_plate",
        "char_hidden": ".",
        "char_revealed": "^",
        "color_revealed": "red",
        "trigger": "on_step",
        "effect": "damage_fire",
        "effect_power": (4, 8),
        "detect_chance": 0.30,
        "one_time": True,
        "depth_min": 3,
        "description": "Плита вспыхивает огнём.",
    },
    "ice_spike": {
        "id": "ice_spike",
        "char_hidden": ".",
        "char_revealed": "^",
        "color_revealed": "cyan",
        "trigger": "on_step",
        "effect": "freezing",
        "effect_power": 3,
        "detect_chance": 0.25,
        "one_time": True,
        "depth_min": 4,
        "description": "Ледяной шип замораживает ноги.",
    },
    "teleport_trap": {
        "id": "teleport_trap",
        "char_hidden": ".",
        "char_revealed": "^",
        "color_revealed": "magenta",
        "trigger": "on_step",
        "effect": "teleport",
        "effect_power": None,
        "detect_chance": 0.20,
        "one_time": True,
        "depth_min": 4,
        "description": "Магическая руна телепортирует жертву.",
    },
    "alarm_trap": {
        "id": "alarm_trap",
        "char_hidden": ".",
        "char_revealed": "^",
        "color_revealed": "yellow",
        "trigger": "on_step",
        "effect": "alarm",
        "effect_power": 2,
        "detect_chance": 0.30,
        "one_time": True,
        "depth_min": 3,
        "description": "Сигнал призывает ближайших монстров.",
    },
    "sleep_gas": {
        "id": "sleep_gas",
        "char_hidden": ".",
        "char_revealed": "^",
        "color_revealed": "blue",
        "trigger": "on_step",
        "effect": "paralyzed",
        "effect_power": 3,
        "detect_chance": 0.25,
        "one_time": True,
        "depth_min": 5,
        "description": "Усыпляющий газ выбрасывается из щели.",
    },
    "curse_rune": {
        "id": "curse_rune",
        "char_hidden": ".",
        "char_revealed": "^",
        "color_revealed": "black",
        "trigger": "on_step",
        "effect": "random_debuff",
        "effect_power": 5,
        "detect_chance": 0.20,
        "one_time": True,
        "depth_min": 6,
        "description": "Руна проклятия ослабляет жертву.",
    },
    "falling_rock": {
        "id": "falling_rock",
        "char_hidden": ".",
        "char_revealed": "^",
        "color_revealed": "brown",
        "trigger": "on_step",
        "effect": "damage_physical",
        "effect_power": (10, 18),
        "detect_chance": 0.25,
        "one_time": True,
        "depth_min": 5,
        "description": "С потолка падает тяжёлый камень.",
    },
    "magic_rune": {
        "id": "magic_rune",
        "char_hidden": ".",
        "char_revealed": "^",
        "color_revealed": "magenta",
        "trigger": "on_step",
        "effect": "damage_arcane",
        "effect_power": (8, 14),
        "detect_chance": 0.20,
        "one_time": True,
        "depth_min": 7,
        "description": "Руна взрывается магической энергией.",
    },
}


def get_trap(trap_id: str) -> dict | None:
    return TRAPS.get(trap_id)


def traps_for_depth(depth: int) -> list[str]:
    """Вернуть ID ловушек, доступных на этой глубине."""
    return [tid for tid, data in TRAPS.items() if data.get("depth_min", 1) <= depth]
