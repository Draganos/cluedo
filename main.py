import random
from GridMovement import Player as BoardPlayer

class Character:
    def __init__(self, name):
        self.name = name
        self.room = None  # applied in randomizer if murderer
        self.weapon = None  # applied in randomizer if murderer
        self.position = None  # coordinates or board indexes can be added later with sese coordination

    def move_to_room(self, room):
        """Move a character to a room"""

    def is_in_room(self, room):
        """Return true if a character is in a room, false otherwise"""

    def setposition(self, position):
        self.position = position

    def describe_state(self):
        """Describe a character's state"""

class Room:
    def __init__(self, name):
        self.name = name
        self.characters = []
        self.weapons = []

class Board:
    def __init__(self, rooms):
        self.rooms = rooms
        self.characters = []
        self.weapons = []

    def move_character_to_square(self, character, position):
        """Move a character to a valid square"""

    def add_character_to_room(self, character, room):
        """Add a character into a room"""

    def add_weapon_to_room(self, weapon, room):
        """Add a weapon into a room"""

    def list_rooms(self):
        """List all the rooms"""

    def list_characters_in_room(self, room_name):
        """List characters in a given room"""

    def move_weapon_between_room(self, new_room_name):
        """Move weapon from the current room to the new room"""

    def list_weapons_in_room(self, room_name):
        """List all weapons in a given room"""

    def get_room(self, room_name):
        """Return a room object by the given name"""

class Asset:
    def __init__(self, item_name, item_type):
        self.item_name = item_name
        self.item_type = item_type

class Weapon(Asset):
    def __init__(self, name):
        super().__init__(name, "weapon")
        self.room = None

class Envelope:
    def __init__(self):
        self.character = None
        self.weapon = None
        self.room = None

    def set_envelope(self, character, weapon, room):
        self.character = character
        self.weapon = weapon
        self.room = room

class Dice(Asset):
    def __init__(self, sides=6):
        super().__init__("Dice", "dice")
        self.sides = sides

    def roll(self):
        return random.randint(1, self.sides)

class Game:
    def __init__(self, board, characters, weapons, envelope, dice):
        self.board = board
        self.characters = characters
        self.weapons = weapons
        self.envelope = envelope
        self.dice = dice
        self.current_turn = 0
        # for initializing the game rounds later.

class Player:
    def __init__(self, isCPU=False, character=None):
        self.isCPU = isCPU  # set to none if not user.
        self.character = character
        self.hand = []

    def show_hand(self):
        """Show all the character's hand"""
        return [c.name if isinstance(c, Character) or isinstance(c, Room)
                else c.item_name for c in self.hand]

def setup_game(selected_character_name):

    print("Setting up game...")
    characters = [Character(n) for n
                  in ["Scarlet",
                      "Plum",
                      "Mustard",
                      "Peacock",
                      "Green",
                      "White"]]
    rooms = [Room(n) for n
             in ["Study",
                 "Hall",
                 "Lounge",
                 "Library",
                "Billiard Room",
                "Dining Room",
                "Conservatory",
                "Ballroom",
                "Kitchen"]]
    weapons = [Weapon(n) for n
               in ["Candlestick",
                   "Knife",
                   "Revolver",
                   "Rope",
                   "Lead Pipe",
                   "Wrench"]]

    # Assign human player and CPU players
    user_character = next(c for c in characters if c.name == selected_character_name)
    player = BoardPlayer(isCPU=False, character=user_character)
    cpu_players = [Player(isCPU=True, character=c) for c in characters if c != user_character]

    # Create the envelope
    envelope = Envelope()
    envelope.set_envelope(random.choice(characters),
                          random.choice(weapons),
                          random.choice(rooms))
    print("Show envelope solution: ")
    print(f"Character: {envelope.character.name}, "
          f"Weapon: {envelope.weapon.item_name}, "
          f"Room: {envelope.room.name}")

    # Shuffle and deal remaining cards
    remaining_chars = [c for c in characters if c != envelope.character]
    remaining_weapons = [w for w in weapons if w != envelope.weapon]
    remaining_rooms = [r for r in rooms if r != envelope.room]

    deck = remaining_chars + remaining_weapons + remaining_rooms
    random.shuffle(deck)
    all_players = [player] + cpu_players
    for i, card in enumerate(deck):
        all_players[i % len(all_players)].hand.append(card)

    print("Game initialised...")
    return player, cpu_players, rooms, weapons, characters, envelope
