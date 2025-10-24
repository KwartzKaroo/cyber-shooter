import pygame


class Body(pygame.sprite.Sprite):
    def __init__(self, game, level, size, pos, speed, hp, image_offset=(0, 0), group=()):
        super().__init__(group)

        # Access to game and level class
        self.game = game
        self.level = level

        # Position and movement
        self.pos = pygame.Vector2(pos[0], pos[1] + (32 - size[1]))
        self.velocity = pygame.Vector2()
        self.speed = speed
        self.is_on_floor = False
        self.jump_count = 0
        self.direction = 1

        # Image
        self.image_offset = image_offset
        self.image = pygame.Surface(size)
        self.image.fill('orange')
        self.flip = False

        # Rects
        self.rect = pygame.Rect(pos, size)
        self.bottom_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.w, 1)

        # Health
        self.init_hp = hp
        self.hp = hp

    def draw(self):
        self.game.layers[4].blit(self.image, self.image_position())

    def image_position(self):
        return self.pos[0] - self.level.scroll[0], self.pos[1] - self.level.scroll[1]

    def check_on_floor(self):
        tiles = self.level.tilemap.get_collision_tiles(self.rect)
        self.is_on_floor = False
        if self.bottom_rect.collidelistall(tiles):
            self.is_on_floor = True

    def apply_gravity(self):
        if not self.is_on_floor:
            self.velocity[1] = min(self.velocity[1] + .155 * self.game.delta, 8)

    def tile_collisions(self):
        for tile in self.level.tilemap.get_collision_tiles(self.rect):
            # Vertical collision
            if tile.rect.colliderect(self.pos[0], self.pos[1] + self.velocity[1], self.rect.w, self.rect.h):
                self.velocity[1] = 0
                if self.velocity[1] >= 0:
                    self.rect.bottom = tile.rect.top
                    self.jump_count = 0
                elif self.velocity[1] < 0:
                    self.rect.top = tile.rect.bottom
                self.pos[1] = self.rect.y

            # Left and right collision
            if tile.rect.colliderect(self.pos[0] + self.velocity[0], self.pos[1], self.rect.w, self.rect.h):
                if self.velocity[0] < 0:
                    self.rect.left = tile.rect.right
                elif self.velocity[0] > 0:
                    self.rect.right = tile.rect.left
                self.velocity[0] = 0
                self.pos[0] = self.rect.x

    def ramp_collisions(self):
        ramps = self.level.tilemap.get_collision_ramps(self.rect)
        for ramp in ramps:
            if ramp.rect.colliderect(self.pos[0], self.pos[1], self.rect.w, self.rect.h):
                self.velocity[1] = 0
                self.jump_count = 0
                if ramp.index == 0:
                    self.rect.bottom = ramp.rect.bottom + (self.rect.left - ramp.rect.right)
                if ramp.index == 1:
                    self.rect.bottom = ramp.rect.bottom + (ramp.rect.left - self.rect.right)
                self.pos[1] = self.rect.y

    def boundary_collision(self):
        for boundary in self.level.tilemap.get_boundaries(self.rect):
            if boundary.rect.colliderect(self):
                self.hp = -1

    def update_position(self):
        self.pos += self.velocity * self.game.delta

        # Update rect
        self.rect = pygame.Rect(self.pos, self.rect.size)
        self.bottom_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.w, 1)

    def center(self):
        return self.pos[0] + self.rect.w / 2, self.pos[1] + self.rect.h / 2

    def zero_health(self):
        return self.hp <= 0

    def off_screen(self):
        return (self.rect.right < self.level.scroll[0] - 64 or self.rect.left > self.level.scroll[0] + 576 + 64 or
                self.rect.bottom < self.level.scroll[1] - 64 or self.rect.top > self.level.scroll[1] + 320 + 64)

    def update(self, *args, **kwargs):
        pass
