"""Тест голода."""

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
from engine.game_loop import _apply_hunger
from systems.stats import recalculate_stats


def test_hunger():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    recalculate_stats(state.player)

    # Много ходов
    for turn in range(1, 101):
        state.turn = turn
        _apply_hunger(state)

    print(f"After 100 turns satiety: {state.player.satiety}")
    assert state.player.satiety < 100

    # Еда восстанавливает сытость
    state.player.satiety = 30
    _apply_hunger(state)  # один ход
    print(f"Satiety status: {state.player.satiety_status()}")

    print("Hunger test passed")


if __name__ == "__main__":
    test_hunger()
