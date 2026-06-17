"""Утилиты для работы с текстом в curses."""

from __future__ import annotations

import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from curses import _CursesWindow


def wrap_text(text: str, width: int) -> list[str]:
    """Перенести текст на несколько строк заданной ширины.

    Учитывает пробелы и переносит по словам. Если слово длиннее width,
    оно режется посимвольно.
    """
    if width <= 0:
        return []
    lines: list[str] = []
    current = ""
    for word in text.split(" "):
        word = word.strip()
        if not word:
            continue
        # Длина слова с учётом возможного пробела
        add_len = len(word) if not current else len(current) + 1 + len(word)
        if add_len <= width:
            current = word if not current else f"{current} {word}"
        else:
            if current:
                lines.append(current)
            # Если само слово длиннее width — нарезаем
            while len(word) > width:
                lines.append(word[:width])
                word = word[width:]
            current = word
    if current:
        lines.append(current)
    return lines


def add_wrapped_text(
    stdscr: "_CursesWindow",
    y: int,
    x: int,
    text: str,
    width: int,
    attr: int = 0,
    max_lines: int | None = None,
) -> int:
    """Нарисовать перенесённый текст. Вернуть количество занятых строк."""
    lines = wrap_text(text, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for idx, line in enumerate(lines):
        try:
            stdscr.addstr(y + idx, x, line[:width], attr)
        except curses.error:
            pass
    return len(lines)


def show_wrapped_message(stdscr: "_CursesWindow", message: str) -> None:
    """Показать модальное сообщение с переносом и ждать любой клавиши."""
    height, width = stdscr.getmaxyx()
    usable_width = max(10, width - 4)
    lines = wrap_text(message, usable_width)
    box_h = len(lines) + 2
    box_w = min(usable_width + 2, width - 2)
    y0 = max(0, (height - box_h) // 2)
    x0 = max(0, (width - box_w) // 2)

    # Рамка
    for y in range(box_h):
        for x in range(box_w):
            try:
                stdscr.addch(y0 + y, x0 + x, " ", curses.color_pair(9))
            except curses.error:
                pass
    for x in range(1, box_w - 1):
        try:
            stdscr.addch(y0, x0 + x, "-", curses.color_pair(9))
            stdscr.addch(y0 + box_h - 1, x0 + x, "-", curses.color_pair(9))
        except curses.error:
            pass
    for y in range(1, box_h - 1):
        try:
            stdscr.addch(y0 + y, x0, "|", curses.color_pair(9))
            stdscr.addch(y0 + y, x0 + box_w - 1, "|", curses.color_pair(9))
        except curses.error:
            pass

    for idx, line in enumerate(lines):
        try:
            stdscr.addstr(y0 + 1 + idx, x0 + 1, line[: box_w - 2], curses.color_pair(9))
        except curses.error:
            pass

    stdscr.refresh()
    stdscr.getch()
