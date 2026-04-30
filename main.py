import random

class Character:
    def __init__(self, name):
        self.name = name
        self.room = None  # applied in randomizer if murderer
        self.weapon = None  # applied in randomizer if murderer
        self.position = None  # coordinates added later with sese coordination on gridmovement

class Room:
    def __init__(self, name):
        self.name = name
        self.characters = []
        self.weapons = []

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

class Player:
    def __init__(self, isCPU=False, character=None):
        self.isCPU = isCPU  # set to none if not user.
        self.character = character
        self.hand = []
        self.is_eliminated = False #check if CPU has been eliminated from the game.


        #Tracks what cards each player has seen.
        self.known_cards = set()

def setup_game(selected_character_name):
    """
    Initialises game state for GridMovement.py.

    :param selected_character_name: The name of the character chosen by the player
    :type selected_character_name: str
    :return: The player, CPU players, rooms, weapons, characters, and envelope
    :rtype: tuple
    """
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
                   "Dagger",
                   "Revolver",
                   "Rope",
                   "Lead Pipe",
                   "Wrench"]]

    # Assign human player and CPU players
    user_character = next(c for c in characters if c.name == selected_character_name)
    player = Player(isCPU=False, character=user_character)
    cpu_players = [Player(isCPU=True, character=c) for c in characters if c != user_character]

    # Create the envelope
    envelope = Envelope()
    envelope.set_envelope(random.choice(characters),
                          random.choice(weapons),
                          random.choice(rooms))

    # Shuffle and deal remaining cards
    remaining_chars = [c for c in characters if c != envelope.character]
    remaining_weapons = [w for w in weapons if w != envelope.weapon]
    remaining_rooms = [r for r in rooms if r != envelope.room]
    all_players = [player] + cpu_players
    deck = remaining_chars + remaining_weapons + remaining_rooms
    random.shuffle(deck)
    for i, card in enumerate(deck):
        receiver = all_players[i % len(all_players)]
        receiver.hand.append(card)
        receiver.known_cards.add(card)
    return player, cpu_players, rooms, weapons, characters, envelope

def make_suggestion(player, room_name, suspect, weapon, all_players):
    """
       Processes a player's suggestion and checks if any other player can disprove it.

       :param player: The player making the suggestion
       :type player: Player
       :param room_name: The name of the suggested room
       :type room_name: str
       :param suspect: The suggested character
       :type suspect: Character
       :param weapon: The suggested weapon
       :type weapon: Weapon
       :param all_players: List of all players in the game
       :type all_players: list
       :return: A tuple containing the shown card and the player who revealed it,
                if no player can disprove the suggestion
       :rtype: tuple
       """

    start_index = all_players.index(player) 
    for i in range(1, len(all_players)):
        other = all_players[(start_index + i) % len(all_players)]

        matching_cards = []

        for card in other.hand:
            if isinstance(card, Character) and card.name == suspect.name:
                matching_cards.append(card)
            elif isinstance(card, Weapon) and card.item_name == weapon.item_name:
                matching_cards.append(card)
            elif isinstance(card, Room) and card.name == room_name:
                matching_cards.append(card)

        if matching_cards:
            shown_card = random.choice(matching_cards)
            return shown_card, other
    return None, None

def accusation(player, all_players):
    accusations = {"character": None, "weapon": None, "room": None}

    char_list = ["scarlet", "plum", "mustard", "white", "peacock", "green"]
    weap_list = ["candlestick", "dagger", "pistol", "rope", "lead pipe", "wrench"]
    room_list = ["study", "hall", "lounge", "library", "billiard room",
                 "dining room", "conservatory", "ballroom", "kitchen"]

    accused = input("Who do you accuse?: ").lower()
    while accused not in char_list:
        #print("Suspect must be one of: Scarlet, Plum, Mustard, White, Peacock, Green.")
        accused = input("Who do you accuse?: ").lower()
    accusations["character"] = accused.capitalize()

    weapon = input("What did they use to carry out the murder?: ").lower()
    while weapon not in weap_list:
        #print("Weapon must be one of: Candlestick, Dagger, Pistol, Rope, Lead Pipe, Wrench.")
        weapon = input("What did they use to carry out the murder?: ").lower()
    accusations["weapon"] = weapon.capitalize()

    location = input("Where was the murder committed?: ").lower()
    while location not in room_list:
        #print(
        #    "Room must be one of: Study, Hall, Lounge, Library, Billiard Room, Dining Room, Conservatory, Ballroom, Kitchen.")
        location = input("Where was the murder committed?: ").lower()
    accusations["room"] = location.capitalize()

    # print(f"{player.character.name} has accused {accusations["character"]} of using the {accusations["weapon"]} to murder Black in the {accusations["room"]}.")


if __name__ == "__main__":
    selected_character = "Scarlet"
    player, cpu_players, rooms, weapons, characters, envelope = setup_game(selected_character)
    all_players = [player] + cpu_players
    queue = all_players
    eliminated = []  # keeps track of eliminated player objects
    test_room = rooms[0]
    # suggestion(player, test_room, characters, weapons, all_players)
    # game = True
    # while (game): # simulate game loop (REMOVE ONCE MAIN AND GRIDMOVEMENT ARE FULLY LINKED)
    #    game, queue = round(queue, test_room, characters, weapons, all_players)
