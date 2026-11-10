"""Pixel art, animations, held weapons, and room furniture for Pizza Station Ares.

Every character, animation frame, and item sprite in SPRITES is a 16x16 grid of
letters. Each letter is a colour from PALETTE and '.' means transparent.
Floors, walls, big tables, kitchen counters, ovens, windows, and held weapons
are built with code further down.
"""

import random

PALETTE = {
    "k": (24, 14, 20),      # outline
    "w": (240, 238, 228),   # white
    "g": (175, 178, 190),   # light grey
    "s": (240, 190, 150),   # skin
    "r": (205, 45, 40),     # tomato red
    "R": (130, 25, 30),     # dark red
    "o": (232, 128, 40),    # orange
    "y": (250, 212, 80),    # cheese yellow
    "Y": (212, 150, 70),    # crust
    "b": (150, 80, 45),     # meat brown
    "B": (95, 50, 28),      # dark brown
    "c": (95, 200, 230),    # cyan
    "C": (40, 85, 150),     # dark blue
    "m": (125, 132, 148),   # metal
    "M": (72, 76, 92),      # dark metal
    "G": (90, 200, 90),     # alien green
    "e": (255, 60, 60),     # glowing eye
}

SPRITES = {
    "chef": [
        ".....kkkkkk.....",
        "....kwwwwwwk....",
        "...kwwwwwwwwk...",
        "...kwwwwwwwwk...",
        "....kwwwwwwk....",
        "....kssssssk....",
        "....kskssksk....",
        "....kssssssk....",
        ".....kssssk.....",
        "...kkwwwwwwkk...",
        "..kswwwrrwwwsk..",
        "..kswwwwwwwwsk..",
        "...kwwwwwwwwk...",
        "....kwwwwwwk....",
        "....kCCkkCCk....",
        "....kkk..kkk....",
    ],
    "chef_walk": [
        "....kkkkkk......",
        "...kwwwwwwk.....",
        "..kwwwwwwwwk....",
        "...kwwwwwwwwk...",
        "....kwwwwwwk....",
        "....kssssssk....",
        "....kskssksk....",
        "....kssssssk....",
        ".....kssssk.....",
        "...kkwwwwwwkk...",
        "..kswwwrrwwwsk..",
        "...kwwwwwwwwk...",
        "...kwwwwwwwwk...",
        "...kCCk..kCCk...",
        "...kkk....kkk...",
        "................",
    ],
    "meatball": [
        "................",
        "................",
        ".....kkkkkk.....",
        "...kkBbbbbbBkk..",
        "..kBbbbbbbbbbBk.",
        "..kbbrbbbbbrbbk.",
        ".kbbkekbbbkekbbk",
        ".kbbkkkbbbkkkbbk",
        ".kbbbbbbbbbbbbbk",
        ".kbbbrbkkkbbrbbk",
        ".kbbbbkrrrkbbbbk",
        "..kbbbbkkkbbbbk.",
        "..kBbbrbbbbbbBk.",
        "...kkBbbbbbBkk..",
        ".....kkkkkk.....",
        "................",
    ],
    "meatball_step": [
        "................",
        "................",
        "................",
        "....kkkkkkkk....",
        "..kkBbbbbbbbBkk.",
        ".kBbbbrbbbbrbbBk",
        ".kbbkekbbbkekbbk",
        ".kbbkkkbbbkkkbbk",
        ".kbbbbbbbbbbbbbk",
        ".kbbbkkkkkkkbbbk",
        ".kbbkrwrwrwrkbbk",
        "..kbkkkkkkkkkbk.",
        "..kBbbrbbbrbbBk.",
        "...kkBbbbbbbBkk.",
        ".....kkkkkkkk...",
        "................",
    ],
    "drone": [
        "................",
        ".kkkk......kkkk.",
        "kggggk....kggggk",
        ".kkkk.kkkk.kkkk.",
        ".....kmmmmk.....",
        "...kkmmmmmmkk...",
        "..kmmmmmmmmmmk..",
        "..kmMkkkkkkMmk..",
        "..kmMkeeeekMmk..",
        "..kmMkkkkkkMmk..",
        "..kmmmmmmmmmmk..",
        "...kkmmrrmmkk...",
        ".....kkmmkk.....",
        "......kyyk......",
        "......kYYk......",
        ".......kk.......",
    ],
    "drone_step": [
        "................",
        "..kk........kk..",
        ".kwwk......kwwk.",
        "..kk..kkkk..kk..",
        ".....kmmmmk.....",
        "...kkmmmmmmkk...",
        "..kmmmmmmmmmmk..",
        "..kmMkkkkkkMmk..",
        "..kmMkewwwekMmk.",
        "..kmMkkkkkkMmk..",
        "..kmmmmmmmmmmk..",
        "...kkmmrrmmkk...",
        ".....kkmmkk.....",
        "......kook......",
        "......kyyk......",
        ".......kk.......",
    ],
    "anchovy": [
        "................",
        "................",
        "..........kk....",
        ".........kcck...",
        "..kkkkkkkkcccck.",
        ".kcccccccccccck.",
        "kcgccccccccckek.",
        "kcccccccccccckck",
        "kcgcccccccccccck",
        ".kcCCCCCCCCCCck.",
        "..kkCCCCCCCCkk..",
        "...kkkkkkkkkk...",
        "...kG.kG.kG.kG..",
        "...kG.kG.kG.kG..",
        "..kk.kk.kk.kk...",
        "................",
    ],
    "anchovy_step": [
        "................",
        ".........kk.....",
        "........kcck....",
        "..kkkkkkkcccck..",
        ".kcccccccccccck.",
        "kcgccccccccckek.",
        "kcccccccccccckck",
        "kcgccccccckwwwwk",
        ".kcCCCCCCCkkkkk.",
        "..kkCCCCCCCCkk..",
        "...kkkkkkkkkk...",
        "..kG.kG.kG.kG...",
        "...kG.kG.kG.kG..",
        "...kk.kk.kk.kk..",
        "................",
        "................",
    ],
    "calzone": [
        "................",
        "......kkkk......",
        "....kkYYYYkk....",
        "...kYYyYYyYYk...",
        "..kYYYYYYYYYYk..",
        ".kYYkkYYYYkkYYk.",
        ".kYkeekYYkeekYk.",
        "kYYkkkYYYYkkkYYk",
        "kYYYYYYYYYYYYYYk",
        "kYYkkkkkkkkkkYYk",
        "kYYkrwrwrwrwkYYk",
        "kYYkrrrrrrrrkYYk",
        ".kYYkkkkkkkkYYk.",
        "..kYYYYYYYYYYk..",
        "...kkYyYYyYkk...",
        ".....kkkkkk.....",
    ],
    "calzone_step": [
        "......kkkk......",
        "....kkYYYYkk....",
        "...kYYyYYyYYk...",
        "..kYYYYYYYYYYk..",
        ".kYYkkYYYYkkYYk.",
        ".kYkeekYYkeekYk.",
        "kYYkkkYYYYkkkYYk",
        "kYYYYYYYYYYYYYYk",
        "kYYkkkkkkkkkkYYk",
        "kYYkwkwkwkwkkYYk",
        "kYYkrrrrrrrrkYYk",
        "kYYkryyyyyyrkYYk",
        ".kYYkwkwkwkwYYk.",
        "..kYYkkkkkkkkk..",
        "...kkYyYYyYkk...",
        ".....kkkkkk.....",
    ],
    "pizza": [
        "................",
        "..kkkkkkkkkkkk..",
        "..kYYYYYYYYYYk..",
        "..kYYYYYYYYYYk..",
        "...kyyryyyyyk...",
        "...kyyyyyryyk...",
        "....kyryyyyk....",
        "....kyyyyyyk....",
        ".....kyyryk.....",
        ".....kyyyyk.....",
        "......kyyk......",
        "......kyyk......",
        ".......kk.......",
        "................",
        "................",
        "................",
    ],
    "rolling_pin": [
        "................",
        ".............kk.",
        "............kbbk",
        "...........kbbk.",
        "..........kYYk..",
        ".........kYYYk..",
        "........kYYYk...",
        ".......kYYYk....",
        "......kYYYk.....",
        ".....kYYYk......",
        "....kYYYk.......",
        "...kYYYk........",
        "..kbbk..........",
        ".kbbk...........",
        "..kk............",
        "................",
    ],
    "cutter": [
        "................",
        "....kkkkk.......",
        "...kgggggk......",
        "..kgwwwwwgk.....",
        "..kgwgkgwgk.....",
        "..kgwkmkwgk.....",
        "..kgwgkgwgk.....",
        "..kgwwwwwgk.....",
        "...kgggggkk.....",
        "....kkkkkrrk....",
        ".........krrk...",
        "..........krrk..",
        "...........krrk.",
        "............krk.",
        ".............k..",
        "................",
    ],
    "apron": [
        "................",
        ".....kk..kk.....",
        "....kwk..kwk....",
        "....kwk..kwk....",
        "...kkwkkkkwkk...",
        "...kooooooook...",
        "...kooooooook...",
        "..kooookkooook..",
        "..koookyykoook..",
        "..kooookkooook..",
        "..koooooooooook.",
        "..kookkkkkkook..",
        "..koooooooooook.",
        "...kooooooook...",
        "....kkkkkkkk....",
        "................",
    ],
    "oxygen": [
        "................",
        "......kkkk......",
        ".....kmmmmk.....",
        "......kmmk......",
        ".....kkkkkk.....",
        "....kccccwck....",
        "....kccccwck....",
        "....kcCCCwck....",
        "....kcCwCwck....",
        "....kcCCCwck....",
        "....kccccwck....",
        "....kccccwck....",
        "....kccccwck....",
        "....kCCCCCCk....",
        ".....kkkkkk.....",
        "................",
    ],
    "credits": [
        "................",
        "................",
        "................",
        ".....kkkkkk.....",
        "....kyyyyyyk....",
        "...kyyYYYYyyk...",
        "...kyYyyyyYyk...",
        "...kyYyyyyyyk...",
        "...kyYyyyyyyk...",
        "...kyYyyyyYyk...",
        "...kyyYYYYyyk...",
        "....kyyyyyyk....",
        ".....kkkkkk.....",
        "................",
        "................",
        "................",
    ],
}

