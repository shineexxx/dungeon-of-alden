"""Тест системы опознания."""

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

import random
from systems.game_state import GameState
from systems.identification import get_display_name, identify_item, is_identified


def test_identification():
    state = GameState(seed=42, depth=1)
    state.generate_level()

    # Зелья неопознанны изначально
    assert not is_identified(state, "potion_healing")
    name1 = get_display_name(state, "potion_healing")
    name2 = get_display_name(state, "potion_healing")
    assert name1 == name2
    assert "зелье" in name1
    print(f"Healing potion display name: {name1}")

    # Свитки тоже неопознанны
    scroll_name = get_display_name(state, "scroll_identify")
    assert "свиток" in scroll_name
    print(f"Identify scroll display name: {scroll_name}")

    # Еда опознана сразу
    food_name = get_display_name(state, "bread")
    assert food_name == "краюха хлеба"
    print(f"Bread display name: {food_name}")

    # Опознаём зелье
    msg = identify_item(state, "potion_healing")
    print(msg)
    assert is_identified(state, "potion_healing")
    assert get_display_name(state, "potion_healing") == "зелье лечения"

    print("Identification test passed")


if __name__ == "__main__":
    test_identification()
