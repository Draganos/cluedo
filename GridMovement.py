import itertools
import random
import pygame

from main import setup_game, make_suggestion  # for linking gridcontroller

# Constants = OFFSET X, Y and TILE_SIZE determine the grid layout. 
# Sheet is for the cells inside the checksheet.
SCALE = 0.6
TILE_SIZE = 46.5 * SCALE
OFFSET_X = 37 * SCALE
HEADER_HEIGHT = 80
OFFSET_Y = (18 * SCALE) + HEADER_HEIGHT

# Button colours
COLOUR = "#462779"
COLOUR_HOVER = "#9040BA"


class Player:
    #Initialisation
    def __init__(self, col=0, row=0, color=(255, 255, 255), isCPU=False, character=None):
        self.col = col
        self.in_room = None
        self.row = row
        self.color = color
        self.isCPU = isCPU  # set to none if not user.
        self.character = character
        self.hand = []
        self.is_eliminated = False
        self.logic_p = None


    def move(self, dx, dy, forbidden_zones, doors, room_seats, room_exits):
        # if player is inside room, first move them to the rooms exit
        if self.in_room is not None:
            exit_tile = room_exits[self.in_room]
            self.col = exit_tile[0]
            self.row = exit_tile[1]
            print(f"Player left the {self.in_room}")
            self.in_room = None
            return "LEFT_ROOM"
            
        # Calculate new position
        new_col = self.col + dx
        new_row = self.row + dy

        # Door Check
        if (new_col, new_row) in doors:
            entered_room = doors[(new_col, new_row)]
            print(f"Player entered the {entered_room}!")

            # Teleport to the first seat, up to 6 seats per room.
            available_seats = room_seats[entered_room]
            self.col = available_seats[0][0]
            self.row = available_seats[0][1]
            self.in_room = entered_room

            return "ENTERED_ROOM"

        # Forbidden tile Check
        if (new_col, new_row) in forbidden_zones:
            return None

        # Boundary check (so they don't walk off the screen)
        if 0 <= new_col < 24 and 0 <= new_row < 25:
            self.col = new_col
            self.row = new_row
            return "MOVED"

    #Draws player on the grid
    def draw(self, surface):
        
        # Converts grid position to pixels and draws the player on the grid.
        pixel_x = OFFSET_X + (self.col * TILE_SIZE) + (TILE_SIZE / 2)
        pixel_y = OFFSET_Y + (self.row * TILE_SIZE) + (TILE_SIZE / 2)
        pygame.draw.circle(surface, self.color, (int(pixel_x), int(pixel_y)), int(TILE_SIZE / 3))


class Board:
    #Initilisation for the board
    def __init__(self):
        
        # Loads and scales the board
        self.image = pygame.image.load("Assets/cluedoboard.jpg")
        self.width = int(self.image.get_width() * SCALE)
        self.height = int(self.image.get_height() * SCALE)
        self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))

        # Loads and scales the sheet
        self.sheet = pygame.image.load("Assets/cluedo-sheet.png")
        self.sheet_width = int(self.sheet.get_width() * 0.5 * SCALE)
        self.sheet_height = self.height - 200
        self.sheet = pygame.transform.smoothscale(self.sheet, (self.sheet_width, self.sheet_height))

    #Draws the board shifted down by Header_Height
    def draw(self, surface):
    
        surface.blit(self.image, (0, HEADER_HEIGHT))
        surface.blit(self.sheet, (self.width, HEADER_HEIGHT))

        # Fills the empty space under the checksheet with green.
        pygame.draw.rect(
            surface,
            (140, 185, 130),
            (self.width, self.sheet_height + HEADER_HEIGHT, self.sheet_width, self.height - self.sheet_height)
        )


#Victor's Spritework
class Spritesheet():
    #Initilisation for the sprite
    def __init__(self, image):
        self.sheet = image
    
    def get_frame(self, frame_x, frame_y, width, height, scale=1):
        frame = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        frame.blit(self.sheet, (0, 0), (frame_x * width, frame_y * height, width, height))
        frame = pygame.transform.smoothscale_by(frame, scale)

        return frame

#Animation
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
        x = 0
        y = 0

        for i in range(animation_steps):
            self.animation_list.append(self.sprite_sheet.get_frame(x, y, width, height))
            y += 1
            if y == 6:
                y = 0
                x += 1

    def draw(self, surface):
        # Update animation
        done = False
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time
            if self.frame >= len(self.animation_list):
                self.frame = 0
                done = True

        surface.blit(self.animation_list[self.frame], (0, 0))

        if done:
            return True
        return False


