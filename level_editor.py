# Author: Uhone DK Teffo AKA KwartzKaroo
# Date created: 02 December 2025
# Level editor for Cyber Shooter


# Import and initialize pygame
import pygame
from scripts.globals import GUN_NAMES

pygame.init()


# Other imports
import os
import json
from pygame.constants import *
from time import time
from scripts.utils import TextButton, load_images_folder, debug_info, load_image, cut_sprite_sheet

# Set the environment variable to center the window
os.environ['SDL_VIDEO_CENTERED'] = '1'


class LevelEditor:
    def __init__(self):
        # Import settings
        self.screen_size = (576, 320)
        self.window_size = (34 * 32, 640)
        self.panel_width = 8 * 32
        self.panel_colour = '#02232e'

        # Level Editor loop
        self.running = True
        self.delta = 0
        self.frame_rate = 66

        # Input
        self.key_presses = self.held_key_presses = set()
        self.mouse_clicks = self.held_mouse_clicks = set()
        self.mouse_rect = pygame.Rect(0, 0, 10, 15)
        self.mouse_button_down = self.key_down = False
        self.mouse_button_up = False

        # Buttons
        self.buttons = {
            'green-zone': TextButton((160, 48), 'Green Zone', bd_width=4),
            'factory': TextButton((160, 48), 'Factory', bd_width=4),
            'power-station': TextButton((160, 48), 'Power Station', bd_width=4, font_size=25),
            'exclusion': TextButton((160, 48), 'Exclusion', bd_width=4),
            'sea-port': TextButton((160, 48), 'Sea Port', bd_width=4),
            'new': TextButton((160, 48), 'Create new', bd_width=4),
            'load': TextButton((160, 48), 'Load', bd_width=4),
            'save': TextButton((160, 48), 'Save', bd_width=4),
            'recenter': TextButton((160, 48), 'Recenter', bd_width=4),
            'pencil': TextButton((160, 48), 'Pencil', bd_width=4, font_size=20),
            'rect': TextButton((160, 48), 'Rect', bd_width=4, font_size=20),
        }

        # Editing
        self.images = {}
        self.scroll = [0, 0]
        self.selected_grid = []
        self.tileset = ''
        self.data = {}
        self.texts = []
        self.typed_text = ''
        self.font = pygame.font.Font('assets/fonts/cyberpunk.otf', 28)
        self.typing = False
        self.init_pos = [0, 0]
        self.drawing_mode = 'pencil'
        self.drawing = False

        # Draw
        self.layer = pygame.Surface(self.screen_size)
        self.selected_tile_image = pygame.Surface((32, 32))
        self.player_image = pygame.Surface((21, 32))
        self.player_image.fill('orange')

        # Left panel
        self.layer_mappings = {
            'offgrid': 'tiles',
            'tiles': 'tiles',
            'ramps': 'ramps',
            'ladders': 'objects',
            'objects': 'objects',
            'animated objects': 'animated objects',
            'bosses': 'bosses',
            'enemies': 'enemies',
            'guns': 'guns',
            'pickups': 'pickups',
            'checkpoints': 'checkpoints',
            'boundaries': 'boundaries'
        }
        self.selected_layer_index = 0
        self.selected_layer = 'tiles'
        self.left_selection_rect = pygame.Rect(0, 0, 8 * 32, 32)

        # Right panel
        self.right_panel_width = 8 * 32

        # Bottom
        self.bottom_panel_height = 320
        self.bottom_selection_rect = pygame.Rect(32, 32, 32, 32)
        self.bottom_selection_surf = pygame.Surface((32, 32))
        self.bottom_selection_surf.fill('green')
        self.bottom_selection_surf.set_alpha(80)
        self.tile_index = 0

        # Saving
        self.tileset = ''
        self.level = 0

        # Screen
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption('Cyber Shooter Level Editor')

        # States
        self.states = {
            'start': True,
            'select tileset': False,
            'editor': False
        }

    # Screen methods
    def start_screen(self):
        if K_ESCAPE in self.key_presses and not self.key_down:
            self.running = False

        click = 1 in self.mouse_clicks and not self.mouse_button_down

        self.buttons['new'].draw(self.screen, (self.screen_size[0] * 1 / 2, self.screen_size[1] * 2 / 6))
        if self.buttons['new'].click(self.mouse_rect, click):
            self.change_state('start', 'select tileset')
            self.mouse_button_down = True

        self.buttons['load'].draw(self.screen, (self.screen_size[0] * 1 / 2, self.screen_size[1] * 4 / 6))
        if self.buttons['load'].click(self.mouse_rect, click):
            if len(os.listdir('levels')) == 0:
                print('No levels to load. Create a new one')
                return
            self.load_from_file()
            self.mouse_button_down = True
            self.change_state('start', 'editor')
            self.screen = pygame.display.set_mode(self.window_size)

    def select_tileset(self):
        # Go back to main menu
        if pygame.K_ESCAPE in self.key_presses and not self.key_down:
            self.change_state('select tileset', 'start')
            self.key_down = True

        # Button clicks
        click = 1 in self.mouse_clicks and not self.mouse_button_down
        start = False
        tileset = ''

        self.buttons['green-zone'].draw(self.screen, (self.screen_size[0] * 1 / 5, self.screen_size[1] * 2 / 6))
        if self.buttons['green-zone'].click(self.mouse_rect, click):
            start = True
            tileset = 'green zone'

        self.buttons['factory'].draw(self.screen, (self.screen_size[0] * 1 / 2, self.screen_size[1] * 2 / 6))
        if self.buttons['factory'].click(self.mouse_rect, click):
            tileset = 'factory'
            start = True

        self.buttons['power-station'].draw(self.screen, (self.screen_size[0] * 4 / 5, self.screen_size[1] * 2 / 6))
        if self.buttons['power-station'].click(self.mouse_rect, click):
            tileset = 'power station'
            start = True

        self.buttons['exclusion'].draw(self.screen, (self.screen_size[0] * 2 / 6, self.screen_size[1] * 4 / 6))
        if self.buttons['exclusion'].click(self.mouse_rect, click):
            tileset = 'exclusion'
            start = True

        self.buttons['sea-port'].draw(self.screen, (self.screen_size[0] * 4 / 6, self.screen_size[1] * 4 / 6))
        if self.buttons['sea-port'].click(self.mouse_rect, click):
            tileset = 'sea port'
            start = True

        if start:
            self.level = len(os.listdir('levels')) + 1
            self.new_data()
            self.load_images(tileset)
            self.change_state('select tileset', 'editor')
            self.change_screen_size(self.window_size)
            self.mouse_button_down = True

    def editor(self):
        if pygame.K_ESCAPE in self.key_presses and not self.key_down:
            self.change_state('editor', 'select tileset')
            self.screen = pygame.display.set_mode(self.screen_size)
            self.key_down = True

        if K_s in self.key_presses and K_LCTRL in self.held_key_presses:
            self.save_to_file()

        self.draw()
        self.place_on_grid()
        self.bottom_panel()
        self.left_panel()
        self.right_panel()

    # Methods for the editor method
    def draw(self):
        rect = (self.panel_width, 0, self.screen_size[0], self.screen_size[1])
        self.layer = pygame.Surface(self.screen_size, pygame.SRCALPHA)

        self.grid()

        for layer in self.data:
            for x in range(int(self.scroll[0] // 32), int((self.scroll[0] + self.screen_size[0]) // 32) + 1):
                for y in range(int(self.scroll[1] // 32), int((self.scroll[1] + self.screen_size[1]) // 32) + 1):
                    loc = f'{x},{y}'
                    if loc in self.data[layer]:
                        tile = self.data[layer][loc]
                        image = self.images[self.layer_mappings[layer]][tile['index']]
                        pos = tile['pos'][0], tile['pos'][1] + (32 - image.get_height())
                        self.layer.blit(image, (pos[0] - self.scroll[0], pos[1] - self.scroll[1]))

        if self.mouse_rect.colliderect(rect) and self.mouse_rect.x > rect[0] and self.mouse_rect.y > rect[1]:
            pos = ((self.mouse_rect.centerx + self.scroll[0]) // 32, (self.mouse_rect.y + self.scroll[1]) // 32)
            pos = pos[0] * 32, pos[1] * 32 + (32 - self.selected_tile_image.get_height())
            self.screen.blit(self.selected_tile_image, (pos[0] - self.scroll[0], pos[1] - self.scroll[1]))

        # HUD
        debug_info(self.layer, ((self.mouse_rect.x + self.scroll[0] - self.panel_width) // 32,
                                 (self.mouse_rect.y + self.scroll[1]) // 32), (20, 20))
        self.layer.blit(self.player_image, (self.screen_size[0] / 2 - 10, 6 * 32))

        # Draw the ground line
        pygame.draw.line(self.layer, 'red', (0, 320 - 94 - self.scroll[1]), (576, 320 - 94 - self.scroll[1]), 2)

        self.screen.blit(self.layer, (self.panel_width, 0))

        for item in self.texts:
            pos, text = item
            ttt = self.font.render(text, True, 'white')
            self.screen.blit(ttt, (pos[0] - self.scroll[0], pos[1] - self.scroll[1]))

            if 3 in self.mouse_clicks and self.mouse_rect.colliderect((pos[0] - self.scroll[0], pos[1] - self.scroll[1]), ttt.get_size()):
                self.texts.remove(item)


    def place_on_grid(self):
        # Scroll
        if 2 in self.mouse_clicks:
            self.init_pos[0] = self.mouse_rect.x + self.scroll[0]
            self.init_pos[1] = self.mouse_rect.y + self.scroll[1]

        if 2 in self.held_mouse_clicks:
            self.scroll[0] = (self.init_pos[0] - self.mouse_rect.x)
            self.scroll[1] = (self.init_pos[1] - self.mouse_rect.y)

        rect = (self.panel_width, 0, self.screen_size[0], self.screen_size[1])

        if self.tile_index == -1:
            return

        if self.mouse_rect.colliderect(rect) and self.mouse_rect.x > rect[0] and self.mouse_rect.y > rect[1]:
            x = (self.mouse_rect.x - self.panel_width + self.scroll[0]) // 32
            y = (self.mouse_rect.y + self.scroll[1]) // 32

            # Rectangle selection
            if self.drawing_mode == 'rect':
                if 1 in self.mouse_clicks:
                    self.init_pos = [x, y]
                    self.drawing = True

                if 3 in self.mouse_clicks:
                    self.init_pos = [x, y]
                    self.drawing = False

                if 1 in self.held_mouse_clicks or 3 in self.held_mouse_clicks:
                    rect = (self.init_pos[0] * 32 + self.panel_width - self.scroll[0], self.init_pos[1] * 32 - self.scroll[1],
                            (x - self.init_pos[0] + 1) * 32, (y - self.init_pos[1] + 1) * 32)
                    pygame.draw.rect(self.screen, 'orange', rect, 2)

                if self.mouse_button_up:
                    for b in range(self.init_pos[1], y + 1):
                        for a in range(self.init_pos[0], x + 1):
                            self.selected_grid.append((a, b))

            # Normal pencil drawing
            if self.drawing_mode == 'pencil':
                if 1 in self.held_mouse_clicks and not self.mouse_button_down:
                    self.drawing = True
                    self.selected_grid.append((x, y))

                if 3 in self.held_mouse_clicks:
                    self.drawing = False
                    self.selected_grid.append((x, y))

            # Add all the tiles to the grid
            if self.selected_grid:
                for a, b in self.selected_grid:
                    loc = f'{a},{b}'
                    if self.drawing:
                        self.data[self.selected_layer][loc] = {
                            'pos': (a * 32, b * 32),
                            'index': self.tile_index,
                        }
                    else:
                        if loc in self.data[self.selected_layer]:
                            self.data[self.selected_layer].pop(loc)

                self.selected_grid = []

    def left_panel(self):
        surface = pygame.Surface((self.panel_width, self.screen.get_height()))
        surface.fill(self.panel_colour)
        debug_info(surface, 'Layers', (128, 48), True, 32, 'white', self.panel_colour)

        click = 1 in self.mouse_clicks and not self.mouse_button_down

        if self.mouse_rect.colliderect(0, 80, 8 * 32, len(self.layer_mappings) * 32):
            if click:
                self.selected_layer_index = (self.mouse_rect.y - 80) // 32
                self.selected_layer = list(self.layer_mappings)[self.selected_layer_index]

        for y, layer in enumerate(self.layer_mappings.keys()):
            if layer == self.selected_layer:
                pygame.draw.rect(surface, '#037094', (0, y * 32 + 80, 256, 32))
                debug_info(surface, layer.capitalize(), (128, 32 * y + 96), True, 26, 'white', '#037094')
            else:
                debug_info(surface, layer.capitalize(), (128, 32 * y + 96), True, 26, 'white', self.panel_colour)

        self.screen.blit(surface, (0, 0))

    def right_panel(self):
        pygame.draw.rect(self.screen, self.panel_colour, (576 + 8 * 32, 0, self.panel_width, self.screen.get_height()))

        click = 1 in self.mouse_clicks and not self.mouse_button_down

        if self.drawing_mode == 'pencil':
            self.buttons['pencil'].draw(self.screen, (576 + self.panel_width + self.right_panel_width / 2, 48))
            if self.buttons['pencil'].click(self.mouse_rect, click):
                self.drawing_mode = 'rect'
        elif self.drawing_mode == 'rect':
            self.buttons['rect'].draw(self.screen, (576 + self.panel_width + self.right_panel_width / 2, 48))
            if self.buttons['rect'].click(self.mouse_rect, click):
                self.drawing_mode = 'pencil'

        self.buttons['load'].draw(self.screen, (576 + self.panel_width + self.right_panel_width / 2, 48 + 128))
        if self.buttons['load'].click(self.mouse_rect, click):
            if len(os.listdir('levels')) == 0:
                print('No levels to load. Create a new one')
            else:
                self.load_from_file()

        self.buttons['save'].draw(self.screen, (576 + self.panel_width + self.right_panel_width / 2, 96 + 16 + 128))
        if self.buttons['save'].click(self.mouse_rect, click):
            self.save_to_file()

        self.buttons['recenter'].draw(self.screen, (576 + self.panel_width + self.right_panel_width / 2, 96 + 48 + 32 + 128))
        if self.buttons['recenter'].click(self.mouse_rect, click):
            self.scroll = [0, 0]

    def bottom_panel(self):
        images = self.images[self.layer_mappings[self.selected_layer]]

        # Create the side panel surface
        surface = pygame.Surface(self.screen_size)

        surface.fill('orange')

        if not images:
            self.screen.blit(surface, (self.panel_width, self.screen_size[1]))
            self.tile_index = -1
            return

        # Side panel rect
        rect = (self.panel_width + 32, self.screen_size[1] + 32, self.screen_size[0] - 64, self.screen_size[1] - 64)

        # Draw the images
        x = 1
        y = 1
        for image in images:
            if image.get_width() > 32:
                scale = (32, 32 * image.get_height() / image.get_width())
                image = pygame.transform.scale(image, scale)
            if image.get_height() > 32:
                scale = (32 * image.get_width() / image.get_height(), 32)
                image = pygame.transform.scale(image, scale)
            surface.blit(image, (x * 32, y * 32))
            if x % 16 == 0:
                x = 0
                y += 1
            x += 1

        # Rect
        if self.mouse_rect.colliderect(rect) and self.mouse_rect.x > rect[0] and self.mouse_rect.y > rect[1]:
            tile = (self.mouse_rect.x - self.panel_width) // 32 - 1, (self.mouse_rect.y - self.screen_size[1]) // 32 - 1
            pygame.draw.rect(surface, 'dark green',
                             (tile[0] * 32 + 32, tile[1] * 32 + 32, 32, 32), 2)
            index = tile[0] + tile[1] * 16
            if 1 in self.mouse_clicks and not self.mouse_button_down and index < len(images):
                self.bottom_selection_rect.x = tile[0] * 32 + 32
                self.bottom_selection_rect.y = tile[1] * 32 + 32
                self.tile_index = index

                # Selected image
                if not self.typing:
                    self.selected_tile_image = pygame.Surface(images[self.tile_index].get_size())
                    self.selected_tile_image.fill('yellow')
                    self.selected_tile_image.blit(images[self.tile_index], (0, 0))
                    self.selected_tile_image.set_alpha(90)

        # Draw everything on the screen
        surface.blit(self.bottom_selection_surf, self.bottom_selection_rect)
        self.screen.blit(surface, (self.panel_width, self.screen_size[1]))

    def add_text(self):
        pass

    # Utility methods
    def grid(self, colour='grey'):
        for x in range(int(self.scroll[0] // 32), int((self.scroll[0] + self.screen_size[0]) // 32 + 1)):
            pygame.draw.line(self.layer, colour, (x * 32 - self.scroll[0], 0),
                             (x * 32 - self.scroll[0], self.screen_size[1]), 1)

        for y in range(int(self.scroll[1] // 32), int((self.scroll[1] + self.screen_size[1]) // 32 + 1)):
            pygame.draw.line(self.layer, colour, (0, y * 32 - self.scroll[1]),
                             (self.screen_size[0], y * 32 - self.scroll[1]), 1)

    def new_data(self):
        self.data['offgrid'] = {}
        self.data['tiles'] = {}
        self.data['ramps'] = {}
        self.data['ladders'] = {}
        self.data['objects'] = {}
        self.data['animated objects'] = {}
        self.data['enemies'] = {}
        self.data['bosses'] = {}
        self.data['guns'] = {}
        self.data['pickups'] = {}
        self.data['checkpoints'] = {}
        self.data['boundaries'] = {}

        self.texts = []
        self.typed_text = ''
        self.typing = False

    def load_images(self, tileset):
        self.tileset = tileset

        self.images = {
            'tiles': load_images_folder(f'assets/sprites/tilesets/{self.tileset}/tiles'),
            'ramps': load_images_folder(f'assets/sprites/tilesets/{self.tileset}/ramps'),
            'objects': load_images_folder(f'assets/sprites/tilesets/{self.tileset}/objects'),
            'animated objects': load_images_folder(f'assets/sprites/tilesets/{self.tileset}/animated objects'),
            'checkpoints': load_images_folder('assets/sprites/checkpoints'),
            'enemies': load_images_folder(''),
            'guns': load_images_folder(''),
            'bosses': load_images_folder(''),
            'pickups': load_images_folder(''),
            'boundaries': [pygame.Surface((32, 32))],
        }

        # Load enemy images
        for root, _, files in os.walk('assets/sprites/enemies'):
            for file in files:
                if 'idle' in file.lower():
                    image = load_image(root + '/' + file)
                    size = image.get_height(), image.get_height()
                    self.images['enemies'].append(cut_sprite_sheet(image, size)[0])

        # Load boss images
        for root, _, files in os.walk('assets/sprites/bosses'):
            for file in files:
                if 'idle' in file.lower():
                    image = load_image(root + '/' + file)
                    size = image.get_height(), image.get_height()
                    self.images['bosses'].append(cut_sprite_sheet(image, size)[0])

        # Load gun images
        for name in GUN_NAMES:
            self.images['guns'].append(load_image(f'assets/sprites/weapons/guns/{name}_1.png'))

    def load_from_file(self):
        self.level += 1
        if self.level > len(os.listdir('levels')):
            self.level = 1

        with open(f'levels/level{self.level}.json', 'r') as file:
            loaded_data = json.loads(file.read())
            self.load_images(loaded_data['tileset'])
            self.data = loaded_data['data']
            self.texts = loaded_data['text']
        print(f'Loaded level {self.level}')

    def save_to_file(self):
        save_data = {
            'tileset': self.tileset,
            'data': self.data,
            'text': self.texts
        }

        with open(f'levels/level{self.level}.json', 'w') as file:
            file.write(json.dumps(save_data))
            print(f'Saved level {self.level}')

    def change_screen_size(self, screen_size):
        self.screen = pygame.display.set_mode(screen_size)

    def change_state(self, current_state, new_state):
        if current_state not in self.states:
            raise KeyError(f'"{current_state}" is not a defined state')

        if new_state not in self.states:
            raise KeyError(f'"{new_state}" is not a defined state')

        self.states[new_state] = True
        self.states[current_state] = False

    # Main method
    def run(self):
        prev_time = time()
        while self.running:
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.typing:
                        pos = ((self.mouse_rect.centerx + self.scroll[0]) // 32,
                               (self.mouse_rect.y + self.scroll[1]) // 32)
                        pos = pos[0] * 32, pos[1] * 32 + (32 - self.selected_tile_image.get_height())
                        self.texts.append((pos, self.typed_text))
                    else:
                        self.mouse_clicks.add(event.button)
                        self.held_mouse_clicks.add(event.button)

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button in self.held_mouse_clicks:
                        self.held_mouse_clicks.remove(event.button)
                    self.mouse_button_down = False
                    self.mouse_button_up = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RSHIFT:
                        self.typing = not self.typing

                    if self.typing:
                        if event.key == pygame.K_BACKSPACE:
                            self.typed_text = self.typed_text[:-1]
                        else:
                            if 32 <= event.key <= 126:
                                self.typed_text += chr(event.key)

                        self.selected_tile_image = self.font.render(self.typed_text, True, 'white')
                        self.selected_tile_image.set_alpha(255)
                    else:
                        self.key_presses.add(event.key)
                        self.held_key_presses.add(event.key)

                if event.type == pygame.KEYUP:
                    if event.key in self.held_key_presses:
                        self.held_key_presses.remove(event.key)
                    self.key_down = False

                if event.type == pygame.MOUSEMOTION:
                    self.mouse_rect.topleft = event.pos

            # Default screen colour
            self.screen.fill('#4eadf5')

            # Update everything in between here
            # State manager
            if self.states['start']:
                self.start_screen()
            elif self.states['select tileset']:
                self.select_tileset()
            elif self.states['editor']:
                self.editor()

            # Update screen
            pygame.display.update()

            # Reset inputs
            self.key_presses = set()
            self.mouse_clicks = set()
            self.mouse_button_up = False

            # Delta time and frame rate
            current_time = time()
            self.delta = current_time - prev_time
            prev_time = current_time


if __name__ == '__main__':
    LevelEditor().run()