# Floor colours for each room type: (colour A, colour B)
FLOOR_COLOURS = {
    "kitchen": ((128, 126, 132), (104, 102, 112)),    # grey kitchen tiles
    "dining":  ((140, 48, 46), (176, 150, 118)),      # red & cream tablecloth checker
    "freezer": ((112, 162, 192), (154, 200, 224)),    # icy blue
    "storage": ((118, 82, 50), (92, 62, 38)),         # wooden planks
    "dust":    ((162, 74, 44), (190, 96, 56)),        # red Mars dust
}


def _grid_to_surface(pygame, rows):
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    for y, row in enumerate(rows[:16]):
        for x, ch in enumerate(row[:16]):
            if ch in PALETTE:
                surf.set_at((x, y), PALETTE[ch])
    return surf


def _floor_tile(pygame, kind, variant):
    a, b = FLOOR_COLOURS[kind]
    surf = pygame.Surface((16, 16))
    surf.fill(a)
    rng = random.Random(sum(map(ord, kind)) * 10 + variant)
    if kind in ("kitchen", "dining"):          # checkerboard
        surf.fill(b, (0, 0, 8, 8))
        surf.fill(b, (8, 8, 8, 8))
    elif kind == "freezer":                     # ice tiles with light grout
        pygame.draw.rect(surf, b, (0, 0, 16, 16), 1)
        surf.set_at((rng.randint(3, 12), rng.randint(3, 12)), (230, 245, 255))
    elif kind == "storage":                     # planks
        for y in (3, 7, 11, 15):
            pygame.draw.line(surf, b, (0, y), (15, y))
        pygame.draw.line(surf, b, (rng.randint(2, 13), 0), (rng.randint(2, 13), 3))
    else:                                       # Mars dust: random specks
        for _ in range(10):
            surf.set_at((rng.randint(0, 15), rng.randint(0, 15)), b)
        for _ in range(5):
            surf.set_at((rng.randint(0, 15), rng.randint(0, 15)), (120, 52, 32))
    return surf


