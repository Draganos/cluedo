import pygame
from main import setup_game #for linking gridcontroller

#This file contains both the Board game screen and the title screen.

#Constants, OFFSET X, Y and TILE_SIZE determine the grid layout.
SCALE = 0.6
TILE_SIZE = 46.5 * SCALE
OFFSET_X = 37 * SCALE
OFFSET_Y = 18 * SCALE
#Button colours
COLOUR = "#462779"
COLOUR_HOVER = "#9040BA"

class Player:
    def __init__(self, col=0, row=0, color=(255, 255, 255), isCPU=False, character=None):
        self.col = col
        self.row = row
        self.color = color
        self.isCPU = isCPU #set to none if not user.
        self.character = character
        self.hand = []

    def move(self, dx, dy, forbidden_zones):
        #Players Grid Position.
        # Add boundary checks here later
        new_col = self.col + dx
        new_row = self.row + dy

        # Forbidden tile Check:
        if (new_col, new_row) in forbidden_zones:
            print("Cannot move in there!")
            return

            # Boundary check (so they don't walk off the screen)
        if 0 <= new_col < 24 and 0 <= new_row < 25:
            self.col = new_col
            self.row = new_row


    def draw(self, surface):
        #Convert grid position to pixels and draws the player on the grid.
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

        # I've also commented out these lines for the sake of menu viewing.
        # Visual Debug: To see the grid lines.
        for r in range(25):
            for c in range(24):
                rect = (OFFSET_X + c * TILE_SIZE, OFFSET_Y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, (255, 0, 0), rect, 1)


