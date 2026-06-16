"""Тесты настроек."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from systems.settings import Settings, load_settings, save_settings


def test_settings_defaults():
    s = Settings()
    assert s.use_unicode is True
    print("Settings defaults OK")


def test_settings_save_load():
    s = Settings(use_unicode=False)
    assert save_settings(s)
    loaded = load_settings()
    assert loaded.use_unicode is False
    print("Settings save/load OK")


if __name__ == "__main__":
    test_settings_defaults()
    test_settings_save_load()
    print("All settings tests passed")
