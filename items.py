"""All the items the chef can find on the station."""

ITEM_TYPES = {
    "pizza":       {"name": "Pizza Slice",       "sprite": "pizza",       "kind": "consumable"},
    "oxygen":      {"name": "Oxygen Tank",       "sprite": "oxygen",      "kind": "maxhp", "amount": 5},
    "rolling_pin": {"name": "Rolling Pin",       "sprite": "rolling_pin", "kind": "weapon", "attack": 2},
    "cutter":      {"name": "Pizza Cutter",      "sprite": "cutter",      "kind": "weapon", "attack": 4},
    "apron":       {"name": "Heat-Shield Apron", "sprite": "apron",       "kind": "armor", "defense": 2},
    "credits":     {"name": "Mars Credits",      "sprite": "credits",     "kind": "credits"},
}


class Item:
    def __init__(self, key, x, y, amount=1):
        self.key = key
        self.x, self.y = x, y
        self.amount = amount          # only used for credits
        self.name = ITEM_TYPES[key]["name"]
        self.sprite = ITEM_TYPES[key]["sprite"]
