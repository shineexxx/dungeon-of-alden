"""Тест утилит переноса текста."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.text_utils import wrap_text


def test_wrap_text():
    lines = wrap_text("Это очень длинная строка для проверки переноса", 10)
    assert all(len(line) <= 10 for line in lines)
    assert len(lines) > 1
    print("Wrap text OK")


def test_wrap_long_word():
    lines = wrap_text("словоизбукв", 5)
    assert all(len(line) <= 5 for line in lines)
    print("Wrap long word OK")


if __name__ == "__main__":
    test_wrap_text()
    test_wrap_long_word()
    print("All text utils tests passed")
