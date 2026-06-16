"""Таблица событий и спецкомнат.

СХЕМА ПОЛЕЙ:
    id              : str      уникальный ключ
    name            : str      название
    rarity          : str      common/uncommon/rare
    depth_min       : int      минимальная глубина
    biome_tags      : list     подходящие биомы (хотя бы один тег совпадает)
    room_size       : tuple    (w, h) размер спецкомнаты
    one_time        : bool     только одно на уровень
    description     : str      текст при входе
    choices         : list     {key, label, effect, cost}
    npc_id          : str|None если событие — NPC
    interactable    : str      id интерактивного объекта
"""

from __future__ import annotations

EVENTS: dict[str, dict] = {
    # --- Алтари ---
    "altar_blood": {
        "id": "altar_blood",
        "name": "Кровавый алтарь",
        "rarity": "uncommon",
        "depth_min": 3,
        "biome_tags": ["dungeon", "crypt", "hell"],
        "room_size": (5, 5),
        "one_time": False,
        "description": "Алтарь, пропитанный засохшей кровью. Принять жертву?",
        "choices": [
            {"key": "1", "label": "Пожертвовать 10 HP (+2 ATK)", "effect": "altar_blood_sacrifice", "cost": {"hp": 10}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "altar",
    },
    "altar_wisdom": {
        "id": "altar_wisdom",
        "name": "Алтарь мудрости",
        "rarity": "uncommon",
        "depth_min": 4,
        "biome_tags": ["dungeon", "crypt", "deep"],
        "room_size": (5, 5),
        "one_time": False,
        "description": "Алтарь светится мягким сиянием. Обменять кровь на знания?",
        "choices": [
            {"key": "1", "label": "Пожертвовать 10 HP (+100 XP)", "effect": "altar_wisdom_gain", "cost": {"hp": 10}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "altar",
    },
    "altar_dark": {
        "id": "altar_dark",
        "name": "Тёмный алтарь",
        "rarity": "rare",
        "depth_min": 6,
        "biome_tags": ["crypt", "hell", "deep"],
        "room_size": (5, 5),
        "one_time": False,
        "description": "Тени клубятся вокруг алтаря. Положить предмет — и получить силу ценой проклятия.",
        "choices": [
            {"key": "1", "label": "Пожертвовать экипированное оружие (бонус +3, проклятие)", "effect": "altar_dark_curse", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "altar",
    },
    "altar_holy": {
        "id": "altar_holy",
        "name": "Святой алтарь",
        "rarity": "rare",
        "depth_min": 5,
        "biome_tags": ["dungeon", "crypt"],
        "room_size": (5, 5),
        "one_time": False,
        "description": "Святой алтарь излучает покой. Снять проклятия?",
        "choices": [
            {"key": "1", "label": "Молиться (снять все проклятия, +20 HP)", "effect": "altar_holy_cleanse", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "altar",
    },
    "altar_fate": {
        "id": "altar_fate",
        "name": "Алтарь судьбы",
        "rarity": "rare",
        "depth_min": 8,
        "biome_tags": ["cave", "mushroom", "deep"],
        "room_size": (5, 5),
        "one_time": False,
        "description": "Алтарь мерцает непостижимыми цветами. Испытать судьбу?",
        "choices": [
            {"key": "1", "label": "Бросить жребий (случайный сильный эффект)", "effect": "altar_fate_random", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "altar",
    },

    # --- Фонтаны ---
    "fountain_clean": {
        "id": "fountain_clean",
        "name": "Чистый фонтан",
        "rarity": "common",
        "depth_min": 1,
        "biome_tags": ["dungeon", "cave", "crypt"],
        "room_size": (5, 5),
        "one_time": True,
        "description": "Кристально чистая вода журчит в фонтане. Выпить?",
        "choices": [
            {"key": "1", "label": "Выпить (полное исцеление)", "effect": "fountain_heal", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "fountain",
    },
    "fountain_mana": {
        "id": "fountain_mana",
        "name": "Зачарованный фонтан",
        "rarity": "uncommon",
        "depth_min": 3,
        "biome_tags": ["dungeon", "crypt", "deep"],
        "room_size": (5, 5),
        "one_time": True,
        "description": "Фонтан светится голубым. Восполнить ману?",
        "choices": [
            {"key": "1", "label": "Выпить (полное восстановление MP)", "effect": "fountain_mana", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "fountain",
    },
    "fountain_murky": {
        "id": "fountain_murky",
        "name": "Мутный фонтан",
        "rarity": "common",
        "depth_min": 2,
        "biome_tags": ["cave", "crypt", "mushroom"],
        "room_size": (5, 5),
        "one_time": True,
        "description": "Вода в фонтане мутная и пахнет грибами. Рискнуть?",
        "choices": [
            {"key": "1", "label": "Выпить (случайно: +стат / отравление / мутация)", "effect": "fountain_random", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "fountain",
    },

    # --- Сундуки ---
    "chest_locked": {
        "id": "chest_locked",
        "name": "Запертый сундук",
        "rarity": "uncommon",
        "depth_min": 2,
        "biome_tags": ["dungeon", "cave", "crypt"],
        "room_size": (4, 4),
        "one_time": True,
        "description": "Сундук заперт. Взломать или уйти?",
        "choices": [
            {"key": "1", "label": "Взломать (шанс ловушки, но есть редкий лут)", "effect": "chest_pick", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "chest",
    },
    "chest_mimic": {
        "id": "chest_mimic",
        "name": "Подозрительный сундук",
        "rarity": "rare",
        "depth_min": 5,
        "biome_tags": ["dungeon", "cave", "crypt", "deep"],
        "room_size": (4, 4),
        "one_time": True,
        "description": "Сундук слегка дрожит. Открыть?",
        "choices": [
            {"key": "1", "label": "Открыть", "effect": "chest_mimic", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "chest",
    },
    "hidden_cache": {
        "id": "hidden_cache",
        "name": "Тайник за разрушаемой стеной",
        "rarity": "uncommon",
        "depth_min": 3,
        "biome_tags": ["dungeon", "cave", "hell"],
        "room_size": (4, 4),
        "one_time": True,
        "description": "Вы нашли потайной тайник. Забрать содержимое?",
        "choices": [
            {"key": "1", "label": "Забрать золото и предмет", "effect": "cache_loot", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "cache",
    },

    # --- Загадки и интерактив ---
    "riddle_tablet": {
        "id": "riddle_tablet",
        "name": "Каменная табличка",
        "rarity": "uncommon",
        "depth_min": 4,
        "biome_tags": ["dungeon", "crypt", "deep"],
        "room_size": (5, 5),
        "one_time": True,
        "description": "На табличке выбита загадка. 'Я без голоса, но говорю; без крыльев, но летаю. Кто я?'",
        "choices": [
            {"key": "1", "label": "Эхо", "effect": "riddle_correct", "cost": {}},
            {"key": "2", "label": "Ветер", "effect": "riddle_wrong", "cost": {}},
            {"key": "3", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "tablet",
    },
    "lever_room": {
        "id": "lever_room",
        "name": "Комната с рычагами",
        "rarity": "rare",
        "depth_min": 6,
        "biome_tags": ["dungeon", "hell", "deep"],
        "room_size": (6, 6),
        "one_time": True,
        "description": "Три рычага. Какой потянуть?",
        "choices": [
            {"key": "1", "label": "Левый", "effect": "lever_left", "cost": {}},
            {"key": "2", "label": "Средний", "effect": "lever_middle", "cost": {}},
            {"key": "3", "label": "Правый", "effect": "lever_right", "cost": {}},
            {"key": "4", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "lever",
    },
    "sacrificial_circle": {
        "id": "sacrificial_circle",
        "name": "Жертвенный круг",
        "rarity": "rare",
        "depth_min": 7,
        "biome_tags": ["crypt", "hell", "deep"],
        "room_size": (6, 6),
        "one_time": True,
        "description": "Войти в круг — получить силу, но пробудить стража.",
        "choices": [
            {"key": "1", "label": "Войти (+урон, призвать мини-босса)", "effect": "circle_power", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "circle",
    },

    # --- NPC ---
    "npc_merchant": {
        "id": "npc_merchant",
        "name": "Странствующий торговец",
        "rarity": "common",
        "depth_min": 2,
        "biome_tags": ["dungeon", "cave", "crypt"],
        "room_size": (5, 5),
        "one_time": True,
        "description": "Странствующий торговец разложил товары.",
        "choices": [],
        "npc_id": "merchant",
        "interactable": "npc",
    },
    "npc_smith": {
        "id": "npc_smith",
        "name": "Кузнец",
        "rarity": "uncommon",
        "depth_min": 4,
        "biome_tags": ["dungeon", "hell"],
        "room_size": (5, 5),
        "one_time": True,
        "description": "Кузнец чинит и улучшает доспехи.",
        "choices": [],
        "npc_id": "smith",
        "interactable": "npc",
    },
    "npc_alchemist": {
        "id": "npc_alchemist",
        "name": "Алхимик",
        "rarity": "uncommon",
        "depth_min": 3,
        "biome_tags": ["cave", "mushroom", "crypt"],
        "room_size": (5, 5),
        "one_time": True,
        "description": "Алхимик предлагает опознать зелья за скромную плату.",
        "choices": [
            {"key": "1", "label": "Опознать все зелья (20 золота)", "effect": "alchemist_identify", "cost": {"gold": 20}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": "alchemist",
        "interactable": "npc",
    },
    "npc_spellvendor": {
        "id": "npc_spellvendor",
        "name": "Заклинатель",
        "rarity": "rare",
        "depth_min": 6,
        "biome_tags": ["crypt", "deep"],
        "room_size": (5, 5),
        "one_time": True,
        "description": "Заклинатель продаёт древние книги заклинаний.",
        "choices": [],
        "npc_id": "spellvendor",
        "interactable": "npc",
    },
    "npc_prisoner": {
        "id": "npc_prisoner",
        "name": "Пленник в клетке",
        "rarity": "uncommon",
        "depth_min": 3,
        "biome_tags": ["dungeon", "crypt", "hell"],
        "room_size": (5, 5),
        "one_time": True,
        "description": "В клетке сидит измождённый пленник. Освободить?",
        "choices": [
            {"key": "1", "label": "Высвободить (награда или предательство)", "effect": "prisoner_free", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": "prisoner",
        "interactable": "npc",
    },

    # --- Опасности/события ---
    "ambush_room": {
        "id": "ambush_room",
        "name": "Засада",
        "rarity": "uncommon",
        "depth_min": 4,
        "biome_tags": ["dungeon", "cave", "hell"],
        "room_size": (6, 6),
        "one_time": True,
        "description": "Дверь за вами захлопывается! Засада!",
        "choices": [
            {"key": "1", "label": "Приготовиться к бою", "effect": "ambush_spawn", "cost": {}},
        ],
        "npc_id": None,
        "interactable": "trap_door",
    },
    "collapse_room": {
        "id": "collapse_room",
        "name": "Обвал",
        "rarity": "uncommon",
        "depth_min": 5,
        "biome_tags": ["cave", "hell"],
        "room_size": (6, 6),
        "one_time": True,
        "description": "Часть потолка обрушилась, открыв тайник.",
        "choices": [
            {"key": "1", "label": "Обыскать завалы", "effect": "collapse_loot", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "rubble",
    },
    "lost_spirit": {
        "id": "lost_spirit",
        "name": "Заблудший дух",
        "rarity": "rare",
        "depth_min": 6,
        "biome_tags": ["crypt", "deep"],
        "room_size": (5, 5),
        "one_time": True,
        "description": "Полупрозрачный дух качается в воздухе. Позволить ему следовать за вами?",
        "choices": [
            {"key": "1", "label": "Принять (подсвечивает ловушки на 50 ходов)", "effect": "spirit_follow", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "spirit",
    },
    "lore_wall": {
        "id": "lore_wall",
        "name": "Древняя надпись",
        "rarity": "common",
        "depth_min": 1,
        "biome_tags": ["dungeon", "cave", "crypt", "mushroom", "hell", "deep"],
        "room_size": (4, 4),
        "one_time": True,
        "description": "На стене выцарапаны странные символы.",
        "choices": [
            {"key": "1", "label": "Прочитать", "effect": "lore_read", "cost": {}},
            {"key": "2", "label": "Уйти", "effect": None},
        ],
        "npc_id": None,
        "interactable": "lore",
    },
}


def get_event(event_id: str) -> dict | None:
    return EVENTS.get(event_id)


def events_for_depth(depth: int, biome_tags: list[str]) -> list[dict]:
    """Вернуть события, подходящие для глубины и биома."""
    result = []
    biome_set = set(biome_tags)
    for event in EVENTS.values():
        if event["depth_min"] > depth:
            continue
        if not (set(event.get("biome_tags", [])) & biome_set):
            continue
        result.append(event)
    return result
