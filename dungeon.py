"""Isaac-style room-by-room floor generation with themed furniture & decorations.

Every floor is a grid of single-screen rooms connected by N/S/E/W doors:
- Start room at (0, 0): safe kitchen with ovens, prep tables, and windows.
- Normal rooms: pizzeria rooms with big dining tables, kitchen counters, cryo
  freezers, or cargo crates in symmetric layouts.
- Treasure room: a supply room with a guaranteed upgrade item on a pedestal.
- Boss room: the room farthest from (0, 0). Clearing it opens the delivery hatch
  (or, on floor 5, defeats the Giant Calzone and wins the game!).
"""

import math
from settings import ROOM_W, ROOM_H, DOOR_X, DOOR_Y, CELL

WALL = "#"
FLOOR = "."
OBSTACLE = "O"
DOOR = "D"
HATCH = ">"

ROOM_STYLES = ["kitchen", "dining", "freezer", "storage", "dust"]

# Grid offsets and opposite directions for doors
DIR_OFFSET = {
    "N": (0, -1),
    "S": (0, 1),
    "W": (-1, 0),
    "E": (1, 0),
}
OPPOSITE_DIR = {"N": "S", "S": "N", "W": "E", "E": "W"}

# Tile coordinates of the 4 possible doors in a room
DOOR_TILES = {
    "N": (DOOR_X, 0),
    "S": (DOOR_X, ROOM_H - 1),
    "W": (0, DOOR_Y),
    "E": (ROOM_W - 1, DOOR_Y),
}

# Furniture sprite names for each room style: (left_half, right_half, single_tile)
STYLE_FURNITURE = {
    "dining":  ("table_left",   "table_right",   "table_single"),
    "kitchen": ("counter_left", "counter_right", "oven_block"),
    "freezer": ("freezer_left", "freezer_right", "ice_block"),
    "storage": ("crate_left",   "crate_right",   "crate_single"),
    "dust":    ("hydro_left",   "hydro_right",   "rock_single"),
}


