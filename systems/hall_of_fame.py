"""Зал славы — топ результатов."""

from __future__ import annotations

import curses
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from curses import _CursesWindow
    from systems.game_state import GameState


ROOT_DIR = Path(__file__).resolve().parent.parent
HALL_OF_FAME_FILE = ROOT_DIR / "saves" / "hall_of_fame.json"
MAX_ENTRIES = 10


@dataclass
class HallOfFameEntry:
    player_name: str
    depth: int
    score: int
    gold: int
    level: int
    victory: bool
    date: str
    total_score: int

    def to_dict(self) -> dict:
        return {
            "player_name": self.player_name,
            "depth": self.depth,
            "score": self.score,
            "gold": self.gold,
            "level": self.level,
            "victory": self.victory,
            "date": self.date,
            "total_score": self.total_score,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HallOfFameEntry":
        return cls(
            player_name=data.get("player_name", "Unknown"),
            depth=data.get("depth", 0),
            score=data.get("score", 0),
            gold=data.get("gold", 0),
            level=data.get("level", 1),
            victory=data.get("victory", False),
            date=data.get("date", ""),
            total_score=data.get("total_score", 0),
        )


def _ensure_dir() -> None:
    HALL_OF_FAME_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_hall_of_fame() -> list[HallOfFameEntry]:
    """Загрузить зал славы из файла."""
    if not HALL_OF_FAME_FILE.exists():
        return []
    try:
        with open(HALL_OF_FAME_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [HallOfFameEntry.from_dict(entry) for entry in data]
    except (json.JSONDecodeError, OSError):
        return []


def save_hall_of_fame(entries: list[HallOfFameEntry]) -> None:
    """Сохранить зал славы."""
    _ensure_dir()
    try:
        with open(HALL_OF_FAME_FILE, "w", encoding="utf-8") as f:
            json.dump([e.to_dict() for e in entries], f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def compute_total_score(state: "GameState", victory: bool = False) -> int:
    """Посчитать итоговые очки забега."""
    player = state.player
    total = state.depth * 100 + state.score + player.gold + player.level * 50
    if victory:
        total += 5000
    return total


def record_run(player_name: str, state: "GameState", victory: bool = False) -> None:
    """Записать результат забега в зал славы."""
    entries = load_hall_of_fame()
    total = compute_total_score(state, victory)
    entry = HallOfFameEntry(
        player_name=player_name or "Unknown",
        depth=state.depth,
        score=state.score,
        gold=state.player.gold,
        level=state.player.level,
        victory=victory,
        date=datetime.now().isoformat(),
        total_score=total,
    )
    entries.append(entry)
    entries.sort(key=lambda e: e.total_score, reverse=True)
    save_hall_of_fame(entries[:MAX_ENTRIES])


def show_hall_of_fame(stdscr: "_CursesWindow") -> None:
    """Показать зал славы."""
    entries = load_hall_of_fame()
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    title = " ЗАЛ СЛАВЫ "
    try:
        stdscr.attron(curses.color_pair(9))
        stdscr.addstr(1, (width - len(title)) // 2, title)
        stdscr.attroff(curses.color_pair(9))
    except curses.error:
        pass

    if not entries:
        try:
            stdscr.addstr(3, 2, "Пока нет записей.")
        except curses.error:
            pass
    else:
        header = f"{'#':<3} {'Имя':<15} {'Гл':<4} {'Очки':<8} {'Золото':<8} {'Ур':<4} {'Результат':<10}"
        try:
            stdscr.addstr(3, 2, header[: width - 4])
        except curses.error:
            pass
        for i, entry in enumerate(entries[:MAX_ENTRIES]):
            result = "ПОБЕДА" if entry.victory else "смерть"
            line = f"{i + 1:<3} {entry.player_name:<15} {entry.depth:<4} {entry.total_score:<8} {entry.gold:<8} {entry.level:<4} {result:<10}"
            try:
                stdscr.addstr(5 + i, 2, line[: width - 4])
            except curses.error:
                pass

    try:
        stdscr.addstr(height - 2, 2, "Любая клавиша — закрыть", curses.color_pair(9))
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()
