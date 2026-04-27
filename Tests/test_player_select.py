import unittest
from unittest.mock import patch

from GridMovement import MenuButton

""" IMPORTANT INFORMATION

    This test should be run from the Command Line Interface (e.g. Command Prompt, Powershell, etc.), not VScode or whatever other program you 
    may be using. This is almost definitely true for all other tests as well.

    First, navigate to your project folder (not necessarily your repository folder).
    I don't know Mac commands but on Windows do: 
        1) $env:PYTHONPATH="."
        2) py -m unittest Tests/whatever_file.py 
            - In this case, you would type: ### py -m unittest Tests/test_player_select.py ###
            - Note that 'py' is what works for me but may not necessarily be what works for you. If 'py' fails, try py3, python, python3
    This is because tests are stored in a folder, and running it using that little play button up in the top right treats the Tests folder
    as a root directory, and searches for in Tests (which obviously does not exist)

    If you want to feel like a proper computer scientist who hates mouses and you're on Windows, do Win+R to launch the run command, then 
    type in "powershell" (no speech marks), enter, then cd, cd, cd until you reach the project folder. No need for a mouse at all!

    Should you want to run all tests within the Tests folder, run:
        py -m unittest discover -s Tests -p "test_*.py"
    This command assumes that all tests will follow the naming convention "test_<wildcard>.py".
    """

class TestMenuButton(unittest.TestCase):
    # this simulates the application without actually launching a pygame application because that would be long

    @patch("PickYourCharacter.MainMenu2")
    def test_button_returns_expected_character(self, MockMainMenu2):
        # Arrange
        mock_instance = MockMainMenu2.return_value
        mock_instance.run.return_value = "Scarlet"  # expected result

        button = MenuButton((255, 0, 0), 100, 100, 140, 60, "Start") # creates a MenuButton for simulation use

        # Simulate mouse click inside the button
        mouse_pos = (110, 110)

        # Act
        result = button.changeGameState(mouse_pos)

        # Assert
        self.assertEqual(result, "Scarlet")
        mock_instance.run.assert_called_once()

    # There will eventually be more tests but I wanted to push this now because the CLI thing is important-ish


if __name__ == "__main__":
    unittest.main()