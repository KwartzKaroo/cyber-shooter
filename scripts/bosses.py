import pygame
import random
from scripts.entity import Entity
from scripts.utils import Animation, Timer, load_image
from scripts.globals import FPS
from scripts.projectile import RugbyBall, Missile, Normal, ThrownProjectile, Electric
from scripts.enemies import Demoness
from scripts.audio import ATTACK_SFX, DEATH_SFX, MISC_SFX


class Boss(Entity):
    def __init__(self, level, name, size, position, speed, hp, image_offset, image_size=(72, 72)):
        super().__init__(level, size, position, speed, hp)
        # Display image
        self.name = name
        self.actions = {'hurt': False, 'death': False, 'walk': False, 'idle': True}
        self.animations = {
            'idle': Animation(f'assets/sprites/bosses/{name}/idle.png', 4, True, image_size),
            'walk': Animation(f'assets/sprites/bosses/{name}/walk.png', 8, True, image_size),
            'death': Animation(f'assets/sprites/bosses/{name}/death.png', 6, False, image_size),
            'hurt': Animation(f'assets/sprites/bosses/{name}/hurt.png', 9, False, image_size),
        }
        self.display_image = self.animations['idle'].get_image()
        self.current_action = 'idle'
        self.prev_action = 'idle'
        self.image_offset = image_offset
        self.image_size = image_size

        # AI
        self.selected_attack = 1
        self.attack_cooldown = Timer(1000)
        self.player_spotted = False
        self.visions = {}
        self.hit_player = False
        self.attack_rect = pygame.Rect(self.position, (20, 20))
        self.celebrate = False

        # Health
        self.death_timer = Timer(5000)
        self.death_sound = 'human 1'

    def reset(self):
        self.velocity[0] = 0
        self.actions['walk'] = False

    def draw(self):
        position = self.image_position()
        self.draw_health_bar(self.level.canvases[5], self.level.camera)
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
        image = self.animations[self.current_action].get_image().copy()

        # When hurt
        if self.hurt > 0:
            mask = pygame.mask.from_surface(image)
            mask_image = mask.to_surface()
            mask_image.set_colorkey((0, 0, 0))

            for w in range(mask_image.get_width()):
                for h in range(mask_image.get_height()):
                    if mask_image.get_at((w, h))[0] != 0:
                        mask_image.set_at((w, h), '#ed590e')
                    else:
                        mask_image.set_at((w, h), (0, 0, 0))
            mask_image.set_alpha(160)
            image.blit(mask_image, (0, 0))
        self.display_image = pygame.transform.flip(image, self.flip, False)

    def image_position(self):
        position = list(self.position)

        position[1] += self.image_offset[1]
        if self.flip:
            position[0] += (self.rect.w - self.image_size[0] - self.image_offset[0])
        else:
            position[0] += self.image_offset[0]

        return position

    def update_vision(self):
        pass

    def set_cooldown_timer(self, duration):
        self.attack_cooldown = Timer(duration)
        self.attack_cooldown.activate()

    def guard(self, player):
        if self.attack_cooldown:
            return

        if self.health_depleted():
            return

        if abs(self.rect.centerx - player.rect.centerx) <= 256:
            self.player_spotted = True

        if self.rect.right < player.rect.left:
            self.direction = 1
            if not player.health_depleted():
                self.actions['walk'] = True
                self.velocity[0] = self.speed * 0.7
        elif self.rect.left > player.rect.right:
            self.direction = -1
            if not player.health_depleted():
                self.actions['walk'] = True
                self.velocity[0] = -self.speed * 0.7

    def choose_attack(self, player):
        pass

    def handle_attacks(self, player):
        pass

    def special(self, player):
        pass

    def update_health(self):
        # Kill zone boundaries
        for tile in self.level.tilemap.get_tiles_around('boundaries', self.rect):
            if self.rect.colliderect(tile):
                self.hp = 0

        for bullet in self.level.player_bullets:
            if bullet.rect.colliderect(self.rect) and not self.health_depleted():
                if bullet.rect.colliderect(self.rect):
                    if isinstance(bullet, Electric):
                        bullet.hit_entity = True
                        self.hp -= bullet.damage / FPS
                    elif bullet not in self.bullets_touched:
                        self.bullets_touched.append(bullet)
                        self.hp -= bullet.damage
                    bullet.hit_entity = True
                    self.hurt = 1

        # When hurt
        if self.hurt > 0:
            self.hurt += 1
            if self.hurt > 20:
                self.hurt = 0

    def on_death(self):
        if self.health_depleted():
            self.velocity[0] = 0
            if not self.actions['death']:
                self.level.player.start_emote('happy')
                DEATH_SFX[self.death_sound].play()
            self.actions['death'] = True
            self.death_timer.activate()
            self.death_timer.update()
            if not self.death_timer:
                self.dead = True

    def draw_health_bar(self, surface, scroll):
        pygame.draw.rect(surface, 'red', (self.rect.centerx - 10 - scroll[0], self.rect.y - scroll[1] - 10, 20, 3))
        scale = self.init_hp / 20
        pygame.draw.rect(surface, 'green', (self.rect.centerx - 10 - scroll[0], self.rect.y - scroll[1] - 10, self.hp / scale, 3))

    def update(self):
        if not self.level.camera.on_screen(self, 128):
            return

        tiles = self.level.tilemap.get_tiles_around('tiles', self.rect)
        ramps = self.level.tilemap.get_tiles_around('ramps', self.rect)
        player = self.level.player

        self.reset()
        self.apply_gravity()
        self.update_vision()
        self.guard(player)
        if self.player_spotted:
            self.choose_attack(player)
            if not self.health_depleted():
                self.handle_attacks(player)
        self.update_health()
        self.on_death()

        self.tile_collisions(tiles)
        self.ramp_collisions(ramps)
        self.update_position()
        self.boss_fight_bounds()

        self.animate()
        self.draw()


