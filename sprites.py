"""Pixel art for Pizza Station Ares.

Every character sprite is a 16x16 grid of letters. Each letter is a colour
from PALETTE and '.' means transparent. You can redraw any sprite just by
editing the letters, or replace them with PNG files made in Piskel later.
Floors, walls and the hatch are drawn with code further down.
"""

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
    "kitchen": ((128, 126, 132), (100, 98, 108)),    # grey kitchen tiles
    "dining":  ((140, 48, 46), (176, 150, 118)),     # red & cream, like a tablecloth
    "freezer": ((112, 162, 192), (160, 205, 228)),   # icy blue
    "storage": ((112, 76, 46), (82, 54, 32)),        # wooden planks
    "dust":    ((160, 72, 42), (190, 96, 56)),       # red Mars dust
}


def _grid_to_surface(pygame, rows):
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    for y, row in enumerate(rows[:16]):
        for x, ch in enumerate(row[:16]):
            if ch in PALETTE:
                surf.set_at((x, y), PALETTE[ch])
    return surf


def _floor_tile(pygame, kind, variant):
    import random
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
        surf.fill((46, 46, 58))
        pygame.draw.rect(surf, (62, 62, 78), (0, 0, 16, 16), 1)
    return surf


def _hatch_tile(pygame):
    surf = pygame.Surface((16, 16))
    surf.fill((28, 26, 34))
    for i in range(16):                                  # hazard stripes border
        colour = (250, 212, 80) if (i // 2) % 2 == 0 else (24, 14, 20)
        for x, y in ((i, 0), (i, 15), (0, i), (15, i)):
            surf.set_at((x, y), colour)
    arrow = [(5, 5), (10, 5), (10, 8), (12, 8), (8, 12), (7, 12), (3, 8), (5, 8)]
    pygame.draw.polygon(surf, (250, 212, 80), arrow)
    return surf


def build_sprites(scale):
    """Turn all the art into scaled pygame surfaces.

    Returns (sprites, floors, walls):
      sprites["chef"] -> surface
      floors["dust"]  -> list of 3 variants
      walls["front"] / walls["top"] / sprites["hatch"]
    """
    import pygame
    size = 16 * scale

    def big(surf):
        return pygame.transform.scale(surf, (size, size))   # keeps pixels sharp

    sprites = {name: big(_grid_to_surface(pygame, rows)) for name, rows in SPRITES.items()}
    sprites["hatch"] = big(_hatch_tile(pygame))
    floors = {kind: [big(_floor_tile(pygame, kind, v)) for v in range(3)] for kind in FLOOR_COLOURS}
    walls = {"front": big(_wall_tile(pygame, True)), "top": big(_wall_tile(pygame, False))}
    return sprites, floors, walls
