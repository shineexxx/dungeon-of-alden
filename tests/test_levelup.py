"""Тест цикла level-up."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
from systems.progression import add_xp, apply_perk, get_level_up_choices
import random


def test_level_up_flow():
    player = Player(0, 0)
    rng = random.Random(42)

    # Даём XP на 2 уровня сразу
    add_xp(player, 90)  # 20 + 40 + остаток 30
    assert player.level == 3
    assert player.xp == 30
    print(f"Player level {player.level}, xp {player.xp}/{player.xp_to_next()}")

    # Проверяем выбор перков
    choices = get_level_up_choices(rng)
    assert len(choices) == 3
    print(f"Level-up choices: {[c.name for c in choices]}")

    # Применяем первый перк
    msg = apply_perk(player, choices[0].key)
    print(f"Applied: {msg}")

    print("Level-up test passed")


if __name__ == "__main__":
    test_level_up_flow()
