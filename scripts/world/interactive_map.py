from scripts.constants import GUN_NAMES
from scripts.guns.gun import Gun
from scripts.utils import load_all_images, Animation
from scripts.world.tilemap import Layer, AnimatedLayer


class InteractiveMap:
    def __init__(self, game, level):
        # Access game and level
        self.game = game
        self.level = level

        self.guns = []
        self.pickups = None
        self.checkpoints = None

        self.images = {}

        self.load()

    def draw(self):
        # Checkpoints
        self.checkpoints.draw(self.game.layers[2], self.level.scroll)

        # Pickups
        self.pickups.draw(self.game.delta, self.game.layers[3], self.level.scroll)

        # Draw guns
        for gun in self.guns:
            gun.floating()

    def get_checkpoints(self, rect):
        return self.checkpoints.tiles_around(rect)

    def get_pickups(self, rect):
        return self.pickups.tiles_around(rect)

    def remove_pickup(self, pos):
        pos = f'{pos[0] // 32},{pos[1] // 32}'
        self.pickups.remove(pos)

    def load(self):
        # Load images
        self.images = {
            'pickups': load_all_images(f'assets/sprites/tilesets/{self.level.tileset}/pickups'),
            'checkpoints': load_all_images(f'assets/sprites/checkpoints'),
        }

        for _, value in self.level.data['guns'].items():
            pos = value['pos'][0] * 32, value['pos'][1] * 32
            self.guns.append(Gun(self.game, self.level, GUN_NAMES[value['index']], pos))

        self.checkpoints = Layer(self.images['checkpoints'], self.level.data['checkpoints'])

        self.pickups = {}
        for key, value in self.level.data['pickups'].items():
            self.pickups[key] = {
                'animation': Animation(self.images['pickups'][value['index']], 5, True, (24, 24)),
                'pos': value['pos'],
                'index': value['index']
            }

        self.pickups = AnimatedLayer(self.pickups)
