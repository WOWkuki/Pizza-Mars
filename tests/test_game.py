"""Automatic tests for Pizza Station Ares.

Run with:   .venv/bin/python -m unittest discover -s tests -v
"""

import os
import sys
import unittest
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dungeon import HATCH                       # noqa: E402
from entities import Monster                    # noqa: E402
from game import Game, DIRECTIONS               # noqa: E402
from items import Item                          # noqa: E402
from settings import FINAL_FLOOR                # noqa: E402
from sprites import SPRITES, PALETTE            # noqa: E402


def reachable(dungeon, start):
    seen, todo = {start}, deque([start])
    while todo:
        x, y = todo.popleft()
        for dx, dy in DIRECTIONS:
            n = (x + dx, y + dy)
            if n not in seen and dungeon.is_walkable(*n):
                seen.add(n)
                todo.append(n)
    return seen


def bot_play(game, max_turns=4000):
    """A simple robot player: eat when hurt, fight, grab items, find the hatch."""
    stuck = 0
    while game.state == "playing" and game.turn < max_turns:
        p = game.player
        if p.hp <= p.max_hp * 0.45 and p.pizzas and game.eat_pizza():
            continue
        targets = [(m.x, m.y) for m in game.monsters]
        targets += [(i.x, i.y) for i in game.items]
        if game.dungeon.hatch:
            targets.append(game.dungeon.hatch)
        start = (p.x, p.y)
        came = {start: None}
        todo = deque([start])
        goal = None
        target_set = set(targets)
        while todo:
            cur = todo.popleft()
            if cur in target_set and cur != start:
                goal = cur
                break
            for dx, dy in DIRECTIONS:
                n = (cur[0] + dx, cur[1] + dy)
                if n not in came and game.dungeon.is_walkable(*n):
                    came[n] = cur
                    todo.append(n)
        moved = False
        if goal:
            step = goal
            while came[step] != start:
                step = came[step]
            moved = game.player_move(step[0] - p.x, step[1] - p.y)
        if not moved:
            game.player_wait()
            stuck += 1
            if stuck > 500:
                raise AssertionError("bot got stuck")
    return game


class TestSprites(unittest.TestCase):
    def test_sprites_are_16x16_and_use_palette(self):
        for name, rows in SPRITES.items():
            self.assertEqual(len(rows), 16, name)
            for row in rows:
                self.assertEqual(len(row), 16, f"{name}: '{row}'")
                for ch in row:
                    self.assertTrue(ch == "." or ch in PALETTE, f"{name}: bad colour '{ch}'")


class TestDungeon(unittest.TestCase):
    def test_every_floor_is_fully_connected(self):
        for seed in range(150):
            g = Game(seed)
            for floor in range(1, FINAL_FLOOR + 1):
                d = g.dungeon
                self.assertGreaterEqual(len(d.rooms), 4, f"seed {seed} floor {floor}")
                walkable = {(x, y) for y in range(d.height) for x in range(d.width) if d.is_walkable(x, y)}
                self.assertEqual(reachable(d, (g.player.x, g.player.y)), walkable)
                if floor < FINAL_FLOOR:
                    hx, hy = d.hatch
                    self.assertEqual(d.tiles[hy][hx], HATCH)
                    g.descend()
                else:
                    self.assertIsNone(d.hatch)
                    self.assertIsNotNone(g.boss, f"seed {seed}: no boss")

    def test_nothing_spawns_inside_walls_or_on_top_of_each_other(self):
        for seed in range(100):
            g = Game(seed)
            spots = [(m.x, m.y) for m in g.monsters] + [(g.player.x, g.player.y)]
            self.assertEqual(len(spots), len(set(spots)))
            for x, y in spots + [(i.x, i.y) for i in g.items]:
                self.assertTrue(g.dungeon.is_walkable(x, y))

    def test_rolling_pin_on_floor_one(self):
        for seed in range(50):
            self.assertTrue(any(i.key == "rolling_pin" for i in Game(seed).items))


