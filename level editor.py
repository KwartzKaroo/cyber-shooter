import pygame
import os
import time
import math
import json
from scripts.utils import (CustomButton, load_all_images, load_pickup_icons, load_enemy_icons,
                           debug_rect, debug_info)

# Set the environment variable to center the window
os.environ['SDL_VIDEO_CENTERED'] = '1'

EDITOR_SIZE = 576 + 32 * 6, 320 + 32 * 6


class Editor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((576, 324))
        pygame.display.set_caption('Cyber Shooter Level Editor')

        # Editor variables
        self.running = True
        self.delta = 0
        self.key_presses = self.held_key_presses = set()
        self.mouse_clicks = self.held_mouse_clicks = set()
        self.key_down = self.clicked = False
        self.mouse_rect = pygame.Rect(0, 0, 4, 4)

        # States
        self.states = {
            'start screen': True,
            'select set': False,
            'main': False,
        }

        # Buttons
        self.buttons = {
            'gz': CustomButton((160, 48), 'Green Zone', bd_width=4),
            'fac': CustomButton((160, 48), 'Factory', bd_width=4),
            'ps': CustomButton((160, 48), 'Power Station', bd_width=4, font_size=25),
            'exc': CustomButton((160, 48), 'Exclusion', bd_width=4),
            'sea': CustomButton((160, 48), 'Sea Port', bd_width=4),
            'new': CustomButton((160, 48), 'Create new', bd_width=4),
            'load': CustomButton((160, 48), 'Load', bd_width=4),
            'time': CustomButton((160, 48), 'Change time', bd_width=4, font_size=20),
            'offgrid': CustomButton((160, 48), 'Offgrid', bd_width=4, font_size=20),
            'save': CustomButton((160, 48), 'Save', bd_width=4),
            'recenter': CustomButton((160, 48), 'Recenter', bd_width=4),
            'next': CustomButton((40, 40), '>', bd_width=4),
            'prev': CustomButton((40, 40), '<', bd_width=4),
        }

        # Save data
        self.scroll = [0, 0]
        self.init_pos = [0, 0]
        self.data = {}
        self.images = {}
        self.background = {}
        self.tileset = ''
        self.time = 'day'
        self.images_index = 0
        self.categories = []
        self.selection_rect = pygame.Rect(32, 32, 32, 32)
        self.place_in_offgrid = False
        self.tile_index = 0
        self.level = 0
        self.loaded = False

    def create_data(self):
        self.data['offgrid'] = {}
        self.data['objects'] = {}
        self.data['pickups'] = {}
        self.data['checkpoints'] = {}
        self.data['guns'] = {}
        self.data['bosses'] = {}
        self.data['enemies'] = {}
        self.data['ramps'] = {}
        self.data['tiles'] = {}
        self.data['boundaries'] = {}

    def load_images(self, tileset):
        self.tileset = tileset

        self.images = {
            'tiles': load_all_images(f'assets/sprites/tilesets/{self.tileset}/tiles/blocks'),
            'ramps': load_all_images(f'assets/sprites/tilesets/{self.tileset}/tiles/ramps'),
            'objects': load_all_images(f'assets/sprites/tilesets/{self.tileset}/objects'),
            'pickups': load_pickup_icons(f'assets/sprites/tilesets/{self.tileset}/pickups'),
            'guns': load_all_images(f'assets/sprites/guns/guns/1'),
            'checkpoints': load_all_images(f'assets/sprites/checkpoints'),
            'enemies': load_enemy_icons('assets/sprites/enemies', size=(48, 48)),
            'bosses': load_enemy_icons('assets/sprites/bosses', (48, 48)),
            'boundaries': [pygame.Surface((32, 32))],
        }
        self.categories = list(self.images)

        # Day
        surf = pygame.Surface((576, 324))
        for image in load_all_images(f'assets/sprites/tilesets/{self.tileset}/background/day'):
            surf.blit(image, (0, 0))
        self.background['day'] = surf

        # Night
        surf = pygame.Surface((576, 324))
        for image in load_all_images(f'assets/sprites/tilesets/{self.tileset}/background/night'):
            surf.blit(image, (0, 0))
        self.background['night'] = surf

    def start_screen(self):
        if pygame.K_ESCAPE in self.key_presses and not self.key_down:
            self.running = False

        self.buttons['new'].draw(self.screen, (572 * 1/2, 324 * 2/6))
        self.buttons['load'].draw(self.screen, (572 * 1/2, 324 * 4/6))

        click = 1 in self.mouse_clicks and not self.clicked
        if self.buttons['new'].click(self.mouse_rect, click):
            self.clicked = True
            self.states['start screen'] = False
            self.states['select set'] = True
        if self.buttons['load'].click(self.mouse_rect, click):
            if len(os.listdir('levels')) == 0:
                print('No levels to load. Create a new one')
                return
            self.load()
            self.clicked = True
            self.screen = pygame.display.set_mode((EDITOR_SIZE[0] + 10 * 32, EDITOR_SIZE[1] + 3 * 32))
            self.states['start screen'] = False
            self.states['main'] = True

    def select_set(self):
        # Go back to main menu
        if pygame.K_ESCAPE in self.key_presses and not self.key_down:
            self.states['select set'] = False
            self.states['start screen'] = True
            self.key_down = True

        # Draw buttons
        self.buttons['gz'].draw(self.screen, (572 * 1/5, 324 * 2/6))
        self.buttons['fac'].draw(self.screen, (572 * 1/2, 324 * 2/6))
        self.buttons['ps'].draw(self.screen, (572 * 4/5, 324 * 2/6))
        self.buttons['exc'].draw(self.screen, (572 * 2/6, 324 * 4/6))
        self.buttons['sea'].draw(self.screen, (572 * 4/6, 324 * 4/6))

        # Button clicks
        click = 1 in self.mouse_clicks and not self.clicked
        start = False
        if self.buttons['gz'].click(self.mouse_rect, click):
            self.load_images('green zone')
            start = True
        if self.buttons['fac'].click(self.mouse_rect, click):
            self.load_images('factory')
            start = True
        if self.buttons['ps'].click(self.mouse_rect, click):
            self.load_images('power station')
            start = True
        if self.buttons['exc'].click(self.mouse_rect, click):
            self.load_images('exclusion')
            start = True
        if self.buttons['sea'].click(self.mouse_rect, click):
            self.load_images('sea port')
            start = True

        if start:
            self.screen = pygame.display.set_mode((EDITOR_SIZE[0] + 10 * 32, EDITOR_SIZE[1] + 3 * 32))
            self.states['select set'] = False
            self.states['main'] = True

    def main(self):
        if pygame.K_ESCAPE in self.key_presses and not self.key_down:
            self.states['main'] = False
            self.states['start screen'] = True
            self.screen = pygame.display.set_mode((576, 324))
            self.key_down = True

        self.edit()
        self.grid()
        self.draw()
        self.side_bar()
        self.bottom_bar()
        self.hud()

    def draw(self):
        for cat in self.data:
            for x in range(int(self.scroll[0] // 32), int((self.scroll[0] + EDITOR_SIZE[0]) // 32) + 1):
                for y in range(int(self.scroll[1] // 32), int((self.scroll[1] + EDITOR_SIZE[1]) // 32) + 1):
                    loc = f'{x},{y}'
                    if loc in self.data[cat]:
                        tile = self.data[cat][loc]
                        image = self.images[tile['category']][tile['index']]
                        pos = tile['pos'][0] * 32, tile['pos'][1] * 32 + (32 - image.get_height())
                        self.screen.blit(image, (pos[0] - self.scroll[0], pos[1] - self.scroll[1]))

    def grid(self, colour='grey'):
        # Background
        self.screen.blit(self.background[self.time], (96, 96))

        for x in range(int(self.scroll[0] // 32), int((self.scroll[0] + EDITOR_SIZE[0]) // 32 + 1)):
            pygame.draw.line(self.screen, colour, (x * 32 - self.scroll[0], 0),
                             (x * 32 - self.scroll[0], EDITOR_SIZE[1]), 1)

        for y in range(int(self.scroll[1] // 32), int((self.scroll[1] + EDITOR_SIZE[1]) // 32 + 1)):
            pygame.draw.line(self.screen, colour, (0, y * 32 - self.scroll[1]),
                             (EDITOR_SIZE[0], y * 32 - self.scroll[1]), 1)

    def edit(self):
        # Scroll
        if 2 in self.mouse_clicks:
            self.init_pos[0] = self.mouse_rect.x + self.scroll[0]
            self.init_pos[1] = self.mouse_rect.y + self.scroll[1]

        if 2 in self.held_mouse_clicks:
            self.scroll[0] = (self.init_pos[0] - self.mouse_rect.x)
            self.scroll[1] = (self.init_pos[1] - self.mouse_rect.y)

        # Edit the tile map
        if pygame.K_o in self.key_presses and self.categories[self.images_index] == 'tiles':
            self.place_in_offgrid = not self.place_in_offgrid

        if self.mouse_rect.colliderect(0, 0, EDITOR_SIZE[0], EDITOR_SIZE[1]) and self.mouse_rect.x > 0 and self.mouse_rect.y > 0 and not self.clicked:
            category = self.categories[self.images_index]
            if self.place_in_offgrid:
                category = 'offgrid'
            x, y = (self.mouse_rect.x + self.scroll[0]) // 32, (self.mouse_rect.y + self.scroll[1]) // 32
            loc = f'{x},{y}'
            if 1 in self.held_mouse_clicks:
                self.data[category][loc] = {
                    'pos': (x, y),
                    'category': self.categories[self.images_index],
                    'index': self.tile_index,
                }

            if 3 in self.held_mouse_clicks:
                if loc in self.data[category]:
                    self.data[category].pop(loc)

    def side_bar(self):
        # Change categories
        if pygame.K_a in self.key_presses:
            self.images_index = (self.images_index - 1) % len(self.categories)
        if pygame.K_d in self.key_presses:
            self.images_index = (self.images_index + 1) % len(self.categories)

        category = self.categories[self.images_index]
        images = self.images[category]

        # Create the side panel surface
        surface = pygame.Surface((320, self.screen.get_height()))
        surface.fill('orange')
        debug_info(surface, category.capitalize(), (160, 32), True, 40)

        # Side panel rect
        rect = pygame.Rect(EDITOR_SIZE[0] + 32, 64, surface.get_width() - 64, math.ceil(len(images) / 8) * 32)

        # Draw the images
        x = 0
        y = 2
        for image in images:
            if image.get_width() > 32 or image.get_height() > 32:
                image = pygame.transform.scale(image, (32, 32))
            surface.blit(image, (x * 32 + 32, y * 32))
            x += 1
            if x % 8 == 0:
                x = 0
                y += 1

        # Rect
        if self.mouse_rect.colliderect(rect) and self.mouse_rect.x > EDITOR_SIZE[0] + 32 and self.mouse_rect.y > 64:
            tile = (self.mouse_rect.x - EDITOR_SIZE[0] - 32) // 32, (self.mouse_rect.y - 64) // 32
            if 1 in self.mouse_clicks:
                self.selection_rect.topleft = tile[0] * 32, tile[1] * 32
                self.tile_index = tile[0] + tile[1] * 8
                if self.tile_index > len(images) - 1:
                    self.selection_rect.topleft = tile[0] * 32, tile[1] * 32
                    self.tile_index = len(images) - 1

        # Selection
        debug_rect(surface, self.selection_rect, (-32, -64))

        # Draw everything on the screen
        self.screen.blit(surface, (self.screen.get_width() - surface.get_width(), 0))

        self.buttons['prev'].draw(self.screen, (40 + EDITOR_SIZE[0], 32))
        self.buttons['next'].draw(self.screen, (self.screen.get_width() - 40, 32))

        click = 1 in self.mouse_clicks and not self.clicked
        if self.buttons['prev'].click(self.mouse_rect, click):
            self.images_index = (self.images_index - 1) % len(self.categories)
            self.clicked = True

        if self.buttons['next'].click(self.mouse_rect, click):
            self.images_index = (self.images_index + 1) % len(self.categories)
            self.clicked = True

    def bottom_bar(self):
        # Create the side panel surface
        surface = pygame.Surface((EDITOR_SIZE[0], 96))
        surface.fill('orange')

        self.screen.blit(surface, (0, EDITOR_SIZE[1]))

        self.buttons['load'].draw(self.screen, (self.screen.get_width() * 1 / 6, EDITOR_SIZE[1] + 48))
        self.buttons['save'].draw(self.screen, (self.screen.get_width() * 2 / 6, EDITOR_SIZE[1] + 48))
        self.buttons['recenter'].draw(self.screen, (self.screen.get_width() * 3 / 6, EDITOR_SIZE[1] + 48))
        self.buttons['time'].draw(self.screen, (self.screen.get_width() * 4 / 6, EDITOR_SIZE[1] + 48))
        self.buttons['offgrid'].draw(self.screen, (self.screen.get_width() * 5 / 6, EDITOR_SIZE[1] + 48))

        click = 1 in self.mouse_clicks and not self.clicked
        if self.buttons['load'].click(self.mouse_rect, click):
            self.load()
            self.clicked = True

        if self.buttons['save'].click(self.mouse_rect, click):
            self.clicked = True
            self.save()

        if self.buttons['recenter'].click(self.mouse_rect, click):
            self.clicked = True
            self.scroll = [0, 0]

        if self.buttons['offgrid'].click(self.mouse_rect, click):
            self.clicked = True
            self.place_in_offgrid = not self.place_in_offgrid

        if self.buttons['time'].click(self.mouse_rect, click):
            if self.time == 'day':
                self.time = 'night'
            else:
                self.time = 'day'

    def hud(self):
        if self.place_in_offgrid:
            pygame.draw.rect(self.screen, 'yellow', (0, 0, EDITOR_SIZE[0], EDITOR_SIZE[1]), 5)

        # Camera bounds
        rect = (EDITOR_SIZE[0] - 576) / 2, (EDITOR_SIZE[1] - 320) / 2, 576, 320
        pygame.draw.rect(self.screen, 'white', rect, 2)

        # Scroll
        debug_info(self.screen, ((self.mouse_rect.x + self.scroll[0]) // 32,
                                 (self.mouse_rect.y + self.scroll[1]) // 32), (20, 20))

    def load(self):
        if len(os.listdir('levels')) == 0:
            print('No levels to load. Create a new one')
            return

        self.level += 1
        if self.level > len(os.listdir('levels')):
            self.level = 1

        with open(f'levels/level{self.level}.json', 'r') as file:
            self.data = json.loads(file.read())
            self.tileset = self.data['tileset']
            self.time = self.data['time']
            self.load_images(self.tileset)

            self.data.pop('tileset')
            self.data.pop('time')
            self.loaded = True
            print(f'Loaded level {self.level}')

    def save(self):
        save_data = self.data.copy()
        save_data['time'] = self.time
        save_data['tileset'] = self.tileset

        if not self.loaded:
            self.level = len(os.listdir('levels')) + 1

        with open(f'levels/level{self.level}.json', 'w') as file:
            file.write(json.dumps(save_data))
            print(f'Saved level {self.level}')
        self.loaded = True

    def run(self):
        prev_time = time.time()
        self.create_data()
        while self.running:
            # Reset
            self.key_presses = set()
            self.mouse_clicks = set()

            # Event listener
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

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
                    self.mouse_rect.topleft = event.pos


            # Default screen colour
            self.screen.fill('#43b0f0')

            # State manager
            if self.states['start screen']:
                self.start_screen()
            elif self.states['select set']:
                self.select_set()
            elif self.states['main']:
                self.main()

            # Delta time
            self.delta = (time.time() - prev_time) * 66

            # Update screen
            pygame.display.update()


if __name__ == '__main__':
    Editor().run()
    pygame.quit()
