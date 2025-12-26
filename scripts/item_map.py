import pygame
from scripts.globals import GUN_NAMES, SCREEN_SIZE
from scripts.utils import Animation, load_image
from scripts.gun import Gun


class ItemMap:
    def __init__(self, level, data=None):
        # Access to level
        self.level = level

        self.chests = []
        self.guns = []
        self.chest_image = None

        if data is not None:
            self.load(data)

    def draw(self):
        # Draw chests
        for chest in self.chests:
            if self.level.camera.on_screen(chest, 10):
                chest.update(self.guns)
                chest.draw()

        # Draw guns
        for gun in self.guns:
            if gun.onscreen(SCREEN_SIZE, self.level.camera):
                gun.floating()

    def load(self, data):
        self.chest_image = load_image(f'assets/sprites/chests/{data["tileset"]}.png')

        for value in data['data']['guns'].values():
            pos = value['pos'][0], value['pos'][1]
            size = (self.chest_image.get_height(), self.chest_image.get_height())
            if data["tileset"] == 'green zone':
                size = (32, 22)
            self.chests.append(Chest(self.level, self.chest_image, size, GUN_NAMES[value['index']], pos))


class Chest:
    def __init__(self, level, image, size, gun_name, position):
        self.level = level
        self.animation = Animation(image, 5, False, size)
        self.image = self.animation.get_image()
        self.position = pygame.Vector2(position[0], position[1] + (32 - size[1]))
        self.rect = pygame.Rect(position, (size[0], 32))
        self.rect.y = self.rect.y
        self.opened = False
        self.unlocked = False
        self.gun_name = gun_name

    def update(self, gun_list: list):
        if self.unlocked and not self.opened:
            self.animation.update(self.level.game.delta)
            self.image = self.animation.get_image()
            if self.animation.finished:
                self.opened = True
                gun_list.append(Gun(self.level, self.gun_name, self.rect.topleft))

    def draw(self):
        self.level.canvases[3].blit(self.image, (self.position[0] - self.level.camera[0], self.position[1] - self.level.camera[1]))

    def open(self):
        self.unlocked = True