class Room:
    """One full-screen room on a floor."""

    def __init__(self, gx, gy, style="kitchen", role="normal"):
        self.gx = gx
        self.gy = gy
        self.style = style
        self.role = role          # "start", "normal", "treasure", "boss"
        self.doors = {}           # dir ("N","S","E","W") -> (nx, ny)
        self.tiles = [[FLOOR] * ROOM_W for _ in range(ROOM_H)]
        self.furniture = [[None] * ROOM_W for _ in range(ROOM_H)]
        self.wall_decor = []      # list of (tx, ty, kind) on the top wall
        self.floor_decor = []     # list of (tx, ty, kind) walkable floor details
        self.monsters = []
        self.items = []
        self.visited = False
        self.cleared = role in ("start", "treasure")
        self.locked = False
        self.hatch_spawned = False
        self._build_walls()

    def _build_walls(self):
        for x in range(ROOM_W):
            self.tiles[0][x] = WALL
            self.tiles[ROOM_H - 1][x] = WALL
        for y in range(ROOM_H):
            self.tiles[y][0] = WALL
            self.tiles[y][ROOM_W - 1] = WALL

    def apply_doors(self):
        """Cut DOOR tiles into the outer walls for each connected neighbor."""
        self._build_walls()
        for d in self.doors:
            tx, ty = DOOR_TILES[d]
            self.tiles[ty][tx] = DOOR

    def _place_pair(self, tx, ty, left_key, right_key):
        """Place a 2-tile wide piece of furniture (like a big table or counter)."""
        if tx in (DOOR_X, DOOR_X - 1) or ty == DOOR_Y:
            return
        if 1 <= tx < ROOM_W - 2 and 1 <= ty < ROOM_H - 1:
            self.tiles[ty][tx] = OBSTACLE
            self.tiles[ty][tx + 1] = OBSTACLE
            self.furniture[ty][tx] = left_key
            self.furniture[ty][tx + 1] = right_key

    def _place_single(self, tx, ty, key):
        """Place a 1-tile piece of furniture."""
        if tx == DOOR_X or ty == DOOR_Y:
            return
        if 1 <= tx < ROOM_W - 1 and 1 <= ty < ROOM_H - 1:
            self.tiles[ty][tx] = OBSTACLE
            self.furniture[ty][tx] = key

    def add_obstacles(self, rng):
        """Populate the room with themed tables, counters, ovens, and floor/wall decor."""
        left_k, right_k, single_k = STYLE_FURNITURE.get(
            self.style, STYLE_FURNITURE["kitchen"]
        )

        if self.role == "start":
            # Starting kitchen: corner prep counters and ovens, open center
            self._place_pair(2, 2, "counter_left", "counter_right")
            self._place_pair(ROOM_W - 4, 2, "counter_left", "counter_right")
            self._place_single(2, ROOM_H - 3, "oven_block")
            self._place_single(ROOM_W - 3, ROOM_H - 3, "oven_block")
        elif self.role == "treasure":
            # Supply room: corner cargo tables framing the upgrade pedestal
            self._place_pair(3, 3, "crate_left", "crate_right")
            self._place_pair(ROOM_W - 5, 3, "crate_left", "crate_right")
            self._place_pair(3, ROOM_H - 4, "crate_left", "crate_right")
            self._place_pair(ROOM_W - 5, ROOM_H - 4, "crate_left", "crate_right")
        elif self.role == "boss":
            # Boss room: 4 corner ovens/pillars leaving a wide arena in the middle
            for ox, oy in ((2, 2), (ROOM_W - 3, 2), (2, ROOM_H - 3), (ROOM_W - 3, ROOM_H - 3)):
                self._place_single(ox, oy, "oven_block")
        else:
            # Normal rooms: always pick a rich symmetric furniture layout
            pattern = rng.choice(["banquet_hall", "double_row", "center_islands", "corner_booths"])
            if pattern == "banquet_hall":
                # 4 big 2-tile tables/counters + 2 side stations
                for ox, oy in ((4, 3), (ROOM_W - 6, 3), (4, ROOM_H - 4), (ROOM_W - 6, ROOM_H - 4)):
                    self._place_pair(ox, oy, left_k, right_k)
                self._place_single(2, 2, single_k)
                self._place_single(ROOM_W - 3, 2, single_k)
                self._place_single(2, ROOM_H - 3, single_k)
                self._place_single(ROOM_W - 3, ROOM_H - 3, single_k)
            elif pattern == "double_row":
                # 6 big tables/counters like a busy restaurant / kitchen hall
                for ox in (2, 6, ROOM_W - 8, ROOM_W - 4):
                    if ox in (2, ROOM_W - 4):
                        self._place_pair(ox, 2, left_k, right_k)
                        self._place_pair(ox, ROOM_H - 3, left_k, right_k)
                    else:
                        self._place_pair(ox, 3, left_k, right_k)
                        self._place_pair(ox, ROOM_H - 4, left_k, right_k)
            elif pattern == "center_islands":
                # 4 central prep islands/tables + 4 corner blocks
                for ox, oy in ((5, 4), (ROOM_W - 7, 4), (5, ROOM_H - 5), (ROOM_W - 7, ROOM_H - 5)):
                    self._place_pair(ox, oy, left_k, right_k)
                for ox, oy in ((2, 2), (ROOM_W - 3, 2), (2, ROOM_H - 3), (ROOM_W - 3, ROOM_H - 3)):
                    self._place_single(ox, oy, single_k)
            elif pattern == "corner_booths":
                # Corner tables + mid-room accent blocks
                for ox, oy in ((3, 2), (ROOM_W - 5, 2), (3, ROOM_H - 3), (ROOM_W - 5, ROOM_H - 3)):
                    self._place_pair(ox, oy, left_k, right_k)
                for ox, oy in ((6, 4), (ROOM_W - 7, 4), (6, ROOM_H - 5), (ROOM_W - 7, ROOM_H - 5)):
                    self._place_single(ox, oy, single_k)

        self._add_decorations(rng)

    def _add_decorations(self, rng):
        """Add wall windows, ovens, neon signs, chairs, and floor details."""
        # 1. Top wall fixtures (at x = 3, 6, 12, 15 so they never overlap the North door at 9)
        wall_slots = [3, 6, 12, 15]
        for tx in wall_slots:
            if self.tiles[0][tx] != WALL:
                continue
            if self.style == "kitchen" or self.role == "boss":
                kind = "wall_oven" if tx in (3, 15) else "wall_rack"
            elif self.style == "dining":
                kind = "wall_window" if tx in (3, 15) else "wall_neon"
            elif self.style == "freezer":
                kind = "wall_vent"
            else:
                kind = "wall_window" if tx in (6, 12) else "wall_vent"
            self.wall_decor.append((tx, 0, kind))

        # 2. Walkable floor decorations (rugs, chairs above/below dining tables, sauce/boxes)
        if self.role in ("start", "treasure"):
            self.floor_decor.append((DOOR_X, DOOR_Y, "floor_mat"))

        # Add dining stools/chairs above & below dining tables where floor is walkable
        if self.style == "dining":
            for ty in range(1, ROOM_H - 1):
                for tx in range(1, ROOM_W - 1):
                    if self.furniture[ty][tx] in ("table_left", "table_right"):
                        if self.tiles[ty - 1][tx] == FLOOR:
                            self.floor_decor.append((tx, ty - 1, "stool_top"))
                        if self.tiles[ty + 1][tx] == FLOOR:
                            self.floor_decor.append((tx, ty + 1, "stool_bottom"))

        # Scatter 4..6 subtle floor props (grates, pizza boxes, sauce spots) on empty floor tiles
        prop_choices = {
            "kitchen": ["floor_grate", "sauce_spot", "flour_spot"],
            "dining":  ["pizza_box", "sauce_spot", "floor_grate"],
            "freezer": ["ice_patch", "floor_grate"],
            "storage": ["pizza_box", "flour_spot", "floor_grate"],
            "dust":    ["mars_pebbles", "sauce_spot"],
        }.get(self.style, ["floor_grate", "pizza_box"])

        for _ in range(5):
            tx = rng.randint(2, ROOM_W - 3)
            ty = rng.randint(2, ROOM_H - 3)
            if (tx, ty) == (DOOR_X, DOOR_Y):
                continue
            if self.tiles[ty][tx] == FLOOR and not any(x == tx and y == ty for x, y, _ in self.floor_decor):
                self.floor_decor.append((tx, ty, rng.choice(prop_choices)))

    def spawn_hatch(self):
        """Open the delivery hatch in the center of the room."""
        self.tiles[DOOR_Y][DOOR_X] = HATCH
        self.hatch_spawned = True

    def in_bounds(self, tx, ty):
        return 0 <= tx < ROOM_W and 0 <= ty < ROOM_H

    def is_walkable(self, tx, ty, allow_doors=False):
        if not self.in_bounds(tx, ty):
            return False
        t = self.tiles[ty][tx]
        if t in (FLOOR, HATCH):
            return True
        if t == DOOR and allow_doors and not self.locked:
            return True
        return False

    def is_solid_for_entity(self, tx, ty, is_player=False):
        """Return True if tile (tx, ty) blocks movement."""
        if not self.in_bounds(tx, ty):
            return True
        t = self.tiles[ty][tx]
        if t in (WALL, OBSTACLE):
            return True
        if t == DOOR:
            return True if (not is_player or self.locked) else False
        return False

    def is_solid_for_shot(self, tx, ty):
        """Shots stop on walls, doors, and obstacles."""
        if not self.in_bounds(tx, ty):
            return True
        return self.tiles[ty][tx] in (WALL, OBSTACLE, DOOR)

    def circle_collides(self, px, py, radius, is_player=False):
        """True if a circle at pixel (px, py) overlaps any blocking tile."""
        min_tx = int((px - radius) // CELL)
        max_tx = int((px + radius) // CELL)
        min_ty = int((py - radius) // CELL)
        max_ty = int((py + radius) // CELL)
        for ty in range(min_ty, max_ty + 1):
            for tx in range(min_tx, max_tx + 1):
                if self.is_solid_for_entity(tx, ty, is_player=is_player):
                    rx0, ry0 = tx * CELL, ty * CELL
                    rx1, ry1 = rx0 + CELL, ry0 + CELL
                    cx = max(rx0, min(px, rx1))
                    cy = max(ry0, min(py, ry1))
                    if math.hypot(px - cx, py - cy) < radius:
                        return True
        return False

    def door_at_pixel(self, px, py):
        """If pixel (px, py) reaches an unlocked doorway, return its direction."""
        if self.locked:
            return None
        for d, (dx, dy) in DOOR_TILES.items():
            if d not in self.doors:
                continue
            dcx = (dx + 0.5) * CELL
            dcy = (dy + 0.5) * CELL
            if math.hypot(px - dcx, py - dcy) <= CELL * 0.78:
                return d
        return None

    def random_free_pixel(self, rng, avoid_center=False, margin_tiles=2):
        """Pick a walkable floor tile away from the doors and return its center pixel."""
        for _ in range(80):
            tx = rng.randint(margin_tiles, ROOM_W - 1 - margin_tiles)
            ty = rng.randint(margin_tiles, ROOM_H - 1 - margin_tiles)
            if self.tiles[ty][tx] != FLOOR:
                continue
            if avoid_center and abs(tx - DOOR_X) <= 2 and abs(ty - DOOR_Y) <= 2:
                continue
            return (tx + 0.5) * CELL, (ty + 0.5) * CELL
        # Fallback: find any FLOOR tile in the room
        for ty in range(2, ROOM_H - 2):
            for tx in range(2, ROOM_W - 2):
                if self.tiles[ty][tx] == FLOOR:
                    return (tx + 0.5) * CELL, (ty + 0.5) * CELL
        return (DOOR_X + 0.5) * CELL, (DOOR_Y + 0.5) * CELL


class Dungeon:
    """A floor made of connected single-screen rooms (like The Binding of Isaac)."""

    def __init__(self, rng, num_rooms=8):
        self.rng = rng
        self.rooms = {}           # (gx, gy) -> Room
        self.start_pos = (0, 0)
        self.boss_pos = (0, 0)
        self.treasure_pos = None
        self.generate(num_rooms=num_rooms)

    def generate(self, num_rooms=8):
        self.rooms = {(0, 0): Room(0, 0, style="kitchen", role="start")}
        frontier = [(0, 0)]

        attempts = 0
        while len(self.rooms) < num_rooms and attempts < 200:
            attempts += 1
            base = self.rng.choice(frontier)
            d = self.rng.choice(["N", "S", "E", "W"])
            dx, dy = DIR_OFFSET[d]
            cand = (base[0] + dx, base[1] + dy)
            if cand in self.rooms:
                continue
            neighbors = sum(
                1 for ox, oy in DIR_OFFSET.values()
                if (cand[0] + ox, cand[1] + oy) in self.rooms
            )
            if neighbors > 1 and self.rng.random() < 0.7:
                continue
            style = self.rng.choice(ROOM_STYLES)
            self.rooms[cand] = Room(cand[0], cand[1], style=style, role="normal")
            frontier.append(cand)

        # Connect adjacent rooms with doors
        for (gx, gy), room in self.rooms.items():
            for d, (dx, dy) in DIR_OFFSET.items():
                nb = (gx + dx, gy + dy)
                if nb in self.rooms:
                    room.doors[d] = nb
            room.apply_doors()

        # Pick the Boss Room: farthest room from (0, 0), preferring dead-ends
        candidates = [pos for pos in self.rooms if pos != (0, 0)]
        dead_ends = [pos for pos in candidates if len(self.rooms[pos].doors) == 1]
        pool = dead_ends if dead_ends else candidates
        self.boss_pos = max(pool, key=lambda p: abs(p[0]) + abs(p[1]))
        boss_room = self.rooms[self.boss_pos]
        boss_room.role = "boss"
        boss_room.style = "kitchen"
        boss_room.cleared = False

        # Pick a Treasure Room: another room (preferably dead-end) not start or boss
        other_dead_ends = [p for p in dead_ends if p != self.boss_pos]
        other_rooms = [p for p in candidates if p != self.boss_pos]
        t_pool = other_dead_ends if other_dead_ends else other_rooms
        if t_pool:
            self.treasure_pos = self.rng.choice(t_pool)
            t_room = self.rooms[self.treasure_pos]
            t_room.role = "treasure"
            t_room.style = "storage"
            t_room.cleared = True

        # Add furniture & decorations to all rooms
        for room in self.rooms.values():
            room.add_obstacles(self.rng)