class Game:
    #Initialisation for the game.
    def __init__(self):
        pygame.init()
        self.board = Board()
        win_width = self.board.width + self.board.sheet_width
        self.screen = pygame.display.set_mode((win_width, self.board.height))
        self.menu = Menu()
        # creates dice for dice class
        self.dice = Dice(self.board.width//2 - 60, self.board.height//1.25)
        self.dice_rect = self.dice.rect
        #Determines where the player starts and color.
        self.player = Player(11, 11, (255, 0, 0))  # Red player
        self.running = True
        #Gets mouse position
        self.mouse = pygame.mouse.get_pos()

        ###storing game state variables for gamecontroller
        self.activegame = False
        self.currentplayer = None
        self.otherplayers = []
        self.rooms = []
        self.weapons = []
        self.characters = []
        self.envelope = None
        self.moves_left = 0

        self.forbidden_tiles = [
            #These are all the forbidden zones.
            #Grid is 24x25 ColumnsxRows. starts at 0x0.

            #Study room
            (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0),
            (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
            (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
            (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
            (6, 0), (6, 1), (6, 2), (6, 3),

            #Specific tiles:
            (0,4), (0,11), (0,17), (6,24), (7,24), (6,23),(16, 24), (17,24 ), (17,23), (23,6),(23,8),
            (6,7),(6,8),(6,9), (10, 24),(11,24),(12,24),(13,24),(10, 23),(11,23),(12,23),(13,23),

            #STAIRS:
            (9,8),(9,9),(9,10),(9,11),(10,8),(10,9),(10,10),(10,11),
            (13, 8), (13, 9), (13, 10), (13, 11),(12,8),(12,9),(12,10),(12,11),

            # LOUNGE
            (17, 0), (18, 0), (19, 0), (20, 0), (21, 0), (22, 0), (23, 0),
            (17, 1), (18, 1), (19, 1), (20, 1), (21, 1), (22, 1), (23, 1),
            (17, 2), (18, 2), (19, 2), (20, 2), (21, 2), (22, 2), (23, 2),
            (17, 3), (18, 3), (19, 3), (20, 3), (21, 3), (22, 3), (23, 3),
            (17, 4), (18, 4), (19, 4), (20, 4), (21, 4), (22, 4), (23, 4),
            (17, 5),(18, 5),(19, 5),(20, 5),(21, 5),(22, 5), (23, 5),
            (15,0),  (8,0),

            #Specific Dining Room Coordinates
            (19, 15), (20,15 ), (21,15 ), (22,15 ), (23,15 ), (24,15 ),(24,16), (23,16),
        ]

        #MIDDLE =
        for r in range(12,15):
            for c in range(9,14):
                self.forbidden_tiles.append((c,r))

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

        #BALLROOM =
        for r in range(17, 23):
            for c in range(8, 16):
                self.forbidden_tiles.append((c, r))

        #KITCHEN =
        for r in range(18, 25):
            for c in range(18, 24):
                self.forbidden_tiles.append((c, r))

        #DINING ROOM =
        for r in range(9, 15):
            for c in range(16, 24):
                self.forbidden_tiles.append((c, r))


        #Billiard Room =
        for r in range(12,17):
            for c in range(0,6):
                self.forbidden_tiles.append((c, r))


    def handle_events(self):
        #checks for actions by the user.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:    self.player.move(0, -1, self.forbidden_tiles)
                if event.key == pygame.K_DOWN:  self.player.move(0, 1,self.forbidden_tiles)
                if event.key == pygame.K_LEFT:  self.player.move(-1, 0,self.forbidden_tiles)
                if event.key == pygame.K_RIGHT: self.player.move(1, 0,self.forbidden_tiles)

            if self.menu != None and event.type == pygame.MOUSEBUTTONDOWN:
                # Catch the action
                action = self.menu.buttonAction(self.mouse)
                print("menu action = ", action) #for debugging in console
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

                    #initializing game logic ABDULLAHMODIFIED
                    player, cpu_players, rooms, weapons, characters, envelope = setup_game(selected_name)
                    self.currentplayer = player
                    self.otherplayers = cpu_players
                    self.rooms = rooms
                    self.weapons = weapons
                    self.characters = characters
                    self.envelope = envelope
                    self.player.character = self.currentplayer.character                     #this links visual player to logic of the character
                    self.activegame = True
                    self.menu = None
                    print("the game is fully initialised.")
            
            if self.dice_rect.collidepoint(self.mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                print("Dice has been rolled with mouse.")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: print("Dice has been rolled with spacebar.")


    def run(self):
        while self.running:
            self.handle_events()
            # Renders the game.
            self.screen.fill((0, 0, 0))
            # Gets mouse position while game running
            self.mouse = pygame.mouse.get_pos()


            if self.menu is not None: #checking if we are on menu screen or board screen
                self.menu.draw(self.screen, self.mouse)
            else:
                self.board.draw(self.screen)
                self.player.draw(self.screen)
                self.dice.draw(self.screen, self.mouse)
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
        self.width = self.image.get_width()//4
        self.height = self.image.get_height()//4
        # scales image
        self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))
        self.image_copy = self.image.copy() # a copy that has transparency
        self.image_copy.set_alpha(150)
        #create a rect that matches the size of the image
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface, mouse):
        # gets mouse position 
        self.mouse = mouse
        # uses mouse position to change transparency (on hover or no)
        if self.rect.collidepoint(mouse): # once rounds are introduced, add an extra check to make sure it is the player's turn
            # in fiddling about with pygame and tutorials, this collidepoint/rect thing seemed much cleaner a solution than nested ifs
            # with that said, I have no intention of refactoring the other button
            surface.blit(self.image, (self.x, self.y))
        else:
            surface.blit(self.image_copy, (self.x, self.y))

class Menu:
    def __init__(self):
        # Loads and scales the background image used for the menu to cover the whole screen; overflow ignored
        self.image = pygame.image.load('Assets/Tudor-Mansion.png')
        # Couldn't get the win_width to work, so I just found the screen size instead
        self.disp_surf = pygame.display.get_surface()
        # Unless I'm being daft, which I probably am
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
        # every object in pygame is associated with a rectangle (get_rect())
        # thus accordingly, get the rectangle of the logo, and change its centerx position to match that of the screen
        # make a 'fixed' value for y
        self.logo_rect = self.logo.get_rect()
        self.logo_rect.centerx = pygame.display.get_surface().get_rect().centerx
        self.logo_rect.y = self.height * 0.1
        # now create the start button - centred horizontally
        self.start_btn = MenuButton(COLOUR, self.width//2 - 70, self.height//2 - 30, 140, 60, "Start")
        self.exit_btn = MenuButton(COLOUR, self.width//2 - 70, self.height//2 + 60, 140, 60, "Exit")

    def buttonAction(self, mouse):
        start_action = self.start_btn.changeGameState(mouse)
        exit_action = self.exit_btn.changeGameState(mouse)
        if start_action is not None: #start button returns character selected
            return start_action

        return None

    def draw(self, surface, mouse):
        # Gets mouse pos (taken as parameter)
        self.mouse = mouse
        # Draws background from top-left
        surface.blit(self.image, (0, 0))
        # Draws logo above sheet, centred horizontally
        # use the self.logo_rect which contains information pertaining to where the logo should be drawn
        # Looks nice and pretty, how lovely
        surface.blit(self.logo, (self.logo_rect))
        # this logo should probably be replaced later down the line 
        # draw the button(s)
        self.start_btn.draw(self.disp_surf)
        self.start_btn.mouseHover(self.mouse) #realistically, there's a way to merge the mouseHover code into draw(), but I'm not bothered
        self.exit_btn.draw(self.disp_surf)
        self.exit_btn.mouseHover(self.mouse)

class MenuButton:
    def __init__(self, colour, pos_x, pos_y, width, height, text=''):
        # receives parameters and sets its self values to them
        self.color = colour
        self.width = width
        self.height = height
        self.text = text
        self.pos_x = pos_x
        self.pos_y = pos_y
    
    def draw(self, surface):
        # draw the button as a rectangle
        pygame.draw.rect(surface, self.color, (self.pos_x, self.pos_y, self.width, self.height), 0)

    
        if self.text != '': #checks text isn't empty
            font = pygame.font.SysFont("papyrus", 30)
            text = font.render(self.text, 1, "#FFFFFF")
            surface.blit(text, (self.pos_x + (self.width//2 - text.get_width()//2), self.pos_y + (self.height//2 - text.get_height()//2)))

    def mouseHover(self, position): #changes button colour when mouse is hovering over it
        if position[0] > self.pos_x and position[0] < self.pos_x + self.width:
            if position[1] > self.pos_y and position[1] < self.pos_y + self.height:
                # mouse positions is passed as a paramter into position. position[0] is the mouse's x-coordinate at time of call, position[1] is y-coordinate
                self.color = COLOUR_HOVER
                return True # you should be able to safely delete the returns
        self.color = COLOUR
        return False # I've only left them in because it may be useful at some later point, or for code refactoring, if such a stage is reached
    
    def changeGameState(self, position): # not a very flexible system, but for the limited scope of the game, it'll do
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




