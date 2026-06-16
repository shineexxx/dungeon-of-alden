"""Тест экипировки и пересчёта статов."""

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


def test_equipment():
    player = Player(0, 0)
    recalculate_stats(player)
    base_atk = player.atk
    base_ac = player.ac
    print(f"Base stats: ATK {base_atk}, AC {base_ac}, HP {player.max_hp}")

    # Надеваем оружие
    player.equipped_weapon = "short_sword"
    recalculate_stats(player)
    print(f"With short sword: ATK {player.atk}, AC {player.ac}")
    assert player.atk > base_atk

    # Надеваем броню
    player.equipped_armor = "leather_armor"
    recalculate_stats(player)
    print(f"With armor: ATK {player.atk}, AC {player.ac}")
    assert player.ac > base_ac

    # Надеваем кольцо
    player.equipped_left_ring = "ring_of_health"
    old_hp = player.max_hp
    recalculate_stats(player)
    print(f"With ring: HP {player.max_hp}")
    assert player.max_hp > old_hp

    print("Equipment test passed")


if __name__ == "__main__":
    test_equipment()
