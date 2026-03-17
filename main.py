import random

class Character:
    def __init__(self, name):
        self.name = name
        self.room = None #applied in randomizer if murderer
        self.weapon = None #applied in randomizer if murderer
        self.position = None #coordinates or board indexes can be added later with sese coordination
        
    def move_to_room(self, room):
        """Move a character to a room"""
        self.room = room

    def is_in_room(self, room):
        """Return true if a character is in a room, false otherwise"""
        return self.room == room

    def setposition(self, position):
        self.position = position

    def describe_state(self):
        """Describe a character's state"""
        room_name = self.room.name if self.room else "No room"
        weapon_name = self.weapon.name if self.weapon else "No weapon"
        print(f"Character: {self.name:<10} Room: {room_name:<12} "
              f"Weapon: {weapon_name:<10} ")

class Room:
    def __init__(self, name):
        self.name = name
        self.characters = []
        self.weapons = []

class Board:
    def __init__(self, rooms):
        self.rooms = rooms
        self.characters = [] #add all characters in this room via list
        self.weapons = [] #append all weapons in this room via list for referencing later OOP-style

    def move_character_to_square(self, character, position):
        """Move a character to a valid square"""

    def add_character_to_room(self, character, room):
        """Add a character into a room"""
        if character.room:
            character.room.characters.remove(character)
        character.room = room
        room.characters.append(character)

    def add_weapon_to_room(self, weapon, room):
        """Add a weapon into a room"""
        if weapon.room:
            weapon.room.weapons.remove(weapon)
        weapon.room = room
        room.weapons.append(weapon)

    def list_rooms(self):
        """List all the rooms"""

    def list_characters_in_room(self, room_name):
        """List characters in a given room"""

    def move_weapon_between_room(self,new_room_name):
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
        self.room = None #as weapon must be in one room or not assigned 
        
class Envelope:
    def __init__(self):
        self.character = None
        self.weapon = None
        self.room = None

    def set_envelope(self, character, weapon, room):
        self.character = character
        self.weapon = weapon
        self.room = room

    def show_contents(self):
        """Show the contents of the envelope"""
        char_name = self.character.name if self.character else "None"
        weapon_name = self.weapon.item_name if self.weapon else "None"
        room_name = self.room.name if self.room else "None"
        print(f"Envelope Contents: Character: {char_name}, "
              f"Weapon: {weapon_name}, "
              f"Room: {room_name}")

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
        #for initializing the game rounds later. 

class Player:
    def __init__(self, isCPU=False, character=None):
        self.isCPU = isCPU #set to none if not user.
        self.character = character
        self.hand = []

    def show_hand(self):
        """Show all the character's hand"""
        return [c.name if isinstance(c, Character) or isinstance(c, Room)
                else c.item_name for c in self.hand]

# Game initialisation

def setup_game(selected_character_name):
    # Create 6 character objects
    scarlet = Character("Scarlet")
    plum = Character("Plum")
    mustard = Character("Mustard")
    peacock = Character("Peacock")
    green = Character("Green")
    white = Character("White")
    characters = [scarlet, plum, mustard, peacock, green, white]

    # Create rooms
    study = Room("Study")
    hall = Room("Hall")
    lounge = Room("Lounge")
    library = Room("Library")
    billiard_room = Room("Billiard Room")
    dining_room = Room("Dining Room")
    conservatory = Room("Conservatory")
    ballroom = Room("Ballroom")
    kitchen = Room("Kitchen")
    rooms = [study, hall, lounge, library, billiard_room, dining_room,
             conservatory, ballroom, kitchen]

    # Create weapons
    candlestick = Weapon("Candlestick")
    knife = Weapon("Knife")
    revolver = Weapon("Revolver")
    rope = Weapon("Rope")
    lead_pipe = Weapon("Lead Pipe")
    wrench = Weapon("Wrench")
    weapons = [candlestick, knife, revolver, rope, lead_pipe, wrench]

    # Assign selected character to human player
    user_character = next(c for c in characters if c.name == selected_character_name)
    player = Player(isCPU=False, character=user_character)

    # Assign CPU players
    cpu_players = [Player(isCPU=True, character=c) for c in characters if c != user_character]
    # Create an envelope object
    envelope = Envelope()

    # Envelope randomly picks the solution
    envelope.set_envelope(
        random.choice(characters),
        random.choice(weapons),
        random.choice(rooms)
    )

    # Show the envelope contents
    envelope.show_contents()

    # Create the board object
    board = Board(rooms)

    # Randomly shuffle characters and weapons
    random.shuffle(characters)
    random.shuffle(weapons)

    # Randomly places the characters in 6 rooms
    character_rooms = random.sample(rooms, len(characters))
    for char, room in zip(characters, character_rooms):
        board.add_character_to_room(char, room)

    # Randomly places the weapons in 6 rooms
    weapon_rooms = random.sample(rooms, len(weapons))
    for weapon, room in zip(weapons, weapon_rooms):
        board.add_weapon_to_room(weapon, room)

    # Initialise list, loop through each card and add those not in envelope
    remaining_characters = []
    for c in characters:
        if c != envelope.character:
            remaining_characters.append(c)

    remaining_weapons = []
    for w in weapons:
        if w != envelope.weapon:
            remaining_weapons.append(w)

    remaining_rooms = []
    for r in rooms:
        if r != envelope.room:
            remaining_rooms.append(r)

    #Combine remaining cards into a single deck
    deck = remaining_characters + remaining_weapons + remaining_rooms

    # Shuffle the deck
    random.shuffle(deck)

    # Combine player and CPU players
    all_players = [player] + cpu_players

    # For loop to deal cards to human player and CPU players
    for i, card in enumerate(deck):
        all_players[i % len(all_players)].hand.append(card)

        return player, cpu_players, board, envelope, characters, weapons, rooms



