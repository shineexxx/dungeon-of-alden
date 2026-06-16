"""Тест полного цикла боя с лутом и опытом."""

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
from entities.mob import Mob
from engine.fov import compute_fov
from engine.game_loop import _try_move, _after_player_turn
from systems.stats import recalculate_stats


def test_kill_and_loot():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    recalculate_stats(state.player)
    # Ставим гоблина вплотную (у него есть шанс лута)
    mob = Mob.from_data("goblin", state.player.x + 1, state.player.y)
    state.mobs = [mob]
    compute_fov(state.dungeon, state.player.x, state.player.y, state.player.fov_radius)

    initial_xp = state.player.xp
    initial_gold = state.player.gold

    # Бьём до смерти (гоблин тоже будет бить в ответ)
    for _ in range(20):
        if not mob.alive:
            break
        _try_move(state, 1 if mob.x > state.player.x else (-1 if mob.x < state.player.x else 0),
                        1 if mob.y > state.player.y else (-1 if mob.y < state.player.y else 0))
        _after_player_turn(state)
        if not state.player.is_alive():
            break

    assert mob.alive is False, "Mob should be dead"
    assert state.player.xp > initial_xp, "Should gain XP"
    assert state.player.gold >= initial_gold, "Should gain gold"
    print(f"Items on mob cell: {state.items_on_floor.get((mob.x, mob.y), [])}")
    print("Full combat test passed")


if __name__ == "__main__":
    test_kill_and_loot()
