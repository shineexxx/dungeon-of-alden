#!/usr/bin/env python3
"""Точка входа в roguelike."""

from __future__ import annotations

import curses
import sys

from engine.game_loop import run_game
from engine.menu import (
    new_game,
    select_save_slot,
    show_main_menu,
    show_message,
    show_settings_menu,
)
from engine.render import init_colors
from systems.hall_of_fame import show_hall_of_fame
from systems.save import AUTOSAVE_SLOT, list_slots, load_game
from systems.settings import load_settings


def main(stdscr: "curses._CursesWindow") -> None:
    """Главная функция: показать меню и запустить игру."""
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.keypad(True)
    init_colors()

    settings = load_settings()

    while True:
        choice = show_main_menu(stdscr)

        if choice == "new_game":
            state = new_game(stdscr)
            state.settings = settings
            run_game(stdscr, state)
        elif choice == "load_game":
            slots = list_slots()
            slot = select_save_slot(stdscr, slots, "Выберите сохранение")
            if slot:
                state = load_game(slot)
                if state:
                    state.log_message(f"Загружен слот '{slot}'.")
                    state.settings = settings
                    run_game(stdscr, state)
                else:
                    show_message(stdscr, "Не удалось загрузить сохранение.")
        elif choice == "settings":
            show_settings_menu(stdscr, settings)
        elif choice == "hall_of_fame":
            show_hall_of_fame(stdscr)
        elif choice == "quit":
            break


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
