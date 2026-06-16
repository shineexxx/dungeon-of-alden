"""Лор-фрагменты и сюжетные нити.

СХЕМА ПОЛЕЙ:
    id          : str      уникальный ключ
    title       : str      название/источник
    text        : str      текст лора
    thread      : str      id сюжетной нити
    depth_range : tuple    (min, max) глубины
    biome_tags  : list     подходящие биомы
"""

from __future__ import annotations

LORE: dict[str, dict] = {
    # --- Нить: Падшее королевство ---
    "lore_kingdom_1": {
        "id": "lore_kingdom_1",
        "title": "Выбитая эпитафия",
        "text": "Король Альден приказал запечатать нижние врата. С тех пор никто не выходил. Никто... кроме того, кто стучит.",
        "thread": "fallen_kingdom",
        "depth_range": (1, 4),
        "biome_tags": ["dungeon"],
    },
    "lore_kingdom_2": {
        "id": "lore_kingdom_2",
        "title": "Страница хроники",
        "text": "Год 847. Чума поглотила три квартала. Королевские маги утверждали, что источник — в глубинах. Их никто больше не видел.",
        "thread": "fallen_kingdom",
        "depth_range": (2, 5),
        "biome_tags": ["dungeon", "crypt"],
    },
    "lore_kingdom_3": {
        "id": "lore_kingdom_3",
        "title": "Письмо стражника",
        "text": "Мы спустились слишком глубоко. Стены здесь не каменные — они дышат. Приказ: держать позицию до последнего.",
        "thread": "fallen_kingdom",
        "depth_range": (5, 8),
        "biome_tags": ["cave", "crypt"],
    },
    "lore_kingdom_4": {
        "id": "lore_kingdom_4",
        "title": "Королевская печать",
        "text": "Здесь покоится династия Альдена. Пусть никто не потревожит их сон. Клятва, данная небу, земле и тьме.",
        "thread": "fallen_kingdom",
        "depth_range": (8, 12),
        "biome_tags": ["crypt", "deep"],
    },
    "lore_kingdom_5": {
        "id": "lore_kingdom_5",
        "title": "Последний указ",
        "text": "Если кто-то читает это — королевство пало. Единственная надежда — достичь трона и уничтожить то, что сидит на нём.",
        "thread": "fallen_kingdom",
        "depth_range": (15, 20),
        "biome_tags": ["deep"],
    },

    # --- Нить: Древнее зло ---
    "lore_evil_1": {
        "id": "lore_evil_1",
        "title": "Руны на стене",
        "text": "Оно было здесь задолго до людей. Оно спит, но не умирает. Каждый шаг вниз — это эхо, которое может его разбудить.",
        "thread": "ancient_evil",
        "depth_range": (3, 6),
        "biome_tags": ["cave", "crypt"],
    },
    "lore_evil_2": {
        "id": "lore_evil_2",
        "title": "Записка некроманта",
        "text": "Я слышу голоса. Они обещают силу, вечную жизнь, знания. Я спущусь ещё ниже. Оно ждёт меня.",
        "thread": "ancient_evil",
        "depth_range": (6, 10),
        "biome_tags": ["crypt", "mushroom"],
    },
    "lore_evil_3": {
        "id": "lore_evil_3",
        "title": "Обгоревший свиток",
        "text": "Ритуал почти завершён. Сердце пламени бьётся в такт сердцу тьмы. Два стихийных бога встретятся в одном сосуде.",
        "thread": "ancient_evil",
        "depth_range": (10, 14),
        "biome_tags": ["hell"],
    },
    "lore_evil_4": {
        "id": "lore_evil_4",
        "title": "Метка безумия",
        "text": "Я видел лицо в темноте. Оно не имеет глаз, но оно смотрит. Оно не имеет рта, но оно зовёт моё имя.",
        "thread": "ancient_evil",
        "depth_range": (14, 20),
        "biome_tags": ["deep"],
    },

    # --- Нить: Создатель подземелья ---
    "lore_maker_1": {
        "id": "lore_maker_1",
        "title": "Чертёж на камне",
        "text": "Эти коридоры не высечены — они выращены. Камень помнит форму, которую ему дали. Архитектор был не человеком.",
        "thread": "dungeon_maker",
        "depth_range": (4, 7),
        "biome_tags": ["cave", "dungeon"],
    },
    "lore_maker_2": {
        "id": "lore_maker_2",
        "title": "Запись геоманта",
        "text": "Подземелье живое. Оно меняет форму, когда никто не видит. Лестницы смещаются, комнаты меняются местами. Мы запутались в его мыслях.",
        "thread": "dungeon_maker",
        "depth_range": (8, 12),
        "biome_tags": ["cave", "mushroom", "deep"],
    },
    "lore_maker_3": {
        "id": "lore_maker_3",
        "title": "Имя архитектора",
        "text": "Его звали Велькор. Он создал семь уровней, чтобы удержать то, что не должно было выйти. Седьмой уровень — не камень, а плоть.",
        "thread": "dungeon_maker",
        "depth_range": (15, 20),
        "biome_tags": ["deep"],
    },

    # --- Отдельные фрагменты ---
    "lore_fungus": {
        "id": "lore_fungus",
        "title": "Споровая записка",
        "text": "Грибы помнят. Они питаются мёртвыми и впитывают их воспоминания. Если прислушаться — можно услышать чужие голоса.",
        "thread": "misc",
        "depth_range": (7, 11),
        "biome_tags": ["mushroom"],
    },
    "lore_lava": {
        "id": "lore_lava",
        "title": "Надпись у кузницы",
        "text": "Огонь не прощает. Огонь не забывает. Тот, кто шагнёт в пламя, станет либо слугой, либо пеплом.",
        "thread": "misc",
        "depth_range": (10, 14),
        "biome_tags": ["hell"],
    },
    "lore_spider": {
        "id": "lore_spider",
        "title": "Паутинное послание",
        "text": "Королева внизу. Она плетёт сеть из костей и света. Каждый, кто умирает в пещере, попадает в её коллекцию.",
        "thread": "misc",
        "depth_range": (3, 6),
        "biome_tags": ["cave"],
    },
    "lore_mirror": {
        "id": "lore_mirror",
        "title": "Разбитое зеркало",
        "text": "В осколках отражается не твоё лицо. Оно улыбается тебе. Оно знает, что ты сделаешь дальше.",
        "thread": "misc",
        "depth_range": (12, 17),
        "biome_tags": ["crypt", "deep"],
    },
    "lore_clock": {
        "id": "lore_clock",
        "title": "Сломанные часы",
        "text": "Время внизу течёт иначе. Тот, кто спустился на час, вернулся через год. Тот, кто спустился на год, не вернулся вовсе.",
        "thread": "misc",
        "depth_range": (1, 5),
        "biome_tags": ["dungeon", "cave"],
    },
    "lore_books": {
        "id": "lore_books",
        "title": "Обгоревшая страница",
        "text": "...и седьмая печать была сломана. Из бездны поднялся тот, чьё имя нельзя произносить вслух. Его приход ознаменовал конец первой эпохи.",
        "thread": "misc",
        "depth_range": (16, 20),
        "biome_tags": ["hell", "deep"],
    },
    "lore_prisoner": {
        "id": "lore_prisoner",
        "title": "Каракули на стене клетки",
        "text": "Они держат нас не за преступления. Они кормят им. Спускайся глубже — и ты увидишь, кто здесь настоящий хозяин.",
        "thread": "misc",
        "depth_range": (2, 6),
        "biome_tags": ["dungeon", "crypt"],
    },
    "lore_water": {
        "id": "lore_water",
        "title": "Надпись у источника",
        "text": "Вода внизу не тушит жажду. Она наполняет пустоту, которую ты не замечал. Пей — и услышишь голоса.",
        "thread": "misc",
        "depth_range": (6, 10),
        "biome_tags": ["crypt"],
    },
    "lore_gold": {
        "id": "lore_gold",
        "title": "Торговая марка",
        "text": "Золото здесь не имеет цены. Те, кто приходил за богатством, остались украшать стены.",
        "thread": "misc",
        "depth_range": (1, 8),
        "biome_tags": ["dungeon", "cave"],
    },
    "lore_dragon": {
        "id": "lore_dragon",
        "title": "Чешуя в камне",
        "text": "Драконы не вымерли. Они спят под корнями мира. Этот подземелье — одно из их гнёзд. Мы вторглись в дом огня.",
        "thread": "misc",
        "depth_range": (9, 14),
        "biome_tags": ["hell", "cave"],
    },
    "lore_star": {
        "id": "lore_star",
        "title": "Астрономическая таблица",
        "text": "Звёзды над подземельем расположены не так, как на небе. Они образуют глаз. Он открыт.",
        "thread": "misc",
        "depth_range": (13, 18),
        "biome_tags": ["deep"],
    },
    "lore_smith": {
        "id": "lore_smith",
        "title": "Кузнечная клеймо",
        "text": "Оружие, выкованное в глубинах, помнит каждую кровь. Со временем оно начинает хотеть ещё.",
        "thread": "misc",
        "depth_range": (4, 9),
        "biome_tags": ["dungeon", "hell"],
    },
    "lore_lich": {
        "id": "lore_lich",
        "title": "Философский трактат",
        "text": "Смерть — не конец, а дверь. За ней стоит тот, кто ждёт. Он голоден. Он всегда голоден.",
        "thread": "misc",
        "depth_range": (11, 16),
        "biome_tags": ["crypt", "deep"],
    },
    "lore_seed": {
        "id": "lore_seed",
        "title": "Послание друида",
        "text": "Подземелье — это семя. Когда оно прорастёт, мир перевернётся. Корни уже пробрались вверх.",
        "thread": "misc",
        "depth_range": (7, 12),
        "biome_tags": ["mushroom", "cave"],
    },
    "lore_hero": {
        "id": "lore_hero",
        "title": "Щит павшего героя",
        "text": "Тот, кто шёл до меня, был сильнее. Его щит расколот. Его имя стёрто. Но его путь продолжаю я.",
        "thread": "misc",
        "depth_range": (5, 10),
        "biome_tags": ["dungeon", "crypt", "cave"],
    },
    "lore_door": {
        "id": "lore_door",
        "title": "Над дверью",
        "text": "За этой дверью не то, что ты ищешь. За этой дверью то, что ищет тебя.",
        "thread": "misc",
        "depth_range": (14, 19),
        "biome_tags": ["deep"],
    },
    "lore_last": {
        "id": "lore_last",
        "title": "Последняя запись",
        "text": "Если ты дочитал до сюда — ты уже слишком близко. Оно знает твоё имя. Трон ждёт.",
        "thread": "misc",
        "depth_range": (18, 20),
        "biome_tags": ["deep"],
    },
}


def get_lore(lore_id: str) -> dict | None:
    return LORE.get(lore_id)


def random_lore_for(biome_id: str, depth: int, rng) -> dict | None:
    """Выбрать случайный лор-фрагмент для биома и глубины."""
    candidates = [
        lore for lore in LORE.values()
        if lore["depth_range"][0] <= depth <= lore["depth_range"][1]
        and biome_id in lore.get("biome_tags", [])
    ]
    if not candidates:
        return None
    return rng.choice(candidates)
