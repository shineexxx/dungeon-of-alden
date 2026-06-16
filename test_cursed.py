"""Тест проклятых предметов."""

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

from systems.inventory import InventoryUI
from entities.player import Player


def test_cursed():
    player = Player(0, 0)

    class FakeScr:
        def getmaxyx(self):
            return (24, 80)

    # Фейковый game_state с пустой идентификацией
    class FakeState:
        identification = {"potion": {}, "scroll": {}, "identified": set()}

    ui = InventoryUI(FakeScr(), player, FakeState())
    assert ui._is_cursed("cursed_blade") is True
    assert ui._is_cursed("short_sword") is False
    assert ui._is_cursed("cursed_plate") is True
    assert ui._is_cursed("leather_armor") is False
    assert ui._is_cursed("cursed_ring") is True
    assert ui._is_cursed("ring_of_health") is False
    print("Cursed detection test passed")


if __name__ == "__main__":
    test_cursed()
