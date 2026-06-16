"""Тест генераторов подземелий."""

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

from world.dungeon import generate_dungeon, place_player, place_entities
from systems.game_state import GameState
from content.biomes import BIOMES


def _has_path(dungeon, start, goal):
    """BFS проверка связности."""
    from collections import deque
    visited = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        if (x, y) == goal:
            return True
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if dungeon.in_bounds(nx, ny) and not dungeon.blocks_movement(nx, ny) and (nx, ny) not in visited:
                visited.add((nx, ny))
                q.append((nx, ny))
    return False


def test_generator(biome_id, depth):
    from content.biomes import get_biome
    biome = get_biome(biome_id)
    state = GameState(seed=42, depth=depth)
    dungeon = generate_dungeon(depth=depth, width=40, height=20, rng=state.rng, biome_id=biome_id)
    assert dungeon.biome_id == biome_id
    floors = dungeon.floor_positions()
    assert len(floors) > 20, f"{biome_id}: too few floors"
    start = place_player(dungeon, state.rng)
    goal = dungeon.stairs
    assert dungeon.is_floor(start[0], start[1]), f"{biome_id}: player not on floor"
    assert dungeon.is_floor(goal[0], goal[1]), f"{biome_id}: stairs not on floor"
    assert _has_path(dungeon, start, goal), f"{biome_id}: no path from start to stairs"
    state.dungeon = dungeon
    state.player.x, state.player.y = start
    mobs, items = place_entities(dungeon, state, state.rng)
    print(f"{biome_id}: floors={len(floors)}, mobs={len(mobs)}, items={len(items)}")


def test_all_generators():
    for biome_id, biome in BIOMES.items():
        depth = biome["depth_range"][0]
        test_generator(biome_id, depth)
    print("All generators OK")


if __name__ == "__main__":
    test_all_generators()
