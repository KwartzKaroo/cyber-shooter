import pygame

from scripts.audio import MISC_SFX
from scripts.globals import FPS, GRAVITY, TERMINAL_VELOCITY
from scripts.utils import Animation, Timer, load_image

# Some preloaded images to be used in explosions
EXPLOSION_IMAGE = load_image('assets/sprites/misc/explosion1.png')
ELECTRIC_IMAGE = load_image('assets/sprites/misc/electric.png')


class Projectile(pygame.sprite.Sprite):
    def __init__(self, level, image, position, damage, speed, x_direction, y_direction, group=()):
        super().__init__(group)
        # Access to level
        self.level = level

        # Movement and position
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(x_direction, y_direction).normalize() * speed

        # Image
        self.image = image
        self.rect = pygame.Rect(position, self.image.get_size())

        # Attributes
        self.damage = damage
        self.hit_entity = False
        self.hit_tiles = False
        self.knockback_force = (0, 0)

    def draw(self):
        self.level.canvases[3].blit(self.image, (self.position[0] - self.level.camera[0], self.position[1] - self.level.camera[1]))

    def apply_gravity(self):
        pass

    def update_position(self):
        self.position += self.velocity * self.level.game.delta * FPS
        self.rect = pygame.Rect(self.position, self.rect.size)

    def off_screen(self, scroll):
        return (self.rect.right < scroll[0] or self.rect.left > scroll[0] + 576 or
                self.rect.bottom < scroll[1] or self.rect.top > scroll[1] + 320)

    def collisions(self, tiles):
        for tile in tiles:
            if tile.rect.colliderect(self.rect):
                self.hit_tiles = True

    def on_impact(self):
        pass

    def update(self):
        if not self.level.camera.on_screen(self, 32):
            self.kill()

        # Get tiles for collisions
        tiles = self.level.tilemap.get_tiles_around('tiles', self.rect)
        self.apply_gravity()
        self.collisions(tiles)
        self.on_impact()
        self.update_position()
        self.draw()


class Normal(Projectile):
    def on_impact(self):
        if self.hit_entity or self.hit_tiles:
            self.kill()


class FMJ(Projectile):
    def on_impact(self):
        if self.hit_tiles:
            self.kill()


class Explosive(Projectile):
    def __init__(self, level, image, pos, damage, speed, x_direction, y_direction, group=()):
        super().__init__(level, image, pos, damage, speed, x_direction, y_direction, group)

        self.explosion_animation = Animation(EXPLOSION_IMAGE, 8, False)
        self.exploded = False
        self.knockback_force = (6 * x_direction, -2.5)

    def collisions(self, tiles):
        if self.exploded:
            return

        for tile in tiles:
            if tile.rect.colliderect(self.position[0], self.position[1] + self.velocity[1], self.rect.w, self.rect.h):
                self.rect.w = 48
                self.rect.h = 48
                if self.velocity.y > 0:
                    self.rect.bottom = tile.rect.top
                elif self.velocity.y < 0:
                    self.rect.top = tile.rect.bottom
                self.position.x = self.rect.x - 24
                self.position.y = self.rect.y
                self.hit_tiles = True
                return

            if tile.rect.colliderect(self.position[0] + self.velocity[0], self.position[1], self.rect.w, self.rect.h):
                self.rect.w = 48
                self.rect.h = 48
                if self.velocity.x < 0:
                    self.rect.left = tile.rect.right
                elif self.velocity.x > 0:
                    self.rect.right = tile.rect.left
                self.position.x = self.rect.x
                self.position.y = self.rect.y - 24
                self.hit_tiles = True
                return

    def on_impact(self):
        if self.explosion_animation.finished:
            self.kill()

        if self.hit_tiles or self.hit_entity:
            self.explosion_animation.update(self.level.game.delta)
            self.image = self.explosion_animation.get_image()
            if not self.exploded:
                self.level.camera.shake_screen(300, 4)
                MISC_SFX['explosion 1'].play()
                self.exploded = True
                self.velocity = pygame.Vector2()
                if self.hit_entity:
                    self.rect = self.rect.inflate(48, 48)

            if self.explosion_animation.get_frame() >= 3:
                self.rect.size = (0, 0)


