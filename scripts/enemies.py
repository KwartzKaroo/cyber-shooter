import random
import pygame

from scripts.audio import DEATH_SFX, ATTACK_SFX, MISC_SFX
from scripts.entity import Entity
from scripts.globals import FPS
from scripts.projectile import ElectricBolt, Electric
from scripts.utils import Animation, Timer, load_image


class Enemy(Entity):
    def __init__(self, level, name, size, position, speed, hp, image_offset):
        super().__init__(level, size, position, speed, hp, level.enemies)

        self.actions = {'hurt': False, 'death': False, 'attack': False, 'walk': False, 'idle': True}
        self.animations = {
            'idle': Animation(f'assets/sprites/enemies/{name}/idle.png', 4, True),
            'walk': Animation(f'assets/sprites/enemies/{name}/walk.png', 8, True),
            'hurt': Animation(f'assets/sprites/enemies/{name}/hurt.png', 7, False),
            'death': Animation(f'assets/sprites/enemies/{name}/death.png', 6, False),
            'attack': Animation(f'assets/sprites/enemies/{name}/attack.png', 8, False),
        }
        self.current_action = 'idle'
        self.prev_action = 'idle'
        self.display_image = self.animations['idle'].get_image()
        self.image_offset = image_offset

        # AI
        self.stop_timer = Timer(random.randint(2000, 3500))
        self.stopped = False
        self.player_spotted = False
        self.vision = pygame.Rect(self.rect.x, self.rect.y, 120, 20)
        self.distance = random.randint(50, 200)
        self.distance_walked = 0
        self.edge_rect = pygame.Rect(self.rect.right, self.rect.bottom, 2, 2)
        self.wall_rect = pygame.Rect(self.rect.right, self.rect.top - 4, 2, 8)
        self.is_on_edge = False
        self.is_by_wall = False

        # Attacking
        self.attack_rect = pygame.Rect(self.position, (20, 20))
        self.hit_player = False

        # Health
        self.death_timer = Timer(5000)
        self.attack_sound = 'punch 1'
        self.take_damage_sound = 'human 1'
        self.death_sound = str(random.choice(['human 1', 'human 2', 'human 3']))

    def reset(self):
        self.velocity[0] = 0
        self.actions['walk'] = False
        self.is_on_edge = False
        self.is_by_wall = False

    def draw(self):
        position = self.image_position()
        self.level.canvases[5].blit(self.display_image, (position[0] - self.level.camera.x, position[1] - self.level.camera.y))

    def animate(self):
        # Flip
        if self.direction < 0:
            self.flip = True
        else:
            self.flip = False

        # Update action
        for action in self.actions:
            if self.actions[action]:
                self.current_action = action
                break

        # Keep track of animations
        if self.current_action != self.prev_action:
            self.animations[self.prev_action].reset()
            self.prev_action = self.current_action

        # Get image
        self.animations[self.current_action].update(self.level.game.delta)
        self.display_image = pygame.transform.flip(self.animations[self.current_action].get_image(), self.flip, False)

    def image_position(self):
        pos = list(self.position)

        pos[1] += self.image_offset[1]
        if self.flip:
            pos[0] += (self.rect.w - 48 - self.image_offset[0])
        else:
            pos[0] += self.image_offset[0]

        return pos

    def check_on_edge(self, tiles, ramps):
        if self.flip:
            self.edge_rect = pygame.Rect(self.rect.left - 2 - 10, self.rect.bottom, 2, 2)
            self.wall_rect = pygame.Rect(self.rect.left - 2 - 10, self.rect.top - 4, 2, 8)
            self.ramp_rect = pygame.Rect(self.rect.right - 2 - self.rect.w / 2, self.rect.bottom, self.rect.w / 2, 4)
        else:
            self.edge_rect = pygame.Rect(self.rect.right + 10, self.rect.bottom, 2, 2)
            self.wall_rect = pygame.Rect(self.rect.right + 10, self.rect.top - 4, 2, 8)
            self.ramp_rect = pygame.Rect(self.rect.left - 2, self.rect.bottom, self.rect.w / 2, 4)

        self.is_on_edge =  ((self.edge_rect.collidelist(tiles) == -1 and self.edge_rect.collidelist(ramps) == -1)
                            and self.ramp_rect.collidelist(ramps) == -1)
        self.is_by_wall = self.wall_rect.collidelist(tiles) > -1

    def roam(self):
        if self.health_depleted():
            self.velocity[0] = 0
            self.player_spotted = False
            return

        # Walk a certain distance before stopping
        if self.distance_walked < self.distance and not self.is_on_edge:
            self.actions['walk'] = True
            self.velocity[0] = self.speed * self.direction
            self.distance_walked += self.speed * self.level.game.delta * FPS
        else:
            self.actions['walk'] = False
            self.velocity[0] = 0
            self.stop_timer.activate()

        # Update timer if it is active. Continue walking when its over
        if self.stop_timer:
            self.stop_timer.update()
            if not self.stop_timer:
                self.stop_timer.set_duration(random.randint(2000, 6000))
                self.direction *= int(random.choices([1, -1], [0.2, 0.8])[0])
                self.distance_walked = 0

    def guard(self, player):
        if player.health_depleted():
            self.player_spotted = False
            return

        if self.is_by_wall:
            self.player_spotted = False
            return

        # Update the enemy's vision
        if self.flip:
            self.vision = pygame.Rect(self.rect.centerx - 180, self.rect.y, 180, 20)
        else:
            self.vision = pygame.Rect(self.rect.centerx, self.rect.y, 180, 20)

        # Once the enemy sees the player, the player has been spotted
        if self.vision.colliderect(player):
            self.player_spotted = True

        # When the player is spotted, the enemy can follow him
        if self.player_spotted:
            if self.rect.right < player.rect.left:
                if not self.is_on_edge:
                    self.velocity[0] = self.speed
                    self.actions['walk'] = True
                if not self.actions['attack']:
                    self.direction = 1
            elif self.rect.left > player.rect.right:
                if not self.is_on_edge:
                    self.velocity[0] = -self.speed
                    self.actions['walk'] = True
                if not self.actions['attack']:
                    self.direction = -1

    def attack(self, player):
        pass

    def update_health(self):
        for bullet in self.level.player_bullets:
            if bullet.rect.colliderect(self.rect) and not self.health_depleted():
                if isinstance(bullet, Electric):
                    bullet.hit_entity = True
                    self.hp -= bullet.damage / FPS
                elif bullet not in self.bullets_touched:
                    self.bullets_touched.append(bullet)
                    self.hp -= bullet.damage
                    x, y = bullet.knockback_force
                    self.knockback(x, y)
                if not self.actions['hurt']:
                    self.actions['hurt'] = True
                bullet.hit_entity = True
                self.player_spotted = True

        for bullet in self.bullets_touched:
            if not bullet.alive():
                self.bullets_touched.remove(bullet)

        if self.actions['hurt']:
            self.velocity[0] = 0
            if self.animations['hurt'].finished:
                self.actions['hurt'] = False

    def on_death(self):
        if self.health_depleted():
            self.player_spotted = False
            self.velocity[0] = 0
            if not self.actions['death']:
                DEATH_SFX[self.death_sound].play()
                # ATTACK_SFX[self.attack_sound].stop()
            self.actions['death'] = True
            self.death_timer.activate()
            self.death_timer.update()
            if not self.death_timer:
                self.kill()

    def draw_health_bar(self, surface, scroll):
        pygame.draw.rect(surface, 'red', (self.rect.centerx - 10 - scroll[0], self.rect.y - scroll[1] - 10, 20, 3))

        scale = self.init_hp // 20
        pygame.draw.rect(surface, 'green', (self.rect.centerx - 10 - scroll[0], self.rect.y - scroll[1] - 10, self.hp / scale, 3))

    def update(self):
        tiles = self.level.tilemap.get_tiles_around('tiles', self.rect)
        ramps = self.level.tilemap.get_tiles_around('ramps', self.rect)
        player = self.level.player

        self.reset()
        self.check_on_edge(tiles, ramps)
        self.apply_gravity()

        if not self.player_spotted:
            self.roam()

        self.guard(player)
        if self.offscreen():
            self.player_spotted = False
        self.attack(player)

        self.update_health()
        self.on_death()

        self.tile_collisions(tiles)
        self.ramp_collisions(ramps)
        self.update_position()

        self.animate()
        self.draw()


