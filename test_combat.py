"""Тест боя headless."""

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
from entities.mob import Mob
from engine.fov import compute_fov
from engine.game_loop import _try_move, _after_player_turn
from systems.stats import recalculate_stats


def test_combat():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    recalculate_stats(state.player)
    # Ставим моба рядом с игроком
    mob = Mob.from_data("rat", state.player.x + 1, state.player.y)
    state.mobs = [mob]
    compute_fov(state.dungeon, state.player.x, state.player.y, state.player.fov_radius)

    print(f"Player: ({state.player.x},{state.player.y}) HP:{state.player.hp} ATK:{state.player.atk}")
    print(f"Rat: ({mob.x},{mob.y}) HP:{mob.hp} AI:{mob.ai} speed:{mob.speed}")

    # Игрок бьёт моба
    _try_move(state, 1, 0)
    print(f"After player attacks rat: rat HP {mob.hp}, alive {mob.alive}")

    # Моб бьёт игрока (если жив)
    if mob.alive:
        _after_player_turn(state)
        print(f"After rat turn: player HP {state.player.hp}")

    print(f"Final: player HP {state.player.hp}, rat alive {mob.alive}, xp {state.player.xp}, gold {state.player.gold}")
    print("Combat test passed")


if __name__ == "__main__":
    test_combat()
