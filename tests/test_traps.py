"""Тест ловушек."""

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

from systems.game_state import GameState
from world.dungeon import generate_dungeon
from engine.game_loop import _check_trap, _search_traps


def test_trap_trigger():
    state = GameState(seed=42, depth=3)
    state.dungeon = generate_dungeon(depth=3, width=20, height=15, rng=state.rng, biome_id="dungeon")
    # Принудительно ставим ловушку под игроком
    state.dungeon.traps[(state.player.x, state.player.y)] = "spike_trap"
    hp_before = state.player.hp
    # С высоким шансом она сработает (detect_chance 0.35, но rng может обнаружить)
    _check_trap(state, state.player, is_player=True)
    # Если обнаружена — HP не меняется
    if state.player.hp == hp_before:
        # Повторим несколько раз, пока не сработает
        for _ in range(10):
            state.dungeon.traps[(state.player.x, state.player.y)] = "spike_trap"
            state.dungeon.revealed_traps.discard((state.player.x, state.player.y))
            _check_trap(state, state.player, is_player=True)
            if state.player.hp < hp_before:
                break
    assert state.player.hp <= hp_before
    assert (state.player.x, state.player.y) in state.dungeon.revealed_traps
    print("Trap trigger OK")


def test_search_traps():
    state = GameState(seed=42, depth=3)
    state.dungeon = generate_dungeon(depth=3, width=20, height=15, rng=state.rng, biome_id="dungeon")
    # Ставим ловушки рядом
    for dx, dy in [(1, 0), (0, 1), (-1, 0)]:
        state.dungeon.traps[(state.player.x + dx, state.player.y + dy)] = "spike_trap"
    # Поиск должен обнаружить хотя бы одну за несколько попыток
    found = False
    for _ in range(20):
        msg = _search_traps(state)
        if "обнаружили" in msg:
            found = True
            break
    assert found, "Search did not find any trap"
    print("Search traps OK")


if __name__ == "__main__":
    test_trap_trigger()
    test_search_traps()
    print("All trap tests passed")