class Batsman(Enemy):
    def __init__(self, level, pos):
        super().__init__(level, '01 batsman', (16, 32), pos, 1.5, 30, (-4, -16))
        self.image_offset = (-4, -16)

        self.attack_sound = str(random.choice(['metal hit 1', 'metal hit 2']))
        self.death_sound = str(random.choice(['human 1', 'human 2', 'human 3']))

    def attack(self, player):
        if player.health_depleted():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.health_depleted():
            if self.player_spotted:
                ATTACK_SFX[self.attack_sound].stop()
                self.player_spotted = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 28, self.rect.y, 28, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 28, 16)

        if self.attack_rect.colliderect(player) and not self.actions['attack']:
            self.actions['attack'] = True

        if self.actions['attack']:
            self.velocity[0] = 0
            if self.animations['attack'].get_frame() == 4 and not self.hit_player and self.attack_rect.colliderect(player):
                ATTACK_SFX[self.attack_sound].play()
                player.take_melee_damage(10)
                player.knockback(2 * self.direction)
                self.hit_player = True

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class Pistolerro(Enemy):
    def __init__(self, level, pos):
        super().__init__(level, '02 pistolerro', (17, 40), pos, 1.5, 30, (-6, -8))

        self.attack_sound = 'gun shot'
        self.death_sound = str(random.choice(['human 1', 'human 2', 'human 3']))
        self.shot = False

    def attack(self, player):
        if player.health_depleted():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.health_depleted():
            if self.player_spotted:
                ATTACK_SFX[self.attack_sound].stop()
                self.player_spotted = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 36, self.rect.y, 36, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 36, 16)

        if self.attack_rect.colliderect(player):
            self.actions['attack'] = True

        if self.actions['attack']:
            self.velocity[0] = 0
            frame = self.animations['attack'].get_frame()

            # Play a gun shot sound
            if frame == 0 or frame == 3:
                if not self.shot:
                    ATTACK_SFX[self.attack_sound].play()
                    self.shot = True
            else:
                self.shot = False

            if frame == 2 or frame == 5:
                if not self.hit_player and (player.rect.centerx - self.rect.centerx) * self.direction > 0:
                    player.take_melee_damage(5)
                    player.knockback(2 * self.direction)
                    self.hit_player = True
            else:
                self.hit_player = False

        if self.actions['attack']:
            self.velocity[0] = 0

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class GroundDrone(Enemy):
    def __init__(self, level, pos):
        super().__init__(level, '03 drone', (20, 24), pos, 1.5, 40, (-6, -24))

        self.death_sound = 'robot 4'

    def attack(self, player):
        if player.health_depleted():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.health_depleted():
            return

        self.attack_rect = pygame.Rect(self.rect.x - 3, self.rect.y, self.rect.w + 6, self.rect.h)

        if self.attack_rect.colliderect(player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            player.take_melee_damage(self.level.game.delta * 5)
            if not self.hit_player:
                self.hit_player = True
        else:
            self.actions['attack'] = False

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class CyberHound(Enemy):
    def __init__(self, level, pos):
        super().__init__(level, '04 cyber hound', (37, 21), pos, 2.5, 70, (-5, -27))

        self.distance = random.randint(350, 500)
        self.attack_sound = 'bite'
        self.death_sound = 'robot 2'

        self.bit = False

    def attack(self, player):
        if int(self.distance_walked) % 150 == 0 and self.actions['walk']:
            self.direction *= -1

        if player.health_depleted():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.health_depleted():
            if self.player_spotted:
                ATTACK_SFX[self.attack_sound].stop()
                self.player_spotted = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 22, self.rect.y, 22, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 22, 16)

        if self.attack_rect.colliderect(player):
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 4 and not self.hit_player:
                player.take_melee_damage(10)
                self.hit_player = True

        if self.actions['attack']:
            if not self.bit and self.animations['attack'].get_frame() == 0:
                ATTACK_SFX[self.attack_sound].play()
                self.bit = True

            self.velocity[0] = 0

        if self.animations['attack'].finished:
            self.hit_player = False
            self.bit = False
            self.actions['attack'] = False


