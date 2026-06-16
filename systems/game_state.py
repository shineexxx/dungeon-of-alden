"""Глобальное состояние игры."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from entities.player import Player
from entities.mob import Mob
from entities.npcs import NPC
from world.dungeon import Dungeon, Room, generate_dungeon, place_entities, place_player
from systems.identification import generate_identification_state
from systems.journal import Journal


@dataclass
class GameState:
    seed: int
    depth: int = 1
    score: int = 0
    turn: int = 0
    player_name: str = "Искатель"
    kills: int = 0
    log: list[str] = field(default_factory=list)
    rng: random.Random = field(default_factory=random.Random)
    dungeon: Dungeon = field(default_factory=lambda: Dungeon(0, 0))
    player: Player = field(default_factory=lambda: Player(0, 0))
    mobs: list[Mob] = field(default_factory=list)
    npcs: list[NPC] = field(default_factory=list)
    items_on_floor: dict[tuple[int, int], list[str]] = field(default_factory=dict)
    identification: dict = field(default_factory=dict)
    journal: Journal = field(default_factory=Journal)
    visited_events: set[str] = field(default_factory=set)
    final_boss_spawned: bool = False

    def __post_init__(self) -> None:
        # Убедимся, что rng инициализирован с seed
        if not hasattr(self, "rng") or self.rng is None:
            self.rng = random.Random(self.seed)
        # Генерируем состояние опознания, если его ещё нет
        if not self.identification:
            self.identification = generate_identification_state(self.rng)

    def generate_level(self) -> None:
        """Сгенерировать новый уровень подземелья (или финальный этаж)."""
        from content.biomes import get_biome
        from world.final_floor import FINAL_DEPTH, generate_final_floor

        if self.depth >= FINAL_DEPTH:
            self.dungeon = generate_final_floor(self, self.rng)
            self.log_message("Вы достигли тронного зала. Конец близок...")
        else:
            self.dungeon = generate_dungeon(
                depth=self.depth,
                width=60,
                height=22,
                max_rooms=10 + self.depth,
                rng=self.rng,
            )
            from world.special_rooms import place_special_rooms
            place_special_rooms(self.dungeon, self, self.rng)
            biome = get_biome(self.dungeon.biome_id)
            if biome:
                self.log_message(f"Вы спустились в {biome['name']}.")
                self.journal.record_biome(self.dungeon.biome_id)
            else:
                self.log_message(f"Вы спустились на глубину {self.depth}.")

        px, py = place_player(self.dungeon, self.rng)
        self.player.x = px
        self.player.y = py
        self.mobs, self.items_on_floor = place_entities(self.dungeon, self, self.rng)
        from engine.fov import compute_fov
        compute_fov(self.dungeon, px, py, self.player.fov_radius)

    def log_message(self, message: str) -> None:
        self.log.append(message)
        if len(self.log) > 100:
            self.log.pop(0)

    def to_dict(self) -> dict:
        from systems.identification import serialize_identification
        return {
            "save_version": 7,
            "seed": self.seed,
            "depth": self.depth,
            "score": self.score,
            "turn": self.turn,
            "player_name": self.player_name,
            "kills": self.kills,
            "log": list(self.log),
            "player": self.player.to_dict(),
            "mobs": [m.to_dict() for m in self.mobs],
            "npcs": [n.__dict__ for n in self.npcs],
            "items_on_floor": {f"{x},{y}": items for (x, y), items in self.items_on_floor.items()},
            "journal": self.journal.to_dict(),
            "visited_events": sorted(self.visited_events),
            "final_boss_spawned": self.final_boss_spawned,
            "dungeon": {
                "width": self.dungeon.width,
                "height": self.dungeon.height,
                "tiles": self.dungeon.tiles,
                "visible": self.dungeon.visible,
                "explored": self.dungeon.explored,
                "rooms": [(r.x, r.y, r.w, r.h) for r in self.dungeon.rooms],
                "stairs": self.dungeon.stairs,
                "biome_id": self.dungeon.biome_id,
                "hazards": {f"{x},{y}": hid for (x, y), hid in self.dungeon.hazards.items()},
                "traps": {f"{x},{y}": tid for (x, y), tid in self.dungeon.traps.items()},
                "revealed_traps": [f"{x},{y}" for x, y in self.dungeon.revealed_traps],
                "interactables": {
                    f"{x},{y}": data for (x, y), data in self.dungeon.interactables.items()
                },
            },
            "identification": serialize_identification(self.identification),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        from systems.identification import deserialize_identification

        version = data.get("save_version", 1)
        if version != 7:
            # Место для будущей миграции
            pass

        state = cls(seed=data["seed"])
        state.depth = data["depth"]
        state.score = data["score"]
        state.turn = data["turn"]
        state.player_name = data.get("player_name", "Искатель")
        state.kills = data.get("kills", 0)
        state.log = list(data.get("log", []))
        state.player = Player.from_dict(data["player"])
        state.mobs = [Mob.from_dict(m) for m in data.get("mobs", [])]
        state.npcs = [NPC(**n) for n in data.get("npcs", [])]
        state.identification = deserialize_identification(data.get("identification", {}))
        state.journal = Journal.from_dict(data.get("journal", {}))
        state.visited_events = set(data.get("visited_events", []))
        state.final_boss_spawned = data.get("final_boss_spawned", False)

        # Восстановление предметов
        items_raw = data.get("items_on_floor", {})
        state.items_on_floor = {}
        for key, items in items_raw.items():
            x_str, y_str = key.split(",")
            state.items_on_floor[(int(x_str), int(y_str))] = list(items)

        # Восстановление подземелья
        ddata = data["dungeon"]
        dungeon = Dungeon(width=ddata["width"], height=ddata["height"])
        dungeon.tiles = ddata["tiles"]
        dungeon.visible = [[False for _ in range(dungeon.width)] for _ in range(dungeon.height)]
        dungeon.explored = [list(row) for row in ddata["explored"]]
        dungeon.rooms = [Room(x, y, w, h) for x, y, w, h in ddata["rooms"]]
        dungeon.stairs = tuple(ddata["stairs"])  # type: ignore
        dungeon.biome_id = ddata.get("biome_id", "dungeon")
        dungeon.hazards = {}
        for key, hid in ddata.get("hazards", {}).items():
            x_str, y_str = key.split(",")
            dungeon.hazards[(int(x_str), int(y_str))] = hid
        dungeon.traps = {}
        for key, tid in ddata.get("traps", {}).items():
            x_str, y_str = key.split(",")
            dungeon.traps[(int(x_str), int(y_str))] = tid
        dungeon.revealed_traps = set()
        for key in ddata.get("revealed_traps", []):
            x_str, y_str = key.split(",")
            dungeon.revealed_traps.add((int(x_str), int(y_str)))
        dungeon.interactables = {}
        for key, data in ddata.get("interactables", {}).items():
            x_str, y_str = key.split(",")
            dungeon.interactables[(int(x_str), int(y_str))] = data
        state.dungeon = dungeon
        return state
