"""Генерация подземелья: комнаты, коридоры, биомы, опасности, ловушки."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from systems.game_state import GameState


@dataclass
class Room:
    x: int
    y: int
    w: int
    h: int

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)

    def intersects(self, other: "Room") -> bool:
        return (
            self.x <= other.x + other.w
            and self.x + self.w >= other.x
            and self.y <= other.y + other.h
            and self.y + self.h >= other.y
        )


@dataclass
class Dungeon:
    width: int
    height: int
    tiles: list[list[dict]] = field(default_factory=list)
    visible: list[list[bool]] = field(default_factory=list)
    explored: list[list[bool]] = field(default_factory=list)
    rooms: list[Room] = field(default_factory=list)
    stairs: tuple[int, int] = (0, 0)
    biome_id: str = "dungeon"
    hazards: dict[tuple[int, int], str] = field(default_factory=dict)
    traps: dict[tuple[int, int], str] = field(default_factory=dict)
    revealed_traps: set[tuple[int, int]] = field(default_factory=set)
    interactables: dict[tuple[int, int], dict] = field(default_factory=dict)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def tile_at(self, x: int, y: int) -> dict | None:
        if not self.in_bounds(x, y):
            return None
        return self.tiles[y][x]

    def is_wall(self, x: int, y: int) -> bool:
        t = self.tile_at(x, y)
        return t is not None and t["type"] == "wall"

    def is_floor(self, x: int, y: int) -> bool:
        t = self.tile_at(x, y)
        return t is not None and t["type"] in ("floor", "stairs")

    def blocks_movement(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return True
        tile = self.tiles[y][x]
        if tile["type"] == "wall":
            return True
        # Некоторые hazards блокируют движение (лава)
        hazard_id = self.hazards.get((x, y))
        if hazard_id:
            from world.hazards import get_hazard
            h = get_hazard(hazard_id)
            if h and h.get("blocks_movement"):
                return True
        return False

    def blocks_sight(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return True
        tile = self.tiles[y][x]
        if tile["type"] == "wall":
            return True
        hazard_id = self.hazards.get((x, y))
        if hazard_id:
            from world.hazards import get_hazard
            h = get_hazard(hazard_id)
            if h and h.get("blocks_sight"):
                return True
        return False

    def set_tile(self, x: int, y: int, tile_type: str, biome: dict | None = None) -> None:
        tiles = (biome or {}).get("tiles", {})
        if tile_type == "floor":
            cfg = tiles.get("floor", {"char": ".", "color": "grey"})
            self.tiles[y][x] = _make_tile("floor", cfg)
        elif tile_type == "wall":
            cfg = tiles.get("wall", {"char": "#", "color": "white"})
            self.tiles[y][x] = _make_tile("wall", cfg)
        elif tile_type == "stairs":
            cfg = tiles.get("stairs_down", {"char": ">", "color": "cyan"})
            self.tiles[y][x] = _make_tile("stairs", cfg)

    def floor_positions(self) -> list[tuple[int, int]]:
        """Все клетки пола."""
        positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.is_floor(x, y):
                    positions.append((x, y))
        return positions


def _make_tile(tile_type: str, cfg: dict) -> dict:
    from engine.render import COLOR_MAP

    color_name = cfg.get("color", "white")
    color_visible = COLOR_MAP.get(color_name, 7)
    # Для тумана используем приглушённые цвета
    color_fog = _fog_color_for(color_visible)
    return {
        "type": tile_type,
        "char": cfg.get("char", "?"),
        "color_visible": color_visible,
        "color_fog": color_fog,
    }


def _fog_color_for(color_visible: int) -> int:
    """Вернуть пару цвета для тумана."""
    mapping = {
        0: 5, 1: 5, 2: 4, 3: 5, 4: 4, 5: 5, 6: 5, 7: 5,
        8: 4, 9: 5, 10: 5, 11: 5, 12: 5, 13: 5, 14: 5, 15: 5, 16: 5, 17: 5,
    }
    return mapping.get(color_visible, 5)


def generate_dungeon(
    depth: int,
    width: int = 60,
    height: int = 24,
    max_rooms: int = 12,
    min_size: int = 4,
    max_size: int = 10,
    rng: random.Random | None = None,
    biome_id: str | None = None,
) -> Dungeon:
    """Сгенерировать уровень для заданной глубины и биома."""
    if rng is None:
        rng = random.Random()

    from content.biomes import biome_for_depth, get_biome

    biome = get_biome(biome_id) if biome_id else biome_for_depth(depth, rng)
    biome_id = biome["id"]
    generator_key = biome["generator"]

    dungeon = Dungeon(width, height)
    dungeon.biome_id = biome_id
    dungeon.tiles = [
        [{"type": "wall", "char": "#", "color_visible": 2, "color_fog": 4} for _ in range(width)]
        for _ in range(height)
    ]
    dungeon.visible = [[False for _ in range(width)] for _ in range(height)]
    dungeon.explored = [[False for _ in range(width)] for _ in range(height)]

    if generator_key == "rooms_corridors":
        _generate_rooms_corridors(dungeon, biome, max_rooms, min_size, max_size, rng)
    elif generator_key == "cellular_automata":
        _generate_cellular_automata(dungeon, biome, rng)
    elif generator_key == "tunnels":
        _generate_tunnels(dungeon, biome, rng)
    elif generator_key == "bridges_lava":
        _generate_bridges_lava(dungeon, biome, rng)
    elif generator_key == "open_arena":
        _generate_open_arena(dungeon, biome, rng)
    else:
        _generate_rooms_corridors(dungeon, biome, max_rooms, min_size, max_size, rng)

    _apply_hazards(dungeon, biome, rng)
    _place_traps(dungeon, biome, rng)

    # Лестница — дальняя floor-клетка от старта
    floors = dungeon.floor_positions()
    if floors:
        dungeon.stairs = floors[-1]
        dungeon.set_tile(dungeon.stairs[0], dungeon.stairs[1], "stairs", biome)

    return dungeon


def _generate_rooms_corridors(
    dungeon: Dungeon,
    biome: dict,
    max_rooms: int,
    min_size: int,
    max_size: int,
    rng: random.Random,
) -> None:
    """Классический генератор комнат и коридоров."""
    width, height = dungeon.width, dungeon.height
    rooms: list[Room] = []

    attempts = max_rooms * 5
    while len(rooms) < max_rooms and attempts > 0:
        attempts -= 1
        w = rng.randint(min_size, max_size)
        h = rng.randint(min_size, max_size)
        x = rng.randint(1, width - w - 2)
        y = rng.randint(1, height - h - 2)
        new_room = Room(x, y, w, h)

        if any(new_room.intersects(other) for other in rooms):
            continue

        _create_room(dungeon, new_room, biome)
        if rooms:
            prev_x, prev_y = rooms[-1].center
            new_x, new_y = new_room.center
            if rng.random() < 0.5:
                _create_h_tunnel(dungeon, prev_x, new_x, prev_y, biome)
                _create_v_tunnel(dungeon, prev_y, new_y, new_x, biome)
            else:
                _create_v_tunnel(dungeon, prev_y, new_y, prev_x, biome)
                _create_h_tunnel(dungeon, prev_x, new_x, new_y, biome)

        rooms.append(new_room)

    dungeon.rooms = rooms


def _generate_cellular_automata(dungeon: Dungeon, biome: dict, rng: random.Random) -> None:
    """Органическая пещерная генерация."""
    width, height = dungeon.width, dungeon.height
    # Случайный шум
    grid = [[rng.random() < 0.52 for _ in range(width)] for _ in range(height)]

    # Итерации сглаживания
    for _ in range(3):
        new_grid = [[False for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                neighbors = _count_wall_neighbors(grid, x, y, width, height)
                if grid[y][x]:
                    new_grid[y][x] = neighbors >= 4
                else:
                    new_grid[y][x] = neighbors >= 5
        grid = new_grid

    # Границы всегда стены
    for y in range(height):
        for x in range(width):
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                grid[y][x] = False

    # Записываем в dungeon
    for y in range(height):
        for x in range(width):
            if grid[y][x]:
                dungeon.set_tile(x, y, "floor", biome)

    # Создаём комнаты-пещеры для размещения сущностей
    _find_floor_regions(dungeon)


def _count_wall_neighbors(grid: list[list[bool]], x: int, y: int, width: int, height: int) -> int:
    count = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= width or ny >= height:
                count += 1
            elif not grid[ny][nx]:
                count += 1
    return count


def _find_floor_regions(dungeon: Dungeon) -> None:
    """Найти связные области пола и оставить только самую большую."""
    width, height = dungeon.width, dungeon.height
    visited = [[False for _ in range(width)] for _ in range(height)]
    regions: list[list[tuple[int, int]]] = []

    for y in range(height):
        for x in range(width):
            if dungeon.is_floor(x, y) and not visited[y][x]:
                region = []
                stack = [(x, y)]
                visited[y][x] = True
                while stack:
                    cx, cy = stack.pop()
                    region.append((cx, cy))
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = cx + dx, cy + dy
                        if dungeon.in_bounds(nx, ny) and dungeon.is_floor(nx, ny) and not visited[ny][nx]:
                            visited[ny][nx] = True
                            stack.append((nx, ny))
                regions.append(region)

    if not regions:
        return

    # Оставляем только самую большую область
    largest = max(regions, key=len)
    keep = set(largest)
    for y in range(height):
        for x in range(width):
            if dungeon.is_floor(x, y) and (x, y) not in keep:
                dungeon.set_tile(x, y, "wall")

    # Искусственные "комнаты" — случайные кластеры пола для размещения
    dungeon.rooms = []
    if len(largest) > 20:
        rng = random.Random(hash(tuple(largest[:5])))
        for _ in range(min(8, len(largest) // 30)):
            cx, cy = rng.choice(largest)
            # Ищем квадрат 4x4 вокруг центра
            room = Room(max(1, cx - 2), max(1, cy - 2), 4, 4)
            dungeon.rooms.append(room)


def _generate_tunnels(dungeon: Dungeon, biome: dict, rng: random.Random) -> None:
    """Длинные коридоры с залами (шахты)."""
    width, height = dungeon.width, dungeon.height
    # Горизонтальные туннели
    num_tunnels = rng.randint(4, 7)
    for _ in range(num_tunnels):
        y = rng.randint(2, height - 3)
        for x in range(1, width - 1):
            dungeon.set_tile(x, y, "floor", biome)

    # Вертикальные соединения
    for _ in range(num_tunnels // 2):
        x = rng.randint(2, width - 3)
        for y in range(1, height - 1):
            dungeon.set_tile(x, y, "floor", biome)

    # Несколько залов
    rooms = []
    for _ in range(rng.randint(3, 6)):
        w = rng.randint(5, 10)
        h = rng.randint(4, 8)
        x = rng.randint(1, width - w - 2)
        y = rng.randint(1, height - h - 2)
        room = Room(x, y, w, h)
        _create_room(dungeon, room, biome)
        rooms.append(room)
    dungeon.rooms = rooms


def _generate_bridges_lava(dungeon: Dungeon, biome: dict, rng: random.Random) -> None:
    """Островки пола, соединённые мостками; всё остальное — lava hazard."""
    width, height = dungeon.width, dungeon.height

    # Несколько островков-комнат
    rooms = []
    for _ in range(rng.randint(5, 8)):
        w = rng.randint(4, 8)
        h = rng.randint(4, 8)
        x = rng.randint(2, width - w - 3)
        y = rng.randint(2, height - h - 3)
        room = Room(x, y, w, h)
        _create_room(dungeon, room, biome)
        rooms.append(room)

    # Соединяем комнаты мостками
    for i in range(1, len(rooms)):
        x1, y1 = rooms[i - 1].center
        x2, y2 = rooms[i].center
        if rng.random() < 0.5:
            _create_h_tunnel(dungeon, x1, x2, y1, biome)
            _create_v_tunnel(dungeon, y1, y2, x2, biome)
        else:
            _create_v_tunnel(dungeon, y1, y2, x1, biome)
            _create_h_tunnel(dungeon, x1, x2, y2, biome)

    dungeon.rooms = rooms

    # Всё, что не floor, помечаем лавой
    lava = "lava"
    for y in range(height):
        for x in range(width):
            if not dungeon.is_floor(x, y):
                dungeon.hazards[(x, y)] = lava


def _generate_open_arena(dungeon: Dungeon, biome: dict, rng: random.Random) -> None:
    """Большое открытое пространство с редкими 1x1 колоннами."""
    width, height = dungeon.width, dungeon.height
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            dungeon.set_tile(x, y, "floor", biome)

    # Редкие 1x1 колонны
    rooms = []
    for y in range(3, height - 3, 5):
        for x in range(3, width - 3, 6):
            if rng.random() < 0.25:
                dungeon.set_tile(x, y, "wall", biome)

    dungeon.rooms = [Room(width // 2 - 5, height // 2 - 5, 10, 10)]


def _create_room(dungeon: Dungeon, room: Room, biome: dict) -> None:
    for y in range(room.y, room.y + room.h):
        for x in range(room.x, room.x + room.w):
            dungeon.set_tile(x, y, "floor", biome)


def _create_h_tunnel(dungeon: Dungeon, x1: int, x2: int, y: int, biome: dict) -> None:
    for x in range(min(x1, x2), max(x1, x2) + 1):
        dungeon.set_tile(x, y, "floor", biome)


def _create_v_tunnel(dungeon: Dungeon, y1: int, y2: int, x: int, biome: dict) -> None:
    for y in range(min(y1, y2), max(y1, y2) + 1):
        dungeon.set_tile(x, y, "floor", biome)


def _apply_hazards(dungeon: Dungeon, biome: dict, rng: random.Random) -> None:
    """Разместить статические опасности на floor-клетках."""
    hazards = biome.get("hazards", [])
    density = biome.get("hazard_density", 0.0)
    if not hazards or density <= 0:
        return

    floors = dungeon.floor_positions()
    rng.shuffle(floors)
    count = int(len(floors) * density)
    for x, y in floors[:count]:
        if (x, y) == dungeon.stairs:
            continue
        # Не ставим hazard поверх lava (для bridges_lava lava уже везде)
        if dungeon.hazards.get((x, y)) == "lava":
            continue
        dungeon.hazards[(x, y)] = rng.choice(hazards)


def _place_traps(dungeon: Dungeon, biome: dict, rng: random.Random) -> None:
    """Разместить скрытые ловушки на floor-клетках."""
    from world.traps import traps_for_depth

    density = biome.get("trap_density", 0.0)
    if density <= 0:
        return

    available = traps_for_depth(99)  # все
    if not available:
        return

    floors = dungeon.floor_positions()
    rng.shuffle(floors)
    count = int(len(floors) * density)
    for x, y in floors[:count]:
        if (x, y) == dungeon.stairs:
            continue
        if (x, y) in dungeon.hazards:
            continue
        dungeon.traps[(x, y)] = rng.choice(available)


def place_player(dungeon: Dungeon, rng: random.Random | None = None) -> tuple[int, int]:
    """Выбрать стартовую позицию игрока."""
    if dungeon.rooms:
        return dungeon.rooms[0].center
    floors = dungeon.floor_positions()
    if floors:
        return floors[0]
    return (dungeon.width // 2, dungeon.height // 2)


def place_entities(
    dungeon: Dungeon,
    state: "GameState",
    rng: random.Random | None = None,
) -> tuple[list, dict[tuple[int, int], list[str]]]:
    """Разместить мобов и предметы с учётом биома."""
    from content.biomes import get_biome
    from content.items import items_for_biome
    from content.monsters import monsters_for_biome
    from entities.mob import Mob

    if rng is None:
        rng = random.Random()

    biome = get_biome(dungeon.biome_id)
    biome_tags = biome.get("monster_tags", []) if biome else []
    item_tags = biome.get("item_tags", []) if biome else []

    mobs: list = []
    items_on_floor: dict[tuple[int, int], list[str]] = {}

    candidate_positions = _entity_positions(dungeon, rng)

    # Мобы
    num_mobs = rng.randint(2, 4 + state.depth // 2)
    mob_pool = monsters_for_biome(biome_tags, state.depth)
    for _ in range(num_mobs):
        if not candidate_positions:
            break
        x, y = candidate_positions.pop()
        mob_id = rng.choice(mob_pool)
        mobs.append(Mob.from_data(mob_id, x, y))

    # Предметы
    num_items = rng.randint(2, 5)
    item_pool = items_for_biome(item_tags, state.depth)
    for _ in range(num_items):
        if not candidate_positions:
            break
        x, y = candidate_positions.pop()
        item_id = rng.choice(item_pool)
        items_on_floor.setdefault((x, y), []).append(item_id)

    # Золото
    for _ in range(rng.randint(2, 5)):
        if not candidate_positions:
            break
        x, y = candidate_positions.pop()
        items_on_floor.setdefault((x, y), []).append("gold")

    return mobs, items_on_floor


def _entity_positions(dungeon: Dungeon, rng: random.Random) -> list[tuple[int, int]]:
    """Подходящие позиции для мобов/предметов: floor, не лестница, не hazard."""
    positions = []
    start = place_player(dungeon, rng)
    for x, y in dungeon.floor_positions():
        if (x, y) == dungeon.stairs:
            continue
        if (x, y) == start:
            continue
        if dungeon.hazards.get((x, y)) in ("lava",):
            continue
        positions.append((x, y))
    rng.shuffle(positions)
    return positions
