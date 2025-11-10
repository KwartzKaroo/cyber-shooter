import math

import pygame

from scripts.utils import load_all_images


class TileMap:
    def __init__(self, game, level):
        # Access to game and level
        self.game = game
        self.level = level

        self.tiles = None
        self.offgrid = None
        self.objects = None
        self.ramps = None
        self.boundaries = None

        self.tileset = ''
        self.images = {}

        # Load the data
        self.load()

    def draw(self):
        self.offgrid.draw(self.game.layers[0], self.level.scroll)
        self.objects.draw(self.game.layers[1], self.level.scroll, 4)
        self.ramps.draw(self.game.layers[4], self.level.scroll)
        self.tiles.draw(self.game.layers[4], self.level.scroll)

    def get_collision_tiles(self, rect):
        return self.tiles.tiles_around(rect)

    def get_collision_ramps(self, rect):
        return self.ramps.tiles_around(rect)

    def get_boundaries(self, rect):
        return self.boundaries.tiles_around(rect)

    def load(self):
        self.tileset = self.level.data['tileset']
        self.images = {
            'tiles': load_all_images(f'assets/sprites/tilesets/{self.tileset}/tiles/blocks'),
            'ramps': load_all_images(f'assets/sprites/tilesets/{self.tileset}/tiles/ramps'),
            'objects': load_all_images(f'assets/sprites/tilesets/{self.tileset}/objects'),
            'checkpoints': load_all_images(f'assets/sprites/checkpoints'),
        }

        self.tiles = Layer(self.images['tiles'], self.level.data['tiles'])
        self.offgrid = Layer(self.images['tiles'], self.level.data['offgrid'])
        self.ramps = Layer(self.images['ramps'], self.level.data['ramps'])
        self.objects = Layer(self.images['objects'], self.level.data['objects'])
        self.boundaries = Layer(self.images['ramps'], self.level.data['boundaries'])


class Layer:
    def __init__(self, images, data):
        self.data = data
        self.images = images

    def draw(self, surface, scroll, expansion=0):
        for x in range(int(scroll[0] // 32) - expansion, int((scroll[0] + 576) // 32) + 1 + expansion):
            for y in range(int(scroll[1] // 32) - expansion, int((scroll[1] + 320) // 32) + 1 + expansion):
                loc = f'{x},{y}'
                if loc in self.data:
                    tile = self.data[loc]
                    image = self.images[tile['index']]
                    pos = tile['pos'][0] * 32 - scroll[0], tile['pos'][1] * 32 + (32 - image.get_height()) - scroll[1]
                    surface.blit(image, pos)

    def tiles_around(self, rect):
        tiles = []
        grid_pos = rect.x // 32, rect.y // 32
        for h in range(-1, math.ceil(rect.h / 32) + 1):
            for w in range(-1, math.ceil(rect.w / 32) + 1):
                loc = f'{grid_pos[0] + w},{grid_pos[1] + h}'
                if loc in self.data:
                    tiles.append(
                        Tile(self.images[self.data[loc]['index']], self.data[loc]['pos'], self.data[loc]['index'])
                    )
        return tiles


class AnimatedLayer:
    def __init__(self, objects):
        self.objects: dict = objects

    def draw(self, delta, surface, scroll, expansion=0):
        # for _, obj in self.objects.items():
        for x in range(int(scroll[0] // 32) - expansion, int((scroll[0] + 576) // 32) + 1 + expansion):
            for y in range(int(scroll[1] // 32) - expansion, int((scroll[1] + 320) // 32) + 1 + expansion):
                loc = f'{x},{y}'
                if loc in self.objects:
                    obj = self.objects[loc]['animation']
                    obj.update(delta)
                    image = obj.get_image()
                    pos = x * 32 - scroll[0], y * 32 + (32 - image.get_height()) - scroll[1]
                    surface.blit(image, pos)

    def remove(self, pos):
        self.objects.pop(pos)

    def tiles_around(self, rect):
        tiles = []
        grid_pos = rect.x // 32, rect.y // 32
        for h in range(-1, math.ceil(rect.h / 32) + 1):
            for w in range(-1, math.ceil(rect.w / 32) + 1):
                loc = f'{grid_pos[0] + w},{grid_pos[1] + h}'
                if loc in self.objects:
                    tiles.append(
                        Tile(None, self.objects[loc]['pos'], self.objects[loc]['index'])
                    )
        return tiles


class Tile:
    def __init__(self, image, pos, index):
        self.image = image
        self.rect = pygame.Rect(pos[0] * 32, pos[1] * 32, 32, 32)
        self.index = index
