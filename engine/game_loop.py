"""Главный игровой цикл."""

from __future__ import annotations

import curses
import random
from typing import TYPE_CHECKING

from engine.fov import compute_fov
from engine.help import show_help
from engine.input_handler import get_action
from engine.render import init_colors, render_map, show_message
from engine.targeting import get_affected_positions, select_target
from systems.inventory import open_inventory
from systems.interactables import handle_event
from systems.journal import show_journal
from systems.magic import (
    cast_spell,
    initialize_magic,
    regenerate_mana,
    show_spell_menu,
    show_spellbook,
    tick_cooldowns,
)
from systems.progression import add_xp, apply_perk, get_level_up_choices, show_level_up_menu
from systems.save import (
    AUTOSAVE_SLOT,
    delete_save,
    list_slots,
    load_game,
    save_game,
)
from systems.stats import recalculate_stats
from entities.ai import choose_ai_action
from entities.npcs import interact_with_npc
from systems.effects import apply_status, tick_status_effects, is_paralyzed

if TYPE_CHECKING:
    from curses import _CursesWindow
    from systems.game_state import GameState


MENU_OPTIONS = ["Save", "Load", "New Game", "Quit"]


def run_game(stdscr: "_CursesWindow", state: "GameState") -> None:
    """Запустить или продолжить игру с переданным состоянием."""
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.nodelay(False)
    stdscr.keypad(True)
    init_colors()

    initialize_magic(state.player)
    recalculate_stats(state.player)

    log_lines = state.log[-10:]
    menu_mode = False
    menu_selection = 0
    sub_menu_slots: list[str] = []
    sub_menu_selection = 0
    sub_menu_active = False
    sub_menu_title = ""

    # Первичный FOV
    compute_fov(state.dungeon, state.player.x, state.player.y, state.player.fov_radius)

    pending_level_up: list | None = None

    while True:
        render_map(
            stdscr,
            state,
            state.player,
            state.dungeon,
            state.mobs,
            state.items_on_floor,
            log_lines,
            menu_mode or sub_menu_active or pending_level_up is not None,
            sub_menu_slots if sub_menu_active else (MENU_OPTIONS if pending_level_up is None else []),
            sub_menu_selection if sub_menu_active else (menu_selection if pending_level_up is None else 0),
            level_up_mode=pending_level_up is not None,
        )

        # Если есть ожидающий level-up — показываем меню перков
        if pending_level_up is not None:
            choices, _ = pending_level_up
            perk_key = show_level_up_menu(stdscr, choices)
            desc = apply_perk(state.player, perk_key)
            state.player.perks.append(perk_key)
            recalculate_stats(state.player)
            compute_fov(state.dungeon, state.player.x, state.player.y, state.player.fov_radius)
            state.log_message(f"LEVEL UP! Вы теперь уровень {state.player.level}. {desc}")
            pending_level_up = None
            log_lines = state.log[-10:]
            continue

        key = stdscr.getch()
        if key == -1:
            continue

        # Обработка подменю (Load / Save slot selection)
        if sub_menu_active:
            if key == 27:  # Esc - закрыть подменю
                sub_menu_active = False
                sub_menu_slots = []
                sub_menu_selection = 0
                continue
            if key == curses.KEY_UP:
                sub_menu_selection = (sub_menu_selection - 1) % len(sub_menu_slots)
                continue
            if key == curses.KEY_DOWN:
                sub_menu_selection = (sub_menu_selection + 1) % len(sub_menu_slots)
                continue
            if key in (10, 13, curses.KEY_ENTER):  # Enter
                slot = sub_menu_slots[sub_menu_selection]
                if slot == "<new slot>":
                    slot = _ask_slot_name(stdscr)
                    if not slot:
                        sub_menu_active = False
                        sub_menu_slots = []
                        sub_menu_selection = 0
                        continue
                if sub_menu_title == "Load":
                    loaded = load_game(slot)
                    if loaded:
                        state = loaded
                        initialize_magic(state.player)
                        recalculate_stats(state.player)
                        log_lines = state.log[-10:]
                        compute_fov(state.dungeon, state.player.x, state.player.y, state.player.fov_radius)
                        state.log_message(f"Загружен слот '{slot}'.")
                    else:
                        show_message(stdscr, f"Не удалось загрузить '{slot}'.")
                elif sub_menu_title == "Save":
                    if save_game(state, slot):
                        show_message(stdscr, f"Сохранено в '{slot}'.")
                    else:
                        show_message(stdscr, "Ошибка сохранения.")
                sub_menu_active = False
                sub_menu_slots = []
                sub_menu_selection = 0
            continue

        # Обработка главного меню
        if menu_mode:
            if key == 27:  # Esc - закрыть меню
                menu_mode = False
                menu_selection = 0
                continue
            if key == curses.KEY_UP:
                menu_selection = (menu_selection - 1) % len(MENU_OPTIONS)
                continue
            if key == curses.KEY_DOWN:
                menu_selection = (menu_selection + 1) % len(MENU_OPTIONS)
                continue
            if key in (10, 13, curses.KEY_ENTER):
                choice = MENU_OPTIONS[menu_selection]
                if choice == "Save":
                    sub_menu_title = "Save"
                    sub_menu_slots = [AUTOSAVE_SLOT] + [s for s in list_slots() if s != AUTOSAVE_SLOT]
                    sub_menu_slots.append("<new slot>")
                    sub_menu_selection = 0
                    sub_menu_active = True
                elif choice == "Load":
                    sub_menu_title = "Load"
                    sub_menu_slots = list_slots()
                    if not sub_menu_slots:
                        show_message(stdscr, "Нет сохранений.")
                        continue
                    sub_menu_selection = 0
                    sub_menu_active = True
                elif choice == "New Game":
                    state = _new_game(state)
                    initialize_magic(state.player)
                    recalculate_stats(state.player)
                    log_lines = state.log[-10:]
                    compute_fov(state.dungeon, state.player.x, state.player.y, state.player.fov_radius)
                elif choice == "Quit":
                    save_game(state, AUTOSAVE_SLOT)
                    return
                menu_mode = False
                menu_selection = 0
            continue

        # Обычный игровой ввод
        action = get_action(key)

        if action.type == "quit":
            if _confirm_exit(stdscr):
                save_game(state, AUTOSAVE_SLOT)
                return
            log_lines = state.log[-10:]
            continue

        if action.type == "menu":
            menu_mode = True
            menu_selection = 0
            continue

        if action.type == "inventory" or action.type == "drop":
            if open_inventory(stdscr, state.player, state):
                recalculate_stats(state.player)
                compute_fov(state.dungeon, state.player.x, state.player.y, state.player.fov_radius)
            log_lines = state.log[-10:]
            continue

        if action.type == "spellbook":
            show_spellbook(stdscr, state.player)
            log_lines = state.log[-10:]
            continue

        if action.type == "journal":
            show_journal(stdscr, state.journal)
            log_lines = state.log[-10:]
            continue

        if action.type == "help":
            show_help(stdscr)
            log_lines = state.log[-10:]
            continue

        if action.type == "interact":
            msg = _handle_interact(stdscr, state)
            if msg:
                state.log_message(msg)
            log_lines = state.log[-10:]
            compute_fov(state.dungeon, state.player.x, state.player.y, state.player.fov_radius)
            continue

        if action.type == "cast":
            spell_id = show_spell_menu(stdscr, state.player)
            if spell_id:
                from content.spells import get_spell
                from systems.magic import can_cast
                spell = get_spell(spell_id)
                ok, reason = can_cast(state.player, spell_id)
                if not ok:
                    state.log_message(reason)
                elif spell:
                    if spell["target_type"] == "self":
                        msg = cast_spell(state.player, state, spell_id)
                        state.log_message(msg)
                    else:
                        target_pos = select_target(stdscr, state, spell)
                        if target_pos:
                            msg = _cast_targeted(state, spell_id, spell, target_pos)
                            state.log_message(msg)
            log_lines = state.log[-10:]
            continue

        acted = False
        if action.type == "search":
            msg = _search_traps(state)
            state.log_message(msg)
            acted = True

        if acted:
            state.turn += 1
            _after_player_turn(state)
            _apply_hunger(state)
            _tick_player_status_effects(state)
            tick_cooldowns(state.player)
            _regenerate_mana_tick(state.player)
            compute_fov(state.dungeon, state.player.x, state.player.y, state.player.fov_radius)
            log_lines = state.log[-10:]
            if not state.player.is_alive():
                _handle_death(stdscr, state)
                return
            continue

        if action.type == "move":
            dx = action.data["dx"]
            dy = action.data["dy"]
            # Спутанность: 50% случайное направление
            if state.player.status_effects.get("confused", 0) > 0 and random.random() < 0.5:
                dx, dy = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
            acted = _try_move(state, dx, dy)

        elif action.type == "pickup":
            _pickup(state)
            acted = True

        elif action.type == "use_stairs":
            if (state.player.x, state.player.y) == state.dungeon.stairs:
                _descend(state)
                compute_fov(state.dungeon, state.player.x, state.player.y, state.player.fov_radius)
                acted = True
            else:
                state.log_message("Здесь нет лестницы вниз.")

        if acted:
            state.turn += 1
            _after_player_turn(state)
            _apply_hunger(state)
            _tick_player_status_effects(state)
            tick_cooldowns(state.player)
            _regenerate_mana_tick(state.player)
            compute_fov(state.dungeon, state.player.x, state.player.y, state.player.fov_radius)

        log_lines = state.log[-10:]

        if not state.player.is_alive():
            _handle_death(stdscr, state)
            return

        if _check_victory(state):
            _handle_victory(stdscr, state)
            return

        # Проверка level-up
        while state.player.xp >= state.player.xp_to_next():
            state.player.xp -= state.player.xp_to_next()
            state.player.level += 1
            choices = get_level_up_choices(state.rng)
            pending_level_up = (choices, 0)
            break


