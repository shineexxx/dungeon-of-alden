"""Тесты эффектов событий (headless)."""

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
from systems.interactables import apply_event_effect


def test_fountain_heal():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    state.player.hp = 10
    event = {"id": "fountain_clean", "name": "Чистый фонтан"}
    choice = {"effect": "fountain_heal"}
    msg = apply_event_effect("fountain_heal", state, choice, event)
    assert state.player.hp == state.player.max_hp
    assert "исцеляет" in msg
    print("Fountain heal OK")


def test_altar_blood_sacrifice():
    state = GameState(seed=42, depth=3)
    state.generate_level()
    initial_atk = state.player.atk
    event = {"id": "altar_blood", "name": "Кровавый алтарь"}
    choice = {"effect": "altar_blood_sacrifice"}
    msg = apply_event_effect("altar_blood_sacrifice", state, choice, event)
    assert state.player.atk == initial_atk + 2
    print("Altar blood sacrifice OK")


def test_lore_read():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    event = {"id": "lore_wall", "name": "Древняя надпись"}
    choice = {"effect": "lore_read"}
    msg = apply_event_effect("lore_read", state, choice, event)
    assert len(state.journal.lore_fragments) > 0 or "стёрты" in msg
    print("Lore read OK")


if __name__ == "__main__":
    test_fountain_heal()
    test_altar_blood_sacrifice()
    test_lore_read()
    print("All event tests passed")
