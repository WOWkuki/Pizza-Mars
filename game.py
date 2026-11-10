"""Game rules for Pizza Station Ares.

There is no drawing code in this file. That keeps the rules easy to read
and lets us test the game automatically (see tests/test_game.py).
"""

import random
from collections import deque

from settings import MAP_W, MAP_H, FOV_RADIUS, FINAL_FLOOR, PIZZA_HEAL, REGEN_EVERY
from dungeon import Dungeon, FLOOR, HATCH
from entities import Player, Monster, DEATH_TEXT
from items import Item, ITEM_TYPES

# Message colours (R, G, B)
WHITE = (230, 230, 230)
RED = (235, 90, 80)
GREEN = (120, 220, 120)
YELLOW = (250, 210, 90)
ORANGE = (240, 150, 60)
CYAN = (110, 210, 240)

# The 8 directions a creature can move in
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

FLOOR_NAMES = {
    1: "Dining Deck",
    2: "Kitchen Deck",
    3: "Cold Storage",
    4: "Oven Core",
    5: "The Calzone's Lair",
}


class Game:
    def __init__(self, seed=None):
        self.seed = seed if seed is not None else random.randrange(1_000_000)
        self.rng = random.Random(self.seed)
        self.messages = []          # list of (text, colour)
        self.state = "playing"      # "playing", "dead" or "won"
        self.floor = 1
        self.turn = 0
        self.killer = None
        self.player = Player(0, 0)
        self.new_floor()
        self.log("Welcome to Pizza Station Ares, chef!", ORANGE)
        self.log("Monsters took over the pizzeria. Go down 5 floors "
                 "and defeat the Giant Calzone!", WHITE)

    # ------------------------------------------------------------------ utils
    def log(self, text, colour=WHITE):
        self.messages.append((text, colour))
        self.messages = self.messages[-60:]

    def monster_at(self, x, y):
        for m in self.monsters:
            if m.x == x and m.y == y:
                return m
        return None

    def is_free(self, x, y):
        """Walkable, and nobody is standing there."""
        p = self.player
        return (self.dungeon.is_walkable(x, y) and self.monster_at(x, y) is None
                and (p.x, p.y) != (x, y))

    @property
    def boss(self):
        for m in self.monsters:
            if m.kind == "calzone":
                return m
        return None

    @property
    def score(self):
        p = self.player
        return p.credits + p.kills * 10 + (self.floor - 1) * 50 + (500 if self.state == "won" else 0)

    # ------------------------------------------------------------ floor setup
    def new_floor(self):
        final = self.floor == FINAL_FLOOR
        self.dungeon = Dungeon(MAP_W, MAP_H, self.rng)
        self.dungeon.generate(place_hatch=not final)
        self.monsters = []
        self.items = []
        self.player.x, self.player.y = self.dungeon.rooms[0].center()
        self.populate()
        if final:
            bx, by = self.dungeon.farthest_room().center()
            self.monsters.append(Monster(bx, by, "calzone"))
            self.log("You smell burnt cheese... the Giant Calzone is near!", YELLOW)
        self.update_fov()

    def free_tile_in(self, room):
        for _ in range(30):
            x = self.rng.randint(room.x, room.x + room.w - 1)
            y = self.rng.randint(room.y, room.y + room.h - 1)
            if (self.dungeon.tiles[y][x] == FLOOR and self.is_free(x, y)
                    and not any(i.x == x and i.y == y for i in self.items)):
                return x, y
        return None

    def pick_monster_type(self):
        weights = {"meatball": 6, "drone": 1 + self.floor, "anchovy": max(0, 2 * self.floor - 2)}
        return self.rng.choices(list(weights), weights=list(weights.values()))[0]

    def pick_item_type(self):
        f = self.floor
        weights = {"pizza": 35, "credits": 30, "oxygen": 8, "apron": 4,
                   "rolling_pin": 5 if f <= 2 else 0, "cutter": 4 if f >= 2 else 0}
        return self.rng.choices(list(weights), weights=list(weights.values()))[0]

    def place_item(self, key, room):
        pos = self.free_tile_in(room)
        if pos:
            amount = self.rng.randint(2, 5) + self.floor if key == "credits" else 1
            self.items.append(Item(key, *pos, amount))

    def populate(self):
        rooms = self.dungeon.rooms
        for room in rooms[1:]:   # the first room is safe
            for _ in range(self.rng.randint(0, 1 + self.floor // 3)):
                pos = self.free_tile_in(room)
                if pos:
                    self.monsters.append(Monster(*pos, self.pick_monster_type(), self.floor - 1))
            if self.rng.random() < 0.6:
                self.place_item(self.pick_item_type(), room)
        # Guaranteed weapons so every run is winnable
        if self.floor == 1:
            self.place_item("rolling_pin", self.rng.choice(rooms))
        if self.floor == 3:
            self.place_item("cutter", self.rng.choice(rooms))

    def update_fov(self):
        self.dungeon.compute_fov(self.player.x, self.player.y, FOV_RADIUS)

    # -------------------------------------------------------- player actions
    # Every action returns True if it used up the player's turn.
    def player_move(self, dx, dy):
        if self.state != "playing":
            return False
        p = self.player
        nx, ny = p.x + dx, p.y + dy
        target = self.monster_at(nx, ny)
        if target:
            self.attack(p, target)
            self.end_turn()
            return True
        if not self.dungeon.is_walkable(nx, ny):
            return False
        p.x, p.y = nx, ny
        self.pickup_items()
        if self.dungeon.tiles[ny][nx] == HATCH:
            self.descend()
            return True
        self.end_turn()
        return True

    def player_wait(self):
        if self.state != "playing":
            return False
        self.end_turn()
        return True

    def eat_pizza(self):
        if self.state != "playing":
            return False
        p = self.player
        if p.pizzas <= 0:
            self.log("You have no pizza left!", RED)
            return False
        if p.hp >= p.max_hp:
            self.log("You are already at full health.", WHITE)
            return False
        p.pizzas -= 1
        healed = min(PIZZA_HEAL, p.max_hp - p.hp)
        p.hp += healed
        self.log(f"You eat a pizza slice. Delicious! (+{healed} HP)", GREEN)
        self.end_turn()
        return True

    def pickup_items(self):
        p = self.player
        for item in [i for i in self.items if i.x == p.x and i.y == p.y]:
            self.items.remove(item)
            self.apply_item(item)

    def apply_item(self, item):
        p = self.player
        t = ITEM_TYPES[item.key]
        kind = t["kind"]
        if kind == "consumable":
            p.pizzas += 1
            self.log("You pick up a Pizza Slice. (press H to eat)", GREEN)
        elif kind == "maxhp":
            p.max_hp += t["amount"]
            p.hp = min(p.max_hp, p.hp + t["amount"])
            self.log(f"Oxygen Tank! Max HP +{t['amount']}.", CYAN)
        elif kind == "credits":
            p.credits += item.amount
            self.log(f"You pick up {item.amount} Mars Credits.", YELLOW)
        elif kind in ("weapon", "armor"):
            stat = "attack" if kind == "weapon" else "defense"
            slot = "weapon" if kind == "weapon" else "armor"
            current = getattr(p, slot)
            current_value = ITEM_TYPES[current][stat] if current else 0
            if t[stat] > current_value:
                setattr(p, slot, item.key)
                self.log(f"You equip the {item.name}! (+{t[stat]} {stat})", CYAN)
            else:
                p.credits += 5
                self.log(f"You sell the spare {item.name} for 5 credits.", YELLOW)

    def descend(self):
        self.floor += 1
        self.turn += 1
        p = self.player
        p.hp = min(p.max_hp, p.hp + 5)
        self.log(f"You ride the delivery hatch down to floor {self.floor}: "
                 f"{FLOOR_NAMES.get(self.floor, '')}.", ORANGE)
        self.new_floor()

    # --------------------------------------------------------------- combat
    def attack(self, attacker, defender):
        damage = max(1, attacker.attack - defender.defense + self.rng.randint(-1, 1))
        defender.hp -= damage
        if attacker is self.player:
            self.log(f"You hit the {defender.name} for {damage}.", WHITE)
        else:
            self.log(f"The {attacker.name} hits you for {damage}.", RED)
        if defender.hp <= 0:
            if defender is self.player:
                self.state = "dead"
                self.killer = attacker.name
                self.log(f"You were defeated by the {attacker.name}...", RED)
            else:
                self.monster_dies(defender)

    def monster_dies(self, m):
        self.monsters.remove(m)
        self.player.kills += 1
        self.log(f"The {m.name} {DEATH_TEXT[m.kind]}!", GREEN)
        amount = self.rng.randint(*m.credits)
        if amount > 0:
            self.items.append(Item("credits", m.x, m.y, amount))
        if m.kind == "calzone":
            self.state = "won"
            self.log("You saved Pizza Station Ares! The ovens are yours again.", YELLOW)

    # ------------------------------------------------------------ monster AI
    def end_turn(self):
        self.turn += 1
        p = self.player
        if self.turn % REGEN_EVERY == 0 and p.hp < p.max_hp:
            p.hp += 1   # the chef slowly catches their breath
        if self.state == "playing":
            self.update_fov()
            self.monsters_act()
        self.update_fov()

    def monsters_act(self):
        for m in list(self.monsters):
            if self.state != "playing":
                break
            if m not in self.monsters:
                continue
            if m.kind == "calzone":
                self.boss_special(m)
            for _ in range(m.speed):
                if self.monster_step(m):
                    break   # it attacked, so its turn is over

    def monster_step(self, m):
        """Move or attack once. Returns True if the monster attacked."""
        p = self.player
        if (m.x, m.y) in self.dungeon.visible:
            m.alerted = True
        if max(abs(m.x - p.x), abs(m.y - p.y)) == 1:
            self.attack(m, p)
            return True
        if m.ai == "wander":
            # meatballs are clumsy: they only sometimes chase you
            if m.alerted and self.rng.random() < 0.6:
                self.step_towards(m, p.x, p.y)
            else:
                self.random_step(m)
        elif m.alerted:
            self.step_towards(m, p.x, p.y)
        elif self.rng.random() < 0.3:
            self.random_step(m)
        return False

    def boss_special(self, m):
        """The Giant Calzone spits out meatballs every few turns."""
        if not m.alerted:
            return
        m.timer += 1
        minions = sum(1 for o in self.monsters if o.summoned)
        if m.timer % 6 == 0 and minions < 3:
            spots = [(m.x + dx, m.y + dy) for dx, dy in DIRECTIONS if self.is_free(m.x + dx, m.y + dy)]
            if spots:
                x, y = self.rng.choice(spots)
                self.monsters.append(Monster(x, y, "meatball", self.floor - 1, summoned=True))
                self.log("The Giant Calzone spits out a Mutant Meatball!", ORANGE)

    def random_step(self, m):
        dx, dy = self.rng.choice(DIRECTIONS)
        if self.is_free(m.x + dx, m.y + dy):
            m.x += dx
            m.y += dy

    def step_towards(self, m, tx, ty):
        path = self.find_path((m.x, m.y), (tx, ty))
        if path:
            nx, ny = path[0]
        else:   # no path found: just try to walk in the right direction
            nx = m.x + (tx > m.x) - (tx < m.x)
            ny = m.y + (ty > m.y) - (ty < m.y)
        if self.is_free(nx, ny):
            m.x, m.y = nx, ny

    def find_path(self, start, goal, limit=20):
        """Breadth-first search. Returns the list of steps from start to goal."""
        occupied = {(o.x, o.y) for o in self.monsters}
        came_from = {start: None}
        depth = {start: 0}
        frontier = deque([start])
        while frontier:
            cur = frontier.popleft()
            if cur == goal:
                break
            if depth[cur] >= limit:
                continue
            for dx, dy in DIRECTIONS:
                nxt = (cur[0] + dx, cur[1] + dy)
                if nxt in came_from or not self.dungeon.is_walkable(*nxt):
                    continue
                if nxt in occupied and nxt != goal:
                    continue
                came_from[nxt] = cur
                depth[nxt] = depth[cur] + 1
                frontier.append(nxt)
        if goal not in came_from:
            return None
        path = []
        cur = goal
        while cur != start:
            path.append(cur)
            cur = came_from[cur]
        path.reverse()
        return path
