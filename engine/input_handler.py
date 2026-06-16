"""Обработка ввода с клавиатуры."""

from __future__ import annotations

import curses
from typing import NamedTuple


class Action(NamedTuple):
    type: str
    data: dict | None = None


MOVEMENT_KEYS: dict[int, tuple[int, int]] = {
    ord("w"): (0, -1),
    ord("W"): (0, -1),
    curses.KEY_UP: (0, -1),
    ord("s"): (0, 1),
    ord("S"): (0, 1),
    curses.KEY_DOWN: (0, 1),
    ord("a"): (-1, 0),
    ord("A"): (-1, 0),
    curses.KEY_LEFT: (-1, 0),
    ord("d"): (1, 0),
    ord("D"): (1, 0),
    curses.KEY_RIGHT: (1, 0),
    # Диагонали (пока заблокированы, но можно расширить)
}


def get_action(key: int) -> Action:
    """Преобразовать код клавиши в действие."""
    if key in MOVEMENT_KEYS:
        return Action("move", {"dx": MOVEMENT_KEYS[key][0], "dy": MOVEMENT_KEYS[key][1]})
    if key == ord("g") or key == ord("G"):
        return Action("pickup")
    if key == ord("s") or key == ord("S"):
        return Action("search")
    if key == ord("i") or key == ord("I"):
        return Action("inventory")
    if key == ord("z") or key == ord("Z"):
        return Action("cast")
    if key == ord("b") or key == ord("B"):
        return Action("spellbook")
    if key == ord("t") or key == ord("T") or key == ord("e") or key == ord("E"):
        return Action("interact")
    if key == ord("j") or key == ord("J"):
        return Action("journal")
    if key == ord(" ") or key == 13:  # пробел / enter
        return Action("use_stairs")
    if key == 27:  # Esc
        return Action("menu")
    if key == ord("q") or key == ord("Q"):
        return Action("quit")
    return Action("unknown")