class DockWorker(Enemy):
    def __init__(self, level, pos):
        super().__init__(level, '05 dock worker',(17, 35), pos, 1.5, 20, (-15, -13))

        self.attack_sound = 'punch 1'
        self.can_play_attack_sound = False
        self.death_sound = str(random.choice(['human 1', 'human 2', 'human 3']))

    def attack(self, player):
        if player.health_depleted():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.health_depleted():
            if self.player_spotted:
                ATTACK_SFX[self.attack_sound].stop()
                self.player_spotted = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 20, self.rect.y, 20, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 20, 16)

        if self.attack_rect.colliderect(player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 4 and not self.hit_player:
                player.take_melee_damage(10)
                # player.knockback(3 * self.direction)
                self.hit_player = True

        if self.actions['attack']:
            self.velocity[0] = 0
            if not self.can_play_attack_sound and self.animations['attack'].get_frame() == 3:
                ATTACK_SFX[self.attack_sound].play()
                self.can_play_attack_sound = True

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False
            self.can_play_attack_sound = False


class ExplosiveBot(Enemy):
    def __init__(self, level, pos):
        super().__init__(level, '06 explosive bot', (34, 28), pos, 1.5, 50, (-6, -20))
        self.warnings = 0
        self.explosion = Animation('assets/sprites/misc/explosion2.png', 9, False, (128, 80))
        self.attack_sound = MISC_SFX['explosion 1']
        self.death_sound = 'robot 3'
        self.play_explosion_sound = False

    def draw(self):
        position = self.image_position()
        if self.warnings < 3:
            self.level.canvases[5].blit(self.display_image,
                                        (position[0] - self.level.camera.x, position[1] - self.level.camera.y))
        else:
            self.level.canvases[5].blit(
                self.explosion.get_image(),
                (self.attack_rect.centerx - self.level.camera.x - 64, self.attack_rect.y - self.level.camera.y)
            )

    def attack(self, player):
        if self.health_depleted():
            return

        if self.health_depleted():
            if self.player_spotted:
                ATTACK_SFX[self.attack_sound].stop()
                self.player_spotted = False
            return

        # Change attack rect
        self.attack_rect = pygame.Rect(self.rect.centerx - 40, self.rect.y - 20, 80, 40)
        if self.attack_rect.colliderect(player) and self.warnings < 3:
            self.actions['attack'] = True

        if self.actions['attack']:
            if self.animations['attack'].get_frame() == 2 and not self.hit_player:
                self.warnings += 1
                ATTACK_SFX['warning beep'].play()
                self.hit_player = True
            self.velocity[0] = 0

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False

        if self.warnings >= 3:
            self.hp = 1_000_000
            self.velocity[0] = 0
            self.explosion.update(self.level.game.delta)
            self.attack_rect = pygame.Rect(self.rect.centerx - 64, self.rect.bottom - 80, 128, 80)
            if not self.play_explosion_sound:
                MISC_SFX['explosion 1'].play()
                self.play_explosion_sound = True

            if self.attack_rect.colliderect(player) and not self.hit_player and self.explosion.get_frame() < 6:
                player.take_melee_damage(25)
                player.knockback(5 * self.direction, -5, 2)
                self.hit_player = True

        if self.explosion.finished:
            self.kill()

    def update_health(self):
        for bullet in self.level.player_bullets:
            if bullet.rect.colliderect(self.rect) and not self.health_depleted():
                if isinstance(bullet, Electric):
                    bullet.hit_entity = True
                    self.hp -= bullet.damage / FPS
                elif bullet not in self.bullets_touched:
                    self.bullets_touched.append(bullet)
                    self.hp -= bullet.damage
                    x, y = bullet.knockback_force
                    self.knockback(x, y)
                bullet.hit_entity = True
                self.player_spotted = True

        for bullet in self.bullets_touched:
            if not bullet.alive():
                self.bullets_touched.remove(bullet)


class Zapper(Enemy):
    def __init__(self, level, pos):
        super().__init__(level, '07 zapper',(19, 35), pos, 1.5, 50, (-13, -13))

        self.actions = {'hurt': False, 'resurrect': False, 'death': False, 'attack': False, 'walk': False, 'idle': True}
        self.animations = {
            'idle': Animation(f'assets/sprites/enemies/07 zapper/idle.png', 4, True),
            'walk': Animation(f'assets/sprites/enemies/07 zapper/walk.png', 8, True),
            'hurt': Animation(f'assets/sprites/enemies/07 zapper/hurt.png', 7, False),
            'death': Animation(f'assets/sprites/enemies/07 zapper/death.png', 6, False),
            'resurrect': Animation(f'assets/sprites/enemies/07 zapper/death.png', 6, False),
            'attack': Animation(f'assets/sprites/enemies/07 zapper/attack.png', 8, False),
        }

        self.animations['resurrect'].images = list(reversed(self.animations['death'].images))

        self.resurrect = False
        self.death_timer = Timer(1300)

        self.bolt_images = {
            1: load_image('assets/sprites/enemies/07 zapper/projectile1.png'),
            2: load_image('assets/sprites/enemies/07 zapper/projectile2.png')
        }

        self.death_sound = 'unique'

    def attack(self, player):
        if player.health_depleted():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 128, self.rect.y - 55, 128, 16 + 55)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y - 55, 128, 16 + 55)

        if self.attack_rect.colliderect(player):
            self.actions['attack'] = True

        if self.actions['attack']:
            self.velocity[0] = 0
            if self.animations['attack'].get_frame() == 5 and not self.hit_player:
                if self.flip:
                    bolt_pos = (self.rect.x - 48 + self.rect.w, self.rect.y)
                else:
                    bolt_pos = (self.rect.x + 18, self.rect.y)
                MISC_SFX['electric shock'].play()
                ElectricBolt(self.level, self.bolt_images[1], bolt_pos, 10, 7, self.direction, 0, self.level.enemy_projectiles)
                self.hit_player = True

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False

    def on_death(self):
        if self.actions['resurrect']:
            self.velocity[0] = 0
            if self.animations['resurrect'].finished:
                self.hp = 30
                self.actions['death'] = False
                self.actions['hurt'] = False
                self.actions['resurrect'] = False
            return

        if self.health_depleted():
            self.player_spotted = False
            self.velocity[0] = 0
            if not self.actions['death']:
                DEATH_SFX[self.death_sound].play()
            self.actions['death'] = True
            self.death_timer.activate()
            self.death_timer.update()
            if not self.death_timer:
                if bool(random.choice([0, 1])):
                    self.actions['resurrect'] = True
                else:
                    self.kill()