def _new_game(old_state: "GameState") -> "GameState":
    """Начать новую игру."""
    from systems.game_state import GameState

    seed = random.randint(0, 2_147_483_647)
    state = GameState(seed=seed, depth=1)
    state.log_message("Добро пожаловать в подземелье!")
    state.generate_level()
    return state


def _cast_targeted(state: "GameState", spell_id: str, spell: dict, target_pos: tuple[int, int]) -> str:
    """Применить заклинание с выбранной целью/зоной (одиночное списание маны)."""
    from content.spells import get_spell
    from systems.effects import EFFECTS, apply_status

    tx, ty = target_pos
    affected = get_affected_positions(tx, ty, spell["target_type"], spell.get("aoe_radius", 0), (state.player.x, state.player.y))

    effect_id = spell["effect"]
    power = spell["effect_power"]

    if spell["target_type"] == "single":
        target = None
        for mob in state.mobs:
            if mob.alive and mob.x == tx and mob.y == ty:
                target = mob
                break
        if target is None:
            return "Цель не найдена."

    # Списываем ману и ставим кулдаун один раз
    state.player.mana -= spell["mana_cost"]
    if spell["cooldown"] > 0:
        state.player.spell_cooldowns[spell_id] = spell["cooldown"]

    # Проверяем, есть ли игрок в зоне AoE (кроме self-earthquake)
    if spell["target_type"] == "aoe" and (state.player.x, state.player.y) in affected:
        state.log_message("Внимание: вы в зоне поражения!")

    if spell["target_type"] == "single":
        effect_func = EFFECTS.get(effect_id)
        if effect_func and "target" in effect_func.__code__.co_varnames:
            return effect_func(state.player, state, power, target=target)
        return "Цель не найдена."

    if spell["target_type"] in ("line", "cone", "aoe"):
        total_hits = 0
        for mob in state.mobs:
            if mob.alive and (mob.x, mob.y) in affected:
                effect_func = EFFECTS.get(effect_id)
                if effect_func and "target" in effect_func.__code__.co_varnames:
                    effect_func(state.player, state, power, target=mob)
                else:
                    # Fallback: обычный урон
                    dmg = random.randint(power[0], power[1])
                    mob.take_damage(dmg)
                if spell.get("status"):
                    apply_status(mob, spell["status"], spell.get("status_duration", 3), state=state)
                total_hits += 1
                if not mob.alive:
                    _on_mob_death(state, mob)
        if total_hits:
            return f"{spell['name']} поражает {total_hits} целей."
        return f"{spell['name']} не задевает никого."

    return "Неизвестный тип цели."


