# Author: Uhone DK Teffo AKA KwartzKaroo
# Date created: 02 December 2025
# Date completed: 26 December 2025
# Game name: Cyber Shooter
#
# Okay, so this is a remake of the original Cyber Shooter game. I changed how you win the game and added a few
# more things. So it's more of an update. I also learnt a few new things about pygame, so implemented them here.
# Anyway, as always, I hope you enjoy playing this game :)
#
# You can modify any code here if you think you know what you're doing. But don't touch the art though.
#
# And check out my GitHub for other games and projects: https://github.com/KwartzKaroo/


# If this file does not run, perhaps try to pip install pygame

# Import and initialize pygame
import pygame

pygame.init()
pygame.mixer.set_num_channels(30)


# Other imports
import json
from scripts.globals import SCREEN_SIZE
pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED)  # Don't mind this line here
from scripts.utils import Timer, load_image
from time import time
from states.state_manager import StateManager
from scripts.audio import MUSIC


class Game:
    def __init__(self):
        # Screen
        self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.SCALED)
        pygame.display.set_caption('Cyber Shooter')
        pygame.display.set_icon(load_image('assets/sprites/weapons/guns/02_1.png'))

        # Game loop
        self.running = True
        self.delta = 0
        self.frame_freeze = 0
        self.hit_stop = Timer(1000)
        self.prev_time = 0

        # Input
        self.key_presses = self.held_key_presses = set()
        self.mouse_clicks = self.held_mouse_clicks = set()
        self.mouse_rect = pygame.Rect(0, 0, 10, 15)
        self.mouse_button_down = self.key_down = False

        # Fonts for text
        self.fonts = {
            15: pygame.font.Font('assets/fonts/cyberpunk.otf', 15),
            17: pygame.font.Font('assets/fonts/cyberpunk.otf', 17),
            7: pygame.font.Font('assets/fonts/cyberpunk.otf', 10),
            'data 15': pygame.font.Font('assets/fonts/data-latin.ttf', 15),
        }

        # Data
        self.data = json.loads(open('data/game data/data.json', 'r').read())

        # States
        self.state_manager = StateManager(self)

        # Default background music
        pygame.mixer.music.load(MUSIC['ambience'])
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)

    def run(self):
        while self.running:
            prev_time = time()
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_clicks.add(event.button)
                    self.held_mouse_clicks.add(event.button)

                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_button_down = False
                    if event.button in self.held_mouse_clicks:
                        self.held_mouse_clicks.remove(event.button)

                if event.type == pygame.KEYDOWN:
                    self.key_presses.add(event.key)
                    self.held_key_presses.add(event.key)

                if event.type == pygame.KEYUP:
                    self.key_down = False
                    if event.key in self.held_key_presses:
                        self.held_key_presses.remove(event.key)

                if event.type == pygame.MOUSEMOTION:
                    self.mouse_rect.topleft = event.pos

            # Default screen colour
            self.screen.fill('#03befc')

            # Update everything in between here
            self.state_manager.update()

            # Update screen
            pygame.display.update()

            # Reset inputs
            self.key_presses = set()
            self.mouse_clicks = set()

            # Delta time and frame rate
            current_time = time()
            self.delta = current_time - prev_time

    def quit(self):
        self.running = False
        open('data/game data/data.json', 'w').write(json.dumps(self.data))

if __name__ == '__main__':
    Game().run()
