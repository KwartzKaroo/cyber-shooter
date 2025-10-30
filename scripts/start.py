import pygame

from scripts.background import Background
from scripts.state import State
from scripts.utils import load_image, ImageButton


class StartScreen(State):
    def __init__(self, game):
        super().__init__(game)

        self.data = {'tileset': 'green zone', 'time': 'day'}
        self.scroll = [0, 64]

        self.background = Background(game, self)

        self.buttons = {
            '128x32': ImageButton(pygame.Surface((128, 32), pygame.SRCALPHA)),
            '32x32': ImageButton(pygame.Surface((32, 32), pygame.SRCALPHA)),
        }

        self.images = {
            'main': load_image('assets/sprites/menus/main.png'),
            'tile1': load_image('assets/sprites/tilesets/green zone/tiles/blocks/Tile_02.png'),
            'tile2': load_image('assets/sprites/tilesets/green zone/tiles/blocks/Tile_24.png')
        }

    def update(self):
        # Quit
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.game.quit()

        # Update scroll
        self.scroll[0] = (self.scroll[0] + 1 * self.game.delta) % (576 * 24)

        # Draw background
        self.background.draw()

        # Draw some grass for lively animation
        for i in range(int(self.scroll[0] // 32), int((self.scroll[0] + 672) // 32) + 1):
            self.game.layers[0].blit(self.images['tile1'], (i * 32 - self.scroll[0], 320 - 64))
            self.game.layers[0].blit(self.images['tile2'], (i * 32 - self.scroll[0], 320 - 32))

        # Draw the menu
        self.game.layers[0].blit(self.images['main'], (0, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.clicked
        self.buttons['128x32'].draw(self.game.layers[0], (7 * 32, 6 * 32), False)
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            self.game.state = 'select level'

        self.buttons['32x32'].draw(self.game.layers[0], (5 * 32, 7 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            self.game.change_state('controls')

        self.buttons['32x32'].draw(self.game.layers[0], (12 * 32, 7 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.game.quit()
