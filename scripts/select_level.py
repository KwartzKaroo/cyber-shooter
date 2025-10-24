import pygame
import os
from scripts.state import State
from scripts.utils import load_image, ImageButton


class SelectLevel(State):
    def __init__(self, game):
        super().__init__(game)

        self.buttons = {
            '32x32': ImageButton(pygame.Surface((32, 32), pygame.SRCALPHA)),
            '18x18': ImageButton(pygame.Surface((18, 18), pygame.SRCALPHA)),
        }

        self.images = {
            'main': load_image('assets/sprites/menus/select_level.png'),
            'locked': load_image('assets/sprites/gui/locked.png')
        }

        self.num_of_levels = len(os.listdir('levels'))

    def update(self):
        # Go Back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.game.state = 'start'
            self.game.key_down = True

        # Draw menu
        self.game.layers[0].blit(self.images['main'], (-16, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.clicked
        self.buttons['18x18'].draw(self.game.layers[0], (13 * 32 + 28, 32 + 7), False)
        if self.buttons['18x18'].click(self.game.mouse_rect, click):
            self.game.state = 'start'
            self.game.clicked = True

        # Draw locked levels
        x = 0
        y = 0
        for i in range(self.game.data['levels completed']):
            # Button
            self.buttons['32x32'].draw(self.game.layers[0], (x * 32 * 2 + 144, y * 32 * 2 + 96), False)
            if self.buttons['32x32'].click(self.game.mouse_rect, click):
                self.game.level = (x + 1) + y * 5
                self.game.state = 'select character'

            x += 1
            if x % 5 == 0:
                x = 0
                y += 1

        # Draw locked levels
        x = min(self.game.data['levels completed'], self.num_of_levels)
        y = 0
        for i in range(15 - min(self.game.data['levels completed'], self.num_of_levels)):
            self.game.layers[0].blit(self.images['locked'], (x * 32 * 2 + 144, y * 32 * 2 + 96))

            x += 1
            if x % 5 == 0:
                x = 0
                y += 1

