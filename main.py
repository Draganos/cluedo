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

#Initializing the game

#Create 6 character objects and store them in a list
scarlet = Character("Scarlet")
plum = Character("Plum")
mustard = Character("Mustard")
peacock = Character("Peacock")
green = Character("Green")
white = Character("White")
characters = [scarlet,
              plum,
              mustard,
              peacock,
              green,
              white]

#Create 9 room assets and store them in a list
study = Room("Study")
hall = Room("Hall")
lounge = Room("Lounge")
library = Room("Library")
billard_room = Room("Billard Room")
dining_room = Room("Dining Room")
conservatory = Room("Conservatory")
ballroom = Room("Ballroom")
kitchen = Room("Kitchen")
rooms = [study,
         hall,
         lounge,
         library,
         billard_room,
         dining_room,
         conservatory,
         ballroom,
         kitchen]

# Create 9 weapon assets and store them in a list
candlestick = Weapon("Candlestick")
knife = Weapon("Knife")
revolver = Weapon("Revolver")
rope = Weapon("Rope")
lead_pipe = Weapon("Lead Pipe")
wrench = Weapon("Wrench")
weapons = [candlestick,
           knife,
           revolver,
           rope,
           lead_pipe,
           wrench]

# Show the character list to the human player
print("Choose your character:")
for i, char in enumerate(characters):
    print(f"{i + 1}. {char.name}")

# Take user input
while True:
    try:
        choice = int(input("Enter the number of your character: ")) - 1
        if 0 <= choice < len(characters):
            user_character = characters[choice]
            break
        else:
            print("Invalid number, try again!")
    except ValueError:
        print("Please enter a valid number!")

# Assign chosen character to human player
player = Player(isCPU = False, character = user_character)
print(f"\nYou've picked {user_character.name} as your character!\n")

# Assign the other characters to CPU players
cpu_players = []
for character in characters:
    if character != user_character:
        cpu_players.append(Player(isCPU = True, character = character))

# Create an envelope object
envelope = Envelope()

# Envelope randomly picks a character, weapon and room from list
envelope.set_envelope(
    random.choice(characters),
    random.choice(weapons),
    random.choice(rooms)
)

# Show envelope contents
envelope.show_contents()

# Create the board object
board = Board(rooms)

# Randomly shuffle characters and weapons
random.shuffle(characters)
random.shuffle(weapons)

# Randomly select 6 rooms for the characters
character_rooms = random.sample(rooms, len(characters))
for char, room in zip(characters, character_rooms):
    board.add_character_to_room(char, room)

# Randomly select 6 rooms for the weapons
weapon_rooms = random.sample(rooms, len(weapons))
for weapon, room in zip(weapons, weapon_rooms):
    board.add_weapon_to_room(weapon, room)

# Print board state (FOR DEBUGGING PURPOSES ONLY)
print("\nBoard state after randomisation:")
for room in rooms:
    character_names = [c.name for c in room.characters] if room.characters else ["None"]
    weapon_names = [w.item_name for w in room.weapons] if room.weapons else ["None"]
    print(f"{room.name:<15} | Characters: {character_names} | Weapons: {weapon_names}")
