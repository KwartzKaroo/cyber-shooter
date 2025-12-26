import random

from scripts.globals import SCREEN_SIZE
from scripts.utils import Timer


class Camera:
    def __init__(self, position=(0, 0), bounds=(0, -1_000_000, 1_000_000, 1_000_000)):
        self.x, self.y = position
        self.right = self.x + SCREEN_SIZE[1]
        self.bottom = self.y + SCREEN_SIZE[1]
        self.bounds = {
            'left': bounds[0],
            'top': bounds[1],
            'right': bounds[2],
            'bottom': bounds[3]
        }

        self.precise_x, self.precise_y = position

        self.shake = False
        self.shake_duration = Timer(0)
        self.shake_strength = 0

    def scroll(self, entity, smoothing=2):
        self.precise_x += (entity.rect.centerx - SCREEN_SIZE[0] // 2 - self.precise_x) / smoothing
        self.precise_y += (entity.rect.top - 32 - SCREEN_SIZE[1] // 2 - self.precise_y) / (smoothing * 1.5)

        # Update coordinates
        self.x = self.precise_x
        self.y = int(self.precise_y)

        # Screen shake
        if self.shake_duration:
            self.shake_duration.update()
            self.x += random.uniform(-self.shake_strength / 2, self.shake_strength / 2)
            self.y += random.uniform(-self.shake_strength / 2, self.shake_strength / 2)

        # Update the other coordinates
        self.right = self.x + SCREEN_SIZE[0]
        self.bottom = self.y + SCREEN_SIZE[1]

        # Boundary checks
        if self.x < self.bounds['left']:
            self.x = self.bounds['left']

        if self.right > self.bounds['right']:
            self.x = self.bounds['right'] - SCREEN_SIZE[0]

        if self.y < self.bounds['top']:
            self.y = self.bounds['top']

        if self.bottom > self.bounds['bottom']:
            self.y = self.bounds['bottom'] - SCREEN_SIZE[1]

    def shake_screen(self, duration, strength):
        self.shake_strength = strength
        self.shake_duration.set_duration(duration)
        self.shake_duration.activate()

    def update(self):
        pass

    def on_screen(self, item, margin=64):
        return (item.rect.right > self.x - margin and item.rect.left < self.right + margin and
                item.rect.bottom > self.y - margin and item.rect.top < self.bottom + margin)

    def __getitem__(self, item):
        if item == 0:
            return self.x
        if item == 1:
            return self.y
        if item == 2:
            return self.right
        if item == 3:
            return self.bottom

        raise IndexError('Index is out of bounds')

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
            return
        if key == 1:
            self.y = value
            return
        if key == 2:
            self.right = value
            return
        if key == 3:
            self.bottom = value
            return

        raise IndexError('Index is out of bounds')