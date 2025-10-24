import math
import random
import pygame
from scripts.bullet import Bullet
from scripts.utils import load_image, Timer
from scripts.constants import SPECS, INDEX_TO_DIRECTION
from scripts.constants import GUNS
from scripts.data import BULLET_OFFSETS


class Gun:
    def __init__(self, game, level, name, pos=(0, 0)):
        # Access to game and level
        self.game = game
        self.level = level

        # Attributes
        self.name = name
        self.type = GUNS[name]['type']
        self.damage = GUNS[name]['dmg']
        self.fire_rate = Timer(1000 - GUNS[name]['fire rate'])
        self.mag_size = GUNS[name]['mag size']
        self.ammo = GUNS[name]['mag size']
        self.bullet_speed = GUNS[name]['speed']
        self.bullet_type = GUNS[name]['bullet type']
        self.automatic = GUNS[name]['auto']

        # Images
        self.gun_images = {
            1: load_image(f'assets/sprites/guns/guns/1/{name}.png'),
            2: load_image(f'assets/sprites/guns/guns/2/{name}.png'),
        }

        self.bullet_images = {
            1: load_image(f'assets/sprites/guns/bullets/1/{name}.png'),
            2: load_image(f'assets/sprites/guns/bullets/2/{name}.png'),
        }

        self.image = self.gun_images[1]
        self.bullet_image = self.bullet_images[1]
        self.pos = list(pos)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.rect.left -= 15
        self.rect.w += 30
        self.direction = 1

        # Floating
        self.float_var = random.randint(0, 45)

    def draw(self):
        self.game.layers[4].blit(self.image, (self.pos[0] - self.level.scroll[0], self.pos[1] - self.level.scroll[1]))

    def floating(self):
        self.float_var = (self.float_var + self.game.delta / 18) % 360
        self.game.layers[3].blit(self.gun_images[1],
                                  (self.pos[0] - self.level.scroll[0],
                                   self.pos[1] + math.sin(self.float_var) * 5  - self.level.scroll[1]))

    def update(self, pos, flip, hand_index):
        # Get specs
        specs = SPECS[hand_index]

        # Update gun image
        image = pygame.transform.rotate(self.gun_images[specs['type']], specs['angle'])
        self.image = pygame.transform.flip(image, flip, False)

        # Update bullet image
        image = pygame.transform.rotate(self.bullet_images[specs['type']], specs['angle'])
        self.bullet_image = pygame.transform.flip(image, flip, False)

        # Update position
        self.pos = [pos[0] - self.image.get_width() * flip, pos[1]]

        # Update rect
        self.rect = self.image.get_rect(topleft=self.pos)
        self.rect.left -= 15
        self.rect.w += 30

    def bullet_position(self, direction, hand_index):
        pos = list(self.pos)
        offset = BULLET_OFFSETS['bullet_offsets'][self.name][hand_index]

        if direction < 0:
            pos[0] += self.image.get_width() - self.bullet_image.get_width()

        pos[0] += offset[0] * direction
        pos[1] += offset[1]

        return pos

    def shoot(self, player_direction, hand_index, bullet_group):
        # Get direction from the hand_index
        direction = INDEX_TO_DIRECTION[hand_index]

        # Create the bullet and store in the group
        if not self.fire_rate and self.ammo > 0:
            Bullet(self.game, self.level, self.bullet_image, self.bullet_position(player_direction, hand_index),
                   self.damage, self.bullet_speed, player_direction * direction[0], direction[1], bullet_group)
            self.ammo -= 1
            self.fire_rate.activate()

        # Update the fire rate
        self.fire_rate.update()

