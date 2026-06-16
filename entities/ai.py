"""ИИ-поведения мобов.

Каждая функция принимает:
    mob   — объект Mob
    state — GameState

Возвращает кортеж (action, target_x, target_y):
    action: "move" | "attack" | "ranged_attack" | "skip"
    target_x, target_y: для move — куда идти, для attack — цель,
                        для ranged_attack — цель, для skip — не важно.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.mob import Mob
    from systems.game_state import GameState


ActionResult = tuple[str, int, int]


def choose_ai_action(mob: "Mob", state: "GameState") -> ActionResult:
    """Диспетчер ИИ: выбрать поведение по полю mob.ai."""
    ai_type = mob.ai.upper()
    if ai_type == "AGGRESSIVE":
        return aggressive(mob, state)
    if ai_type == "RANGED":
        return ranged(mob, state)
    if ai_type == "COWARDLY":
        return cowardly(mob, state)
    if ai_type == "STATIONARY":
        return stationary(mob, state)
    if ai_type == "WANDERING":
        return wandering(mob, state)
    if ai_type == "PACK":
        return pack(mob, state)
    if ai_type == "CASTER":
        return caster(mob, state)
    return aggressive(mob, state)


def _distance(mob: "Mob", x: int, y: int) -> int:
    return abs(mob.x - x) + abs(mob.y - y)


def _line_is_clear(state: "GameState", x0: int, y0: int, x1: int, y1: int) -> bool:
    """Проверить, что линия стрельбы не заблокирована стенами (Брезенхем)."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    while True:
        if (x, y) != (x0, y0) and (x, y) != (x1, y1):
            if state.dungeon.blocks_sight(x, y):
                return False
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return True


def _adjacent_positions(state: "GameState", mob: "Mob") -> list[tuple[int, int]]:
    """Все соседние клетки, куда моб может шагнуть (не стены, не другие мобы, не игрок)."""
    positions = []
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = mob.x + dx, mob.y + dy
        if state.dungeon.blocks_movement(nx, ny):
            continue
        if state.player.x == nx and state.player.y == ny:
            continue
        occupied = False
        for other in state.mobs:
            if other is not mob and other.alive and other.x == nx and other.y == ny:
                occupied = True
                break
        if not occupied:
            positions.append((nx, ny))
    return positions


def aggressive(mob: "Mob", state: "GameState") -> ActionResult:
    """Преследует игрока вплотную."""
    px, py = state.player.x, state.player.y
    dist = _distance(mob, px, py)
    if dist == 1:
        return ("attack", px, py)
    return _step_toward(mob, state, px, py)


def ranged(mob: "Mob", state: "GameState") -> ActionResult:
    """Держит дистанцию 3-5 клеток, стреляет, если видит."""
    px, py = state.player.x, state.player.y
    dist = _distance(mob, px, py)

    # Если вплотную — отступаем
    if dist == 1:
        return _step_away(mob, state, px, py)

    # Если в зоне стрельбы и есть линия видимости — стреляем
    if 2 <= dist <= 5 and _line_is_clear(state, mob.x, mob.y, px, py):
        return ("ranged_attack", px, py)

    # Слишком далеко — подходим; слишком близко — отступаем
    if dist < 3:
        return _step_away(mob, state, px, py)
    return _step_toward(mob, state, px, py)


def cowardly(mob: "Mob", state: "GameState") -> ActionResult:
    """Атакует, но при HP <= 30% убегает."""
    px, py = state.player.x, state.player.y
    dist = _distance(mob, px, py)
    health_percent = mob.hp / mob.max_hp

    if health_percent <= 0.3:
        if dist <= 1:
            # Отскакиваем
            return _step_away(mob, state, px, py)
        return _step_away(mob, state, px, py)

    if dist == 1:
        return ("attack", px, py)
    return _step_toward(mob, state, px, py)


def stationary(mob: "Mob", state: "GameState") -> ActionResult:
    """Не двигается, атакует только если игрок вплотную."""
    px, py = state.player.x, state.player.y
    dist = _distance(mob, px, py)
    if dist == 1:
        return ("attack", px, py)
    return ("skip", mob.x, mob.y)


def wandering(mob: "Mob", state: "GameState") -> ActionResult:
    """Блуждает случайно; преследует, если игрок в 2 клетках."""
    px, py = state.player.x, state.player.y
    dist = _distance(mob, px, py)

    if dist == 1:
        return ("attack", px, py)
    if dist <= 2:
        return _step_toward(mob, state, px, py)

    positions = _adjacent_positions(state, mob)
    if positions:
        nx, ny = random.choice(positions)
        return ("move", nx, ny)
    return ("skip", mob.x, mob.y)


def pack(mob: "Mob", state: "GameState") -> ActionResult:
    """Стая: если рядом есть сородичи — агрессивно атакует; иначе осторожно."""
    px, py = state.player.x, state.player.y
    dist = _distance(mob, px, py)

    allies_near = sum(
        1
        for other in state.mobs
        if other is not mob and other.alive and other.id == mob.id and _distance(mob, other.x, other.y) <= 5
    )

    if dist == 1:
        return ("attack", px, py)

    if allies_near > 0:
        return _step_toward(mob, state, px, py)

    # Без поддержки ведём себя как WANDERING
    return wandering(mob, state)


def caster(mob: "Mob", state: "GameState") -> ActionResult:
    """Маг: если игрок в зоне досягаемости — кастует заклинание; иначе как RANGED."""
    px, py = state.player.x, state.player.y
    dist = _distance(mob, px, py)

    # Если вплотную — отступаем или бьём посохом
    if dist == 1:
        return _step_away(mob, state, px, py)

    # Кастуем с шансом, если игрок виден
    if state.dungeon.visible[mob.y][mob.x] and dist <= 6 and random.random() < 0.6:
        return ("cast_spell", px, py)

    # Иначе держим дистанцию как стрелок
    return ranged(mob, state)


def _step_toward(mob: "Mob", state: "GameState", tx: int, ty: int) -> ActionResult:
    """Сделать шаг к цели (по оси, которая дальше)."""
    positions = _adjacent_positions(state, mob)
    if not positions:
        return ("skip", mob.x, mob.y)

    # Сортируем по расстоянию до цели
    positions.sort(key=lambda p: abs(p[0] - tx) + abs(p[1] - ty))
    return ("move", positions[0][0], positions[0][1])


def _step_away(mob: "Mob", state: "GameState", tx: int, ty: int) -> ActionResult:
    """Сделать шаг от цели."""
    positions = _adjacent_positions(state, mob)
    if not positions:
        return ("skip", mob.x, mob.y)

    # Сортируем по убыванию расстояния до цели
    positions.sort(key=lambda p: abs(p[0] - tx) + abs(p[1] - ty), reverse=True)
    return ("move", positions[0][0], positions[0][1])
