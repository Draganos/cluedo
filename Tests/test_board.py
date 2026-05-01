import unittest
from unittest.mock import patch, MagicMock
from GridMovement import Board

SCALE = 1
HEADER_HEIGHT = 50

class TestBoard(unittest.TestCase):

    @patch("GridMovement.SCALE", 1)
    @patch("pygame.image.load")
    @patch("pygame.transform.smoothscale")
    def test_init(self, mock_scale, mock_load):
        mock_image = MagicMock()
        mock_image.get_width.return_value = 1000
        mock_image.get_height.return_value = 800
        mock_load.return_value = mock_image
        mock_scale.side_effect = lambda img, size: img
        board = Board()
        self.assertEqual(board.width, 1000)
        self.assertEqual(board.height, 800)
        self.assertEqual(board.sheet_width, int(1000 * 0.5))
        self.assertEqual(board.sheet_height, 800 - 200)
        self.assertEqual(mock_load.call_count, 2)

    @patch("pygame.draw.rect")
    def test_draw(self, mock_draw_rect):
        board = Board()
        board.image = MagicMock()
        board.sheet = MagicMock()
        board.width = 500
        board.height = 600
        board.sheet_width = 200
        board.sheet_height = 300
        surface = MagicMock()
        board.draw(surface)
        self.assertEqual(surface.blit.call_count, 2)
        mock_draw_rect.assert_called_once()
        args = mock_draw_rect.call_args[0]
        self.assertEqual(args[1], (140, 185, 130))

if __name__ == "__main__":
    unittest.main()

# test