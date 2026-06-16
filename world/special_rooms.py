"""Размещение спецкомнат и событий в подземелье."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from content.biomes import get_biome
from content.events import events_for_depth
from entities.npcs import create_npc

if TYPE_CHECKING:
    from world.dungeon import Dungeon
    from systems.game_state import GameState


def _weight_for_rarity(rarity: str) -> int:
    return {"common": 5, "uncommon": 3, "rare": 1}.get(rarity, 1)


def _pick_event(dungeon: "Dungeon", state: "GameState", rng: random.Random) -> dict | None:
    biome = get_biome(dungeon.biome_id)
    biome_tags = biome.get("monster_tags", []) if biome else []
    candidates = events_for_depth(state.depth, biome_tags)
    if not candidates:
        return None

    # Учитываем one_time на уровне (не повторять уже размещённые id, если one_time)
    # Но событий с one_time может быть несколько разных, поэтому только повторы id запрещаем
    candidates = [e for e in candidates if e["id"] not in state.visited_events]
    if not candidates:
        return None

    weighted = []
    for e in candidates:
        weight = _weight_for_rarity(e.get("rarity", "common"))
        weighted.extend([e] * weight)
    return rng.choice(weighted)


def _find_room_for_special(dungeon: "Dungeon", rng: random.Random, w: int, h: int) -> tuple[int, int] | None:
    """Найти место для прямоугольной спецкомнаты внутри подземелья."""
    for _ in range(50):
        x = rng.randint(1, dungeon.width - w - 2)
        y = rng.randint(1, dungeon.height - h - 2)

        # Проверяем, что область полностью состоит из стен (не пересекает существующие комнаты/коридоры)
        all_walls = True
        for dy in range(h):
            for dx in range(w):
                if not dungeon.is_wall(x + dx, y + dy):
                    all_walls = False
                    break
            if not all_walls:
                break

        if all_walls:
            return (x, y)
    return None


def _carve_special_room(dungeon: "Dungeon", x: int, y: int, w: int, h: int, biome: dict) -> None:
    """Высечь спецкомнату в стенах."""
    for dy in range(h):
        for dx in range(w):
            dungeon.set_tile(x + dx, y + dy, "floor", biome)


def _connect_special_room(dungeon: "Dungeon", x: int, y: int, w: int, h: int, biome: dict, rng: random.Random) -> None:
    """Прорубить коридор от спецкомнаты к ближайшему полу."""
    from world.dungeon import _create_h_tunnel, _create_v_tunnel

    cx, cy = x + w // 2, y + h // 2
    # Ищем ближайшую floor-клетку
    floors = dungeon.floor_positions()
    if not floors:
        return
    floors.sort(key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))
    nearest = floors[0]

    # Коридор от центра комнаты к ближайшему полу
    if rng.random() < 0.5:
        _create_h_tunnel(dungeon, cx, nearest[0], cy, biome)
        _create_v_tunnel(dungeon, cy, nearest[1], nearest[0], biome)
    else:
        _create_v_tunnel(dungeon, cy, nearest[1], cx, biome)
        _create_h_tunnel(dungeon, cx, nearest[0], nearest[1], biome)


def place_special_rooms(dungeon: "Dungeon", state: "GameState", rng: random.Random | None = None) -> None:
    """Разместить спецкомнаты с событиями/NPC в подземелье."""
    if rng is None:
        rng = random.Random()

    from world.dungeon import Room
    from systems.interactables import INTERACTABLES

    biome = get_biome(dungeon.biome_id)
    if biome is None:
        return

    # Очистить npcs для уровня
    state.npcs = []

    max_rooms = rng.randint(1, 2 + state.depth // 4)
    placed = 0
    for _ in range(max_rooms * 5):
        if placed >= max_rooms:
            break
        event = _pick_event(dungeon, state, rng)
        if event is None:
            continue
        w, h = event.get("room_size", (5, 5))
        pos = _find_room_for_special(dungeon, rng, w, h)
        if pos is None:
            continue

        x, y = pos
        _carve_special_room(dungeon, x, y, w, h, biome)
        _connect_special_room(dungeon, x, y, w, h, biome, rng)
        cx, cy = x + w // 2, y + h // 2

        interactable_id = event.get("interactable")
        if interactable_id and interactable_id in INTERACTABLES:
            dungeon.interactables[(cx, cy)] = {
                "id": event["id"],
                "interactable_id": interactable_id,
                "data": event,
                "used": False,
            }

        npc_id = event.get("npc_id")
        if npc_id:
            npc = create_npc(npc_id, cx, cy, rng)
            state.npcs.append(npc)
            # NPC стоит на interactable, не удаляем interactable

        # Записываем, что событие размещено (но не считаем посещённым)
        if event.get("one_time"):
            state.visited_events.add(event["id"])

        dungeon.rooms.append(Room(x, y, w, h))
        placed += 1
