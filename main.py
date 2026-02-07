class Character:
    """Character class"""
    def __init__(self, name):
        self.name = name
        self.room = None
        self.weapon = None
        self.is_murderer = False

    def move_to_room(self, room):
        """Move a character to a room"""
        self.room = room

    def is_in_room(self, room):
        """Check if a character is in a room"""
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

