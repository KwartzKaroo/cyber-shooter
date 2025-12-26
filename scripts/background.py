from scripts.utils import load_image


class Background:
    def __init__(self, tileset=None, time='day'):
        # Initialize
        self.images = {}

        # Load data
        if tileset is not None:
            self.load(tileset, time)

    def draw(self, surface, scroll):
        horizontal = scroll[0] / 6
        height = (-scroll[1] - 96 - 4)

        # First layer
        surface.blit(self.images[1], (0, 0))

        # Second layer
        surface.blit(self.images[2], (-((horizontal * 1) % 576), height))
        surface.blit(self.images[2], (-((horizontal * 1) % 576) + 576, height))

        # Third layer
        surface.blit(self.images[3], (-((horizontal * 2) % 576), height))
        surface.blit(self.images[3], (-((horizontal * 2) % 576) + 576, height))

        # Fourth layer
        surface.blit(self.images[4], (-((horizontal * 3) % 576), height))
        surface.blit(self.images[4], (-((horizontal * 3) % 576) + 576, height))

        # Fifth layer
        surface.blit(self.images[5], (-((horizontal * 4) % 576), height))
        surface.blit(self.images[5], (-((horizontal * 4) % 576) + 576, height))

    def load(self, tileset, time):
        self.images = {
            i: load_image(f'assets/sprites/tilesets/{tileset}/background/{time}/{i}.png') for i in range(1, 6)
        }