def _wall_tile(pygame, front):
    """front=True: the side of the wall you see (floor below it)."""
    surf = pygame.Surface((16, 16))
    if front:
        surf.fill((78, 80, 96))
        surf.fill((112, 115, 132), (0, 0, 16, 4))       # top edge highlight
        pygame.draw.line(surf, (50, 50, 62), (0, 15), (15, 15))
        pygame.draw.line(surf, (60, 62, 76), (8, 4), (8, 14))
        for x, y in ((2, 6), (13, 6), (2, 12), (13, 12)):
            surf.set_at((x, y), (160, 160, 176))         # rivets
        surf.fill((232, 128, 40), (4, 9, 3, 1))         # little orange light
    else:
        surf.fill((52, 54, 68))
        pygame.draw.rect(surf, (70, 72, 88), (0, 0, 16, 16), 1)
    return surf


# ---------------------------------------------------------------------------
# Held Weapons (drawn pointing right at 0 deg so they rotate toward the cursor)
# ---------------------------------------------------------------------------
def _weapon_surface(pygame, kind):
    """Build a 16x10 pixel-art weapon sprite pointing right (+X)."""
    surf = pygame.Surface((16, 10), pygame.SRCALPHA)
    k = (24, 14, 20)
    if kind == "blaster":
        # Retro red & steel Sauce/Dough Blaster with brass nozzle
        pygame.draw.rect(surf, k, (2, 2, 12, 6))
        surf.fill((195, 45, 40), (3, 3, 7, 4))          # red canister body
        surf.fill((240, 238, 228), (4, 3, 5, 1))        # top highlight
        surf.fill((130, 138, 155), (10, 3, 3, 4))       # steel barrel
        surf.fill((250, 212, 80), (13, 3, 2, 4))        # brass muzzle tip
        surf.fill((72, 76, 92), (3, 7, 3, 3))           # grip handle
    elif kind == "rolling_pin":
        # Heavy wooden & brass Rolling-Pin Cannon
        pygame.draw.rect(surf, k, (1, 2, 14, 6))
        surf.fill((150, 80, 45), (1, 4, 3, 2))          # back wooden handle
        surf.fill((212, 150, 70), (4, 3, 8, 4))         # oak roller barrel
        surf.fill((250, 212, 80), (4, 3, 8, 1))         # shine
        surf.fill((205, 45, 40), (7, 3, 2, 4))          # red stripe band
        surf.fill((195, 110, 45), (12, 3, 3, 4))        # front launcher nozzle
    else:
        # Motorized Rotary Pizza Cutter Launcher
        pygame.draw.rect(surf, k, (1, 3, 9, 5))
        surf.fill((205, 45, 40), (2, 4, 6, 3))          # red motor housing
        surf.fill((125, 132, 148), (8, 4, 3, 3))        # steel arm
        # Circular saw/cutter disc at the front
        pygame.draw.circle(surf, k, (11, 5), 4)
        pygame.draw.circle(surf, (220, 225, 235), (11, 5), 3)
        pygame.draw.circle(surf, (205, 45, 40), (11, 5), 1)
    return surf


