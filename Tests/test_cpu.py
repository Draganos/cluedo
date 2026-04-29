import unittest
from GridMovement import Game

class DummyCpu:
    def __init__(self, col, row, character="A"):
        self.col = col
        self.row = row
        self.character = character

class TestCpu(unittest.TestCase):

    def setUp(self):
        self.game = Game()
        self.game.cpulastmove = {}
        self.game.doors = set()
        self.game.forbidden_tiles = set()

    def test_move_up(self):
        cpu = DummyCpu(5, 5)
        target = (5, 2)
        result = self.game.get_cpudirection(cpu, target)
        self.assertEqual(result, (0, -1))

    def test_move_down(self):
        cpu = DummyCpu(5, 5)
        target = (5, 8)
        result = self.game.get_cpudirection(cpu, target)
        self.assertEqual(result, (0, 1))

    def test_move_left(self):
        player = DummyCpu(5, 5)
        target = (2, 5)
        result = self.game.get_cpudirection(player, target)
        self.assertEqual(result, (-1, 0))

    def test_move_right(self):
        cpu = DummyCpu(5, 5)
        target = (7, 5)
        result = self.game.get_cpudirection(cpu, target)
        self.assertEqual(result, (1, 0))

    def test_avoid_cpu_backtrack(self):
        cpu = DummyCpu(5, 5)
        target = (5, 7)
        self.game.cpulastmove[cpu] = (0, -1)
        result = self.game.get_cpudirection(cpu, target)
        self.assertIn(result, [(1, 0), (-1, 0), (0, -1)])

if __name__ == "__main__":
    unittest.main()