class SportsMan(Boss):
    def __init__(self, level, position):
        super().__init__(level, '1 sportsman', (25, 44), position, 1.8, 800, (-14, -28), (72, 72))

        self.actions = {
            'death': False, 'sneer': False,
            'attack1': False, 'attack2': False, 'attack3': False, 'attack4': False,
            'walk': False, 'idle': True
        }
        self.animations = {
            'idle': Animation(f'assets/sprites/bosses/{self.name}/idle.png', 4, True, self.image_size),
            'walk': Animation(f'assets/sprites/bosses/{self.name}/walk.png', 7, True, self.image_size),
            'sneer': Animation(f'assets/sprites/bosses/{self.name}/sneer.png', 7, False, self.image_size),
            'hurt': Animation(f'assets/sprites/bosses/{self.name}/hurt.png', 3, False, self.image_size),
            'death': Animation(f'assets/sprites/bosses/{self.name}/death.png', 6, False, self.image_size),
            'attack1': Animation(f'assets/sprites/bosses/{self.name}/attack1.png', 9, False, self.image_size),
            'attack2': Animation(f'assets/sprites/bosses/{self.name}/attack2.png', 9, False, self.image_size),
            'attack3': Animation(f'assets/sprites/bosses/{self.name}/attack3.png', 9, False, self.image_size),
            'attack4': Animation(f'assets/sprites/bosses/{self.name}/attack4.png', 8, True, self.image_size),
        }

        self.attack = {
            'direction': 1,
            'timer': Timer(1600),
        }
        self.selected_attack = 4
        self.ball_image = load_image('assets/sprites/bosses/1 sportsman/ball.png')

        self.death_sound = 'human 5'

    def update_vision(self):
        self.visions = {
            'attack1': pygame.Rect(self.rect.centerx - 28 * bool(self.direction - 1), self.rect.y, 28, 16),
            'attack2': pygame.Rect(self.rect.centerx - 28 * bool(self.direction - 1), self.rect.y, 28, 20),
            'attack3': pygame.Rect(self.rect.centerx - 216 * bool(self.direction - 1), self.rect.y, 216, 20),
            'attack4': pygame.Rect(self.rect.centerx - 160 * bool(self.direction - 1), self.rect.y, 160, self.rect.h),
        }

    def choose_attack(self, player):
        if self.attack_cooldown:
            self.velocity[0] = 0
            self.actions['walk'] = False
            self.attack_cooldown.update()
            return

        if self.actions['sneer']:
            self.velocity[0] = 0
            if self.animations['sneer'].finished:
                self.actions['sneer'] = False
            return

        # Don't switch attacks when attacking
        if self.actions['attack1'] or self.actions['attack3'] or self.actions['attack2'] or self.actions['attack4']:
            return

        if player.health_depleted():
            self.actions['sneer'] = True
            return

        if self.selected_attack == 1:
            if self.visions['attack1'].colliderect(player):
                self.actions['attack1'] = True
        if self.selected_attack == 2:
            if self.visions['attack2'].colliderect(player):
                self.actions['attack2'] = True
        if self.selected_attack == 3:
            if self.visions['attack3'].colliderect(player):
                self.actions['attack3'] = True
        if self.selected_attack == 4:
            if self.visions['attack4'].colliderect(player):
                self.attack['timer'].activate()
                self.attack['direction'] = self.direction
                self.actions['attack4'] = True
            else:
                self.selected_attack = random.randint(2, 3)

    def handle_attacks(self, player):
        if self.actions['attack1']:
            self.attack1(player)
        elif self.actions['attack2']:
            self.attack2(player)
        elif self.actions['attack3']:
            self.attack3()
        elif self.actions['attack4']:
            self.attack4(player)

    def attack1(self, player):
        if self.animations['attack1'].get_frame() == 4 and not self.hit_player:
            if self.visions['attack1'].colliderect(player):
                self.hit_player = True
                player.take_melee_damage(10)
                player.knockback(4 * self.direction)
                ATTACK_SFX['punch 3'].play()

        self.velocity[0] = 0

        if self.animations['attack1'].finished:
            self.hit_player = False
            self.actions['attack1'] = False
            self.selected_attack = random.randint(1, 2)

    def attack2(self, player):
        if self.animations['attack2'].get_frame() == 4 and not self.hit_player:
            if self.visions['attack2'].colliderect(player):
                self.hit_player = True
                # self.level.freeze_frame(300)
                self.level.camera.shake_screen(200, 4)
                player.take_melee_damage(10)
                player.knockback(4 * self.direction, -2.5, 2)
                ATTACK_SFX['punch 2'].play()

        self.velocity[0] = 0

        if self.animations['attack2'].finished:
            self.hit_player = False
            self.actions['attack2'] = False
            self.set_cooldown_timer(random.randint(400, 800))
            self.selected_attack = random.randint(1, 4)

    def attack3(self):
        self.velocity[0] = 0

        if self.animations['attack3'].finished:
            self.hit_player = False
            self.actions['attack3'] = False
            self.set_cooldown_timer(1200)
            self.selected_attack = random.randint(1, 4)

        if self.animations['attack3'].get_frame() == 4 and not self.hit_player:
            self.hit_player = True
            if self.flip:
                position = (self.rect.left - 12, self.rect.y + 21)
            else:
                position = (self.rect.right + 2, self.rect.y + 21)
            RugbyBall(self.level, self.ball_image, position, self.direction, self.level.enemy_projectiles)

    def attack4(self, player):
        if self.attack['timer']:
            self.attack['timer'].update()
            self.velocity[0] = self.attack['direction'] * 3
            self.direction = self.attack['direction']
            if not self.attack['timer']:
                self.actions['attack4'] = False
                self.attack['direction'] = 0
                self.attack_cooldown.activate()
                return

        # Stop when boss runs into the player
        if self.rect.colliderect(player) and self.velocity[1] >= 0:
            player.take_melee_damage(10)
            player.knockback(7 * self.direction)
            self.actions['attack4'] = False
            self.set_cooldown_timer(random.randint(1000, 2000))
            return


