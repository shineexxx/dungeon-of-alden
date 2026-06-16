"""Тест спуска по лестнице."""

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

from systems.game_state import GameState
from engine.game_loop import _descend
from systems.stats import recalculate_stats
import json


def test_descend():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    recalculate_stats(state.player)
    sx, sy = state.dungeon.stairs
    state.player.x = sx
    state.player.y = sy

    _descend(state)

    assert state.depth == 2
    assert state.dungeon.stairs != (sx, sy)
    assert len(state.log) >= 2
    print(f"Descended to depth {state.depth}, new stairs {state.dungeon.stairs}")

    # Проверим, что autosave создался
    d = json.load(open("saves/autosave.json"))
    assert d["depth"] == 2
    print("Autosave after descend ok")


if __name__ == "__main__":
    test_descend()
