"""Реестр эффектов предметов и заклинаний + статус-эффекты.

Каждый эффект — функция с сигнатурой:
    def effect_name(player: Player, state: GameState, power: Any) -> str:
        ...
        return "сообщение в лог"

power может быть int, tuple, dict.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from entities.player import Player
    from systems.game_state import GameState


EffectFunc = Callable[["Player", "GameState", Any], str]


EFFECTS: dict[str, EffectFunc] = {}


def apply_effect(effect_id: str, player: "Player", state: "GameState", power: Any = None) -> str:
    """Применить эффект по ID. Возвращает сообщение для лога."""
    effect = EFFECTS.get(effect_id)
    if effect is None:
        return "Ничего не произошло."
    return effect(player, state, power)


# --- Статус-эффекты ---

STATUS_DEFINITIONS: dict[str, dict] = {
    "burning": {
        "name": "Горит",
        "icon": "F",
        "color": "red",
        "tick": "damage_fire",
        "on_apply_msg": "{target} вспыхивает!",
        "on_tick_msg": "{target} горит! {power} урона.",
        "on_end_msg": "Огонь на {target} гаснет.",
        "stackable": False,
    },
    "poisoned": {
        "name": "Отравлен",
        "icon": "P",
        "color": "green",
        "tick": "damage_poison",
        "on_apply_msg": "{target} отравлен!",
        "on_tick_msg": "Яд жжёт {target}! {power} урона.",
        "on_end_msg": "Яд выходит из {target}.",
        "stackable": False,
    },
    "bleeding": {
        "name": "Кровотечение",
        "icon": "B",
        "color": "red",
        "tick": "damage_bleed",
        "on_apply_msg": "{target} истекает кровью!",
        "on_tick_msg": "{target} теряет {power} HP от кровотечения.",
        "on_end_msg": "Кровотечение у {target} остановилось.",
        "stackable": False,
    },
    "freezing": {
        "name": "Заморожен",
        "icon": "Z",
        "color": "cyan",
        "tick": "skip_chance",
        "on_apply_msg": "{target} покрывается инеем!",
        "on_tick_msg": "{target} замёрз и не может двигаться.",
        "on_end_msg": "Лед на {target} трескается.",
        "stackable": False,
    },
    "paralyzed": {
        "name": "Парализован",
        "icon": "X",
        "color": "blue",
        "tick": "skip",
        "on_apply_msg": "{target} парализован!",
        "on_tick_msg": "{target} не может пошевелиться.",
        "on_end_msg": "Паралич снимается с {target}.",
        "stackable": False,
    },
    "slowed": {
        "name": "Замедлен",
        "icon": "S",
        "color": "blue",
        "tick": None,
        "on_apply_msg": "{target} замедляется!",
        "on_tick_msg": "",
        "on_end_msg": "{target} снова движется быстро.",
        "stackable": False,
    },
    "hasted": {
        "name": "Ускорен",
        "icon": "H",
        "color": "green",
        "tick": None,
        "on_apply_msg": "{target} ускоряется!",
        "on_tick_msg": "",
        "on_end_msg": "Ускорение {target} заканчивается.",
        "stackable": False,
    },
    "regenerating": {
        "name": "Регенерация",
        "icon": "R",
        "color": "green",
        "tick": "heal_tick",
        "on_apply_msg": "{target} начинает регенерировать!",
        "on_tick_msg": "{target} восстанавливает {power} HP.",
        "on_end_msg": "Регенерация {target} прекращается.",
        "stackable": False,
    },
    "invisible": {
        "name": "Невидим",
        "icon": "I",
        "color": "cyan",
        "tick": None,
        "on_apply_msg": "{target} исчезает из виду!",
        "on_tick_msg": "",
        "on_end_msg": "{target} снова становится видимым.",
        "stackable": False,
    },
    "blessed": {
        "name": "Благословлён",
        "icon": "V",
        "color": "yellow",
        "tick": None,
        "on_apply_msg": "{target} окружён священной аурой!",
        "on_tick_msg": "",
        "on_end_msg": "Благословение сходит с {target}.",
        "stackable": False,
    },
    "stunned": {
        "name": "Оглушён",
        "icon": "U",
        "color": "yellow",
        "tick": "skip",
        "on_apply_msg": "{target} оглушён!",
        "on_tick_msg": "{target} в оцепенении.",
        "on_end_msg": "{target} приходит в себя.",
        "stackable": False,
    },
    "confused": {
        "name": "Спутан",
        "icon": "C",
        "color": "magenta",
        "tick": None,
        "on_apply_msg": "Голова {target} идёт кругом!",
        "on_tick_msg": "",
        "on_end_msg": "Сознание {target} проясняется.",
        "stackable": False,
    },
    "blind": {
        "name": "Слеп",
        "icon": "D",
        "color": "black",
        "tick": None,
        "on_apply_msg": "{target} ослеп!",
        "on_tick_msg": "",
        "on_end_msg": "Зрение {target} возвращается.",
        "stackable": False,
    },
    "detecting": {
        "name": "Обнаружение",
        "icon": "E",
        "color": "blue",
        "tick": None,
        "on_apply_msg": "{target} чувствует присутствие врагов!",
        "on_tick_msg": "",
        "on_end_msg": "Шестое чувство {target} угасает.",
        "stackable": False,
    },
    "ally": {
        "name": "Союзник",
        "icon": "A",
        "color": "white",
        "tick": None,
        "on_apply_msg": "{target} чувствует чью-то поддержку!",
        "on_tick_msg": "",
        "on_end_msg": "Союзник покидает {target}.",
        "stackable": False,
    },
}


def apply_status(target, status_id: str, duration: int, power: int = 1, state: "GameState | None" = None) -> str:
    """Наложить статус-эффект на цель (игрока или моба).
    Возвращает сообщение для лога."""
    definition = STATUS_DEFINITIONS.get(status_id)
    if not definition:
        return ""

    # Если статус не stackable — обновляем длительность
    existing = target.status_effects.get(status_id, 0)
    if not definition.get("stackable", False) and existing > 0:
        target.status_effects[status_id] = max(existing, duration)
    else:
        target.status_effects[status_id] = target.status_effects.get(status_id, 0) + duration

    target_name = _target_name(target)
    msg = definition["on_apply_msg"].format(target=target_name)
    if state and msg:
        state.log_message(msg)
    return msg


def _target_name(target) -> str:
    if hasattr(target, "name"):
        return target.name
    return "Вы"


def tick_status_effects(target, state: "GameState | None" = None) -> list[str]:
    """Тикнуть все статус-эффекты цели. Возвращает список сообщений."""
    messages = []
    expired = []
    target_name = _target_name(target)

    for status_id, turns in list(target.status_effects.items()):
        definition = STATUS_DEFINITIONS.get(status_id)
        if not definition:
            continue

        # Тиковые эффекты
        tick_type = definition.get("tick")
        power = 1
        if tick_type == "damage_fire":
            power = 3
            target.take_damage(power)
            msg = definition["on_tick_msg"].format(target=target_name, power=power)
        elif tick_type == "damage_poison":
            power = 2
            if turns % 2 == 0:
                target.take_damage(power)
                msg = definition["on_tick_msg"].format(target=target_name, power=power)
            else:
                msg = ""
        elif tick_type == "damage_bleed":
            power = 1
            target.take_damage(power)
            msg = definition["on_tick_msg"].format(target=target_name, power=power)
        elif tick_type == "heal_tick":
            power = 2
            target.heal(power)
            msg = definition["on_tick_msg"].format(target=target_name, power=power)
        elif tick_type == "skip":
            msg = definition["on_tick_msg"].format(target=target_name, power=power)
        elif tick_type == "skip_chance":
            msg = definition["on_tick_msg"].format(target=target_name, power=power)
        else:
            msg = ""

        if msg and state:
            state.log_message(msg)
            messages.append(msg)

        # Уменьшаем длительность
        target.status_effects[status_id] -= 1
        if target.status_effects[status_id] <= 0:
            expired.append(status_id)

    for status_id in expired:
        del target.status_effects[status_id]
        definition = STATUS_DEFINITIONS.get(status_id)
        if definition:
            msg = definition["on_end_msg"].format(target=target_name)
            if msg and state:
                state.log_message(msg)
                messages.append(msg)

    return messages


def is_paralyzed(target) -> bool:
    """Проверить, пропускает ли цель ход."""
    if "paralyzed" in target.status_effects and target.status_effects["paralyzed"] > 0:
        return True
    if "freezing" in target.status_effects and target.status_effects["freezing"] > 0 and random.random() < 0.5:
        return True
    if "stunned" in target.status_effects and target.status_effects["stunned"] > 0:
        return True
    return False


# --- Зелья ---

def heal_effect(player: "Player", state: "GameState", power: Any) -> str:
    amount = _roll_power(power, 8, 15)
    player.heal(amount)
    return f"Вы исцелены на {amount} HP."


def heal_major_effect(player: "Player", state: "GameState", power: Any) -> str:
    amount = _roll_power(power, 20, 35)
    player.heal(amount)
    return f"Сильное исцеление восстанавливает {amount} HP."


def restore_mana_effect(player: "Player", state: "GameState", power: Any) -> str:
    from systems.magic import initialize_magic

    initialize_magic(player)
    amount = _roll_power(power, 5, 10)
    before = player.mana
    player.mana = min(player.max_mana, player.mana + amount)
    restored = player.mana - before
    return f"Вы восстановили {restored} MP."


def max_hp_effect(player: "Player", state: "GameState", power: Any) -> str:
    amount = _roll_power(power, 5, 5)
    player.max_hp += amount
    player.hp += amount
    return f"Максимальное HP повышено на {amount}."


def strength_effect(player: "Player", state: "GameState", power: Any) -> str:
    player.atk += 1
    return "Вы чувствуете прилив силы! ATK +1."


def speed_effect(player: "Player", state: "GameState", power: Any) -> str:
    turns = _roll_power(power, 3, 3)
    apply_status(player, "hasted", turns, state=state)
    return f"Скорость повышена на {turns} хода."


def invisibility_effect(player: "Player", state: "GameState", power: Any) -> str:
    turns = _roll_power(power, 10, 10)
    apply_status(player, "invisible", turns, state=state)
    return f"Вы становитесь невидимым на {turns} ходов."


def levitation_effect(player: "Player", state: "GameState", power: Any) -> str:
    turns = _roll_power(power, 15, 15)
    player.status_effects["levitating"] = player.status_effects.get("levitating", 0) + turns
    return f"Вы парите над землёй на {turns} ходов."


def fire_breath_effect(player: "Player", state: "GameState", power: Any) -> str:
    """Конус огня: повреждает всех мобов в радиусе 3 клеток от игрока."""
    dmg = _roll_power(power, 10, 18)
    hits = 0
    for mob in state.mobs:
        if not mob.alive:
            continue
        dist = abs(mob.x - player.x) + abs(mob.y - player.y)
        if dist <= 3 and state.dungeon.visible[mob.y][mob.x]:
            mob.take_damage(dmg)
            apply_status(mob, "burning", 3, state=state)
            hits += 1
            if not mob.alive:
                from engine.game_loop import _on_mob_death
                _on_mob_death(state, mob)
    if hits:
        return f"Пламя охватывает {hits} существ, нанося {dmg} урона каждому."
    return "Пламя вырывается из ваших лёгких, но никого не задевает."


def confusion_effect(player: "Player", state: "GameState", power: Any) -> str:
    turns = _roll_power(power, 5, 5)
    apply_status(player, "confused", turns, state=state)
    return f"Голова идёт кругом! Вы спутаны на {turns} ходов."


def blindness_effect(player: "Player", state: "GameState", power: Any) -> str:
    turns = _roll_power(power, 10, 10)
    apply_status(player, "blind", turns, state=state)
    return f"Зрение пропадает! Вы слепы на {turns} ходов."


def experience_effect(player: "Player", state: "GameState", power: Any) -> str:
    amount = _roll_power(power, 50, 50)
    from systems.progression import add_xp
    levels = add_xp(player, amount)
    msg = f"Вы получаете {amount} опыта."
    if levels > 0:
        msg += f" Уровень повышен до {player.level}!"
    return msg


# --- Свитки ---

def identify_effect(player: "Player", state: "GameState", power: Any) -> str:
    """Опознать один неопознанный предмет в инвентаре.
    Реальная логика выбора находится в инвентаре; здесь заглушка."""
    return "Свиток опознания готов к использованию."


def mapping_effect(player: "Player", state: "GameState", power: Any) -> str:
    for y in range(state.dungeon.height):
        for x in range(state.dungeon.width):
            state.dungeon.explored[y][x] = True
    return "Карта уровня раскрыта перед вами."


def teleport_effect(player: "Player", state: "GameState", power: Any) -> str:
    candidates = [
        (x, y)
        for y in range(state.dungeon.height)
        for x in range(state.dungeon.width)
        if state.dungeon.is_floor(x, y)
    ]
    if candidates:
        x, y = random.choice(candidates)
        player.x, player.y = x, y
        return "Вы телепортированы в случайное место."
    return "Телепортация не удалась."


def magic_missile_effect(player: "Player", state: "GameState", power: Any) -> str:
    targets = [m for m in state.mobs if m.alive and state.dungeon.visible[m.y][m.x]]
    if not targets:
        return "Магическая стрела улетает в пустоту."
    target = random.choice(targets)
    dmg = _roll_power(power, 8, 14)
    target.take_damage(dmg)
    msg = f"Магическая стрела поражает {target.name} на {dmg} урона."
    if not target.alive:
        from engine.game_loop import _on_mob_death
        _on_mob_death(state, target)
    return msg


def summon_ally_effect(player: "Player", state: "GameState", power: Any) -> str:
    turns = _roll_power(power, 10, 10)
    apply_status(player, "ally", turns, state=state)
    return f"Вы чувствуете чью-то поддержку на {turns} ходов."


def remove_curse_effect(player: "Player", state: "GameState", power: Any) -> str:
    from content.items import get_item, get_equipment_details
    cursed = []
    for slot, item_id in [
        ("weapon", player.equipped_weapon),
        ("armor", player.equipped_armor),
    ]:
        if not item_id:
            continue
        data = get_item(item_id)
        if not data:
            continue
        details = get_equipment_details(item_id)
        if details and details.get("cursed"):
            cursed.append((slot, item_id, details))

    if not cursed:
        return "Проклятий не обнаружено."

    slot, item_id, details = cursed[0]
    details["cursed"] = False
    data = get_item(item_id)
    return f"Проклятие снято с {data['name']}."


def enchant_weapon_effect(player: "Player", state: "GameState", power: Any) -> str:
    if not player.equipped_weapon:
        return "У вас нет экипированного оружия."
    from content.items import get_item, get_equipment_details
    data = get_item(player.equipped_weapon)
    details = get_equipment_details(player.equipped_weapon)
    if details and data:
        d_min, d_max = details["damage"]
        details["damage"] = (d_min + 1, d_max + 1)
        return f"{data['name']} зачарован! Урон +1."
    return "Зачарование не удалось."


def enchant_armor_effect(player: "Player", state: "GameState", power: Any) -> str:
    if not player.equipped_armor:
        return "У вас нет экипированной брони."
    from content.items import get_item, get_equipment_details
    data = get_item(player.equipped_armor)
    details = get_equipment_details(player.equipped_armor)
    if details and data:
        details["defense"] = details.get("defense", 0) + 1
        return f"{data['name']} зачарована! Защита +1."
    return "Зачарование не удалось."


def fireball_effect(player: "Player", state: "GameState", power: Any) -> str:
    """AoE 3x3 вокруг игрока."""
    dmg = _roll_power(power, 12, 20)
    hits = 0
    for mob in state.mobs:
        if not mob.alive:
            continue
        if abs(mob.x - player.x) <= 1 and abs(mob.y - player.y) <= 1:
            mob.take_damage(dmg)
            apply_status(mob, "burning", 3, state=state)
            hits += 1
            if not mob.alive:
                from engine.game_loop import _on_mob_death
                _on_mob_death(state, mob)
    if hits:
        return f"Огненный шар взрывается, нанося {dmg} урона {hits} существам."
    return "Огненный шар вспыхивает, но никого не задевает."


def freeze_effect(player: "Player", state: "GameState", power: Any) -> str:
    turns = _roll_power(power, 3, 3)
    hits = 0
    for mob in state.mobs:
        if not mob.alive:
            continue
        if state.dungeon.visible[mob.y][mob.x]:
            apply_status(mob, "freezing", turns, state=state)
            hits += 1
    if hits:
        return f"{hits} существо(а) парализованы льдом на {turns} хода."
    return "Ледяная волна проходит мимо."


# --- Еда ---

def food_effect(player: "Player", state: "GameState", power: Any) -> str:
    amount = _roll_power(power, 30, 30)
    player.satiety = min(100, player.satiety + amount)
    return f"Вы поели. Сытость +{amount}."


def suspicious_food_effect(player: "Player", state: "GameState", power: Any) -> str:
    amount = _roll_power(power, 20, 20)
    player.satiety = min(100, player.satiety + amount)
    if random.random() < 0.3:
        apply_status(player, "poisoned", 10, state=state)
        return "Гриб оказался ядовитым! Сытость +20, но вы отравлены."
    return "Подозрительный гриб съедобен. Сытость +20."


# --- Артефакты ---

def artifact_effect(player: "Player", state: "GameState", power: Any) -> str:
    """Артефакты дают постоянные бонусы при использовании."""
    if isinstance(power, dict):
        bonus = power.get("bonus")
        value = power.get("value", 0)
        if bonus == "max_hp":
            player.max_hp += value
            player.hp += value
            return f"Максимальное HP повышено на {value}."
        if bonus == "xp_bonus":
            player.status_effects["xp_bonus"] = value
            return f"Получаемый опыт увеличен на {value}%."
        if bonus == "speed":
            player.status_effects["artifact_speed"] = value
            return "Скорость повышена артефактом."
        if bonus == "fov":
            player.fov_radius += value
            return f"Радиус обзора увеличен на {value}."
        if bonus == "fire_immune":
            player.status_effects["fire_immune"] = 1
            return "Вы получаете иммунитет к огню."
    return "Артефакт мерцает загадочной силой."


# --- Магические эффекты заклинаний ---

def damage_arcane_effect(player: "Player", state: "GameState", power: Any, target=None) -> str:
    if target is None:
        return "Нет цели."
    dmg = _roll_power(power, 3, 5)
    target.take_damage(dmg)
    msg = f"Магическая стрела поражает {target.name} на {dmg} урона."
    if not target.alive:
        from engine.game_loop import _on_mob_death
        _on_mob_death(state, target)
    return msg


def damage_fire_effect(player: "Player", state: "GameState", power: Any, target=None) -> str:
    if target is None:
        return "Нет цели."
    dmg = _roll_power(power, 10, 18)
    target.take_damage(dmg)
    apply_status(target, "burning", 3, state=state)
    msg = f"Огонь обжигает {target.name} на {dmg} урона."
    if not target.alive:
        from engine.game_loop import _on_mob_death
        _on_mob_death(state, target)
    return msg


def damage_ice_effect(player: "Player", state: "GameState", power: Any, target=None, status_duration: int = 3) -> str:
    if target is None:
        return "Нет цели."
    dmg = _roll_power(power, 6, 9)
    target.take_damage(dmg)
    apply_status(target, "slowed", status_duration, state=state)
    msg = f"Лёд пронзает {target.name} на {dmg} урона."
    if not target.alive:
        from engine.game_loop import _on_mob_death
        _on_mob_death(state, target)
    return msg


def damage_lightning_effect(player: "Player", state: "GameState", power: Any, target=None) -> str:
    if target is None:
        return "Нет цели."
    dmg = _roll_power(power, 8, 12)
    target.take_damage(dmg)
    msg = f"Молния ударяет {target.name} на {dmg} урона."
    if not target.alive:
        from engine.game_loop import _on_mob_death
        _on_mob_death(state, target)
    return msg


def damage_holy_effect(player: "Player", state: "GameState", power: Any, target=None) -> str:
    if target is None:
        return "Нет цели."
    dmg = _roll_power(power, 12, 18)
    if "undead" in getattr(target, "tags", []):
        dmg = int(dmg * 1.5)
        msg = f"Святой свет испепеляет {target.name} на {dmg} урона!"
    else:
        msg = f"Святой свет поражает {target.name} на {dmg} урона."
    target.take_damage(dmg)
    if not target.alive:
        from engine.game_loop import _on_mob_death
        _on_mob_death(state, target)
    return msg


def damage_earth_effect(player: "Player", state: "GameState", power: Any, target=None) -> str:
    if target is None:
        return "Нет цели."
    dmg = _roll_power(power, 5, 8)
    target.take_damage(dmg)
    apply_status(target, "stunned", 1, state=state)
    msg = f"Земля сотрясается под {target.name}, нанося {dmg} урона."
    if not target.alive:
        from engine.game_loop import _on_mob_death
        _on_mob_death(state, target)
    return msg


def chain_lightning_effect(player: "Player", state: "GameState", power: Any) -> str:
    targets = [m for m in state.mobs if m.alive and state.dungeon.visible[m.y][m.x]]
    if not targets:
        return "Молния ударяет в пустоту."
    random.shuffle(targets)
    hits = min(4, len(targets))
    total = 0
    msgs = []
    for i in range(hits):
        dmg = _roll_power(power, 6, 10)
        targets[i].take_damage(dmg)
        total += dmg
        msgs.append(f"{targets[i].name} ({dmg})")
        if not targets[i].alive:
            from engine.game_loop import _on_mob_death
            _on_mob_death(state, targets[i])
    return f"Цепная молния: {', '.join(msgs)}. Всего {total} урона."


def heal_magic_effect(player: "Player", state: "GameState", power: Any) -> str:
    amount = _roll_power(power, 15, 25)
    player.heal(amount)
    return f"Магия исцеляет вас на {amount} HP."


def buff_defense_effect(player: "Player", state: "GameState", power: Any) -> str:
    apply_status(player, "blessed", 10, state=state)
    player.ac += power if isinstance(power, int) else 5
    return f"Барьер повышает вашу защиту на {power}."


def buff_haste_effect(player: "Player", state: "GameState", power: Any) -> str:
    turns = power if isinstance(power, int) else 5
    apply_status(player, "hasted", turns, state=state)
    return f"Вы ускорены на {turns} ходов."


def buff_invisible_effect(player: "Player", state: "GameState", power: Any) -> str:
    turns = power if isinstance(power, int) else 10
    apply_status(player, "invisible", turns, state=state)
    return f"Вы невидимы на {turns} ходов."


def buff_regen_effect(player: "Player", state: "GameState", power: Any) -> str:
    turns = power if isinstance(power, int) else 8
    apply_status(player, "regenerating", turns, state=state)
    return f"Регенерация на {turns} ходов."


def reveal_effect(player: "Player", state: "GameState", power: Any) -> str:
    turns = power if isinstance(power, int) else 5
    apply_status(player, "detecting", turns, state=state)
    count = sum(1 for m in state.mobs if m.alive)
    return f"Вы чувствуете {count} врагов на уровне."


def banish_effect(player: "Player", state: "GameState", power: Any, target=None) -> str:
    if target is None:
        return "Нет цели."
    target.alive = False
    return f"{target.name} исчезает в вспышке света!"


# --- Утилиты ---

def _roll_power(power: Any, default_min: int, default_max: int) -> int:
    if isinstance(power, (list, tuple)) and len(power) == 2:
        return random.randint(int(power[0]), int(power[1]))
    if isinstance(power, int):
        return power
    return random.randint(default_min, default_max)


# Регистрация эффектов
EFFECTS.update({
    # Зелья
    "heal": heal_effect,
    "heal_major": heal_major_effect,
    "restore_mana": restore_mana_effect,
    "max_hp": max_hp_effect,
    "strength": strength_effect,
    "speed": speed_effect,
    "invisibility": invisibility_effect,
    "levitation": levitation_effect,
    "fire_breath": fire_breath_effect,
    "confusion": confusion_effect,
    "blindness": blindness_effect,
    "experience": experience_effect,
    # Свитки
    "identify": identify_effect,
    "mapping": mapping_effect,
    "teleport": teleport_effect,
    "magic_missile": magic_missile_effect,
    "summon_ally": summon_ally_effect,
    "remove_curse": remove_curse_effect,
    "enchant_weapon": enchant_weapon_effect,
    "enchant_armor": enchant_armor_effect,
    "fireball": fireball_effect,
    "freeze": freeze_effect,
    # Еда
    "food": food_effect,
    "suspicious_food": suspicious_food_effect,
    # Артефакты
    "artifact": artifact_effect,
    # Магия
    "damage_arcane": damage_arcane_effect,
    "damage_fire": damage_fire_effect,
    "damage_ice": damage_ice_effect,
    "damage_lightning": damage_lightning_effect,
    "damage_holy": damage_holy_effect,
    "damage_earth": damage_earth_effect,
    "chain_lightning": chain_lightning_effect,
    "heal_spell": heal_magic_effect,
    "buff_defense": buff_defense_effect,
    "buff_haste": buff_haste_effect,
    "buff_invisible": buff_invisible_effect,
    "buff_regen": buff_regen_effect,
    "reveal": reveal_effect,
    "banish": banish_effect,
})
