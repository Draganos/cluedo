import random

import pygame
from main import setup_game  # for linking gridcontroller


# Constants, OFFSET X, Y and TILE_SIZE determine the grid layout.
SCALE = 0.6
TILE_SIZE = 46.5 * SCALE
OFFSET_X = 37 * SCALE
OFFSET_Y = 18 * SCALE
# Button colours
COLOUR = "#462779"
COLOUR_HOVER = "#9040BA"


class Player:
    def __init__(self, col=0, row=0, color=(255, 255, 255), isCPU=False, character=None):
        self.col = col
        self.row = row
        self.color = color
        self.isCPU = isCPU  # set to none if not user.
        self.character = character
        self.hand = []

    def move(self, dx, dy, forbidden_zones, doors, room_seats):
        # Calculate new position
        new_col = self.col + dx
        new_row = self.row + dy

        # 1. Door Check
        if (new_col, new_row) in doors:
            entered_room = doors[(new_col, new_row)]
            print(f"Player entered the {entered_room}!")

            # Teleport to the first seat, up to 6 seats per room.
            available_seats = room_seats[entered_room]
            self.col = available_seats[0][0]
            self.row = available_seats[0][1]
            self.in_room = entered_room  # Save this for main.py logic later!

            return "ENTERED_ROOM"

        # 2. Forbidden tile Check
        if (new_col, new_row) in forbidden_zones:
            print("Cannot move in there!")
            return None

        # 3. Boundary check (so they don't walk off the screen)
        if 0 <= new_col < 24 and 0 <= new_row < 25:
            self.col = new_col
            self.row = new_row
            return "MOVED"

    def draw(self, surface):
        # Convert grid position to pixels and draws the player on the grid.
        pixel_x = OFFSET_X + (self.col * TILE_SIZE) + (TILE_SIZE / 2)
        pixel_y = OFFSET_Y + (self.row * TILE_SIZE) + (TILE_SIZE / 2)
        pygame.draw.circle(surface, self.color, (int(pixel_x), int(pixel_y)), int(TILE_SIZE / 3))


class Board:
    def __init__(self):
        # Load and scale the board
        self.image = pygame.image.load("Assets/cluedoboard.jpg")
        self.width = int(self.image.get_width() * SCALE)
        self.height = int(self.image.get_height() * SCALE)
        self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))

        # Load and scale the sheet
        self.sheet = pygame.image.load("Assets/cluedo-sheet.png")
        self.sheet_width = int(self.sheet.get_width() * 0.5 * SCALE)
        self.sheet = pygame.transform.smoothscale(self.sheet, (self.sheet_width, self.height))

    def draw(self, surface):
        # Draw the board at the top-left, this is neccessary so the player can be drawn on top of the board.
        surface.blit(self.image, (0, 0))
        # Draw the sheet to the right of the board
        surface.blit(self.sheet, (self.width, 0))

        # Visual Debug: To see the grid lines.
        #for r in range(25):
            #for c in range(24):
                #rect = (OFFSET_X + c * TILE_SIZE, OFFSET_Y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
               # pygame.draw.rect(surface, (255, 0, 0), rect, 1)


##SPRITE WORK FROM VICTOR ####
class Spritesheet():
    def __init__(self, image):
        self.sheet = image

    def get_frame(self, frame_x, frame_y, width, height, scale=1):
        frame = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        frame.blit(self.sheet, (0, 0), (frame_x * width, frame_y * height, width, height))
        frame = pygame.transform.smoothscale_by(frame, scale)

        return frame


class Sprite_Chars():
    def __init__(self, width, height):
        self.sprite_sheet_image = pygame.image.load("Assets/143445.png")
        self.sprite_sheet_image = pygame.transform.smoothscale(self.sprite_sheet_image, ((width) * 2, (height) * 7))

        self.sprite_sheet = Spritesheet(self.sprite_sheet_image)

        self.animation_list = []
        animation_steps = 14
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 60  # milliseconds
        self.frame = 0

        self.select_sfx = pygame.mixer.Sound("Assets/dice_roll.mp3")

        x = 0
        y = 0

        for i in range(animation_steps):
            self.animation_list.append(self.sprite_sheet.get_frame(x, y, width, height))
            y += 1
            if y == 6:
                y = 0
                x += 1

    def draw(self, surface):
        # update animation
        done = False
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= len(self.animation_list):
                self.frame = 0
                done = True

        self.select_sfx.set_volume(0.05)
        self.select_sfx.play()
        surface.blit(self.animation_list[self.frame], (0, 0))

        if done:
            return True
        return False


###END SPRITE WORK FROM VICTOR

