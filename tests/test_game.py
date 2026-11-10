"""Automatic tests for Pizza Station Ares (Isaac-style Real-Time Edition).

Run with:   .venv/bin/python -m unittest discover -s tests -v
"""

import math
import os
import sys
import unittest
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dungeon import HATCH, DOOR_TILES, OPPOSITE_DIR          # noqa: E402
from entities import Monster                                 # noqa: E402
from game import Game                                        # noqa: E402
from items import Item                                       # noqa: E402
from settings import CELL, DOOR_X, DOOR_Y, FINAL_FLOOR       # noqa: E402
from sprites import SPRITES, PALETTE                         # noqa: E402


def reachable_rooms(dungeon):
    seen = {(0, 0)}
    todo = deque([(0, 0)])
    while todo:
        cur = todo.popleft()
        for nb in dungeon.rooms[cur].doors.values():
            if nb not in seen and nb in dungeon.rooms:
                seen.add(nb)
                todo.append(nb)
    return seen


def room_path(dungeon, start_pos, goal_pos):
    """BFS on the floor room graph; returns the first door direction to take."""
    if start_pos == goal_pos:
        return None
    came = {start_pos: (None, None)}
    todo = deque([start_pos])
    while todo:
        cur = todo.popleft()
        if cur == goal_pos:
            break
        for d, nb in dungeon.rooms[cur].doors.items():
            if nb not in came:
                came[nb] = (cur, d)
                todo.append(nb)
    if goal_pos not in came:
        return None
    step = goal_pos
    while came[step][0] != start_pos:
        step = came[step][0]
    return came[step][1]


