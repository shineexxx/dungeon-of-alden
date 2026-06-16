"""Прогрессия игрока: опыт, уровни, перки."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.player import Player
    from curses import _CursesWindow


@dataclass
class LevelUpChoice:
    key: str
    name: str
    description: str


# Список возможных перков при повышении уровня
LEVEL_UP_PERKS: list[LevelUpChoice] = [
    LevelUpChoice("hp", "Крепкий", "+8 максимального HP, полное лечение"),
    LevelUpChoice("atk", "Сильный", "+2 к урону"),
    LevelUpChoice("ac", "Бронированный", "+1 к классу брони"),
    LevelUpChoice("fov", "Зоркий", "+1 к радиусу обзора"),
    LevelUpChoice("mana", "Мудрый", "+5 к максимальной мане"),
    LevelUpChoice("mana_regen", "Пробудившийся", "+1 к регенерации маны каждые 5 ходов"),
]


def xp_to_next_level(level: int) -> int:
    """Опыт, необходимый для достижения следующего уровня."""
    return level * 20


def add_xp(player: "Player", amount: int) -> int:
    """Добавить игроку опыт. Возвращает количество новых уровней."""
    player.xp += amount
    new_levels = 0
    while player.xp >= xp_to_next_level(player.level):
        player.xp -= xp_to_next_level(player.level)
        player.level += 1
        new_levels += 1
    return new_levels


def apply_perk(player: "Player", perk_key: str) -> str:
    """Применить выбранный перк к игроку. Возвращает описание."""
    if perk_key == "hp":
        player.max_hp += 8
        player.hp = player.max_hp
        return "Максимальное HP повышено на 8."
    if perk_key == "atk":
        player.atk += 2
        return "Урон повышен на 2."
    if perk_key == "ac":
        player.ac += 1
        return "Класс брони повышен на 1."
    if perk_key == "fov":
        player.fov_radius += 1
        return "Радиус обзора увеличен на 1."
    if perk_key == "mana":
        player.max_mana += 5
        player.mana += 5
        return "Максимальная мана повышена на 5."
    if perk_key == "mana_regen":
        return "Регенерация маны улучшена."
    if perk_key == "speed":
        player.speed += 0.1
        return "Скорость повышена."
    return "Неизвестный перк."


def get_level_up_choices(rng) -> list[LevelUpChoice]:
    """Вернуть 3 случайных перка для выбора."""
    import random

    pool = list(LEVEL_UP_PERKS)
    rng.shuffle(pool)
    return pool[:3]


def show_level_up_menu(stdscr: "_CursesWindow", choices: list[LevelUpChoice]) -> str:
    """Показать меню выбора перка. Возвращает key выбранного перка."""
    import curses

    height, width = stdscr.getmaxyx()
    menu_w = max(len(c.name) + len(c.description) for c in choices) + 12
    menu_w = min(menu_w, width - 4)
    menu_h = len(choices) + 6
    y0 = max(0, (height - menu_h) // 2)
    x0 = max(0, (width - menu_w) // 2)

    selection = 0
    while True:
        # Рамка и фон
        for y in range(menu_h):
            for x in range(menu_w):
                try:
                    stdscr.addch(y0 + y, x0 + x, " ", curses.color_pair(9))
                except curses.error:
                    pass

        try:
            stdscr.addstr(y0, x0 + 2, " НОВЫЙ УРОВЕНЬ! Выберите бонус: ", curses.color_pair(9))
        except curses.error:
            pass

        for idx, choice in enumerate(choices):
            prefix = f"{idx + 1}. "
            line = f"{prefix}{choice.name}: {choice.description}"
            if idx == selection:
                line = "> " + line + " <"
            else:
                line = "  " + line
            try:
                stdscr.addstr(y0 + 2 + idx, x0 + 2, line[: menu_w - 4], curses.color_pair(9))
            except curses.error:
                pass

        try:
            stdscr.addstr(y0 + menu_h - 2, x0 + 2, " 1/2/3 или стрелки + Enter ", curses.color_pair(9))
        except curses.error:
            pass

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selection = (selection - 1) % len(choices)
        elif key == curses.KEY_DOWN:
            selection = (selection + 1) % len(choices)
        elif key in (10, 13, curses.KEY_ENTER):
            return choices[selection].key
        elif key in (ord("1"), ord("2"), ord("3")):
            idx = key - ord("1")
            if idx < len(choices):
                return choices[idx].key
