"""The chef (player) and the monsters."""

from items import ITEM_TYPES
from settings import PLAYER_HP, PLAYER_ATTACK

# Base stats. Monsters get a little stronger on deeper floors (see game.py).
MONSTER_TYPES = {
    "meatball": {"name": "Mutant Meatball", "hp": 5, "attack": 2, "defense": 0,
                 "speed": 1, "ai": "wander", "credits": (1, 3)},
    "drone":    {"name": "Rogue Delivery Drone", "hp": 4, "attack": 3, "defense": 0,
                 "speed": 2, "ai": "chase", "credits": (2, 4)},
    "anchovy":  {"name": "Alien Anchovy", "hp": 8, "attack": 3, "defense": 1,
                 "speed": 1, "ai": "chase", "credits": (3, 6)},
    "calzone":  {"name": "Giant Calzone", "hp": 40, "attack": 5, "defense": 2,
                 "speed": 1, "ai": "boss", "credits": (50, 50)},
}

DEATH_TEXT = {
    "meatball": "squishes into tomato sauce",
    "drone": "crashes and explodes",
    "anchovy": "flops over, defeated",
    "calzone": "bursts open in a cloud of molten cheese",
}


class Entity:
    def __init__(self, x, y, sprite, name, hp):
        self.x, self.y = x, y
        self.sprite = sprite
        self.name = name
        self.hp = self.max_hp = hp

    @property
    def alive(self):
        return self.hp > 0


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, "chef", "Chef", PLAYER_HP)
        self.base_attack = PLAYER_ATTACK
        self.base_defense = 0
        self.weapon = None    # key from ITEM_TYPES, e.g. "cutter"
        self.armor = None
        self.pizzas = 1       # start with one slice
        self.credits = 0
        self.kills = 0

    @property
    def attack(self):
        bonus = ITEM_TYPES[self.weapon]["attack"] if self.weapon else 0
        return self.base_attack + bonus

    @property
    def defense(self):
        bonus = ITEM_TYPES[self.armor]["defense"] if self.armor else 0
        return self.base_defense + bonus


class Monster(Entity):
    def __init__(self, x, y, kind, floor_bonus=0, summoned=False):
        t = MONSTER_TYPES[kind]
        super().__init__(x, y, kind, t["name"], t["hp"] + floor_bonus)
        self.kind = kind
        self.attack = t["attack"] + floor_bonus // 3
        self.defense = t["defense"]
        self.speed = t["speed"]
        self.ai = t["ai"]
        self.credits = (0, 1) if summoned else t["credits"]
        self.summoned = summoned
        self.alerted = False   # becomes True once it has seen the chef
        self.timer = 0         # used by the boss for its special attack
