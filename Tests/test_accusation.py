import unittest
from unittest.mock import Mock
import pygame
from GridMovement import AccuseMenu

class TestAccuseMenu(unittest.TestCase):

    def test_correct_accusation(self):
        pygame.init()
        menu = AccuseMenu(1000, 800)
        envelope = Mock()
        envelope.character.name = "Scarlet"
        envelope.weapon.item_name = "Candlestick"
        envelope.room.name = "Study"
        menu.current_suspect = "Scarlet"
        menu.current_weapon = "Candlestick"
        menu.current_room = "Study"
        menu.check_accusation(envelope)
        self.assertTrue(menu.is_gamewon)
        self.assertTrue(menu.is_gameover)

    def test_wrong_accusation(self):
        pygame.init()
        menu = AccuseMenu(1000, 800)
        envelope = Mock()
        envelope.character.name = "Scarlet"
        envelope.weapon.item_name = "Candlestick"
        envelope.room.name = "Study"
        menu.current_suspect = "Plum"
        menu.current_weapon = "Rope"
        menu.current_room = "Kitchen"
        menu.check_accusation(envelope)
        self.assertFalse(menu.is_gamewon)
        self.assertTrue(menu.is_gameover)

if __name__ == "__main__":
    unittest.main()