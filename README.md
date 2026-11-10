# Pizza Station Ares 🍕🚀

A turn-based **roguelike** set in a pizzeria on Mars, made with **Python 3** and **Pygame-CE**.

The year is 2097. Your Martian pizzeria has been overrun by mutant meatballs,
rogue delivery drones and alien anchovies. Fight your way down 5 floors and
defeat the **Giant Calzone**!

## How to run

```bash
# one-time setup (already done on this PC)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# play
.venv/bin/python main.py
```

## Controls

| Key | Action |
|---|---|
| Arrows / WASD | Move (walk into a monster to attack it) |
| Q E Z C | Move diagonally |
| H | Eat a pizza slice (+8 HP) |
| SPACE | Wait one turn |
| R | Restart after a run ends |
| ESC | Quit |

## The rules

- **Turn-based**: every time you act, all monsters act once.
- **Procedural levels**: every floor is randomly generated.
- **Permadeath**: if you die, the run is over and you start again from floor 1.
- Step on the yellow **delivery hatch** to go down a floor.

| Monster | What it does |
|---|---|
| Mutant Meatball | Weak and clumsy, wanders around |
| Rogue Delivery Drone | Fast: moves 2 tiles per turn |
| Alien Anchovy | Tough, chases you once it sees you |
| Giant Calzone (boss) | Very strong, spits out meatballs |

| Item | Effect |
|---|---|
| Pizza Slice | Stored; press H to heal |
| Oxygen Tank | +5 max HP |
| Rolling Pin / Pizza Cutter | +2 / +4 attack |
| Heat-Shield Apron | +2 defense |
| Mars Credits | Score |

## Project files

| File | What's inside |
|---|---|
| `main.py` | Window, drawing and keyboard input |
| `game.py` | The game rules: turns, combat, items, monster AI |
| `dungeon.py` | Random level generator and field of view |
| `entities.py` | Player and monster stats |
| `items.py` | Item definitions |
| `sprites.py` | All the pixel art (16x16, drawn as letter grids) |
| `settings.py` | Numbers you can tweak (window size, HP, ...) |
| `tests/test_game.py` | Automatic tests, including a robot that plays 150 games |
| `PROGRESS_LOG.txt` | Development diary |

## Run the tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```
