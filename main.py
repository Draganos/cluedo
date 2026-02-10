class Character:
    def __init__(self, name):
        self.name = name
        self.room = None #applied in randomizer if murderer
        self.weapon = None #applied in randomizer if murderer
        self.is_murderer = False #applied in randomizer
        self.is_CPU = False #applied after character is picked

    def move_to_room(self, room):
        """Move a character to a room"""
        self.room = room

    def is_in_room(self, room):
        """Return true if a character is in a room, false otherwise"""
        return self.room == room

    def init_murderer(self, is_murder = True):
        """Initialise a character as the murderer"""
        self.is_murderer = is_murder

    def describe_state(self):
        """Describe a character's state"""
        if self.room:
            room_name = self.room.name
        else:
            room_name = "No room"
        if self.weapon:
            weapon_name = self.weapon.name
        else:
            weapon_name = "No weapon"
        print(f"{self.name}: Room = {room_name}, "
              f"Weapon = {weapon_name}, "
              f"Murderer = {self.is_murderer}")


class Room:
    def __init__(self, name):
        self.name = name
        self.characters = []
        self.weapons = []

class Board:
    def __init__(self, rooms):
        self.rooms = rooms

    def list_rooms(self):
        """List all rooms"""

    def place_weapon(self, weapon, room_name):
        """Place a weapon in a room"""

    def list_weapons_in_room(self, room_name):
        """List all weapons in a room"""

    def describe_room_contents(self, room_name):
        """Describe a room's contents (characters + weapons)"""

class Item:
    def __init__(self, item_name, item_type):
        self.item_name = item_name
        self.item_type = item_type


