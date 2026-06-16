"""Тест выброса предметов."""

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
from systems.inventory import InventoryUI


class FakeWindow:
    """Заглушка curses-окна для теста."""

    def __init__(self):
        self.keys = []
        self.calls = []

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


def test_drop_item():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    state.player.inventory["potion_healing"] = 2
    x, y = state.player.x, state.player.y

    stdscr = FakeWindow()
    # d — выбросить, q — выйти
    stdscr.keys = [ord("d"), ord("q")]
    ui = InventoryUI(stdscr, state.player, state)
    ui.run()

    assert state.player.inventory.get("potion_healing", 0) == 1
    assert (x, y) in state.items_on_floor
    assert "potion_healing" in state.items_on_floor[(x, y)]
    print("Drop item OK")


if __name__ == "__main__":
    test_drop_item()
    print("All drop tests passed")