def _ask_slot_name(stdscr: "_CursesWindow") -> str:
    """Спросить имя нового слота сохранения."""
    height, width = stdscr.getmaxyx()
    prompt = "Имя слота: "
    y = height // 2
    x = max(0, (width - 30) // 2)
    curses.echo()
    curses.curs_set(1)
    try:
        stdscr.addstr(y, x, prompt, curses.color_pair(9))
        stdscr.clrtoeol()
        stdscr.refresh()
        name = stdscr.getstr(y, x + len(prompt), 20).decode("utf-8", errors="replace").strip()
    finally:
        curses.noecho()
        try:
            curses.curs_set(0)
        except curses.error:
            pass
    return name


def _try_move(state: "GameState", dx: int, dy: int) -> bool:
    """Попытаться переместить игрока или атаковать моба."""
    new_x = state.player.x + dx
    new_y = state.player.y + dy

    for mob in state.mobs:
        if mob.alive and mob.x == new_x and mob.y == new_y:
            _player_attack(state, mob)
            return True

    if state.dungeon.blocks_movement(new_x, new_y):
        return False

    state.player.x = new_x
    state.player.y = new_y

    # Лёд: скольжение на 2 клетки в том же направлении
    hazard_id = state.dungeon.hazards.get((new_x, new_y))
    if hazard_id == "ice":
        slide_x = new_x + dx
        slide_y = new_y + dy
        if not state.dungeon.blocks_movement(slide_x, slide_y):
            state.player.x = slide_x
            state.player.y = slide_y
            state.log_message("Вы скользите по льду!")
            new_x, new_y = slide_x, slide_y
            hazard_id = state.dungeon.hazards.get((new_x, new_y))

    # Hazard-эффекты
    if hazard_id:
        _apply_hazard_to_player(state, hazard_id)

    # Ловушки
    _check_trap(state, state.player, is_player=True)

    return True


def _apply_hazard_to_player(state: "GameState", hazard_id: str) -> None:
    """Применить эффект hazard при входе игрока."""
    from world.hazards import get_hazard

    hazard = get_hazard(hazard_id)
    if not hazard:
        return
    effect = hazard.get("on_enter")
    power = hazard.get("on_enter_power")

    if effect == "damage_fire":
        dmg = random.randint(power[0], power[1])
        state.player.take_damage(dmg)
        state.log_message(f"Лава обжигает вас на {dmg} урона!")
    elif effect == "damage_physical":
        dmg = random.randint(power[0], power[1])
        state.player.take_damage(dmg)
        state.log_message(f"Шипы ранят вас на {dmg} урона.")
    elif effect == "slow":
        apply_status(state.player, "slowed", 3, state=state)
        state.log_message("Вода/грязь замедляет вас.")
    elif effect == "poison":
        apply_status(state.player, "poisoned", power, state=state)
        state.log_message("Ядовитый газ отравляет вас!")
    elif effect == "web_stuck":
        apply_status(state.player, "paralyzed", power, state=state)
        state.log_message("Паутина сковывает вас!")
    elif effect == "light":
        apply_status(state.player, "detecting", 5, state=state)
        state.log_message("Свет грибов озаряет окрестности.")
    elif effect == "darkness":
        apply_status(state.player, "blind", 3, state=state)
        state.log_message("Тьма поглощает свет.")
    elif effect == "confusion":
        apply_status(state.player, "confused", power, state=state)
        state.log_message("Пустота сбивает вас с толку.")


def _check_trap(state: "GameState", target, is_player: bool = False) -> None:
    """Проверить ловушку в клетке target."""
    from world.traps import get_trap

    pos = (target.x, target.y)
    trap_id = state.dungeon.traps.get(pos)
    if not trap_id:
        return

    if pos in state.dungeon.revealed_traps:
        return

    trap = get_trap(trap_id)
    if not trap:
        return

    # Бросок на обнаружение (игрок)
    if is_player:
        detect_chance = trap.get("detect_chance", 0.3)
        if state.rng.random() < detect_chance:
            state.dungeon.revealed_traps.add(pos)
            state.log_message(f"Вы заметили {trap['description'].lower()}!")
            return

    # Ловушка срабатывает
    state.dungeon.revealed_traps.add(pos)
    _apply_trap_effect(state, trap, target, is_player)
    if trap.get("one_time", True):
        del state.dungeon.traps[pos]


def _apply_trap_effect(state: "GameState", trap: dict, target, is_player: bool) -> None:
    """Применить эффект ловушки к цели."""
    effect = trap["effect"]
    power = trap.get("effect_power")
    name = "Вы" if is_player else target.name

    if effect == "damage_physical":
        dmg = random.randint(power[0], power[1])
        target.take_damage(dmg)
        state.log_message(f"{name} попадаете в ловушку и получаете {dmg} урона!" if is_player else f"{name} попадает в ловушку!")
    elif effect == "poison":
        apply_status(target, "poisoned", power, state=state)
        state.log_message(f"{name} отравлены иглой." if is_player else f"{name} отравлен.")
    elif effect == "damage_fire":
        dmg = random.randint(power[0], power[1])
        target.take_damage(dmg)
        apply_status(target, "burning", 3, state=state)
        state.log_message(f"Плита под {name} вспыхивает!")
    elif effect == "freezing":
        apply_status(target, "freezing", power, state=state)
        state.log_message(f"{name} замерзли." if is_player else f"{name} замерз.")
    elif effect == "teleport":
        candidates = [
            (x, y)
            for y in range(state.dungeon.height)
            for x in range(state.dungeon.width)
            if state.dungeon.is_floor(x, y)
        ]
        if candidates:
            x, y = state.rng.choice(candidates)
            target.x, target.y = x, y
            state.log_message(f"{name} телепортированы!" if is_player else f"{name} телепортирован.")
    elif effect == "alarm":
        state.log_message("Сигнальная ловушка громко звенит!")
        # Призываем 2-3 монстров биома рядом
        from content.monsters import monsters_for_biome
        from content.biomes import get_biome
        biome = get_biome(state.dungeon.biome_id)
        tags = biome.get("monster_tags", []) if biome else []
        pool = monsters_for_biome(tags, state.depth)
        if pool:
            from entities.mob import Mob
            for _ in range(power):
                candidates = [
                    (x, y)
                    for x in range(max(0, target.x - 5), min(state.dungeon.width, target.x + 6))
                    for y in range(max(0, target.y - 5), min(state.dungeon.height, target.y + 6))
                    if state.dungeon.is_floor(x, y) and (x, y) != (target.x, target.y)
                ]
                if candidates:
                    x, y = state.rng.choice(candidates)
                    state.mobs.append(Mob.from_data(state.rng.choice(pool), x, y))
            state.log_message("К вам спешат враги!")
    elif effect == "paralyzed":
        apply_status(target, "paralyzed", power, state=state)
        state.log_message(f"{name} засыпаете от усыпляющего газа." if is_player else f"{name} засыпает.")
    elif effect == "random_debuff":
        debuff = state.rng.choice(["slowed", "confused", "blind", "weakened"])
        if debuff == "weakened":
            target.atk = max(0, target.atk - 2)
            state.log_message(f"{name} ослаблены проклятием." if is_player else f"{name} ослаблен.")
        else:
            apply_status(target, debuff, power, state=state)
            state.log_message(f"{name} прокляты ({debuff}).")
    elif effect == "damage_arcane":
        dmg = random.randint(power[0], power[1])
        target.take_damage(dmg)
        state.log_message(f"Руна взрывается, {name} получаете {dmg} магического урона!" if is_player else f"Руна взрывается!")


def _search_traps(state: "GameState") -> str:
    """Поиск ловушек в радиусе 1-2 вокруг игрока."""
    from world.traps import get_trap

    px, py = state.player.x, state.player.y
    found = 0
    for y in range(py - 2, py + 3):
        for x in range(px - 2, px + 3):
            if not state.dungeon.in_bounds(x, y):
                continue
            if (x, y) in state.dungeon.revealed_traps:
                continue
            trap_id = state.dungeon.traps.get((x, y))
            if not trap_id:
                continue
            trap = get_trap(trap_id)
            if not trap:
                continue
            chance = trap.get("detect_chance", 0.3)
            if state.rng.random() < chance:
                state.dungeon.revealed_traps.add((x, y))
                found += 1

    # Визуальный эффект поиска: подсветка радиуса на следующий ход
    state.search_highlight_turns = 2

    if found:
        return f"Вы осмотрелись и обнаружили {found} ловушек!"
    return "Вы осмотрелись, но ничего не нашли."


def _player_attack(state: "GameState", mob) -> None:
    """Игрок атакует моба вблизи."""
    from content.items import get_equipment_details

    roll = state.rng.randint(1, 20)
    crit_chance = 0.05
    weapon_table = None

    if state.player.equipped_weapon:
        weapon_table = get_equipment_details(state.player.equipped_weapon)
        if weapon_table:
            crit_chance = weapon_table.get("crit_chance", 0.05)

    if roll >= mob.ac or roll == 20:
        dmg_min, dmg_max = _player_damage_range(state)
        dmg = state.rng.randint(dmg_min, dmg_max)
        is_crit = state.rng.random() < crit_chance
        if is_crit:
            dmg = dmg * 2
            state.log_message(f"КРИТ! Вы ударили {mob.name} на {dmg} урона.")
        else:
            state.log_message(f"Вы ударили {mob.name} на {dmg} урона.")

        mob.take_damage(dmg)

        # Эффекты оружия
        if weapon_table:
            bonus = weapon_table.get("bonus")
            if bonus == "poison":
                apply_status(mob, "poisoned", 5, state=state)
            elif bonus == "fire":
                extra = state.rng.randint(2, 5)
                mob.take_damage(extra)
                state.log_message(f"Огонь обжигает {mob.name} на {extra} урона.")
            elif bonus == "vampiric":
                heal = max(1, dmg // 5)
                state.player.heal(heal)
                state.log_message(f"Вы поглощаете {heal} HP.")
            elif bonus == "frost":
                apply_status(mob, "slowed", 3, state=state)

        if not mob.alive:
            _on_mob_death(state, mob)
    else:
        state.log_message(f"Вы промахнулись по {mob.name}.")


def _player_damage_range(state: "GameState") -> tuple[int, int]:
    """Вернуть (min, max) урон игрока с учётом оружия."""
    from content.items import get_equipment_details

    if state.player.equipped_weapon:
        weapon_table = get_equipment_details(state.player.equipped_weapon)
        if weapon_table:
            return tuple(weapon_table["damage"])
    # Без оружия — кулаки
    return (1, 3)


def _handle_interact(stdscr: "_CursesWindow", state: "GameState") -> str:
    """Обработать взаимодействие с NPC или объектом на соседней/текущей клетке."""
    px, py = state.player.x, state.player.y

    # Сначала проверяем NPC на соседних клетках (включая текущую)
    for npc in state.npcs:
        if abs(npc.x - px) + abs(npc.y - py) <= 1:
            return interact_with_npc(stdscr, state, npc)

    # Затем интерактивные объекты на текущей клетке
    interact = state.dungeon.interactables.get((px, py))
    if interact and not interact.get("used", False):
        event = interact.get("data")
        if event:
            msg = handle_event(stdscr, state, event)
            interact["used"] = True
            state.journal.record_event(event["id"])
            return msg

    return "Здесь не с кем поговорить и не с чем взаимодействовать."


def _on_mob_death(state: "GameState", mob) -> None:
    """Обработка смерти моба: опыт, золото, лут, журнал."""
    state.log_message(f"{mob.name} погибает.")
    state.kills += 1
    state.journal.record_kill(mob.id)

    # Опыт с учётом бонуса
    gained = mob.xp
    if state.player.status_effects.get("xp_bonus", 0) > 0:
        bonus_pct = state.player.status_effects["xp_bonus"]
        gained = int(gained * (1 + bonus_pct / 100))
    state.player.xp += gained
    state.score += gained
    state.log_message(f"Вы получили {gained} XP.")

    # Золото
    gold = mob.roll_gold(state.rng)
    if gold > 0:
        state.player.gold += gold
        state.log_message(f"Вы нашли {gold} золота.")

    # Лут
    loot = mob.roll_loot(state.rng)
    if loot:
        pos = (mob.x, mob.y)
        state.items_on_floor.setdefault(pos, []).append(loot)
        from content.items import get_item
        item_data = get_item(loot)
        if item_data:
            state.log_message(f"{mob.name} роняет {item_data['name']}.")


def _after_player_turn(state: "GameState") -> None:
    """Ходы мобов после игрока с учётом скорости (энергия)."""
    if state.search_highlight_turns > 0:
        state.search_highlight_turns -= 1

    for mob in state.mobs:
        if not mob.alive:
            continue

        # Тикаем статусы мобов
        tick_status_effects(mob, state)
        if not mob.alive:
            continue

        # Паралич/оглушение/заморозка
        if is_paralyzed(mob):
            continue

        mob.energy += mob.speed
        # Замедление уменьшает скорость
        if mob.status_effects.get("slowed", 0) > 0:
            mob.energy -= 0.3

        while mob.energy >= 1.0 and mob.alive:
            mob.energy -= 1.0
            _act_mob(state, mob)
            if not state.player.is_alive():
                return


def _act_mob(state: "GameState", mob) -> None:
    """Выполнить одно действие моба."""
    dist = abs(mob.x - state.player.x) + abs(mob.y - state.player.y)
    if dist > 10 and not state.dungeon.visible[mob.y][mob.x]:
        return

    # Невидимость игрока
    if state.player.status_effects.get("invisible", 0) > 0:
        if dist > 2 and state.rng.random() < 0.7:
            return

    action, tx, ty = choose_ai_action(mob, state)

    if action == "attack":
        _mob_melee_attack(state, mob)
    elif action == "ranged_attack":
        _mob_ranged_attack(state, mob)
    elif action == "cast_spell":
        _mob_cast_spell(state, mob)
    elif action == "move":
        if state.player.x == tx and state.player.y == ty:
            _mob_melee_attack(state, mob)
            return
        occupied = False
        for other in state.mobs:
            if other is not mob and other.alive and other.x == tx and other.y == ty:
                occupied = True
                break
        if not occupied:
            mob.x = tx
            mob.y = ty
            _check_trap(state, mob, is_player=False)
            hazard_id = state.dungeon.hazards.get((mob.x, mob.y))
            if hazard_id and hazard_id != "lava":
                _apply_hazard_to_mob(state, mob, hazard_id)


def _apply_hazard_to_mob(state: "GameState", mob, hazard_id: str) -> None:
    """Упрощённый эффект hazard на моба."""
    from world.hazards import get_hazard

    hazard = get_hazard(hazard_id)
    if not hazard:
        return
    effect = hazard.get("on_enter")
    power = hazard.get("on_enter_power")

    if effect == "damage_fire":
        dmg = random.randint(power[0], power[1])
        mob.take_damage(dmg)
        state.log_message(f"{mob.name} получает {dmg} урона от огня.")
    elif effect == "damage_physical":
        dmg = random.randint(power[0], power[1])
        mob.take_damage(dmg)
    elif effect == "poison":
        apply_status(mob, "poisoned", power, state=state)
    elif effect == "web_stuck":
        apply_status(mob, "paralyzed", power, state=state)
    elif effect == "slow":
        apply_status(mob, "slowed", 3, state=state)

    if not mob.alive:
        _on_mob_death(state, mob)


def _mob_cast_spell(state: "GameState", mob) -> None:
    """Моб-маг кастует заклинание в игрока."""
    from content.spells import get_spell
    from systems.effects import apply_effect

    # Простые магические атаки мобов
    spell_id = state.rng.choice(["magic_missile", "lightning_bolt", "ice_bolt", "fireball"])
    spell = get_spell(spell_id)
    if not spell:
        return

    state.log_message(f"{mob.name} читает заклинание {spell['name']}!")

    if spell_id == "fireball":
        # AoE вокруг игрока
        dmg = state.rng.randint(8, 14)
        state.player.take_damage(dmg)
        apply_status(state.player, "burning", 3, state=state)
        state.log_message(f"Огненный шар наносит вам {dmg} урона.")
    elif spell_id == "ice_bolt":
        dmg = state.rng.randint(5, 8)
        state.player.take_damage(dmg)
        apply_status(state.player, "slowed", 3, state=state)
        state.log_message(f"Ледяная стрела наносит {dmg} урона и замедляет вас.")
    elif spell_id == "lightning_bolt":
        dmg = state.rng.randint(6, 10)
        state.player.take_damage(dmg)
        state.log_message(f"Молния ударяет вас на {dmg} урона.")
    else:
        dmg = state.rng.randint(3, 5)
        state.player.take_damage(dmg)
        state.log_message(f"Магическая стрела наносит {dmg} урона.")


def _mob_melee_attack(state: "GameState", mob) -> None:
    """Моб атакует игрока вблизи."""
    roll = state.rng.randint(1, 20)
    ac = state.player.ac

    if roll >= ac or roll == 20:
        count, sides, bonus = mob.dmg
        dmg = sum(state.rng.randint(1, sides) for _ in range(count)) + bonus
        dmg = max(0, dmg)
        state.player.take_damage(dmg)
        state.log_message(f"{mob.name} ранит вас на {dmg} урона.")
    else:
        state.log_message(f"{mob.name} промахивается.")


def _mob_ranged_attack(state: "GameState", mob) -> None:
    """Моб стреляет в игрока."""
    roll = state.rng.randint(1, 20)
    ac = state.player.ac

    if roll >= ac or roll == 20:
        count, sides, bonus = mob.dmg
        dmg = max(1, sum(state.rng.randint(1, sides) for _ in range(count)) + bonus - 1)
        state.player.take_damage(dmg)
        state.log_message(f"{mob.name} стреляет в вас на {dmg} урона!")
    else:
        state.log_message(f"{mob.name} промахивается дальним ударом.")


def _apply_hunger(state: "GameState") -> None:
    """Обработка голода каждый ход."""
    player = state.player
    if state.turn % 10 == 0:
        player.satiety = max(0, player.satiety - 1)

    # Регенерация при сытости
    if player.satiety >= 50 and state.turn % 20 == 0 and player.hp < player.max_hp:
        player.heal(1)

    # Урон при истощении
    if player.satiety == 0 and state.turn % 5 == 0:
        player.take_damage(1)
        state.log_message("Вы истощены! Голод отнимает здоровье.")

    # Предупреждения
    if player.satiety == 20 and state.turn % 10 == 0:
        state.log_message("Вы очень голодны.")
    elif player.satiety == 50 and state.turn % 10 == 0:
        state.log_message("Вы голодны.")


def _tick_player_status_effects(state: "GameState") -> None:
    """Тикнуть статус-эффекты игрока."""
    tick_status_effects(state.player, state)


def _regenerate_mana_tick(player) -> None:
    """Регенерация маны с учётом перка."""
    base_regen = 5  # каждые 5 ходов
    if "mana_regen" in player.perks:
        base_regen = max(1, base_regen - 1)
    # Используем глобальный turn из player? Нет, player не знает turn.
    # Будем регенерировать каждый вызов, но ограничивать частоту через внутренний счётчик.
    # Пока просто регеним 1 ману раз в 5 ходов, используя spell_cooldowns как счётчик.
    if not hasattr(player, "_mana_regen_counter"):
        player._mana_regen_counter = 0
    player._mana_regen_counter += 1
    if player._mana_regen_counter >= base_regen:
        player._mana_regen_counter = 0
        regenerate_mana(player)


def _pickup(state: "GameState") -> None:
    """Подобрать предметы с пола."""
    from content.items import get_item
    from systems.identification import get_display_name, is_identified

    pos = (state.player.x, state.player.y)
    items = state.items_on_floor.get(pos, [])
    if not items:
        state.log_message("Здесь нечего подбирать.")
        return

    picked = []
    remaining = []
    for item_id in items:
        data = get_item(item_id)
        if data is None:
            continue
        if item_id == "gold":
            amount = state.rng.randint(5, 20)
            state.player.gold += amount
            picked.append(f"{amount} золота")
        else:
            if state.player.total_inventory_count() >= 10:
                state.log_message("Рюкзак полон! Нельзя подобрать больше предметов.")
                remaining.append(item_id)
                continue
            state.player.inventory[item_id] = state.player.inventory.get(item_id, 0) + 1
            display_name = get_display_name(state, item_id)
            if not is_identified(state, item_id):
                display_name += " (неопознано)"
            picked.append(display_name)

    if remaining:
        state.items_on_floor[pos] = remaining
    else:
        del state.items_on_floor[pos]

    state.log_message("Вы подобрали: " + ", ".join(picked) + ".")


def _descend(state: "GameState") -> None:
    """Спуститься на следующий уровень."""
    state.depth += 1
    state.log_message("Вы спускаетесь по лестнице...")
    state.generate_level()
    save_game(state, AUTOSAVE_SLOT)


def _check_victory(state: "GameState") -> bool:
    """Проверить, побеждён ли финальный босс."""
    from world.final_floor import FINAL_DEPTH

    if state.depth < FINAL_DEPTH:
        return False
    for mob in state.mobs:
        if mob.id == "dark_lord" and mob.alive:
            return False
    return True


def _confirm_exit(stdscr: "_CursesWindow") -> bool:
    """Спросить подтверждение выхода."""
    height, width = stdscr.getmaxyx()
    msg = "Выйти из игры? Несохранённый прогресс сохранится в автосейв."
    from engine.text_utils import show_wrapped_message

    show_wrapped_message(stdscr, msg + " Enter — да, Esc — нет.")
    while True:
        key = stdscr.getch()
        if key in (10, 13, curses.KEY_ENTER):
            return True
        if key in (27, ord("n"), ord("N")):
            return False


def _handle_death(stdscr: "_CursesWindow", state: "GameState") -> None:
    """Обработать смерть игрока."""
    from systems.hall_of_fame import record_run

    recent = " | ".join(state.log[-5:])
    msg = (
        f"ВЫ ПОГИБЛИ на глубине {state.depth}. Счёт: {state.score}.\n\n"
        f"Последние события:\n{recent}\n\n"
        "Нажмите Enter для выхода."
    )
    show_message(stdscr, msg)
    while True:
        key = stdscr.getch()
        if key in (10, 13, curses.KEY_ENTER):
            break
    record_run(state.player_name, state, victory=False)
    delete_save(AUTOSAVE_SLOT)


def _handle_victory(stdscr: "_CursesWindow", state: "GameState") -> None:
    """Обработать победу над финальным боссом."""
    from systems.hall_of_fame import record_run

    msg = f"ПОБЕДА! Вы уничтожили Тёмного Владыку! Счёт: {state.score}. Нажмите Enter для выхода."
    show_message(stdscr, msg)
    while True:
        key = stdscr.getch()
        if key in (10, 13, curses.KEY_ENTER):
            break
    record_run(state.player_name, state, victory=True)
    delete_save(AUTOSAVE_SLOT)
