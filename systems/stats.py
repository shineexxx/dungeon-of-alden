"""Пересчёт статов игрока с учётом экипировки, перков и уровня."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.player import Player


BASE_HP = 30
BASE_ATK = 1
BASE_AC = 0
BASE_SPEED = 1.0
BASE_FOV = 8


def recalculate_stats(player: "Player") -> None:
    """Пересчитать все производные статы игрока."""
    from content.items import get_item, get_equipment_details

    # Базовые значения + бонусы уровня
    hp = BASE_HP + (player.level - 1) * 5
    atk = BASE_ATK + (player.level - 1) * 1
    ac = BASE_AC
    speed = BASE_SPEED
    fov = BASE_FOV
    max_mana = player.max_mana + (player.level - 1) * 2

    # Перки
    for perk in player.perks:
        if perk == "hp":
            hp += 8
        elif perk == "atk":
            atk += 2
        elif perk == "ac":
            ac += 1
        elif perk == "fov":
            fov += 1
        elif perk == "mana":
            max_mana += 5
        elif perk == "mana_regen":
            pass  # реген маны обрабатывается отдельно

    # Оружие
    if player.equipped_weapon:
        weapon_data = get_item(player.equipped_weapon)
        if weapon_data and weapon_data["type"] == "weapon":
            w = get_equipment_details(player.equipped_weapon)
            if w:
                atk += (w["damage"][0] + w["damage"][1]) // 4
                speed += w.get("speed", 1.0) - 1.0

    # Броня
    if player.equipped_armor:
        armor_data = get_item(player.equipped_armor)
        if armor_data and armor_data["type"] == "armor":
            a = get_equipment_details(player.equipped_armor)
            if a:
                ac += a["defense"]
                hp += a.get("hp_bonus", 0)
                speed += a.get("speed_penalty", 0.0)

    # Кольца
    for ring_slot in (player.equipped_left_ring, player.equipped_right_ring):
        if ring_slot:
            ring_data = get_item(ring_slot)
            if ring_data and ring_data["type"] == "ring":
                effect = ring_data["effect_power"]
                bonus = effect.get("bonus")
                value = effect.get("value", 0)
                if bonus == "hp":
                    hp += value
                elif bonus == "atk":
                    atk += value
                elif bonus == "def":
                    ac += value
                elif bonus == "speed":
                    speed += value * 0.1
                elif bonus == "fov":
                    fov += value
                # luck пока не влияет на механику напрямую

    # Артефакты (если в инвентаре — дают бонусы)
    for item_id, count in player.inventory.items():
        if count <= 0:
            continue
        data = get_item(item_id)
        if not data or data["type"] != "artifact":
            continue
        power = data.get("effect_power", {})
        if not isinstance(power, dict):
            continue
        bonus = power.get("bonus")
        value = power.get("value", 0)
        if bonus == "max_hp":
            hp += value
        elif bonus == "speed":
            speed += value * 0.1
        elif bonus == "fov":
            fov += value
        # xp_bonus и fire_immune обрабатываются отдельно через status_effects

    # Статус-эффекты
    if player.status_effects.get("haste", 0) > 0:
        speed += 0.3
    if player.status_effects.get("artifact_speed", 0) > 0:
        speed += player.status_effects["artifact_speed"] * 0.1

    # Применяем
    old_max_hp = player.max_hp
    player.max_hp = max(1, hp)
    player.atk = max(0, atk)
    player.ac = max(0, ac)
    player.speed = max(0.1, speed)
    player.fov_radius = max(1, fov)
    player.max_mana = max(0, max_mana)
    if player.mana > player.max_mana:
        player.mana = player.max_mana

    if player.hp > player.max_hp:
        player.hp = player.max_hp
    if player.max_hp > old_max_hp:
        player.hp += player.max_hp - old_max_hp

    # Слепота временно уменьшает FOV
    if player.status_effects.get("blind", 0) > 0:
        player.fov_radius = 1
