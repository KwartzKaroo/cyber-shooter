import math
import random
import pygame
import pickle

# Remember, the standard damage is 10

from scripts.audio import GUN_SHOT_SFX
from scripts.globals import FPS, GUNS, EFFECTS, SPECS, INDEX_TO_DIRECTION
from scripts.projectile import Normal, FMJ, Explosive, Electric
from scripts.utils import load_image, Timer, Animation

BULLETS = {
    'normal': Normal,
    'FMJ': FMJ,
    'explosive': Explosive,
    'electric': Electric
}

GUN_OFFSETS = pickle.loads(open('data/guns/offsets', 'rb').read())
GUN_ATTRIBUTES = pickle.loads(open('data/guns/attributes', 'rb').read())


class Gun:
    def __init__(self, level, name, position=(0, 0)):
        # Access to level
        self.level = level

        # Gun attributes
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
            1: load_image(f'assets/sprites/weapons/guns/{name}_1.png'),
            2: load_image(f'assets/sprites/weapons/guns/{name}_2.png'),
        }

        self.bullet_images = {
            1: load_image(f'assets/sprites/weapons/bullets/{name}_1.png'),
            2: load_image(f'assets/sprites/weapons/bullets/{name}_2.png'),
        }

        self.effect_animations = {
            1: Animation(f'assets/sprites/weapons/shoot effects/{EFFECTS[GUN_ATTRIBUTES[name]["effect"]]}_1.png',
                         GUN_ATTRIBUTES[name]['effect fps'], False),
            2: Animation(f'assets/sprites/weapons/shoot effects/{EFFECTS[GUN_ATTRIBUTES[name]["effect"]]}_2.png',
                         GUN_ATTRIBUTES[name]['effect fps'], False),
        }

        self.image = self.gun_images[1]
        self.bullet_image = self.bullet_images[1]
        self.effect_image = self.effect_animations[1].get_image()
        self.play_effect = False
        self.effect_pos = list(position)
        self.position = pygame.Vector2(position)
        self.rect = self.image.get_rect(topleft=self.position)
        self.rect.left -= 15
        self.rect.w += 30
        self.direction = 1

        # Floating
        self.float_var = random.randint(0, 45)

    def draw(self, surface, scroll):
        surface.blit(self.image, (self.position[0] - scroll[0], self.position[1] - scroll[1]))
        if self.play_effect:
            surface.blit(self.effect_image,
                                     (self.effect_pos[0] - scroll[0],
                                      self.effect_pos[1] - scroll[1]))

    def floating(self):
        self.float_var = (self.float_var + self.level.game.delta * FPS / 18) % 360
        self.level.canvases[4].blit(self.gun_images[1],
                     (self.position[0] - self.level.camera.x, self.position[1] + math.sin(self.float_var) * 5 - self.level.camera.y))

    def update(self, delta, position, flip, direction, hand_index):
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
            self.effect_animations[specs['type']].update(delta)
            image = pygame.transform.rotate(self.effect_animations[specs['type']].get_image(), specs['angle'])
            self.effect_image = pygame.transform.flip(image, flip, False)
            if self.effect_animations[specs['type']].finished:
                self.play_effect = False
                self.effect_animations[1].reset()
                self.effect_animations[2].reset()

        # Update position
        self.position = [position[0] - self.image.get_width() * flip, position[1]]

        # Update effect position
        offset = GUN_OFFSETS['effect offsets'][self.name][hand_index]
        self.effect_pos = [position[0] + offset[0] * direction - 48 * flip, position[1] + offset[1]]

        # Update rect
        self.rect = self.image.get_rect(topleft=self.position)
        self.rect.left -= 15
        self.rect.w += 30

    def bullet_position(self, direction, hand_index):
        position = list(self.position)
        offset = GUN_OFFSETS['bullet offsets'][self.name][hand_index]

        if direction < 0:
            position[0] += self.image.get_width() - self.bullet_image.get_width()

        position[0] += offset[0] * direction
        position[1] += offset[1]

        return position

    def shoot(self, player_direction, hand_index, bullet_group):
        # Get direction from the hand_index
        direction = INDEX_TO_DIRECTION[hand_index]

        # Create the bullet and store in the group
        if not self.fire_rate and self.ammo > 0:
            GUN_SHOT_SFX[self.name].play()
            BULLETS[self.bullet_type](self.level, self.bullet_image, self.bullet_position(player_direction, hand_index),
                       self.damage, self.bullet_speed, player_direction * direction[0], direction[1],
                       bullet_group)
            self.ammo -= 1
            self.play_effect = True
            self.fire_rate.activate()

        # Update the fire rate
        self.fire_rate.update()

    def onscreen(self, screen_size, scroll):
        return (self.rect.right > scroll[0] - 64 or self.rect.left < scroll[0] + screen_size[0] + 64 or
                self.rect.bottom > scroll[1] - 64 or self.rect.top < scroll[1] + screen_size[1] + 64)

    def __repr__(self):
        return f'Gun {self.name}'