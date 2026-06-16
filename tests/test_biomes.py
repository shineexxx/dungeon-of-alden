"""Тест биомов и фильтрации контента по тегам."""

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

from content.biomes import biome_for_depth, get_biome
from content.monsters import monsters_for_biome
from content.items import items_for_biome


def test_biome_for_depth():
    for depth in [1, 2, 3]:
        b = biome_for_depth(depth)
        assert b["id"] == "dungeon", f"Expected dungeon at {depth}, got {b['id']}"
    for depth in [4, 5, 6]:
        b = biome_for_depth(depth)
        assert b["id"] == "caves", f"Expected caves at {depth}, got {b['id']}"
    for depth in [11, 12, 13]:
        b = biome_for_depth(depth)
        assert b["id"] == "hell_forge", f"Expected hell_forge at {depth}, got {b['id']}"
    print("Biome for depth OK")


def test_monsters_for_biome():
    dungeon_mobs = monsters_for_biome(["dungeon"], 2)
    assert "goblin" in dungeon_mobs
    cave_mobs = monsters_for_biome(["cave"], 4)
    assert "bat" in cave_mobs or "troglodyte" in cave_mobs
    hell_mobs = monsters_for_biome(["hell"], 12)
    assert "demon" in hell_mobs or "fire_elemental" in hell_mobs
    print("Monsters for biome OK")


def test_items_for_biome():
    dungeon_items = items_for_biome(["dungeon"], 2)
    assert len(dungeon_items) > 0
    hell_items = items_for_biome(["hell", "fire_themed"], 12)
    assert len(hell_items) > 0
    print("Items for biome OK")


if __name__ == "__main__":
    test_biome_for_depth()
    test_monsters_for_biome()
    test_items_for_biome()
    print("All biome tests passed")
