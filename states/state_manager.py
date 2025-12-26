import pygame

from scripts.globals import FPS, SCREEN_SIZE
from scripts.audio import MUSIC
from scripts.background import Background
from scripts.utils import load_image, InvisibleButton
from states.level import Level


class StateManager:
    def __init__(self, game):
        self.game = game
        self.screen = pygame.display.get_surface()

        # For scenic background
        self.data = {'tileset': 'green zone', 'time': 'day'}
        self.scroll = [0, -4]
        self.background = Background('green zone', 'day')

        # Menu images
        self.images = {
            'main': load_image('assets/sprites/menus/main.png'),
            'pause': load_image('assets/sprites/menus/paused.png'),
            'select level': load_image('assets/sprites/menus/select_level.png'),
            'select character': load_image('assets/sprites/menus/select_character.png'),
            'controls': load_image('assets/sprites/menus/controls.png'),
            'tile1': load_image('assets/sprites/tilesets/green zone/tiles/Tile_02.png'),
            'tile2': load_image('assets/sprites/tilesets/green zone/tiles/Tile_24.png'),
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
        self.blackout_screen = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        self.blackout_screen.fill('black')
        self.phase = False
        self.alpha = 0

        # The level itself
        self.level_scene = None
        self.completed_levels = 1
        self.selected_level = 1
        self.state = 'start'
        self.prev_state = 'start'

    def draw_background(self):
        # Update scroll
        self.scroll[0] = (self.scroll[0] + self.game.delta * FPS) % (576 * 24)

        # Draw background
        self.background.draw(self.screen, self.scroll)

        # Draw some grass for lively animation
        for i in range(int(self.scroll[0] // 32), int((self.scroll[0] + 672) // 32) + 1):
            self.screen.blit(self.images['tile1'], (i * 32 - self.scroll[0], 320 - 96))
            self.screen.blit(self.images['tile2'], (i * 32 - self.scroll[0], 320 - 64))
            self.screen.blit(self.images['tile2'], (i * 32 - self.scroll[0], 320 - 32))

    def start_screen(self):
        # Quit
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.game.quit()

        # Draw the menu
        self.screen.blit(self.images['main'], (0, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.mouse_button_down
        self.buttons['128x32'].set_pos((7 * 32, 6 * 32))
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            self.game.mouse_button_down = True
            self.change_state('select level')

        self.buttons['32x32'].set_pos((5 * 32, 7 * 32))
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.game.mouse_button_down = True
            self.change_state('controls')

        self.buttons['32x32'].set_pos((12 * 32, 7 * 32))
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.game.quit()

    def controls(self):
        # Go Back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.change_state(self.prev_state)
            self.game.key_down = True

        # Draw the menu
        self.screen.blit(self.images['controls'], (0, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.mouse_button_down
        self.buttons['18x18'].set_pos((16 * 32, 32 + 14))
        if self.buttons['18x18'].click(self.game.mouse_rect, click):
            self.game.mouse_button_down = True
            self.change_state(self.prev_state)

    def select_level(self):
        # Go Back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.change_state('start')
            self.game.key_down = True

        # Draw menu
        self.screen.blit(self.images['select level'], (-16, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.mouse_button_down
        self.buttons['18x18'].set_pos((13 * 32 + 28, 32 + 7))
        if self.buttons['18x18'].click(self.game.mouse_rect, click):
            self.state = 'start'
            self.game.mouse_button_down = True

        # Buttons
        x = 0
        y = 0
        for i in range(min(self.game.data['levels completed'], 5)):
            # Button
            self.buttons['32x32'].set_pos((x * 32 * 2 + 160 - 16, y * 32 * 2 + 160))
            if self.buttons['32x32'].click(self.game.mouse_rect, click):
                self.selected_level = (x + 1) + y * 5
                self.state = 'select character'

            x += 1
            if x % 5 == 0:
                x = 0
                y += 1

        # Draw locked levels
        x = min(self.game.data['levels completed'], 5)
        y = x // 5
        for i in range(5 - min(self.game.data['levels completed'], 5)):
            self.screen.blit(self.images['locked'], ((x % 5) * 32 * 2 + 144, 160))

            x += 1
            if x % 5 == 0:
                x = 0
                y += 1

    def select_character(self):
        # Go back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            self.state = 'select level'
            self.game.key_down = True

        # Draw menu
        self.screen.blit(self.images['select character'], (0, 0))

        # Draw effect
        if self.phase:
            if self.alpha > 200:
                pygame.mixer.music.fadeout(1000)
            self.blackout_screen.set_alpha(self.alpha)
            self.alpha += 3 * self.game.delta * FPS
            self.screen.blit(self.blackout_screen, (0, 0))
            if self.alpha > 255:
                # self.phase = False
                self.alpha = 0
                self.set_level()
                self.change_state('level')
            return

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.mouse_button_down and not self.phase

        # Select Biker
        self.buttons['64x64'].set_pos((5 * 32, 4 * 32))
        if self.buttons['64x64'].click(self.game.mouse_rect, click):
            self.game.character = 1
            self.game.mouse_button_down = True
            self.phase = True

        # Select Punk
        self.buttons['64x64'].set_pos((8 * 32, 4 * 32))
        if self.buttons['64x64'].click(self.game.mouse_rect, click):
            self.game.character = 2
            self.game.mouse_button_down = True
            self.phase = True

        # Select Cyborg
        self.buttons['64x64'].set_pos((11 * 32, 4 * 32))
        if self.buttons['64x64'].click(self.game.mouse_rect, click):
            self.game.character = 3
            self.game.mouse_button_down = True
            self.phase = True

        # Quit to previous screen
        self.buttons['18x18'].set_pos((13 * 32 + 11, 2 * 32 + 8))
        if self.buttons['18x18'].click(self.game.mouse_rect, click):
            self.state = 'select level'
            self.game.mouse_button_down = True

    def pause(self):
        # Go Back
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down:
            pygame.mixer.music.unpause()
            self.change_state('level')
            self.game.key_down = True

        self.screen.blit(self.images['pause'], (0, 0))

        # Buttons
        click = 1 in self.game.mouse_clicks and not self.game.mouse_button_down
        self.buttons['128x32'].set_pos((7 * 32, 3 * 32))
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            pygame.mixer.music.unpause()
            self.change_state('level')
            self.game.mouse_button_down = True

        self.buttons['128x32'].set_pos((7 * 32, 5 * 32))
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            self.change_state('controls')
            self.game.mouse_button_down = True

        self.buttons['128x32'].set_pos((7 * 32, 7 * 32))
        if self.buttons['128x32'].click(self.game.mouse_rect, click):
            pygame.mixer.music.load(MUSIC['ambience'])
            pygame.mixer.music.set_volume(.8)
            pygame.mixer.music.play(-1)
            self.change_state('select level')
            self.game.mouse_button_down = True

    def set_level(self):
        self.level_scene = Level(self.game, self)
        self.alpha = 310
        self.phase = True

    def change_state(self, new_state):
        self.prev_state = self.state
        self.state = new_state

    def update(self):
        self.draw_background()

        # Manage state here
        if self.state == 'start':
            self.start_screen()
        elif self.state == 'controls':
            self.controls()
        elif self.state == 'select level':
            self.select_level()
        elif self.state == 'select character':
            self.select_character()
        elif self.state == 'level':
            self.level_scene.update()
        elif self.state == 'pause':
            self.pause()