class TestRules(unittest.TestCase):
    def setUp(self):
        self.g = Game(1)
        self.g.monsters.clear()
        self.g.items.clear()
        self.p = self.g.player

    def free_neighbour(self):
        for dx, dy in DIRECTIONS:
            if self.g.is_free(self.p.x + dx, self.p.y + dy):
                return dx, dy
        self.fail("no free neighbour")

    def test_walls_block_and_cost_no_turn(self):
        d = self.g.dungeon
        # walk left until we hit a wall
        while d.is_walkable(self.p.x - 1, self.p.y):
            self.assertTrue(self.g.player_move(-1, 0))
        turn = self.g.turn
        self.assertFalse(self.g.player_move(-1, 0))
        self.assertEqual(self.g.turn, turn)

    def test_attack_kills_and_drops_credits(self):
        dx, dy = self.free_neighbour()
        m = Monster(self.p.x + dx, self.p.y + dy, "meatball")
        self.g.monsters.append(m)
        for _ in range(20):
            if m not in self.g.monsters:
                break
            self.g.player_move(dx, dy)
        self.assertNotIn(m, self.g.monsters)
        self.assertEqual(self.p.kills, 1)
        self.assertTrue(self.p.hp > 0)

    def test_monster_attacks_player(self):
        dx, dy = self.free_neighbour()
        self.g.monsters.append(Monster(self.p.x + dx, self.p.y + dy, "anchovy"))
        self.g.player_wait()
        self.assertLess(self.p.hp, self.p.max_hp)

    def test_pizza_heals_but_not_above_max(self):
        self.p.hp = self.p.max_hp - 3
        self.p.pizzas = 2
        self.assertTrue(self.g.eat_pizza())
        self.assertEqual(self.p.hp, self.p.max_hp)
        self.assertEqual(self.p.pizzas, 1)
        self.assertFalse(self.g.eat_pizza())   # already full: no pizza wasted
        self.assertEqual(self.p.pizzas, 1)

    def test_items_are_picked_up(self):
        dx, dy = self.free_neighbour()
        x, y = self.p.x + dx, self.p.y + dy
        for key in ("rolling_pin", "cutter", "apron", "oxygen", "pizza"):
            self.g.items.append(Item(key, x, y))
        self.g.items.append(Item("credits", x, y, 7))
        start_attack, start_max = self.p.attack, self.p.max_hp
        self.g.player_move(dx, dy)
        self.assertEqual(self.g.items, [])
        self.assertEqual(self.p.weapon, "cutter")       # best weapon is kept
        self.assertEqual(self.p.attack, start_attack + 4)
        self.assertEqual(self.p.defense, 2)
        self.assertEqual(self.p.max_hp, start_max + 5)
        self.assertEqual(self.p.pizzas, 2)
        self.assertGreaterEqual(self.p.credits, 7)

    def test_dying_and_winning(self):
        dx, dy = self.free_neighbour()
        boss = Monster(self.p.x + dx, self.p.y + dy, "calzone")
        self.g.monsters.append(boss)
        self.p.hp = 1
        self.g.player_wait()
        self.assertEqual(self.g.state, "dead")
        self.assertFalse(self.g.player_move(1, 0))      # no moving when dead

        g = Game(2)
        g.monsters.clear()
        p = g.player
        for dx, dy in DIRECTIONS:
            if g.is_free(p.x + dx, p.y + dy):
                break
        boss = Monster(p.x + dx, p.y + dy, "calzone")
        boss.hp = 1
        g.monsters.append(boss)
        g.player_move(dx, dy)
        self.assertEqual(g.state, "won")


class TestFullGames(unittest.TestCase):
    def test_robot_plays_many_games_without_crashing(self):
        results = {"won": 0, "dead": 0, "playing": 0}
        floors = []
        for seed in range(150):
            g = bot_play(Game(seed))
            results[g.state] += 1
            floors.append(g.floor)
        print(f"\n  Robot results over 150 games: {results}, "
              f"average floor reached {sum(floors) / len(floors):.1f}")
        self.assertEqual(results["playing"], 0, "some games never ended")
        self.assertGreater(results["won"], 0, "the game should be winnable")


if __name__ == "__main__":
    unittest.main()
