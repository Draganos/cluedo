import random

class Character:
    def __init__(self, name):
        self.name = name
        self.room = None  # applied in randomizer if murderer
        self.weapon = None  # applied in randomizer if murderer
        self.position = None  # coordinates or board indexes can be added later with sese coordination

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
    player = Player(isCPU=False, character=user_character)
    player = Player(isCPU=False, character=user_character)
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

def suggestion(player, room, characters, weapons, all_players):
    print(f"\nYou are in {room.name}")

    suspect = random.choice(characters)
    weapon = random.choice(weapons)

    print(f"Suggestion: {suspect.name} in {room.name} with {weapon.item_name}")

    # Move the suggested suspect into the room
    suspect.room = room
    start_index = all_players.index(player)

    for i in range(1, len(all_players)):
        other = all_players[(start_index + i) % len(all_players)]

        # Find matching cards
        matches = []
        for card in other.hand:
            if isinstance(card, Character) and card.name == suspect.name:
                matches.append(card)
            elif isinstance(card, Weapon) and card.item_name == weapon.item_name:
                matches.append(card)
            elif isinstance(card, Room) and card.name == room.name:
                matches.append(card)
        if matches:
            shown = random.choice(matches)
            print(f"{other.character.name} shows you a card.")

            return shown
    print("No player could show you a card.")
    return None

def round(player, room, characters, weapons, all_players):
    # TODO - round initialisation, ideally functions in the game loop but main itself does not loop
    # Should be called with each new round (a round is considered complete once all players have taken a turn)
    # could also potentially be a class (with turn as a function/subroutine) but that's long
    # for i in queue { call turn(i) }
    # when receiving some special note, queue is updated
    return None

def turn(player, room, characters, weapons, all_players):
    # TODO
    # This is a player's turn (NOT A ROUND)
    # variable 'player' should receive whatever correct player is needed for their turn
    # player turn consists of 1) dice roll, 2) suggestion (already done), 3) end turn OR accusation
    # if turn ends with accusation and accusation FALSE, return some special note that removes the player from the queue
    return None

if __name__ == "__main__":
    selected_character = "Scarlet"
    player, cpu_players, rooms, weapons, characters, envelope = setup_game(selected_character)
    all_players = [player] + cpu_players
    test_room = rooms[0]
    suggestion(player, test_room, characters, weapons, all_players)

