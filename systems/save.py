"""Система сохранений / загрузки."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from systems.game_state import GameState


ROOT_DIR = Path(__file__).resolve().parent.parent
SAVE_DIR = ROOT_DIR / "saves"
SAVE_VERSION = 7
AUTOSAVE_SLOT = "autosave"


def _ensure_dir() -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)


def slot_path(slot_name: str) -> Path:
    _ensure_dir()
    return SAVE_DIR / f"{slot_name}.json"


def list_slots() -> list[str]:
    """Вернуть список существующих слотов сохранений."""
    _ensure_dir()
    slots = []
    for p in SAVE_DIR.glob("*.json"):
        slots.append(p.stem)
    return sorted(slots)


def save_game(state: "GameState", slot_name: str = AUTOSAVE_SLOT) -> bool:
    """Сохранить текущее состояние в слот. Возвращает True при успехе."""
    _ensure_dir()
    path = slot_path(slot_name)
    data = state.to_dict()
    data["slot_name"] = slot_name
    data["saved_at"] = datetime.now().isoformat()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (OSError, TypeError) as e:
        print(f"Ошибка сохранения: {e}")
        return False


def load_game(slot_name: str) -> "GameState | None":
    """Загрузить состояние из слота. При ошибке вернуть None и сообщение."""
    from systems.game_state import GameState

    path = slot_path(slot_name)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        version = data.get("save_version", 0)
        if version != SAVE_VERSION:
            # Мягкая миграция: пока ничего не делаем, но предупреждаем
            data["log"] = data.get("log", []) + [
                f"[Сохранение версии {version}, ожидалась {SAVE_VERSION}]"
            ]
        return GameState.from_dict(data)
    except json.JSONDecodeError as e:
        print(f"Битый файл сохранения {slot_name}: {e}")
        return None
    except (OSError, KeyError, TypeError) as e:
        print(f"Ошибка загрузки {slot_name}: {e}")
        return None


def delete_save(slot_name: str) -> bool:
    """Удалить файл сохранения."""
    path = slot_path(slot_name)
    if path.exists():
        try:
            os.remove(path)
            return True
        except OSError:
            return False
    return False
