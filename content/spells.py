"""
Таблица заклинаний для roguelike.

КАК ДОБАВИТЬ НОВОЕ ЗАКЛИНАНИЕ:
- Добавь новый ключ (уникальный ID) в SPELLS.
- Заполни поля по схеме ниже.

СХЕМА ПОЛЕЙ:
    id              : str          уникальный ключ
    name            : str          название
    mana_cost       : int          стоимость маны
    cooldown        : int          кулдаун в ходах (0 = нет)
    target_type     : str          single / aoe / self / line / cone
    aoe_radius      : int          радиус AoE (1 = 3x3, 2 = 5x5)
    range           : int          дальность каста
    effect          : str          основной эффект (damage_fire/damage_ice/heal/buff и т.д.)
    effect_power    : tuple/int    сила эффекта
    status          : str | None   накладываемый статус
    status_duration : int          длительность статуса
    school          : str          школа магии
    level_req       : int          минимальный уровень игрока
    description     : str          описание
"""

from __future__ import annotations

SPELLS: dict[str, dict] = {
    # --- Боевые single ---
    "magic_missile": {
        "name": "магическая стрела",
        "mana_cost": 2,
        "cooldown": 0,
        "target_type": "single",
        "range": 7,
        "effect": "damage_arcane",
        "effect_power": (3, 5),
        "status": None,
        "status_duration": 0,
        "school": "arcane",
        "level_req": 1,
        "description": "Простой снаряд чистой магии. Быстро и дёшево.",
    },
    "lightning_bolt": {
        "name": "удар молнии",
        "mana_cost": 6,
        "cooldown": 0,
        "target_type": "single",
        "range": 7,
        "effect": "damage_lightning",
        "effect_power": (8, 12),
        "status": None,
        "status_duration": 0,
        "school": "lightning",
        "level_req": 2,
        "description": "Молния поражает одну цель.",
    },
    "ice_bolt": {
        "name": "ледяная стрела",
        "mana_cost": 5,
        "cooldown": 0,
        "target_type": "single",
        "range": 6,
        "effect": "damage_ice",
        "effect_power": (6, 9),
        "status": "slowed",
        "status_duration": 3,
        "school": "ice",
        "level_req": 2,
        "description": "Ледяной снаряд замедляет цель.",
    },
    "holy_light": {
        "name": "святой свет",
        "mana_cost": 7,
        "cooldown": 0,
        "target_type": "single",
        "range": 6,
        "effect": "damage_holy",
        "effect_power": (12, 18),
        "status": None,
        "status_duration": 0,
        "school": "holy",
        "level_req": 3,
        "description": "Особенно эффективен против нежити.",
    },

    # --- AoE ---
    "fireball": {
        "name": "огненный шар",
        "mana_cost": 8,
        "cooldown": 3,
        "target_type": "aoe",
        "aoe_radius": 1,
        "range": 6,
        "effect": "damage_fire",
        "effect_power": (10, 18),
        "status": "burning",
        "status_duration": 3,
        "school": "fire",
        "level_req": 3,
        "description": "Взрыв огня поражает всех в зоне 3x3.",
    },
    "ice_storm": {
        "name": "ледяная буря",
        "mana_cost": 10,
        "cooldown": 5,
        "target_type": "aoe",
        "aoe_radius": 2,
        "range": 5,
        "effect": "damage_ice",
        "effect_power": (8, 14),
        "status": "freezing",
        "status_duration": 2,
        "school": "ice",
        "level_req": 4,
        "description": "Буря льда накрывает область 5x5.",
    },
    "chain_lightning": {
        "name": "цепная молния",
        "mana_cost": 9,
        "cooldown": 4,
        "target_type": "single",
        "range": 7,
        "effect": "chain_lightning",
        "effect_power": (6, 10),
        "status": None,
        "status_duration": 0,
        "school": "lightning",
        "level_req": 4,
        "description": "Молния прыгает между видимыми врагами.",
    },
    "earthquake": {
        "name": "землетрясение",
        "mana_cost": 12,
        "cooldown": 6,
        "target_type": "aoe",
        "aoe_radius": 3,
        "range": 0,
        "effect": "damage_earth",
        "effect_power": (5, 8),
        "status": "stunned",
        "status_duration": 1,
        "school": "nature",
        "level_req": 5,
        "description": "Удар по всем существам в большом радиусе вокруг вас.",
    },

    # --- Линия/конус ---
    "fire_breath": {
        "name": "огненное дыхание",
        "mana_cost": 6,
        "cooldown": 2,
        "target_type": "cone",
        "range": 3,
        "effect": "damage_fire",
        "effect_power": (6, 10),
        "status": "burning",
        "status_duration": 2,
        "school": "fire",
        "level_req": 3,
        "description": "Конус пламени обжигает врагов перед вами.",
    },
    "ray_of_frost": {
        "name": "луч холода",
        "mana_cost": 6,
        "cooldown": 2,
        "target_type": "line",
        "range": 5,
        "effect": "damage_ice",
        "effect_power": (7, 12),
        "status": "slowed",
        "status_duration": 3,
        "school": "ice",
        "level_req": 3,
        "description": "Ледяной луч пронзает врагов на линии.",
    },

    # --- Бафы (self) ---
    "heal_spell": {
        "name": "лечение",
        "mana_cost": 5,
        "cooldown": 2,
        "target_type": "self",
        "range": 0,
        "effect": "heal_spell",
        "effect_power": (15, 25),
        "status": None,
        "status_duration": 0,
        "school": "holy",
        "level_req": 1,
        "description": "Восстанавливает здоровье магией.",
    },
    "barrier": {
        "name": "магический барьер",
        "mana_cost": 6,
        "cooldown": 4,
        "target_type": "self",
        "range": 0,
        "effect": "buff_defense",
        "effect_power": 5,
        "status": "blessed",
        "status_duration": 10,
        "school": "arcane",
        "level_req": 2,
        "description": "Повышает защиту на 10 ходов.",
    },
    "haste": {
        "name": "ускорение",
        "mana_cost": 6,
        "cooldown": 5,
        "target_type": "self",
        "range": 0,
        "effect": "buff_haste",
        "effect_power": 5,
        "status": "hasted",
        "status_duration": 5,
        "school": "arcane",
        "level_req": 2,
        "description": "Вы ходите чаще.",
    },
    "invisibility": {
        "name": "невидимость",
        "mana_cost": 8,
        "cooldown": 8,
        "target_type": "self",
        "range": 0,
        "effect": "buff_invisible",
        "effect_power": 10,
        "status": "invisible",
        "status_duration": 10,
        "school": "dark",
        "level_req": 3,
        "description": "Враги перестают вас видеть.",
    },
    "regeneration": {
        "name": "регенерация",
        "mana_cost": 6,
        "cooldown": 5,
        "target_type": "self",
        "range": 0,
        "effect": "buff_regen",
        "effect_power": 2,
        "status": "regenerating",
        "status_duration": 8,
        "school": "nature",
        "level_req": 2,
        "description": "Восстанавливает HP каждый ход.",
    },

    # --- Утилитарные ---
    "teleport_spell": {
        "name": "телепорт",
        "mana_cost": 7,
        "cooldown": 5,
        "target_type": "self",
        "range": 0,
        "effect": "teleport",
        "effect_power": None,
        "status": None,
        "status_duration": 0,
        "school": "arcane",
        "level_req": 2,
        "description": "Переносит вас в случайное место уровня.",
    },
    "summon_skeleton": {
        "name": "призыв скелета",
        "mana_cost": 9,
        "cooldown": 8,
        "target_type": "self",
        "range": 0,
        "effect": "summon_ally",
        "effect_power": 15,
        "status": "ally",
        "status_duration": 15,
        "school": "dark",
        "level_req": 4,
        "description": "Призывает скелета-союзника на 15 ходов.",
    },
    "reveal": {
        "name": "обнаружение",
        "mana_cost": 5,
        "cooldown": 6,
        "target_type": "self",
        "range": 0,
        "effect": "reveal",
        "effect_power": 5,
        "status": "detecting",
        "status_duration": 5,
        "school": "arcane",
        "level_req": 2,
        "description": "Показывает всех монстров на уровне на 5 ходов.",
    },
    "banish": {
        "name": "изгнание",
        "mana_cost": 15,
        "cooldown": 10,
        "target_type": "single",
        "range": 4,
        "effect": "banish",
        "effect_power": None,
        "status": None,
        "status_duration": 0,
        "school": "holy",
        "level_req": 5,
        "description": "Мгновенно удаляет одного монстра с уровня.",
    },
}


def get_spell(spell_id: str) -> dict | None:
    return SPELLS.get(spell_id)


def spells_for_level(level: int) -> list[str]:
    """Вернуть ID заклинаний, доступных игроку данного уровня."""
    return [sid for sid, data in SPELLS.items() if data["level_req"] <= level]
