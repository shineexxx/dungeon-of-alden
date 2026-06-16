"""Рендеринг и цветовая палитра curses."""

from __future__ import annotations

import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.dungeon import Dungeon
    from entities.player import Player
    from entities.mob import Mob
    from entities.npcs import NPC
    from systems.game_state import GameState


# Именованные цвета для data-driven контента.
# Используем ТОЛЬКО стандартные 8 цветов curses для совместимости.
COLOR_MAP: dict[str, int] = {
    "white": curses.COLOR_WHITE,
    "black": curses.COLOR_BLACK,
    "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN,
    "yellow": curses.COLOR_YELLOW,
    "blue": curses.COLOR_BLUE,
    "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_CYAN,
    "brown": curses.COLOR_YELLOW,      # fallback
    "dark_green": curses.COLOR_GREEN,  # fallback
    "grey": curses.COLOR_BLUE,         # fallback
    "orange": curses.COLOR_YELLOW,     # fallback
    "pink": curses.COLOR_MAGENTA,      # fallback
}

# Пары цветов curses (номер: (foreground, background))
# 0 - стандартная, 1 - игрок, 2 - видимая стена, 3 - видимый пол,
# 4 - туман стена, 5 - туман пол, 6 - мобы, 7 - предметы, 8 - лестница,
# 9 - меню/лог, 10 - HUD
COLOR_PAIRS: dict[int, tuple[int | str, int | str]] = {
    1: ("white", "black"),
    2: ("white", "black"),      # стена видимая
    3: ("grey", "black"),       # пол видимый
    4: ("blue", "black"),       # стена в тумане
    5: ("black", "black"),      # пол в тумане
    6: ("red", "black"),        # мобы
    7: ("yellow", "black"),     # предметы
    8: ("cyan", "black"),       # лестница
    9: ("white", "blue"),       # меню/выделение
    10: ("green", "black"),     # HUD
    11: ("brown", "black"),     # дерево/коричневое
    12: ("green", "black"),     # зелёное
    13: ("yellow", "black"),    # жёлтое
    14: ("dark_green", "black"),
    15: ("cyan", "black"),
    16: ("magenta", "black"),
    17: ("white", "black"),     # белое
}


def init_colors() -> None:
    """Инициализировать палитру curses."""
    try:
        curses.start_color()
        curses.use_default_colors()
    except curses.error:
        pass
    for pair_id, (fg_name, bg_name) in COLOR_PAIRS.items():
        fg = COLOR_MAP.get(fg_name, curses.COLOR_WHITE)
        bg = COLOR_MAP.get(bg_name, curses.COLOR_BLACK)
        try:
            curses.init_pair(pair_id, fg, bg)
        except (curses.error, ValueError):
            # Если терминал не поддерживает цвета - игра всё равно запустится
            pass


def color_attr(color_name: str | int) -> int:
    """Вернуть атрибут curses по имени цвета."""
    if isinstance(color_name, int):
        return curses.color_pair(color_name)
    return curses.color_pair(COLOR_MAP.get(color_name, curses.COLOR_WHITE))


