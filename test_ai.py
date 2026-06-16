"""Тест ИИ-поведений."""

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
from entities.ai import choose_ai_action


def test_ai_types():
    state = GameState(seed=42, depth=3)
    state.generate_level()
    px, py = state.player.x, state.player.y

    # RANGED должен выбрать допустимое действие
    archer = Mob.from_data("skeleton_archer", px + 3, py)
    action, tx, ty = choose_ai_action(archer, state)
    print(f"Archer at ({archer.x},{archer.y}) vs player ({px},{py}): {action} -> ({tx},{ty})")
    assert action in ("ranged_attack", "move", "skip")

    # STATIONARY не двигается
    zombie = Mob.from_data("zombie", px + 5, py)
    action, tx, ty = choose_ai_action(zombie, state)
    print(f"Zombie far away: {action}")
    assert action == "skip"

    # COWARDLY при полном HP идёт в атаку
    snake = Mob.from_data("snake", px + 1, py)
    action, tx, ty = choose_ai_action(snake, state)
    print(f"Snake adjacent full HP: {action}")
    assert action == "attack"

    # COWARDLY при ранении убегает
    snake.hp = 1
    action, tx, ty = choose_ai_action(snake, state)
    print(f"Snake wounded (1 HP): {action} -> ({tx},{ty})")
    assert action == "move"

    # AGGRESSIVE атакует вблизи
    orc = Mob.from_data("orc", px + 1, py)
    action, tx, ty = choose_ai_action(orc, state)
    print(f"Orc adjacent: {action} -> ({tx},{ty})")
    assert action == "attack"

    print("AI test passed")


if __name__ == "__main__":
    test_ai_types()
