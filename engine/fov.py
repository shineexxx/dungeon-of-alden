"""Поле зрения (FOV) и туман войны."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.dungeon import Dungeon


def compute_fov(dungeon: "Dungeon", px: int, py: int, radius: int) -> None:
    """Обновить массивы visible и explored подземелья."""
    # Сброс видимости
    for y in range(dungeon.height):
        for x in range(dungeon.width):
            dungeon.visible[y][x] = False

    # Проверяем 360 лучей
    for deg in range(360):
        angle = math.radians(deg)
        dx = math.cos(angle)
        dy = math.sin(angle)
        _cast_ray(dungeon, px, py, dx, dy, radius)

    # Позиция игрока всегда видна
    dungeon.visible[py][px] = True
    dungeon.explored[py][px] = True


def _cast_ray(dungeon: "Dungeon", x0: int, y0: int, dx: float, dy: float, radius: int) -> None:
    """Бросить один луч и пометить видимые клетки."""
    x = float(x0) + 0.5
    y = float(y0) + 0.5
    for _ in range(radius):
        ix = int(x)
        iy = int(y)
        if not dungeon.in_bounds(ix, iy):
            break
        dungeon.visible[iy][ix] = True
        dungeon.explored[iy][ix] = True
        if dungeon.blocks_sight(ix, iy):
            break
        x += dx
        y += dy