class Electric(Projectile):
    def __init__(self, level, image, pos, damage, speed, x_direction, y_direction, group=()):
        super().__init__(level, image, pos, damage, speed, x_direction, y_direction, group)

        self.explosion = Animation(ELECTRIC_IMAGE, 4, False, (32, 32))
        self.exploded = False

    def on_impact(self):
        if self.explosion.finished:
            self.kill()

        if self.hit_tiles:
            self.kill()

        if self.hit_entity:
            if not self.exploded:
                MISC_SFX['electroshock'].play()
                self.exploded = True
                self.velocity = pygame.Vector2()
            self.explosion.update(self.level.game.delta)
            self.image = self.explosion.get_image()


class ElectricBolt(Normal):
    def __init__(self, level, image, position, damage, speed, x_direction, y_direction, group=()):
        self.animation = Animation(image, 9, True, (16, 16))

        super().__init__(level, self.animation.get_image(), position, damage, speed, x_direction, y_direction, group)

    def draw(self):
        self.image = self.animation.get_image()
        self.level.canvases[3].blit(self.image, (self.position[0] - self.level.camera[0], self.position[1] - self.level.camera[1]))


class ThrownProjectile(Normal):
    def __init__(self, level, image, position, damage, speed, x_direction, y_direction, group):
        super().__init__(level, image, position, damage, speed, x_direction, y_direction, group)

        self.velocity = pygame.Vector2(x_direction * speed, y_direction)

    def apply_gravity(self):
        if not (self.hit_tiles or self.hit_entity):
            self.velocity[1] = min(self.velocity[1] + GRAVITY * self.level.game.delta * FPS, TERMINAL_VELOCITY)


class RugbyBall(Normal):
    def __init__(self, level, image, position, x_direction, group=()):
        super().__init__(level, image, position, 10, 6, x_direction, 0, group)
        self.timer = Timer(1000)
        self.bounces = 0

    def apply_gravity(self):
        if self.bounces > 0:
            self.velocity[1] = min(self.velocity[1] + GRAVITY * self.level.game.delta * FPS, TERMINAL_VELOCITY)

    def collisions(self, tiles):
        for tile in tiles:
            # Vertical collision
            if tile.rect.colliderect(self.position[0], self.position[1] + self.velocity[1], self.rect.w, self.rect.h):
                self.damage = 0
                if self.velocity[1] >= 0:
                    self.rect.bottom = tile.rect.top
                elif self.velocity[1] < 0:
                    self.rect.top = tile.rect.bottom
                self.position[1] = self.rect.y
                self.velocity[1] *= -3/6
                self.velocity[0] *= 2/5
                self.bounces += 1

            # Left and right collision
            if tile.rect.colliderect(self.position[0] + self.velocity[0], self.position[1], self.rect.w, self.rect.h):
                self.damage = 0

                if self.velocity[0] < 0:
                    self.rect.left = tile.rect.right
                elif self.velocity[0] > 0:
                    self.rect.right = tile.rect.left
                self.position[0] = self.rect.x
                self.bounces += 1
                self.velocity[0] *= -2/5

    def on_impact(self):
        if self.hit_entity and self.bounces == 0:
            self.velocity[0] *= -0.2
            self.bounces = 1

        if self.bounces >= 5:
            self.velocity[0] = 0
            self.velocity[1] = 0
            self.timer.activate()

        if self.timer:
            self.timer.update()
            if not self.timer:
                self.kill()


class Missile(Explosive, ThrownProjectile):
    def __init__(self, level, image, position, damage, speed, x_direction, y_direction, group):
        super().__init__(level, image, position, damage, speed, x_direction, y_direction, group)
        self.velocity = pygame.Vector2(x_direction * speed, y_direction)



