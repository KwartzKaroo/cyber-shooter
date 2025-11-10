import pygame

from scripts.audio import MUSIC
from scripts.states.level import Level
from scripts.utils import load_image, InvisibleButton
from scripts.world.background import Background


class State:
    def __init__(self, game):
        self.game = game
        self.phase = False
        self.alpha = 1000

        self.blackout_screen = pygame.Surface((576, 320), pygame.SRCALPHA)
        self.blackout_screen.fill('black')
        self.blackout_screen.set_alpha(28)

    def update(self):
        pass

    def transition(self):
        pass


class StateManager:
    def __init__(self, game):
        self.game = game

        # For scenic background
        self.data = {'tileset': 'green zone', 'time': 'day'}
        self.scroll = [0, 64]
        self.background = Background(game, self)

        # Menu images
        self.images = {
            'main': load_image('assets/sprites/menus/main.png'),
            'pause': load_image('assets/sprites/menus/paused.png'),
            'select level': load_image('assets/sprites/menus/select_level.png'),
            'select character': load_image('assets/sprites/menus/select_character.png'),
            'controls': load_image('assets/sprites/menus/controls.png'),
            'tile1': load_image('assets/sprites/tilesets/green zone/tiles/blocks/Tile_02.png'),
            'tile2': load_image('assets/sprites/tilesets/green zone/tiles/blocks/Tile_24.png'),
            'locked': load_image('assets/sprites/gui/locked.png')
        }

        # Buttons
        self.buttons = {
            '128x32': InvisibleButton((128, 32)),
            '64x64': InvisibleButton((64, 64)),
            '32x32': InvisibleButton((32, 32)),
            '18x18': InvisibleButton((18, 18)),
        }

        # For transitions
        self.blackout_screen = pygame.Surface((576, 320), pygame.SRCALPHA)
        self.blackout_screen.fill('black')
        self.phase = False
        self.alpha = 0

        # The level itself
        self.level = None

    def draw_background(self):
        # Update scroll
        self.scroll[0] = (self.scroll[0] + self.game.framerate) % (576 * 24)

        # Draw background
        self.background.draw()

        # Draw some grass for lively animation
        for i in range(int(self.scroll[0] // 32), int((self.scroll[0] + 672) // 32) + 1):
            self.game.layers[0].blit(self.images['tile1'], (i * 32 - self.scroll[0], 320 - 64))
            self.game.layers[0].blit(self.images['tile2'], (i * 32 - self.scroll[0], 320 - 32))

    def start_screen(self):
        # Quit
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.game.quit()

        # Draw the menu
        self.game.layers[0].blit(self.images['main'], (0, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.clicked
        self.buttons['128x32'].set_pos((7 * 32, 6 * 32))
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            self.game.change_state('select level')

        self.buttons['32x32'].set_pos((5 * 32, 7 * 32))
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            self.game.change_state('controls')

        self.buttons['32x32'].set_pos((12 * 32, 7 * 32))
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.game.quit()

    def controls(self):
        # Go Back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.game.change_state(self.game.prev_state)
            self.game.key_down = True

        # Draw the menu
        self.game.layers[0].blit(self.images['controls'], (0, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.clicked
        self.buttons['18x18'].set_pos((16 * 32, 32 + 14))
        if self.buttons['18x18'].click(self.game.mouse_rect, click):
            self.game.clicked = True
            self.game.change_state(self.game.prev_state)

    def select_level(self):
        # Go Back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.game.change_state('start')
            self.game.key_down = True

        # Draw menu
        self.game.layers[0].blit(self.images['select level'], (-16, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.clicked
        self.buttons['18x18'].set_pos((13 * 32 + 28, 32 + 7))
        if self.buttons['18x18'].click(self.game.mouse_rect, click):
            self.game.state = 'start'
            self.game.clicked = True

        # Draw locked levels
        x = 0
        y = 0
        for i in range(self.game.data['levels completed']):
            # Button
            self.buttons['32x32'].set_pos((x * 32 * 2 + 144, y * 32 * 2 + 96))
            if self.buttons['32x32'].click(self.game.mouse_rect, click):
                self.game.level = (x + 1) + y * 5
                self.game.state = 'select character'

            x += 1
            if x % 5 == 0:
                x = 0
                y += 1

        # Draw locked levels
        x = min(self.game.data['levels completed'], self.game.num_of_levels)
        y = 0
        for i in range(15 - min(self.game.data['levels completed'], self.game.num_of_levels)):
            self.game.layers[0].blit(self.images['locked'], (x * 32 * 2 + 144, y * 32 * 2 + 96))

            x += 1
            if x % 5 == 0:
                x = 0
                y += 1

    def select_character(self):
        # Go back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.game.state = 'select level'
            self.game.key_down = True

        # Draw menu
        self.game.layers[0].blit(self.images['select character'], (0, 0))

        # Draw effect
        if self.phase:
            if self.alpha > 200:
                pygame.mixer.music.fadeout(1000)
            self.blackout_screen.set_alpha(self.alpha)
            self.alpha += 2
            self.game.layers[4].blit(self.blackout_screen, (0, 0))
            if self.alpha > 255:
                self.phase = False
                self.alpha = 0
                self.level = Level(self.game)
                self.game.change_state('level')

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.clicked and not self.phase

        # Select Biker
        self.buttons['64x64'].set_pos((5 * 32, 4 * 32))
        if self.buttons['64x64'].click(self.game.mouse_rect, click):
            self.game.character = 1
            self.game.clicked = True
            self.phase = True

        # Select Punk
        self.buttons['64x64'].set_pos((8 * 32, 4 * 32))
        if self.buttons['64x64'].click(self.game.mouse_rect, click):
            self.game.character = 2
            self.game.clicked = True
            self.phase = True

        # Select Cyborg
        self.buttons['64x64'].set_pos((11 * 32, 4 * 32))
        if self.buttons['64x64'].click(self.game.mouse_rect, click):
            self.game.character = 3
            self.game.clicked = True
            self.phase = True

        # Quit to previous screen
        self.buttons['18x18'].set_pos((13 * 32 + 11, 2 * 32 + 8))
        if self.buttons['18x18'].click(self.game.mouse_rect, click):
            self.game.state = 'select level'
            self.game.clicked = True

    def pause(self):
        # Go Back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            pygame.mixer.music.unpause()
            self.game.change_state('level')
            self.game.key_down = True

        self.game.layers[0].blit(self.images['pause'], (0, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.clicked
        self.buttons['128x32'].set_pos((7 * 32, 3 * 32))
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            pygame.mixer.music.unpause()
            self.game.change_state('level')
            self.game.clicked = True

        self.buttons['128x32'].set_pos((7 * 32, 5 * 32))
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            self.game.change_state('controls')
            self.game.clicked = True

        self.buttons['128x32'].set_pos((7 * 32, 7 * 32))
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            pygame.mixer.music.load(MUSIC['ambience 2'])
            pygame.mixer.music.set_volume(.8)
            pygame.mixer.music.play(-1)
            self.game.change_state('select level')
            self.game.clicked = True

    def update(self):
        self.draw_background()

        # Manage state here
        if self.game.state == 'start':
            self.start_screen()
        elif self.game.state == 'controls':
            self.controls()
        elif self.game.state == 'select level':
            self.select_level()
        elif self.game.state == 'select character':
            self.select_character()
        elif self.game.state == 'level':
            self.level.update()
        elif self.game.state == 'pause':
            self.pause()


