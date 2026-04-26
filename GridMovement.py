import random

import pygame

from main import setup_game  # for linking gridcontroller

# Constants, OFFSET X, Y and TILE_SIZE determine the grid layout. Sheet is for the squares inside the sheet.
SCALE = 0.6
TILE_SIZE = 46.5 * SCALE
OFFSET_X = 37 * SCALE
HEADER_HEIGHT = 80
OFFSET_Y = (18 * SCALE) + HEADER_HEIGHT

# Button colours
COLOUR = "#462779"
COLOUR_HOVER = "#9040BA"


class Player:
    def __init__(self, col=0, row=0, color=(255, 255, 255), isCPU=False, character=None):
        self.col = col
        self.in_room = None
        self.row = row
        self.color = color
        self.isCPU = isCPU  # set to none if not user.
        self.character = character
        self.hand = []

    def move(self, dx, dy, forbidden_zones, doors, room_seats, room_exits):
        #if player is inside room, first move them to the rooms exit
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
            self.in_room = entered_room  # Save this for main.py logic later!

            return "ENTERED_ROOM"

        # Forbidden tile Check
        if (new_col, new_row) in forbidden_zones:
            print("Cannot move in there!")
            return None

        # Boundary check (so they don't walk off the screen)
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
        self.sheet_height = self.height - 200
        self.sheet = pygame.transform.smoothscale(self.sheet, (self.sheet_width, self.sheet_height))

    def draw(self, surface):
        # Draw the board and sheet shifted down by HEADER_HEIGHT
        surface.blit(self.image, (0, HEADER_HEIGHT))
        surface.blit(self.sheet, (self.width, HEADER_HEIGHT))

        # Fill the empty space under the sheet with green.
        pygame.draw.rect(
            surface,
            (140, 185, 130),
            (self.width, self.sheet_height + HEADER_HEIGHT, self.sheet_width, self.height - self.sheet_height)
        )

        # Visual Debug: To see the grid lines.
        # for r in range(25):
        # for c in range(24):
        # rect = (OFFSET_X + c * TILE_SIZE, OFFSET_Y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
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

        # Board init
        self.board = Board()
        win_width = self.board.width + self.board.sheet_width
        self.screen = pygame.display.set_mode((win_width, self.board.height + HEADER_HEIGHT))
        self.menu = Menu()

        # Header, Dice and Accuse button
        #self.turn_image = pygame.image.load('Assets/Your turn.png')   ####MADE REDUNDANT BY NEW YOUR TURN IMAGE
        #self.turn_image = pygame.transform.smoothscale(self.turn_image, (400, 60))   ###MADE REDUNDANT BY NEW YOUR TURN GRAPHIC
        item_y = self.board.sheet_height + 50 + HEADER_HEIGHT
        dice_x = self.board.width + 40
        accuse_x = self.board.width + 220
        self.dice = Dice(dice_x, item_y)
        self.dice_rect = self.dice.rect
        self.accuse_btn = AccuseButton(accuse_x, item_y)

        self.check_sheet = CheckSheetFunction(self.board.width + 67)

        # Determines where the player starts and color.
        self.visual_players = []
        self.player = Player(11, 11, (255, 0, 0))  # Red player
        self.running = True
        # Gets mouse position
        self.mouse = pygame.mouse.get_pos()

        self.sprite = Sprite_Chars(win_width, self.board.height)

        ###cpu-related
        self.cpu_timer = 0
        self.cpu_moves_left = 0
        self.cpu_rolled = False
        self.cpu_roomtarget = {}
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

            ####    INPUTTING THE MOVEMENT FUNCTIONALITY BY CURRENT TURN. PHASE LOOP DONE VIA SELF.TURN_PHASE SET AS MOVE.
            if event.type == pygame.KEYDOWN:
                if not self.activegame or self.get_active_player() != self.currentplayer:  # added 24/04/2026 for locking movement to current turn
                    return  # added 24/04/2026 for locking movement to current turn
                ###SECRET PASSAGES
                elif event.key == pygame.K_s and self.player.in_room in self.secret_passages:
                    target_room = self.secret_passages[self.player.in_room]
                    seat = self.room_seats[target_room][0]
                    self.player.col = seat[0]
                    self.player.row = seat[1]
                    self.player.in_room = target_room
                    print(f"Secret passage used: moved to {target_room}")
                    self.moves_left = 0
                    self.turn_phase = "END"
                    if self.player.character:
                        self.player.character.position = (self.player.col, self.player.row)
                        self.player.character.room = self.player.in_room
                    ##MOVEMENT FUNCTIONALITY BELOW
                elif event.key == pygame.K_UP and self.moves_left > 0 and self.turn_phase == "MOVE":
                    result = self.player.move(0, -1, self.forbidden_tiles, self.doors, self.room_seats, self.room_exits);
                    if result in ["MOVED", "ENTERED_ROOM", "LEFT_ROOM"]:
                        self.moves_left -= 1
                    if result == "ENTERED_ROOM":
                        self.moves_left = 0
                        self.turn_phase = "END"
                    if self.moves_left == 0:
                        self.turn_phase = "END"
                elif event.key == pygame.K_DOWN and self.moves_left > 0 and self.turn_phase == "MOVE":
                    result = self.player.move(0, 1, self.forbidden_tiles, self.doors, self.room_seats, self.room_exits);
                    if result in ["MOVED", "ENTERED_ROOM", "LEFT_ROOM"]:
                        self.moves_left -= 1
                    if result == "ENTERED_ROOM":
                        self.moves_left = 0
                        self.turn_phase = "END"
                    if self.moves_left == 0:
                        self.turn_phase = "END"

                elif event.key == pygame.K_LEFT and self.moves_left > 0 and self.turn_phase == "MOVE":
                    result = self.player.move(-1, 0, self.forbidden_tiles, self.doors, self.room_seats, self.room_exits);
                    if result in ["MOVED", "ENTERED_ROOM", "LEFT_ROOM"]:
                        self.moves_left -= 1
                    if result == "ENTERED_ROOM":
                        self.moves_left = 0
                        self.turn_phase = "END"
                    if self.moves_left == 0:
                        self.turn_phase = "END"
                elif event.key == pygame.K_RIGHT and self.moves_left > 0 and self.turn_phase == "MOVE":
                    result = self.player.move(1, 0, self.forbidden_tiles, self.doors, self.room_seats, self.room_exits);
                    if result in ["MOVED", "ENTERED_ROOM", "LEFT_ROOM"]:
                        self.moves_left -= 1
                    if result == "ENTERED_ROOM":
                        self.moves_left = 0
                        self.turn_phase = "END"
                    if self.moves_left == 0:
                        self.turn_phase = "END"

                elif event.key == pygame.K_RETURN and self.turn_phase == "END":
                    print("TURN ENDED")
                    self.end_turn()

            ###        MENU SELECTION BELOW
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

                    ###CPU GRAPHICS
                    cpu_start_positions = [
                        (0, 6),
                        (7, 0),
                        (16, 0),
                        (23, 7),
                        (14, 24)
                    ]
                    cpu_colours = [
                        (128, 0, 128),  #Plum
                        (255, 255, 0),  #Mustard
                        (0, 128, 0),  #Green
                        (0, 0, 255),  #Peacock
                        (255, 255, 255)  #White
                    ]
                    self.visual_players = [self.player]
                    for i, cpu in enumerate(self.otherplayers):
                        col, row = cpu_start_positions[i]
                        colour = cpu_colours[i]
                        visual_cpu = Player(col, row, colour, isCPU=True, character=cpu.character)
                        self.visual_players.append(visual_cpu)

            if self.dice_rect.collidepoint(self.mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                if not self.activegame or self.get_active_player() != self.currentplayer:  # added 24/04/2026 for locking movement to current turn
                    print(
                        "Dice cannot be rolled with mouse as not players turn")  # added 24/04/2026 for locking movement to current turn
                    return  # added 24/04/2026 for locking movement to current turn

                print("Dice has been rolled with mouse.")  # debugging
                if self.activegame and self.turn_phase == "ROLL":
                 self.moves_left = random.randint(2, 12)
                 print(f"Rolled: {self.moves_left}")

                 self.turn_phase = "MOVE"

            if event.type == pygame.MOUSEBUTTONDOWN:
                 self.check_sheet.handle_click(self.mouse)


            # Accuse button logic
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hasattr(self, 'accuse_btn') and self.accuse_btn.rect.collidepoint(self.mouse):
                    # Check if the game has started and if it's the active player's turn
                    if self.activegame and self.get_active_player() == self.currentplayer:
                        print("Accuse button clicked!")

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.activegame or self.get_active_player() != self.currentplayer:  # added 24/04/2026 for locking movement to current turn
                        print(
                            "Dice cannot be rolled with spacebar as not players turn")  # added 24/04/2026 for locking movement to current turn
                        return  # added 24/04/2026 for locking movement to current turn
                    print("Dice has been rolled with spacebar.")
                    if self.activegame and self.turn_phase == "ROLL": #26/04/2026 changes made such that roll cannot be done while moving
                        self.moves_left = random.randint(2, 12)
                        print(f"Rolled: {self.moves_left}")
                        self.turn_phase = "MOVE"

    ###for turn system below VVV
    def get_active_player(self):
        return self.all_players[self.turn_index]

    def get_next_player(self):
        next_index = (self.turn_index + 1) % len(self.all_players)
        return self.all_players[next_index]


##CPU DEF FUNCTIONS
    def getvisualplayer(self, logic_player):
        for visual_player in self.visual_players:
            if visual_player.character == logic_player.character:
                return visual_player
        return None

    def get_cpudirection(self, visual_player, target_tile):
        dx = target_tile[0] - visual_player.col
        dy = target_tile[1] - visual_player.row
        #if target_room == None:
            #target_room = random.choice(list(self.room_seats.keys()))
        if abs(dx) > abs(dy):
            return (1 if dx > 0 else -1, 0)
        elif dy != 0:
            return (0, 1 if dy > 0 else -1)
        return (0, 0)

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

            # CPU HANDLING FOR NON-USER TURN (CPU's Turn)
            if self.activegame and self.get_active_player() != self.currentplayer:
                self.cpu_timer += 1
                cpu = self.get_active_player()
                visualcpu = self.getvisualplayer(cpu)
#CPU step by step actions in CPU Turn
                if visualcpu is not None: #rolls dice here for each cpu at their turn
                    if not self.cpu_rolled:
                        self.cpu_moves_left = random.randint(2, 12)
                        self.cpu_rolled = True
                        print(f"{cpu.character.name} (CPU) rolled {self.cpu_moves_left}")

                    #Assigning a room for CPU to target
                    if cpu not in self.cpu_roomtarget or self.cpu_roomtarget[cpu] is None:
                        self.cpu_roomtarget[cpu] = random.choice(list(self.room_exits.keys()))

                    target_room = self.cpu_roomtarget[cpu]
                    target_tile = self.room_exits[target_room]

                    #CPU MOVES W DELAY
                    if self.cpu_timer > 70 and self.cpu_moves_left > 0:
                        dx, dy = self.get_cpudirection(visualcpu, target_tile)
                        result = visualcpu.move(
                            dx,
                            dy,
                            self.forbidden_tiles,
                            self.doors,
                            self.room_seats,
                            self.room_exits
                        )
                        if result is None: #If CPU goes into the wall or something
                            dx, dy = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
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
                        #behavior for when the cpu reaches that room
                        if result == "ENTERED_ROOM":
                            self.cpu_roomtarget[cpu] = None
                            self.cpu_moves_left = 0
                            ###CPU WILL NEED TO MAKE ACCUSATION IF RELEVANT MAYBE??? CHECK

                        self.cpu_timer = 0

                    #CPUENDTURN
                    if self.cpu_rolled and self.cpu_moves_left == 0:
                        self.cpu_rolled = False
                        self.end_turn()

            ######### drawing menus
            if self.menu is not None:  # checking if we are on menu screen or board screen
                self.menu.draw(self.screen, self.mouse)

            # This draws everything basically.
            else:
                pygame.draw.rect(self.screen, (140, 185, 130),
                                 (0, 0, self.board.width + self.board.sheet_width, HEADER_HEIGHT))

                #Board and sheet get drawn first
                self.board.draw(self.screen)

                #ticks and debug grid drawn on top of the sheet.
                self.check_sheet.draw(self.screen)

                # Draw the turn image at the top ###REDUNDANT NOW AS NEW TURN GRAPHIC IS DONE DYNAMICALLY
                #######if hasattr(self, 'turn_image'):
                #######    img_x = (self.board.width + self.board.sheet_width) // 2 - (self.turn_image.get_width() // 2)
                #######    img_y = HEADER_HEIGHT // 2 - (self.turn_image.get_height() // 2)
                #######    self.screen.blit(self.turn_image, (img_x, img_y))

                #Draw UI and Players
                ##TURN DISPLAY
                if self.activegame and self.all_players:
                    font = pygame.font.SysFont(None, 42)
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
                    small_font = pygame.font.SysFont(None, 28)

                    next_player = self.get_next_player().character.name

                    if self.turn_phase == "ROLL":
                        status = "ROLL"
                    elif self.turn_phase == "MOVE":
                        status = f"Moves left: {self.moves_left}"
                    elif self.turn_phase == "END":
                        status = "Make Accusation or ENTER to end"
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

               # self.player.draw(self.screen) ###HASHING FOR NOW TO FOR LOOP THE CPU WITH PLAYERS
                for visual_player in self.visual_players:
                    visual_player.draw(self.screen)
                self.dice.draw(self.screen, self.mouse)

                if hasattr(self, 'accuse_btn'):
                    self.accuse_btn.draw(self.screen, self.mouse)

                if self.playing:
                    finished = self.sprite.draw(self.screen)

                    if finished:
                        self.playing = False



            pygame.display.flip()
        pygame.quit()

    def end_turn(self):
        print(f"Ending turn: {self.get_active_player().character.name}")

        self.turn_index = (self.turn_index + 1) % len(self.all_players)
        self.moves_left = 0
        self.turn_phase = "ROLL"

        print(f"Next player: {self.get_active_player().character.name}")


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
        if self.rect.collidepoint(mouse):
            # draw the solid original
            surface.blit(self.image, (self.x, self.y))
        else:
            # draw the transparent copy
            surface.blit(self.image_copy, (self.x, self.y))


class AccuseButton:
    def __init__(self, x, y):
        self.image = pygame.image.load('Assets/Accuse.png')
        self.image = pygame.transform.smoothscale(self.image, (150, 120))
        # Transparent effect
        self.image_hover = self.image.copy()
        self.image_hover.set_alpha(150)

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self, surface, mouse_pos):
        # Check if the mouse is currently inside the button's picture frame
        if self.rect.collidepoint(mouse_pos):
            # If hovering, draw the normal, solid version
            surface.blit(self.image, self.rect.topleft)
        else:
            # If not hovering, draw the slightly transparent version
            surface.blit(self.image_hover, self.rect.topleft)


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