def render_map(
    stdscr: "curses._CursesWindow",
    state: "GameState",
    player: "Player",
    dungeon: "Dungeon",
    mobs: list["Mob"],
    items_on_floor: dict[tuple[int, int], list[str]],
    log_lines: list[str],
    menu_mode: bool,
    menu_options: list[str],
    menu_selection: int,
    level_up_mode: bool = False,
) -> None:
    """Отрисовать всё игровое состояние."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    if height < 12 or width < 40:
        msg = "Terminal too small"
        try:
            stdscr.addstr(0, 0, msg[: width - 1])
        except curses.error:
            pass
        stdscr.refresh()
        return

    # Верхняя панель HUD
    xp_next = player.xp_to_next()
    satiety = player.satiety_status()
    status_icons = _status_icons(player)
    from content.biomes import get_biome
    biome = get_biome(state.dungeon.biome_id)
    biome_name = biome["name"] if biome else state.dungeon.biome_id
    hud = (
        f" HP:{player.hp}/{player.max_hp} | MP:{player.mana}/{player.max_mana} "
        f"| ATK:{player.atk} | DEF:{player.ac} | Lvl:{player.level} "
        f"| XP:{player.xp}/{xp_next} | Гл:{state.depth} {biome_name} | G:{player.gold} | Сыт:{satiety}{status_icons}"
    )
    stdscr.attron(curses.color_pair(10))
    stdscr.addstr(0, 0, hud[: width - 1])
    stdscr.attroff(curses.color_pair(10))

    # Область карты
    map_top = 1
    map_height = height - 4  # HUD + лог (3 строки) + разделитель

    # Отрисовка тайлов
    for y in range(dungeon.height):
        if map_top + y >= map_height + map_top:
            break
        for x in range(dungeon.width):
            if x >= width - 1:
                break
            tile = dungeon.tiles[y][x]
            visible = dungeon.visible[y][x]
            explored = dungeon.explored[y][x]

            if visible:
                char = tile["char"]
                attr = curses.color_pair(tile["color_visible"])
            elif explored:
                char = tile["char"]
                attr = curses.color_pair(tile["color_fog"])
            else:
                char = " "
                attr = curses.color_pair(5)

            # Рисуем лестницу поверх пола
            if (x, y) == dungeon.stairs and (visible or explored):
                char = ">"
                attr = curses.color_pair(8)

            # Рисуем hazard поверх пола (если виден или исследован)
            if (visible or explored) and (x, y) in dungeon.hazards:
                from world.hazards import get_hazard
                hazard = get_hazard(dungeon.hazards[(x, y)])
                if hazard:
                    char = hazard["char"]
                    attr = color_attr(hazard["color"])

            # Рисуем revealed traps
            if visible and (x, y) in dungeon.revealed_traps and (x, y) in dungeon.traps:
                from world.traps import get_trap
                trap = get_trap(dungeon.traps[(x, y)])
                if trap:
                    char = trap["char_revealed"]
                    attr = color_attr(trap["color_revealed"])

            # Рисуем предметы (если видимы)
            if visible and (x, y) in items_on_floor and items_on_floor[(x, y)]:
                item_id = items_on_floor[(x, y)][0]
                from content.items import get_item
                item_data = get_item(item_id)
                if item_data:
                    char = item_data["char"]
                    attr = curses.color_pair(7)

            # Рисуем интерактивные объекты спецкомнат (если видимы)
            if visible and (x, y) in dungeon.interactables:
                interact = dungeon.interactables[(x, y)]
                if not interact.get("used", False):
                    from systems.interactables import get_interactable
                    it_data = get_interactable(interact.get("interactable_id", ""))
                    if it_data:
                        char = it_data["char"]
                        attr = color_attr(it_data["color"])

            # Рисуем NPC (если видимы) — поверх предметов
            if visible:
                for npc in state.npcs:
                    if npc.x == x and npc.y == y:
                        char = npc.char
                        attr = color_attr(npc.color)
                        break

            # Рисуем мобов (если видимы) — поверх NPC
            if visible:
                for mob in mobs:
                    if mob.x == x and mob.y == y and mob.alive:
                        char = mob.char
                        attr = curses.color_pair(mob.color_pair)
                        break

            # Игрок всегда поверх
            if player.x == x and player.y == y:
                char = "@"
                attr = curses.color_pair(1)

            try:
                stdscr.addch(map_top + y, x, char, attr)
            except curses.error:
                pass

    # Лог событий внизу экрана
    log_y_start = height - 3
    stdscr.hline(log_y_start - 1, 0, curses.ACS_HLINE, width - 1)
    for i, line in enumerate(log_lines[-3:]):
        try:
            stdscr.addstr(log_y_start + i, 0, line[: width - 1])
        except curses.error:
            pass

    # Меню Esc (не рисуем, если показывается level-up меню — оно само всё рисует)
    if menu_mode and not level_up_mode:
        _render_menu(stdscr, menu_options, menu_selection)

    stdscr.refresh()


def _status_icons(player: "Player") -> str:
    """Вернуть строку иконок активных статус-эффектов."""
    from systems.effects import STATUS_DEFINITIONS

    if not player.status_effects:
        return ""
    icons = []
    for status_id in player.status_effects:
        definition = STATUS_DEFINITIONS.get(status_id)
        icon = definition["icon"] if definition else status_id[0].upper()
        icons.append(icon)
    return " [" + "".join(icons) + "]"


def _render_menu(
    stdscr: "curses._CursesWindow",
    options: list[str],
    selection: int,
) -> None:
    """Отрисовать всплывающее меню по центру экрана."""
    height, width = stdscr.getmaxyx()
    menu_w = max(len(o) for o in options) + 4
    menu_h = len(options) + 4
    y0 = max(0, (height - menu_h) // 2)
    x0 = max(0, (width - menu_w) // 2)

    # Рамка
    for y in range(menu_h):
        for x in range(menu_w):
            try:
                stdscr.addch(y0 + y, x0 + x, " ", curses.color_pair(9))
            except curses.error:
                pass

    for x in range(1, menu_w - 1):
        try:
            stdscr.addch(y0, x0 + x, "-", curses.color_pair(9))
            stdscr.addch(y0 + menu_h - 1, x0 + x, "-", curses.color_pair(9))
        except curses.error:
            pass
    for y in range(1, menu_h - 1):
        try:
            stdscr.addch(y0 + y, x0, "|", curses.color_pair(9))
            stdscr.addch(y0 + y, x0 + menu_w - 1, "|", curses.color_pair(9))
        except curses.error:
            pass

    try:
        stdscr.addstr(y0, x0 + 2, " МЕНЮ ", curses.color_pair(9))
    except curses.error:
        pass

    for idx, opt in enumerate(options):
        line = f" {opt} "
        if idx == selection:
            line = f"> {opt} <"
        try:
            stdscr.addstr(y0 + 2 + idx, x0 + 2, line[: menu_w - 4], curses.color_pair(9))
        except curses.error:
            pass


def show_message(stdscr: "curses._CursesWindow", message: str) -> None:
    """Показать модальное сообщение и ждать любой клавиши."""
    height, width = stdscr.getmaxyx()
    msg = message[: width - 4]
    y = height // 2
    x = max(0, (width - len(msg)) // 2)
    try:
        stdscr.addstr(y - 1, x, " " * len(msg), curses.color_pair(9))
        stdscr.addstr(y, x, msg, curses.color_pair(9))
        stdscr.addstr(y + 1, x, " " * len(msg), curses.color_pair(9))
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()
