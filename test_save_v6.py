"""Тест сохранений версии 6 (биом, hazards, traps)."""

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
from systems.save import save_game, load_game


def test_save_v6():
    # Генерируем обычный уровень с фиксированным биомом для проверки round-trip v7
    from world.dungeon import generate_dungeon
    state = GameState(seed=42, depth=11)
    state.dungeon = generate_dungeon(depth=11, biome_id="hell_forge", rng=state.rng)
    assert state.dungeon.biome_id == "hell_forge"
    assert len(state.dungeon.hazards) > 0
    assert len(state.dungeon.traps) > 0

    # Reveal one trap
    some_trap_pos = next(iter(state.dungeon.traps.keys()))
    state.dungeon.revealed_traps.add(some_trap_pos)

    assert save_game(state, "test_v6")
    loaded = load_game("test_v6")
    assert loaded is not None
    assert loaded.dungeon.biome_id == state.dungeon.biome_id
    assert loaded.dungeon.hazards == state.dungeon.hazards
    assert loaded.dungeon.traps == state.dungeon.traps
    assert loaded.dungeon.revealed_traps == state.dungeon.revealed_traps
    print("Save/load v6 OK")


if __name__ == "__main__":
    test_save_v6()
    print("All save v6 tests passed")