class Game:
    # Initialisation for the game.
    def __init__(self):
        
        #MUSIC INIT
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load('Assets/bgm.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.2)
        self.dice_sound = pygame.mixer.Sound("Assets/diceroll.mp3")
        self.card_sound = pygame.mixer.Sound("Assets/cardshuffle.mp3")
        self.click_sound = pygame.mixer.Sound("Assets/click.mp3")

        # Board init
        self.board = Board()
        win_width = self.board.width + self.board.sheet_width
        self.screen = pygame.display.set_mode((win_width, self.board.height + HEADER_HEIGHT))
        self.menu = Menu()
        # self.play_menu_music()
        self.last_roll = None
        self.roll_source = None
        self.roll_display_time = 0

        # Header, Dice, Accuse and CardButton
        item_y = self.board.sheet_height + 50 + HEADER_HEIGHT
        dice_x = self.board.width + 40
        accuse_x = self.board.width + 220
        self.dice = Dice(dice_x, item_y)
        self.dice_rect = self.dice.rect
        self.accuse_btn = AccuseButton(accuse_x, item_y)
        self.accuse_menu = AccuseMenu(win_width, self.board.height + HEADER_HEIGHT)
        self.check_sheet = CheckSheetFunction(self.board.width + 67)
        cards_x = (self.board.width * 0.80) - (150 // 2)
        cards_y = HEADER_HEIGHT - 80
        self.cards_btn = CardsButton(cards_x, cards_y)

        # Cards and Dropdown menu for cards init
        self.show_cards_dropdown = False
        self.dropdown_font = pygame.font.SysFont(None, 24)
        self.card_images = {}
        self.load_card_images()

        # Determines where the player starts and color.
        self.visual_players = []
        self.player = Player(11, 11, (255, 0, 0))  # Red player
        self.running = True
        # Gets mouse position
        self.mouse = pygame.mouse.get_pos()
        self.sprite = Sprite_Chars(win_width, self.board.height + HEADER_HEIGHT)

        #CPU init
        self.cpu_timer = 0
        self.cpu_moves_left = 0
        self.cpu_rolled = False
        self.cpu_roomtarget = {}
        self.cpu_tiletarget = {}
        
        #storing game state variables for gamecontroller
        self.activegame = False
        self.currentplayer = None
        self.otherplayers = []
        self.rooms = []
        self.weapons = []
        self.characters = []
        self.envelope = None
        self.moves_left = 0
        self.cpulastmove = {}

        # suggestion tracking variables
        self.suggestion_result = None
        self.readytosuggest = False
        
        #TURN TRACKING VARIABLES
        self.turn_index = 0
        self.all_players = []
        self.turn_phase = "ROLL"  # ROLL/MOVE/ACTION/END

        self.message = ""
        self.message_timer = 0
        self.font = pygame.font.SysFont(None, 32)

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
        self.room_doors = {}
        for tile, room_name in self.doors.items():
            if room_name not in self.room_doors:
                self.room_doors[room_name] = []
            self.room_doors[room_name].append(tile)

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
        self.room_exits = {
            "Study": (6, 4),
            "Hall": (11, 7),
            "Lounge": (17, 6),
            "Library": (6, 10),
            "Billiard Room": (5, 17),
            "Dining Room": (16, 15),
            "Conservatory": (4, 18),
            "Ballroom": (8, 16),
            "Kitchen": (19, 17)
        }
        self.secret_passages = {
            "Study": "Kitchen",
            "Kitchen": "Study",
            "Lounge": "Conservatory",
            "Conservatory": "Lounge"
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

            # CONSERVATORY
            (0, 19), (0, 20), (1, 19), (2, 19), (3, 19), (4, 20), (5, 20),
            (0, 21), (1, 23), (2, 23), (3, 23), (4, 23), (5, 21),
            (0, 22), (5, 22),
            (0, 23), (5, 23),

            # Specific Dining Room Coordinates
            (19, 15), (20, 15), (21, 15), (22, 15), (23, 15), (23, 16), (15, 24)
            # (24, 15), (24, 16),  <----- ive removed these cause the white cpu would always get stuck in boundary, 0<23 are columns valid and 24 is out of board.
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
        #for r in range(19, 25):
        #    for c in range(0, 6):
        #        self.forbidden_tiles.append((c, r))

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

        # Variables for the suggestion/accusation selection
        self.pre_selection = False
        self.selecting = False  # the suggestion/accusation menu
        self.selecting_block = True  # to patch an annoying glitch
        self.select_suspect = False  # selecting suspect menu
        self.select_weapon = False  # selecting weapon menu
        self.select_room = False  # selecting room menu

        self.suspect_picked = False
        self.weapon_picked = False
        self.room_picked = False
        self.card_pos = {
            "char": [
                (250, 225), (450, 225), (650, 225),
                (250, 475), (450, 475), (650, 475)
            ],
            "weap": [
                (250, 225), (450, 225), (650, 225),
                (250, 475), (450, 475), (650, 475)
            ],
            "room": [
                (250, 200), (450, 200), (650, 200),
                (250, 450), (450, 450), (650, 450),
                (250, 700), (450, 700), (650, 700)
            ]
        }
        self.selection_card_list = []
        self.char_card_list = []
        self.weap_card_list = []
        self.room_card_list = []

    def load_card_images(self):
        self.card_images = {
            # characters
            "Mustard": pygame.transform.smoothscale(pygame.image.load("Cards/Col Mustard.png").convert_alpha(),
                                                    (140, 200)),
            "Scarlet": pygame.transform.smoothscale(pygame.image.load("Cards/MissScarlett.png").convert_alpha(),
                                                    (140, 200)),
            "White": pygame.transform.smoothscale(pygame.image.load("Cards/MrsWhite.png").convert_alpha(), (140, 200)),
            "Peacock": pygame.transform.smoothscale(pygame.image.load("Cards/Mrs. Peacock.png").convert_alpha(),
                                                    (140, 200)),
            "Plum": pygame.transform.smoothscale(pygame.image.load("Cards/ProfessorPlum.png").convert_alpha(),
                                                 (140, 200)),
            "Green": pygame.transform.smoothscale(pygame.image.load("Cards/Rev Green.png").convert_alpha(), (140, 200)),

            # weapons
            "Candlestick": pygame.transform.smoothscale(pygame.image.load("Cards/Candlestick.png").convert_alpha(),
                                                        (140, 200)),
            "Dagger": pygame.transform.smoothscale(pygame.image.load("Cards/dagger.png").convert_alpha(), (140, 200)),
            "Revolver": pygame.transform.smoothscale(pygame.image.load("Cards/Revolver.png").convert_alpha(),
                                                     (140, 200)),
            "Rope": pygame.transform.smoothscale(pygame.image.load("Cards/Rope.svg").convert_alpha(), (140, 200)),
            "Lead Pipe": pygame.transform.smoothscale(pygame.image.load("Cards/LeadPipe.png").convert_alpha(),
                                                      (140, 200)),
            "Wrench": pygame.transform.smoothscale(pygame.image.load("Cards/spanner.png").convert_alpha(), (140, 200)),
            "Spanner": pygame.transform.smoothscale(pygame.image.load("Cards/spanner.png").convert_alpha(), (140, 200)), #done for debugging as names were previously interchangable

            # rooms
            "Study": pygame.transform.smoothscale(pygame.image.load("Cards/Study.png").convert_alpha(), (140, 200)),
            "Hall": pygame.transform.smoothscale(pygame.image.load("Cards/Hall.png").convert_alpha(), (140, 200)),
            "Lounge": pygame.transform.smoothscale(pygame.image.load("Cards/Lounge.png").convert_alpha(), (140, 200)),
            "Library": pygame.transform.smoothscale(pygame.image.load("Cards/Library.png").convert_alpha(), (140, 200)),
            "Billiard Room": pygame.transform.smoothscale(pygame.image.load("Cards/Billiards Room.png").convert_alpha(),
                                                          (140, 200)),
            "Dining Room": pygame.transform.smoothscale(pygame.image.load("Cards/Dining Room.png").convert_alpha(),
                                                        (140, 200)),
            "Conservatory": pygame.transform.smoothscale(pygame.image.load("Cards/Conservatory.png").convert_alpha(),
                                                         (140, 200)),
            "Ballroom": pygame.transform.smoothscale(pygame.image.load("Cards/Ballroom.png").convert_alpha(),
                                                     (140, 200)),
            "Kitchen": pygame.transform.smoothscale(pygame.image.load("Cards/Kitchen.png").convert_alpha(), (140, 200)),
        }

    #Guess logic
    def select_suspicions(self, player, type):
        self.overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()),
                                      pygame.SRCALPHA).convert_alpha()
        position_x = [300, 450, 600]
        self.overlay.fill((35, 45, 60, 128))
        sus_room = {"room": None, "alterable": True}
        types = ["char", "weap", "room"]
        if type == "suggestion":
            for i in self.rooms:
                if i.name == player.in_room:
                    sus_room["room"] = i
            sus_room["alterable"] = False
        self.blank_surf = pygame.Surface((140, 200))
        self.blank_surf.fill((35, 45, 60))

        for i in range(3):
            card = SuggestionCards(self.blank_surf, position_x[i], 350, 140, 200, None, types[i])
            if i == 2 and type == "suggestion":
                card = SuggestionCards(self.card_images[sus_room["room"].name], position_x[i], 350, 140, 200,
                                       sus_room["room"], types[i], False)
                self.room_picked = True
            self.selection_card_list.append(card)

        self.submit = MenuButton(COLOUR, 640, 600, 140, 40, "Submit", 20)

    def suggest_button(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA).convert_alpha()
        overlay.fill((35, 45, 60, 128))
        suggest = MenuButton(COLOUR, 450, 300, 200, 60, "Make suggestion?", 20)
        refuse = MenuButton(COLOUR, 450, 380, 200, 60, "Continue", 20)
        return suggest, refuse, overlay


    def make_suspicion_choice(self, type, positions):
        cards = {
            "char": {
                "loop": 6,
                "names": self.characters
            },
            "weap": {
                "loop": 6,
                "names": self.weapons
            },
            "room": {
                "loop": 9,
                "names": self.rooms
            }
        }

        for i in range(cards[type]["loop"]):
            if type == "weap":
                card = SuggestionCards(self.card_images[cards[type]["names"][i].item_name], positions[i][0],
                                       positions[i][1], 140, 200, cards[type]["names"][i])
            else:
                card = SuggestionCards(self.card_images[cards[type]["names"][i].name], positions[i][0], positions[i][1],
                                       140, 200, cards[type]["names"][i])

            match type:
                case "char":
                    self.char_card_list.append(card)
                case "weap":
                    self.weap_card_list.append(card)
                case "room":
                    self.room_card_list.append(card)


    def handle_events(self):
        # checks for actions by the user.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN and self.menu is None:  # mute button, accessible at any time after menu closes
                if event.key == pygame.K_m:
                    if pygame.mixer.music.get_volume() != 0:
                        pygame.mixer.music.set_volume(0)
                    else:
                        pygame.mixer.music.set_volume(0.2)

            #INPUTTING THE MOVEMENT FUNCTIONALITY BY CURRENT TURN. PHASE LOOP DONE VIA SELF.TURN_PHASE SET AS MOVE.
            if event.type == pygame.KEYDOWN and not self.pre_selection and not self.selecting:
                if not self.activegame or self.get_active_player() != self.currentplayer:  # added 24/04/2026 for locking movement to current turn
                    continue  # added 24/04/2026 for locking movement to current turn
                #SECRET PASSAGES
                elif event.key == pygame.K_RETURN and self.player.in_room in self.secret_passages and not self.pre_selection and self.turn_phase == "ROLL":
                    target_room = self.secret_passages[self.player.in_room]
                    seat = self.room_seats[target_room][0]
                    self.player.col = seat[0]
                    self.player.row = seat[1]
                    self.player.in_room = target_room
                    print(f"Secret passage used: moved to {target_room}")
                    self.moves_left = 0
                    self.turn_phase = "ACTION"
                    self.readytosuggest = True
                    self.pre_selection = True
                    if self.player.character:
                        self.player.character.position = (self.player.col, self.player.row)
                        self.player.character.room = self.player.in_room

                #MOVEMENT FUNCTIONALITY BELOW
                elif (
                        event.key == pygame.K_UP or event.key == pygame.K_w) and self.moves_left > 0 and self.turn_phase == "MOVE":
                    result = self.player.move(0, -1, self.forbidden_tiles, self.doors, self.room_seats, self.room_exits)
                    if result is None:
                        self.message = "Cannot move in there!"
                        self.message_timer = pygame.time.get_ticks()

                    if result in ["MOVED", "ENTERED_ROOM", "LEFT_ROOM"]:
                        self.moves_left -= 1

                    if result == "ENTERED_ROOM":
                        self.pre_selection = True
                        self.moves_left = 0
                        self.turn_phase = "ACTION"
                        self.readytosuggest = True
                        self.suggestbtn, self.passbtn, self.suggest_overlay = self.suggest_button()

                    elif self.moves_left == 0:
                        self.turn_phase = "END"


                elif (
                        event.key == pygame.K_DOWN or event.key == pygame.K_s) and self.moves_left > 0 and self.turn_phase == "MOVE":
                    result = self.player.move(0, 1, self.forbidden_tiles, self.doors, self.room_seats, self.room_exits)
                    if result is None:
                        self.message = "Cannot move in there!"
                        self.message_timer = pygame.time.get_ticks()

                    if result in ["MOVED", "ENTERED_ROOM", "LEFT_ROOM"]:
                        self.moves_left -= 1

                    if result == "ENTERED_ROOM":
                        self.pre_selection = True
                        self.moves_left = 0
                        self.turn_phase = "ACTION"
                        self.readytosuggest = True
                        self.suggestbtn, self.passbtn, self.suggest_overlay = self.suggest_button()

                    elif self.moves_left == 0:
                        self.turn_phase = "END"


                elif (
                        event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.moves_left > 0 and self.turn_phase == "MOVE":
                    result = self.player.move(-1, 0, self.forbidden_tiles, self.doors, self.room_seats, self.room_exits)
                    if result is None:
                        self.message = "Cannot move in there!"
                        self.message_timer = pygame.time.get_ticks()

                    if result in ["MOVED", "ENTERED_ROOM", "LEFT_ROOM"]:
                        self.moves_left -= 1

                    if result == "ENTERED_ROOM":
                        self.pre_selection = True
                        self.moves_left = 0
                        self.turn_phase = "ACTION"
                        self.readytosuggest = True
                        self.suggestbtn, self.passbtn, self.suggest_overlay = self.suggest_button()


                    elif self.moves_left == 0:
                        self.turn_phase = "END"


                elif (
                        event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.moves_left > 0 and self.turn_phase == "MOVE":
                    result = self.player.move(1, 0, self.forbidden_tiles, self.doors, self.room_seats, self.room_exits)
                    if result is None:
                        self.message = "Cannot move in there!"
                        self.message_timer = pygame.time.get_ticks()

                    if result in ["MOVED", "ENTERED_ROOM", "LEFT_ROOM"]:
                        self.moves_left -= 1

                    if result == "ENTERED_ROOM":
                        self.pre_selection = True
                        self.moves_left = 0
                        self.turn_phase = "ACTION"
                        self.readytosuggest = True
                        self.suggestbtn, self.passbtn, self.suggest_overlay = self.suggest_button()

                    elif self.moves_left == 0:
                        self.turn_phase = "END"

                elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER] and self.turn_phase in ["END", "ACTION"]:
                    self.readytosuggest = False
                    self.suggestion_result = None
                    self.end_turn()

            #Menu Selection
            if self.menu != None and event.type == pygame.MOUSEBUTTONDOWN:
                # Catch the action
                action = self.menu.buttonAction(self.mouse)
                print("menu action = ", action)  # for debugging in console
                # If the action is START, get rid of the menu
                if action is not None and action == "Mute":
                    pygame.mixer.music.set_volume(0)
                elif action is not None and action == "Unmute":
                    pygame.mixer.music.set_volume(0.2)
                elif action is not None and (action != "Mute" and action != "Unmute"):
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
                    self.all_players = [self.currentplayer] + self.otherplayers

                    self.turn_index = 0 
                    for person in self.all_players:
                        if "Scarlet" in person.character.name:
                            self.turn_index = self.all_players.index(person)

                     
                    self.rooms = rooms
                    self.weapons = weapons
                    self.characters = characters
                    self.envelope = envelope
                    self.player.character = self.currentplayer.character  # this links visual player to logic of the character
                    self.activegame = True
                    self.menu = None
                    print("Game initialised.")

                    #CPU GRAPHICS
                    cpu_start_positions = [
                        (0, 5),
                        (7, 0),
                        (16, 0),
                        (23, 7),
                        (14, 24)
                    ]
                    cpu_colours = [
                        (128, 0, 128),  # Plum
                        (255, 255, 0),  # Mustard
                        (0, 128, 0),  # Green
                        (0, 0, 255),  # Peacock
                        (255, 255, 255)  # White
                    ]
                    self.visual_players = [self.player]
                    self.player.logic_p = self.currentplayer

                    #Initalises and links visual CPU players to logic data for rendering and elimination
                    for i, cpu in enumerate(self.otherplayers):
                        col, row = cpu_start_positions[i]
                        colour = cpu_colours[i]
                        visual_cpu = Player(col, row, colour, isCPU=True, character=cpu.character)
                        visual_cpu.logic_p = cpu
                        self.visual_players.append(visual_cpu)

            if self.dice_rect.collidepoint(self.mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                if not self.activegame or self.get_active_player() != self.currentplayer:  # added 24/04/2026 for locking movement to current turn
                    print(
                        "Dice cannot be rolled with mouse as not players turn")  # added 24/04/2026 for locking movement to current turn
                    continue  # added 24/04/2026 for locking movement to current turn

                if self.activegame and self.turn_phase == "ROLL":
                    d1 = random.randint(1, 6)
                    d2 = random.randint(1, 6)
                    self.moves_left = d1 + d2
                    self.last_roll = self.moves_left
                    self.roll_display_time = pygame.time.get_ticks()
                    self.turn_phase = "MOVE"

                    self.turn_phase = "MOVE"
                    self.dice_sound.play()

            if event.type == pygame.MOUSEBUTTONDOWN and self.turn_phase == "ACTION" and self.readytosuggest and self.pre_selection:
                res1 = self.suggestbtn.suggest_or_pass(self.mouse)
                res2 = self.passbtn.suggest_or_pass(self.mouse)
                if res1 and not res2:
                    self.selecting = True
                    self.select_suspect = False
                    self.select_weapon = False
                    self.select_room = False
                    self.pre_selection = False
                    self.select_suspicions(self.player, "suggestion")
                elif res2 is False and res1 is not True:
                    self.pre_selection = False
                    self.readytosuggest = False
                    self.turn_phase = "END"
                else:
                    continue

            # Accuse button logic
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Handle Cards Dropdown
                if self.cards_btn.rect.collidepoint(self.mouse):
                    self.show_cards_dropdown = not self.show_cards_dropdown
                    self.card_sound.play()

                #if accuse menu is already open let it handle the clicks.
                elif self.accuse_menu.active:
                    self.accuse_menu.handle(self.mouse, self.envelope)
                    self.click_sound.play()

                #checks if we clicked the Accuse button to open it if menu is closed
                elif self.accuse_btn.rect.collidepoint(self.mouse) and self.activegame and self.get_active_player() == self.currentplayer:
                    print("Accuse button clicked! Opening Menu.")
                    self.accuse_menu.active = True
                    self.click_sound.play()

                elif self.selecting and (
                    not self.select_suspect and not self.select_weapon and not self.select_room):
                    type_selection = None

                    for card in self.selection_card_list:
                        selection = card.handle_click(self.mouse)
                        if selection is not None:
                            type_selection = selection
                            break

                    mousex = self.mouse[0]
                    mousey = self.mouse[1]
                    if not isinstance(type_selection, str):
                        if (mousey >= 350 and mousey <= 550):
                            if mousex < 440 and mousex > 300:
                                type_selection = "char"
                            elif mousex > 600 and mousex < 740:
                                type_selection = None
                            elif mousex >= 450 and mousex <= 590:
                                type_selection = "weap"

                    # Where submit button is clicked
                    if (mousey >= 600 and mousey <= 640) and (
                            self.suspect_picked and self.weapon_picked and self.room_picked):
                        if (mousex >= 640 and mousex <= 780):
                            self.suggestion_result, self.selecting, self.readytosuggest, self.turn_phase, displayer = self.submit.submit_suggestion(
                                self.mouse, self.currentplayer, self.selection_card_list[0].obj,
                                self.selection_card_list[1].obj, self.selection_card_list[2].obj, self.all_players)
                            suggested_character = self.selection_card_list[0].obj
                            target_room = self.player.in_room
                            taken_seats = []

                            #tracking of tiles
                            for p in self.visual_players:
                                taken_seats.append((p.col, p.row))

                            #teleports other players below
                            for teleportedPlayer in self.visual_players:
                                if teleportedPlayer.character == suggested_character:
                                    teleportedPlayer.in_room = target_room

                                    placedintile = False
                                    for seat in self.room_seats[target_room]:
                                        if seat not in taken_seats:
                                            teleportedPlayer.col, teleportedPlayer.row = seat
                                            placedintile = True
                                            break
                                    if not placedintile:
                                        teleportedPlayer.col, teleportedPlayer.row = self.room_seats[target_room][0]

                            if self.suggestion_result:
                                card_name = (
                                    self.suggestion_result.item_name
                                    if hasattr(self.suggestion_result, "item_name")
                                    else self.suggestion_result.name
                                )
                                self.message = f"{displayer.character.name} shows you {card_name}."
                            else:
                                self.message = "No one could disprove your suggestion."
                            self.message_timer = pygame.time.get_ticks()

                    match type_selection:
                        case "char":
                            self.select_suspect = True
                        case "weap":
                            self.select_weapon = True
                        case "room":
                            self.select_room = True

                    if type_selection:
                        self.make_suspicion_choice(type_selection, self.card_pos[type_selection])

                    #CHARACTER PICKING
                if self.select_suspect and event.type == pygame.MOUSEBUTTONDOWN and self.selecting_block == False:
                    suspect = None
                    for char_card in self.char_card_list:
                        selection = char_card.handle_click(self.mouse)
                        if selection is not None:
                            suspect = selection
                            break

                    if suspect:
                        new_card = SuggestionCards(self.card_images[suspect.name], 300, 350, 140, 200, suspect)
                        self.selection_card_list[0] = new_card
                        self.select_suspect = False
                        self.selecting_block = True
                        self.suspect_picked = True

                    # WEAPON PICKING
                if self.select_weapon and event.type == pygame.MOUSEBUTTONDOWN and self.selecting_block == False:
                    weapon = None
                    for weap_card in self.weap_card_list:
                        selection = weap_card.handle_click(self.mouse)
                        if selection is not None:
                            weapon = selection
                            break

                    if weapon:
                        new_card = SuggestionCards(self.card_images[weapon.item_name], 450, 350, 140, 200, weapon)
                        self.selection_card_list[1] = new_card
                        self.select_weapon = False
                        self.selecting_block = True
                        self.weapon_picked = True

                    # ROOM PICKING
                if self.select_room and event.type == pygame.MOUSEBUTTONDOWN and self.selecting_block == False:
                    q_room = None
                    for room_card in self.room_card_list:
                        selection = room_card.handle_click(self.mouse)
                        if selection is not None:
                            q_room = selection
                            break

                    if q_room:
                        new_card = SuggestionCards(self.card_images[q_room.name], 600, 350, 140, 200, q_room)
                        self.selection_card_list[2] = new_card
                        self.select_room = False
                        self.selecting_block = True
                        self.room_picked = True



                # Handles clicks on check sheet
                elif self.activegame and event.type == pygame.MOUSEBUTTONDOWN and not self.selecting and not self.accuse_menu.active:
                    if self.check_sheet.handle_click(self.mouse):
                        self.click_sound.play()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.activegame or self.get_active_player() != self.currentplayer:  # added 24/04/2026 for locking movement to current turn
                        print(
                            "Dice cannot be rolled with spacebar as not players turn")  # added 24/04/2026 for locking movement to current turn
                        continue  # added 24/04/2026 for locking movement to current turn
                    print("Dice has been rolled with spacebar.")

                    if self.activegame and self.turn_phase == "ROLL":  # 26/04/2026 changes made such that roll cannot be done while moving
                        d1 = random.randint(1, 6)
                        d2 = random.randint(1, 6)
                        self.moves_left = d1 + d2
                        print(f"Rolled: {self.moves_left}")
                        self.turn_phase = "MOVE"
                        self.dice_sound.play()

    #Turn system
    def get_active_player(self):
        return self.all_players[self.turn_index]

    def get_next_player(self):
        next_index = (self.turn_index + 1) % len(self.all_players)
        return self.all_players[next_index]

    #CPU DEF FUNCTIONS
    def getvisualplayer(self, logic_player):
        for visual_player in self.visual_players:
            if visual_player.character == logic_player.character:
                return visual_player
        return None

    def get_cpudirection(self, visual_player, target_tile):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        valid_directions = []
        lastmove = self.cpulastmove.get(
            visual_player)  # to avoid the backtracking the cpu was doing going front and back around
        opposite = None
        if lastmove:
            opposite = (-lastmove[0], -lastmove[1])
        for dx, dy in directions:  # checkvalid directions
            new_col = visual_player.col + dx
            new_row = visual_player.row + dy
            if opposite and (dx, dy) == opposite:  # remove backtrack
                continue
            if (new_col, new_row) in self.doors:
                valid_directions.append((dx, dy))
            elif (
                    0 <= new_col < 24
                    and 0 <= new_row < 25
                    and (new_col, new_row) not in self.forbidden_tiles):
                valid_directions.append((dx, dy))
        if not valid_directions:  # lets cpu go backwards if it gets stuck
            for dx, dy in directions:
                new_col = visual_player.col + dx
                new_row = visual_player.row + dy
                if (new_col, new_row) in self.doors:
                    return (dx, dy)
                elif (
                        0 <= new_col < 24
                        and 0 <= new_row < 25
                        and (new_col, new_row) not in self.forbidden_tiles):
                    return (dx, dy)
            return (0, 0)
        # set target door and room to move towards
        dx_to_target = target_tile[0] - visual_player.col
        dy_to_target = target_tile[1] - visual_player.row
        if abs(dx_to_target) > abs(dy_to_target):
            preferred = (1 if dx_to_target > 0 else -1, 0)
        elif dy_to_target != 0:
            preferred = (0, 1 if dy_to_target > 0 else -1)
        else:
            preferred = (0, 0)
        if preferred in valid_directions:  # bias set in direction
            return preferred
        return random.choice(valid_directions)  # else do another direction which is valid

    def run(self):
        while self.running:
            self.handle_events()
            # Renders the game.
            self.screen.fill((0, 0, 0))
            # Gets mouse position while game running
            self.mouse = pygame.mouse.get_pos()
            current_time = pygame.time.get_ticks()
            # Lose Animation Trigger
            if self.accuse_menu.is_gameover and not self.accuse_menu.is_gamewon:
                    if not self.playing and not self.play_finished:
                        self.playing = True
                        self.sprite.frame = 0

            # CPU HANDLING FOR NON-USER TURN (CPU's Turn)
            if self.activegame and self.get_active_player() != self.currentplayer:
                self.cpu_timer += 1
                cpu = self.get_active_player()
                visualcpu = self.getvisualplayer(cpu)

                # CPU step by step actions in CPU Turn
                if visualcpu is not None:  # rolls dice here for each cpu at their turn
                    if not self.cpu_rolled:
                        d1 = random.randint(1, 6)
                        d2 = random.randint(1, 6)
                        self.cpu_moves_left = d1 + d2
                        self.cpu_rolled = True
                        self.last_roll = self.cpu_moves_left
                        self.roll_display_time = pygame.time.get_ticks()

                        # Assigning a room for CPU to target
                        if cpu not in self.cpu_roomtarget or self.cpu_roomtarget[cpu] is None:

                            #CPU prioritizes rooms it has not seen yet.
                            unknown_room_names = [r.name for r in self.rooms if r not in cpu.known_cards]

                            if unknown_room_names:
                                target_room = random.choice(unknown_room_names)
                            else:
                                target_room = random.choice(list(self.room_doors.keys()))

                            self.cpu_roomtarget[cpu] = target_room
                            self.cpu_tiletarget[cpu] = random.choice(self.room_doors[target_room])

                    target_room = self.cpu_roomtarget[cpu]
                    target_tile = self.cpu_tiletarget[cpu]

                    #CPU MOVES WITH DELAY
                    if self.cpu_timer > 25 and self.cpu_moves_left > 0:

                        #If CPU is in a room, bypass pathfinding and just exit the door.
                        if visualcpu.in_room is not None:
                            dx, dy = 0, 0
                            result = visualcpu.move(dx, dy, self.forbidden_tiles, self.doors, self.room_seats,
                                                    self.room_exits)

                        #Normal pathfinding
                        else:
                            dx, dy = self.get_cpudirection(visualcpu, target_tile)
                            if (dx, dy) == (0, 0):
                                self.cpu_moves_left = 0
                                result = None
                            else:
                                result = visualcpu.move(
                                    dx,
                                    dy,
                                    self.forbidden_tiles,
                                    self.doors,
                                    self.room_seats,
                                    self.room_exits
                                )

                        if result in ["MOVED", "ENTERED_ROOM", "LEFT_ROOM"]:
                            self.cpu_moves_left -= 1
                            # Only tracks the last move if they are actually walking in the hallway
                            if result == "MOVED":
                                self.cpulastmove[visualcpu] = (dx, dy)
                        # behavior for when the cpu reaches that room
                        if result == "ENTERED_ROOM":
                            self.cpu_roomtarget[cpu] = None
                            self.cpu_tiletarget[cpu] = None
                            self.cpu_moves_left = 0

                            #CPU accusation + suggestion logic

                            #unknown cards
                            unknownchars = [c for c in self.characters if c not in cpu.known_cards]
                            unknownweapons = [w for w in self.weapons if w not in cpu.known_cards]
                            unknownrooms = [r for r in self.rooms if r not in cpu.known_cards]

                            # Accusation Attempt
                            #when the cpu knows 15 or more cards they take a guess at the missing ones
                            if len(cpu.known_cards) >= 15: #they guess the first item in each unknown list
                                if unknownchars and unknownweapons and unknownrooms:
                                    guesscharacter = unknownchars[0]
                                    guessweapon = unknownweapons[0]
                                    guessroom = unknownrooms[0]
                                else:
                                    self.cpu_moves_left = 0
                                    self.end_turn()
                                    continue

                                #checks against the envelope
                                if (guesscharacter == self.envelope.character and guessweapon == self.envelope.weapon and guessroom == self.envelope.room):
                                    #CPU guesses, game over
                                    pygame.mixer.music.stop()
                                    self.accuse_menu.active = True
                                    self.accuse_menu.is_gameover = True
                                    self.accuse_menu.cpu_winner_name = cpu.character.name
                                    self.accuse_menu.lose_sfx.play()
                                    self.accuse_menu.gameover_timer = pygame.time.get_ticks()
                                    continue #ends turn moves on straight away
                                else:
                                    #If accusation is incorrect then they are eliminated.
                                    print(f"!!! {cpu.character.name} FAILED AND IS OUT !!!")
                                    self.message = f"{cpu.character.name} is ELIMINATED!"
                                    self.message_timer = pygame.time.get_ticks()
                                    cpu.is_eliminated = True
                                    self.end_turn()
                                    continue

                            #the suggestion cpu does without enough information
                            target_room = visualcpu.in_room
                            suggested_char = random.choice(unknownchars or self.characters)
                            suggested_weap = random.choice(unknownweapons or self.weapons)

                            shown_card, displayer = make_suggestion(cpu, target_room, suggested_char, suggested_weap,
                                                         self.all_players)
                            if shown_card:
                                cpu.known_cards.add(shown_card)
                                self.message = f"{cpu.character.name} suggests: {suggested_char.name}, {target_room}, {suggested_weap.item_name}. {displayer.character.name} shows {cpu.character.name} a card!"
                            else:
                                self.message = f"{cpu.character.name} suggests: {suggested_char.name}, {target_room}, {suggested_weap.item_name}. No Evidence!"

                            self.message_timer = pygame.time.get_ticks()

                            #Suggested Characters get teleported into the room.
                            taken_seats = [(p.col, p.row) for p in self.visual_players]
                            for p in self.visual_players:
                                if p.character == suggested_char:
                                    p.in_room = target_room
                                    placedintile = False
                                    for seat in self.room_seats[target_room]: #finds empty place in that room/seat in that room
                                        if seat not in taken_seats:
                                            p.col, p.row = seat
                                            placedintile = True
                                            break
                                    if not placedintile:
                                        p.col, p.row = self.room_seats[target_room][0]
                                    break

                        self.cpu_timer = 0

                    #CPU END TURN
                    if self.cpu_rolled and self.cpu_moves_left == 0:
                        self.cpu_rolled = False
                        self.end_turn()


            #drawing menus
            if self.menu is not None:  # checking if we are on menu screen or board screen
                self.menu.draw(self.screen, self.mouse)

            # This draws everything basically.
            else:
                pygame.draw.rect(self.screen, (140, 185, 130),
                                 (0, 0, self.board.width + self.board.sheet_width, HEADER_HEIGHT))

                # Board and sheet get drawn first
                self.board.draw(self.screen)

                # ticks and debug grid drawn on top of the sheet.
                self.check_sheet.draw(self.screen)

                # Draw UI and Players
                if self.activegame and self.all_players:
                    font = pygame.font.SysFont("courier", 17)
                    active_player = self.get_active_player()
                    active = active_player.character.name
                    room_text = ""
                    if active_player == self.currentplayer and self.player.in_room is not None:
                        room_text = f" - In {self.player.in_room}"
                    text = font.render(f"{active}'s Turn{room_text}", True, (255, 255, 255))
                    text_rect = text.get_rect(
                        midleft=(20, HEADER_HEIGHT // 2)
                    )
                    bg_rect = text_rect.inflate(20, 12)

                    pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
                    self.screen.blit(text, text_rect)
                if self.activegame and self.all_players:
                    small_font = pygame.font.SysFont("courier", 17)
                    next_player = self.get_next_player().character.name

                    if self.turn_phase == "ROLL" and (self.player.in_room in self.secret_passages) and (
                            self.get_active_player() == self.currentplayer):
                        status = "ROLL or ENTER to use shortcut"
                    elif self.turn_phase == "ROLL":
                        status = "ROLL"
                    elif self.turn_phase == "MOVE":
                        status = f"Moves left: {self.moves_left}"
                    elif self.turn_phase == "ACTION":
                        status = "Suggest / Accuse or click ENTER"
                    elif self.turn_phase == "END":
                        status = "Accuse or ENTER to end"
                    else:
                        status = self.turn_phase

                    line1 = small_font.render(status, True, (255, 255, 255))
                    line2 = small_font.render(f"Next: {next_player}", True, (255, 255, 255))

                    box_width = max(line1.get_width(), line2.get_width()) + 20
                    box_height = line1.get_height() + line2.get_height() + 15

                    box_rect = pygame.Rect(
                        self.screen.get_width() - box_width - 20,
                        15,
                        box_width,
                        box_height
                    )

                    pygame.draw.rect(self.screen, (0, 0, 0), box_rect)

                    self.screen.blit(line1, (box_rect.x + 10, box_rect.y + 5))
                    self.screen.blit(line2, (box_rect.x + 10, box_rect.y + 5 + line1.get_height()))

                for vp in self.visual_players:
                    #Only draws the circle if their linked logic player isn't eliminated
                    if not vp.logic_p.is_eliminated:
                        vp.draw(self.screen)

                self.dice.draw(self.screen, self.mouse)
                self.cards_btn.draw(self.screen, self.mouse)

                # UI for dice roll
                if self.last_roll is not None:
                    font = pygame.font.SysFont(None, 23)

                    if self.roll_source:
                        display_text = f"Rolled: {self.last_roll} ({self.roll_source})"
                    else:
                        display_text = f"Rolled: {self.last_roll}"
                    text = font.render(display_text, True, (255, 255, 255))
                    rect = text.get_rect(topleft=(10, HEADER_HEIGHT - 20))
                    bg = rect.inflate(20, 15)
                    pygame.draw.rect(self.screen, (0, 0, 0), bg, border_radius=8)
                    pygame.draw.rect(self.screen, (255, 255, 255), bg, 2, border_radius=8)
                    self.screen.blit(text, rect)

                # CardButton Dropdown Menu running
                if self.show_cards_dropdown and self.currentplayer:
                    cards_in_hand = self.currentplayer.hand
                    if cards_in_hand:
                        card_w = 140
                        card_h = 200
                        padding = 15
                        drop_y = self.cards_btn.rect.bottom
                        max_width = self.screen.get_width() - 40
                        drop_w = min((card_w + padding) * len(cards_in_hand) + padding, max_width)
                        drop_h = card_h + 20
                        drop_x = self.cards_btn.rect.centerx - (drop_w // 2)

                        pygame.draw.rect(self.screen, (50, 50, 50), (drop_x, drop_y, drop_w, drop_h))
                        pygame.draw.rect(self.screen, (255, 255, 255), (drop_x, drop_y, drop_w, drop_h), 2)
                        for i, card in enumerate(cards_in_hand):
                            if hasattr(card, "item_name"):
                                card_name = card.item_name
                            else:
                                card_name = card.name

                            x = drop_x + padding + i * (card_w + padding)
                            if x + card_w > drop_x + drop_w:
                                break  # stop drawing if cards arent in the box anymore
                            y = drop_y + padding

                            if card_name in self.card_images:
                                self.screen.blit(self.card_images[card_name], (x, y))
                            else:
                                text_dropdown = self.dropdown_font.render(card_name, True, (255, 255, 255))
                                self.screen.blit(text_dropdown, (x, y))


                self.accuse_btn.draw(self.screen, self.mouse)

                if self.player.in_room is not None and self.pre_selection:  # BOOKMARK
                    self.screen.blit(self.suggest_overlay, (0, 0))
                    self.suggestbtn.draw(self.screen)
                    self.suggestbtn.mouseHover(self.mouse)
                    self.passbtn.draw(self.screen)
                    self.passbtn.mouseHover(self.mouse)

            if self.message:
                elapsed = pygame.time.get_ticks() - self.message_timer
                if elapsed < 5000:
                    text_surface = self.font.render(self.message, True, (255, 255, 255))
                    text_rect = text_surface.get_rect()

                    text_rect.center = (self.screen.get_width() // 2, self.screen.get_height() - 40)

                    padding = 10
                    bg_rect = text_rect.inflate(padding * 2, padding * 2)
                    # Draws box
                    pygame.draw.rect(self.screen, (30, 30, 30), bg_rect, border_radius=8)
                    pygame.draw.rect(self.screen, (200, 50, 50), bg_rect, 2, border_radius=8)
                    self.screen.blit(text_surface, text_rect)
                else:
                    self.message = ""

            self.accuse_menu.draw(self.screen, self.card_images)

            if self.playing:
                finished = self.sprite.draw(self.screen)

                if finished:
                    self.playing = False
                    self.play_finished = True

            if self.selecting:
                self.screen.blit(self.overlay, (0, 0))

                if not self.select_suspect and not self.select_weapon and not self.select_room:
                    for card in self.selection_card_list:
                        card.draw(self.screen, self.mouse)
                    self.submit.draw(self.screen)
                    if self.suspect_picked and self.weapon_picked and self.room_picked:
                        self.submit.mouseHover(self.mouse)

                if self.select_suspect:
                    for card in self.char_card_list:
                        card.draw(self.screen, self.mouse)
                    self.selecting_block = False

                elif self.select_weapon:
                    for card in self.weap_card_list:
                        card.draw(self.screen, self.mouse)
                    self.selecting_block = False

                elif self.select_room:
                    for card in self.room_card_list:
                        card.draw(self.screen, self.mouse)
                    self.selecting_block = False

            pygame.display.flip()
        pygame.quit()

    def end_turn(self):
        #Move to the next player index
        self.turn_index += 1

        # Reset to 0 if we go past the last player
        if self.turn_index >= len(self.all_players):
            self.turn_index = 0

        # Skip anyone who is eliminated
        while self.all_players[self.turn_index].is_eliminated:
            self.turn_index += 1
            if self.turn_index >= len(self.all_players):
                self.turn_index = 0
                
        self.moves_left = 0
        self.turn_phase = "ROLL"
        self.cpu_timer = 0
        self.cpu_moves_left = 0
        self.cpu_rolled = False
        self.cpulastmove = {}
        self.suspect_picked = False
        self.weapon_picked = False
        self.room_picked = False
        self.selection_card_list = []


class Dice:
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
        if self.rect.collidepoint(mouse):
            # draw the solid original
            surface.blit(self.image, (self.x, self.y))
        else:
            # draw the transparent copy
            surface.blit(self.image_copy, (self.x, self.y))


class CardsButton:
    #Loads up and scales the card button .png
    def __init__(self, x, y):
        self.image = pygame.image.load('Assets/HandCards.png')
        self.image = pygame.transform.smoothscale(self.image, (150, 80))
        
        # Transparent Effect
        self.image_hover = self.image.copy()
        self.image_hover.set_alpha(150)


        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    #Renders button to screen and draws it.
    def draw(self, surface, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            surface.blit(self.image, self.rect.topleft)
        else:
            surface.blit(self.image_hover, self.rect.topleft)



class AccuseButton:
    #Initalises and loads up the Accuse.png
    def __init__(self, x, y):
        self.image = pygame.image.load('Assets/Accuse.png')
        self.image = pygame.transform.smoothscale(self.image, (150, 120))
        
        # Transparent effect
        self.image_hover = self.image.copy()
        self.image_hover.set_alpha(150)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    #Renders and draws the .png to the screen.
    def draw(self, surface, mouse_pos):
        # Checks if the mouse is currently inside the button
        if self.rect.collidepoint(mouse_pos):
            # If hovering, draw the normal, solid version
            surface.blit(self.image, self.rect.topleft)
        else:
            # If not hovering, draw the slightly transparent version
            surface.blit(self.image_hover, self.rect.topleft)


class AccuseMenu:
    def __init__(self, screen_width, screen_height):
        self.font = pygame.font.SysFont("courier", 30)
        self.small_font = pygame.font.SysFont("courier", 17)
        self.giant_font = pygame.font.SysFont("courier", 25)

        # SoundBytes
        self.win_sfx = pygame.mixer.Sound('Assets/victory.mp3')
        self.lose_sfx = pygame.mixer.Sound('Assets/lose.mp3')

        # TIMER AND CHECKS
        self.is_gameover = False
        self.gameover_timer = 0
        self.is_gamewon = False
        self.cpu_winner_name = None

        # Checks if menu is currently open or not.
        self.active = False

        # Position of Accuse Menu
        self.width = 800
        self.height = 550
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2

        # Endless cycles for suspect, weapon and room
        self.suspect_cycle = itertools.cycle(["Scarlet", "Plum", "Mustard", "Peacock", "Green", "White"])
        self.weapon_cycle = itertools.cycle(["Candlestick", "Dagger", "Revolver", "Rope", "Lead Pipe", "Wrench"])
        self.room_cycle = itertools.cycle(
            ["Study", "Hall", "Lounge", "Library", "Billiard Room", "Dining Room", "Conservatory", "Ballroom",
             "Kitchen"])

        # First item in each cycle to start
        self.current_suspect = next(self.suspect_cycle)
        self.current_weapon = next(self.weapon_cycle)
        self.current_room = next(self.room_cycle)

        # Clickable areas for Suspect, weapon and room.
        self.suspect_rect = pygame.Rect(self.x + 33, self.y + 80, 200, 40)
        self.weapon_rect = pygame.Rect(self.x + 300, self.y + 80, 200, 40)
        self.room_rect = pygame.Rect(self.x + 566, self.y + 80, 200, 40)

        self.submit_rect = pygame.Rect(self.x + 250, self.y + 450, 130, 40)
        self.cancel_rect = pygame.Rect(self.x + 420, self.y + 450, 130, 40)
        self.result_message = ""

    #renders the menu.
    def draw(self, surface, card_images):
        if not self.active:
            return

        # Menu Background
        pygame.draw.rect(surface, (40, 40, 40), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y, self.width, self.height), 3)

        if self.is_gameover:
            # Timer Countdown
            seconds_left = 5 - ((pygame.time.get_ticks() - self.gameover_timer) // 1000)

            if seconds_left <= 0:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

            # Giant text highlighting whether you have won or lost
            if self.is_gamewon:
                text = f"YOU WIN! CONGRATULATIONS! Closing in {seconds_left}..."
                color = (0, 255, 0)
            elif self.cpu_winner_name:
                text = f"{self.cpu_winner_name.upper()} SOLVED IT! YOU LOSE! Closing in {seconds_left}..."
                color = (255, 0, 0)
            else:
                text = f"WRONG COMBINATION! YOU LOSE! Closing in {seconds_left}..."
                color = (255, 0, 0)

            title_surf = self.giant_font.render(text, True, color)
            title_rect = title_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            surface.blit(title_surf, title_rect)



        else:
            # Normal menu state
            # Title
            title = self.font.render('Do you wish to make an Accusation?', True, (255, 255, 255))
            surface.blit(title, (self.x + 105, self.y + 20))

            # Room Button
            pygame.draw.rect(surface, (100, 100, 100), self.room_rect)
            pygame.draw.rect(surface, (255, 255, 255), self.room_rect, 2)
            text_surf = self.small_font.render(f"Room: {self.current_room}", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.room_rect.center)
            surface.blit(text_surf, text_rect)

            # Weapon Button
            pygame.draw.rect(surface, (100, 100, 100), self.weapon_rect)
            pygame.draw.rect(surface, (255, 255, 255), self.weapon_rect, 2)
            text_surf = self.small_font.render(f"Weapon: {self.current_weapon}", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.weapon_rect.center)
            surface.blit(text_surf, text_rect)

            # Suspect Button
            pygame.draw.rect(surface, (100, 100, 100), self.suspect_rect)
            pygame.draw.rect(surface, (255, 255, 255), self.suspect_rect, 2)
            text_surf = self.small_font.render(f"Suspect: {self.current_suspect}", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.suspect_rect.center)
            surface.blit(text_surf, text_rect)

            # Accuse Button
            pygame.draw.rect(surface, (150, 50, 50), self.submit_rect)
            pygame.draw.rect(surface, (255, 255, 255), self.submit_rect, 2)
            text_surf = self.small_font.render("Accuse!", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.submit_rect.center)
            surface.blit(text_surf, text_rect)

            # Go Back Button
            pygame.draw.rect(surface, (80, 80, 80), self.cancel_rect)
            pygame.draw.rect(surface, (255, 255, 255), self.cancel_rect, 2)
            text_surf = self.small_font.render("Go Back", True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=self.cancel_rect.center)
            surface.blit(text_surf, text_rect)

            # IMAGES
            self.draw_image(surface, self.current_suspect, card_images, self.suspect_rect.x + 30, self.y + 140)
            self.draw_image(surface, self.current_weapon, card_images, self.weapon_rect.x + 30, self.y + 140)
            self.draw_image(surface, self.current_room, card_images, self.room_rect.x + 30, self.y + 140)

            # Warning Text
            warningText = "Caution! If you choose the wrong combination, then you will lose the game!"
            warningSurf = self.small_font.render(warningText, True, (255, 255, 0))
            warningRect = warningSurf.get_rect(center=(self.x + self.width // 2, self.y + 400))
            surface.blit(warningSurf, warningRect)

    # Draws the card images in the menu
    def draw_image(self, surface, item_name, card_images, x, y):
        img = item_name
        if img in card_images:
            surface.blit(card_images[img], (x, y))

    #Event handling on mouse click.
    def handle(self, mouse_pos, envelope):
        # If game is over, all clicks get ignored.
        if not self.active or self.is_gameover:
            return False

        if self.suspect_rect.collidepoint(mouse_pos):
            self.current_suspect = next(self.suspect_cycle)

        elif self.weapon_rect.collidepoint(mouse_pos):
            self.current_weapon = next(self.weapon_cycle)

        elif self.room_rect.collidepoint(mouse_pos):
            self.current_room = next(self.room_cycle)

        elif self.cancel_rect.collidepoint(mouse_pos):
            self.active = False
            self.result_message = ""

        elif self.submit_rect.collidepoint(mouse_pos):
            self.check_accusation(envelope)

        return True
    
    def check_accusation(self, envelope):
        env_suspect = envelope.character.name
        env_weapon = envelope.weapon.item_name
        env_room = envelope.room.name

        pygame.mixer.music.stop()

        # Checks envelope to see if its correct or incorrect
        if self.current_suspect == env_suspect and self.current_weapon == env_weapon and self.current_room == env_room:
            print("YOU WIN!")
            self.is_gamewon = True
            self.win_sfx.play()
        
        else:
            print("YOU LOSE!")
            self.is_gamewon = False
            self.lose_sfx.play()

        # Keeps track of game over state and timer.
        self.is_gameover = True
        self.gameover_timer = pygame.time.get_ticks()

#Starting Main Menu
class Menu:
    def __init__(self):
        self.image = pygame.image.load('Assets/Tudor-Mansion.png')
        self.disp_surf = pygame.display.get_surface()
        x = self.disp_surf.get_width()
        y = self.disp_surf.get_height()
        self.image = pygame.transform.smoothscale(self.image, (x, y))
        self.width = x
        self.height = y
        self.logo = pygame.image.load('Assets/CLUE_logo.png')
        self.logo_width = int(self.logo.get_width())
        self.logo_height = int(self.logo.get_height())
        self.logo = pygame.transform.smoothscale(self.logo, (self.logo_width, self.logo_height))
        self.logo_rect = self.logo.get_rect()
        self.logo_rect.centerx = pygame.display.get_surface().get_rect().centerx
        self.logo_rect.y = self.height * 0.1
        self.start_btn = MenuButton(COLOUR, self.width // 2 - 70, self.height // 2 - 60, 160, 60, "Start")
        self.mute_btn = MenuButton(COLOUR, self.width // 2 - 70, self.height // 2 + 15, 160, 60, "Mute Music", 22)
        self.exit_btn = MenuButton(COLOUR, self.width // 2 - 70, self.height // 2 + 90, 160, 60, "Exit")

    #Button actions for the menu.
    def buttonAction(self, mouse):
        start_action = self.start_btn.changeGameState(mouse)
        mute_action = self.mute_btn.changeGameState(mouse)
        exit_action = self.exit_btn.changeGameState(mouse)
        if start_action is not None:
            return start_action
        elif mute_action is not None:
            return mute_action

        return None

    
    # Draws background from top-left
    def draw(self, surface, mouse):
        # Gets mouse position
        self.mouse = mouse
        
        surface.blit(self.image, (0, 0))
        surface.blit(self.logo, (self.logo_rect))
        self.start_btn.draw(self.disp_surf)
        self.start_btn.mouseHover(self.mouse)
        self.mute_btn.draw(self.disp_surf)
        self.mute_btn.mouseHover(self.mouse)
        self.exit_btn.draw(self.disp_surf)
        self.exit_btn.mouseHover(self.mouse)



class CheckSheetFunction:
    def __init__(self, start_x):
        self.start_x = start_x
        # Width and height of each cell within the sheet
        self.cell_w = 49
        self.cell_h = 16.5

        # Starting positions on Y axis for each of the grids.
        self.y_suspects = 174.5
        self.y_weapons = 310
        self.y_rooms = 440

        # Font
        pygame.font.init()
        self.font = pygame.font.SysFont('courier', 17)

        # X render
        self.x_image = self.font.render("X", True, (0, 0, 0))

        # Centers the X right in the middle of a cell.
        self.center_offset_x = self.cell_w // 2
        self.center_offset_y = self.cell_h // 2

        # Dictionary to check rows/col per grid.
        self.sections = {
            "Suspects": {"y": self.y_suspects, "rows": 6, "cols": 6},
            "Weapons": {"y": self.y_weapons, "rows": 6, "cols": 6},
            "Rooms": {"y": self.y_rooms, "rows": 9, "cols": 6}
        }

        # Keeps track of boxes that have been ticked.
        self.ticks = set()

    def handle_click(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos

        for section, data in self.sections.items():
            start_y = data["y"]

            # Loops through every possible cell in this section
            for row in range(data["rows"]):
                for col in range(data["cols"]):
                    # Calculate the top-left corner of this specific cell
                    cell_x = self.start_x + (col * self.cell_w)
                    cell_y = start_y + (row * self.cell_h)

                    # Creates a hitbox for the cell
                    cell_rect = pygame.Rect(cell_x, cell_y, self.cell_w, self.cell_h)

                    # Check if the mouse click happened inside this cell's rect
                    if cell_rect.collidepoint(mouse_x, mouse_y):
                        cell_id = (section, row, col)

                        # Toggle Logic with ticks
                        if cell_id in self.ticks:
                            self.ticks.remove(cell_id)  # Remove tick if already clicked
                        else:
                            self.ticks.add(cell_id)  # Add tick if empty

                        return True
        return False
        
    #Draws the X in the middle of cell for checksheet.
    def draw(self, surface):
        for (section, row, col) in self.ticks:
            # Find the center
            start_y = self.sections[section]["y"]
            center_x = self.start_x + (col * self.cell_w) + self.center_offset_x
            center_y = start_y + (row * self.cell_h) + self.center_offset_y

            # Creates hitbox
            x_rect = self.x_image.get_rect(center=(center_x, center_y))
            surface.blit(self.x_image, x_rect)


#Buttons for the menu
class MenuButton:
    def __init__(self, colour, pos_x, pos_y, width, height, text='', font_size=30):
        self.color = colour
        self.width = width
        self.height = height
        self.text = text
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.size = font_size

    def draw(self, surface):
        # draw the button as a rectangle
        pygame.draw.rect(surface, self.color, (self.pos_x, self.pos_y, self.width, self.height), 0)

        if self.text != '':  # checks text isn't empty
            font = pygame.font.SysFont("papyrus", self.size)
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
                    print("Start game!")
                    from PickYourCharacter import MainMenu2
                    char_menu = MainMenu2()
                    selectedchar = char_menu.run()
                    return selectedchar
                elif self.text == "Exit":
                    pygame.quit()
                elif self.text == "Mute Music":
                    self.text = "Unmute Music"
                    return "Mute"
                elif self.text == "Unmute Music":
                    self.text = "Mute Music"
                    return "Unmute"
        return None

    def submit_suggestion(self, position, player, suspect, weapon, guess_room, all_players):
        if position[0] > self.pos_x and position[0] < self.pos_x + self.width:
            if position[1] > self.pos_y and position[1] < self.pos_y + self.height:
                if suspect and weapon and guess_room:
                    shown_card, displayer = make_suggestion(
                        player,
                        guess_room.name,
                        suspect,
                        weapon,
                        all_players
                    )
                    return shown_card, False, False, "END", displayer

    def suggest_or_pass(self, position):
        if position[0] > self.pos_x and position[0] < self.pos_x + self.width:
            if position[1] > self.pos_y and position[1] < self.pos_y + self.height:
                if self.text == "Make suggestion?":
                    return True
                else:
                    return False

#Clickable cards for suggestion screen.
class SuggestionCards:
    def __init__(self, image, x, y, width, height, obj, type=None, alterable=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
        self.obj = obj
        self.alterable = alterable
        self.type = type
        # creates a Rect with the same dimensions as the image
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, mouse):
        surface.blit(self.image, (self.x, self.y))
        if self.rect.collidepoint(mouse) and self.alterable:
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 3)

    def handle_click(self, mouse):
        if self.alterable != True:
            return None

        if self.obj and self.alterable:
            if self.rect.collidepoint(mouse) and self.alterable:
                return self.obj

        elif not self.obj and self.alterable:
            if self.rect.collidepoint(mouse) and self.alterable:
                return self.type



if __name__ == "__main__":
    clue_game = Game()
    clue_game.run()