def tile_step(room, start_px, goal_px):
    """Return a pixel target one tile step along the shortest walkable path inside `room`."""
    st = (int(start_px[0] // CELL), int(start_px[1] // CELL))
    gt = (int(goal_px[0] // CELL), int(goal_px[1] // CELL))
    if st == gt:
        return goal_px
    came = {st: None}
    todo = deque([st])
    while todo:
        cx, cy = todo.popleft()
        if (cx, cy) == gt:
            break
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = cx + dx, cy + dy
            if (nx, ny) not in came and (room.is_walkable(nx, ny, allow_doors=True) or (nx, ny) == gt):
                came[(nx, ny)] = (cx, cy)
                todo.append((nx, ny))
    if gt not in came:
        return goal_px
    step = gt
    while came[step] != st and came[step] is not None:
        step = came[step]
    return (step[0] + 0.5) * CELL, (step[1] + 0.5) * CELL


def has_line_of_sight(room, p1, p2):
    """Return True if a straight shot from p1 to p2 doesn't hit an obstacle."""
    dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    steps = max(1, int(dist // (CELL * 0.4)))
    for i in range(1, steps):
        t = i / steps
        x = p1[0] + (p2[0] - p1[0]) * t
        y = p1[1] + (p2[1] - p1[1]) * t
        if room.is_solid_for_shot(int(x // CELL), int(y // CELL)):
            return False
    return True


def bot_play(game, max_seconds=260.0):
    """An automated real-time player that dodges, aims, shoots, and clears floors."""
    dt = 0.05
    steps = int(max_seconds / dt)
    for _ in range(steps):
        if game.state != "playing":
            break
        p = game.player
        room = game.room

        # Eat pizza when below 60% HP
        if p.hp <= p.max_hp * 0.60 and p.pizzas > 0:
            game.eat_pizza()

        # 1. If monsters are in the room: kite and shoot the nearest monster
        if room.monsters:
            target = min(room.monsters, key=lambda m: math.hypot(m.x - p.x, m.y - p.y))
            dx = target.x - p.x
            dy = target.y - p.y
            dist = math.hypot(dx, dy) or 1.0
            cx, cy = (DOOR_X + 0.5) * CELL, (DOOR_Y + 0.5) * CELL
            if not has_line_of_sight(room, (p.x, p.y), (target.x, target.y)) or dist > 240.0:
                wp = tile_step(room, (p.x, p.y), (target.x, target.y))
                mx, my = wp[0] - p.x, wp[1] - p.y
            elif dist < 165.0:
                mx = -(dx / dist) + (cx - p.x) * 0.006
                my = -(dy / dist) + (cy - p.y) * 0.006
            else:
                mx, my = -dy / dist + (cx - p.x) * 0.004, dx / dist + (cy - p.y) * 0.004
            game.update(dt, mx, my, aim_target=(target.x, target.y), shooting=True)
            continue

        # 2. Room is clear: pick up any items in the room first
        if room.items:
            it = room.items[0]
            wp = tile_step(room, (p.x, p.y), (it.x, it.y))
            game.update(dt, wp[0] - p.x, wp[1] - p.y, shooting=False)
            continue

        # 3. If the delivery hatch is open in this room, walk onto it
        if room.hatch_spawned:
            hx, hy = (DOOR_X + 0.5) * CELL, (DOOR_Y + 0.5) * CELL
            wp = tile_step(room, (p.x, p.y), (hx, hy))
            game.update(dt, wp[0] - p.x, wp[1] - p.y, shooting=False)
            continue

        # 4. Otherwise navigate to the Treasure Room first, then the Boss Room
        t_pos = game.dungeon.treasure_pos
        if t_pos and not game.dungeon.rooms[t_pos].visited:
            goal_room = t_pos
        else:
            goal_room = game.dungeon.boss_pos

        door_dir = room_path(game.dungeon, game.current_pos, goal_room)
        if door_dir:
            dtx, dty = DOOR_TILES[door_dir]
            tx, ty = (dtx + 0.5) * CELL, (dty + 0.5) * CELL
            wp = tile_step(room, (p.x, p.y), (tx, ty))
            game.update(dt, wp[0] - p.x, wp[1] - p.y, shooting=False)
        else:
            game.update(dt, 0.0, 0.0, shooting=False)
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
    def test_every_floor_is_connected_and_has_boss_and_treasure(self):
        for seed in range(60):
            g = Game(seed)
            for floor in range(1, FINAL_FLOOR + 1):
                d = g.dungeon
                self.assertGreaterEqual(len(d.rooms), 5, f"seed {seed} floor {floor}")
                self.assertEqual(reachable_rooms(d), set(d.rooms.keys()))
                # Doors must be symmetric
                for pos, room in d.rooms.items():
                    for direction, nb in room.doors.items():
                        opp = OPPOSITE_DIR[direction]
                        self.assertEqual(d.rooms[nb].doors.get(opp), pos)
                boss_room = d.rooms[d.boss_pos]
                self.assertEqual(boss_room.role, "boss")
                self.assertTrue(len(boss_room.monsters) >= 1)
                if floor == FINAL_FLOOR:
                    self.assertTrue(any(m.kind == "calzone" for m in boss_room.monsters))
                else:
                    g.descend()

    def test_nothing_spawns_inside_walls_or_obstacles(self):
        for seed in range(50):
            g = Game(seed)
            for room in g.dungeon.rooms.values():
                for m in room.monsters:
                    tx, ty = int(m.x // CELL), int(m.y // CELL)
                    self.assertTrue(room.is_walkable(tx, ty))
                for i in room.items:
                    tx, ty = int(i.x // CELL), int(i.y // CELL)
                    self.assertTrue(room.is_walkable(tx, ty))

    def test_rolling_pin_on_floor_one(self):
        for seed in range(30):
            g = Game(seed)
            all_items = [i.key for r in g.dungeon.rooms.values() for i in r.items]
            self.assertIn("rolling_pin", all_items)


class TestRules(unittest.TestCase):
    def setUp(self):
        self.g = Game(1)
        self.room = self.g.room
        self.room.monsters.clear()
        self.room.items.clear()
        self.room.locked = False
        self.p = self.g.player

    def test_walls_block_movement(self):
        for _ in range(120):
            self.g.update(0.05, -1.0, 0.0)
        self.assertGreater(self.p.x, CELL)

    def test_shooting_hits_and_unlocks_doors(self):
        m = Monster(self.p.x + 140.0, self.p.y, "meatball")
        self.room.monsters.append(m)
        self.room.locked = True
        self.room.cleared = False

        for _ in range(120):
            if m not in self.room.monsters:
                break
            self.g.update(0.05, 0.0, 0.0, aim_target=(m.x, m.y), shooting=True)

        self.assertNotIn(m, self.room.monsters)
        self.assertFalse(self.room.locked)
        self.assertTrue(self.room.cleared)
        self.assertEqual(self.p.kills, 1)

    def test_monster_contact_and_iframes(self):
        m = Monster(self.p.x + 5.0, self.p.y, "anchovy")
        self.room.monsters.append(m)
        self.p.iframe_timer = 0.0
        start_hp = self.p.hp
        self.g.update(0.05, 0.0, 0.0)
        after_first_hit = self.p.hp
        self.assertLess(after_first_hit, start_hp)
        # Immediate next frame should be protected by i-frames
        self.g.update(0.05, 0.0, 0.0)
        self.assertEqual(self.p.hp, after_first_hit)

    def test_pizza_heals_but_not_above_max(self):
        self.p.hp = self.p.max_hp - 3
        self.p.pizzas = 2
        self.assertTrue(self.g.eat_pizza())
        self.assertEqual(self.p.hp, self.p.max_hp)
        self.assertEqual(self.p.pizzas, 1)
        self.assertFalse(self.g.eat_pizza())
        self.assertEqual(self.p.pizzas, 1)

    def test_items_are_picked_up(self):
        x, y = self.p.x + 10.0, self.p.y
        for key in ("rolling_pin", "cutter", "apron", "oxygen", "pizza"):
            self.room.items.append(Item(key, x, y))
        self.room.items.append(Item("credits", x, y, 7))
        start_attack, start_max = self.p.attack, self.p.max_hp
        self.g.update(0.05, 1.0, 0.0)
        self.assertEqual(self.room.items, [])
        self.assertEqual(self.p.weapon, "cutter")
        self.assertEqual(self.p.attack, start_attack + 4)
        self.assertEqual(self.p.defense, 2)
        self.assertEqual(self.p.max_hp, start_max + 5)
        self.assertEqual(self.p.pizzas, 2)
        self.assertGreaterEqual(self.p.credits, 7)

    def test_dying_and_winning(self):
        boss = Monster(self.p.x, self.p.y, "calzone")
        self.room.monsters.append(boss)
        self.p.hp = 1
        self.p.iframe_timer = 0.0
        self.g.update(0.05)
        self.assertEqual(self.g.state, "dead")

        g = Game(2)
        g.room.monsters.clear()
        boss = Monster(g.player.x + 80.0, g.player.y, "calzone")
        boss.hp = 1
        g.room.monsters.append(boss)
        for _ in range(30):
            if g.state == "won":
                break
            g.update(0.05, 0.0, 0.0, aim_target=(boss.x, boss.y), shooting=True)
        self.assertEqual(g.state, "won")


class TestFullGames(unittest.TestCase):
    def test_robot_plays_many_games_without_crashing(self):
        results = {"won": 0, "dead": 0, "playing": 0}
        floors = []
        for seed in range(60):
            g = bot_play(Game(seed))
            results[g.state] += 1
            floors.append(g.floor)
        print(
            f"\n  Real-time robot results over 60 games: {results}, "
            f"average floor reached {sum(floors) / len(floors):.1f}"
        )
        self.assertEqual(results["playing"], 0, "some games never finished")
        self.assertGreater(results["won"], 0, "the game should be winnable")


if __name__ == "__main__":
    unittest.main()
