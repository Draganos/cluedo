import pygame

#
#Constants, OFFSET X, Y and TILE_SIZE determine the grid layout.
SCALE = 0.6
TILE_SIZE = 46.5 * SCALE
OFFSET_X = 37 * SCALE
OFFSET_Y = 18 * SCALE


class Player:
    def __init__(self, col, row, color, isCPU=False, character=None):
        self.col = col
        self.row = row
        self.color = color
        self.isCPU = isCPU #set to none if not user.
        self.character = character

    def move(self, dx, dy):
        #Players Grid Position.
        # Add boundary checks here later
        self.col += dx
        self.row += dy

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

        # Visual Debug: To see the grid lines.
        #for r in range(25):
            #for c in range(24):
                #rect = (OFFSET_X + c * TILE_SIZE, OFFSET_Y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                #pygame.draw.rect(surface, (255, 0, 0), rect, 1)


class Game:

    #Intialisation for the game.
    def __init__(self):
        pygame.init()
        self.board = Board()
        win_width = self.board.width + self.board.sheet_width
        self.screen = pygame.display.set_mode((win_width, self.board.height))
        #Determines where the player starts and color.
        self.player = Player(11, 11, (255, 0, 0))  # Red player
        self.running = True

    def handle_events(self):
        #checks for actions by the user.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:    self.player.move(0, -1)
                if event.key == pygame.K_DOWN:  self.player.move(0, 1)
                if event.key == pygame.K_LEFT:  self.player.move(-1, 0)
                if event.key == pygame.K_RIGHT: self.player.move(1, 0)

    def run(self):
        while self.running:
            self.handle_events()
            # Renders the game.
            self.screen.fill((0, 0, 0))
            self.board.draw(self.screen)
            self.player.draw(self.screen)
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    clue_game = Game()
    clue_game.run()

