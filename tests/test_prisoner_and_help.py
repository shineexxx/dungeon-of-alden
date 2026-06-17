"""Тест пленника, подсказки предмета под ногами и справки."""

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
from entities.npcs import create_npc, prisoner_ui


class FakeWindow:
    def __init__(self, keys):
        self.keys = list(keys)

    def getch(self):
        return self.keys.pop(0) if self.keys else 27

    def clear(self):
        pass

    def refresh(self):
        pass

    def addstr(self, *args, **kwargs):
        pass

    def addch(self, *args, **kwargs):
        pass

    def hline(self, *args, **kwargs):
        pass

    def getmaxyx(self):
        return (30, 80)

    def attron(self, *args):
        pass

    def attroff(self, *args):
        pass


def test_prisoner_no_key():
    state = GameState(seed=42, depth=3)
    state.generate_level()
    npc = create_npc("prisoner", state.player.x, state.player.y, state.rng)
    state.npcs.append(npc)

    stdscr = FakeWindow([10, 27])
    msg = prisoner_ui(stdscr, state, npc)

    assert npc in state.npcs
    assert "нужен ключ" in msg
    print("Prisoner no key OK")


def test_prisoner_free():
    state = GameState(seed=42, depth=3)
    state.generate_level()
    npc = create_npc("prisoner", state.player.x, state.player.y, state.rng)
    state.npcs.append(npc)
    state.player.inventory["prisoner_key"] = 1

    # Enter выбирает первый вариант (освободить), затем Esc
    stdscr = FakeWindow([10, 27])
    msg = prisoner_ui(stdscr, state, npc)

    assert npc not in state.npcs
    assert "prisoner_key" not in state.player.inventory
    assert "освободили" in msg
    print("Prisoner free OK")


def test_floor_hint():
    from engine.render import _floor_item_hint
    state = GameState(seed=42, depth=1)
    state.generate_level()
    state.items_on_floor[(state.player.x, state.player.y)] = ["short_sword"]
    hint = _floor_item_hint(state, state.player)
    assert "короткий меч" in hint
    print("Floor hint OK")


def test_help_import():
    from engine.help import SECTIONS, show_help
    assert len(SECTIONS) > 0
    print("Help import OK")


def test_prisoner_key_spawned():
    from world.special_rooms import place_special_rooms
    state = GameState(seed=42, depth=3)
    state.generate_level()
    state.npcs = []
    state.dungeon.interactables = {}
    place_special_rooms(state.dungeon, state, state.rng)
    has_prisoner = any(npc.id == "prisoner" for npc in state.npcs)
    if has_prisoner:
        keys_on_floor = sum(
            1 for items in state.items_on_floor.values() for iid in items if iid == "prisoner_key"
        )
        assert keys_on_floor == 1, "Key should spawn on the same floor as prisoner"
    print("Prisoner key spawn OK")


if __name__ == "__main__":
    test_prisoner_no_key()
    test_prisoner_free()
    test_floor_hint()
    test_help_import()
    test_prisoner_key_spawned()
    print("All prisoner/help tests passed")
