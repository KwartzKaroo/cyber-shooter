import pygame


class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, level, image, pos, damage, speed, x_direction, y_direction, group=()):
        super().__init__(group)

        # Access to game and level
        self.game = game
        self.level = level

        # Movement and position
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(x_direction, y_direction).normalize() * speed

        # Image
        self.image = image
        self.rect = pygame.Rect(pos, self.image.get_size())

        # Attributes
        self.damage = damage
        self.impacted = False

    def draw(self):
        self.game.layers[3].blit(self.image, (self.pos[0] - self.level.scroll[0], self.pos[1] - self.level.scroll[1]))

    def update_pos(self):
        self.pos += self.velocity * self.game.framerate
        self.rect = pygame.Rect(self.pos, self.rect.size)

    def off_screen(self):
        return (self.rect.right < self.level.scroll[0] or self.rect.left > self.level.scroll[0] + 576 or
                self.rect.bottom < self.level.scroll[1] or self.rect.top > self.level.scroll[1] + 320)

    def collisions(self):
        for tile in self.level.tilemap.get_collision_tiles(self.rect):
            if tile.rect.colliderect(self.rect):
                self.impacted = True

    def on_impact(self):
        if self.off_screen():
            self.kill()

        if self.impacted:
            self.kill()

    def update(self):
        self.draw()
        self.on_impact()
        self.collisions()
        self.update_pos()
