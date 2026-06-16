"""Монстры / мобы."""

from __future__ import annotations

import curses
from dataclasses import dataclass, field

from content.monsters import get_monster
from engine.render import COLOR_MAP, COLOR_PAIRS


@dataclass
class Mob:
    id: str
    name: str
    char: str
    unicode_char: str
    color_pair: int
    x: int
    y: int
    hp: int
    max_hp: int
    atk: int
    dmg: tuple[int, int, int]
    ac: int
    speed: float
    xp: int
    ai: str
    gold_min: int
    gold_max: int
    loot_chance: float
    loot_table: list[str]
    energy: float = 0.0
    alive: bool = True
    status_effects: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_data(cls, monster_id: str, x: int, y: int) -> "Mob":
        data = get_monster(monster_id)
        if data is None:
            raise ValueError(f"Unknown monster id: {monster_id}")

        color_name = data.get("color", "white")
        color_code = COLOR_MAP.get(color_name, curses.COLOR_WHITE)
        pair_id = _resolve_color_pair(color_code)

        return cls(
            id=monster_id,
            name=data["name"],
            char=data["char"],
            unicode_char=data.get("unicode_char", data["char"]),
            color_pair=pair_id,
            x=x,
            y=y,
            hp=data["hp"],
            max_hp=data["hp"],
            atk=data["atk"],
            dmg=tuple(data["dmg"]),  # type: ignore
            ac=data["ac"],
            speed=data.get("speed", 1.0),
            xp=data["xp"],
            ai=data.get("ai", "AGGRESSIVE"),
            gold_min=data.get("gold", (0, 0))[0],
            gold_max=data.get("gold", (0, 0))[1],
            loot_chance=data.get("loot_chance", 0.0),
            loot_table=list(data.get("loot_table", [])),
        )

    def is_alive(self) -> bool:
        return self.alive

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def roll_gold(self, rng) -> int:
        if self.gold_max <= self.gold_min:
            return self.gold_min
        return rng.randint(self.gold_min, self.gold_max)

    def roll_loot(self, rng) -> str | None:
        if not self.loot_table:
            return None
        if rng.random() < self.loot_chance:
            return rng.choice(self.loot_table)
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "alive": self.alive,
            "energy": self.energy,
            "status_effects": dict(self.status_effects),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Mob":
        mob = cls.from_data(data["id"], data["x"], data["y"])
        mob.hp = data["hp"]
        mob.max_hp = data["max_hp"]
        mob.alive = data["alive"]
        mob.energy = data.get("energy", 0.0)
        mob.status_effects = dict(data.get("status_effects", {}))
        return mob


def _resolve_color_pair(color_code: int) -> int:
    """Сопоставить код цвета curses с парой из engine/render."""
    for pair_id, (fg_name, _) in COLOR_PAIRS.items():
        if COLOR_MAP.get(fg_name, curses.COLOR_WHITE) == color_code:
            return pair_id
    return 6  # fallback: мобы
