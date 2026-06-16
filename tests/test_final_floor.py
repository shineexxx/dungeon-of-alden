"""Тесты финального этажа и босса (headless)."""

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
from world.final_floor import FINAL_DEPTH, generate_final_floor


def test_final_floor_generation():
    state = GameState(seed=42, depth=FINAL_DEPTH)
    dungeon = generate_final_floor(state, state.rng)
    assert dungeon.biome_id == "final_floor"
    assert len(dungeon.floor_positions()) > 50
    print("Final floor generation OK")


def test_boss_spawn():
    state = GameState(seed=42, depth=FINAL_DEPTH)
    generate_final_floor(state, state.rng)
    bosses = [m for m in state.mobs if m.id == "dark_lord"]
    assert len(bosses) == 1
    boss = bosses[0]
    assert boss.hp == 200
    assert boss.alive
    print("Boss spawn OK")


def test_boss_once():
    state = GameState(seed=42, depth=FINAL_DEPTH)
    generate_final_floor(state, state.rng)
    count_first = len([m for m in state.mobs if m.id == "dark_lord"])
    generate_final_floor(state, state.rng)
    count_second = len([m for m in state.mobs if m.id == "dark_lord"])
    assert count_first == count_second == 1
    print("Boss spawn once OK")


if __name__ == "__main__":
    test_final_floor_generation()
    test_boss_spawn()
    test_boss_once()
    print("All final floor tests passed")