class Game:
    # Initialisation for the game.
    def __init__(self):
        pygame.init()
        self.board = Board()
        win_width = self.board.width + self.board.sheet_width
        self.screen = pygame.display.set_mode((win_width, self.board.height))
        self.menu = Menu()
        # creates dice for dice class
        self.dice = Dice(self.board.width // 2 - 60, self.board.height // 1.25)
        self.dice_rect = self.dice.rect
        # Determines where the player starts and color.
        self.player = Player(11, 11, (255, 0, 0))  # Red player
        self.running = True
        # Gets mouse position
        self.mouse = pygame.mouse.get_pos()

        self.sprite = Sprite_Chars(win_width, self.board.height)

        ###storing game state variables for gamecontroller
        self.activegame = False
        self.currentplayer = None
        self.otherplayers = []
        self.rooms = []
        self.weapons = []
        self.characters = []
        self.envelope = None
        self.moves_left = 0

        ###TURN TRACKING VARIABLES
        self.turn_index = 0
        self.all_players = []
        self.turn_phase = "ROLL"  # ROLL → MOVE → END

        # Door tiles
        self.doors = {
            (6, 3): "Study",
            (9, 4): "Hall",
            (11, 6): "Hall",
            (12, 6): "Hall",
            (17, 5): "Lounge",
            (6, 8): "Library",
            (3, 10): "Library",
            (1, 12): "Billiard Room",
            (5, 15): "Billiard Room",
            (16, 12): "Dining Room",
            (17, 9): "Dining Room",
            (4, 19): "Conservatory",
            (8, 19): "Ballroom",
            (15, 19): "Ballroom",
            (9, 17): "Ballroom",
            (14, 17): "Ballroom",
            (19, 18): "Kitchen",
        }

        self.room_seats = {
            "Study": [(2, 1), (3, 1), (2, 2), (3, 2), (1, 1), (4, 1)],
            "Hall": [(11, 2), (12, 2), (11, 3), (12, 3), (11, 4), (12, 4)],
            "Lounge": [(19, 2), (20, 2), (21, 2), (19, 3), (20, 3), (21, 3)],
            "Library": [(2, 7), (3, 7), (2, 8), (3, 8), (2, 9), (3, 9)],
            "Billiard Room": [(2, 13), (3, 13), (2, 14), (3, 14), (2, 15), (3, 15)],
            "Dining Room": [(19, 10), (20, 10), (21, 10), (19, 11), (20, 11), (21, 11)],
            "Conservatory": [(2, 20), (3, 20), (2, 21), (3, 21), (2, 22), (3, 22)],
            "Ballroom": [(10, 19), (11, 19), (12, 19), (10, 20), (11, 20), (12, 20)],
            "Kitchen": [(20, 20), (21, 20), (20, 21), (21, 21), (20, 22), (21, 22)]
        }

        self.forbidden_tiles = [
            # These are all the forbidden zones.
            # Grid is 24x25 ColumnsxRows. starts at 0x0 top left corner.

            # Study room
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0),
            (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
            (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
            (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
            (6, 0), (6, 1), (6, 2), (6, 3),

            # Specific tiles:
            (0, 4), (0, 11), (0, 17), (6, 24), (7, 24), (6, 23), (16, 24), (17, 24), (17, 23), (23, 6), (23, 8),
            (6, 7), (6, 8), (6, 9), (10, 24), (11, 24), (12, 24), (13, 24), (10, 23), (11, 23), (12, 23), (13, 23),

            # STAIRS:
            (9, 8), (9, 9), (9, 10), (9, 11), (10, 8), (10, 9), (10, 10), (10, 11),
            (13, 8), (13, 9), (13, 10), (13, 11), (12, 8), (12, 9), (12, 10), (12, 11),

            # LOUNGE
            (17, 0), (18, 0), (19, 0), (20, 0), (21, 0), (22, 0), (23, 0),
            (17, 1), (18, 1), (19, 1), (20, 1), (21, 1), (22, 1), (23, 1),
            (17, 2), (18, 2), (19, 2), (20, 2), (21, 2), (22, 2), (23, 2),
            (17, 3), (18, 3), (19, 3), (20, 3), (21, 3), (22, 3), (23, 3),
            (17, 4), (18, 4), (19, 4), (20, 4), (21, 4), (22, 4), (23, 4),
            (17, 5), (18, 5), (19, 5), (20, 5), (21, 5), (22, 5), (23, 5),
            (15, 0), (8, 0),

            # Specific Dining Room Coordinates
            (19, 15), (20, 15), (21, 15), (22, 15), (23, 15), (24, 15), (24, 16), (23, 16),
        ]

        # MIDDLE =
        for r in range(12, 15):
            for c in range(9, 14):
                self.forbidden_tiles.append((c, r))

        # HALL =
        for r in range(0, 7):
            for c in range(9, 15):
                self.forbidden_tiles.append((c, r))

        # LIBRARY =
        for r in range(6, 11):
            for c in range(0, 6):
                self.forbidden_tiles.append((c, r))

        # CONSERVATORY =
        for r in range(19, 25):
            for c in range(0, 6):
                self.forbidden_tiles.append((c, r))

        # BALLROOM =
        for r in range(17, 23):
            for c in range(8, 16):
                self.forbidden_tiles.append((c, r))

        # KITCHEN =
        for r in range(18, 25):
            for c in range(18, 24):
                self.forbidden_tiles.append((c, r))

        # DINING ROOM =
        for r in range(9, 15):
            for c in range(16, 24):
                self.forbidden_tiles.append((c, r))

        # Billiard Room =
        for r in range(12, 17):
            for c in range(0, 6):
                self.forbidden_tiles.append((c, r))

        # Variables for Sprite animations
        self.chance = 10000
        self.last_surprise = pygame.time.get_ticks()
        self.playing = False
        self.play_finished = False
        self.cooldown = 840  # milliseconds

    def handle_events(self):
        # checks for actions by the user.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if not self.activegame or self.get_active_player() != self.currentplayer:  # added 24/04/2026 for locking movement to current turn
                    return  # added 24/04/2026 for locking movement to current turn
                if event.key == pygame.K_UP:    self.player.move(0, -1, self.forbidden_tiles, self.doors,
                                                                 self.room_seats)
                if event.key == pygame.K_DOWN:  self.player.move(0, 1, self.forbidden_tiles, self.doors,
                                                                 self.room_seats)
                if event.key == pygame.K_LEFT:  self.player.move(-1, 0, self.forbidden_tiles, self.doors,
                                                                 self.room_seats)
                if event.key == pygame.K_RIGHT: self.player.move(1, 0, self.forbidden_tiles, self.doors,
                                                                 self.room_seats)

            if self.menu != None and event.type == pygame.MOUSEBUTTONDOWN:
                # Catch the action
                action = self.menu.buttonAction(self.mouse)
                print("menu action = ", action)  # for debugging in console
                # If the action is START, get rid of the menu
                if action is not None:
                    selected_name = action
                    # Extract proper character name
                    if "Mustard" in selected_name:
                        selected_name = "Mustard"
                    elif "Scarlet" in selected_name:
                        selected_name = "Scarlet"
                    elif "White" in selected_name:
                        selected_name = "White"
                    elif "Peacock" in selected_name:
                        selected_name = "Peacock"
                    elif "Plum" in selected_name:
                        selected_name = "Plum"
                    elif "Green" in selected_name:
                        selected_name = "Green"

                    # initializing game logic ABDULLAHMODIFIED
                    player, cpu_players, rooms, weapons, characters, envelope = setup_game(selected_name)
                    self.currentplayer = player
                    self.otherplayers = cpu_players
                    self.all_players = [self.currentplayer] + self.otherplayers  ###for turn system
                    self.turn_index = 0  ###turn index
                    self.rooms = rooms
                    self.weapons = weapons
                    self.characters = characters
                    self.envelope = envelope
                    self.player.character = self.currentplayer.character  # this links visual player to logic of the character
                    self.activegame = True
                    self.menu = None
                    print("the game is fully initialised.")

            if self.dice_rect.collidepoint(self.mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                if not self.activegame or self.get_active_player() != self.currentplayer:  # added 24/04/2026 for locking movement to current turn
                    print(
                        "Dice cannot be rolled with mouse as not players turn")  # added 24/04/2026 for locking movement to current turn
                    return  # added 24/04/2026 for locking movement to current turn

                print("Dice has been rolled with mouse.")  # debugging
                if self.activegame:
                    self.moves_left = random.randint(1, 6)
                    print(f"Rolled: {self.moves_left}")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.activegame or self.get_active_player() != self.currentplayer:  # added 24/04/2026 for locking movement to current turn
                        print(
                            "Dice cannot be rolled with mouse as not players turn")  # added 24/04/2026 for locking movement to current turn
                        return  # added 24/04/2026 for locking movement to current turn
                    print("Dice has been rolled with spacebar.")
                    if self.activegame:
                        self.moves_left = random.randint(1, 6)
                        print(f"Rolled: {self.moves_left}")

    def get_active_player(self):  ###for turn system
        return self.all_players[self.turn_index]

    def run(self):
        while self.running:
            self.handle_events()
            # Renders the game.
            self.screen.fill((0, 0, 0))
            # Gets mouse position while game running
            self.mouse = pygame.mouse.get_pos()

            current_time = pygame.time.get_ticks()

            # Random sprite trigger logic
            if current_time - self.last_surprise >= self.cooldown and not self.playing:
                j_roll = random.randint(1, self.chance)

                if j_roll == self.chance:
                    self.playing = True
                    self.play_finished = False
                    self.last_surprise = current_time

            if self.menu is not None:  # checking if we are on menu screen or board screen
                self.menu.draw(self.screen, self.mouse)
            else:
                self.board.draw(self.screen)
                self.player.draw(self.screen)
                self.dice.draw(self.screen, self.mouse)

                if self.playing:
                    finished = self.sprite.draw(self.screen)

                    if finished:
                        self.playing = False

            pygame.display.flip()
        pygame.quit()


class Dice:
    # Should (ideally) have both mouse and keyboard functionality.
    def __init__(self, x, y):
        # getting positions for later when drawing
        self.x = x
        self.y = y
        # load dice image
        self.image = pygame.image.load('Assets/dice.png')
        # width and height
        self.width = self.image.get_width() // 4
        self.height = self.image.get_height() // 4
        # scales image
        self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))
        self.image_copy = self.image.copy()  # a copy that has transparency
        self.image_copy.set_alpha(150)
        # create a rect that matches the size of the image
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface, mouse):
        # gets mouse position
        self.mouse = mouse
        # uses mouse position to change transparency (on hover or no)
        if self.rect.collidepoint(
                mouse):  # once rounds are introduced, add an extra check to make sure it is the player's turn
            surface.blit(self.image, (self.x, self.y))
        else:
            surface.blit(self.image_copy, (self.x, self.y))


class Menu:
    def __init__(self):
        # Loads and scales the background image used for the menu to cover the whole screen; overflow ignored
        self.image = pygame.image.load('Assets/Tudor-Mansion.png')
        self.disp_surf = pygame.display.get_surface()
        x = self.disp_surf.get_width()
        y = self.disp_surf.get_height()
        self.image = pygame.transform.smoothscale(self.image, (x, y))
        self.width = x
        self.height = y
        # Using the same principles as Board(), load the Clue logo
        self.logo = pygame.image.load('Assets/CLUE_logo.png')
        self.logo_width = int(self.logo.get_width())
        self.logo_height = int(self.logo.get_height())
        self.logo = pygame.transform.smoothscale(self.logo, (self.logo_width, self.logo_height))
        self.logo_rect = self.logo.get_rect()
        self.logo_rect.centerx = pygame.display.get_surface().get_rect().centerx
        self.logo_rect.y = self.height * 0.1
        # now create the start button - centred horizontally
        self.start_btn = MenuButton(COLOUR, self.width // 2 - 70, self.height // 2 - 30, 140, 60, "Start")
        self.exit_btn = MenuButton(COLOUR, self.width // 2 - 70, self.height // 2 + 60, 140, 60, "Exit")

    def buttonAction(self, mouse):
        start_action = self.start_btn.changeGameState(mouse)
        exit_action = self.exit_btn.changeGameState(mouse)
        if start_action is not None:  # start button returns character selected
            return start_action

        return None

    def draw(self, surface, mouse):
        # Gets mouse pos (taken as parameter)
        self.mouse = mouse
        # Draws background from top-left
        surface.blit(self.image, (0, 0))
        surface.blit(self.logo, (self.logo_rect))
        self.start_btn.draw(self.disp_surf)
        self.start_btn.mouseHover(self.mouse)
        self.exit_btn.draw(self.disp_surf)
        self.exit_btn.mouseHover(self.mouse)


class MenuButton:
    def __init__(self, colour, pos_x, pos_y, width, height, text=''):
        self.color = colour
        self.width = width
        self.height = height
        self.text = text
        self.pos_x = pos_x
        self.pos_y = pos_y

    def draw(self, surface):
        # draw the button as a rectangle
        pygame.draw.rect(surface, self.color, (self.pos_x, self.pos_y, self.width, self.height), 0)

        if self.text != '':  # checks text isn't empty
            font = pygame.font.SysFont("papyrus", 30)
            text = font.render(self.text, 1, "#FFFFFF")
            surface.blit(text, (self.pos_x + (self.width // 2 - text.get_width() // 2),
                                self.pos_y + (self.height // 2 - text.get_height() // 2)))

    def mouseHover(self, position):  # changes button colour when mouse is hovering over it
        if position[0] > self.pos_x and position[0] < self.pos_x + self.width:
            if position[1] > self.pos_y and position[1] < self.pos_y + self.height:
                self.color = COLOUR_HOVER
                return True
        self.color = COLOUR
        return False

    def changeGameState(self, position):
        if position[0] > self.pos_x and position[0] < self.pos_x + self.width:
            if position[1] > self.pos_y and position[1] < self.pos_y + self.height:
                if self.text == "Start":
                    # This should transition to the character select screen
                    print("Start game!")
                    from PickYourCharacter import MainMenu2
                    char_menu = MainMenu2()
                    selectedchar = char_menu.run()
                    return selectedchar
                else:
                    # Anyway, importantly, the exit button works (i.e. exits the game)
                    pygame.quit()
        return None


if __name__ == "__main__":
    clue_game = Game()
    clue_game.run()


