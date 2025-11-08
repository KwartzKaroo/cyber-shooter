from scripts.audio import SFX
from scripts.guns.bullet import Bullet
from scripts.utils import Animation


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

        self.explosion = Animation('assets/sprites/extras/explosion.png', 8, False, size=(48, 48))
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
