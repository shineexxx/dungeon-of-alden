"""Журнал игрока: бестиарий, лор, достижения."""

from __future__ import annotations

import curses
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from curses import _CursesWindow


@dataclass
class Journal:
    seen_monsters: dict[str, int] = field(default_factory=dict)  # monster_id -> kills
    seen_items: set[str] = field(default_factory=set)
    visited_biomes: set[str] = field(default_factory=set)
    visited_events: set[str] = field(default_factory=set)
    lore_fragments: list[str] = field(default_factory=list)
    achievements: set[str] = field(default_factory=set)

    def record_kill(self, monster_id: str) -> None:
        self.seen_monsters[monster_id] = self.seen_monsters.get(monster_id, 0) + 1

    def record_item(self, item_id: str) -> None:
        self.seen_items.add(item_id)

    def record_biome(self, biome_id: str) -> None:
        self.visited_biomes.add(biome_id)

    def record_event(self, event_id: str) -> None:
        self.visited_events.add(event_id)

    def record_lore(self, lore_text: str) -> None:
        if lore_text not in self.lore_fragments:
            self.lore_fragments.append(lore_text)

    def add_achievement(self, achievement_id: str) -> None:
        self.achievements.add(achievement_id)

    def to_dict(self) -> dict:
        return {
            "seen_monsters": dict(self.seen_monsters),
            "seen_items": sorted(self.seen_items),
            "visited_biomes": sorted(self.visited_biomes),
            "visited_events": sorted(self.visited_events),
            "lore_fragments": list(self.lore_fragments),
            "achievements": sorted(self.achievements),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Journal":
        return cls(
            seen_monsters=dict(data.get("seen_monsters", {})),
            seen_items=set(data.get("seen_items", [])),
            visited_biomes=set(data.get("visited_biomes", [])),
            visited_events=set(data.get("visited_events", [])),
            lore_fragments=list(data.get("lore_fragments", [])),
            achievements=set(data.get("achievements", [])),
        )


def show_journal(stdscr: "_CursesWindow", journal: "Journal") -> None:
    """Показать журнал с табами."""
    from content.monsters import get_monster
    from content.items import get_item

    tabs = ["Монстры", "Предметы", "Места", "Лор", "Достижения"]
    tab_idx = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Заголовок табов
        header = "  ".join(f"[{t}]" if i == tab_idx else t for i, t in enumerate(tabs))
        try:
            stdscr.attron(curses.color_pair(9))
            stdscr.addstr(0, 2, header[: width - 4])
            stdscr.attroff(curses.color_pair(9))
        except curses.error:
            pass

        content = []
        if tab_idx == 0:
            content.append("БЕСТИАРИЙ")
            if not journal.seen_monsters:
                content.append("Вы ещё не встретили ни одного монстра.")
            else:
                for mid, kills in sorted(journal.seen_monsters.items()):
                    data = get_monster(mid)
                    name = data["name"] if data else mid
                    known = kills >= 3
                    desc = data.get("description", "???") if known and data else "???"
                    line = f"{name}: убито {kills}"
                    if known:
                        line += f" | HP~{data['hp']} ATK~{data['atk']} AC~{data['ac']} | {desc[:60]}"
                    else:
                        line += " (убейте ещё, чтобы узнать больше)"
                    content.append(line)
        elif tab_idx == 1:
            content.append("ОПОЗНАННЫЕ ПРЕДМЕТЫ")
            if not journal.seen_items:
                content.append("Вы ещё не опознали предметов.")
            else:
                for iid in sorted(journal.seen_items):
                    data = get_item(iid)
                    name = data["name"] if data else iid
                    desc = data.get("description", "") if data else ""
                    content.append(f"{name}: {desc[:80]}")
        elif tab_idx == 2:
            content.append("ПОСЕЩЁННЫЕ МЕСТА")
            if not journal.visited_biomes:
                content.append("Пока ничего.")
            else:
                for biome_id in sorted(journal.visited_biomes):
                    content.append(biome_id)
            content.append("")
            content.append("СОБЫТИЯ")
            if not journal.visited_events:
                content.append("Пока ничего.")
            else:
                for event_id in sorted(journal.visited_events):
                    from content.events import get_event
                    ev = get_event(event_id)
                    content.append(ev["name"] if ev else event_id)
        elif tab_idx == 3:
            content.append("ЛОР")
            if not journal.lore_fragments:
                content.append("Вы ещё не нашли ни одной надписи.")
            else:
                for text in journal.lore_fragments:
                    content.append(f"• {text}")
        elif tab_idx == 4:
            content.append("ДОСТИЖЕНИЯ")
            if not journal.achievements:
                content.append("Пока нет достижений.")
            else:
                for ach in sorted(journal.achievements):
                    content.append(f"✓ {ach}")

        # Вывод контента
        for i, line in enumerate(content[: height - 4]):
            try:
                stdscr.addstr(2 + i, 2, line[: width - 4])
            except curses.error:
                pass

        try:
            stdscr.addstr(height - 2, 2, "←→ табы, Esc — закрыть", curses.color_pair(9))
        except curses.error:
            pass
        stdscr.refresh()

        key = stdscr.getch()
        if key in (27, ord("j"), ord("J")):
            return
        if key == curses.KEY_LEFT:
            tab_idx = (tab_idx - 1) % len(tabs)
        elif key == curses.KEY_RIGHT:
            tab_idx = (tab_idx + 1) % len(tabs)
