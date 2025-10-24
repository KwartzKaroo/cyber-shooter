import pygame
from scripts.state import State
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
            '32x32': ImageButton(pygame.Surface((32, 32), pygame.SRCALPHA)),
        }

    def update(self):
        self.game.layers[0].blit(self.game.prev_frame, (0, 0))
        self.game.layers[0].blit(self.images['main'], (0, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.clicked

        self.buttons['128x32'].draw(self.game.layers[0], (7 * 32, 3 * 32), False)
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            self.game.state = 'level'

        self.buttons['128x32'].draw(self.game.layers[0], (7 * 32, 5 * 32), False)
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            print('controls')
            # self.game.state = 'controls'

        self.buttons['128x32'].draw(self.game.layers[0], (7 * 32, 7 * 32), False)
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            self.game.state = 'select level'

    def set_screen(self):
        print('check some')
        self.images['prev screen'] = self.game.layers[3].copy()