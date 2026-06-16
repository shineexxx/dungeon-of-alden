"""Система магии: мана, заклинания, кулдауны, обучение."""

from __future__ import annotations

import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from curses import _CursesWindow
    from entities.player import Player
    from systems.game_state import GameState


DEFAULT_STARTING_SPELLS = ["magic_missile", "heal_spell"]


def initialize_magic(player: "Player") -> None:
    """Инициализировать магические параметры нового игрока."""
    if not hasattr(player, "max_mana") or player.max_mana is None:
        player.max_mana = 10
    if not hasattr(player, "mana") or player.mana is None:
        player.mana = player.max_mana
    if not hasattr(player, "known_spells") or not player.known_spells:
        player.known_spells = list(DEFAULT_STARTING_SPELLS)
    if not hasattr(player, "spell_cooldowns") or player.spell_cooldowns is None:
        player.spell_cooldowns = {}


def learn_spell(player: "Player", spell_id: str) -> str:
    """Выучить заклинание. Возвращает сообщение."""
    from content.spells import get_spell

    spell = get_spell(spell_id)
    if not spell:
        return "Неизвестное заклинание."
    if spell_id in player.known_spells:
        return f"Вы уже знаете {spell['name']}."
    player.known_spells.append(spell_id)
    return f"Вы выучили заклинание {spell['name']}!"


def can_cast(player: "Player", spell_id: str) -> tuple[bool, str]:
    """Проверить, можно ли скастовать заклинание."""
    from content.spells import get_spell

    initialize_magic(player)
    spell = get_spell(spell_id)
    if not spell:
        return False, "Неизвестное заклинание."
    if spell_id not in player.known_spells:
        return False, "Вы не знаете это заклинание."
    if player.spell_cooldowns.get(spell_id, 0) > 0:
        return False, f"Заклинание на кулдауне: {player.spell_cooldowns[spell_id]} ходов."
    if player.mana < spell["mana_cost"]:
        return False, f"Недостаточно маны ({player.mana}/{spell['mana_cost']})."
    if player.level < spell["level_req"]:
        return False, f"Требуется уровень {spell['level_req']}."
    return True, ""


def cast_spell(player: "Player", state: "GameState", spell_id: str, target=None) -> str:
    """Скастовать заклинание. Возвращает сообщение."""
    from content.spells import get_spell
    from systems.effects import apply_effect

    initialize_magic(player)
    ok, reason = can_cast(player, spell_id)
    if not ok:
        return reason

    spell = get_spell(spell_id)
    player.mana -= spell["mana_cost"]
    if spell["cooldown"] > 0:
        player.spell_cooldowns[spell_id] = spell["cooldown"]

    effect_id = spell["effect"]
    power = spell["effect_power"]

    # Для single/line/cone/aoe эффекты обрабатываются отдельно через targeting,
    # но здесь поддерживаем self и utility.
    if spell["target_type"] == "self":
        return apply_effect(effect_id, player, state, power)

    # Single target с переданной целью
    if spell["target_type"] in ("single", "line", "cone") and target is not None:
        # Некоторые эффекты принимают target как keyword
        from systems.effects import EFFECTS
        effect_func = EFFECTS.get(effect_id)
        if effect_func and "target" in effect_func.__code__.co_varnames:
            return effect_func(player, state, power, target=target)
        return apply_effect(effect_id, player, state, power)

    # AoE без target обрабатывается в targeting
    return apply_effect(effect_id, player, state, power)


def tick_cooldowns(player: "Player") -> None:
    """Уменьшить кулдауны заклинаний на 1."""
    for spell_id in list(player.spell_cooldowns.keys()):
        player.spell_cooldowns[spell_id] -= 1
        if player.spell_cooldowns[spell_id] <= 0:
            del player.spell_cooldowns[spell_id]


def regenerate_mana(player: "Player") -> None:
    """Регенерация маны."""
    if player.mana < player.max_mana:
        player.mana = min(player.max_mana, player.mana + 1)


def get_castable_spells(player: "Player") -> list[str]:
    """Вернуть список заклинаний, которые игрок может сейчас использовать."""
    return [sid for sid in player.known_spells if can_cast(player, sid)[0]]


def show_spell_menu(stdscr: "_CursesWindow", player: "Player") -> str | None:
    """Показать меню выбора заклинания. Возвращает ID выбранного или None."""
    from content.spells import get_spell

    initialize_magic(player)
    if not player.known_spells:
        return None

    selection = 0
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = " ЗАКЛИНАНИЯ (MP:{}/{}) ".format(player.mana, player.max_mana)
        try:
            stdscr.attron(curses.color_pair(9))
            stdscr.addstr(0, (width - len(title)) // 2, title)
            stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        for idx, spell_id in enumerate(player.known_spells):
            spell = get_spell(spell_id)
            if not spell:
                continue
            ok, reason = can_cast(player, spell_id)
            prefix = "> " if idx == selection else "  "
            cd = player.spell_cooldowns.get(spell_id, 0)
            cd_str = f" [CD:{cd}]" if cd > 0 else ""
            line = f"{prefix}{spell['name']} ({spell['mana_cost']} MP){cd_str} — {spell['description'][:40]}"
            color = 1 if ok else 8  # 8 = серый/лазурный для недоступных
            try:
                stdscr.addstr(2 + idx, 2, line[: width - 4], curses.color_pair(color))
            except curses.error:
                pass

        try:
            stdscr.addstr(height - 2, 2, "↑↓ выбор, Enter — каст, Esc — отмена", curses.color_pair(9))
        except curses.error:
            pass

        stdscr.refresh()
        key = stdscr.getch()

        if key in (27, ord("z"), ord("Z")):
            return None
        if key == curses.KEY_UP:
            selection = (selection - 1) % len(player.known_spells)
        elif key == curses.KEY_DOWN:
            selection = (selection + 1) % len(player.known_spells)
        elif key in (10, 13, curses.KEY_ENTER):
            return player.known_spells[selection]


def show_spellbook(stdscr: "_CursesWindow", player: "Player") -> None:
    """Показать книгу всех известных заклинаний (просмотр)."""
    from content.spells import get_spell

    initialize_magic(player)
    selection = 0
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = " КНИГА ЗАКЛИНАНИЙ "
        try:
            stdscr.attron(curses.color_pair(9))
            stdscr.addstr(0, (width - len(title)) // 2, title)
            stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        for idx, spell_id in enumerate(player.known_spells):
            spell = get_spell(spell_id)
            if not spell:
                continue
            prefix = "> " if idx == selection else "  "
            line = f"{prefix}{spell['name']} (школа: {spell['school']}, {spell['mana_cost']} MP)"
            try:
                stdscr.addstr(2 + idx, 2, line[: width - 4])
            except curses.error:
                pass

        spell = get_spell(player.known_spells[selection]) if player.known_spells else None
        if spell:
            desc = spell.get("description", "")
            try:
                stdscr.addstr(4 + len(player.known_spells), 2, desc[: width - 4])
            except curses.error:
                pass

        try:
            stdscr.addstr(height - 2, 2, "↑↓ просмотр, b/Esc — закрыть", curses.color_pair(9))
        except curses.error:
            pass

        stdscr.refresh()
        key = stdscr.getch()

        if key in (27, ord("b"), ord("B")):
            return
        if key == curses.KEY_UP:
            selection = (selection - 1) % max(1, len(player.known_spells))
        elif key == curses.KEY_DOWN:
            selection = (selection + 1) % max(1, len(player.known_spells))
