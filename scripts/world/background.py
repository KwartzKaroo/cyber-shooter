from scripts.utils import load_image


class Background:
    def __init__(self, game, level):
        # Access to game and level class
        self.game = game
        self.level = level

        # Initialize
        self.images = {}

        # Load data
        self.load()

    def draw(self):
        # First layer
        self.game.layers[0].blit(self.images[1], (0, 0))

        horizontal = self.level.scroll[0] / 6
        height = (-self.level.scroll[1])

        # Second layer
        self.game.layers[0].blit(self.images[2], (-((horizontal * 1) % 576), height))
        self.game.layers[0].blit(self.images[2], (-((horizontal * 1) % 576) + 576, height))

        # Third layer
        self.game.layers[0].blit(self.images[3], (-((horizontal * 2) % 576), height))
        self.game.layers[0].blit(self.images[3], (-((horizontal * 2) % 576) + 576, height))

        # Fourth layer
        self.game.layers[0].blit(self.images[4], (-((horizontal * 3) % 576), height))
        self.game.layers[0].blit(self.images[4], (-((horizontal * 3) % 576) + 576, height))

        # Fifth layer
        self.game.layers[0].blit(self.images[5], (-((horizontal * 4) % 576), height))
        self.game.layers[0].blit(self.images[5], (-((horizontal * 4) % 576) + 576, height))

    def load(self):
        tileset = self.level.data['tileset']
        time = self.level.data['time']

        self.images = {
            i: load_image(f'assets/sprites/tilesets/{tileset}/background/{time}/{i}.png') for i in range(1, 6)
        }
