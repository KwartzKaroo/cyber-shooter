import math
import random

import pygame

from scripts.audio import GUN_SHOTS
from scripts.constants import FPS, GUNS, EFFECTS
from scripts.constants import SPECS, INDEX_TO_DIRECTION
from scripts.data import GUN_ATTRIBUTES, GUN_OFFSETS
from scripts.guns.bullet_presets import Normal, FMJ, Explosive
from scripts.utils import load_image, Timer, Animation

BULLETS = {
    'normal': Normal,
    'FMJ': FMJ,
    'explosive': Explosive
}


class Gun:
    def __init__(self, game, level, name, pos=(0, 0)):
        # Access to game and level
        self.game = game
        self.level = level

        # Attributes
        self.name = name
        self.type = GUNS[name]['type']
        self.damage = GUN_ATTRIBUTES[name]['damage']
        self.fire_rate = Timer(1000 - GUN_ATTRIBUTES[name]['fire rate'])
        self.mag_size = GUN_ATTRIBUTES[name]['mag size']
        self.ammo = GUN_ATTRIBUTES[name]['mag size']
        self.bullet_speed = GUN_ATTRIBUTES[name]['bullet speed']
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

        self.effect_animations = {
            1: Animation(f'assets/sprites/guns/shoot effects/1/{EFFECTS[GUN_ATTRIBUTES[name]["effect"]]}.png',
                         GUN_ATTRIBUTES[name]['effect fps'], False, (48, 48)),
            2: Animation(f'assets/sprites/guns/shoot effects/2/{EFFECTS[GUN_ATTRIBUTES[name]["effect"]]}.png',
                         GUN_ATTRIBUTES[name]['effect fps'], False, (48, 48)),
        }

        self.image = self.gun_images[1]
        self.bullet_image = self.bullet_images[1]
        self.effect_image = self.effect_animations[1].get_image()
        self.play_effect = False
        self.effect_pos = list(pos)
        self.pos = list(pos)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.rect.left -= 15
        self.rect.w += 30
        self.direction = 1

        # Floating
        self.float_var = random.randint(0, 45)

    def draw(self):
        self.game.layers[4].blit(self.image, (self.pos[0] - self.level.scroll[0], self.pos[1] - self.level.scroll[1]))
        if self.play_effect:
            self.game.layers[4].blit(self.effect_image,
                                     (self.effect_pos[0] - self.level.scroll[0],
                                      self.effect_pos[1] - self.level.scroll[1]))

    def floating(self):
        self.float_var = (self.float_var + self.game.delta * FPS / 18) % 360
        self.game.layers[3].blit(self.gun_images[1],
                                 (self.pos[0] - self.level.scroll[0],
                                  self.pos[1] + math.sin(self.float_var) * 5 - self.level.scroll[1]))

    def update(self, pos, flip, direction, hand_index):
        # Get specs
        specs = SPECS[hand_index]

        # Update gun image
        image = pygame.transform.rotate(self.gun_images[specs['type']], specs['angle'])
        self.image = pygame.transform.flip(image, flip, False)

        # Update bullet image
        image = pygame.transform.rotate(self.bullet_images[specs['type']], specs['angle'])
        self.bullet_image = pygame.transform.flip(image, flip, False)

        # Update effect image
        if self.play_effect:
            self.effect_animations[specs['type']].update(self.game.delta)
            image = pygame.transform.rotate(self.effect_animations[specs['type']].get_image(), specs['angle'])
            self.effect_image = pygame.transform.flip(image, flip, False)
            if self.effect_animations[specs['type']].finished:
                self.play_effect = False
                self.effect_animations[1].reset()
                self.effect_animations[2].reset()

        # Update position
        self.pos = [pos[0] - self.image.get_width() * flip, pos[1]]

        # Update effect position
        offset = GUN_OFFSETS['effect offsets'][self.name][hand_index]
        self.effect_pos = [pos[0] + offset[0] * direction - 48 * flip, pos[1] + offset[1]]

        # Update rect
        self.rect = self.image.get_rect(topleft=self.pos)
        self.rect.left -= 15
        self.rect.w += 30

    def bullet_position(self, direction, hand_index):
        pos = list(self.pos)
        offset = GUN_OFFSETS['bullet offsets'][self.name][hand_index]

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
            GUN_SHOTS[self.name].play()
            BULLETS[self.bullet_type](self.game, self.level, self.bullet_image,
                                      self.bullet_position(player_direction, hand_index),
                                      self.damage, self.bullet_speed, player_direction * direction[0], direction[1],
                                      bullet_group)
            self.ammo -= 1
            self.play_effect = True
            self.fire_rate.activate()

        # Update the fire rate
        self.fire_rate.update()
