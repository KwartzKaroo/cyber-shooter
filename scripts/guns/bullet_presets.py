from scripts.audio import SFX
from scripts.guns.bullet import Bullet
from scripts.utils import Animation, load_image, Timer


class Normal(Bullet):
    pass


class FMJ(Bullet):
    def on_impact(self):
        if self.off_screen():
            self.kill()

    def collisions(self):
        for tile in self.level.tilemap.get_collision_tiles(self.rect):
            if tile.rect.colliderect(self.rect):
                self.kill()


class Explosive(Bullet):
    def __init__(self, game, level, image, pos, damage, speed, x_direction, y_direction, group=()):
        super().__init__(game, level, image, pos, damage, speed, x_direction, y_direction, group)

        self.explosion = Animation('assets/sprites/extras/explosion.png', 8, False, (48, 48))
        self.exploded = False

    def collisions(self):
        if self.exploded:
            return

        for tile in self.level.tilemap.get_collision_tiles(self.rect):
            # Vertical collision
            if tile.rect.colliderect(self.rect):
                self.rect.w = 48
                self.rect.h = 48
                if self.velocity[1] > 0:
                    self.rect.bottom = tile.rect.top
                if self.velocity[1] < 0:
                    self.rect.top = tile.rect.bottom
                if self.velocity[0] < 0:
                    self.rect.left = tile.rect.right
                if self.velocity[0] > 0:
                    self.rect.right = tile.rect.left
                self.pos[0] = self.rect.x
                self.pos[1] = self.rect.y

                self.impacted = True

    def on_impact(self):
        if self.explosion.finished:
            self.kill()

        if self.impacted:
            if not self.exploded:
                SFX['explosion'].play()
                self.exploded = True
            self.rect.w = 48
            self.rect.h = 48
            self.velocity *= 0
            self.explosion.update(self.game.delta)
            self.image = self.explosion.get_image()


class Heavy(Bullet):
    pass


class Ball(Bullet):
    def __init__(self, game, level, pos, x_direction, group=()):
        self.ball_images = {
            1: load_image('assets/sprites/enemies/4/Ball1.png'),
            2: load_image('assets/sprites/enemies/4/Ball2.png')
        }
        self.bounces = 0
        self.timer = Timer(1000)
        super().__init__(game, level, self.ball_images[1], pos, 10, 6, x_direction, 0, group)

    def collisions(self):
        if self.bounces > 0:
            self.velocity[1] = min(self.velocity[1] + .155 * self.game.framerate, 8)

        for tile in self.level.tilemap.get_collision_tiles(self.rect):
            # Vertical collision
            if tile.rect.colliderect(self.pos[0], self.pos[1] + self.velocity[1], self.rect.w, self.rect.h):
                self.damage = 0
                self.image = self.ball_images[2]
                if self.velocity[1] >= 0:
                    self.rect.bottom = tile.rect.top
                elif self.velocity[1] < 0:
                    self.rect.top = tile.rect.bottom
                self.pos[1] = self.rect.y
                self.velocity[1] *= -3/6
                self.velocity[0] *= 2/5
                self.bounces += 1

            # Left and right collision
            if tile.rect.colliderect(self.pos[0] + self.velocity[0], self.pos[1], self.rect.w, self.rect.h):
                self.damage = 0
                self.image = self.ball_images[2]
                if self.velocity[0] < 0:
                    self.rect.left = tile.rect.right
                elif self.velocity[0] > 0:
                    self.rect.right = tile.rect.left
                self.pos[0] = self.rect.x
                self.bounces += 1
                self.velocity[0] *= -2/5

    def on_impact(self):
        if self.off_screen():
            self.kill()

        if self.impacted:
            self.kill()

        if self.bounces >= 5:
            self.velocity[0] = 0
            self.velocity[1] = 0
            self.timer.activate()
            # self.kill()

        if self.timer:
            self.timer.update()
            if not self.timer:
                self.kill()

