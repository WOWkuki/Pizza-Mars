"""Procedural map generation and field of view (what the chef can see).

Every floor is made of rectangular rooms connected by tunnels of red Mars dust.
"""

WALL = "#"
FLOOR = "."
HATCH = ">"   # the delivery hatch that leads to the next floor

ROOM_KINDS = ["kitchen", "dining", "freezer", "storage"]


class Room:
    """A rectangular room. (x, y) is the top-left floor tile."""

    def __init__(self, x, y, w, h, kind):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.kind = kind

    def center(self):
        return self.x + self.w // 2, self.y + self.h // 2

    def intersects(self, other):
        """True if the rooms overlap or touch (we want a wall between rooms)."""
        return not (self.x + self.w < other.x or other.x + other.w < self.x or
                    self.y + self.h < other.y or other.y + other.h < self.y)

    def tiles(self):
        for ty in range(self.y, self.y + self.h):
            for tx in range(self.x, self.x + self.w):
                yield tx, ty


def line(x0, y0, x1, y1):
    """Bresenham's line algorithm: all tiles on a straight line between two points."""
    points = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return points
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


class Dungeon:
    def __init__(self, width, height, rng):
        self.width, self.height = width, height
        self.rng = rng
        self.tiles = [[WALL] * width for _ in range(height)]
        self.style = [["dust"] * width for _ in range(height)]   # floor look
        self.explored = [[False] * width for _ in range(height)]
        self.visible = set()
        self.rooms = []
        self.hatch = None

    # --- generation ---------------------------------------------------------
    def generate(self, max_rooms=11, min_size=4, max_size=9, place_hatch=True):
        for _ in range(max_rooms * 10):
            if len(self.rooms) >= max_rooms:
                break
            w = self.rng.randint(min_size, max_size)
            h = self.rng.randint(min_size, max_size - 2)
            x = self.rng.randint(1, self.width - w - 1)
            y = self.rng.randint(1, self.height - h - 1)
            kind = "kitchen" if not self.rooms else self.rng.choice(ROOM_KINDS)
            room = Room(x, y, w, h, kind)
            if any(room.intersects(other) for other in self.rooms):
                continue
            self.carve_room(room)
            if self.rooms:
                # connect every new room to the previous one -> everything is reachable
                self.carve_tunnel(*self.rooms[-1].center(), *room.center())
            self.rooms.append(room)

        if place_hatch:
            self.hatch = self.farthest_room().center()
            hx, hy = self.hatch
            self.tiles[hy][hx] = HATCH

    def carve_room(self, room):
        for tx, ty in room.tiles():
            self.tiles[ty][tx] = FLOOR
            self.style[ty][tx] = room.kind

    def carve_tunnel(self, x1, y1, x2, y2):
        """L-shaped tunnel: first horizontal then vertical, or the other way round."""
        corner = (x2, y1) if self.rng.random() < 0.5 else (x1, y2)
        for (ax, ay), (bx, by) in (((x1, y1), corner), (corner, (x2, y2))):
            for tx in range(min(ax, bx), max(ax, bx) + 1):
                for ty in range(min(ay, by), max(ay, by) + 1):
                    if self.tiles[ty][tx] == WALL:
                        self.tiles[ty][tx] = FLOOR
                        self.style[ty][tx] = "dust"

    def farthest_room(self):
        """The room farthest from the starting room (used for the hatch and the boss)."""
        sx, sy = self.rooms[0].center()
        candidates = self.rooms[1:] or self.rooms
        return max(candidates, key=lambda r: abs(r.center()[0] - sx) + abs(r.center()[1] - sy))

    # --- queries ------------------------------------------------------------
    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x, y):
        return self.in_bounds(x, y) and self.tiles[y][x] != WALL

    # --- field of view ------------------------------------------------------
    def compute_fov(self, px, py, radius):
        """Cast rays from the player to the edge of a square; walls block sight."""
        self.visible = {(px, py)}
        targets = []
        for i in range(-radius, radius + 1):
            targets += [(px + i, py - radius), (px + i, py + radius),
                        (px - radius, py + i), (px + radius, py + i)]
        limit = radius * radius + radius   # makes the view round instead of square
        for tx, ty in targets:
            for x, y in line(px, py, tx, ty)[1:]:
                if not self.in_bounds(x, y) or (x - px) ** 2 + (y - py) ** 2 > limit:
                    break
                self.visible.add((x, y))
                if self.tiles[y][x] == WALL:
                    break
        for x, y in self.visible:
            self.explored[y][x] = True
