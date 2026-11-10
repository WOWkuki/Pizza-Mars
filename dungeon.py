"""Isaac-style room-by-room floor generation.

Every floor is a grid of single-screen rooms connected by N/S/E/W doors:
- Start room at (0, 0): safe kitchen where you spawn.
- Normal rooms: pizzeria rooms with enemies and symmetric obstacle layouts.
- Treasure room: a supply room with a guaranteed upgrade item.
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


class Room:
    """One full-screen room on a floor."""

    def __init__(self, gx, gy, style="kitchen", role="normal"):
        self.gx = gx
        self.gy = gy
        self.style = style
        self.role = role          # "start", "normal", "treasure", "boss"
        self.doors = {}           # dir ("N","S","E","W") -> (nx, ny)
        self.tiles = [[FLOOR] * ROOM_W for _ in range(ROOM_H)]
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

    def add_obstacles(self, rng):
        """Place symmetric Isaac-style obstacle blocks (tables/counters/crates)."""
        if self.role != "normal":
            return
        pattern = rng.choice(["none", "four_pillars", "corners", "center_bars", "twin_islands"])
        coords = []
        if pattern == "four_pillars":
            coords = [(5, 3), (ROOM_W - 6, 3), (5, ROOM_H - 4), (ROOM_W - 6, ROOM_H - 4)]
        elif pattern == "corners":
            coords = [
                (3, 2), (4, 2), (3, 3),
                (ROOM_W - 4, 2), (ROOM_W - 5, 2), (ROOM_W - 4, 3),
                (3, ROOM_H - 3), (4, ROOM_H - 3), (3, ROOM_H - 4),
                (ROOM_W - 4, ROOM_H - 3), (ROOM_W - 5, ROOM_H - 3), (ROOM_W - 4, ROOM_H - 4),
            ]
        elif pattern == "center_bars":
            coords = [(6, DOOR_Y - 2), (6, DOOR_Y + 2), (ROOM_W - 7, DOOR_Y - 2), (ROOM_W - 7, DOOR_Y + 2)]
        elif pattern == "twin_islands":
            coords = [(6, DOOR_Y - 2), (7, DOOR_Y - 2), (ROOM_W - 7, DOOR_Y + 2), (ROOM_W - 8, DOOR_Y + 2)]

        for ox, oy in coords:
            # Never block the main N-S or W-E door corridors
            if ox == DOOR_X or oy == DOOR_Y:
                continue
            self.tiles[oy][ox] = OBSTACLE

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
            # Enemies can never walk into doors; player can only enter unlocked doors
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
                    # Closest point on tile rectangle to circle center
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
        for _ in range(60):
            tx = rng.randint(margin_tiles, ROOM_W - 1 - margin_tiles)
            ty = rng.randint(margin_tiles, ROOM_H - 1 - margin_tiles)
            if self.tiles[ty][tx] != FLOOR:
                continue
            if avoid_center and abs(tx - DOOR_X) <= 2 and abs(ty - DOOR_Y) <= 2:
                continue
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

        # Grow a tree/cluster of rooms from (0, 0)
        attempts = 0
        while len(self.rooms) < num_rooms and attempts < 200:
            attempts += 1
            base = self.rng.choice(frontier)
            d = self.rng.choice(["N", "S", "E", "W"])
            dx, dy = DIR_OFFSET[d]
            cand = (base[0] + dx, base[1] + dy)
            if cand in self.rooms:
                continue
            # Prefer dead-ends / fewer neighbors so the map has branches like Isaac
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

        # Add obstacle layouts to normal combat rooms
        for room in self.rooms.values():
            room.add_obstacles(self.rng)
