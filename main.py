import json
import pygame
import time

from scripts.level import Level
from scripts.start import StartScreen
from scripts.select_character import SelectCharacter
from scripts.pause import PauseMenu
from scripts.select_level import SelectLevel


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((576, 320))
        pygame.display.set_caption('Cyber Shooter')
        self.layers = {i: pygame.Surface((576, 320), pygame.SRCALPHA) for i in range(5)}
        self.prev_frame = pygame.Surface((576, 320), pygame.SRCALPHA)

        # Game variables
        self.__running = True
        self.delta = 0
        self.key_presses = self.held_key_presses = set()
        self.mouse_clicks = self.held_mouse_clicks = set()
        self.key_down = self.clicked = False
        self.mouse_rect = pygame.Rect(0, 0, 4, 4)

        # Data
        self.data = json.loads(open('data/game data/data.json', 'r').read())

        # For level
        self.level = 1
        self.character = 1

        # States
        self.state = 'start'
        self.__states = {
            'start': StartScreen(self),
            'select character': SelectCharacter(self),
            'select level': SelectLevel(self),
            'pause': PauseMenu(self),
            'level': Level(self)
        }

        # Fonts
        self.fonts = {
            15: pygame.font.Font('assets/sprites/gui/font/cyberpunk.otf', 15),
            17: pygame.font.Font('assets/sprites/gui/font/cyberpunk.otf', 17),
        }

    def run(self):
        prev_time = time.time()
        while self.__running:
            # Event listener
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

                if event.type == pygame.KEYDOWN:
                    self.key_presses.add(event.key)
                    self.held_key_presses.add(event.key)

                if event.type == pygame.KEYUP:
                    self.key_down = False
                    if event.key in self.held_key_presses:
                        self.held_key_presses.remove(event.key)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_clicks.add(event.button)
                    self.held_mouse_clicks.add(event.button)

                if event.type == pygame.MOUSEBUTTONUP:
                    self.clicked = False
                    if event.button in self.held_mouse_clicks:
                        self.held_mouse_clicks.remove(event.button)

                if event.type == pygame.MOUSEMOTION:
                    self.mouse_rect.topleft = event.pos

            # Last frame
            self.prev_frame = self.screen.copy()

            # Default screen colour
            self.screen.fill('#43b0f0')


            # Renew surfaces
            self.layers = {i: pygame.Surface((576, 320), pygame.SRCALPHA) for i in range(6)}

            # States
            self.__states[self.state].update()

            # Draw every layer onto the screen
            for _, layer in self.layers.items():
                self.screen.blit(layer, (0, 0))

            # Update screen
            pygame.display.update()

            # Delta time
            self.delta = (time.time() - prev_time) * 66
            prev_time = time.time()

            # Clear inputs
            self.key_presses = set()
            self.mouse_clicks = set()

    def set_level(self):
        self.__states['level'] = Level(self)

    def quit(self):
        self.__running = False
        open('data/game data/data.json', 'w').write(json.dumps(self.data))


if __name__ == '__main__':
    Game().run()
    pygame.quit()

