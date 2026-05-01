import unittest
import random

from main import make_suggestion, Player, Asset, Weapon, Room, Character, Envelope

class TestSuggestions(unittest.TestCase):
    def setUp(self):
        # similar to main.setup_game, creates a list of Character, Room, and Weapon objects
        self.characters = [Character(n) for n
                  in ["Scarlet",
                      "Plum",
                      "Mustard",
                      "Peacock",
                      "Green",
                      "White"]]
        self.rooms = [Room(n) for n
                in ["Study",
                    "Hall",
                    "Lounge",
                    "Library",
                    "Billiard Room",
                    "Dining Room",
                    "Conservatory",
                    "Ballroom",
                    "Kitchen"]]
        self.weapons = [Weapon(n) for n
                in ["Candlestick",
                    "Dagger",
                    "Revolver",
                    "Rope",
                    "Lead Pipe",
                    "Wrench"]]

        #setting player list, this assumes 6 players
        self.all_players = [Player(False, n) for n in self.characters]

        # creating Envelope object
        self.envelope = Envelope()
        # filling envelope with Scarlet, Rope, and Dining Room
        self.envelope.set_envelope(self.characters[0], self.weapons[3], self.rooms[5])

        # assigning pre-determined cards to each player
        self.all_players[0].hand = [self.characters[1], self.rooms[8], self.rooms[0]] # Plum, Kitchen, Study
        self.all_players[1].hand = [self.characters[2], self.weapons[0], self.rooms[7]] # Mustard, Candlestick, Ballroom
        self.all_players[2].hand = [self.weapons[1], self.rooms[2], self.weapons[5]] # Dagger, Lounge, Wrench
        self.all_players[3].hand = [self.characters[4], self.rooms[4], self.rooms[3]] # Green, Billiard Room, Library
        self.all_players[4].hand = [self.characters[3], self.weapons[2], self.rooms[6]] # Peacock, Revolver, Conservatory
        self.all_players[5].hand = [self.characters[5], self.weapons[4], self.rooms[1]] # White, Lead Pipe, Hall

    """
    test to ensure suggestions are disproved when a matching card is found, and that the response is clockwise from the suggester

    in this test, the player after Scarlet is Plum: Plum has a matching card (Candlestick - self.weapons[0]) so make_suggestion(...) 
    should return Candlestick, "Plum"
    """
    def test_suggestion_disproven(self):
        # Scarlet makes the suggestion Plum, Study, Candlestick
        result, displayer = make_suggestion(self.all_players[0], self.rooms[0].name, self.all_players[1].character, self.weapons[0], self.all_players)
        # Expect to see Candlestick (i.e. self.weapons[0] returned, as it is the first matching card)
        self.assertEqual(result, self.weapons[0])
        self.assertEqual(displayer.character.name, "Plum")
    
    """
    test to check make_suggestion(...) returns None when suggestion == envelope
    """
    def test_suggestion_proven(self):
        # Scarlet makes the suggestion Scarlet, Rope, Dining Room
        # parameters passed are Scarlet (Player object), Dining Room (String), Scarlet (Character object), Rope (Weapon object), list of all Player objects
        result, displayer = make_suggestion(self.all_players[0], self.rooms[5].name, self.all_players[0].character, self.weapons[3], self.all_players)
        self.assertIsNone(result)
        self.assertIsNone(displayer)