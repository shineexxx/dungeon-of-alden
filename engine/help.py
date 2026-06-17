"""Экран справки по игре."""

from __future__ import annotations

import curses
from typing import TYPE_CHECKING

from engine.text_utils import add_wrapped_text, wrap_text

if TYPE_CHECKING:
    from curses import _CursesWindow


SECTIONS: list[tuple[str, list[str]]] = [
    (
        "Управление",
        [
            "WASD / стрелки — ходить",
            "G — подобрать предмет",
            "I — инвентарь",
            "D — выбросить предмет",
            "T / E — взаимодействовать с NPC/объектом",
            "Z — кастовать заклинание",
            "B — книга заклинаний",
            "J — журнал",
            "F — искать ловушки (подсвечивает область)",
            "Пробел / Enter — спуститься по лестнице",
            "Esc — меню",
            "Q — быстрый выход",
            "? — эта справка",
        ],
    ),
    (
        "Символы",
        [
            "@ / ☻ — игрок",
            "> / ▼ — лестница",
            "# / ▓ — стена",
            ". / · — пол",
            "! — зелья",
            "? — свитки",
            "% — еда",
            "$ — золото",
            "/ — оружие",
            "[ — броня",
            "= — кольца",
            "+ — книги заклинаний",
            "\" — артефакты",
        ],
    ),
    (
        "Советы",
        [
            "Зелья и свитки изначально неопознаны — используйте или несите к алхимику.",
            "Ешьте вовремя: голод снижает HP.",
            "Проклятые предметы нельзя снять, пока не снять проклятие.",
            "Освобождайте пленников — они отблагодарят (T/E).",
            "На 7-м уровне ждёт финальный босс.",
        ],
    ),
]


def show_help(stdscr: "_CursesWindow") -> None:
    """Показать экран справки."""
    page = 0
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = " СПРАВКА "
        try:
            stdscr.attron(curses.color_pair(9))
            stdscr.addstr(0, (width - len(title)) // 2, title)
            stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        section_title, lines = SECTIONS[page]
        try:
            stdscr.attron(curses.color_pair(10))
            stdscr.addstr(2, 2, section_title[: width - 4])
            stdscr.attroff(curses.color_pair(10))
        except curses.error:
            pass

        y = 4
        for line in lines:
            used = add_wrapped_text(stdscr, y, 2, line, width - 4)
            y += used + 1
            if y >= height - 3:
                break

        footer = f"Страница {page + 1}/{len(SECTIONS)}. ← → — страницы, Esc — закрыть."
        add_wrapped_text(stdscr, height - 2, 2, footer, width - 4, curses.color_pair(9))

        stdscr.refresh()
        key = stdscr.getch()
        if key in (27, ord("q"), ord("Q")):
            return
        if key == curses.KEY_LEFT:
            page = (page - 1) % len(SECTIONS)
        elif key == curses.KEY_RIGHT:
            page = (page + 1) % len(SECTIONS)
