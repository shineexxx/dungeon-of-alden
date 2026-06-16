"""Тесты спецкомнат и событий (headless)."""

import sys

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
from world.special_rooms import place_special_rooms


def test_special_rooms_placement():
    state = GameState(seed=42, depth=5)
    state.generate_level()
    before = len(state.dungeon.rooms)
    place_special_rooms(state.dungeon, state, state.rng)
    after = len(state.dungeon.rooms)
    assert after >= before, "Special rooms should add rooms"
    assert state.dungeon.interactables, "Should place interactables"
    print(f"Special rooms placed: {after - before}")


def test_event_registry():
    from content.events import EVENTS
    from systems.interactables import EVENT_EFFECTS

    for event_id, event in EVENTS.items():
        for choice in event.get("choices", []):
            effect = choice.get("effect")
            if effect is not None:
                assert effect in EVENT_EFFECTS, f"Missing effect: {effect}"
    print("Event effects registry OK")


if __name__ == "__main__":
    test_special_rooms_placement()
    test_event_registry()
    print("All special room tests passed")