# ---------------------------------------------------------------------------
# Room Furniture & Obstacles (Tables, Kitchen Counters, Ovens, Freezers, Crates)
# ---------------------------------------------------------------------------
def _table_tile(pygame, part="single"):
    """Dining table with red & white checkered tablecloth, legs, and pizza/candle."""
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    k = (24, 14, 20)
    wood = (110, 62, 34)
    red = (198, 45, 42)
    cream = (242, 235, 220)

    x0 = 1 if part in ("left", "single") else 0
    x1 = 15 if part in ("right", "single") else 16
    w = x1 - x0

    # Wooden legs at bottom
    if part in ("left", "single"):
        surf.fill(k, (2, 11, 3, 5))
        surf.fill(wood, (3, 11, 1, 4))
    if part in ("right", "single"):
        surf.fill(k, (11, 11, 3, 5))
        surf.fill(wood, (12, 11, 1, 4))
    # Shadow under table
    surf.fill((18, 10, 16, 140), (x0, 13, w, 3))

    # Table top + hanging cloth skirt
    surf.fill(k, (x0, 1, w, 12))
    for ty in range(2, 11):
        for tx in range(x0 + (1 if x0 else 0), x1 - (1 if x1 == 15 else 0)):
            col = red if ((tx // 3) + (ty // 3)) % 2 == 0 else cream
            if ty >= 9:
                # Darker cloth hang front
                col = (max(0, col[0] - 40), max(0, col[1] - 40), max(0, col[2] - 40))
            surf.set_at((tx, ty), col)

    # Items on top of the table!
    if part == "left":
        # Whole pizza on a wooden platter
        pygame.draw.circle(surf, (212, 150, 70), (11, 5), 3)
        pygame.draw.circle(surf, (250, 212, 80), (11, 5), 2)
        surf.set_at((11, 5), red)
        surf.set_at((12, 4), red)
    elif part == "right":
        # Glowing table candle + parmesan shaker
        surf.fill((240, 238, 228), (4, 4, 2, 3))
        surf.set_at((4, 3), (250, 212, 80))
        surf.set_at((5, 2), (240, 130, 40))
        surf.fill((160, 210, 235), (9, 5, 2, 2))
    else:
        pygame.draw.circle(surf, (250, 212, 80), (8, 5), 2)
        surf.set_at((8, 5), red)
    return surf


def _counter_tile(pygame, part="left"):
    """Stainless-steel kitchen prep counter with dough, cutting board & sauce pot."""
    surf = pygame.Surface((16, 16))
    k = (24, 14, 20)
    surf.fill(k)
    x0 = 1 if part == "left" else 0
    x1 = 16 if part == "left" else 15
    w = x1 - x0

    # Steel top surface
    surf.fill((168, 174, 188), (x0, 1, w, 8))
    surf.fill((215, 220, 232), (x0, 1, w, 2))
    # Red trim & cabinet doors below
    surf.fill((195, 45, 40), (x0, 9, w, 2))
    surf.fill((95, 102, 118), (x0, 11, w, 4))
    surf.fill((65, 70, 84), (4, 12, 8, 2))

    if part == "left":
        # Wooden cutting board + rolled pizza dough + knife
        surf.fill((185, 130, 70), (3, 3, 7, 5))
        pygame.draw.circle(surf, (245, 225, 160), (6, 5), 2)
        surf.fill((230, 235, 245), (11, 4, 3, 1))
    else:
        # Simmering pot of tomato sauce + basil leaves
        pygame.draw.circle(surf, (80, 85, 100), (6, 5), 3)
        pygame.draw.circle(surf, (205, 45, 40), (6, 5), 2)
        surf.fill((90, 200, 90), (11, 4, 2, 2))
    return surf


def _oven_tile(pygame, frame=0):
    """Brick pizza oven with flickering orange-and-yellow fire inside."""
    surf = pygame.Surface((16, 16))
    surf.fill((24, 14, 20))
    # Brick body
    surf.fill((155, 58, 42), (1, 2, 14, 13))
    surf.fill((110, 42, 32), (1, 1, 14, 2))
    # Brick mortar lines
    for y in (4, 7, 10, 13):
        pygame.draw.line(surf, (115, 40, 30), (1, y), (14, y))
    # Dark arched oven mouth
    surf.fill((32, 18, 22), (4, 6, 8, 8))
    surf.fill((90, 92, 106), (3, 5, 10, 1))
    # Animated flickering flames inside
    flame_hi = (255, 230, 95)
    flame_mid = (245, 140, 40)
    flame_lo = (215, 55, 35)
    surf.fill(flame_lo, (5, 10, 6, 3))
    if frame == 0:
        surf.fill(flame_mid, (5, 8, 5, 3))
        surf.fill(flame_hi, (6, 9, 3, 2))
        surf.set_at((9, 7), flame_mid)
    else:
        surf.fill(flame_mid, (6, 7, 5, 4))
        surf.fill(flame_hi, (7, 8, 3, 3))
        surf.set_at((5, 7), flame_hi)
    return surf


def _freezer_tile(pygame, part="left"):
    """Cryo-freezer display chest with frosted glass and frozen pizzas."""
    surf = pygame.Surface((16, 16))
    surf.fill((24, 14, 20))
    x0 = 1 if part == "left" else 0
    x1 = 16 if part == "left" else 15
    w = x1 - x0
    surf.fill((180, 215, 235), (x0, 1, w, 9))
    surf.fill((95, 165, 210), (x0 + 1, 2, w - 2, 7))
    # Frozen pizza visible through glass
    pygame.draw.circle(surf, (235, 200, 110), (8, 5), 2)
    surf.set_at((5, 3), (245, 252, 255))
    surf.set_at((11, 7), (245, 252, 255))
    # Lower cryo unit
    surf.fill((75, 115, 145), (x0, 10, w, 5))
    surf.fill((95, 225, 255), (6, 12, 4, 1))
    return surf


def _ice_block_tile(pygame):
    surf = pygame.Surface((16, 16))
    surf.fill((24, 14, 20))
    surf.fill((125, 195, 235), (1, 1, 14, 14))
    surf.fill((195, 235, 255), (2, 2, 12, 3))
    pygame.draw.line(surf, (240, 252, 255), (3, 6), (7, 10))
    pygame.draw.line(surf, (85, 145, 185), (2, 13), (13, 13))
    return surf


def _crate_tile(pygame, part="single"):
    """Wooden Mars cargo crate + stacked pizza delivery boxes."""
    surf = pygame.Surface((16, 16))
    surf.fill((24, 14, 20))
    x0 = 1 if part in ("left", "single") else 0
    x1 = 15 if part in ("right", "single") else 16
    w = x1 - x0
    surf.fill((158, 96, 52), (x0, 1, w, 14))
    pygame.draw.rect(surf, (115, 66, 34), (x0, 1, w, 14), 2)
    pygame.draw.line(surf, (115, 66, 34), (x0, 8), (x1 - 1, 8))
    if part == "right":
        # Stack of white & red pizza boxes on top
        surf.fill((240, 235, 225), (3, 2, 9, 5))
        surf.fill((205, 45, 40), (4, 3, 7, 2))
    else:
        pygame.draw.line(surf, (190, 125, 72), (3, 3), (12, 12))
    return surf


def _hydro_tile(pygame, part="left"):
    """Martian hydroponic planter growing alien tomatoes and basil."""
    surf = pygame.Surface((16, 16))
    surf.fill((24, 14, 20))
    x0 = 1 if part == "left" else 0
    x1 = 16 if part == "left" else 15
    w = x1 - x0
    surf.fill((90, 96, 112), (x0, 2, w, 13))
    surf.fill((75, 45, 32), (x0 + 1, 3, w - 2, 6))      # rich Mars soil
    for gx in (3, 7, 11):
        surf.fill((80, 195, 85), (gx, 2, 3, 5))          # green leaves
        surf.set_at((gx + 1, 3), (225, 50, 45))          # ripe red tomato
    surf.fill((95, 200, 230), (x0 + 2, 11, w - 4, 2))    # glowing water strip
    return surf


def _rock_tile(pygame):
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(surf, (24, 14, 20), (8, 9), 7)
    pygame.draw.circle(surf, (135, 55, 38), (8, 9), 6)
    pygame.draw.circle(surf, (175, 78, 50), (7, 7), 4)
    return surf


# ---------------------------------------------------------------------------
# Wall & Floor Decorations (Windows, Wall Ovens, Neon Signs, Stools, Rugs)
# ---------------------------------------------------------------------------
def _wall_window_tile(pygame, frame=0):
    """Panoramic window on the north wall looking out at Mars and twinkling stars."""
    surf = _wall_tile(pygame, front=True)
    surf.fill((24, 14, 20), (1, 3, 14, 10))
    surf.fill((14, 10, 26), (2, 4, 12, 8))               # deep space
    # Red Mars horizon curve
    pygame.draw.circle(surf, (185, 75, 45), (10, 15), 6)
    # Twinkling stars
    star_col = (255, 255, 220) if frame == 0 else (160, 210, 255)
    surf.set_at((4, 6), star_col)
    surf.set_at((11, 5), (240, 240, 255))
    surf.set_at((7, 8), star_col)
    # Window mullion bar
    pygame.draw.line(surf, (95, 100, 118), (8, 4), (8, 11))
    return surf


def _wall_neon_tile(pygame, frame=0):
    """Glowing neon pizza sign mounted on the north wall."""
    surf = _wall_tile(pygame, front=True)
    surf.fill((28, 16, 28), (2, 4, 12, 9))
    glow = (255, 90, 70) if frame == 0 else (255, 160, 60)
    pygame.draw.rect(surf, glow, (2, 4, 12, 9), 1)
    # Neon pizza slice triangle
    pygame.draw.polygon(surf, (250, 220, 90), [(5, 6), (11, 6), (8, 11)])
    surf.set_at((8, 8), (255, 60, 60))
    return surf


def _wall_rack_tile(pygame):
    """Hanging kitchen rack with pots and knives on the north wall."""
    surf = _wall_tile(pygame, front=True)
    pygame.draw.line(surf, (40, 42, 52), (2, 5), (13, 5))
    # Copper pot & steel pan hanging
    pygame.draw.circle(surf, (215, 125, 55), (5, 9), 2)
    pygame.draw.circle(surf, (185, 192, 208), (10, 9), 2)
    surf.fill((230, 235, 245), (13, 6, 1, 5))
    return surf


def _wall_vent_tile(pygame):
    surf = _wall_tile(pygame, front=True)
    surf.fill((42, 46, 58), (3, 5, 10, 8))
    for y in (6, 8, 10):
        pygame.draw.line(surf, (95, 105, 125), (4, y), (11, y))
    return surf


def _floor_decor_tile(pygame, kind):
    """Non-blocking floor details (stools, rugs, pizza boxes, grates, sauce)."""
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    if kind == "floor_mat":
        surf.fill((185, 45, 40), (1, 2, 14, 12))
        pygame.draw.rect(surf, (250, 212, 80), (2, 3, 12, 10), 1)
    elif kind == "stool_top":
        pygame.draw.circle(surf, (24, 14, 20), (8, 11), 4)
        pygame.draw.circle(surf, (205, 48, 45), (8, 11), 3)
        surf.set_at((7, 10), (245, 180, 175))
    elif kind == "stool_bottom":
        pygame.draw.circle(surf, (24, 14, 20), (8, 5), 4)
        pygame.draw.circle(surf, (205, 48, 45), (8, 5), 3)
        surf.set_at((7, 4), (245, 180, 175))
    elif kind == "floor_grate":
        surf.fill((55, 58, 70), (3, 4, 10, 8))
        for x in (5, 8, 11):
            pygame.draw.line(surf, (25, 26, 34), (x, 5), (x, 10))
    elif kind == "pizza_box":
        surf.fill((24, 14, 20), (3, 4, 9, 8))
        surf.fill((238, 232, 218), (4, 5, 7, 6))
        surf.fill((205, 45, 40), (5, 6, 5, 3))
    elif kind == "sauce_spot":
        pygame.draw.circle(surf, (175, 38, 35, 190), (7, 8), 3)
        pygame.draw.circle(surf, (195, 45, 40, 190), (10, 10), 2)
    elif kind == "flour_spot":
        pygame.draw.circle(surf, (235, 230, 215, 160), (8, 8), 3)
        pygame.draw.circle(surf, (235, 230, 215, 140), (5, 10), 2)
    elif kind == "ice_patch":
        pygame.draw.circle(surf, (190, 235, 255, 150), (8, 8), 4)
    elif kind == "mars_pebbles":
        for px, py in ((5, 6), (10, 9), (7, 11)):
            surf.fill((120, 48, 30), (px, py, 2, 2))
    return surf


def _door_tile(pygame, locked=False, boss=False):
    """An Isaac-style doorway in the room wall."""
    surf = pygame.Surface((16, 16))
    frame_col = (195, 55, 50) if boss else (212, 150, 70)
    surf.fill(frame_col)
    if locked:
        surf.fill((58, 60, 74), (2, 2, 12, 12))
        for y in (4, 8, 12):
            pygame.draw.line(surf, (250, 212, 80), (2, y), (13, y))
        surf.fill((220, 50, 45), (6, 6, 4, 4))
    else:
        inner = (70, 20, 28) if boss else (42, 30, 24)
        glow = (235, 95, 75) if boss else (245, 190, 95)
        surf.fill(inner, (2, 2, 12, 12))
        pygame.draw.rect(surf, glow, (3, 3, 10, 10), 1)
    return surf


def _hatch_tile(pygame):
    surf = pygame.Surface((16, 16))
    surf.fill((28, 26, 34))
    for i in range(16):
        colour = (250, 212, 80) if (i // 2) % 2 == 0 else (24, 14, 20)
        for x, y in ((i, 0), (i, 15), (0, i), (15, i)):
            surf.set_at((x, y), colour)
    arrow = [(5, 5), (10, 5), (10, 8), (12, 8), (8, 12), (7, 12), (3, 8), (5, 8)]
    pygame.draw.polygon(surf, (250, 212, 80), arrow)
    return surf


def build_sprites(scale):
    """Turn all the art into scaled pygame surfaces."""
    import pygame
    size = 16 * scale

    def big(surf, factor=1.0):
        w = int(surf.get_width() * scale * factor)
        h = int(surf.get_height() * scale * factor)
        return pygame.transform.scale(surf, (w, h))

    sprites = {name: big(_grid_to_surface(pygame, rows)) for name, rows in SPRITES.items()}
    sprites["calzone_boss"] = big(_grid_to_surface(pygame, SPRITES["calzone"]), 1.45)
    sprites["calzone_boss_step"] = big(_grid_to_surface(pygame, SPRITES["calzone_step"]), 1.45)
    sprites["hatch"] = big(_hatch_tile(pygame))

    # Held weapons (scaled so they fit nicely in the chef's hands)
    sprites["weapon_blaster"] = big(_weapon_surface(pygame, "blaster"), 0.85)
    sprites["weapon_rolling_pin"] = big(_weapon_surface(pygame, "rolling_pin"), 0.9)
    sprites["weapon_cutter"] = big(_weapon_surface(pygame, "cutter"), 0.9)

    floors = {kind: [big(_floor_tile(pygame, kind, v)) for v in range(3)] for kind in FLOOR_COLOURS}
    walls = {
        "front": big(_wall_tile(pygame, True)),
        "top": big(_wall_tile(pygame, False)),
        "obstacle": big(_counter_tile(pygame, "left")),
        # Furniture
        "table_left": big(_table_tile(pygame, "left")),
        "table_right": big(_table_tile(pygame, "right")),
        "table_single": big(_table_tile(pygame, "single")),
        "counter_left": big(_counter_tile(pygame, "left")),
        "counter_right": big(_counter_tile(pygame, "right")),
        "oven_block": big(_oven_tile(pygame, 0)),
        "oven_block_alt": big(_oven_tile(pygame, 1)),
        "freezer_left": big(_freezer_tile(pygame, "left")),
        "freezer_right": big(_freezer_tile(pygame, "right")),
        "ice_block": big(_ice_block_tile(pygame)),
        "crate_left": big(_crate_tile(pygame, "left")),
        "crate_right": big(_crate_tile(pygame, "right")),
        "crate_single": big(_crate_tile(pygame, "single")),
        "hydro_left": big(_hydro_tile(pygame, "left")),
        "hydro_right": big(_hydro_tile(pygame, "right")),
        "rock_single": big(_rock_tile(pygame)),
        # Wall fixtures
        "wall_window": big(_wall_window_tile(pygame, 0)),
        "wall_window_alt": big(_wall_window_tile(pygame, 1)),
        "wall_oven": big(_oven_tile(pygame, 0)),
        "wall_oven_alt": big(_oven_tile(pygame, 1)),
        "wall_neon": big(_wall_neon_tile(pygame, 0)),
        "wall_neon_alt": big(_wall_neon_tile(pygame, 1)),
        "wall_rack": big(_wall_rack_tile(pygame)),
        "wall_vent": big(_wall_vent_tile(pygame)),
        # Doors
        "door_open": big(_door_tile(pygame, locked=False, boss=False)),
        "door_locked": big(_door_tile(pygame, locked=True, boss=False)),
        "door_boss_open": big(_door_tile(pygame, locked=False, boss=True)),
        "door_boss_locked": big(_door_tile(pygame, locked=True, boss=True)),
    }
    # Floor decorations
    for d_kind in (
        "floor_mat", "stool_top", "stool_bottom", "floor_grate",
        "pizza_box", "sauce_spot", "flour_spot", "ice_patch", "mars_pebbles",
    ):
        walls[d_kind] = big(_floor_decor_tile(pygame, d_kind))

    return sprites, floors, walls
