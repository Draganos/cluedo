import unittest
import pygame
from unittest.mock import patch

from GridMovement import Menu, MenuButton, Game

class TestMenuScreen(unittest.TestCase):

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((800, 600))

    # check if the start button actually goes to the the character select screen
    # done by checking the return after having run the char select screen (because of how the function changeGameState(...) works)
    @patch("PickYourCharacter.MainMenu2")
    def test_start_triggers_character_screen(self, MockMainMenu2):
        mock_menu = MockMainMenu2.return_value
        mock_menu.run.return_value = "MissScarlett.png"

        # create a simulated "Start" button
        # this button is a different colour & location to the actual button, but they are irrelevant for testing
        button = MenuButton((255, 0, 0), 100, 100, 140, 60, "Start")

        # simulates a click inside button
        mouse_pos = (110, 110)

        # gets the result from the click
        result = button.changeGameState(mouse_pos)

        # then compares the result to see if it's the correct image
        self.assertEqual(result, "MissScarlett.png")
        mock_menu.run.assert_called_once()

    @patch("pygame.quit")
    def test_exit_button(self, mock_quit):
        button = MenuButton((255, 0, 0), 100, 100, 140, 60, "Exit")

        result = button.changeGameState((110, 110))

        mock_quit.assert_called_once()
        self.assertIsNone(result)
    
    # testing the mute buttons toggle and return as expected
    def test_mute(self):
        # create a simulated "Mute" button
        button = MenuButton((255, 0, 0), 100, 100, 140, 60, "Mute Music")

        # simulates a click inside button
        mouse_pos = (110, 110)

        # gets the result from the click
        result = button.changeGameState(mouse_pos)

        self.assertEqual(result, "Mute")
        self.assertEqual(button.text, "Unmute Music")

    def test_unmute(self):
        # create a simulated "Unmute" button
        button = MenuButton((255, 0, 0), 100, 100, 140, 60, "Unmute Music")

        # simulates a click inside button
        mouse_pos = (110, 110)

        # gets the result from the click
        result = button.changeGameState(mouse_pos)

        self.assertEqual(result, "Unmute")
        self.assertEqual(button.text, "Mute Music")

    # testing mouse hover functionality
    def test_mouse_hover_over_buttons(self):
        # simulate a button
        button = MenuButton((255, 0, 0), 100, 100, 140, 60, "Start")

        # simulate mouse over button
        mouse_pos = (110, 110)

        hovered = button.mouseHover(mouse_pos)

        self.assertTrue(hovered)

    def test_mouse_hover_outside_buttons(self):
        # simulate a button
        button = MenuButton((255, 0, 0), 100, 100, 140, 60, "Start")

        # simulate mouse far away
        mouse_pos = (0, 0)

        hovered = button.mouseHover(mouse_pos)

        self.assertFalse(hovered)
