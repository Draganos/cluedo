import pygame
from pygame.locals import *

# constants
x = 1152 # width of the game screen
y = 720 # height of the game screen

# creating the main application class
class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = x, y

    # following performed on initialisation
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Clue!")

        #setting up the board image (may replace later)
        board = pygame.image.load("Assets/cluedoboard.jpg")
        board = pygame.transform.scale(board, (y, y))

        #setting up sheet (replace sheet image later - this is only a placeholder)
        sheet = pygame.image.load("Assets/cluedo-sheet.png")
        sheet = pygame.transform.scale(sheet, (x-y, y))

        #display on screen
        self._display_surf.blit(board, (0, 0))
        self._display_surf.blit(sheet, (y, 0))
        pygame.display.flip()

        self._running = True

    # game loop functions
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
    def on_loop(self):
        pass
    def on_render(self):
        pass
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while(self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()