import pygame
from scripts.globals import *


class Entity(pygame.sprite.Sprite):
    def __init__(self, level, size, position, speed, hp, group=()):
        super().__init__(group)
        self.level = level

        # Position and movement
        self.position = pygame.Vector2(position[0], position[1] + (32 - size[1]))
        self.velocity = pygame.Vector2()
        self.speed = speed
        self.jump_count = 0
        self.direction = 1
        self.is_on_floor = True

        # Image
        self.image = pygame.Surface(size)
        self.image.fill('orange')
        self.flip = False

        # Rect for collision
        self.rect = pygame.Rect(position, size)
        self.bottom_rect = pygame.Rect(self.rect.x + 1, self.rect.bottom, self.rect.w - 2, 1)
        self.overhead_rect = pygame.Rect(self.rect.x - 2, self.rect.top - 2, self.rect.w + 4, 1)
        self.ramp_rect = pygame.Rect(self.rect.left - 4, self.rect.bottom, 8, 4)

        # Health
        self.hurt = 0
        self.init_hp = hp
        self.hp = hp
        self.dead = False
        self.knocked_back = False
        self.knock_type = 1
        self.knockback_force = pygame.Vector2()
        self.bullets_touched = []

    def apply_gravity(self):
        if not self.is_on_floor:
            self.velocity[1] = min(self.velocity[1] + GRAVITY * self.level.game.delta * FPS, TERMINAL_VELOCITY)

    def health_depleted(self):
        return self.hp <= 0

    def knockback(self, x, y=0, knock_type=1):
        self.knockback_force = pygame.Vector2(x, y)
        self.knocked_back = True
        self.knock_type = knock_type

    def update_knockback(self):
        if not self.knocked_back:
            return

        if self.knock_type == 1:
            self.knockback_force[1] = 0
            if self.knockback_force[0] > 0:
                self.knockback_force[0] -= self.level.game.delta * 20
                if self.knockback_force[0] <= 0:
                    self.knocked_back = False
                    self.knockback_force = pygame.Vector2()

            if self.knockback_force[0] < 0:
                self.knockback_force[0] += self.level.game.delta * 20
                if self.knockback_force[0] >= 0:
                    self.knocked_back = False
                    self.knockback_force = pygame.Vector2()

        if self.knock_type == 2:
            self.knockback_force[1] = min(self.knockback_force[1] + GRAVITY * self.level.game.delta * FPS, 8)
            if self.knockback_force[1] >= 0:
                self.knock_type = 1

    def take_melee_damage(self, damage):
        self.hp -= damage
        self.hurt = 1

    def update_health(self):
        pass

    def on_death(self):
        pass

    def tile_collisions(self, tiles):
        self.is_on_floor = False
        for tile in tiles:
            # Vertical collision
            if tile.rect.colliderect(self.position[0], self.position[1] + self.velocity[1], self.rect.w, self.rect.h):
                if self.velocity[1] >= 0:
                    self.rect.bottom = tile.rect.top
                    self.jump_count = 0
                    self.is_on_floor = True
                elif self.velocity[1] < 0:
                    self.rect.top = tile.rect.bottom
                self.velocity[1] = 0
                self.position[1] = self.rect.y

            # Left and right collision
            if tile.rect.colliderect(self.position[0] + self.velocity[0], self.position[1], self.rect.w, self.rect.h):
                if self.velocity[0] < 0:
                    self.rect.left = tile.rect.right
                elif self.velocity[0] > 0:
                    self.rect.right = tile.rect.left
                self.velocity[0] = 0
                self.position[0] = self.rect.x

    def ramp_collisions(self, ramps):
        for ramp in ramps:
            if ramp.rect.colliderect(self.position[0], self.position[1], self.rect.w, self.rect.h):
                if pygame.sprite.collide_mask(self, ramp):
                    self.velocity[1] = 0
                    self.jump_count = 0
                    self.is_on_floor = True
                    if ramp.index == 1:
                        self.rect.bottom = ramp.rect.bottom + (self.rect.left - ramp.rect.right)
                    if ramp.index == 0:
                        self.rect.bottom = ramp.rect.bottom + (ramp.rect.left - self.rect.right)
                    self.position[1] = self.rect.y

    def update_position(self):
        self.update_knockback()

        self.position += (self.velocity + self.knockback_force) * self.level.game.delta * FPS
        self.rect = pygame.Rect(self.position, self.rect.size)

        # Update rects
        self.bottom_rect = pygame.Rect(self.rect.x + 1, self.rect.bottom, self.rect.w - 2, 2)
        self.overhead_rect = pygame.Rect(self.rect.x - 2, self.rect.top - 2, self.rect.w + 4, 1)

        if self.flip:
            self.ramp_rect = pygame.Rect(self.rect.right - 4, self.rect.bottom, 8, 4)
        else:
            self.ramp_rect = pygame.Rect(self.rect.left - 4, self.rect.bottom, 8, 4)

    def boss_fight_bounds(self):
        if self.level.boss_fight:
            if self.rect.x < self.level.boundaries[0]:
                self.rect.left = self.level.boundaries[0]
                self.position.x = self.rect.x
            if self.rect.right > self.level.boundaries[1]:
                self.rect.right = self.level.boundaries[1]
                self.position.x = self.rect.x

    def offscreen(self):
        return not self.level.camera.on_screen(self, 64)
