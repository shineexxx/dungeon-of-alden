"""Интерактивные объекты и эффекты событий спецкомнат."""

from __future__ import annotations

import curses
import random
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from curses import _CursesWindow
    from systems.game_state import GameState


# Реестр интерактивных объектов (тайлы на карте)
INTERACTABLES: dict[str, dict] = {
    "altar": {"char": "_", "color": "red", "name": "алтарь"},
    "fountain": {"char": "F", "color": "blue", "name": "фонтан"},
    "chest": {"char": "C", "color": "yellow", "name": "сундук"},
    "tablet": {"char": "?", "color": "white", "name": "табличка"},
    "lever": {"char": "L", "color": "brown", "name": "рычаги"},
    "circle": {"char": "O", "color": "magenta", "name": "жертвенный круг"},
    "lore": {"char": '"', "color": "cyan", "name": "надпись"},
    "cache": {"char": "$", "color": "yellow", "name": "тайник"},
    "trap_door": {"char": "T", "color": "red", "name": "засада"},
    "spirit": {"char": "G", "color": "white", "name": "дух"},
    "npc": {"char": "@", "color": "yellow", "name": "NPC"},
    "rubble": {"char": "R", "color": "brown", "name": "завалы"},
}


def get_interactable(interactable_id: str) -> dict | None:
    return INTERACTABLES.get(interactable_id)


# Реестр эффектов событий
EventEffect = Callable[["GameState", dict, dict], str]
EVENT_EFFECTS: dict[str, EventEffect] = {}


def register_event_effect(effect_id: str, func: EventEffect) -> None:
    EVENT_EFFECTS[effect_id] = func


def apply_event_effect(effect_id: str | None, state: "GameState", choice: dict, event: dict) -> str:
    if effect_id is None:
        return "Вы решили ничего не делать."
    effect = EVENT_EFFECTS.get(effect_id)
    if effect is None:
        return "Ничего не произошло."
    return effect(state, choice, event)


def handle_event(stdscr: "_CursesWindow", state: "GameState", event: dict) -> str:
    """Показать окно события и вернуть сообщение в лог."""
    choices = event.get("choices", [])
    selection = 0
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = f" {event['name'].upper()} "
        try:
            stdscr.attron(curses.color_pair(9))
            stdscr.addstr(1, (width - len(title)) // 2, title)
            stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        # Описание с переносом строк
        desc = event.get("description", "")
        lines = _wrap_text(desc, width - 6)
        for i, line in enumerate(lines[: height - 8]):
            try:
                stdscr.addstr(3 + i, 3, line)
            except curses.error:
                pass

        # Варианты выбора
        base_y = 5 + len(lines)
        for idx, choice in enumerate(choices):
            prefix = "> " if idx == selection else "  "
            line = f"{prefix}{choice['key']}. {choice['label']}"
            try:
                stdscr.addstr(base_y + idx, 3, line[: width - 6])
            except curses.error:
                pass

        try:
            stdscr.addstr(height - 2, 3, "↑↓ выбор, Enter — подтвердить, Esc — уйти", curses.color_pair(9))
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27,):
            return "Вы решили уйти."
        if key == curses.KEY_UP:
            selection = (selection - 1) % max(1, len(choices))
        elif key == curses.KEY_DOWN:
            selection = (selection + 1) % max(1, len(choices))
        elif key in (10, 13, curses.KEY_ENTER):
            if not choices:
                return "Нечего выбирать."
            choice = choices[selection]
            # Проверка стоимости
            cost = choice.get("cost", {})
            if "hp" in cost and state.player.hp <= cost["hp"]:
                return "Недостаточно здоровья."
            if "gold" in cost and state.player.gold < cost["gold"]:
                return "Недостаточно золота."
            # Списать стоимость
            if "hp" in cost:
                state.player.take_damage(cost["hp"])
            if "gold" in cost:
                state.player.gold -= cost["gold"]
            return apply_event_effect(choice.get("effect"), state, choice, event)