class Tank(Boss):
    def __init__(self, level, position):
        super().__init__(level, '2 tank', (63, 52), position, 0.9, 3000, (-4, -20), (72, 72))

        self.actions = {
            'hurt': False, 'death': False, 'sneer': False,
            'attack1': False, 'attack2': True, 'attack3': False, 'attack4': False,
            'walk': False, 'idle': True
        }
        self.animations = {
            'idle': Animation(f'assets/sprites/bosses/{self.name}/idle.png', 4, True, self.image_size),
            'walk': Animation(f'assets/sprites/bosses/{self.name}/walk.png', 7, True, self.image_size),
            'hurt': Animation(f'assets/sprites/bosses/{self.name}/hurt.png', 3, False, self.image_size),
            'death': Animation(f'assets/sprites/bosses/{self.name}/death.png', 6, False, self.image_size),
            'sneer': Animation(f'assets/sprites/bosses/{self.name}/sneer.png', 6, False, self.image_size),
            'attack1': Animation(f'assets/sprites/bosses/{self.name}/attack1.png', 6, False, self.image_size),
            'attack2': Animation(f'assets/sprites/bosses/{self.name}/attack2.png', 6, False, self.image_size),
            'attack3': Animation(f'assets/sprites/bosses/{self.name}/attack3.png', 7, False, self.image_size),
            'attack4': Animation(f'assets/sprites/bosses/{self.name}/attack4.png', 6, False, self.image_size),
        }

        self.attack = {
            'direction': 1,
            'timer': Timer(1600),
            'velocity': 0,
            'frame': 0
        }

        self.selected_attack = 4
        self.beam_image = load_image('assets/sprites/bosses/2 tank/beam.png')
        self.missile_image = load_image('assets/sprites/bosses/2 tank/missile.png')
        self.death_sound = 'robot 3'

    def update_vision(self):
        self.visions = {
            'attack1': pygame.Rect(self.rect.centerx - 160 * bool(self.direction - 1), self.rect.y - 60, 160, 126),
            'attack2': pygame.Rect(self.rect.centerx - 384 * bool(self.direction - 1), self.rect.y - 60, 384, 126),
            'attack3': pygame.Rect(self.rect.centerx - 192 * bool(self.direction - 1), self.rect.y, 160, 20),
            'attack4': pygame.Rect(self.rect.centerx - 160 * bool(self.direction - 1), self.rect.y, 160, self.rect.h),
        }

    def choose_attack(self, player):
        if self.attack_cooldown:
            self.velocity[0] = 0
            self.actions['walk'] = False
            self.attack_cooldown.update()
            return

        if self.selected_attack == 1:
            if self.visions['attack1'].colliderect(player):
                self.actions['attack1'] = True
                self.attack['direction'] = self.direction
        if self.selected_attack == 2:
            if self.visions['attack2'].colliderect(player):
                self.attack['direction'] = self.direction
                self.actions['attack2'] = True
        if self.selected_attack == 3:
            if self.visions['attack3'].colliderect(player):
                self.actions['attack3'] = True
            else:
                self.selected_attack = 4
        if self.selected_attack == 4:
            if self.visions['attack4'].colliderect(player):
                self.actions['attack4'] = True

    def handle_attacks(self, player):
        self.attack_rect = self.rect

        if self.health_depleted():
            return

        if self.actions['attack1']:
            self.attack1(player)
        elif self.actions['attack2']:
            self.attack2(player)
        elif self.actions['attack3']:
            self.attack3()
        elif self.actions['attack4']:
            self.attack4(player)

    def attack1(self, player):
        frame = self.animations['attack1'].get_frame()
        self.velocity[0] = 0

        speed = abs(self.position[0] - player.rect.centerx) / FPS * 1.25
        image = pygame.transform.flip(self.missile_image, self.flip, False)

        if frame == 1 and not self.hit_player:
            pos = (self.rect.x + 5 + 20, self.rect.top -3 + 2 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame
        elif frame == 2 and not self.hit_player:
            pos = (self.rect.x + 5 + 21, self.rect.top -3 + 7 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame
        elif frame == 3 and not self.hit_player:
            pos = (self.rect.x + 5 + 25, self.rect.top -3 + 2 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame
        elif frame == 4 and not self.hit_player:
            pos = (self.rect.x + 5 + 26, self.rect.top -3 + 7 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame
        elif frame == 5 and not self.hit_player:
            pos = (self.rect.x + 5 + 27, self.rect.top -3 + 2 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame
        elif frame == 6 and not self.hit_player:
            pos = (self.rect.x + 5 + 28, self.rect.top -3 + 7 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame

        if frame != self.attack['frame']:
            self.hit_player = False

        if self.animations['attack1'].finished:
            self.hit_player = False
            self.actions['attack1'] = False
            self.set_cooldown_timer(1600)
            self.selected_attack = random.randint(1, 4)
            return

    def attack2(self, player):
        frame = self.animations['attack2'].get_frame()
        speed = abs(self.position[0] - player.rect.centerx) / FPS * 1.25
        image = pygame.transform.flip(self.missile_image, self.flip, False)

        if frame == 1 and not self.hit_player:
            pos = (self.rect.x + 5 + 20, self.rect.top - 3 + 2 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame
        elif frame == 2 and not self.hit_player:
            pos = (self.rect.x + 5 + 21, self.rect.top - 3 + 7 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame
        elif frame == 3 and not self.hit_player:
            pos = (self.rect.x + 5 + 25, self.rect.top - 3 + 2 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame
        elif frame == 4 and not self.hit_player:
            pos = (self.rect.x + 5 + 26, self.rect.top - 3 + 7 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame
        elif frame == 5 and not self.hit_player:
            pos = (self.rect.x + 5 + 27, self.rect.top - 3 + 2 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame
        elif frame == 6 and not self.hit_player:
            pos = (self.rect.x + 5 + 28, self.rect.top - 3 + 7 - 1)
            Missile(self.level, image, pos, 10, speed, self.direction, -2.55, self.level.enemy_projectiles)
            self.hit_player = True
            self.attack['frame'] = frame

        if frame != self.attack['frame']:
            self.hit_player = False

        if self.animations['attack2'].finished:
            self.hit_player = False
            self.velocity[0] = 0
            self.selected_attack = random.randint(1, 4)
            self.set_cooldown_timer(2100)
            self.actions['attack2'] = False
            return

    def attack3(self):
        self.velocity[0] = 0
        frame = self.animations['attack3'].get_frame()
        if frame == 2 and not self.hit_player:
            self.hit_player = True
            position = (self.rect.x + (63 - 18), self.rect.y + 40)
            ATTACK_SFX['laser shot'].play()
            Normal(self.level, self.beam_image, position, 10, 6, self.direction, 0, self.level.enemy_projectiles)

        if self.animations['attack3'].finished:
            self.hit_player = False
            self.velocity[0] = 0
            self.actions['attack3'] = False

    def attack4(self, player):
        if self.animations['attack4'].finished:
            self.hit_player = False
            self.velocity[0] = 0
            self.actions['attack4'] = False
            ATTACK_SFX['smash down'].play()
            self.selected_attack = random.randint(1, 4)
            return

        if self.rect.collidelist(self.level.tilemap.get_tiles_around('tiles', self.rect)) and self.jump_count > 0 and self.velocity.y > 3:
            ATTACK_SFX['smash down'].play()
            self.level.camera.shake_screen(200, 8)
            self.jump_count = 0

        if self.jump_count == 0 and self.animations['attack4'].get_frame() == 0:
            ATTACK_SFX['thrust up'].play()
            self.attack['velocity'] = abs(self.rect.centerx - player.rect.centerx) / FPS * self.direction
            self.velocity[1] = -4
            self.jump_count = 1

        self.velocity[0] = self.attack['velocity']

        if self.animations['attack4'].get_frame() == 5:
            self.velocity[0] = 0

        if self.attack_rect.colliderect(player) and not self.hit_player and self.velocity[1] > 0:
            self.hit_player = True
            player.take_melee_damage(10)
            player.knockback(7 * self.direction)


class Mech(Boss):
    def __init__(self, level, position):
        super().__init__(level, '3 mech', (31, 49), position, 1.6, 2000, (-12, -47), (96, 96))

        self.actions = {
            'hurt': False, 'death': False, 'special': False,
            'attack1': False, 'attack2': False, 'attack3': False, 'attack4': False,
            'walk': False, 'idle': True
        }
        self.animations = {
            'idle': Animation(f'assets/sprites/bosses/{self.name}/idle.png', 4, True, self.image_size),
            'walk': Animation(f'assets/sprites/bosses/{self.name}/walk.png', 7, True, self.image_size),
            'hurt': Animation(f'assets/sprites/bosses/{self.name}/hurt.png', 3, False, self.image_size),
            'death': Animation(f'assets/sprites/bosses/{self.name}/death.png', 6, False, self.image_size),
            'special': Animation(f'assets/sprites/bosses/{self.name}/special.png', 6, False, self.image_size),
            'attack1': Animation(f'assets/sprites/bosses/{self.name}/attack1.png', 7, False, self.image_size),
            'attack2': Animation(f'assets/sprites/bosses/{self.name}/attack2.png', 6, False, self.image_size),
            'attack3': Animation(f'assets/sprites/bosses/{self.name}/attack3.png', 7, False, self.image_size),
            'attack4': Animation(f'assets/sprites/bosses/{self.name}/attack4.png', 8, False, self.image_size),
        }

        self.random_direction = 1
        self.regenerate = False
        self.selected_attack = 1
        self.energy_ball = load_image('assets/sprites/bosses/3 mech/projectile.png')
        self.death_sound = 'robot 5'

    def update_vision(self):
        self.visions = {
            'attack1': pygame.Rect(self.rect.centerx - 160 * bool(self.direction - 1), self.rect.y, 160, 20),
            'attack2': pygame.Rect(self.rect.centerx - 256 * bool(self.direction - 1), self.rect.y, 256, 20),
            'attack3': pygame.Rect(self.rect.centerx - 28 * bool(self.direction - 1), self.rect.y, 28, 20),
            'attack4': pygame.Rect(self.rect.centerx - 28 * bool(self.direction - 1), self.rect.y, 28, 20),
        }

    def choose_attack(self, player):
        if self.attack_cooldown:
            self.velocity[0] = 0
            self.actions['walk'] = False
            self.attack_cooldown.update()
            return

        # Can regenerate once when hp is low enough
        if self.hp <= self.init_hp / 3 and not self.regenerate:
            self.actions['special'] = True

        if self.actions['special'] and not self.regenerate:
            self.hp = min(self.hp + self.level.game.delta * FPS * 5, self.init_hp)
            if self.animations['special'].finished:
                self.actions['special'] = False
                self.regenerate = True
                self.set_cooldown_timer(1000)

        if self.actions['special']:
            self.velocity[0] = 0
            if self.animations['special'].finished:
                self.actions['special'] = False
            return


        # Don't switch attacks when attacking
        if self.actions['attack1'] or self.actions['attack3'] or self.actions['attack2'] or self.actions['attack4']:
            return

        if self.selected_attack == 1:
            if self.visions['attack1'].colliderect(player):
                self.actions['attack1'] = True
        if self.selected_attack == 2:
            if self.visions['attack2'].colliderect(player):
                self.actions['attack2'] = True
                self.random_direction = int(random.choice((-1, 1)))
        if self.selected_attack == 3:
            if self.visions['attack3'].colliderect(player):
                self.actions['attack3'] = True
        if self.selected_attack == 4:
            if self.visions['attack4'].colliderect(player):
                self.actions['attack4'] = True

    def handle_attacks(self, player):
        self.attack_rect = self.rect

        if self.actions['attack1']:
            self.attack1()
        elif self.actions['attack2']:
            self.attack2()
        elif self.actions['attack3']:
            self.attack3(player)
        elif self.actions['attack4']:
            self.attack4(player)

    def attack1(self):
        self.velocity[0] = 0

        if self.animations['attack1'].get_frame() == 4 and not self.hit_player:
            self.hit_player = True
            if self.flip:
                position = (self.rect.x + self.rect.w - 40 - 13, self.rect.y + 8)
            else:
                position = (self.rect.x + 40, self.rect.y + 8)
            ATTACK_SFX['laser shot 2'].play()
            Normal(self.level, self.energy_ball, position, 10, 7, self.direction, 0, self.level.enemy_projectiles)

        if self.animations['attack1'].finished:
            self.hit_player = False
            self.actions['attack1'] = False
            self.set_cooldown_timer(800)
            self.selected_attack = random.randint(1, 4)

    def attack2(self):
        if self.animations['attack2'].get_frame() == 4 and not self.hit_player:
            self.hit_player = True
            if self.flip:
                position = (self.rect.x + self.rect.w - 40 - 13, self.rect.y + 8)
            else:
                position = (self.rect.x + 40, self.rect.y + 8)
            Normal(self.level, self.energy_ball, position, 10, 7, self.direction, 0, self.level.enemy_projectiles)
            ATTACK_SFX['laser shot 2'].play()

        self.velocity[0] = self.speed * 0.6 * self.random_direction

        if self.animations['attack2'].finished:
            self.hit_player = False
            self.actions['attack2'] = False
            self.set_cooldown_timer(300)
            self.selected_attack = random.randint(1, 4)

    def attack3(self, player):
        if self.visions['attack3'].colliderect(player):
            if self.animations['attack3'].get_frame() == 4 and not self.hit_player:
                self.hit_player = True
                player.take_melee_damage(10)
                player.knockback(5 * self.direction, -3, 2)
                self.level.camera.shake_screen(200, 6)
                ATTACK_SFX['metal hit 4'].play()

        self.velocity[0] = 0

        if self.animations['attack3'].finished:
            self.hit_player = False
            self.actions['attack3'] = False
            self.set_cooldown_timer(300)
            self.selected_attack = random.randint(1, 4)

    def attack4(self, player):
        if self.visions['attack3'].colliderect(player):
            frame = self.animations['attack4'].get_frame()
            if frame == 4 and not self.hit_player:
                self.hit_player = True
                player.take_melee_damage(10)
                player.knockback(5 * self.direction)
                self.level.camera.shake_screen(200, 8)
                ATTACK_SFX['metal hit 2'].play()

        self.velocity[0] = self.speed * 1.3 * self.direction

        if self.animations['attack4'].finished:
            self.hit_player = False
            self.velocity[0] = 0
            self.actions['attack4'] = False
            self.set_cooldown_timer(300)
            self.selected_attack = random.randint(1, 4)


class Vampire(Boss):
    def __init__(self, level, position):
        super().__init__(level, '4 vampire', (17, 41), position, 1.5, 3000, (-14, -55), (96, 96))

        self.actions = {
            'hurt': False, 'death': False, 'sneer': False,
            'attack1': False, 'attack2': False, 'attack3': False, 'attack4': False,
            'walk': False, 'idle': True
        }
        self.animations = {
            'idle': Animation(f'assets/sprites/bosses/{self.name}/idle.png', 4, True, self.image_size),
            'walk': Animation(f'assets/sprites/bosses/{self.name}/walk.png', 7, True, self.image_size),
            'hurt': Animation(f'assets/sprites/bosses/{self.name}/hurt.png', 3, False, self.image_size),
            'death': Animation(f'assets/sprites/bosses/{self.name}/death.png', 6, False, self.image_size),
            'sneer': Animation(f'assets/sprites/bosses/{self.name}/sneer.png', 6, False, self.image_size),
            'attack1': Animation(f'assets/sprites/bosses/{self.name}/attack1.png', 11, True, self.image_size),
            'attack2': Animation(f'assets/sprites/bosses/{self.name}/attack2.png', 8, False, self.image_size),
            'attack3': Animation(f'assets/sprites/bosses/{self.name}/attack3.png', 7, False, self.image_size),
            'attack4': Animation(f'assets/sprites/bosses/{self.name}/attack4.png', 12, False, self.image_size),
        }

        # AI extras
        self.selected_attack = 1
        self.attack = {
            'timer': Timer(1500),
            'direction': 1,
            'count': 0
        }
        self.summon_effect = Animation('assets/sprites/bosses/4 vampire/attack3_effect.png', 10, False)
        self.pumpkin_image = load_image('assets/sprites/bosses/4 vampire/pumpkin.png')
        self.summon = False
        self.summon_position = (self.rect.centerx - 35 - 48, self.position[1] - 30)
        self.play_sound = False
        self.death_sound = 'human 4'

    def draw(self):
        position = self.image_position()

        # Display image
        self.level.canvases[5].blit(self.display_image,
                                    (position[0] - self.level.camera.x, position[1] - self.level.camera.y))

        # Health bar
        self.draw_health_bar(self.level.canvases[5], self.level.camera)

        # Summon effect
        if self.summon and not self.health_depleted():
            self.summon_effect.update(self.level.game.delta)
            self.level.canvases[5].blit(
                self.summon_effect.get_image(),
                (self.summon_position[0] - self.level.camera.x, self.summon_position[1] - self.level.camera.y)
            )

    def update_vision(self):
        self.visions = {
            'attack1': pygame.Rect(self.rect.centerx - 160 * bool(self.direction - 1), self.rect.y, 160, 20),
            'attack2': pygame.Rect(self.rect.centerx - 128 * bool(self.direction - 1), self.rect.y, 128, 20),
            'attack3': pygame.Rect(self.rect.centerx - 300 * bool(self.direction - 1), self.rect.y, 300, 20),
            'attack4': pygame.Rect(self.rect.centerx - 128 * bool(self.direction - 1), self.rect.y - 40, 128, 80),
        }

    def choose_attack(self, player):
        if self.attack_cooldown:
            self.velocity[0] = 0
            self.actions['walk'] = False
            self.attack_cooldown.update()
            return

        # Don't switch attacks when attacking
        if self.actions['attack1'] or self.actions['attack3'] or self.actions['attack2'] or self.actions['attack4']:
            return

        if self.actions['sneer']:
            self.velocity[0] = 0
            if self.animations['sneer'].finished:
                self.actions['sneer'] = False
            return

        if player.health_depleted():
            self.actions['sneer'] = True
            return

        if self.selected_attack == 1:
            if self.visions['attack1'].colliderect(player):
                self.actions['attack1'] = True
                self.attack['direction'] = self.direction
                self.attack['timer'] = Timer(random.randint(1000, 2000))
                self.attack['timer'].activate()
        if self.selected_attack == 2:
            if self.visions['attack2'].colliderect(player):
                self.actions['attack2'] = True
        if self.selected_attack == 3:
            if  self.hp < self.init_hp / 2:
                self.actions['attack3'] = True
                self.summon = True
            else:
                self.selected_attack = int(random.choice((1, 2, 4)))
        if self.selected_attack == 4:
            if self.visions['attack4'].colliderect(player):
                self.attack['direction'] = self.direction
                self.actions['attack4'] = True

    def handle_attacks(self, player):
        if self.actions['attack1']:
            self.attack1(player)
        elif self.actions['attack2']:
            self.attack2(player)
        elif self.actions['attack3']:
            self.attack3()
        elif self.actions['attack4']:
            self.attack4(player)

    def attack1(self, player):
        self.velocity[0] = self.attack['direction'] * 2.4
        self.direction = self.attack['direction']

        self.attack['timer'].update()
        if not self.attack['timer']:
            self.actions['attack1'] = False
            self.attack['direction'] = 0
            self.velocity[0] = 0
            self.set_cooldown_timer(700)
            if self.hp > self.init_hp * (3 / 2):
                self.selected_attack = random.randint(1, 4)
            else:
                self.selected_attack = 3
            return

        # Stop when boss runs into the player
        if self.rect.colliderect(player):
            player.take_melee_damage(10)
            player.knockback(6 * self.direction)
            self.level.camera.shake_screen(200, 8)
            self.actions['attack1'] = False
            self.velocity[0] = 0
            self.set_cooldown_timer(1200)
            if self.hp > self.init_hp * (3 / 2):
                self.selected_attack = random.randint(1, 4)
            else:
                self.selected_attack = 3

    def attack2(self, player):
        self.velocity[0] = 0

        frame = self.animations['attack2'].get_frame()
        if frame == 4 and not self.hit_player:
            if self.flip:
                pos = (self.rect.left - 2 - 5, self.rect.y + 19)
            else:
                pos = (self.rect.right + 2, self.rect.y + 19)
            speed = abs(self.rect.centerx - player.rect.centerx) / FPS * 1.7
            ThrownProjectile(self.level, self.pumpkin_image, pos, 10, speed, self.direction, -3, self.level.enemy_projectiles)
            self.hit_player = True

        if self.animations['attack2'].finished:
            self.hit_player = False
            self.animations['attack2'].reset()
            self.actions['attack2'] = False
            self.set_cooldown_timer(1200)
            if self.hp > self.init_hp * (3 / 2):
                self.selected_attack = random.randint(1, 4)
            else:
                self.selected_attack = 3

    def attack3(self):
        self.velocity[0] = 0

        if self.flip:
            self.summon_position = (self.rect.centerx - 35 - 48, self.position[1] - 30)
        else:
            self.summon_position = (self.rect.centerx + 35, self.position[1] - 30)

        if self.animations['attack3'].finished:
            self.hit_player = False
            self.actions['attack3'] = False
            self.summon_effect.reset()
            self.summon = False
            enemy = Demoness(self.level, (self.summon_position[0] + 18, self.summon_position[1] + 9))
            enemy.hp = enemy.init_hp * 0.5
            enemy.player_spotted = True
            self.set_cooldown_timer(random.randint(1500, 3000))
            self.selected_attack = random.randint(1, 4)

    def attack4(self, player):
        if not self.play_sound and self.animations['attack4'].get_frame() == 2:
            MISC_SFX['dash 2'].play()
            self.play_sound = True

        self.velocity[0] = self.attack['direction'] * 4
        self.direction = self.attack['direction']

        if self.rect.colliderect(player) and not self.hit_player:
            self.hit_player = True
            player.take_melee_damage(10)

        if self.animations['attack4'].finished:
            self.animations['attack4'].reset()
            self.attack['count'] += 1

        if self.attack['count'] > 1:
            self.attack['count'] = 0
            self.hit_player = False
            self.actions['attack4'] = False
            self.play_sound = False
            self.set_cooldown_timer(random.randint(1000, 2400))

            if self.hp > self.init_hp * (3 / 2):
                self.selected_attack = random.randint(1, 4)
            else:
                self.selected_attack = 3


class TheScientist(Boss):
    def __init__(self, level, position):
        super().__init__(level, '5 the scientist', (21, 41), position, 1.5, 2000, (-14, -55), (96, 96))

        self.actions = {
            'hurt': False, 'death': False, 'special': False,
            'attack1': False, 'attack2': True, 'attack3': False, 'attack4': False, 'attack4_2': False,
            'walk': False, 'idle': True
        }

        self.animations = {
            'idle': Animation(f'assets/sprites/bosses/{self.name}/special.png', 4, True, self.image_size),
            'walk': Animation(f'assets/sprites/bosses/{self.name}/walk.png', 7, True, self.image_size),
            'hurt': Animation(f'assets/sprites/bosses/{self.name}/hurt.png', 3, False, self.image_size),
            'death': Animation(f'assets/sprites/bosses/{self.name}/death.png', 6, False, self.image_size),
            'attack1': Animation(f'assets/sprites/bosses/{self.name}/attack1.png', 6, False, self.image_size),
            'attack2': Animation(f'assets/sprites/bosses/{self.name}/attack2.png', 9, False, self.image_size),
            'attack3': Animation(f'assets/sprites/bosses/{self.name}/attack3.png', 10, False, self.image_size),
            'attack4': Animation(f'assets/sprites/bosses/{self.name}/attack4.png', 8, False, self.image_size),
            'attack4_2': Animation(f'assets/sprites/bosses/{self.name}/attack4_2.png', 8, True, self.image_size),
            'special': Animation(f'assets/sprites/bosses/{self.name}/special.png', 8, True, self.image_size),
        }

        self.attack = {
            'direction': 1,
            'timer': Timer(1600),
            'end position': position,
            'frame': 0,
            'counter': 0,
            'limit': random.randint(1, 3)
        }

        self.laser_image = load_image('assets/sprites/bosses/5 the scientist/laser.png')
        self.death_sound = 'human 4'

    def update_vision(self):
        self.visions = {
            'attack1': pygame.Rect(self.rect.centerx - 192 * bool(self.direction - 1), self.rect.y, 192, 20),
            'attack2': pygame.Rect(self.rect.centerx - 192 * bool(self.direction - 1), self.rect.y, 192, 20),
            'attack3': pygame.Rect(self.rect.centerx - 28 * bool(self.direction - 1), self.rect.y, 28, 20),
            'attack4': pygame.Rect(self.rect.centerx - 192 * bool(self.direction - 1), self.rect.y, 192, self.rect.h),
        }

    def choose_attack(self, player):
        if self.attack_cooldown:
            self.velocity[0] = 0
            self.actions['walk'] = False
            self.attack_cooldown.update()
            return

        # Don't switch attacks when attacking
        if self.actions['attack1'] or self.actions['attack3'] or self.actions['attack2'] or self.actions['attack4'] or self.actions['attack4_2']:
            return

        if player.health_depleted():
            return

        if self.selected_attack == 1:
            if self.visions['attack1'].colliderect(player):
                self.actions['attack1'] = True
        if self.selected_attack == 2:
            if self.visions['attack2'].colliderect(player):
                self.actions['attack2'] = True
        if self.selected_attack == 3:
            if self.visions['attack3'].colliderect(player):
                self.actions['attack3'] = True
        if self.selected_attack == 4:
            if self.visions['attack4'].colliderect(player):
                self.attack['direction'] = self.direction
                self.actions['attack4'] = True
                ATTACK_SFX['flapping wings'].play()

    def handle_attacks(self, player):
        if self.actions['attack1']:
            self.attack1()
        elif self.actions['attack2']:
            self.attack2()
        elif self.actions['attack3']:
            self.attack3(player)
        elif self.actions['attack4'] or self.actions['attack4_2']:
            self.attack4(player)

    def attack1(self):
        if self.attack['counter'] > self.attack['limit']:
            self.attack['limit'] = random.randint(1, 3)
            self.actions['attack1'] = False
            self.selected_attack = random.randint(1, 4)
            self.velocity[0] = 0
            return

        frame = self.animations['attack1'].get_frame()
        if frame == 2 or frame == 5:
            if not self.hit_player:
                self.hit_player = True
                if self.flip:
                    position = (self.rect.x + self.rect.w - 20, self.rect.y + 15)
                else:
                    position = (self.rect.x + 20, self.rect.y + 15)
                Normal(self.level, self.laser_image, position, 5, 6, self.direction, 0, self.level.enemy_projectiles)
                self.attack['counter'] += 1
                ATTACK_SFX['laser shot'].play()
        else:
            self.hit_player = False

        if self.animations['attack1'].finished:
            self.hit_player = False
            self.animations['attack1'].reset()

    def attack2(self):
        self.velocity[0] = 0
        frame = self.animations['attack2'].get_frame()
        if frame == 4 and not self.hit_player:
            self.hit_player = True
            if self.flip:
                position = (self.rect.right - 9 - 20, self.rect.y + 15)
            else:
                position = (self.rect.x + 20, self.rect.y + 15)
            Normal(self.level, self.laser_image, position, 10, 8, self.direction, 0, self.level.enemy_projectiles)
            ATTACK_SFX['laser shot'].play()

        if self.animations['attack2'].finished:
            self.hit_player = False
            self.actions['attack2'] = False
            self.selected_attack = random.randint(1, 4)

    def attack3(self, player):
        if self.animations['attack3'].get_frame() == 4 and not self.hit_player:
            if self.visions['attack3'].colliderect(player):
                self.hit_player = True
                player.take_melee_damage(10)

        self.velocity[0] = 2. * self.direction

        if self.animations['attack3'].finished:
            self.hit_player = False
            self.actions['attack3'] = False
            self.selected_attack = random.randint(1, 4)

    def attack4(self, player):
        if self.actions['attack4'] and not self.actions['attack4_2']:
            self.velocity[0] = 0
            if self.animations['attack4'].finished:
                self.actions['attack4'] = False
                self.actions['attack4_2'] = True
                self.attack['end position'] = player.rect.center
                self.attack['direction'] = self.direction
            return

        if self.actions['attack4_2'] and not self.actions['attack4']:
            if self.rect.colliderect(player):
                self.velocity[0] = 0
                self.actions['attack4_2'] = False
                self.attack['direction'] = 0
                player.take_melee_damage(10)
                player.knockback(6 * self.direction)
                self.level.camera.shake_screen(200, 8)
                self.selected_attack = random.randint(1, 4)
                ATTACK_SFX['flapping wings'].stop()
                return

        if abs(self.rect.centerx - self.attack['end position'][0]) < 5 or not self.level.camera.on_screen(self, -28):
            ATTACK_SFX['flapping wings'].stop()
            self.actions['attack4_2'] = False
            self.velocity[0] = 0
            self.level.camera.shake_screen(200, 8)
            self.selected_attack = random.randint(1, 4)
            return

        self.velocity[0] = self.speed * 2.7 * self.attack['direction']

