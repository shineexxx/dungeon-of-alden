"""
Таблица брони для roguelike.

КАК ДОБАВИТЬ НОВУЮ БРОНЮ:
- Добавь новый ключ (уникальный ID) в ARMOR.
- Заполни поля по схеме ниже.

СХЕМА ПОЛЕЙ:
    id            : str          уникальный ключ
    char          : str          символ на карте
    name          : str          название
    color         : str          цвет curses
    defense       : int          снижение входящего урона
    hp_bonus      : int          бонус к максимальному HP
    speed_penalty : float        штраф к скорости хода (отрицательное число)
    cursed        : bool         проклятая — нельзя снять
    rarity        : str          common/uncommon/rare/legendary
    depth_min     : int          минимальная глубина появления
    description   : str          описание
"""

from __future__ import annotations

ARMOR: dict[str, dict] = {
    # --- Лёгкая броня ---
    "leather_armor": {
        "char": "[",
        "name": "кожаный доспех",
        "color": "yellow",
        "defense": 1,
        "hp_bonus": 0,
        "speed_penalty": 0.0,
        "cursed": False,
        "rarity": "common",
        "depth_min": 1,
        "description": "Грубая кожа, но лучше, чем ничего.",
    },
    "studded_leather": {
        "char": "[",
        "name": "доспех с клепками",
        "color": "yellow",
        "defense": 2,
        "hp_bonus": 0,
        "speed_penalty": 0.0,
        "rarity": "common",
        "depth_min": 2,
        "description": "Кожа, усиленная металлическими клепками.",
    },
    "hide_armor": {
        "char": "[",
        "name": "доспех из шкур",
        "color": "yellow",
        "defense": 2,
        "hp_bonus": 5,
        "speed_penalty": -0.05,
        "cursed": False,
        "rarity": "common",
        "depth_min": 2,
        "description": "Толстые шкуры зверей. Даёт немного запаса здоровья.",
    },
    "chain_shirt": {
        "char": "[",
        "name": "кольчужная рубаха",
        "color": "cyan",
        "defense": 3,
        "hp_bonus": 0,
        "speed_penalty": -0.05,
        "cursed": False,
        "rarity": "uncommon",
        "depth_min": 3,
        "description": "Лёгкая кольчуга под одеждой.",
    },

    # --- Средняя броня ---
    "scale_mail": {
        "char": "[",
        "name": "чешуйчатый доспех",
        "color": "cyan",
        "defense": 4,
        "hp_bonus": 0,
        "speed_penalty": -0.1,
        "cursed": False,
        "rarity": "uncommon",
        "depth_min": 3,
        "description": "Металлические чешуйки, напоминающие чешую рыбы.",
    },
    "brigandine": {
        "char": "[",
        "name": "бригандина",
        "color": "cyan",
        "defense": 4,
        "hp_bonus": 5,
        "speed_penalty": -0.1,
        "cursed": False,
        "rarity": "uncommon",
        "depth_min": 4,
        "description": "Ткань с вшитыми металлическими пластинами.",
    },
    "breastplate": {
        "char": "[",
        "name": "нагрудник",
        "color": "blue",
        "defense": 5,
        "hp_bonus": 0,
        "speed_penalty": -0.1,
        "cursed": False,
        "rarity": "rare",
        "depth_min": 4,
        "description": "Прочная металлическая грудная пластина.",
    },

    # --- Тяжёлая броня ---
    "splint_armor": {
        "char": "[",
        "name": "пластинчатый доспех",
        "color": "blue",
        "defense": 6,
        "hp_bonus": 0,
        "speed_penalty": -0.15,
        "cursed": False,
        "rarity": "rare",
        "depth_min": 5,
        "description": "Пластины, нашитые на кожаную основу. Тяжёлый, но надёжный.",
    },
    "plate_armor": {
        "char": "[",
        "name": "рыцарские латы",
        "color": "yellow",
        "defense": 8,
        "hp_bonus": 10,
        "speed_penalty": -0.2,
        "cursed": False,
        "rarity": "legendary",
        "depth_min": 6,
        "description": "Полный комплект латов. Лучшая защита, но замедляет.",
    },
    "cursed_plate": {
        "char": "[",
        "name": "проклятые латы",
        "color": "red",
        "defense": 10,
        "hp_bonus": 15,
        "speed_penalty": -0.25,
        "cursed": True,
        "rarity": "legendary",
        "depth_min": 6,
        "description": "Невероятно прочные, но проклятые. Нельзя снять.",
    },
}


def get_armor(armor_id: str) -> dict | None:
    return ARMOR.get(armor_id)


def armor_for_depth(depth: int) -> list[str]:
    """Вернуть ID брони, подходящей для глубины."""
    return [aid for aid, data in ARMOR.items() if data["depth_min"] <= depth + 1]


def rarity_color(rarity: str) -> str:
    """Цвет для отображения редкости."""
    return {
        "common": "white",
        "uncommon": "green",
        "rare": "blue",
        "legendary": "yellow",
    }.get(rarity, "white")
