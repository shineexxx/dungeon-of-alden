"""Игрок."""

from __future__ import annotations

from dataclasses import dataclass, field

from systems.progression import xp_to_next_level


@dataclass
class Player:
    x: int
    y: int
    hp: int = 30
    max_hp: int = 30
    atk: int = 1
    ac: int = 0
    xp: int = 0
    level: int = 1
    gold: int = 0
    speed: float = 1.0
    fov_radius: int = 8
    satiety: int = 100
    max_mana: int = 10
    mana: int = 10
    perks: list[str] = field(default_factory=list)
    inventory: dict[str, int] = field(default_factory=dict)  # item_id -> count
    status_effects: dict[str, int] = field(default_factory=dict)  # effect -> turns
    known_spells: list[str] = field(default_factory=list)
    spell_cooldowns: dict[str, int] = field(default_factory=dict)
    equipped_weapon: str | None = None
    equipped_armor: str | None = None
    equipped_left_ring: str | None = None
    equipped_right_ring: str | None = None

    def is_alive(self) -> bool:
        return self.hp > 0

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def xp_to_next(self) -> int:
        return xp_to_next_level(self.level)

    def total_inventory_count(self) -> int:
        """Общее количество предметов в рюкзаке (не экипировка, не золото)."""
        return sum(
            count
            for item_id, count in self.inventory.items()
            if get_item(item_id) and get_item(item_id)["type"] not in ("gold",)
        )

    def equipped_items(self) -> list[str]:
        """Список надетых предметов."""
        items = []
        if self.equipped_weapon:
            items.append(self.equipped_weapon)
        if self.equipped_armor:
            items.append(self.equipped_armor)
        if self.equipped_left_ring:
            items.append(self.equipped_left_ring)
        if self.equipped_right_ring:
            items.append(self.equipped_right_ring)
        return items

    def is_equipped(self, item_id: str) -> bool:
        return item_id in self.equipped_items()

    def satiety_status(self) -> str:
        if self.satiety >= 50:
            return "сыт"
        if self.satiety >= 20:
            return "голоден"
        if self.satiety > 0:
            return "очень голоден"
        return "истощён"

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "atk": self.atk,
            "ac": self.ac,
            "xp": self.xp,
            "level": self.level,
            "gold": self.gold,
            "speed": self.speed,
            "fov_radius": self.fov_radius,
            "satiety": self.satiety,
            "max_mana": self.max_mana,
            "mana": self.mana,
            "perks": list(self.perks),
            "inventory": dict(self.inventory),
            "status_effects": dict(self.status_effects),
            "known_spells": list(self.known_spells),
            "spell_cooldowns": dict(self.spell_cooldowns),
            "equipped_weapon": self.equipped_weapon,
            "equipped_armor": self.equipped_armor,
            "equipped_left_ring": self.equipped_left_ring,
            "equipped_right_ring": self.equipped_right_ring,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        return cls(
            x=data["x"],
            y=data["y"],
            hp=data["hp"],
            max_hp=data["max_hp"],
            atk=data["atk"],
            ac=data["ac"],
            xp=data["xp"],
            level=data["level"],
            gold=data["gold"],
            speed=data.get("speed", 1.0),
            fov_radius=data.get("fov_radius", 8),
            satiety=data.get("satiety", 100),
            max_mana=data.get("max_mana", 10),
            mana=data.get("mana", 10),
            perks=list(data.get("perks", [])),
            inventory=dict(data.get("inventory", {})),
            status_effects=dict(data.get("status_effects", {})),
            known_spells=list(data.get("known_spells", [])),
            spell_cooldowns=dict(data.get("spell_cooldowns", {})),
            equipped_weapon=data.get("equipped_weapon"),
            equipped_armor=data.get("equipped_armor"),
            equipped_left_ring=data.get("equipped_left_ring"),
            equipped_right_ring=data.get("equipped_right_ring"),
        )


def get_item(item_id: str):
    """Локальный хелпер для избежания циклического импорта."""
    from content.items import get_item as _get_item
    return _get_item(item_id)
