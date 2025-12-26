import pygame
from math import ceil

from scripts.globals import SCREEN_SIZE
from scripts.utils import load_images_folder


LAYER_IMAGE_MAPPINGS = {
    'offgrid': 'tiles',
    'tiles': 'tiles',
    'ramps': 'ramps',
    'ladders': 'objects',
    'objects': 'objects',
    'animated objects': 'animated objects',
    'boss': 'bosses',
    'enemies': 'enemies',
    'guns': 'guns',
    'pickups': 'pickups',
    'checkpoints': 'checkpoints',
    'boundaries': 'tiles'
}


class TileMap:
    def __init__(self, level, data=None):
        self.level = level
        self.data = {}
        self.images = {}

        if data is not None:
            self.load(data)

    def draw(self):
        for y in range(int(self.level.camera[1] // 32) - 5, int((self.level.camera[1] + SCREEN_SIZE[1]) // 32) + 6):
            for x in range(int(self.level.camera[0] // 32) - 5, int((self.level.camera[0] + SCREEN_SIZE[0]) // 32) + 6):
                loc = f'{x},{y}'
                if loc in self.data['offgrid']:
                    tile = self.data['offgrid'][loc]
                    image = self.images['tiles'][tile['index']]
                    pos = tile['pos'][0] - self.level.camera[0], tile['pos'][1] - self.level.camera[1]
                    self.level.canvases[1].blit(image, pos)

                if loc in self.data['objects']:
                    tile = self.data['objects'][loc]
                    image = self.images['objects'][tile['index']]
                    pos = (tile['pos'][0] - self.level.camera[0],
                           tile['pos'][1] + (32 - image.get_height()) - self.level.camera[1])
                    self.level.canvases[3].blit(image, pos)

                if loc in self.data['tiles']:
                    tile = self.data['tiles'][loc]
                    image = self.images['tiles'][tile['index']]
                    pos = tile['pos'][0] - self.level.camera[0], tile['pos'][1] - self.level.camera[1]
                    self.level.canvases[4].blit(image, pos)

                if loc in self.data['ramps']:
                    tile = self.data['ramps'][loc]
                    image = self.images['ramps'][tile['index']]
                    pos = tile['pos'][0] - self.level.camera[0], tile['pos'][1] - self.level.camera[1]
                    self.level.canvases[4].blit(image, pos)

                if loc in self.data['ladders']:
                    tile = self.data['ladders'][loc]
                    image = self.images['objects'][tile['index']]
                    pos = (tile['pos'][0] + (32 - image.get_width()) / 2 - self.level.camera[0],
                           tile['pos'][1] + (32 - image.get_height()) - self.level.camera[1])
                    self.level.canvases[4].blit(image, pos)

                if loc in self.data['checkpoints']:
                    tile = self.data['checkpoints'][loc]
                    image = self.images['checkpoints'][tile['index']]
                    pos = (tile['pos'][0] + (32 - image.get_width()) / 2 - self.level.camera[0],
                           tile['pos'][1] + (32 - image.get_height()) - self.level.camera[1])
                    self.level.canvases[3].blit(image, pos)

    def get_tiles_around(self, layer, rect):
        tiles = []
        grid_pos = rect.x // 32, rect.y // 32
        for h in range(-1, ceil(rect.h / 32) + 1):
            for w in range(-1, ceil(rect.w / 32) + 1):
                loc = f'{grid_pos[0] + w},{grid_pos[1] + h}'
                if loc in self.data[layer]:
                    index = self.data[layer][loc]['index']
                    image = self.images[LAYER_IMAGE_MAPPINGS[layer]][index]
                    pos = self.data[layer][loc]['pos']
                    tiles.append(Tile(image, pos, index))
        return tiles

    def load(self, data):
        tileset = data['tileset']

        self.data['offgrid'] = data['data']['offgrid']
        self.data['tiles'] = data['data']['tiles']
        self.data['ramps'] = data['data']['ramps']
        self.data['ladders'] = data['data']['ladders']
        self.data['objects'] = data['data']['objects']
        self.data['animated objects'] = data['data']['animated objects']
        self.data['checkpoints'] = data['data']['checkpoints']
        self.data['boundaries'] = data['data']['boundaries']

        self.images = {
            'tiles': load_images_folder(f'assets/sprites/tilesets/{tileset}/tiles'),
            'ramps': load_images_folder(f'assets/sprites/tilesets/{tileset}/ramps'),
            'objects': load_images_folder(f'assets/sprites/tilesets/{tileset}/objects'),
            'checkpoints': load_images_folder(f'assets/sprites/checkpoints'),
        }


class Tile:
    def __init__(self, image, pos, index):
        self.image = image
        self.rect = pygame.Rect(pos[0], pos[1], 32, 32)
        self.index = index