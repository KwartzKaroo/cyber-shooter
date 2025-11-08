import pygame

from scripts.menus.state import State
from scripts.utils import load_image, ImageButton


class PauseMenu(State):
    def __init__(self, game):
        super().__init__(game)

        self.images = {
            'main': load_image('assets/sprites/menus/paused.png'),
            'prev screen': pygame.Surface((576, 320))
        }
        self.images['prev screen'].fill('orange')

        self.buttons = {
            '128x32': ImageButton(pygame.Surface((128, 32), pygame.SRCALPHA)),
        }

    def update(self):
        # Go Back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            # pygame.mixer.music.unpause()
            self.game.change_state('level')
            self.game.key_down = True

        self.game.layers[0].blit(self.game.prev_frame, (0, 0))
        self.game.layers[0].blit(self.images['main'], (0, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.clicked
        self.buttons['128x32'].draw(self.game.layers[0], (7 * 32, 3 * 32), False)
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            self.game.change_state('level')

        self.buttons['128x32'].draw(self.game.layers[0], (7 * 32, 5 * 32), False)
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            self.game.change_state('controls')

        self.buttons['128x32'].draw(self.game.layers[0], (7 * 32, 7 * 32), False)
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            self.game.change_state('select level')


class Controls(State):
    def __init__(self, game):
        super().__init__(game)

        self.images = {
            'main': load_image('assets/sprites/menus/controls.png'),
            'prev screen': pygame.Surface((576, 320))
        }
        self.images['prev screen'].fill('orange')

        self.buttons = {
            '18x18': ImageButton(pygame.Surface((18, 18), pygame.SRCALPHA)),
        }

    def update(self):
        # Go Back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.game.change_state(self.game.prev_state)
            self.game.key_down = True

        # Draw the menu
        self.game.layers[0].blit(self.game.prev_frame, (0, 0))
        self.game.layers[0].blit(self.images['main'], (0, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.clicked
        self.buttons['18x18'].draw(self.game.layers[4], (16 * 32, 32 + 14), False)
        if self.buttons['18x18'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            self.game.change_state(self.game.prev_state)
