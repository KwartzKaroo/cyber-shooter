import pygame
import pickle
import random

from scripts.audio import MISC_SFX, DEATH_SFX
from scripts.entity import Entity
from scripts.globals import FPS
from scripts.gun import Gun
from scripts.projectile import Electric
from scripts.utils import Animation, load_images_folder, Timer

DOUBLE_STATES = {'jump', 'run', 'idle', 'crouch', 'walk'}
EMOTES = ('angry', 'happy', 'talk', 'use', 'watch')


class Character(Entity):
    def __init__(self, level, character, size, position, speed, hp, image_offset):
        super().__init__(level, size, position, speed, hp)
        self.actions = {
            'death': False, 'hurt': False, 'climb': False, 'pull up': False, 'fall': False, 'hang': False,
            'angry': False, 'happy': False, 'talk': False, 'use': False, 'watch': False,
            'double jump': False, 'jump': False, 'crouch': False, 'walk': False, 'run': False,
            'idle': True
        }
        self.animations = {
            'idle1': Animation(f'assets/sprites/characters/{character}/idle1.png', 3),
            'idle2': Animation(f'assets/sprites/characters/{character}/idle2.png', 3),
            'run1': Animation(f'assets/sprites/characters/{character}/run1.png', 8),
            'run2': Animation(f'assets/sprites/characters/{character}/run2.png', 8),
            'walk1': Animation(f'assets/sprites/characters/{character}/walk1.png', 5),
            'walk2': Animation(f'assets/sprites/characters/{character}/walk2.png', 5),
            'jump1': Animation(f'assets/sprites/characters/{character}/jump1.png', 6, False),
            'jump2': Animation(f'assets/sprites/characters/{character}/jump2.png', 6, False),
            'double jump': Animation(f'assets/sprites/characters/{character}/double_jump.png', 8, False),
            'crouch1': Animation(f'assets/sprites/characters/{character}/crouch1.png', 7, False),
            'crouch2': Animation(f'assets/sprites/characters/{character}/crouch2.png', 7, False),
            'death': Animation(f'assets/sprites/characters/{character}/death.png', 6, False),
            'hurt': Animation(f'assets/sprites/characters/{character}/hurt.png', 2, False),
            'pull up': Animation(f'assets/sprites/characters/{character}/pull_up.png', 5, False, (48, 96)),
            'hang': Animation(f'assets/sprites/characters/{character}/hang.png', 3, True),
            'fall': Animation(f'assets/sprites/characters/{character}/fall.png', 3, False),
            'climb': Animation(f'assets/sprites/characters/{character}/climb.png', 6),

            # Emotes
            'angry': Animation(f'assets/sprites/characters/{character}/angry.png', 5, False),
            'happy': Animation(f'assets/sprites/characters/{character}/happy.png', 5, False),
            'watch': Animation(f'assets/sprites/characters/{character}/watch.png', 5, False),
            'use': Animation(f'assets/sprites/characters/{character}/use.png', 5, False),
            'talk': Animation(f'assets/sprites/characters/{character}/talk.png', 5, False),
        }
        self.current_action = 'idle'
        self.current_animation = 'idle1'
        self.display_image = self.animations[self.current_animation]
        self.image_offset = image_offset

        # Extra mobility
        self.walking = False
        self.emoting = False
        self.climbing = {
            'up': False,
            'down': False
        }
        self.hang_rect = pygame.Rect(self.rect.right, self.position.x - 2, 2, 2)
        self.side_rect = pygame.Rect(self.rect.right, self.rect.centerx, 2, 2)

        # Hands
        self.hand_images = {
            1: load_images_folder(f'assets/sprites/weapons/hands/{character}/1'),
            2: load_images_folder(f'assets/sprites/weapons/hands/{character}/2'),
        }
        self.hand_image = self.hand_images[1][2]
        self.hand_index = 2

        # Guns
        self.guns = [Gun(self.level, '02'), Gun(self.level, '08')]
        self.guns_index = 0
        self.equipped_gun = self.guns[self.guns_index]
        self.hand_type = self.equipped_gun.type

        # Offsets for hands and guns
        self.offsets = pickle.loads(open(f'data/hand offsets/{character}', 'rb').read())

        # Lives and health
        self.death_timer = Timer(3000)
        self.lives = 2
        self.respawn_point = list(self.position)
        self.dead = False
        self.off_map = False

    # Drawing methods
    def update_image(self):
        for action in self.actions:
            if self.actions[action]:
                self.current_action = action
                break

        # Get image
        state = self.current_action
        if self.current_action in DOUBLE_STATES:
            state = self.current_action  + str(self.hand_type)

        # Keep track of animations
        if self.current_animation != state:
            self.animations[self.current_animation].reset()
            self.current_animation = state

        # Emoting
        if self.emoting and self.animations[state].finished:
            self.emoting = False
            self.actions[self.current_action] = False

        # Get the image
        image: pygame.Surface = self.animations[state].get_image().copy()

        # When hurt
        if self.hurt:
            # Main character image
            mask = pygame.mask.from_surface(image)
            mask_image = mask.to_surface()
            mask_image.set_colorkey((0, 0, 0))

            for w in range(mask_image.get_width()):
                for h in range(mask_image.get_height()):
                    if mask_image.get_at((w, h))[0] != 0:
                        mask_image.set_at((w, h), '#fcba03')
                    else:
                        mask_image.set_at((w, h), (0, 0, 0))
            mask_image.set_alpha(160)
            image.blit(mask_image, (0, 0))

            # Hand image
            hand_mask = pygame.mask.from_surface(self.hand_image)
            hand_mask_image = hand_mask.to_surface()
            hand_mask_image.set_colorkey((0, 0, 0))

            for w in range(32):
                for h in range(32):
                    if hand_mask_image.get_at((w, h))[0] != 0:
                        hand_mask_image.set_at((w, h), '#fcba03')
                    else:
                        hand_mask_image.set_at((w, h), (0, 0, 0))
            hand_mask_image.set_alpha(160)
            self.hand_image.blit(hand_mask_image, (0, 0))

        if self.actions['climb']:
            self.animations[state].update(self.level.game.delta, self.climbing['up'] or self.climbing['down'])
        else:
            self.animations[state].update(self.level.game.delta)

        self.display_image = pygame.transform.flip(image, self.flip, False)

    def draw(self):
        position = self.image_position()
        hand_pos = self.hand_position()

        # Type 1 hand
        if self.hand_type == 1 and self.current_action in DOUBLE_STATES:
            self.equipped_gun.draw(self.level.canvases[5], self.level.camera)
            self.level.canvases[5].blit(self.hand_image,
                                     (hand_pos[0] - self.level.camera[0], hand_pos[1] - self.level.camera[1]))

        # Character image
        self.level.canvases[5].blit(self.display_image, (position[0] - self.level.camera[0], position[1] - self.level.camera[1]))

        # Type 2 hand
        if self.hand_type == 2 and self.current_action in DOUBLE_STATES:
            self.equipped_gun.draw(self.level.canvases[5], self.level.camera)
            self.level.canvases[5].blit(self.hand_image,
                                     (hand_pos[0] - self.level.camera[0], hand_pos[1] - self.level.camera[1]))

    def image_position(self):
        position = list(self.position)

        position[1] += self.image_offset[1]

        if self.flip:
            position[0] += (self.rect.w - 48 - self.image_offset[0])
        else:
            position[0] += self.image_offset[0]

        # Hanging
        if self.actions['hang']:
            position[0] += 4 * self.direction
            position[1] += 3

        if self.actions['pull up']:
            position[1] -= 48

        return position

    # Movement methods
    def run(self):
        if self.actions['hang'] or self.actions['pull up'] or self.actions['fall'] or self.emoting:
            self.velocity[0] = 0
            return

        if self.knocked_back:
            return

        if self.health_depleted():
            self.velocity.x = 0
            return

        left = pygame.K_a in self.level.game.held_key_presses
        right = pygame.K_d in self.level.game.held_key_presses

        if left and not right:
            self.direction = -1
            self.flip = True
        if right and not left:
            self.direction = 1
            self.flip = False

        self.actions['run'] = bool(right - left)
        self.velocity.x = (right - left) * self.speed

    def jump(self):
        if self.health_depleted():
            return

        if self.jump_count == 0:
            self.actions['double jump'] = False
            self.actions['jump'] = False

        if self.current_action == 'double jump':
            if self.animations['double jump'].finished:
                self.actions['double jump'] = False

        jump = pygame.K_SPACE in self.level.game.key_presses
        if jump and self.jump_count == 0:
            self.jump_count = 1
            self.velocity.y = -3.5
            self.actions['jump'] = True
        elif jump and self.jump_count == 1:
            self.jump_count = 2
            self.velocity.y = -3.5
            self.actions['double jump'] = True

    def crouch(self):
        # Don't crouch if jumping
        if self.actions['jump'] or self.actions['double jump'] or self.emoting:
            return

        # Reset crouch
        self.actions['crouch'] = False

        if self.health_depleted():
            return

        if pygame.K_c in self.level.game.held_key_presses:
            self.actions['crouch'] = True
            self.velocity.x = 0

    def ladder_climbing(self, tiles):
        if self.health_depleted():
            return

        ladders = self.level.tilemap.get_tiles_around('ladders', self.rect)

        # Some flags that help to see if we can climb a ladder or not
        can_climb = False
        snap_pos = (0, 0)

        # Check the
        for ladder in ladders:
            if self.rect.colliderect(ladder):
                if abs(ladder.rect.centerx - self.rect.centerx) < 10:
                    snap_pos = (ladder.rect.centerx - self.rect.w / 2, self.position.y)
                    can_climb = True
                else:
                    self.climbing = {'up': False, 'down': False}
                    self.actions['climb'] = False

        if not can_climb:
            self.actions['climb'] = False
            return

        # Input
        up = pygame.K_w in self.level.game.held_key_presses
        down = pygame.K_s in self.level.game.held_key_presses

        # If player can climb a ladder
        if pygame.K_c in self.level.game.key_presses:
            self.actions['climb'] = not self.actions['climb']
            self.position = pygame.Vector2(snap_pos)

        self.climbing['up'] = up
        self.climbing['down'] = down

        # Stop moving up the ladder when it ends
        overhead_rect = pygame.Rect((self.rect.x - 2, self.rect.top + self.rect.h - 32 - 1, self.rect.w + 4, 1))
        if overhead_rect.collidelist(ladders) == -1:
            self.climbing['up'] = False

        overhead_rect = pygame.Rect((self.rect.x - 2, self.rect.top - 2, self.rect.w + 4, 1))
        if overhead_rect.collidelist(tiles) > -1:
            self.climbing['up'] = False

        # Latch on the ladder if velocity is high enough
        elif overhead_rect.collidelist(ladders) > -1 and  self.velocity.y > 1:
            self.actions['climb'] = True

        # Stop moving down the ladder when it ends
        if self.bottom_rect.collidelist(ladders) == -1:
            self.climbing['down'] = False

        # Moving up and down the ladders
        if self.actions['climb']:
            self.velocity.y = (down - up)
            if not self.climbing['up'] and up:
                self.velocity.y = 0

            if not self.climbing['down'] and down:
                self.velocity.y = 0

    def hang(self, tiles):
        self.actions['hang'] = False

        if self.health_depleted():
            return

        if self.actions['climb']:
            self.actions['pull up'] = False
            return

        if self.flip:
            self.hang_rect = pygame.Rect(self.rect.left - 2, self.rect.top - 1, 2, 1)
            self.side_rect = pygame.Rect(self.rect.left - 2, self.rect.top, 2, 2)
        else:
            self.hang_rect = pygame.Rect(self.rect.right, self.rect.top - 1, 2, 1)
            self.side_rect = pygame.Rect(self.rect.right, self.rect.top, 2, 2)

        # Condition to be hanging
        if self.velocity.y >= 0 and not self.actions['fall']:
            if self.side_rect.collidelist(tiles) > -1 and self.hang_rect.collidelist(tiles) == -1:
                self.velocity.y = 0
                self.jump_count = 3
                self.actions['hang'] = True
                self.actions['double jump'] = False
                self.actions['jump'] = False

        # When pulling up
        if self.actions['pull up']:
            if self.animations['pull up'].finished:
                self.actions['pull up'] = False
                self.actions['hang'] = False
                self.rect.bottom = self.hang_rect.bottom
                self.position.y = self.rect.y
                self.position.x += 6 * self.direction
                self.jump_count = 0

        # Cancel when character is on the floor
        if self.is_on_floor:
            self.actions['hang'] = False
            self.actions['fall'] = False
            self.actions['pull up'] = False

    def pull_up(self):
        # Can't pull up if he's not hanging
        if not self.actions['hang'] or self.actions['fall']:
            return

        if pygame.K_w in self.level.game.key_presses:
            self.actions['pull up'] = True

    def drop_off_ledge(self):
        # Can't pull up if he's not hanging
        if not self.actions['hang'] or self.actions['pull up']:
            return

        if pygame.K_s in self.level.game.key_presses:
            self.actions['fall'] = True

    # Interaction methods
    def start_emote(self, action):
        if self.actions['hang'] or self.actions['pull up'] or self.actions['fall'] or self.actions['climb'] or self.emoting:
            return

        self.actions[action] = True
        self.emoting = True
        self.current_action = action

    def emote(self):
        if pygame.K_e in self.level.game.key_presses:
            action = str(random.choice(['angry', 'happy']))
            self.start_emote(action)

        if self.emoting:
            if self.animations[self.current_action].finished:
                self.actions[self.current_action] = False
                self.emoting = False

    def open_chest(self):
        for chest in self.level.item_map.chests:
            if pygame.K_f in self.level.game.key_presses:
                if self.rect.colliderect(chest) and not chest.unlocked:
                    self.start_emote('use')
                    chest.open()

    def pick_up_gun(self):
        for gun in self.level.item_map.guns:
            if pygame.K_f in self.level.game.key_presses and self.rect.colliderect(gun):
                temp = self.equipped_gun

                # Load into load out
                self.guns[self.guns_index] = gun
                self.level.item_map.guns.remove(gun)

                # Add to map
                self.level.item_map.guns.append(temp)
                self.equipped_gun = self.guns[self.guns_index]
                self.hand_type = self.equipped_gun.type

    def update_checkpoint(self):
        for point in self.level.tilemap.get_tiles_around('checkpoints', self.rect):
            if self.rect.colliderect(point.rect.left - 16, point.rect.top - 96, 64, 96):
                self.respawn_point = [point.rect.left - 16, point.rect.top + (32 - self.rect.h)]

    # Hand methods
    def update_hands(self):
        self.hand_index = 2

        # if self.current_action == 'run' and self.hand_type == 2 and not pygame.K_j in self.level.game.held_key_presses:
        #     self.hand_index = 1

        if pygame.K_w in self.level.game.held_key_presses:
            self.hand_index = 4
            if pygame.K_k in self.level.game.held_key_presses:
                self.hand_index = 3

        if pygame.K_s in self.level.game.held_key_presses:
            self.hand_index = 0
            if pygame.K_k in self.level.game.held_key_presses:
                self.hand_index = 1

        self.hand_image = pygame.transform.flip(self.hand_images[self.hand_type][self.hand_index], self.flip, False)

    def hand_position(self):
        hand_offset = [0, 0]
        if self.current_action in DOUBLE_STATES:
            hand_offset = (self.offsets['hand offsets'][self.hand_type][self.current_action]
            [self.animations[self.current_animation].get_frame()])

        position = [self.position.x + hand_offset[0] * self.direction, self.position.y + hand_offset[1]]

        if self.flip:
            position[0] += (self.rect.w - 32)

        return position

    # Gun methods
    def gun_position(self):
        hand_pos = self.hand_position()
        gun_offset = self.offsets['gun offsets'][self.equipped_gun.name][self.hand_index]

        if self.flip:
            hand_pos[0] += 32

        return [hand_pos[0] + gun_offset[0] * self.direction, hand_pos[1] + gun_offset[1]]

    def update_guns(self):
        # Update the currently equipped gun
        self.equipped_gun.update(self.level.game.delta, self.gun_position(), self.flip, self.direction, self.hand_index)

        # Shoot
        shoot = pygame.K_j in self.level.game.key_presses
        if self.equipped_gun.ammo == 0 and shoot:
            MISC_SFX['clip empty'].play()
        if self.equipped_gun.automatic:
            shoot = pygame.K_j in self.level.game.held_key_presses

        if shoot and self.current_action in DOUBLE_STATES:
            self.equipped_gun.shoot(self.direction, self.hand_index, self.level.player_bullets)

        # Change a gun
        if pygame.K_i in self.level.game.key_presses:
            self.guns_index = (self.guns_index + 1) % len(self.guns)
            self.equipped_gun = self.guns[self.guns_index]
            self.hand_type = self.equipped_gun.type

    # Health
    def respawn(self):
        self.position = pygame.Vector2(self.respawn_point[0], self.respawn_point[1] + (32 - self.rect.h))
        self.hp = int(self.init_hp)
        self.lives -= 1
        self.actions['death'] = False
        self.hurt = 0
        self.off_map = False

        # Restore some guns
        if self.level.boss_fight:
            self.guns = [Gun(self.level, '09'), Gun(self.level, '13')]
        else:
            self.guns = [Gun(self.level, '02'), Gun(self.level, '15')]
        self.equipped_gun = self.guns[0]
        self.hand_type = self.equipped_gun.type

    def update_health(self):
        # Kill zone boundaries
        for tile in self.level.tilemap.get_tiles_around('boundaries', self.rect):
            if self.rect.colliderect(tile):
                self.hp = 0
                self.off_map = True

        # Enemy projectiles
        for bullet in self.level.enemy_projectiles:
            if bullet.rect.colliderect(self.rect) and not self.health_depleted():
                if isinstance(bullet, Electric):
                    bullet.hit_entity = True
                    self.hp -= bullet.damage / FPS
                elif bullet not in self.bullets_touched:
                    self.bullets_touched.append(bullet)
                    self.hp -= bullet.damage
                bullet.hit_entity = True
                self.hurt = 1

        for bullet in self.bullets_touched:
            if not bullet.alive():
                self.bullets_touched.remove(bullet)

        if self.hurt > 0:
            self.hurt += 1
            if self.hurt > 20:
                self.hurt = 0

        if self.health_depleted():
            if not self.actions['death']:
                DEATH_SFX['player death'].play()
            self.actions['death'] = True
            self.death_timer.activate()
            self.death_timer.update()

            if not self.death_timer:
                if self.lives > 0:
                    self.respawn()
                else:
                    self.dead = True

    def update(self):
        tiles = self.level.tilemap.get_tiles_around('tiles', self.rect)
        ramps = self.level.tilemap.get_tiles_around('ramps', self.rect)

        # Basic checks
        self.apply_gravity()

        # Methods that function on player input
        self.run()
        self.crouch()
        self.jump()
        self.pull_up()
        self.drop_off_ledge()
        self.pick_up_gun()
        self.open_chest()
        self.ladder_climbing(tiles)
        self.emote()

        self.tile_collisions(tiles)
        self.ramp_collisions(ramps)
        self.hang(tiles)
        self.update_health()
        self.update_checkpoint()
        self.update_position()
        self.boss_fight_bounds()

        self.update_guns()
        self.update_hands()

        self.update_image()
        self.draw()


# The presets of characters
class Biker(Character):
    def __init__(self, level, position):
        super().__init__(level, 'biker', (17, 34), position, 2.0, 50, (-6, -14))


class Punk(Character):
    def __init__(self, level, position):
        super().__init__(level, 'punk', (15, 34), position, 2.0, 40, (-7, -14))


class Cyborg(Character):
    def __init__(self, level, position):
        super().__init__(level, 'cyborg', (14, 35), position, 2.0, 40, (-8, -13))
