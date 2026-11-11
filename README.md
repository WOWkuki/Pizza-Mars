# Pizza Station Ares 🍕🚀

An **Isaac-style real-time action roguelike** set in a pizzeria on Mars, made with **Python 3** and **Pygame-CE**.

The year is 2097. Your Martian pizzeria has been overrun by mutant meatballs,
rogue delivery drones and alien anchovies. Fight room-by-room across 5 floors,
collect upgrades, and defeat the **Giant Calzone**!

## How to run

```bash
# one-time setup (already done on this PC)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# play
.venv/bin/python main.py
```

## Controls

| Input | Action |
|---|---|
| **WASD** / Arrow Keys | Move smoothly in 8 directions (or navigate menus) |
| **Mouse Cursor** | Aim your shots / click menu buttons |
| **Left Mouse Button (LMB)** | Shoot (hold or click to fire toward cursor) |
| **H / E / Right Mouse Button** | Eat a pizza slice (+8 HP) |
| **F5** | Quick-save your current run |
| **M** | Save run & return to Starter Menu |
| **R / Enter** | Restart after a run ends |
| **ESC** | Save & Quit |

## Starter Menu, Accounts & Save/Load

- **Starter Menu**: Choose **Play**, **Settings**, or **Quit** with the mouse or keyboard.
- **Login / Sign Up** (button in the **bottom-right** of the Starter Menu, or press **L**):
  - **Sign Up** creates a new account in the SQLite database `accounts.db` (passwords are stored hashed).
  - **Log In** loads that account's saved run, best score, highest floor, and settings.
  - **Test account: `admin` / `admin`** has full progress: best score 9999, a ready-to-load Floor 5 save,
    and every new game starts with the Pizza Cutter, Heat-Shield Apron and 35 HP.
  - Beating the Giant Calzone once unlocks the same "full progress" start gear on your own account.
  - Without logging in you play as **Guest** (saved to `savegame.json` on this computer).
- **Play Menu**: Choose **Load Saved Game** (continues your auto-saved or F5-saved run) or **Start New Game**.
- **Settings Menu**: Change the **Window Resolution** and **Graphics Quality** (`Low`, `Medium`, `High`). Saved per account.

## How the game works

- **Isaac-style Rooms & Doors**: One room fills the screen, completely lit up so you can see the whole room clearly. When you enter a room with enemies, the doors lock until you defeat all enemies in that room.
- **Minimap**: The side panel shows a map of the rooms you've explored, plus neighboring rooms (`$` = Supply/Treasure Room, `B` = Boss Room).
- **Floor Guardians & Delivery Hatch**: Defeating the boss room on Floors 1–4 opens the yellow **delivery hatch** to the next floor. On Floor 5, the **Giant Calzone** awaits!
- **Permadeath**: If your HP hits 0, the run is over and you start a fresh station layout on Floor 1.

| Monster | What it does |
|---|---|
| Mutant Meatball | Wobbles and chases you across the room |
| Rogue Delivery Drone | Hovers at range and fires laser bolts |
| Alien Anchovy | Stalks you and lunges at high speed |
| Giant Calzone (Floor 5 Boss) | Fires 3-way spreads of molten cheese and spits out meatballs |

| Item | Effect |
|---|---|
| Pizza Slice | Stored; press H or Right-Click to heal (+8 HP) |
| Oxygen Tank | +5 Max HP (and heals 5 HP) |
| Rolling Pin | +2 shot damage and faster firing |
| Pizza Cutter | +4 shot damage and rapid spinning cutter discs |
| Heat-Shield Apron | +2 defense (reduces damage taken) |
| Mars Credits | Score |

## Project files

| File | What's inside |
|---|---|
| `main.py` | 60 FPS window, room & minimap drawing, keyboard + mouse input |
| `game.py` | Real-time game rules: movement, shooting, room locking, monster AI, save/load |
| `database.py` | SQLite account database: sign up, log in, saved runs, stats, admin account |
| `dungeon.py` | Isaac-style connected room generator, doors, obstacles |
| `entities.py` | Player, Monster, and Projectile classes |
| `items.py` | Item definitions |
| `sprites.py` | All 16x16 pixel art sprites, floors, walls, doors, and counters |
| `settings.py` | Tweakable numbers (window size, speeds, HP, cooldowns) |
| `tests/test_game.py` | Automatic tests, including a real-time robot that plays 60 games |
| `PROGRESS_LOG.txt` | Development diary |

## Run the tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```
