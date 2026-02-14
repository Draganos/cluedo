import pygame
import random

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
        return random.randomint(1, self.sides)

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

#Create 6 character objects and store them in a list
scarlet = Character("Scarlet")
plum = Character("Plum")
mustard = Character("Mustard")
peacock = Character("Peacock")
green = Character("Green")
characters = [scarlet,
              plum,
              mustard,
              peacock,
              green]

#Create 9 room objects and store them in a list
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

#Pick a random character and assign them as the murderer
murderer = random.choice(characters)
murderer.init_murderer(True)

# Assign every character to a random room
for character in characters:
    room = random.choice(rooms)
    character.move_to_room(room)
    room.characters.append(character)




