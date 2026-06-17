"""Инвентарь и UI экипировки."""

from __future__ import annotations

import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from curses import _CursesWindow
    from entities.player import Player
    from systems.game_state import GameState


MAX_BACKPACK_SIZE = 10


class InventoryUI:
    """UI инвентаря."""

    def __init__(self, stdscr: "_CursesWindow", player: "Player", game_state: "GameState"):
        self.stdscr = stdscr
        self.player = player
        self.game_state = game_state
        self.selection = 0
        self.mode = "backpack"  # "backpack" | "equipment"
        self._message = ""

    def run(self) -> bool:
        """Запустить UI. Возвращает True, если нужно пересчитать FOV/статы."""
        needs_refresh = False
        while True:
            self._draw()
            key = self.stdscr.getch()
            if key in (ord("i"), ord("I"), ord("q"), ord("Q"), 27):
                break
            if key == curses.KEY_UP:
                self.selection = max(0, self.selection - 1)
            elif key == curses.KEY_DOWN:
                self.selection = self.selection + 1
            elif key == curses.KEY_LEFT or key == curses.KEY_RIGHT:
                self._switch_mode()
            elif key in (ord("e"), ord("E")):
                if self._equip_selected():
                    needs_refresh = True
            elif key in (ord("d"), ord("D")):
                self._drop_selected()
            elif key in (ord("u"), ord("U")):
                if self._use_selected():
                    needs_refresh = True
        return needs_refresh

    def _switch_mode(self) -> None:
        if self.mode == "backpack":
            self.mode = "equipment"
            self.selection = 0
        else:
            self.mode = "backpack"
            self.selection = 0

    def _backpack_items(self) -> list[str]:
        """Список предметов в рюкзаке (с развёрткой стопок)."""
        from content.items import get_item

        items = []
        for item_id, count in sorted(self.player.inventory.items()):
            if count > 0 and get_item(item_id) and get_item(item_id)["type"] != "gold":
                for _ in range(count):
                    items.append(item_id)
        return items

    def _equipment_slots(self) -> list[tuple[str, str | None]]:
        """Список слотов экипировки."""
        return [
            ("Оружие", self.player.equipped_weapon),
            ("Броня", self.player.equipped_armor),
            ("Кольцо (левое)", self.player.equipped_left_ring),
            ("Кольцо (правое)", self.player.equipped_right_ring),
        ]

    def _display_name(self, item_id: str) -> str:
        """Имя предмета с учётом опознания."""
        from systems.identification import get_display_name
        return get_display_name(self.game_state, item_id)

    def _draw(self) -> None:
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        if height < 15 or width < 60:
            try:
                self.stdscr.addstr(0, 0, "Terminal too small")
            except curses.error:
                pass
            self.stdscr.refresh()
            return

        # Заголовок
        title = " ИНВЕНТАРЬ "
        self.stdscr.attron(curses.color_pair(9))
        self.stdscr.addstr(0, (width - len(title)) // 2, title)
        self.stdscr.attroff(curses.color_pair(9))

        # Статистика игрока
        stats = f"HP:{self.player.hp}/{self.player.max_hp} | ATK:{self.player.atk} | DEF:{self.player.ac} | SPD:{self.player.speed:.1f} | FOV:{self.player.fov_radius} | Сыт:{self.player.satiety}"
        self.stdscr.attron(curses.color_pair(10))
        self.stdscr.addstr(1, 2, stats[: width - 4])
        self.stdscr.attroff(curses.color_pair(10))

        # Левая панель — рюкзак
        left_w = width // 2 - 2
        left_x = 2
        self.stdscr.addstr(3, left_x, "РЮКЗАК" if self.mode == "backpack" else "рюкзак")
        bp = self._backpack_items()
        for idx, item_id in enumerate(bp[: MAX_BACKPACK_SIZE]):
            name = self._display_name(item_id)
            prefix = "> " if self.mode == "backpack" and idx == self.selection else "  "
            color = self._rarity_color(item_id)
            line = f"{prefix}{name[:left_w - 4]}"
            try:
                self.stdscr.addstr(4 + idx, left_x, line, curses.color_pair(color))
            except curses.error:
                pass

        # Индикатор заполненности
        count = len(bp)
        self.stdscr.addstr(4 + MAX_BACKPACK_SIZE + 1, left_x, f"Занято: {count}/{MAX_BACKPACK_SIZE}")

        # Правая панель — экипировка
        right_x = width // 2 + 1
        self.stdscr.addstr(3, right_x, "ЭКИПИРОВКА" if self.mode == "equipment" else "экипировка")
        slots = self._equipment_slots()
        for idx, (slot_name, item_id) in enumerate(slots):
            name = self._display_name(item_id) if item_id else "<пусто>"
            prefix = "> " if self.mode == "equipment" and idx == self.selection else "  "
            color = self._rarity_color(item_id) if item_id else 1
            line = f"{prefix}{slot_name}: {name[:left_w - len(slot_name) - 6]}"
            try:
                self.stdscr.addstr(4 + idx, right_x, line, curses.color_pair(color))
            except curses.error:
                pass

        # Подсказки
        help_y = height - 3
        action_key = "[e]снять" if self.mode == "equipment" else "[e]надеть"
        hints = f"[↑↓] выбор  [←→] вкладка  {action_key}  [d]выбросить  [u]использовать  [i/q/Esc] выход"
        self.stdscr.addstr(help_y, 2, hints[: width - 4])

        # Описание выбранного предмета
        desc_y = help_y - 4
        selected_id = self._selected_item_id()
        if selected_id:
            from systems.identification import get_description
            desc = get_description(self.game_state, selected_id)
            self.stdscr.addstr(desc_y, 2, desc[: width - 4])

        # Сообщение
        if self._message:
            self.stdscr.addstr(help_y - 2, 2, self._message[: width - 4], curses.color_pair(6))
            self._message = ""

        self.stdscr.refresh()

    def _selected_item_id(self) -> str | None:
        if self.mode == "backpack":
            bp = self._backpack_items()
            if 0 <= self.selection < len(bp):
                return bp[self.selection]
        else:
            slots = self._equipment_slots()
            if 0 <= self.selection < len(slots):
                return slots[self.selection][1]
        return None

    def _rarity_color(self, item_id: str | None) -> int:
        """Вернуть пару цветов для редкости предмета."""
        if not item_id:
            return 1
        from content.items import get_item, get_equipment_details
        data = get_item(item_id)
        if not data:
            return 1
        rarity = data.get("rarity", "common")
        if data["type"] in ("weapon", "armor"):
            details = get_equipment_details(item_id)
            if details:
                rarity = details.get("rarity", "common")
        return {
            "common": 1,
            "uncommon": 12,
            "rare": 15,
            "legendary": 13,
        }.get(rarity, 1)

    def _equip_selected(self) -> bool:
        """Надеть/снять выбранный предмет."""
        item_id = self._selected_item_id()
        if not item_id:
            return False
        from content.items import get_item
        data = get_item(item_id)
        if not data:
            return False

        if self.mode == "equipment":
            return self._unequip_selected_slot()

        if data["type"] == "weapon":
            if self.player.equipped_weapon and self._is_cursed(self.player.equipped_weapon):
                self._message = "Текущее оружие проклято! Нельзя его снять."
                return False
            if self.player.equipped_weapon:
                old = self.player.equipped_weapon
                self.player.inventory[old] = self.player.inventory.get(old, 0) + 1
            self.player.equipped_weapon = item_id
            self._remove_from_inventory(item_id, 1)
            return True
        if data["type"] == "armor":
            if self.player.equipped_armor and self._is_cursed(self.player.equipped_armor):
                self._message = "Текущая броня проклята! Нельзя её снять."
                return False
            if self.player.equipped_armor:
                old = self.player.equipped_armor
                self.player.inventory[old] = self.player.inventory.get(old, 0) + 1
            self.player.equipped_armor = item_id
            self._remove_from_inventory(item_id, 1)
            return True
        if data["type"] == "ring":
            if self.player.equipped_left_ring is None:
                self.player.equipped_left_ring = item_id
            elif self.player.equipped_right_ring is None:
                self.player.equipped_right_ring = item_id
            else:
                if not self._is_cursed(self.player.equipped_left_ring):
                    old = self.player.equipped_left_ring
                    self.player.inventory[old] = self.player.inventory.get(old, 0) + 1
                    self.player.equipped_left_ring = item_id
                elif not self._is_cursed(self.player.equipped_right_ring):
                    old = self.player.equipped_right_ring
                    self.player.inventory[old] = self.player.inventory.get(old, 0) + 1
                    self.player.equipped_right_ring = item_id
                else:
                    self._message = "Все кольца прокляты! Нельзя снять ни одно."
                    return False
            self._remove_from_inventory(item_id, 1)
            return True
        return False

    def _remove_from_inventory(self, item_id: str, count: int) -> None:
        if item_id in self.player.inventory:
            self.player.inventory[item_id] -= count
            if self.player.inventory[item_id] <= 0:
                del self.player.inventory[item_id]
            if self.mode == "backpack" and self.selection > 0:
                self.selection -= 1

    def _is_cursed(self, item_id: str) -> bool:
        """Проверить, является ли предмет проклятым."""
        from content.items import get_item, get_equipment_details
        data = get_item(item_id)
        if not data:
            return False
        if data["type"] in ("weapon", "armor"):
            details = get_equipment_details(item_id)
            return bool(details and details.get("cursed"))
        if data["type"] == "ring":
            effect = data.get("effect_power", {})
            return bool(effect.get("cursed"))
        return False

    def _unequip_selected_slot(self) -> bool:
        """Снять предмет из выбранного слота экипировки."""
        slots = self._equipment_slots()
        if self.selection < 0 or self.selection >= len(slots):
            return False
        slot_name, item_id = slots[self.selection]
        if not item_id:
            return False

        if self._is_cursed(item_id):
            self._message = "Предмет проклят! Ты не можешь его снять."
            return False

        self.player.inventory[item_id] = self.player.inventory.get(item_id, 0) + 1
        if slot_name == "Оружие":
            self.player.equipped_weapon = None
        elif slot_name == "Броня":
            self.player.equipped_armor = None
        elif slot_name == "Кольцо (левое)":
            self.player.equipped_left_ring = None
        elif slot_name == "Кольцо (правое)":
            self.player.equipped_right_ring = None
        return True

    def _drop_selected(self) -> None:
        """Выбросить выбранный предмет на пол под игроком."""
        item_id = self._selected_item_id()
        if not item_id:
            self._message = "Нечего выбрасывать."
            return

        from content.items import get_item
        data = get_item(item_id)
        if not data:
            self._message = "Неизвестный предмет."
            return

        # Если предмет надет — сначала снять (если не проклят)
        if self.mode == "equipment":
            if self._is_cursed(item_id):
                self._message = "Проклятый предмет нельзя снять."
                return
            if not self._unequip_selected_slot():
                self._message = "Не удалось снять предмет."
                return

        # Удаляем один экземпляр из инвентаря
        self._remove_from_inventory(item_id, 1)

        # Кладём на пол
        pos = (self.player.x, self.player.y)
        self.game_state.items_on_floor.setdefault(pos, []).append(item_id)

        self._message = f"Вы выбросили {data['name']}."
        if data["type"] == "gold":
            self._message = "Золото нельзя выбросить."

    def _use_selected(self) -> bool:
        """Использовать выбранный предмет (зелье/свиток/еда/артефакт)."""
        from content.items import get_item
        from systems.effects import apply_effect
        from systems.identification import identify_item, is_identified

        item_id = self._selected_item_id()
        if not item_id:
            return False
        data = get_item(item_id)
        if not data:
            return False

        item_type = data["type"]
        if item_type not in ("potion", "scroll", "food", "artifact", "spellbook"):
            self._message = "Этот предмет нельзя использовать таким образом."
            return False

        # Книги заклинаний обучают заклинанию
        if item_type == "spellbook":
            from systems.magic import learn_spell

            teaches = data.get("teaches")
            if teaches:
                msg = learn_spell(self.player, teaches)
                self._message = msg
                self._remove_from_inventory(item_id, 1)
                return True
            self._message = "Книга пуста."
            return False

        effect_id = data.get("effect")
        power = data.get("effect_power")

        # Свиток опознания — особый случай
        if item_id == "scroll_identify":
            target = self._choose_identify_target()
            if target:
                msg = identify_item(self.game_state, target)
                self._message = msg
                self._remove_from_inventory(item_id, 1)
                return True
            self._message = "Нет неопознанных предметов."
            return False

        # Артефакты используются один раз и дают постоянный бонус
        if item_type == "artifact":
            msg = apply_effect(effect_id, self.player, self.game_state, power)
            self._message = msg
            self._remove_from_inventory(item_id, 1)
            return True

        # Обычные расходники
        was_identified = is_identified(self.game_state, item_id)
        msg = apply_effect(effect_id, self.player, self.game_state, power)
        self._message = msg
        self._remove_from_inventory(item_id, 1)

        # Автоопознание после использования
        if not was_identified:
            identify_msg = identify_item(self.game_state, item_id)
            self._message += " " + identify_msg
        return True

    def _choose_identify_target(self) -> str | None:
        """Выбрать первый неопознанный предмет в рюкзаке/экипировке."""
        from systems.identification import is_identified

        for item_id in self.player.inventory:
            if not is_identified(self.game_state, item_id):
                return item_id
        for item_id in self.player.equipped_items():
            if not is_identified(self.game_state, item_id):
                return item_id
        return None


def open_inventory(stdscr: "_CursesWindow", player: "Player", game_state: "GameState") -> bool:
    """Открыть инвентарь. Возвращает True, если нужно пересчитать FOV/статы."""
    ui = InventoryUI(stdscr, player, game_state)
    return ui.run()
