"""Базовые тесты без curses (headless)."""

import os
import sys

# Подавляем curses, чтобы протестировать логику
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
from systems.save import load_game, save_game, list_slots
from systems.stats import recalculate_stats


def test_generate_and_save():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    assert state.dungeon.width > 0
    assert state.player.x > 0
    assert len(state.mobs) >= 0
    assert state.player.fov_radius == 8
    assert state.identification
    print("Dungeon generated ok")

    recalculate_stats(state.player)
    assert state.player.max_hp == 30
    print("Stats recalculated ok")

    # Save / load roundtrip
    assert save_game(state, "test_slot")
    loaded = load_game("test_slot")
    assert loaded is not None
    assert loaded.depth == state.depth
    assert loaded.player.x == state.player.x
    assert loaded.player.fov_radius == state.player.fov_radius
    assert loaded.player.speed == state.player.speed
    assert len(loaded.mobs) == len(state.mobs)
    assert loaded.identification
    print("Save/load roundtrip ok")

    # Cleanup
    os.remove("saves/test_slot.json")
    print("Test passed")


if __name__ == "__main__":
    test_generate_and_save()