class Demoness(Enemy):
    def __init__(self, level, pos):
        super().__init__(level, '08 demoness', (18, 35), pos, 2.0, 100, (-7, -13))

        self.attack_sound = 'punch 3'
        self.death_sound = str(random.choice(['demoness 1', 'demoness 2']))

    def attack(self, player):
        if player.health_depleted():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 18, self.rect.y, 18, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 18, 16)

        if self.attack_rect.colliderect(player):
            self.velocity[0] = 0
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 3 and not self.hit_player:
                ATTACK_SFX[self.attack_sound].play()
                self.hit_player = True
                player.knockback(4.5 * self.direction, -3.5, 2)
                player.take_melee_damage(10)

        if self.actions['attack']:
            self.velocity[0] = 0

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False


class Zombie(Enemy):
    def __init__(self, level, pos):
        super().__init__(level, '09 zombie', (17, 35), pos, 0.8, 200, (-3, -13))

        self.attack_sound = 'punch 3'
        self.death_sound = str(random.choice(['zombie 1', 'zombie 2']))

    def attack(self, player):
        if player.health_depleted():
            self.hit_player = False
            self.actions['attack'] = False
            return

        if self.flip:
            self.attack_rect = pygame.Rect(self.rect.centerx - 18, self.rect.y, 18, 16)
        else:
            self.attack_rect = pygame.Rect(self.rect.centerx, self.rect.y, 18, 16)

        if self.attack_rect.colliderect(player):
            self.actions['attack'] = True
            if self.animations['attack'].get_frame() == 3 and not self.hit_player:
                self.hit_player = True
                player.knockback((5 * self.direction, -1.5), 2)
                player.take_melee_damage(10)
                ATTACK_SFX[self.attack_sound].play()

        if self.actions['attack']:
            self.velocity[0] = 0

        if self.animations['attack'].finished:
            self.hit_player = False
            self.actions['attack'] = False
