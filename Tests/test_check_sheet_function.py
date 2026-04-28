import unittest
from GridMovement import CheckSheetFunction

class TestCheckSheetFunction(unittest.TestCase):

 def test_click_add_tick(self):
    sheet = CheckSheetFunction(start_x=100)
    mouse_position = (110, 180)
    result = sheet.handle_click(mouse_position)
    self.assertTrue(result)
    self.assertEqual(len(sheet.ticks), 1)

if __name__ == '__main__':
    unittest.main()