class CheckSheetFunction:
    def __init__(self,start_x):
        self.start_x = start_x
        # Width and height of each cell within the sheet
        self.cell_w = 49
        self.cell_h = 16.5

        #Starting positions on Y axis for each of the grids.
        self.y_suspects = 174.5
        self.y_weapons = 310
        self.y_rooms = 440

        #Font
        pygame.font.init()
        self.font = pygame.font.SysFont(None, 25)

        #X render
        self.x_image = self.font.render("X", True, (0, 0, 0))

        #Centers the X right in the middle of a cell.
        self.center_offset_x = self.cell_w // 2
        self.center_offset_y = self.cell_h // 2

        # Dictionary to check rows/col per grid.
        self.sections = {
            "Suspects": {"y": self.y_suspects, "rows": 6, "cols": 6},
            "Weapons": {"y": self.y_weapons, "rows": 6, "cols": 6},
            "Rooms": {"y": self.y_rooms, "rows": 9, "cols": 6}
        }

        #Keeps track of boxes that have been ticked.
        self.ticks = set()

    def handle_click(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos

        for section, data in self.sections.items():
            start_y = data["y"]

            # Loop through every possible cell in this section
            for row in range(data["rows"]):
                for col in range(data["cols"]):
                    # Calculate the top-left corner of this specific cell
                    cell_x = self.start_x + (col * self.cell_w)
                    cell_y = start_y + (row * self.cell_h)

                    # Creates a hitbox for the cell
                    cell_rect = pygame.Rect(cell_x, cell_y, self.cell_w, self.cell_h)

                    # Check if the mouse click happened inside this cell's rectangle
                    if cell_rect.collidepoint(mouse_x, mouse_y):
                        cell_id = (section, row, col)

                        # Toggle Logic with ticks
                        if cell_id in self.ticks:
                            self.ticks.remove(cell_id)  # Remove tick if already clicked
                        else:
                            self.ticks.add(cell_id)  # Add tick if empty

                        return

    def draw(self, surface):
        for (section, row, col) in self.ticks:
            #Find the center
            start_y = self.sections[section]["y"]
            center_x = self.start_x + (col * self.cell_w) + self.center_offset_x
            center_y = start_y + (row * self.cell_h) + self.center_offset_y

            #Creates hitbox
            x_rect = self.x_image.get_rect(center=(center_x, center_y))
            surface.blit(self.x_image, x_rect)




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
