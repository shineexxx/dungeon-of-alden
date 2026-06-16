"""Система опознания предметов.

Каждый вид зелья/свитка в начале забега получает случайное неопознанное имя.
После первого использования/опознания все такие же предметы в инвентаре
и на полу становятся известны игроку.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from systems.game_state import GameState


# Пулы случайных имён по категориям
POTION_ADJECTIVES = [
    "красное", "синее", "пузырящееся", "мутное", "светящееся",
    "вязкое", "дымящееся", "пахучее", "искристое", "тёмное",
    "молочное", "радужное", "зелёное", "фиолетовое", "оранжевое",
]

SCROLL_ADJECTIVES = [
    "со странными рунами", "с печатью орла", "потрёпанный",
    "горящий синим", "пыльный", "с печатью змеи",
    "запечатанный воском", "с кровавой надписью", "с золотым ободком",
    "из шкуры ящерицы", "с печатью дракона",
]


def generate_identification_state(rng: random.Random) -> dict:
    """Сгенерировать случайное соответствие id предмета → неопознанное имя.

    Возвращает словарь:
        {
            "potion": {"potion_healing": "красное", ...},
            "scroll": {"scroll_identify": "со странными рунами", ...},
            "identified": set()  # id предметов, которые уже опознаны
        }
    """
    from content.items import ITEMS

    state = {
        "potion": {},
        "scroll": {},
        "identified": set(),
    }

    potion_ids = [iid for iid, data in ITEMS.items() if data["type"] == "potion"]
    scroll_ids = [iid for iid, data in ITEMS.items() if data["type"] == "scroll"]

    rng.shuffle(POTION_ADJECTIVES)
    rng.shuffle(SCROLL_ADJECTIVES)

    for idx, iid in enumerate(potion_ids):
        adj = POTION_ADJECTIVES[idx % len(POTION_ADJECTIVES)]
        state["potion"][iid] = adj

    for idx, iid in enumerate(scroll_ids):
        adj = SCROLL_ADJECTIVES[idx % len(SCROLL_ADJECTIVES)]
        state["scroll"][iid] = adj

    # Предметы, опознанные по умолчанию
    for iid, data in ITEMS.items():
        if data.get("identified_by_default"):
            state["identified"].add(iid)

    return state


def get_display_name(game_state: "GameState", item_id: str) -> str:
    """Вернуть имя предмета для отображения в UI."""
    from content.items import get_item

    data = get_item(item_id)
    if not data:
        return item_id

    # Если предмет опознан — показываем настоящее имя
    if is_identified(game_state, item_id):
        return data["name"]

    item_type = data["type"]
    if item_type == "potion":
        adj = game_state.identification["potion"].get(item_id, "неизвестное")
        return f"зелье ({adj})"
    if item_type == "scroll":
        adj = game_state.identification["scroll"].get(item_id, "неизвестный")
        return f"свиток {adj}"

    # Для остальных типов показываем настоящее имя
    return data["name"]


def is_identified(game_state: "GameState", item_id: str) -> bool:
    """Опознан ли предмет?"""
    if item_id in game_state.identification["identified"]:
        return True
    from content.items import get_item
    data = get_item(item_id)
    if data and data.get("identified_by_default"):
        return True
    return False


def identify_item(game_state: "GameState", item_id: str) -> str:
    """Опознать предмет. Возвращает сообщение."""
    from content.items import get_item

    if is_identified(game_state, item_id):
        data = get_item(item_id)
        name = data["name"] if data else item_id
        return f"{name} уже опознан."

    game_state.identification["identified"].add(item_id)
    data = get_item(item_id)
    name = data["name"] if data else item_id
    return f"Это было {name}!"


def identify_all_of_type(game_state: "GameState", item_id: str) -> None:
    """Автоматически опознать все предметы того же типа (для зелий/свитков).
    В данной реализации опознаём только конкретный id."""
    identify_item(game_state, item_id)


def serialize_identification(ident_state: dict) -> dict:
    """Сериализовать состояние опознания для сохранения."""
    return {
        "potion": dict(ident_state["potion"]),
        "scroll": dict(ident_state["scroll"]),
        "identified": list(ident_state["identified"]),
    }


def deserialize_identification(data: dict) -> dict:
    """Десериализовать состояние опознания."""
    return {
        "potion": dict(data.get("potion", {})),
        "scroll": dict(data.get("scroll", {})),
        "identified": set(data.get("identified", [])),
    }
