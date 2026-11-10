"""Global settings and map definitions for Pizza Station Ares.

Change the numbers here to tweak the game without touching the other files.
"""

TITLE = "Pizza Station Ares"

# --- Graphics & Room Grid ---------------------------------------------------
TILE = 16              # size of one pixel-art sprite (16x16 pixels)
SCALE = 3              # every pixel-art pixel is drawn as a 3x3 block
CELL = TILE * SCALE    # size of one tile on the screen (48 px)

ROOM_W = 19            # tiles wide per room (including walls) -> 912 px
ROOM_H = 13            # tiles tall per floor room (including walls) -> 624 px
DOOR_X = ROOM_W // 2   # middle column for North/South doors (9)
DOOR_Y = ROOM_H // 2   # middle row for West/East doors (6)

# --- Window (Internal logical canvas size) ----------------------------------
VIEW_W = ROOM_W * CELL             # 912 px play area width
VIEW_H = ROOM_H * CELL             # 624 px play area height
PANEL_W = 300                      # width of the info panel on the right
SCREEN_W = VIEW_W + PANEL_W        # 1212 px total canvas width
SCREEN_H = VIEW_H                  # 624 px total canvas height
FPS = 60                           # 60 frames per second for smooth action

# Available window resolutions in the Settings menu
RESOLUTIONS = [
    ("1010x520 (Compact)", (1010, 520)),
    ("1212x624 (Default)", (1212, 624)),
    ("1454x748 (Large)",   (1454, 748)),
    ("1696x874 (HD+)",     (1696, 874)),
]
GRAPHICS_LEVELS = ["Low", "Medium", "High"]

# --- Gameplay ---------------------------------------------------------------
FINAL_FLOOR = 5        # the boss waits on this floor
PLAYER_HP = 25
PLAYER_ATTACK = 3
PLAYER_SPEED = 220.0   # pixels per second
FIRE_COOLDOWN = 0.26   # seconds between shots
SHOT_SPEED = 540.0     # pixels per second for player shots
IFRAME_TIME = 0.75     # seconds of invincibility after taking a hit
PIZZA_HEAL = 8

# --- Playable Maps / Campaigns ----------------------------------------------
MAP_ORDER = ["ares_station", "cryo_vaults", "lava_ovens", "mothership"]

MAPS = {
    "ares_station": {
        "id": "ares_station",
        "name": "Pizza Station Ares",
        "subtitle": "Standard Martian Pizzeria",
        "desc": "The original orbital pizzeria. Kitchens, dining halls, and the Giant Calzone.",
        "styles": ["kitchen", "dining", "storage"],
        "boss_style": "kitchen",
        "boss_name": "Giant Calzone",
        "difficulty": 1,
        "hp_mult": 1.0,
        "unlock_text": "Unlocked from the start",
        "accent": (240, 150, 60),
    },
    "cryo_vaults": {
        "id": "cryo_vaults",
        "name": "Polar Cryo-Vaults",
        "subtitle": "Sub-Zero Deep Freezer Sector",
        "desc": "Icy storage vaults under Mars' north pole. More drones and frosted rooms.",
        "styles": ["freezer", "storage", "kitchen"],
        "boss_style": "freezer",
        "boss_name": "Frostbite Calzone",
        "difficulty": 2,
        "hp_mult": 1.15,
        "unlock_text": "Reach Floor 3 or beat Map 1",
        "accent": (100, 210, 245),
    },
    "lava_ovens": {
        "id": "lava_ovens",
        "name": "Olympus Lava Ovens",
        "subtitle": "Volcanic Crust Foundry",
        "desc": "Built inside a Martian volcano! Red dust caverns, fiery ovens, and tough foes.",
        "styles": ["dust", "kitchen", "dining"],
        "boss_style": "dust",
        "boss_name": "Volcanic Calzone",
        "difficulty": 3,
        "hp_mult": 1.3,
        "unlock_text": "Beat Polar Cryo-Vaults",
        "accent": (235, 85, 55),
    },
    "mothership": {
        "id": "mothership",
        "name": "Anchovy Mothership",
        "subtitle": "Alien Saucer in High Orbit",
        "desc": "Board the alien flagship! High-speed enemies and Emperor Calzone Rex.",
        "styles": ["freezer", "dust", "kitchen", "dining", "storage"],
        "boss_style": "freezer",
        "boss_name": "Emperor Calzone Rex",
        "difficulty": 4,
        "hp_mult": 1.45,
        "unlock_text": "Beat Olympus Lava Ovens",
        "accent": (140, 230, 120),
    },
}
