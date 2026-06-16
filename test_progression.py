"""Тест прогрессии и перков."""

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
from systems.progression import add_xp, apply_perk, xp_to_next_level


def test_progression():
    player = Player(0, 0)
    assert player.xp_to_next() == 20

    # Даём 25 XP -> должен быть 1 уровень и 5 XP
    levels = add_xp(player, 25)
    assert levels == 1
    assert player.level == 2
    assert player.xp == 5
    print(f"After 25 XP: level {player.level}, xp {player.xp}, next {player.xp_to_next()}")

    # Применяем перк
    old_hp = player.max_hp
    msg = apply_perk(player, "hp")
    assert player.max_hp == old_hp + 8
    print(f"HP perk: {msg}")

    old_atk = player.atk
    msg = apply_perk(player, "atk")
    assert player.atk == old_atk + 2
    print(f"ATK perk: {msg}")

    print("Progression test passed")


if __name__ == "__main__":
    test_progression()
