"""Финальный этаж и босс."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from systems.game_state import GameState
    from world.dungeon import Dungeon


FINAL_DEPTH = 7


def generate_final_floor(state: "GameState", rng: random.Random | None = None) -> "Dungeon":
    """Сгенерировать финальный тронный зал с боссом."""
    from world.dungeon import Dungeon, Room
    from engine.render import COLOR_MAP

    if rng is None:
        rng = random.Random()

    width, height = 60, 22
    dungeon = Dungeon(width, height)
    dungeon.biome_id = "final_floor"

    # Всё — стены
    dungeon.tiles = [
        [{"type": "wall", "char": "#", "color_visible": COLOR_MAP.get("white", 7), "color_fog": 4} for _ in range(width)]
        for _ in range(height)
    ]
    dungeon.visible = [[False for _ in range(width)] for _ in range(height)]
    dungeon.explored = [[False for _ in range(width)] for _ in range(height)]

    biome_tiles = {
        "wall": {"char": "#", "color": "red"},
        "floor": {"char": ".", "color": "grey"},
        "stairs_down": {"char": ">", "color": "cyan"},
    }

    # Большой тронный зал
    hall_x, hall_y = 5, 5
    hall_w, hall_h = width - 10, height - 10
    for y in range(hall_y, hall_y + hall_h):
        for x in range(hall_x, hall_x + hall_w):
            dungeon.set_tile(x, y, "floor", {"tiles": biome_tiles})

    # Колонны
    for y in range(hall_y + 2, hall_y + hall_h - 2, 4):
        for x in range(hall_x + 4, hall_x + hall_w - 4, 8):
            dungeon.set_tile(x, y, "wall", {"tiles": biome_tiles})

    # Трон на противоположном конце
    throne_x = hall_x + hall_w // 2
    throne_y = hall_y + hall_h - 3
    dungeon.set_tile(throne_x, throne_y, "floor", {"tiles": biome_tiles})
    dungeon.rooms = [Room(hall_x, hall_y, hall_w, hall_h)]

    # Стартовая позиция — у входа
    start_x = hall_x + hall_w // 2
    start_y = hall_y + 2

    # Восходящая лестница/портал победы (условно stairs)
    dungeon.stairs = (start_x, start_y)
    dungeon.set_tile(start_x, start_y, "stairs", {"tiles": biome_tiles})

    # Босс — Тёмный Владыка
    if not state.final_boss_spawned:
        from entities.mob import Mob
        boss = Mob.from_data("dark_lord", throne_x, throne_y)
        # Усиленные характеристики босса
        boss.hp = 200
        boss.max_hp = 200
        boss.dmg = (4, 8, 4)
        boss.ac = 8
        boss.xp = 1000
        boss.gold_min = 500
        boss.gold_max = 1000
        boss.speed = 1.0
        state.mobs.append(boss)
        state.final_boss_spawned = True

    # Несколько прислужников
    from content.monsters import monsters_for_biome
    minion_pool = monsters_for_biome(["deep", "undead", "demon"], FINAL_DEPTH)
    for _ in range(4):
        mx = rng.randint(hall_x + 3, hall_x + hall_w - 4)
        my = rng.randint(hall_y + 5, hall_y + hall_h - 4)
        if dungeon.is_floor(mx, my) and (mx, my) not in {(start_x, start_y), (throne_x, throne_y)}:
            from entities.mob import Mob
            state.mobs.append(Mob.from_data(rng.choice(minion_pool), mx, my))

    return dungeon


# Определяем босса в таблице монстров? Лучше добавить динамически в content/monsters.py
# Но здесь оставим хук, который регистрирует dark_lord, если его нет.
def register_dark_lord() -> None:
    """Зарегистрировать босса в таблице монстров, если отсутствует."""
    from content.monsters import MONSTERS

    if "dark_lord" in MONSTERS:
        return

    MONSTERS["dark_lord"] = {
        "char": "&",
        "name": "Тёмный Владыка",
        "color": "magenta",
        "hp": 200,
        "atk": 8,
        "dmg": (4, 8, 4),
        "ac": 8,
        "speed": 1.0,
        "xp": 1000,
        "ai": "CASTER",
        "gold": (500, 1000),
        "loot_chance": 1.0,
        "loot_table": ["crown_of_wisdom", "heart_of_dragon", "amulet_of_life"],
        "depth": 99,
        "biome": "final_floor",
        "description": "Древнее зло, сидящее на троне подземелья.",
        "tags": ["deep", "demon", "mage"],
    }


register_dark_lord()
