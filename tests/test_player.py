import unittest
from GridMovement import Player

class TestPlayer(unittest.TestCase):

    def test_player_move(self):
        player = Player(5, 5)
        result = player.move(1, 0, [], {}, {})
        self.assertEqual(result, "MOVED")
        self.assertEqual(player.col, 6)
        self.assertEqual(player.row, 5)

if __name__ == '__main__':
    unittest.main()