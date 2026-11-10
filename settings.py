"""Global settings for Pizza Station Ares.

Change the numbers here to tweak the game without touching the other files.
"""

TITLE = "Pizza Station Ares"

# --- Graphics ---------------------------------------------------------------
TILE = 16              # size of one pixel-art tile (16x16 pixels)
SCALE = 2              # every pixel-art pixel is drawn as a SCALE x SCALE block
CELL = TILE * SCALE    # size of one tile on the screen (32 px)

# --- Map --------------------------------------------------------------------
MAP_W, MAP_H = 50, 34      # size of a whole floor in tiles
VIEW_W, VIEW_H = 30, 20    # how many tiles fit on screen (the camera follows you)

# --- Window -----------------------------------------------------------------
PANEL_W = 300                      # width of the info panel on the right
SCREEN_W = VIEW_W * CELL + PANEL_W
SCREEN_H = VIEW_H * CELL
FPS = 30

# --- Gameplay ---------------------------------------------------------------
FOV_RADIUS = 7         # how far the chef can see
FINAL_FLOOR = 5        # the Giant Calzone waits on this floor
PLAYER_HP = 25
PLAYER_ATTACK = 3
PIZZA_HEAL = 8
REGEN_EVERY = 10       # the chef heals 1 HP every this many turns
