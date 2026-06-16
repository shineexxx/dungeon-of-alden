"""
Таблица оружия для roguelike.

КАК ДОБАВИТЬ НОВОЕ ОРУЖИЕ:
- Добавь новый ключ (уникальный ID) в WEAPONS.
- Заполни поля по схеме ниже.

СХЕМА ПОЛЕЙ:
    id          : str          уникальный ключ
    char        : str          символ на карте
    name        : str          название
    color       : str          цвет curses
    damage      : tuple[int]   (min_damage, max_damage)
    speed       : float        бонус к скорости атаки (1.0 = норма)
    crit_chance : float        шанс критического удара (0.0 - 1.0)
    cursed      : bool         проклятое — нельзя снять
    bonus       : str | None   спецэффект: 'poison', 'fire', 'vampiric', 'frost', None
    rarity      : str          common/uncommon/rare/legendary
    depth_min   : int          минимальная глубина появления
    description : str          описание
"""

from __future__ import annotations

WEAPONS: dict[str, dict] = {
    # --- Клинки ---
    "dagger": {
        "char": "/",
        "name": "кинжал",
        "color": "white",
        "damage": (2, 4),
        "speed": 1.2,
        "crit_chance": 0.15,
        "cursed": False,
        "bonus": None,
        "rarity": "common",
        "depth_min": 1,
        "description": "Лёгкое и острое лезвие. Быстрое, но слабое.",
    },
    "short_sword": {
        "char": "/",
        "name": "короткий меч",
        "color": "white",
        "damage": (3, 6),
        "speed": 1.0,
        "crit_chance": 0.1,
        "cursed": False,
        "bonus": None,
        "rarity": "common",
        "depth_min": 1,
        "description": "Надёжный клинок для начинающих искателей приключений.",
    },
    "long_sword": {
        "char": "/",
        "name": "длинный меч",
        "color": "white",
        "damage": (5, 9),
        "speed": 1.0,
        "crit_chance": 0.1,
        "cursed": False,
        "bonus": None,
        "rarity": "common",
        "depth_min": 2,
        "description": "Сбалансированное оружие с хорошей досягаемостью.",
    },
    "rapier": {
        "char": "/",
        "name": "рапира",
        "color": "cyan",
        "damage": (4, 7),
        "speed": 1.3,
        "crit_chance": 0.2,
        "cursed": False,
        "bonus": None,
        "rarity": "uncommon",
        "depth_min": 3,
        "description": "Тонкий клинок, идеальный для точных уколов.",
    },
    "greatsword": {
        "char": "/",
        "name": "двуручный меч",
        "color": "yellow",
        "damage": (8, 14),
        "speed": 0.8,
        "crit_chance": 0.1,
        "cursed": False,
        "bonus": None,
        "rarity": "rare",
        "depth_min": 4,
        "description": "Массивный меч, требующий силы. Медленный, но разрушительный.",
    },

    # --- Дробящее ---
    "club": {
        "char": "|",
        "name": "дубина",
        "color": "white",
        "damage": (2, 5),
        "speed": 0.9,
        "crit_chance": 0.05,
        "cursed": False,
        "bonus": None,
        "rarity": "common",
        "depth_min": 1,
        "description": "Тяжёлая деревянная палка.",
    },
    "mace": {
        "char": "|",
        "name": "булава",
        "color": "white",
        "damage": (4, 7),
        "speed": 1.0,
        "crit_chance": 0.08,
        "cursed": False,
        "bonus": None,
        "rarity": "common",
        "depth_min": 2,
        "description": "Оружие с шипастой головой. Хорошо против брони.",
    },
    "warhammer": {
        "char": "|",
        "name": "боевой молот",
        "color": "yellow",
        "damage": (7, 12),
        "speed": 0.8,
        "crit_chance": 0.1,
        "cursed": False,
        "bonus": None,
        "rarity": "rare",
        "depth_min": 4,
        "description": "Двуручный молот. Крушит черепа и доспехи.",
    },

    # --- Древковое ---
    "spear": {
        "char": "-",
        "name": "копьё",
        "color": "white",
        "damage": (4, 8),
        "speed": 1.0,
        "crit_chance": 0.12,
        "cursed": False,
        "bonus": None,
        "rarity": "common",
        "depth_min": 2,
        "description": "Позволяет атаковать врага на расстоянии одной клетки.",
    },
    "quarterstaff": {
        "char": "-",
        "name": "боевой посох",
        "color": "cyan",
        "damage": (3, 6),
        "speed": 1.2,
        "crit_chance": 0.1,
        "cursed": False,
        "bonus": None,
        "rarity": "uncommon",
        "depth_min": 2,
        "description": "Древко из твёрдого дерева. Быстрое и универсальное.",
    },

    # --- Особые ---
    "poisoned_blade": {
        "char": "/",
        "name": "отравленный клинок",
        "color": "green",
        "damage": (3, 6),
        "speed": 1.1,
        "crit_chance": 0.12,
        "cursed": False,
        "bonus": "poison",
        "rarity": "uncommon",
        "depth_min": 3,
        "description": "Покрыт ядом. Ранит не только плоть, но и кровь.",
    },
    "flaming_sword": {
        "char": "/",
        "name": "огненный меч",
        "color": "red",
        "damage": (6, 10),
        "speed": 1.0,
        "crit_chance": 0.1,
        "cursed": False,
        "bonus": "fire",
        "rarity": "rare",
        "depth_min": 4,
        "description": "Клинок, пылающий магическим огнём.",
    },
    "vampiric_dagger": {
        "char": "/",
        "name": "вампирский кинжал",
        "color": "magenta",
        "damage": (4, 7),
        "speed": 1.1,
        "crit_chance": 0.1,
        "cursed": False,
        "bonus": "vampiric",
        "rarity": "rare",
        "depth_min": 4,
        "description": "Восстанавливает здоровье владельцу при ударах.",
    },
    "frost_axe": {
        "char": "|",
        "name": "ледяной топор",
        "color": "cyan",
        "damage": (7, 11),
        "speed": 0.9,
        "crit_chance": 0.1,
        "cursed": False,
        "bonus": "frost",
        "rarity": "rare",
        "depth_min": 5,
        "description": "Покрыт инеем. Замедляет жертву.",
    },
    "cursed_blade": {
        "char": "/",
        "name": "проклятый клинок",
        "color": "red",
        "damage": (10, 16),
        "speed": 1.0,
        "crit_chance": 0.15,
        "cursed": True,
        "bonus": "vampiric",
        "rarity": "legendary",
        "depth_min": 5,
        "description": "Мощное оружие, но невозможно снять, пока не снято проклятие.",
    },
}


def get_weapon(weapon_id: str) -> dict | None:
    return WEAPONS.get(weapon_id)


def weapons_for_depth(depth: int) -> list[str]:
    """Вернуть ID оружия, подходящего для глубины."""
    return [wid for wid, data in WEAPONS.items() if data["depth_min"] <= depth + 1]


def rarity_color(rarity: str) -> str:
    """Цвет для отображения редкости."""
    return {
        "common": "white",
        "uncommon": "green",
        "rare": "blue",
        "legendary": "yellow",
    }.get(rarity, "white")
