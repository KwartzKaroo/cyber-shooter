from scripts.entities.enemy import *


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
        super().__init__(game, level, (17, 40), pos, 1.5, 100, '2', (-6, -8), group)


class EnemyThree(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (20, 24), pos, 1.5, 100, '3', (-6, -24), group)


class EnemyFour(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (17, 34), pos, 1.5, 100, '4', (-8, -14), group)


class EnemyFive(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (17, 35), pos, 1.5, 100, '5', (-15, -13), group)


class EnemySix(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (37, 21), pos, 1.5, 100, '6', (-5, -27), group)


class EnemySeven(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (19, 35), pos, 1.5, 100, '7', (-13, -13), group)


class EnemyEight(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (21, 36), pos, 1.5, 100, '8', (-14, -12), group)
