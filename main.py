import pygame
import random

#class definition
class Character:
    def __init__(self, name):
        self.name = name
        self.room = None #applied in randomizer if murderer
        self.weapon = None #applied in randomizer if murderer
        self.is_murderer = False #applied in randomizer
        self.position = None #coordinates or board indexes can be added later with sese coordination
        
    def move_to_room(self, room):
        """Move a character to a room"""
        self.room = room

    def is_in_room(self, room):
        """Return true if a character is in a room, false otherwise"""
        return self.room == room

    def init_murderer(self, is_murder = True):
        """Initialise a character as the murderer"""
        self.is_murderer = is_murder

    def setposition(self, position):
        self.position = position

    def describe_state(self):
        """Describe a character's state"""
        room_name = self.room.name if self.room else "No room"
        weapon_name = self.weapon.name if self.weapon else "No weapon"
        print(f"Character: {self.name:<10} Room: {room_name:<12} "
              f"Weapon: {weapon_name:<10} "
              f"Murderer: {self.is_murderer}")


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

    def add_character_into_room(self, character):
        """Add a character into a room"""

    def list_rooms(self):
        """List all the rooms"""

    def list_characters_in_room(self, room_name):
        """List characters in a given room"""

    def move_weapon_between_room(self,new_room_name):
        """Move weapon from the current room to the new room"""

    def place_weapon_in_room(self, weapon, room_name):
        """Place a weapon in a room"""

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

#Create 9 room assets and the weapon assets and store them in a list
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

#User must pick character before all below, take the input and then assign below
#Take input from user
#Assign Character to user, set all else characters to CPU, set is_murderer to True
#Assign Here pls whit

#########################################

# Print the character list to the user
print("Choose your character:")
for i, char in enumerate(characters):
    print(f"{i + 1}. {char.name}")

#Take input from user (also handles checks)
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

# Assign chosen character to user
player = Player(isCPU = False, character = user_character)
print(f"You picked {user_character.name} as your character!")

#Assign the other characters to CPUs
cpu_players = []
for character in characters:
    if character != user_character:
        cpu_players.append(Player(isCPU = True, character = character))

#########################################

#Pick a random character and assign them as the murderer
murderer = random.choice(characters)
murderer.init_murderer(True)

# Assign every character to a random room
for character in characters:
    room = random.choice(rooms)
    character.move_to_room(room)
    room.characters.append(character)

#Uncomment for debug
# for character in characters:
    # character.describe_state()

#Add for later: User to see if his role is murderer or other role.
