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
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption("Clue!")
        self.title_img = None
        self.title_position = (150, 85)
        self.loaded_characters = []
        self.positions = [
            (250, 250), (450, 250), (650, 250),
            (250, 450), (450, 450), (650, 450)
        ]

        self.character_rects = []
        # Calls load function
        self.load_assets()

    def load_assets(self):
        # Directory Python File
        script_dir = os.path.dirname(__file__)

        #Loads Title
        title_path = os.path.join(script_dir, "Assets", "PickYourCharacter.png")
        self.title_img = pygame.image.load(title_path).convert_alpha()

        # Load Characters
        self.character_names = [
            "Col Mustard.png",
            "MissScarlett.png",
            "MrsWhite.png",
            "Mrs. Peacock.png",
            "ProfessorPlum.png",
            "Rev Green.png"
        ]

        #Finds cards folder, loads and resizes it, then stores it as self.loaded_characters
        for i, name in enumerate(self.character_names):
            img_path = os.path.join(script_dir, "Cards", name)
            img = pygame.image.load(img_path).convert_alpha()
            max_size = 140
            w, h = img.get_size()
            scale = min(max_size / w, max_size / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = pygame.transform.smoothscale(img, (new_w, new_h))
            self.loaded_characters.append(img)

            #hitbox for mouseHover
            x, y = self.positions[i]
            rect = img.get_rect(center=(x + 60, y + 60))
            self.character_rects.append(rect)


    def draw(self):
          #Fills the screen with color and the title screen.
        self.screen.fill((35, 45, 60))
        self.screen.blit(self.title_img, self.title_position)
        hovered_rect = self.mouseHover()

         #Loads the characters onto the screen at the coordinated positions
        for i in range(len(self.loaded_characters)):
            self.screen.blit(self.loaded_characters[i], self.character_rects[i])

            if hovered_rect == self.character_rects[i]:
             pygame.draw.rect(self.screen, (0,0,0), self.character_rects[i], 3)


        pygame.display.flip()


    def run(self):
        #Game Loop
        self.selected_character = None
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                 clicked_rect = self.mouseHover()
                 if clicked_rect is not None:
                    # Get the index of the clicked rect, self.selected_character is the selected character chosen on main screen.
                    index = self.character_rects.index(clicked_rect)
                     
                    self.selected_character = self.character_names[index]
                     
                    print("Character Selected!... Moving to board!")
                     
                    running = False
                     
            self.draw()
        return self.selected_character #other code can use selected character

    #Checks to see if mouse is hovering over character cards.
    def mouseHover(self):
        mouse_pos = pygame.mouse.get_pos()

        for rect in self.character_rects:
            if rect.collidepoint(mouse_pos):
                return rect
        return None



#It prevents your game menu from accidentally launching if you try to import it into another file.
if __name__ == "__main__":
    menu = MainMenu2()
    menu.run()

