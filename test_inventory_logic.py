"""Тест логики инвентаря (без UI)."""

import sys

# Подавляем curses
sys.modules["curses"] = type(sys)("curses")
curses_mod = sys.modules["curses"]
for name, val in [
    ("COLOR_WHITE", 0), ("COLOR_BLACK", 1), ("COLOR_RED", 2),
    ("COLOR_GREEN", 3), ("COLOR_YELLOW", 4), ("COLOR_BLUE", 5),
    ("COLOR_MAGENTA", 6), ("COLOR_CYAN", 7),
]:
    setattr(curses_mod, name, val)
for fn in ["init_pair", "color_pair", "start_color", "use_default_colors"]:
    setattr(curses_mod, fn, lambda *a, **k: None)
curses_mod.KEY_UP = 259
curses_mod.KEY_DOWN = 258
curses_mod.KEY_LEFT = 260
curses_mod.KEY_RIGHT = 261
curses_mod.KEY_ENTER = 10
curses_mod.ACS_HLINE = "-"
curses_mod.echo = lambda: None
curses_mod.noecho = lambda: None
curses_mod.curs_set = lambda *a: None

from entities.player import Player
from systems.stats import recalculate_stats


def test_inventory_logic():
    player = Player(0, 0)
    player.inventory["short_sword"] = 1
    player.inventory["leather_armor"] = 1
    player.inventory["ring_of_health"] = 1

    # Надеваем оружие
    player.equipped_weapon = "short_sword"
    player.inventory["short_sword"] -= 1
    if player.inventory["short_sword"] <= 0:
        del player.inventory["short_sword"]

    # Надеваем броню
    player.equipped_armor = "leather_armor"
    player.inventory["leather_armor"] -= 1
    if player.inventory["leather_armor"] <= 0:
        del player.inventory["leather_armor"]

    # Надеваем кольцо
    player.equipped_left_ring = "ring_of_health"
    player.inventory["ring_of_health"] -= 1
    if player.inventory["ring_of_health"] <= 0:
        del player.inventory["ring_of_health"]

    recalculate_stats(player)
    print(f"Equipped stats: ATK {player.atk}, AC {player.ac}, HP {player.max_hp}")
    assert player.atk > 1
    assert player.ac > 0
    assert player.max_hp > 30

    # Снимаем (не проклятое)
    player.inventory[player.equipped_weapon] = player.inventory.get(player.equipped_weapon, 0) + 1
    player.equipped_weapon = None
    recalculate_stats(player)
    print(f"After unequip weapon: ATK {player.atk}")
    assert player.atk == 1  # базовый ATK на 1 уровне

    print("Inventory logic test passed")


if __name__ == "__main__":
    test_inventory_logic()
