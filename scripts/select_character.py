import pygame
from scripts.state import State
from scripts.utils import load_image, ImageButton


class SelectCharacter(State):
    def __init__(self, game):
        super().__init__(game)

        self.image = load_image('assets/sprites/menus/select_character.png')
        self.buttons = {
            '64x64': ImageButton(pygame.Surface((64, 64), pygame.SRCALPHA)),
            '18x18': ImageButton(pygame.Surface((18, 18), pygame.SRCALPHA)),
        }

        self.phase = False
        self.alpha = 0

    def update(self):
        # Go back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.game.state = 'select level'

        # Draw menu
        self.game.layers[0].blit(self.image, (0, 0))

        # Draw effect
        if self.phase:
            self.blackout_screen.set_alpha(self.alpha)
            self.alpha += 1
            self.game.layers[4].blit(self.blackout_screen, (0, 0))
            if self.alpha > 255:
                self.phase = False
                self.alpha = 0
                self.game.set_level()
                self.game.state = 'level'

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.clicked and not self.phase

        # Select Biker
        self.buttons['64x64'].draw(self.game.layers[0], (5 * 32, 4 * 32), False)
        if self.buttons['64x64'].click(self.game.mouse_rect, click):
            self.game.character = 1
            self.game.clicked = True
            self.phase = True

        # Select Punk
        self.buttons['64x64'].draw(self.game.layers[0], (8 * 32, 4 * 32), False)
        if self.buttons['64x64'].click(self.game.mouse_rect, click):
            self.game.character = 2
            self.game.clicked = True
            self.phase = True

        # Select Cyborg
        self.buttons['64x64'].draw(self.game.layers[0], (11 * 32, 4 * 32), False)
        if self.buttons['64x64'].click(self.game.mouse_rect, click):
            self.game.character = 3
            self.game.clicked = True
            self.phase = True

        # Quit to previous screen
        self.buttons['18x18'].draw(self.game.layers[0], (13 * 32 + 11, 2 * 32 + 8), False)
        if self.buttons['18x18'].click(self.game.mouse_rect, click):
            self.game.state = 'select level'
            self.game.clicked = True

    def fade(self):
        pass