"""Тесты NPC и торговли (headless)."""

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

from entities.npcs import create_npc
from entities.player import Player


def test_create_npc():
    npc = create_npc("merchant", 10, 10)
    assert npc.id == "merchant"
    assert npc.x == 10
    assert npc.y == 10
    assert npc.shop_items
    print("NPC creation OK")


def test_npc_prices():
    npc = create_npc("merchant", 0, 0)
    player = Player(0, 0, gold=100)
    price = npc.get_price("potion_healing", buying=True)
    assert price > 0
    sell_price = npc.get_price("potion_healing", buying=False)
    assert sell_price < price
    print("NPC prices OK")


def test_npc_trade_logic():
    npc = create_npc("merchant", 0, 0)
    player = Player(0, 0, gold=100)
    item_id = npc.shop_items[0]
    price = npc.get_price(item_id, buying=True)
    player.gold -= price
    player.inventory[item_id] = player.inventory.get(item_id, 0) + 1
    assert player.gold == 100 - price
    assert player.inventory[item_id] == 1
    print("NPC trade logic OK")


if __name__ == "__main__":
    test_create_npc()
    test_npc_prices()
    test_npc_trade_logic()
    print("All NPC tests passed")
