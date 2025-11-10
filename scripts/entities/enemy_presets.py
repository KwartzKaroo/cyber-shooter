from scripts.entities.enemy import *
from scripts.utils import debug_rect, load_image
from scripts.guns.bullet_presets import Ball


class EnemyOne(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (16, 32), pos, 1.5, 100, '1', (-4, -16), group)
        self.image_offset = (-4, -16)

    def attack(self):
        if self.level.player.zero_health():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 28, self.rect.y, 28, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 28, 16)

        if self.attack_rect.colliderect(self.level.player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 4 and not self.hit_player:
                self.level.player.hp -= 20
                self.level.player.actions['hurt'] = True
                self.hit_player = True
                SFX['punch 1'].play()

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class EnemyTwo(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (17, 40), pos, 1.5, 120, '2', (-6, -8), group)

    def attack(self):
        if self.level.player.zero_health():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 36, self.rect.y, 36, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 36, 16)

        if self.attack_rect.colliderect(self.level.player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            frame = self.animations['attack'].get_frame()
            if frame == 2 or frame == 5:
                if not self.hit_player:
                    self.hit_player = True
                    self.level.player.hp -= 10
                    self.level.player.actions['hurt'] = True
                    SFX['bullet hit'].play()
            else:
                self.hit_player = False

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class EnemyThree(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (20, 24), pos, 1.5, 100, '3', (-6, -24), group)

    def attack(self):
        if self.level.player.zero_health():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.zero_health():
            return

        self.attack_rect = pygame.Rect(self.rect.x - 3, self.rect.y, self.rect.w + 6, self.rect.h)

        if self.attack_rect.colliderect(self.level.player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            SFX['bullet hit'].play()
            frame = self.animations['attack'].get_frame()
            if frame == 0 and not self.hit_player:
                self.hit_player = True
                self.level.player.actions['hurt'] = True
                self.level.player.hp -= 5

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class EnemyFour(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (17, 34), pos, 1.5, 100, '4', (-8, -14), group)

    def attack(self):
        if self.level.player.zero_health():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.zero_health():
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 96, self.rect.y, 96, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 96, 16)

        if self.attack_rect.colliderect(self.level.player):
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 1 and not self.hit_player:
                Ball(self.game, self.level, (self.rect.centerx, self.rect.centery - 3), self.direction, self.level.enemy_projectiles)
                self.hit_player = True
                # SFX['punch 1'].play()

        if self.actions['attack']:
            self.velocity[0] = 0

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class EnemyFive(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (17, 35), pos, 1.5, 120, '5', (-15, -13), group)

    def attack(self):
        if self.level.player.zero_health():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 20, self.rect.y, 20, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 20, 16)

        debug_rect(self.game.layers[4], self.attack_rect, self.level.scroll)

        if self.attack_rect.colliderect(self.level.player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 4 and not self.hit_player:
                self.level.player.hp -= 40
                self.level.player.actions['hurt'] = True
                self.hit_player = True
                SFX['punch 1'].play()

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class EnemySix(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (37, 21), pos, 1.5, 100, '6', (-5, -27), group)

    def attack(self):
        if self.level.player.zero_health():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 28, self.rect.y, 28, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 28, 16)

        debug_rect(self.game.layers[4], self.attack_rect, self.level.scroll)

        if self.attack_rect.colliderect(self.level.player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 4 and not self.hit_player:
                self.level.player.hp -= 20
                self.level.player.actions['hurt'] = True
                self.hit_player = True
                SFX['punch 1'].play()

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class EnemySeven(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (19, 35), pos, 1.5, 100, '7', (-13, -13), group)

    def attack(self):
        if self.level.player.zero_health():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 28, self.rect.y, 28, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 28, 16)

        debug_rect(self.game.layers[4], self.attack_rect, self.level.scroll)

        if self.attack_rect.colliderect(self.level.player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 4 and not self.hit_player:
                self.level.player.hp -= 20
                self.level.player.actions['hurt'] = True
                self.hit_player = True
                SFX['punch 1'].play()

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class EnemyEight(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (21, 36), pos, 1.5, 100, '8', (-14, -12), group)

    def attack(self):
        if self.level.player.zero_health():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 28, self.rect.y, 28, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 28, 16)

        debug_rect(self.game.layers[4], self.attack_rect, self.level.scroll)

        if self.attack_rect.colliderect(self.level.player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 4 and not self.hit_player:
                self.level.player.hp -= 20
                self.level.player.actions['hurt'] = True
                self.hit_player = True
                SFX['punch 1'].play()

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False