def _wrap_text(text: str, width: int) -> list[str]:
    """Простой перенос текста по словам."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines if lines else [""]


# --- Эффекты алтарей ---

def _altar_blood_sacrifice(state: "GameState", choice: dict, event: dict) -> str:
    state.player.atk += 2
    return "Алтарь принимает жертву. Ваша сила увеличена (+2 ATK)."


def _altar_wisdom_gain(state: "GameState", choice: dict, event: dict) -> str:
    from systems.progression import add_xp
    add_xp(state.player, 100)
    return "Знания наполняют разум. +100 XP."


def _altar_dark_curse(state: "GameState", choice: dict, event: dict) -> str:
    if not state.player.equipped_weapon:
        return "У вас нет оружия для жертвоприношения."
    from content.items import get_item, get_equipment_details
    wpn = state.player.equipped_weapon
    details = get_equipment_details(wpn)
    if details:
        d_min, d_max = details["damage"]
        details["damage"] = (d_min + 3, d_max + 3)
        details["cursed"] = True
    data = get_item(wpn)
    return f"{data['name']} впитал тьму: урон +3, но предмет проклят."


def _altar_holy_cleanse(state: "GameState", choice: dict, event: dict) -> str:
    from content.items import get_equipment_details
    for slot in ["weapon", "armor"]:
        item_id = getattr(state.player, f"equipped_{slot}")
        if item_id:
            details = get_equipment_details(item_id)
            if details:
                details["cursed"] = False
    state.player.heal(20)
    return "Святой свет смывает проклятия. +20 HP."


def _altar_fate_random(state: "GameState", choice: dict, event: dict) -> str:
    roll = random.random()
    if roll < 0.33:
        state.player.max_hp += 10
        state.player.hp += 10
        return "Судьба благосклонна: максимальное HP +10."
    elif roll < 0.66:
        state.player.atk += 3
        return "Судьба усиливает удар: ATK +3."
    else:
        from systems.effects import apply_status
        apply_status(state.player, "confused", 10, state=state)
        state.player.take_damage(8)
        return "Судьба обернулась против вас: замешательство и 8 урона."


# --- Эффекты фонтанов ---

def _fountain_heal(state: "GameState", choice: dict, event: dict) -> str:
    state.player.hp = state.player.max_hp
    return "Фонтан исцеляет все раны."


def _fountain_mana(state: "GameState", choice: dict, event: dict) -> str:
    state.player.mana = state.player.max_mana
    return "Мана полностью восстановлена."


def _fountain_random(state: "GameState", choice: dict, event: dict) -> str:
    roll = random.random()
    if roll < 0.4:
        state.player.max_hp += 5
        state.player.hp += 5
        return "Вода укрепляет тело. Макс HP +5."
    elif roll < 0.7:
        from systems.effects import apply_status
        apply_status(state.player, "poisoned", 8, state=state)
        return "Вода оказалась отравленной."
    else:
        state.player.fov_radius += 1
        return "Вода просветляет зрение. FOV +1."


# --- Эффекты сундуков ---

def _chest_pick(state: "GameState", choice: dict, event: dict) -> str:
    if random.random() < 0.35:
        dmg = random.randint(5, 10)
        state.player.take_damage(dmg)
        return f"В сундуке была ловушка! Вы получили {dmg} урона."
    # Редкий лут
    loot = random.choice(["potion_healing_major", "scroll_fireball", "ring_of_health", "spellbook_fireball"])
    state.player.inventory[loot] = state.player.inventory.get(loot, 0) + 1
    from content.items import get_item
    data = get_item(loot)
    return f"Взлом удался! Вы получили {data['name']}."


def _chest_mimic(state: "GameState", choice: dict, event: dict) -> str:
    from entities.mob import Mob
    mob = Mob.from_data("mimic", state.player.x, state.player.y)
    mob.hp = 40
    mob.max_hp = 40
    mob.dmg = (2, 6, 2)
    mob.ac = 3
    mob.xp = 50
    mob.gold_min = 20
    mob.gold_max = 50
    state.mobs.append(mob)
    return "Сундук ожил! Это мимик!"


def _cache_loot(state: "GameState", choice: dict, event: dict) -> str:
    gold = random.randint(30, 80)
    state.player.gold += gold
    loot = random.choice(["potion_healing", "scroll_identify", "potion_mana"])
    state.player.inventory[loot] = state.player.inventory.get(loot, 0) + 1
    return f"Тайник содержал {gold} золота и ценный предмет."


# --- Загадки и интерактив ---

def _riddle_correct(state: "GameState", choice: dict, event: dict) -> str:
    artifact = random.choice(["amulet_of_life", "crown_of_wisdom", "boots_of_wind", "eye_of_truth"])
    state.player.inventory[artifact] = state.player.inventory.get(artifact, 0) + 1
    from content.items import get_item
    data = get_item(artifact)
    return f"Правильно! Вы получили {data['name']}."


def _riddle_wrong(state: "GameState", choice: dict, event: dict) -> str:
    state.player.take_damage(5)
    return "Неверно. Механизм ударяет вас током. 5 урона."


def _lever_left(state: "GameState", choice: dict, event: dict) -> str:
    state.player.gold += 50
    return "Рычаг открывает тайник с 50 золота."


def _lever_middle(state: "GameState", choice: dict, event: dict) -> str:
    state.player.heal(20)
    return "Рычаг активирует исцеляющий поток. +20 HP."


def _lever_right(state: "GameState", choice: dict, event: dict) -> str:
    state.player.take_damage(10)
    return "Рычаг запускает ловушку. 10 урона."


def _circle_power(state: "GameState", choice: dict, event: dict) -> str:
    state.player.atk += 3
    from entities.mob import Mob
    from content.monsters import monsters_for_biome
    from content.biomes import get_biome
    biome = get_biome(state.dungeon.biome_id)
    tags = biome.get("monster_tags", []) if biome else []
    pool = monsters_for_biome(tags, state.depth)
    if pool:
        for _ in range(2):
            candidates = [
                (x, y)
                for x in range(max(0, state.player.x - 4), min(state.dungeon.width, state.player.x + 5))
                for y in range(max(0, state.player.y - 4), min(state.dungeon.height, state.player.y + 5))
                if state.dungeon.is_floor(x, y) and (x, y) != (state.player.x, state.player.y)
            ]
            if candidates:
                x, y = random.choice(candidates)
                state.mobs.append(Mob.from_data(random.choice(pool), x, y))
    return "Сила наполняет вас (+3 ATK), но круг пробуждает стражей!"


# --- NPC-эффекты ---

def _alchemist_identify(state: "GameState", choice: dict, event: dict) -> str:
    from systems.identification import identify_item, is_identified
    identified = 0
    for item_id in list(state.player.inventory.keys()):
        if not is_identified(state, item_id):
            identify_item(state, item_id)
            identified += 1
    return f"Алхимик опознал {identified} предметов."


def _prisoner_free(state: "GameState", choice: dict, event: dict) -> str:
    roll = random.random()
    if roll < 0.7:
        gold = random.randint(20, 50)
        state.player.gold += gold
        return f"Пленник благодарит вас и отдаёт {gold} золота."
    else:
        from entities.mob import Mob
        state.mobs.append(Mob.from_data("vampire", state.player.x, state.player.y))
        return "Пленник превращается в вампира! Это была ловушка!"


# --- Опасности/события ---

def _ambush_spawn(state: "GameState", choice: dict, event: dict) -> str:
    from entities.mob import Mob
    from content.monsters import monsters_for_biome
    from content.biomes import get_biome
    biome = get_biome(state.dungeon.biome_id)
    tags = biome.get("monster_tags", []) if biome else []
    pool = monsters_for_biome(tags, state.depth)
    if pool:
        for _ in range(3):
            candidates = [
                (x, y)
                for x in range(max(0, state.player.x - 5), min(state.dungeon.width, state.player.x + 6))
                for y in range(max(0, state.player.y - 5), min(state.dungeon.height, state.player.y + 6))
                if state.dungeon.is_floor(x, y) and (x, y) != (state.player.x, state.player.y)
            ]
            if candidates:
                x, y = random.choice(candidates)
                state.mobs.append(Mob.from_data(random.choice(pool), x, y))
    return "Из теней вырываются враги!"


def _collapse_loot(state: "GameState", choice: dict, event: dict) -> str:
    gold = random.randint(10, 30)
    state.player.gold += gold
    loot = random.choice(["potion_healing", "potion_mana", "bread"])
    state.player.inventory[loot] = state.player.inventory.get(loot, 0) + 1
    return f"В завалах вы находите {gold} золота и {loot}."


def _spirit_follow(state: "GameState", choice: dict, event: dict) -> str:
    from systems.effects import apply_status
    apply_status(state.player, "detecting", 50, state=state)
    return "Дух сливается с вашей аурой. Ловушки будут видны в течение долгого времени."


def _lore_read(state: "GameState", choice: dict, event: dict) -> str:
    from content.lore import random_lore_for
    lore = random_lore_for(state.dungeon.biome_id, state.depth, state.rng)
    if lore:
        state.journal.record_lore(lore["text"])
        return f"Вы читаете: {lore['text']}"
    return "Символы стёрты временем."


# Регистрация эффектов
EVENT_EFFECTS.update({
    "altar_blood_sacrifice": _altar_blood_sacrifice,
    "altar_wisdom_gain": _altar_wisdom_gain,
    "altar_dark_curse": _altar_dark_curse,
    "altar_holy_cleanse": _altar_holy_cleanse,
    "altar_fate_random": _altar_fate_random,
    "fountain_heal": _fountain_heal,
    "fountain_mana": _fountain_mana,
    "fountain_random": _fountain_random,
    "chest_pick": _chest_pick,
    "chest_mimic": _chest_mimic,
    "cache_loot": _cache_loot,
    "riddle_correct": _riddle_correct,
    "riddle_wrong": _riddle_wrong,
    "lever_left": _lever_left,
    "lever_middle": _lever_middle,
    "lever_right": _lever_right,
    "circle_power": _circle_power,
    "alchemist_identify": _alchemist_identify,
    "prisoner_free": _prisoner_free,
    "ambush_spawn": _ambush_spawn,
    "collapse_loot": _collapse_loot,
    "spirit_follow": _spirit_follow,
    "lore_read": _lore_read,
})
