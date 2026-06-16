"""Тест эффектов предметов."""

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
from systems.effects import apply_effect
from systems.stats import recalculate_stats


def test_effects():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    recalculate_stats(state.player)

    # Лечение
    state.player.hp = 10
    msg = apply_effect("heal", state.player, state, (8, 15))
    print(msg)
    assert state.player.hp > 10

    # Опыт
    old_level = state.player.level
    msg = apply_effect("experience", state.player, state, 50)
    print(msg)
    assert state.player.level > old_level or state.player.xp > 0

    # Еда
    state.player.satiety = 50
    msg = apply_effect("food", state.player, state, 30)
    print(msg)
    assert state.player.satiety == 80

    # Карта
    msg = apply_effect("mapping", state.player, state, None)
    print(msg)
    assert all(state.dungeon.explored[y][x] for y in range(state.dungeon.height) for x in range(state.dungeon.width))

    print("Effects test passed")


if __name__ == "__main__":
    test_effects()
