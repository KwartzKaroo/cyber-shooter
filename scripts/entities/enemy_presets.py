from scripts.entities.enemy import *
from scripts.utils import debug_rect, load_image
from scripts.guns.bullet_presets import Ball, Normal


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
                self.level.player.hurt = 1
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
                    self.level.player.hurt = 1
                    SFX['bullet hit'].play()
            else:
                self.hit_player = False

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class EnemyThree(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (20, 24), pos, 1.5, 100, '3', (-6, -24), group)

        self.hit_player_sound = 'grinder'
        self.take_damage_sound = 'robot hurt'

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
                self.level.player.hurt = 1
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
                self.level.player.hurt = 1
                self.hit_player = True
                SFX['punch 1'].play()

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class EnemySix(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (37, 21), pos, 1.5, 100, '6', (-5, -27), group)

        self.take_damage_sound = 'robot hurt'
        self.death_sound = 'robot death 2'

    def roam(self):
        # Reset velocity to 0
        self.velocity[0] = 0
        self.actions['walk'] = False

        # Ignore roaming when player is spotted or dead
        if self.sees_player or self.zero_health():
            return

        # Continue walking if distance has not been covered
        if int(self.walk_distance) == int(self.distance // 2):
            self.direction *= -1

        if self.walk_distance < self.distance and not self.is_on_edge and not self.is_by_wall:
            self.actions['walk'] = True
            self.velocity[0] = self.speed * self.direction
            self.walk_distance += self.speed * self.game.framerate
            return

        # Start waiting after walking a certain distance
        if not self.stop_timer:
            self.stop_timer.activate()

        # Update timer if it is active
        if self.stop_timer:
            self.stop_timer.update()
            if not self.stop_timer:
                self.stop_timer.set_duration(random.randint(1000, 3000))
                self.direction *= -1
                self.walk_distance = 0

    def attack(self):
        if self.level.player.zero_health():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 22, self.rect.y, 22, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 22, 16)

        # debug_rect(self.game.layers[4], self.attack_rect, self.level.scroll)

        if self.attack_rect.colliderect(self.level.player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 4 and not self.hit_player:
                self.level.player.hp -= 40
                self.level.player.hurt = 1
                self.hit_player = True
                SFX['punch 1'].play()

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class EnemySeven(Enemy):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (19, 35), pos, 1.5, 100, '7', (-13, -13), group)

        self.bullet_image = load_image('assets/sprites/enemies/7/projectile.png')

    def attack(self):
        if self.level.player.zero_health():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 128, self.rect.y, 128, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 128, 16)

        if self.attack_rect.colliderect(self.level.player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 1 and not self.hit_player:
                if self.flip:
                    Normal(self.game, self.level, self.bullet_image, (self.rect.centerx - 10, self.rect.centery - 10),
                           10, 5, self.direction, 0, self.level.enemy_projectiles)
                else:
                    Normal(self.game, self.level, self.bullet_image, (self.rect.centerx + 10, self.rect.centery - 10),
                           10, 5, self.direction, 0, self.level.enemy_projectiles)
                self.hit_player = True
                # SFX['punch 1'].play()

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

        # debug_rect(self.game.layers[4], self.attack_rect, self.level.scroll)

        if self.attack_rect.colliderect(self.level.player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 4 and not self.hit_player:
                self.level.player.hp -= 20
                self.level.player.hurt = 1
                self.hit_player = True
                SFX['punch 1'].play()

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False
