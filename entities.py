"""The chef (player), monsters, and projectiles for real-time combat."""

from items import ITEM_TYPES
from settings import PLAYER_HP, PLAYER_ATTACK, PLAYER_SPEED, FIRE_COOLDOWN

MONSTER_TYPES = {
    "meatball": {
        "name": "Mutant Meatball",
        "hp": 9,
        "attack": 3,
        "defense": 0,
        "speed": 95.0,
        "radius": 15.0,
        "ai": "wander_chase",
        "credits": (1, 3),
    },
    "drone": {
        "name": "Rogue Delivery Drone",
        "hp": 8,
        "attack": 3,
        "defense": 0,
        "speed": 135.0,
        "radius": 14.0,
        "ai": "shooter",
        "credits": (2, 4),
    },
    "anchovy": {
        "name": "Alien Anchovy",
        "hp": 13,
        "attack": 4,
        "defense": 1,
        "speed": 130.0,
        "radius": 15.0,
        "ai": "lunge",
        "credits": (3, 6),
    },
    "calzone": {
        "name": "Giant Calzone",
        "hp": 90,
        "attack": 6,
        "defense": 1,
        "speed": 85.0,
        "radius": 24.0,
        "ai": "boss",
        "credits": (50, 50),
    },
}

DEATH_TEXT = {
    "meatball": "splatters into tomato sauce",
    "drone": "sparks and crashes",
    "anchovy": "flops over, defeated",
    "calzone": "bursts open in a cloud of molten cheese",
}


class Entity:
    def __init__(self, x, y, sprite, name, hp, radius=14.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.radius = float(radius)
        self.sprite = sprite
        self.name = name
        self.hp = self.max_hp = int(hp)
        self.hit_flash = 0.0      # seconds remaining of white damage flash

    @property
    def alive(self):
        return self.hp > 0


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, "chef", "Chef", PLAYER_HP, radius=14.0)
        self.speed = PLAYER_SPEED
        self.base_attack = PLAYER_ATTACK
        self.base_defense = 0
        self.weapon = None        # key from ITEM_TYPES, e.g. "cutter"
        self.armor = None
        self.pizzas = 1           # start with one slice
        self.credits = 0
        self.kills = 0
        self.fire_timer = 0.0
        self.iframe_timer = 0.0   # brief invincibility after taking a hit
        self.aim_angle = 0.0
        self.moving = False
        self.walk_timer = 0.0
        self.recoil_timer = 0.0   # weapon kickback animation timer
        self.muzzle_timer = 0.0   # muzzle flash animation timer

    @property
    def held_weapon_sprite(self):
        if self.weapon == "cutter":
            return "weapon_cutter"
        if self.weapon == "rolling_pin":
            return "weapon_rolling_pin"
        return "weapon_blaster"

    @property
    def attack(self):
        bonus = ITEM_TYPES[self.weapon]["attack"] if self.weapon else 0
        return self.base_attack + bonus

    @property
    def defense(self):
        bonus = ITEM_TYPES[self.armor]["defense"] if self.armor else 0
        return self.base_defense + bonus

    @property
    def fire_cooldown(self):
        if self.weapon and "cooldown" in ITEM_TYPES[self.weapon]:
            return ITEM_TYPES[self.weapon]["cooldown"]
        return FIRE_COOLDOWN

    @property
    def shot_kind(self):
        if self.weapon == "cutter":
            return "cutter"
        if self.weapon == "rolling_pin":
            return "spice"
        return "dough"


class Monster(Entity):
    def __init__(self, x, y, kind, floor_bonus=0, summoned=False, mini_boss=False):
        t = MONSTER_TYPES[kind]
        hp = t["hp"] + floor_bonus * 2
        radius = t["radius"]
        name = t["name"]
        if mini_boss and kind != "calzone":
            hp = int(hp * 1.8) + 6
            radius += 4.0
            name = f"Alpha {name}"
        super().__init__(x, y, kind, name, hp, radius=radius)
        self.kind = kind
        self.attack = t["attack"] + floor_bonus // 2 + (1 if mini_boss else 0)
        self.defense = t["defense"]
        self.speed = t["speed"]
        self.ai = t["ai"]
        self.credits = (0, 1) if summoned else t["credits"]
        self.summoned = summoned
        self.mini_boss = mini_boss
        self.timer = 0.0          # general AI timer (wander/lunge/boss patterns)
        self.shot_timer = 1.1     # cooldown before next ranged attack
        self.wander_angle = 0.0


class Projectile:
    """A flying shot (dough ball, cutter blade, drone laser, or molten cheese)."""

    def __init__(self, x, y, vx, vy, damage, from_player, kind="dough", radius=6.0, owner_name=""):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.damage = int(damage)
        self.from_player = bool(from_player)
        self.kind = kind
        self.radius = float(radius)
        self.owner_name = owner_name
        self.lifetime = 2.2       # seconds before disappearing
        self.age = 0.0
