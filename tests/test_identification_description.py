"""Тест неопознанных описаний и подсказки предмета под ногами."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
from systems.identification import get_description, is_identified
from engine.render import _floor_item_hint


def test_unidentified_description():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    assert not is_identified(state, "potion_healing")
    desc = get_description(state, "potion_healing")
    assert "неизвестного" in desc.lower() or "неизвестным" in desc.lower()
    print("Unidentified description OK")


def test_identified_description():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    from systems.identification import identify_item
    identify_item(state, "potion_healing")
    desc = get_description(state, "potion_healing")
    assert "Восстанавливает" in desc
    print("Identified description OK")


def test_floor_hint_multiple():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    state.items_on_floor[(state.player.x, state.player.y)] = ["short_sword", "potion_healing"]
    hint = _floor_item_hint(state, state.player)
    assert "короткий меч" in hint
    assert "зелье" in hint
    print("Floor hint multiple OK")


if __name__ == "__main__":
    test_unidentified_description()
    test_identified_description()
    test_floor_hint_multiple()
    print("All identification description tests passed")
