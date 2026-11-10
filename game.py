"""Real-time Isaac-style game rules for Pizza Station Ares.

There is no pygame drawing code in this file. That keeps the rules easy to
read and lets us test the game automatically (see tests/test_game.py).
"""

import math
import random

from settings import (
    CELL, ROOM_W, ROOM_H, DOOR_X, DOOR_Y,
    FINAL_FLOOR, SHOT_SPEED, IFRAME_TIME, PIZZA_HEAL,
)
from dungeon import Dungeon, HATCH, OPPOSITE_DIR, DOOR_TILES
from entities import Player, Monster, Projectile, DEATH_TEXT
from items import Item, ITEM_TYPES

# Message colours (R, G, B)
WHITE = (230, 230, 230)
RED = (235, 90, 80)
GREEN = (120, 220, 120)
YELLOW = (250, 210, 90)
ORANGE = (240, 150, 60)
CYAN = (110, 210, 240)

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
        self.time = 0.0             # elapsed seconds played
        self.rooms_cleared = 0
        self.killer = None
        self.player = Player(0, 0)
        self.projectiles = []       # active shots in the current room
        self.particles = []         # small visual hit/sauce splashes: [x, y, vx, vy, col, life]
        self.door_cooldown = 0.0
        self.hatch_cooldown = 0.0
        self.current_pos = (0, 0)
        self.new_floor()
        self.log("Welcome to Pizza Station Ares, chef!", ORANGE)
        self.log("Move with WASD, aim with the mouse, and shoot with Left Click!", WHITE)

    # ------------------------------------------------------------------ utils
    @property
    def room(self):
        return self.dungeon.rooms[self.current_pos]

    @property
    def monsters(self):
        return self.room.monsters

    @property
    def items(self):
        return self.room.items

    @property
    def boss(self):
        for m in self.room.monsters:
            if m.kind == "calzone" or m.mini_boss:
                return m
        return None

    @property
    def score(self):
        p = self.player
        return (
            p.credits
            + p.kills * 10
            + self.rooms_cleared * 15
            + (self.floor - 1) * 50
            + (500 if self.state == "won" else 0)
        )

    def log(self, text, colour=WHITE):
        self.messages.append((text, colour))
        self.messages = self.messages[-60:]

    # ------------------------------------------------------------ floor setup
    def new_floor(self):
        num_rooms = 6 + self.floor
        self.dungeon = Dungeon(self.rng, num_rooms=num_rooms)
        self.projectiles.clear()
        self.particles.clear()
        self.populate_floor()
        self.enter_room((0, 0), from_dir=None)

    def pick_monster_type(self):
        weights = {
            "meatball": 6,
            "drone": 2 + self.floor,
            "anchovy": max(1, 2 * self.floor - 1),
        }
        return self.rng.choices(list(weights), weights=list(weights.values()))[0]

    def pick_item_type(self):
        f = self.floor
        weights = {
            "pizza": 38,
            "credits": 30,
            "oxygen": 10,
            "apron": 5,
            "rolling_pin": 6 if f <= 2 else 0,
            "cutter": 5 if f >= 2 else 0,
        }
        return self.rng.choices(list(weights), weights=list(weights.values()))[0]

    def populate_floor(self):
        cx = (DOOR_X + 0.5) * CELL
        cy = (DOOR_Y + 0.5) * CELL

        for pos, room in self.dungeon.rooms.items():
            if room.role == "start":
                continue

            if room.role == "treasure":
                # Guaranteed upgrade in the treasure room
                if self.floor == 1:
                    key = "rolling_pin"
                elif self.floor == 3:
                    key = "cutter"
                else:
                    key = self.rng.choice(["oxygen", "apron", "pizza", "cutter"])
                room.items.append(Item(key, cx, cy))
                continue

            if room.role == "boss":
                if self.floor == FINAL_FLOOR:
                    room.monsters.append(Monster(cx, cy, "calzone"))
                else:
                    kind = "anchovy" if self.floor >= 2 else "drone"
                    room.monsters.append(Monster(cx, cy, kind, self.floor - 1, mini_boss=True))
                    # Add a helper meatball on deeper floors
                    if self.floor >= 3:
                        hx, hy = room.random_free_pixel(self.rng, avoid_center=True, margin_tiles=3)
                        room.monsters.append(Monster(hx, hy, "meatball", self.floor - 1))
                continue

            # Normal room: spawn 2..4 monsters away from doors
            count = self.rng.randint(2, min(4, 1 + self.floor))
            for _ in range(count):
                mx, my = room.random_free_pixel(self.rng, avoid_center=False, margin_tiles=3)
                room.monsters.append(Monster(mx, my, self.pick_monster_type(), self.floor - 1))

            if self.rng.random() < 0.55:
                ix, iy = room.random_free_pixel(self.rng, avoid_center=False, margin_tiles=2)
                key = self.pick_item_type()
                amount = self.rng.randint(2, 5) + self.floor if key == "credits" else 1
                room.items.append(Item(key, ix, iy, amount))

    def enter_room(self, pos, from_dir=None):
        """Move the player into room `pos`. Locks doors if enemies are inside."""
        self.current_pos = pos
        room = self.room
        room.visited = True
        self.projectiles.clear()
        self.particles.clear()
        self.door_cooldown = 0.35

        # Spawn player near the doorway they entered from (or room center on start)
        if from_dir is None:
            self.player.x = (DOOR_X + 0.5) * CELL
            self.player.y = (DOOR_Y + 0.5) * CELL
        else:
            entry_door = OPPOSITE_DIR[from_dir]
            dtx, dty = DOOR_TILES[entry_door]
            # Step 1.3 tiles inside the room from the doorway
            if entry_door == "N":
                self.player.x = (dtx + 0.5) * CELL
                self.player.y = (dty + 1.45) * CELL
            elif entry_door == "S":
                self.player.x = (dtx + 0.5) * CELL
                self.player.y = (dty - 0.45) * CELL
            elif entry_door == "W":
                self.player.x = (dtx + 1.45) * CELL
                self.player.y = (dty + 0.5) * CELL
            elif entry_door == "E":
                self.player.x = (dtx - 0.45) * CELL
                self.player.y = (dty + 0.5) * CELL

        if room.monsters:
            room.locked = True
            room.cleared = False
            # Brief grace period when entering a room with monsters
            self.player.iframe_timer = max(self.player.iframe_timer, 0.45)
            if room.role == "boss":
                if self.floor == FINAL_FLOOR:
                    self.log("BOSS ROOM: The Giant Calzone blocks your way!", YELLOW)
                else:
                    self.log(f"Floor Guardian: Defeat {room.monsters[0].name} to open the hatch!", ORANGE)
            else:
                self.log("Doors locked! Defeat all enemies in the room.", ORANGE)
        else:
            room.locked = False
            room.cleared = True
            if room.role == "treasure" and room.items:
                self.log("Supply Room! Pick up your upgrade.", CYAN)

    # --------------------------------------------------------- real-time loop
    def update(self, dt, move_dx=0.0, move_dy=0.0, aim_target=None, shooting=False):
        """Advance the real-time simulation by `dt` seconds."""
        if self.state != "playing":
            return
        self.time += dt
        p = self.player

        # Timers
        if p.fire_timer > 0:
            p.fire_timer = max(0.0, p.fire_timer - dt)
        if p.iframe_timer > 0:
            p.iframe_timer = max(0.0, p.iframe_timer - dt)
        if p.hit_flash > 0:
            p.hit_flash = max(0.0, p.hit_flash - dt)
        if self.door_cooldown > 0:
            self.door_cooldown = max(0.0, self.door_cooldown - dt)
        if self.hatch_cooldown > 0:
            self.hatch_cooldown = max(0.0, self.hatch_cooldown - dt)

        # Aim toward mouse target
        if aim_target is not None:
            ax, ay = aim_target
            if ax != p.x or ay != p.y:
                p.aim_angle = math.atan2(ay - p.y, ax - p.x)

        # Move player smoothly with wall sliding
        if move_dx != 0.0 or move_dy != 0.0:
            length = math.hypot(move_dx, move_dy)
            vx = (move_dx / length) * p.speed
            vy = (move_dy / length) * p.speed
            self.move_entity(p, vx * dt, vy * dt, is_player=True)

        # Shoot toward mouse target when LMB is held/clicked
        if shooting and p.fire_timer <= 0.0:
            self.player_shoot(aim_target)

        # Pickups, doors, and floor hatch
        self.pickup_items()
        if self.check_doors():
            return
        if self.check_hatch():
            return

        # Update projectiles, monsters, particles, and room lock state
        self.update_projectiles(dt)
        self.update_monsters(dt)
        self.update_particles(dt)
        self.check_room_clear()

    def move_entity(self, ent, dx, dy, is_player=False):
        """Move `ent` by (dx, dy) in pixels, sliding along walls and obstacles."""
        room = self.room
        moved_x = False
        moved_y = False
        if dx != 0.0:
            nx = ent.x + dx
            if not room.circle_collides(nx, ent.y, ent.radius, is_player=is_player):
                ent.x = nx
                moved_x = True
        if dy != 0.0:
            ny = ent.y + dy
            if not room.circle_collides(ent.x, ny, ent.radius, is_player=is_player):
                ent.y = ny
                moved_y = True
        # If a monster is blocked by a table/counter on one axis, slide along the other axis
        if not is_player:
            step = math.hypot(dx, dy)
            if dx != 0.0 and not moved_x:
                slide_y = step if dy >= 0 else -step
                if not room.circle_collides(ent.x, ent.y + slide_y, ent.radius):
                    ent.y += slide_y
                elif not room.circle_collides(ent.x, ent.y - slide_y, ent.radius):
                    ent.y -= slide_y
            if dy != 0.0 and not moved_y:
                slide_x = step if dx >= 0 else -step
                if not room.circle_collides(ent.x + slide_x, ent.y, ent.radius):
                    ent.x += slide_x
                elif not room.circle_collides(ent.x - slide_x, ent.y, ent.radius):
                    ent.x -= slide_x

    # -------------------------------------------------------- player actions
    def player_shoot(self, aim_target=None):
        """Fire a projectile from the chef toward `aim_target` (or `player.aim_angle`)."""
        if self.state != "playing":
            return False
        p = self.player
        if aim_target is not None:
            ax, ay = aim_target
            if ax != p.x or ay != p.y:
                p.aim_angle = math.atan2(ay - p.y, ax - p.x)

        angle = p.aim_angle
        vx = math.cos(angle) * SHOT_SPEED
        vy = math.sin(angle) * SHOT_SPEED
        sx = p.x + math.cos(angle) * 16.0
        sy = p.y + math.sin(angle) * 16.0
        radius = 8.0 if p.shot_kind == "cutter" else 6.0
        proj = Projectile(
            sx, sy, vx, vy,
            damage=p.attack,
            from_player=True,
            kind=p.shot_kind,
            radius=radius,
            owner_name="Chef",
        )
        self.projectiles.append(proj)
        p.fire_timer = p.fire_cooldown
        return True

    def eat_pizza(self):
        if self.state != "playing":
            return False
        p = self.player
        if p.pizzas <= 0:
            self.log("You have no pizza slices left!", RED)
            return False
        if p.hp >= p.max_hp:
            self.log("You are already at full health.", WHITE)
            return False
        p.pizzas -= 1
        healed = min(PIZZA_HEAL, p.max_hp - p.hp)
        p.hp += healed
        self.log(f"You eat a hot pizza slice! (+{healed} HP)", GREEN)
        return True

    def pickup_items(self):
        p = self.player
        for item in list(self.room.items):
            if math.hypot(item.x - p.x, item.y - p.y) <= p.radius + 16.0:
                self.room.items.remove(item)
                self.apply_item(item)

    def apply_item(self, item):
        p = self.player
        t = ITEM_TYPES[item.key]
        kind = t["kind"]
        if kind == "consumable":
            p.pizzas += 1
            self.log("Picked up a Pizza Slice! (Press H or Right-Click to eat)", GREEN)
        elif kind == "maxhp":
            p.max_hp += t["amount"]
            p.hp = min(p.max_hp, p.hp + t["amount"])
            self.log(f"Oxygen Tank! Max HP +{t['amount']}.", CYAN)
        elif kind == "credits":
            p.credits += item.amount
            self.log(f"Picked up {item.amount} Mars Credits.", YELLOW)
        elif kind in ("weapon", "armor"):
            stat = "attack" if kind == "weapon" else "defense"
            slot = "weapon" if kind == "weapon" else "armor"
            current = getattr(p, slot)
            current_value = ITEM_TYPES[current][stat] if current else 0
            if t[stat] > current_value:
                setattr(p, slot, item.key)
                self.log(f"Equipped {item.name}! (+{t[stat]} {stat})", CYAN)
            else:
                p.credits += 5
                self.log(f"Sold spare {item.name} for 5 credits.", YELLOW)

    def check_doors(self):
        """Transition into the neighboring room if the player walks into an open door."""
        if self.door_cooldown > 0.0 or self.room.locked:
            return False
        d = self.room.door_at_pixel(self.player.x, self.player.y)
        if d and d in self.room.doors:
            target_pos = self.room.doors[d]
            self.enter_room(target_pos, from_dir=d)
            return True
        return False

    def check_hatch(self):
        """Descend to the next floor if the player steps onto the open delivery hatch."""
        if self.hatch_cooldown > 0.0 or self.room.locked:
            return False
        tx = int(self.player.x // CELL)
        ty = int(self.player.y // CELL)
        if self.room.in_bounds(tx, ty) and self.room.tiles[ty][tx] == HATCH:
            self.descend()
            return True
        return False

    def descend(self):
        self.floor += 1
        self.hatch_cooldown = 0.6
        p = self.player
        p.hp = min(p.max_hp, p.hp + 5)
        self.log(
            f"You ride the delivery hatch down to Floor {self.floor}: "
            f"{FLOOR_NAMES.get(self.floor, '')}!",
            ORANGE,
        )
        self.new_floor()

    # ----------------------------------------------------- combat & projectiles
    def spawn_splash(self, x, y, colour, count=6):
        for _ in range(count):
            ang = self.rng.uniform(0, math.tau)
            spd = self.rng.uniform(35, 110)
            self.particles.append([x, y, math.cos(ang) * spd, math.sin(ang) * spd, colour, 0.28])

    def update_particles(self, dt):
        kept = []
        for pt in self.particles:
            pt[0] += pt[2] * dt
            pt[1] += pt[3] * dt
            pt[5] -= dt
            if pt[5] > 0:
                kept.append(pt)
        self.particles = kept

    def update_projectiles(self, dt):
        room = self.room
        p = self.player
        for proj in list(self.projectiles):
            proj.x += proj.vx * dt
            proj.y += proj.vy * dt
            proj.age += dt
            if proj.age >= proj.lifetime:
                self.projectiles.remove(proj)
                continue

            tx, ty = int(proj.x // CELL), int(proj.y // CELL)
            if room.is_solid_for_shot(tx, ty):
                self.spawn_splash(proj.x, proj.y, (230, 190, 110), count=4)
                self.projectiles.remove(proj)
                continue

            if proj.from_player:
                hit_monster = None
                for m in room.monsters:
                    if math.hypot(proj.x - m.x, proj.y - m.y) <= proj.radius + m.radius:
                        hit_monster = m
                        break
                if hit_monster is not None:
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    self.damage_monster(hit_monster, proj.damage, proj.vx, proj.vy)
            else:
                if math.hypot(proj.x - p.x, proj.y - p.y) <= proj.radius + p.radius:
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    self.damage_player(proj.damage, proj.owner_name or "Enemy shot")

    def damage_monster(self, m, raw_damage, knock_vx=0.0, knock_vy=0.0):
        damage = max(1, raw_damage - m.defense)
        m.hp -= damage
        m.hit_flash = 0.12
        self.spawn_splash(m.x, m.y, (215, 55, 45), count=6)
        # Gentle knockback
        k_len = math.hypot(knock_vx, knock_vy)
        if k_len > 0 and m.kind != "calzone":
            self.move_entity(m, (knock_vx / k_len) * 8.0, (knock_vy / k_len) * 8.0)
        if m.hp <= 0 and m in self.room.monsters:
            self.monster_dies(m)

    def damage_player(self, raw_damage, attacker_name):
        p = self.player
        if p.iframe_timer > 0.0 or self.state != "playing":
            return False
        damage = max(1, raw_damage - p.defense)
        p.hp -= damage
        p.iframe_timer = IFRAME_TIME
        p.hit_flash = 0.2
        self.spawn_splash(p.x, p.y, (235, 80, 70), count=8)
        self.log(f"The {attacker_name} hits you for {damage}!", RED)
        if p.hp <= 0:
            p.hp = 0
            self.state = "dead"
            self.killer = attacker_name
            self.log(f"You were defeated by the {attacker_name}...", RED)
        return True

    def monster_dies(self, m):
        if m in self.room.monsters:
            self.room.monsters.remove(m)
        self.player.kills += 1
        self.spawn_splash(m.x, m.y, (240, 120, 50), count=12)
        self.log(f"The {m.name} {DEATH_TEXT[m.kind]}!", GREEN)
        amount = self.rng.randint(*m.credits)
        if amount > 0:
            self.room.items.append(Item("credits", m.x, m.y, amount))
        if m.kind == "calzone":
            self.state = "won"
            self.room.locked = False
            self.room.cleared = True
            self.log("You defeated the Giant Calzone and saved Pizza Station Ares!", YELLOW)

    def check_room_clear(self):
        room = self.room
        if room.locked and not room.monsters and self.state == "playing":
            room.locked = False
            room.cleared = True
            self.rooms_cleared += 1
            # Catch breath (+1 HP on room clear)
            if self.player.hp < self.player.max_hp:
                self.player.hp += 1
            self.log("Room cleared! The doors unlock.", GREEN)
            # Chance to spawn a slice of pizza as a room-clear reward
            if self.rng.random() < 0.35:
                rx = (DOOR_X + 0.5) * CELL
                ry = (DOOR_Y + 0.5) * CELL
                if not room. circle_collides(rx, ry, 12.0):
                    room.items.append(Item("pizza", rx, ry))
            if room.role == "boss" and self.floor < FINAL_FLOOR and not room.hatch_spawned:
                room.spawn_hatch()
                self.log("The delivery hatch opens! Step on it to go down.", YELLOW)

    # ------------------------------------------------------------ monster AI
    def update_monsters(self, dt):
        p = self.player
        monsters = list(self.room.monsters)
        for m in monsters:
            if self.state != "playing" or m not in self.room.monsters:
                continue
            if m.hit_flash > 0:
                m.hit_flash = max(0.0, m.hit_flash - dt)
            m.timer += dt
            m.shot_timer -= dt

            dx = p.x - m.x
            dy = p.y - m.y
            dist = math.hypot(dx, dy) or 1.0
            ux, uy = dx / dist, dy / dist

            if m.ai == "wander_chase":
                # Meatballs wobble and chase the player
                wobble = math.sin(m.timer * 3.5 + m.x * 0.05) * 0.65
                ang = math.atan2(dy, dx) + wobble
                vx = math.cos(ang) * m.speed
                vy = math.sin(ang) * m.speed
                self.move_entity(m, vx * dt, vy * dt)

            elif m.ai == "shooter":
                # Drones keep medium distance, bob/weave, and pause briefly to shoot
                if m.shot_timer < 0.35:
                    vx, vy = 0.0, 0.0
                elif dist < 140.0:
                    vx, vy = -ux * m.speed * 0.75, -uy * m.speed * 0.75
                elif dist > 230.0:
                    vx, vy = ux * m.speed * 0.85, uy * m.speed * 0.85
                else:
                    strafe_dir = 1.0 if math.sin(m.timer * 2.2) >= 0 else -1.0
                    vx, vy = -uy * m.speed * 0.55 * strafe_dir, ux * m.speed * 0.55 * strafe_dir
                self.move_entity(m, vx * dt, vy * dt)
                if m.shot_timer <= 0.0:
                    self.enemy_shoot(m, ux, uy, speed=250.0, kind="enemy")
                    m.shot_timer = 1.55 if m.mini_boss else 1.95

            elif m.ai == "lunge":
                # Anchovies stalk the player and periodically dash fast
                cycle = m.timer % 2.4
                mult = 1.65 if cycle > 1.85 else 0.88
                self.move_entity(m, ux * m.speed * mult * dt, uy * m.speed * mult * dt)

            elif m.ai == "boss":
                # Giant Calzone: stalks, fires 3-way molten cheese spreads, spawns meatballs
                self.move_entity(m, ux * m.speed * dt, uy * m.speed * dt)
                if m.shot_timer <= 0.0:
                    base_ang = math.atan2(dy, dx)
                    for offset in (-0.28, 0.0, 0.28):
                        ang = base_ang + offset
                        self.enemy_shoot(
                            m, math.cos(ang), math.sin(ang),
                            speed=250.0, kind="cheese", radius=8.0
                        )
                    m.shot_timer = 1.75
                # Summon a meatball every ~6.5 seconds if fewer than 2 summoned exist
                if m.timer >= 6.5:
                    m.timer = 0.0
                    minions = sum(1 for o in self.room.monsters if o.summoned)
                    if minions < 2:
                        sx, sy = self.room.random_free_pixel(self.rng, avoid_center=False, margin_tiles=3)
                        if math.hypot(sx - p.x, sy - p.y) > 90.0:
                            self.room.monsters.append(
                                Monster(sx, sy, "meatball", self.floor - 1, summoned=True)
                            )
                            self.log("The Giant Calzone spits out a Mutant Meatball!", ORANGE)

            # Contact damage when touching the chef
            if math.hypot(p.x - m.x, p.y - m.y) <= p.radius + m.radius - 2.0:
                self.damage_player(m.attack, m.name)

        # Gently push overlapping monsters apart so they don't stack
        for i in range(len(monsters)):
            for j in range(i + 1, len(monsters)):
                a, b = monsters[i], monsters[j]
                if a not in self.room.monsters or b not in self.room.monsters:
                    continue
                ox = b.x - a.x
                oy = b.y - a.y
                d = math.hypot(ox, oy)
                min_d = a.radius + b.radius
                if 0 < d < min_d:
                    push = (min_d - d) * 0.5
                    self.move_entity(a, -(ox / d) * push, -(oy / d) * push)
                    self.move_entity(b, (ox / d) * push, (oy / d) * push)

    def enemy_shoot(self, m, ux, uy, speed=250.0, kind="enemy", radius=6.0):
        sx = m.x + ux * (m.radius + 6.0)
        sy = m.y + uy * (m.radius + 6.0)
        self.projectiles.append(
            Projectile(
                sx, sy, ux * speed, uy * speed,
                damage=m.attack,
                from_player=False,
                kind=kind,
                radius=radius,
                owner_name=m.name,
            )
        )
