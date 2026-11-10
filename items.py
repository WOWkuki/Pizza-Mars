"""All the items the chef can find on Pizza Station Ares."""

ITEM_TYPES = {
    "pizza":       {"name": "Pizza Slice",       "sprite": "pizza",       "kind": "consumable"},
    "oxygen":      {"name": "Oxygen Tank",       "sprite": "oxygen",      "kind": "maxhp", "amount": 5},
    "rolling_pin": {"name": "Rolling Pin",       "sprite": "rolling_pin", "kind": "weapon", "attack": 2, "cooldown": 0.23},
    "cutter":      {"name": "Pizza Cutter",      "sprite": "cutter",      "kind": "weapon", "attack": 4, "cooldown": 0.18},
    "apron":       {"name": "Heat-Shield Apron", "sprite": "apron",       "kind": "armor", "defense": 2},
    "credits":     {"name": "Mars Credits",      "sprite": "credits",     "kind": "credits"},
}


class Item:
    """An item lying on the floor of a room at pixel position (x, y)."""

    def __init__(self, key, x, y, amount=1):
        self.key = key
        self.x = float(x)
        self.y = float(y)
        self.amount = amount          # only used for credits
        self.name = ITEM_TYPES[key]["name"]
        self.sprite = ITEM_TYPES[key]["sprite"]
