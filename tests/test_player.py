import unittest
from GridMovement import Player

class TestPlayer(unittest.TestCase):

    def test_player_move(self):
        player = Player(5, 5)
        result = player.move(1, 0, [], {}, {})
        self.assertEqual(result, "MOVED")
        self.assertEqual(player.col, 6)
        self.assertEqual(player.row, 5)

    def test_player_move_through_door(self):
        player = Player(5, 5)
        doors = {(6, 5): "Kitchen"}
        room_seats = {"Kitchen": [(10, 10), (11, 11)]}
        result = player.move(1, 0, [], doors, room_seats)
        self.assertEqual(result, "ENTERED_ROOM")
        self.assertEqual(player.col, 10)
        self.assertEqual(player.row, 10)
        self.assertEqual(player.in_room, "Kitchen")

if __name__ == '__main__':
    unittest.main()