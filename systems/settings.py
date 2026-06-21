"""Настройки игры."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
SETTINGS_FILE = ROOT_DIR / "saves" / "settings.json"


@dataclass
class Settings:
    use_unicode: bool = True
    fullscreen_log: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "use_unicode": self.use_unicode,
            "fullscreen_log": self.fullscreen_log,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Settings":
        return cls(
            use_unicode=data.get("use_unicode", True),
            fullscreen_log=data.get("fullscreen_log", False),
        )


def load_settings() -> Settings:
    """Загрузить настройки из файла или вернуть значения по умолчанию."""
    if not SETTINGS_FILE.exists():
        return Settings()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Settings.from_dict(data)
    except (json.JSONDecodeError, OSError):
        return Settings()


def save_settings(settings: Settings) -> bool:
    """Сохранить настройки."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings.to_dict(), f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False
