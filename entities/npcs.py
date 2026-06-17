"""NPC и торговля."""

from __future__ import annotations

import curses
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from curses import _CursesWindow
    from entities.player import Player
    from systems.game_state import GameState


@dataclass
class NPC:
    id: str
    name: str
    char: str
    unicode_char: str
    color: str
    x: int
    y: int
    greeting: str
    farewell: str
    shop_items: list[str] = field(default_factory=list)
    buy_modifier: float = 1.0
    sell_modifier: float = 0.5
    dialogue: list[dict] = field(default_factory=list)

    def get_price(self, item_id: str, buying: bool = True) -> int:
        from content.items import get_item
        data = get_item(item_id)
        if not data:
            return 0
        base = data.get("value", 10)
        if buying:
            return int(base * self.buy_modifier)
        return max(1, int(base * self.sell_modifier))

    def talk(self, player: "Player") -> str:
        for entry in self.dialogue:
            condition = entry.get("condition", "default")
            if condition == "first_meeting":
                return entry["text"]
            if condition == "low_gold" and player.gold < 20:
                return entry["text"]
        # default
        for entry in self.dialogue:
            if entry.get("condition") == "default":
                return entry["text"]
        return self.greeting


NPC_TEMPLATES: dict[str, dict] = {
    "merchant": {
        "name": "Странствующий торговец",
        "char": "@",
        "unicode_char": "🧑‍💼",
        "color": "yellow",
        "greeting": "А-а, путник! Заходи, не стесняйся.",
        "farewell": "Удачи в глубинах.",
        "inventory_pool": ["potion_healing", "potion_mana", "scroll_identify", "scroll_teleport", "bread", "ration"],
        "inventory_size": 6,
        "buy_modifier": 1.2,
        "sell_modifier": 0.5,
        "dialogue": [
            {"condition": "first_meeting", "text": "Я обхожу все семь уровней. Если выживешь — увидимся снова."},
            {"condition": "low_gold", "text": "У тебя пусто в кошельке. Возвращайся, когда поднимешь золото."},
            {"condition": "default", "text": "Что желаешь?"},
        ],
    },
    "smith": {
        "name": "Кузнец",
        "char": "@",
        "unicode_char": "⚒",
        "color": "brown",
        "greeting": "Качественная сталь и надёжные заклёпки.",
        "farewell": "Пусть твой клинок остаётся острым.",
        "inventory_pool": [],
        "inventory_size": 0,
        "buy_modifier": 1.0,
        "sell_modifier": 0.0,
        "dialogue": [
            {"condition": "default", "text": "За 100 золота я улучшу твоё оружие или броню на +1."},
        ],
    },
    "alchemist": {
        "name": "Алхимик",
        "char": "@",
        "unicode_char": "⚗",
        "color": "green",
        "greeting": "Зелья, эликсиры, приворотные отвары...",
        "farewell": "Не перепутай флаконы.",
        "inventory_pool": ["potion_healing", "potion_mana", "potion_speed", "potion_invisibility", "potion_fire_breath"],
        "inventory_size": 4,
        "buy_modifier": 1.1,
        "sell_modifier": 0.6,
        "dialogue": [
            {"condition": "default", "text": "У меня лучшие зелья в подземелье."},
        ],
    },
    "spellvendor": {
        "name": "Заклинатель",
        "char": "@",
        "unicode_char": "🔮",
        "color": "magenta",
        "greeting": "Знание — самая мощная валюта.",
        "farewell": "Пусть магия течёт сквозь тебя.",
        "inventory_pool": ["spellbook_lightning", "spellbook_ice_bolt", "spellbook_barrier", "spellbook_haste", "spellbook_teleport"],
        "inventory_size": 3,
        "buy_modifier": 1.3,
        "sell_modifier": 0.4,
        "dialogue": [
            {"condition": "default", "text": "Ищешь силу? У меня есть книги, которых не найти в библиотеках смертных."},
        ],
    },
    "prisoner": {
        "name": "Пленник",
        "char": "@",
        "unicode_char": "⛓",
        "color": "white",
        "greeting": "Прошу, помоги мне...",
        "farewell": "Спасибо. Я не забуду этого.",
        "inventory_pool": [],
        "inventory_size": 0,
        "buy_modifier": 1.0,
        "sell_modifier": 0.0,
        "dialogue": [
            {"condition": "default", "text": "Они держат меня здесь уже недели. Освободи меня — и я отблагодарю."},
        ],
    },
}


