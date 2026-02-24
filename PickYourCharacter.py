import os
import pygame
from GridMovement import Board


class MainMenu2:
    def __init__(self):
        #Initialization, Screen set up, variables.
        pygame.init()

        self.board = Board()
        win_width = self.board.width + self.board.sheet_width
        win_height = self.board.height

        self.screen = pygame.display.set_mode((win_width, win_height))
        pygame.display.set_caption("Clue!")

        self.title_img = None
        self.title_position = (150, 85)
        self.loaded_characters = []
        self.positions = [
            (250, 250), (450, 250), (650, 250),
            (250, 450), (450, 450), (650, 450)
        ]

        # Calls load function
        self.load_assets()

    def load_assets(self):
        # Directory Python File
        script_dir = os.path.dirname(__file__)

        #Loads Title
        title_path = os.path.join(script_dir, "Assets", "PickYourCharacter.png")
        self.title_img = pygame.image.load(title_path).convert_alpha()

        # Load Characters
        character_names = [
            "Col Mustard.png",
            "MissScarlett.svg",
            "MrsWhite.svg",
            "Mrs. Peacock.png",
            "ProfessorPlum.svg",
            "Rev Green.png"
        ]

        for name in character_names:
            # Path for loading
            img_path = os.path.join(script_dir, "Cards", name)

            #Draws the characters on the screen.
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, (120, 120))
            self.loaded_characters.append(img)

    def draw(self):
          #Fills the screen with color and the title screen.
        self.screen.fill((35, 45, 60))
        self.screen.blit(self.title_img, self.title_position)
         #Loads the characters onto the screen at the coordinated positins
        for i in range(len(self.loaded_characters)):
            self.screen.blit(self.loaded_characters[i], self.positions[i])
        pygame.display.flip()

    def run(self):
        #Game Loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.draw()
        pygame.quit()

#It prevents your game menu from accidentally launching if you try to import it into another file.
if __name__ == "__main__":
    menu = MainMenu2()
    menu.run()

