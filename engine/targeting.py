"""Таргетинг для заклинаний: выбор цели и подсветка AoE."""

from __future__ import annotations

import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from curses import _CursesWindow
    from systems.game_state import GameState


def get_affected_positions(tx: int, ty: int, target_type: str, aoe_radius: int, player_pos: tuple[int, int]) -> list[tuple[int, int]]:
    """Вернуть список клеток, затронутых заклинанием."""
    positions = []
    if target_type == "aoe":
        for y in range(ty - aoe_radius, ty + aoe_radius + 1):
            for x in range(tx - aoe_radius, tx + aoe_radius + 1):
                positions.append((x, y))
    elif target_type == "single":
        positions = [(tx, ty)]
    elif target_type == "line":
        # Линия от игрока к цели
        px, py = player_pos
        positions = _line_positions(px, py, tx, ty)
    elif target_type == "cone":
        # Конус 3 клетки от игрока в направлении цели
        positions = _cone_positions(player_pos, tx, ty)
    return positions


def _line_positions(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """Брезенхем: точки на линии."""
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        points.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return points


def _cone_positions(player_pos: tuple[int, int], tx: int, ty: int) -> list[tuple[int, int]]:
    """Конус длиной 3 клетки в направлении от игрока к цели."""
    px, py = player_pos
    dx = tx - px
    dy = ty - py
    # Определяем направление
    if abs(dx) >= abs(dy):
        step_x = 1 if dx >= 0 else -1
        step_y = 0 if dx != 0 else (1 if dy >= 0 else -1)
    else:
        step_x = 0 if dy != 0 else (1 if dx >= 0 else -1)
        step_y = 1 if dy >= 0 else -1

    positions = []
    for dist in range(1, 4):
        cx = px + step_x * dist
        cy = py + step_y * dist
        positions.append((cx, cy))
        # Расширяем конус
        if step_x == 0:
            positions.append((cx + 1, cy))
            positions.append((cx - 1, cy))
        elif step_y == 0:
            positions.append((cx, cy + 1))
            positions.append((cx, cy - 1))
        else:
            positions.append((cx, cy))
    return list(set(positions))


def get_visible_mobs(state: "GameState") -> list:
    """Вернуть список видимых живых мобов."""
    return [m for m in state.mobs if m.alive and state.dungeon.visible[m.y][m.x]]


def select_target(stdscr: "_CursesWindow", state: "GameState", spell: dict) -> tuple[int, int] | None:
    """Позволить игроку выбрать цель заклинания. Возвращает (x, y) или None."""
    from engine.render import render_map

    px, py = state.player.x, state.player.y
    cx, cy = px, py
    range_limit = spell["range"]
    target_type = spell["target_type"]
    aoe_radius = spell.get("aoe_radius", 0)

    visible_mobs = get_visible_mobs(state)
    mob_index = -1

    while True:
        # Отрисовка карты с курсором
        stdscr.clear()
        affected = get_affected_positions(cx, cy, target_type, aoe_radius, (px, py))
        _render_targeting(stdscr, state, cx, cy, affected)

        help_text = "WASD/стрелки — курсор, Tab — монстр, Enter — каст, Esc — отмена"
        try:
            stdscr.addstr(0, 0, help_text[: stdscr.getmaxyx()[1] - 1], curses.color_pair(9))
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27,):
            return None
        if key in (10, 13, curses.KEY_ENTER):
            # Проверяем дальность
            if abs(cx - px) + abs(cy - py) <= range_limit or (cx == px and cy == py):
                return (cx, cy)
        if key == ord("\t"):
            if visible_mobs:
                mob_index = (mob_index + 1) % len(visible_mobs)
                cx, cy = visible_mobs[mob_index].x, visible_mobs[mob_index].y
        elif key in (curses.KEY_UP, ord("w"), ord("W")):
            cy = max(0, cy - 1)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
            cy = min(state.dungeon.height - 1, cy + 1)
        elif key in (curses.KEY_LEFT, ord("a"), ord("A")):
            cx = max(0, cx - 1)
        elif key in (curses.KEY_RIGHT, ord("d"), ord("D")):
            cx = min(state.dungeon.width - 1, cx + 1)


def _render_targeting(stdscr: "_CursesWindow", state: "GameState", cx: int, cy: int, affected: list[tuple[int, int]]) -> None:
    """Отрисовать карту с курсором и зоной поражения."""
    height, width = stdscr.getmaxyx()
    dungeon = state.dungeon
    map_top = 1

    affected_set = set(affected)

    for y in range(dungeon.height):
        if map_top + y >= height - 3:
            break
        for x in range(dungeon.width):
            if x >= width - 1:
                break
            tile = dungeon.tiles[y][x]
            visible = dungeon.visible[y][x]
            explored = dungeon.explored[y][x]

            char = " "
            attr = curses.color_pair(5)
            if visible or explored:
                char = tile["char"]
                attr = curses.color_pair(tile["color_visible"] if visible else tile["color_fog"])

            if (x, y) == dungeon.stairs and (visible or explored):
                char = ">"
                attr = curses.color_pair(8)

            # Мобы
            if visible:
                for mob in state.mobs:
                    if mob.alive and mob.x == x and mob.y == y:
                        char = mob.char
                        attr = curses.color_pair(mob.color_pair)

            # Игрок
            if state.player.x == x and state.player.y == y:
                char = "@"
                attr = curses.color_pair(1)

            # Подсветка зоны поражения
            if (x, y) in affected_set and (visible or explored):
                attr = curses.color_pair(6)  # красная подсветка

            # Курсор
            if x == cx and y == cy:
                char = "X"
                attr = curses.color_pair(9)

            try:
                stdscr.addch(map_top + y, x, char, attr)
            except curses.error:
                pass