def create_npc(npc_id: str, x: int, y: int, rng: random.Random | None = None) -> NPC:
    """Создать NPC по шаблону."""
    if rng is None:
        rng = random.Random()
    template = NPC_TEMPLATES[npc_id]
    pool = list(template.get("inventory_pool", []))
    size = min(template.get("inventory_size", 0), len(pool))
    shop_items = rng.sample(pool, size) if size > 0 else []
    return NPC(
        id=npc_id,
        name=template["name"],
        char=template["char"],
        unicode_char=template.get("unicode_char", template["char"]),
        color=template["color"],
        x=x,
        y=y,
        greeting=template["greeting"],
        farewell=template["farewell"],
        shop_items=shop_items,
        buy_modifier=template.get("buy_modifier", 1.0),
        sell_modifier=template.get("sell_modifier", 0.5),
        dialogue=template.get("dialogue", []),
    )


def trade_ui(stdscr: "_CursesWindow", player: "Player", npc: NPC, state: "GameState") -> str:
    """UI торговли. Возвращает сообщение в лог."""
    from content.items import get_item

    mode = "buy"  # "buy" | "sell"
    selection = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = f" {npc.name} | Золото: {player.gold} "
        try:
            stdscr.attron(curses.color_pair(9))
            stdscr.addstr(0, (width - len(title)) // 2, title)
            stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        # Левая панель — товар NPC (buy)
        left_x = 2
        left_w = width // 2 - 4
        stdscr.addstr(2, left_x, "КУПИТЬ" if mode == "buy" else "купить")
        for idx, item_id in enumerate(npc.shop_items):
            data = get_item(item_id)
            if not data:
                continue
            price = npc.get_price(item_id, buying=True)
            prefix = "> " if mode == "buy" and idx == selection else "  "
            line = f"{prefix}{data['name'][:20]} ({price} зол)"
            try:
                stdscr.addstr(3 + idx, left_x, line[:left_w])
            except curses.error:
                pass

        # Правая панель — инвентарь игрока (sell)
        right_x = width // 2 + 1
        right_w = width // 2 - 4
        stdscr.addstr(2, right_x, "ПРОДАТЬ" if mode == "sell" else "продать")
        player_items = [iid for iid, count in player.inventory.items() if count > 0 and iid != "gold"]
        for idx, item_id in enumerate(player_items):
            data = get_item(item_id)
            if not data:
                continue
            price = npc.get_price(item_id, buying=False)
            prefix = "> " if mode == "sell" and idx == selection else "  "
            line = f"{prefix}{data['name'][:20]} x{player.inventory[item_id]} ({price} зол)"
            try:
                stdscr.addstr(3 + idx, right_x, line[:right_w])
            except curses.error:
                pass

        # Подсказки
        hints = "[Tab] сменить режим  [Enter] купить/продать  [Esc] уйти"
        try:
            stdscr.addstr(height - 2, 2, hints[: width - 4], curses.color_pair(9))
        except curses.error:
            pass

        stdscr.refresh()
        key = stdscr.getch()

        if key in (27, ord("q"), ord("Q")):
            return npc.farewell
        if key == ord("\t") or key == curses.KEY_BTAB:
            mode = "sell" if mode == "buy" else "buy"
            selection = 0
        elif key == curses.KEY_UP:
            selection = max(0, selection - 1)
        elif key == curses.KEY_DOWN:
            items = npc.shop_items if mode == "buy" else player_items
            selection = min(len(items) - 1, selection + 1)
        elif key in (10, 13, curses.KEY_ENTER):
            if mode == "buy":
                if not npc.shop_items:
                    continue
                item_id = npc.shop_items[selection]
                price = npc.get_price(item_id, buying=True)
                if player.gold < price:
                    return f"Недостаточно золота для {get_item(item_id)['name']}."
                if player.total_inventory_count() >= 10:
                    return "Рюкзак полон."
                player.gold -= price
                player.inventory[item_id] = player.inventory.get(item_id, 0) + 1
                return f"Вы купили {get_item(item_id)['name']} за {price} золота."
            else:
                if not player_items:
                    continue
                item_id = player_items[selection]
                price = npc.get_price(item_id, buying=False)
                player.gold += price
                player.inventory[item_id] -= 1
                if player.inventory[item_id] <= 0:
                    del player.inventory[item_id]
                return f"Вы продали {get_item(item_id)['name']} за {price} золота."


def smith_ui(stdscr: "_CursesWindow", player: "Player", npc: NPC, state: "GameState") -> str:
    """UI кузнеца: улучшить оружие/броню за 100 золота."""
    from content.items import get_item, get_equipment_details

    options = []
    if player.equipped_weapon:
        data = get_item(player.equipped_weapon)
        options.append(("weapon", f"{data['name']} (+1 урона)", player.equipped_weapon))
    if player.equipped_armor:
        data = get_item(player.equipped_armor)
        options.append(("armor", f"{data['name']} (+1 защиты)", player.equipped_armor))

    if not options:
        return "У вас нет экипировки для улучшения."

    selection = 0
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        title = f" {npc.name} | Золото: {player.gold} "
        try:
            stdscr.attron(curses.color_pair(9))
            stdscr.addstr(0, (width - len(title)) // 2, title)
            stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        try:
            stdscr.addstr(2, 2, "Улучшение стоит 100 золота.")
        except curses.error:
            pass

        for idx, (slot, label, item_id) in enumerate(options):
            prefix = "> " if idx == selection else "  "
            try:
                stdscr.addstr(4 + idx, 2, f"{prefix}{label}")
            except curses.error:
                pass

        try:
            stdscr.addstr(height - 2, 2, "Enter — улучшить, Esc — уйти", curses.color_pair(9))
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27,):
            return npc.farewell
        if key == curses.KEY_UP:
            selection = max(0, selection - 1)
        elif key == curses.KEY_DOWN:
            selection = min(len(options) - 1, selection + 1)
        elif key in (10, 13, curses.KEY_ENTER):
            if player.gold < 100:
                return "Недостаточно золота."
            slot, label, item_id = options[selection]
            details = get_equipment_details(item_id)
            if not details:
                return "Невозможно улучшить."
            if slot == "weapon":
                d_min, d_max = details["damage"]
                details["damage"] = (d_min + 1, d_max + 1)
            else:
                details["defense"] = details.get("defense", 0) + 1
            player.gold -= 100
            from systems.stats import recalculate_stats
            recalculate_stats(player)
            return f"{get_item(item_id)['name']} улучшен."


def prisoner_ui(stdscr: "_CursesWindow", state: "GameState", npc: NPC) -> str:
    """UI пленника: освободить или оставить."""
    import random

    options = [
        ("free", "Освободить (требуется просто подойти и помочь)"),
        ("leave", "Уйти"),
    ]
    selection = 0
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        title = f" {npc.name} "
        try:
            stdscr.attron(curses.color_pair(9))
            stdscr.addstr(0, (width - len(title)) // 2, title)
            stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        try:
            stdscr.addstr(2, 2, npc.talk(state.player)[: width - 4])
        except curses.error:
            pass

        for idx, (action_id, label) in enumerate(options):
            prefix = "> " if idx == selection else "  "
            try:
                stdscr.addstr(4 + idx, 2, f"{prefix}{label}"[: width - 4])
            except curses.error:
                pass

        try:
            stdscr.addstr(height - 2, 2, "↑↓ выбор, Enter — подтвердить, Esc — уйти", curses.color_pair(9))
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27,):
            return npc.farewell
        if key == curses.KEY_UP:
            selection = (selection - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selection = (selection + 1) % len(options)
        elif key in (10, 13, curses.KEY_ENTER):
            action_id = options[selection][0]
            if action_id == "leave":
                return npc.farewell

            # Освобождаем пленника
            state.npcs.remove(npc)
            rng = state.rng
            reward_type = rng.choice(["gold", "item", "xp"])
            if reward_type == "gold":
                amount = rng.randint(50, 100)
                state.player.gold += amount
                return f"Вы освободили {npc.name}. В благодарность он отдал {amount} золота."
            elif reward_type == "xp":
                amount = rng.randint(40, 80)
                from systems.progression import add_xp
                add_xp(state.player, amount)
                return f"Вы освободили {npc.name}. Его история вдохновила вас (+{amount} опыта)."
            else:
                from content.items import items_for_depth, get_item
                pool = items_for_depth(state.depth)
                if pool:
                    item_id = rng.choice(pool)
                    state.player.inventory[item_id] = state.player.inventory.get(item_id, 0) + 1
                    item_name = get_item(item_id)["name"]
                    return f"Вы освободили {npc.name}. Он отдал вам {item_name}."
                state.player.gold += 50
                return f"Вы освободили {npc.name}. Он отдал вам 50 золота."


def interact_with_npc(stdscr: "_CursesWindow", state: "GameState", npc: NPC) -> str:
    """Взаимодействие с NPC: диалог, торговля или кузнец."""
    if npc.id == "smith":
        return smith_ui(stdscr, state.player, npc, state)
    if npc.id in ("merchant", "alchemist", "spellvendor"):
        return trade_ui(stdscr, state.player, npc, state)
    if npc.id == "prisoner":
        return prisoner_ui(stdscr, state, npc)
    return npc.talk(state.player)
