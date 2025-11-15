# This is the main file. Run the game entire game here.
# Some of the other files will give you an error if you run them directly.
# They are all useless on their own

# Author: Uhone DK Teffo A.K.A KwartzKaroo
# Game title: Cyber Shooter 2D
# My first complete game. Actually, it's my second complete game. I lost my first game called Agent Spas.
# Hopefully I'll find it someday. I'll upload it if I do.
# But anyway, I hope you have fun playing this game. It took me a very long time, about 6 months
# with continuous updates to make the game run better.
# Feel free to modify anything here if you know what you're doing.
# Check out my GitHub (KwartzKaroo) in the future because I plan on making more and better games, and a few other projects.


import pygame
import json
import time
from os import listdir

# Game imports
from scripts.constants import SCREEN_SIZE
from scripts.states.state import StateManager
from scripts.states.level import Level
from scripts.audio import MUSIC


# Initialize pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(30)


class Game:
    def __init__(self):

        # Set window and screen
        self.scale = 2
        self.screen = pygame.display.set_mode((576 * self.scale, 320 * self.scale))
        pygame.display.set_caption('Cyber Shooter')

        # Layers to be drawn on the screen
        self.prev_frame = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.layers = {i: pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA) for i in range(5)}
        self.__surface = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)

        # Game variables
        self.__running = True
        self.delta = 0
        self.framerate = 66
        self.key_presses = self.held_key_presses = set()
        self.mouse_clicks = self.held_mouse_clicks = set()
        self.key_down = self.clicked = False
        self.mouse_rect = pygame.Rect(0, 0, 4, 4)

        # Data
        self.data = json.loads(open('data/game data/data.json', 'r').read())

        # For level
        self.level = 3
        self.character = 1
        self.num_of_levels = len(listdir('levels'))

        # States
        self.state_manager = StateManager(self)
        self.state = 'level'
        self.prev_state = 'start'

        # Fonts
        self.fonts = {
            15: pygame.font.Font('assets/sprites/gui/font/cyberpunk.otf', 15),
            17: pygame.font.Font('assets/sprites/gui/font/cyberpunk.otf', 17),
        }

        # Default background music
        pygame.mixer.music.load(MUSIC['ambience 2'])
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)

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
                    self.mouse_rect.topleft = event.pos[0] / self.scale, event.pos[1] / self.scale

            # Last frame
            self.prev_frame = self.__surface.copy()

            # Default screen colour
            self.screen.fill('#43b0f0')

            # Renew surfaces
            self.__surface = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
            self.layers = {i: pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA) for i in range(6)}

            # States
            self.state_manager.update()

            # Draw every layer onto the screen
            for _, layer in self.layers.items():
                self.__surface.blit(layer, (0, 0))

            self.screen.blit(pygame.transform.scale(self.__surface, self.screen.get_size()), (0, 0))

            # Update screen
            pygame.display.update()

            # Clear inputs
            self.key_presses = set()
            self.mouse_clicks = set()

            # Delta time
            current_time = time.time()
            self.delta = current_time - prev_time
            self.framerate = self.delta * 62
            prev_time = current_time

    def set_level(self):
        self.state_manager.level = Level(self)

    def change_state(self, new_state):
        self.prev_state = self.state
        self.state = new_state

    def quit(self):
        self.__running = False
        open('data/game data/data.json', 'w').write(json.dumps(self.data))


if __name__ == '__main__':
    Game().run()
    pygame.quit()

