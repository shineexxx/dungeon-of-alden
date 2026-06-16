"""Тест опасностей (hazards)."""

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

from systems.game_state import GameState
from world.dungeon import generate_dungeon
from engine.game_loop import _apply_hazard_to_player


def test_lava_damage():
    state = GameState(seed=42, depth=12)
    state.dungeon = generate_dungeon(depth=12, width=20, height=15, rng=state.rng, biome_id="hell_forge")
    # Найти клетку лавы
    lava_pos = next(((x, y) for (x, y), hid in state.dungeon.hazards.items() if hid == "lava"), None)
    assert lava_pos, "No lava generated"
    assert state.dungeon.blocks_movement(lava_pos[0], lava_pos[1]), "Lava should block movement"
    print("Lava hazard OK")


def test_water_slow():
    state = GameState(seed=42, depth=7)
    state.dungeon = generate_dungeon(depth=7, width=20, height=15, rng=state.rng, biome_id="crypt")
    water_pos = next(((x, y) for (x, y), hid in state.dungeon.hazards.items() if hid == "water"), None)
    if water_pos:
        state.player.x, state.player.y = water_pos
        _apply_hazard_to_player(state, "water")
        assert state.player.status_effects.get("slowed", 0) > 0
        print("Water slow OK")
    else:
        print("No water generated (ok)")


def test_spikes_damage():
    state = GameState(seed=42, depth=7)
    state.dungeon = generate_dungeon(depth=7, width=20, height=15, rng=state.rng, biome_id="crypt")
    hp_before = state.player.hp
    state.dungeon.hazards[(state.player.x, state.player.y)] = "spikes"
    _apply_hazard_to_player(state, "spikes")
    assert state.player.hp < hp_before
    print("Spikes damage OK")


if __name__ == "__main__":
    test_lava_damage()
    test_water_slow()
    test_spikes_damage()
    print("All hazard tests passed")
