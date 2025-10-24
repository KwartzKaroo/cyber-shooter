import pygame
from scripts.constants import GUN_NAMES
from scripts.gun import Gun
from scripts.tilemap import Layer
from scripts.utils import load_all_images


class InteractiveMap:
    def __init__(self, game, level):
        # Access game and level
        self.game = game
        self.level = level

        self.guns = []
        self.checkpoints = None
        self.pickups = None

        self.images = {}

        self.load()

    def draw(self):
        self.checkpoints.draw(self.game.layers[2], self.level.scroll)

        # Draw guns
        for gun in self.guns:
            gun.floating()

    def get_checkpoints(self, rect):
        return self.checkpoints.tiles_around(rect)

    def load(self):
        # Load images
        self.images = {
            'pickups': load_all_images(f'assets/sprites/tilesets/{self.level.tileset}/animated objects/pickups'),
            'checkpoints': load_all_images(f'assets/sprites/checkpoints'),
        }

        for _, value in self.level.data['guns'].items():
            pos = value['pos'][0] * 32, value['pos'][1] * 32
            self.guns.append(Gun(self.game, self.level, GUN_NAMES[value['index']], pos))

        self.checkpoints = Layer(self.images['checkpoints'], self.level.data['checkpoints'])


