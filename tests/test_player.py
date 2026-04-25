import unittest
from GridMovement import Player

class TestPlayer(unittest.TestCase):

    def test_player_move(self):
        player = Player(5, 5)
        result = player.move(1, 0, [], {}, {})
        self.assertEqual(result, "MOVED")
        self.assertEqual(player.col, 6)
        self.assertEqual(player.row, 5)

    def test_player_enter_rooms(self):
        rooms = [
            ((6, 5), "Kitchen", (20, 20)),
            ((6, 3), "Study", (2, 1)),
            ((9, 4), "Hall", (11, 2)),
            ((17, 5), "Lounge", (19, 2)),
            ((6, 8), "Library", (2, 7)),
            ((8, 19), "Ballroom", (10, 19)),
        ]
        for door_position, room_name, expected_position in rooms:
            player = Player(5, 5)
            doors = {door_position: room_name}
            room_seats = {room_name: [expected_position]}
            dx = door_position[0] - 5
            dy = door_position[1] - 5
            result = player.move(dx, dy, [], doors, room_seats)
            self.assertEqual(result, "ENTERED_ROOM")
            self.assertEqual((player.col, player.row), expected_position)
            self.assertEqual(player.in_room, room_name)

if __name__ == '__main__':
    unittest.main()