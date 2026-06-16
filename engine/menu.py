"""Главное меню игры."""

from __future__ import annotations

import curses
from typing import TYPE_CHECKING

from systems.settings import Settings, load_settings, save_settings

if TYPE_CHECKING:
    from curses import _CursesWindow
    from systems.game_state import GameState


MENU_OPTIONS = [
    ("new_game", "Новая игра"),
    ("load_game", "Загрузить игру"),
    ("settings", "Настройки"),
    ("hall_of_fame", "Зал славы"),
    ("quit", "Выход"),
]


def show_main_menu(stdscr: "_CursesWindow") -> str:
    """Показать главное меню. Вернуть выбранный action_id."""
    selection = 0
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = " ПОДЗЕМЕЛЬЕ АЛЬДЕНА "
        try:
            stdscr.attron(curses.color_pair(9))
            stdscr.addstr(2, (width - len(title)) // 2, title)
            stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        start_y = height // 2 - len(MENU_OPTIONS) // 2
        for idx, (action_id, label) in enumerate(MENU_OPTIONS):
            prefix = "> " if idx == selection else "  "
            line = f"{prefix}{label}"
            try:
                stdscr.addstr(start_y + idx, (width - len(line)) // 2, line)
            except curses.error:
                pass

        try:
            stdscr.addstr(height - 2, 2, "↑↓ выбор, Enter — подтвердить", curses.color_pair(9))
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP:
            selection = (selection - 1) % len(MENU_OPTIONS)
        elif key == curses.KEY_DOWN:
            selection = (selection + 1) % len(MENU_OPTIONS)
        elif key in (10, 13, curses.KEY_ENTER):
            return MENU_OPTIONS[selection][0]


def select_save_slot(stdscr: "_CursesWindow", slots: list[str], title: str) -> str | None:
    """Показать список слотов сохранений. Вернуть выбранный слот или None."""
    if not slots:
        show_message(stdscr, "Нет доступных сохранений.")
        return None

    selection = 0
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        try:
            stdscr.attron(curses.color_pair(9))
            stdscr.addstr(1, 2, title[: width - 4])
            stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        for idx, slot in enumerate(slots):
            prefix = "> " if idx == selection else "  "
            try:
                stdscr.addstr(3 + idx, 2, f"{prefix}{slot}")
            except curses.error:
                pass

        try:
            stdscr.addstr(height - 2, 2, "↑↓ выбор, Enter — загрузить, Esc — назад", curses.color_pair(9))
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27,):
            return None
        if key == curses.KEY_UP:
            selection = (selection - 1) % len(slots)
        elif key == curses.KEY_DOWN:
            selection = (selection + 1) % len(slots)
        elif key in (10, 13, curses.KEY_ENTER):
            return slots[selection]


def show_settings_menu(stdscr: "_CursesWindow", settings: "Settings") -> None:
    """Меню настроек."""
    options = [
        ("use_unicode", "Графика", ["Unicode", "Классика"], settings.use_unicode),
    ]
    selection = 0
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        title = " НАСТРОЙКИ "
        try:
            stdscr.attron(curses.color_pair(9))
            stdscr.addstr(1, (width - len(title)) // 2, title)
            stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        for idx, (key, label, values, current) in enumerate(options):
            prefix = "> " if idx == selection else "  "
            current_label = values[0] if current else values[1]
            line = f"{prefix}{label}: {current_label}"
            try:
                stdscr.addstr(3 + idx, 2, line[: width - 4])
            except curses.error:
                pass

        try:
            stdscr.addstr(height - 2, 2, "↑↓ выбор, Enter — переключить, Esc — назад", curses.color_pair(9))
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27,):
            save_settings(settings)
            return
        if key == curses.KEY_UP:
            selection = (selection - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selection = (selection + 1) % len(options)
        elif key in (10, 13, curses.KEY_ENTER):
            opt_key, _, _, current = options[selection]
            new_value = not current
            setattr(settings, opt_key, new_value)
            options[selection] = (opt_key, options[selection][1], options[selection][2], new_value)


def show_message(stdscr: "_CursesWindow", message: str) -> None:
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


def ask_player_name(stdscr: "_CursesWindow") -> str:
    """Спросить имя игрока."""
    height, width = stdscr.getmaxyx()
    prompt = "Введите имя искателя: "
    y = height // 2
    x = max(0, (width - 40) // 2)
    curses.echo()
    curses.curs_set(1)
    try:
        stdscr.clear()
        stdscr.addstr(y, x, prompt, curses.color_pair(9))
        stdscr.refresh()
        name = stdscr.getstr(y, x + len(prompt), 20).decode("utf-8", errors="replace").strip()
    finally:
        curses.noecho()
        try:
            curses.curs_set(0)
        except curses.error:
            pass
    return name or "Искатель"


def new_game(stdscr: "_CursesWindow") -> "GameState":
    """Создать новое состояние игры через меню."""
    import random
    from systems.game_state import GameState

    name = ask_player_name(stdscr)
    seed = random.randint(0, 2_147_483_647)
    state = GameState(seed=seed, depth=1, player_name=name)
    state.log_message(f"Добро пожаловать, {name}!")
    state.generate_level()
    return state
