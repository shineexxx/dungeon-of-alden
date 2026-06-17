"""Тест, что книги заклинаний могут спавниться в биомах."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from content.items import items_for_biome


def test_spellbooks_in_biomes():
    for tags in [["common", "dungeon"], ["common", "cave"], ["common", "crypt"]]:
        pool = items_for_biome(tags, depth=5)
        spellbooks = [iid for iid in pool if iid.startswith("spellbook_")]
        assert spellbooks, f"No spellbooks for biome tags {tags}"
        print(f"{tags}: {spellbooks}")
    print("Spellbooks spawn OK")


if __name__ == "__main__":
    test_spellbooks_in_biomes()
