"""Тест системы магии."""

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
from systems.magic import (
    can_cast,
    cast_spell,
    initialize_magic,
    learn_spell,
    tick_cooldowns,
)
from systems.effects import apply_effect
from systems.save import load_game, save_game
from content.spells import get_spell


def test_initial_spells():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    initialize_magic(state.player)
    assert "magic_missile" in state.player.known_spells
    assert "heal_spell" in state.player.known_spells
    print("Initial spells OK")


def test_mana_restore():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    initialize_magic(state.player)
    state.player.mana = 0
    apply_effect("restore_mana", state.player, state, (5, 10))
    assert state.player.mana > 0
    assert state.player.mana <= state.player.max_mana
    print("Mana restore OK")


def test_learn_spell():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    initialize_magic(state.player)
    msg = learn_spell(state.player, "fireball")
    assert "выучили" in msg
    assert "fireball" in state.player.known_spells
    msg2 = learn_spell(state.player, "fireball")
    assert "уже знаете" in msg2
    print("Learn spell OK")


def test_cast_heal():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    initialize_magic(state.player)
    state.player.hp = 5
    mana_before = state.player.mana
    msg = cast_spell(state.player, state, "heal_spell")
    assert state.player.hp > 5
    assert state.player.mana < mana_before
    print(f"Cast heal: {msg}")
    print("Cast heal OK")


def test_cooldown():
    state = GameState(seed=42, depth=1)
    state.generate_level()
    initialize_magic(state.player)
    cast_spell(state.player, state, "heal_spell")
    ok, reason = can_cast(state.player, "heal_spell")
    assert not ok
    assert "кулдауне" in reason
    tick_cooldowns(state.player)
    assert state.player.spell_cooldowns.get("heal_spell") == 1
    print("Cooldown OK")


def test_save_load_v5():
    state = GameState(seed=42, depth=2)
    state.generate_level()
    initialize_magic(state.player)
    learn_spell(state.player, "fireball")
    state.player.mana = 3
    state.player.spell_cooldowns["heal_spell"] = 2
    assert save_game(state, "test_magic_slot")
    loaded = load_game("test_magic_slot")
    assert loaded is not None
    assert loaded.player.max_mana == state.player.max_mana
    assert loaded.player.mana == 3
    assert "fireball" in loaded.player.known_spells
    assert loaded.player.spell_cooldowns.get("heal_spell") == 2
    print("Save/load v5 OK")


if __name__ == "__main__":
    test_initial_spells()
    test_mana_restore()
    test_learn_spell()
    test_cast_heal()
    test_cooldown()
    test_save_load_v5()
    print("All magic tests passed")
