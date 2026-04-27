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
                   "Dagger",
                   "Pistol",
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
    print(f"\nYou are {player.character.name} in {room.name}")

    #suspect = random.choice(list(set(characters)-set(eliminated)))
    suspect = random.choice(characters) #replaced above line with this such that game doesnt crash in gridmovement
    weapon = random.choice(weapons)

    print(f"Suggestion: {suspect.name} in {room.name} with {weapon.item_name}")

    active_players = list(set(all_players)-set(eliminated))

    # Move the suggested suspect into the room
    suspect.room = room
    start_index = active_players.index(player)

    for i in range(1, len(all_players)-len(eliminated)):
        other = active_players[(start_index + i) % len(active_players)]

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

""" - returns boolean (False means game ends) and queue (turn order of all non-eliminated players)"""
#def round(queue, room, characters, weapons, all_players): #####hashed as not usable in gridmovement architecture, left here for reference
#    # this function makes the assumption that it is called repeatedly in the game loop, which is effectively a while True loop
#    # this while True loop is simulated in main.py. I cannot stress this enough, that is solely for testing purposes and NOT TO BE IMPLEMENTED IN THE FINAL GAME
#    if len(all_players) > (len(eliminated)-3):
#        player_turn = queue[0]
#        queue = turn(queue[0], room, characters, weapons, all_players)
#        if player_turn in queue:
#            popped = queue.pop(0)
#            queue.append(popped)
#    else:
#        print("Winner is", list(set(all_players)-set(eliminated))[0].character.name)
#        return False, queue
#    return True, queue

"""This is a player's turn (NOT A ROUND)
    - variable 'player' should receive whatever correct player is needed for their turn
    - player turn consists of 1) dice roll, 2) suggestion (already done), 3) end turn OR accusation
    - if turn ends with accusation and accusation FALSE, removes the player from the queue
    - returns array of Player objects, all_players """

#below block is hashed as can cause crashes, new method under
#######def turn(player, room, characters, weapons, all_players):
#######    if player not in eliminated:
#######        print("You can move up to", roll_dice(player), "spaces.")
#######        suggestion(player, room, characters, weapons, all_players)
#######
#######        # end/accusation
#######        print("\nDebug notes: Accusation has been partially implemented, but always makes the assumption the accusation was incorrect. This is because no envelope with the correct cards have been determined afaik in main.py.\n")
#######        receive = input("End turn or make accusation? (Type 'End' to end turn, 'Accuse' to make accusation, case-insensitive).")
#######        if receive.lower() == "end":
#######            print("Ended turn.")
#######        else:
#######            print("Made an accusation.")
#######            accusation(player, all_players)
#######            # currently, the code makes the default assumption that all accusations are incorrect
#######            eliminated.append(player)
#######            #debug_elim = []
#######            #for i in eliminated:
#######            #debug_elim.append(i.character.name)
#######            #print(debug_elim)
#######            all_players.remove(player)
#######
#######    return all_players

def make_suggestion(player, room_name, suspect, weapon, all_players):
    print(f"{player.character.name} suggests:")
    print(f"{suspect.name} in the {room_name} with the {weapon.item_name}")

    for other in all_players:
        if other == player:
            continue

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
            print(f"{other.character.name} shows a card.")
            return shown_card

    print("the suggestion couldnt be disproved.")
    return None

def roll_dice(player):
    dice_roll = random.randint(2, 12) # randomly generate number between 2-12
    return dice_roll

def accusation(player, all_players):
    accusations = {"character": None, "weapon": None, "room": None}

    char_list = ["scarlet", "plum", "mustard", "white", "peacock", "green"]
    weap_list = ["candlestick", "dagger", "pistol", "rope", "lead pipe", "wrench"]
    room_list = ["study", "hall", "lounge", "library", "billiard room", 
                 "dining room", "conservatory", "ballroom", "kitchen"]
    
    accused = input("Who do you accuse?: ").lower()
    while accused not in char_list:
        print("Suspect must be one of: Scarlet, Plum, Mustard, White, Peacock, Green.")
        accused = input("Who do you accuse?: ").lower()
    accusations["character"] = accused.capitalize()

    weapon = input("What did they use to carry out the murder?: ").lower()
    while weapon not in weap_list:
        print("Weapon must be one of: Candlestick, Dagger, Pistol, Rope, Lead Pipe, Wrench.")
        weapon = input("What did they use to carry out the murder?: ").lower()
    accusations["weapon"] = weapon.capitalize()

    location = input("Where was the murder committed?: ").lower()
    while location not in room_list:
        print("Room must be one of: Study, Hall, Lounge, Library, Billiard Room, Dining Room, Conservatory, Ballroom, Kitchen.")
        location = input("Where was the murder committed?: ").lower()
    accusations["room"] = location.capitalize()

    #print(f"{player.character.name} has accused {accusations["character"]} of using the {accusations["weapon"]} to murder Black in the {accusations["room"]}.")

if __name__ == "__main__":
    selected_character = "Scarlet"
    player, cpu_players, rooms, weapons, characters, envelope = setup_game(selected_character)
    all_players = [player] + cpu_players
    queue = all_players 
    eliminated = [] # keeps track of eliminated player objects
    test_room = rooms[0]
    #suggestion(player, test_room, characters, weapons, all_players)
    #game = True
    #while (game): # simulate game loop (REMOVE ONCE MAIN AND GRIDMOVEMENT ARE FULLY LINKED)
    #    game, queue = round(queue, test_room, characters, weapons, all_players)
