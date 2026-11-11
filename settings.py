"""Global settings for Pizza Station Ares (Real-Time Action Roguelike).

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

# Available window & render resolutions in the Settings menu
RESOLUTIONS = [
    ("606x312 (Retro Low-Res)", (606, 312)),
    ("1010x520 (Compact)",      (1010, 520)),
    ("1212x624 (Default)",      (1212, 624)),
    ("1454x748 (Large)",        (1454, 748)),
    ("1696x874 (HD+)",          (1696, 874)),
]
GRAPHICS_LEVELS = ["Low", "Medium", "High"]

# --- Gameplay ---------------------------------------------------------------
FINAL_FLOOR = 5        # the Giant Calzone waits on this floor
PLAYER_HP = 25
PLAYER_ATTACK = 3
PLAYER_SPEED = 220.0   # pixels per second
FIRE_COOLDOWN = 0.26   # seconds between shots
SHOT_SPEED = 540.0     # pixels per second for player shots
IFRAME_TIME = 0.75     # seconds of invincibility after taking a hit
PIZZA_HEAL = 8
