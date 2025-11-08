import random

import pygame

from scripts.audio import SFX
from scripts.data import HAND_OFFSETS
from scripts.entities.body import Body
from scripts.guns.gun import Gun
from scripts.utils import Animation, load_all_images, Timer

DOUBLE_STATES = {'jump', 'run', 'idle', 'crouch', 'walk'}
EMOTES = ('angry', 'happy', 'talk', 'use', 'watch')


class Character(Body):
    def __init__(self, game, level, size, pos, speed, hp, image_offset, character, starting_guns, group=()):
        super().__init__(game, level, size, pos, speed, hp, image_offset, group)
        # Animations
        self.character = character
        self.actions = {'death': False, 'hurt': False,
                        'pull up': False, 'fall': False, 'hang': False,
                        'angry': False, 'happy': False, 'talk': False, 'use': False, 'watch': False,
                        'double jump': False, 'jump': False, 'crouch': False,
                        'walk': False, 'run': False, 'idle': True}
        self.animations = {
            'idle1': Animation(f'assets/sprites/characters/{character}/idle1.png', 3, True, 4),
            'idle2': Animation(f'assets/sprites/characters/{character}/idle2.png', 3, True, 4),
            'run1': Animation(f'assets/sprites/characters/{character}/run1.png', 8, True, 6),
            'run2': Animation(f'assets/sprites/characters/{character}/run2.png', 8, True, 6),
            'walk1': Animation(f'assets/sprites/characters/{character}/walk1.png', 5, True, 6),
            'walk2': Animation(f'assets/sprites/characters/{character}/walk2.png', 5, True, 6),
            'jump1': Animation(f'assets/sprites/characters/{character}/jump1.png', 6, False, 4),
            'jump2': Animation(f'assets/sprites/characters/{character}/jump2.png', 6, False, 4),
            'double jump': Animation(f'assets/sprites/characters/{character}/double_jump.png', 8, False, 6),
            'crouch1': Animation(f'assets/sprites/characters/{character}/crouch1.png', 4, False, 4),
            'crouch2': Animation(f'assets/sprites/characters/{character}/crouch2.png', 4, False, 4),
            'death': Animation(f'assets/sprites/characters/{character}/death.png', 6, False, 6),
            'hurt': Animation(f'assets/sprites/characters/{character}/hurt.png', 2, False, 1),
            'pull up': Animation(f'assets/sprites/characters/{character}/pull_up.png', 5, False, 6),
            'hang': Animation(f'assets/sprites/characters/{character}/hang.png', 3, True, 4),
            'fall': Animation(f'assets/sprites/characters/{character}/fall.png', 3, False, 4),

            # Emotes
            'angry': Animation(f'assets/sprites/characters/{character}/angry.png', 5, False, 6),
            'happy': Animation(f'assets/sprites/characters/{character}/happy.png', 5, False, 6),
            'watch': Animation(f'assets/sprites/characters/{character}/watch.png', 5, False, 6),
            'use': Animation(f'assets/sprites/characters/{character}/use.png', 5, False, 6),
            'talk': Animation(f'assets/sprites/characters/{character}/talk.png', 5, False, 6),
        }
        self.current_action = 'idle'
        self.state = 'idle1'
        self.display_image = None

        # Extra mobility
        self.hanging = False
        self.hang_rect = pygame.Rect(self.rect.right, self.pos[0] - 2, 2, 2)
        self.side_rect = pygame.Rect(self.rect.right, self.center()[1], 2, 2)

        # Emoting
        self.emoting = False

        # Hands and guns
        self.hand_images = {
            1: load_all_images(f'assets/sprites/guns/hands/{character}/1'),
            2: load_all_images(f'assets/sprites/guns/hands/{character}/2'),
        }
        self.guns = [
            Gun(game, level, starting_guns[0]),
            Gun(game, level, starting_guns[1]),
        ]
        self.guns_index = 0

        self.equipped_gun = self.guns[self.guns_index]
        self.offsets = HAND_OFFSETS[character]
        self.hand_type = self.equipped_gun.type
        self.hand_index = 2

        # For start
        self.start_timer = Timer(2700)
        self.start_timer.activate()

        # Health
        self.hurt = False
        self.death_timer = Timer(3000)
        self.lives = 1
        self.dead = False
        self.respawn_point = list(pos)

    def draw(self):
        hand_pos = self.hand_position()

        # Type 1 hand
        if self.hand_type == 1 and self.current_action in DOUBLE_STATES:
            hand_image = pygame.transform.flip(self.hand_images[1][self.hand_index], self.flip, False)
            self.guns[self.guns_index].draw()
            self.game.layers[4].blit(hand_image,
                                     (hand_pos[0] - self.level.scroll[0], hand_pos[1] - self.level.scroll[1]))

        # Character image
        self.game.layers[4].blit(self.image, self.image_position())

        # Type 2 hand
        if self.hand_type == 2 and self.current_action in DOUBLE_STATES:
            hand_image = pygame.transform.flip(self.hand_images[2][self.hand_index], self.flip, False)
            self.guns[self.guns_index].draw()
            self.game.layers[4].blit(hand_image,
                                     (hand_pos[0] - self.level.scroll[0], hand_pos[1] - self.level.scroll[1]))

    def animate(self):
        for action in self.actions:
            if self.actions[action]:
                self.current_action = action
                break

        # Get image
        state = self.current_action
        if self.current_action in DOUBLE_STATES:
            state = self.current_action + str(self.hand_type)

        # Keep track of animations
        if self.state != state:
            self.animations[self.state].reset()
            self.state = state

        # Emoting
        if self.emoting and self.animations[state].finished:
            self.emoting = False
            self.actions[self.current_action] = False

        # Get the image
        image: pygame.Surface = self.animations[state].get_image()

        # # When hurt
        # if self.hurt:
        #     image2 = image
        self.animations[state].update(self.game.delta)
        self.image = pygame.transform.flip(image, self.flip, False)

    def image_position(self):
        pos = list(self.pos)

        pos[1] += self.image_offset[1]

        if self.flip:
            pos[0] += (self.rect.w - 48 - self.image_offset[0])
        else:
            pos[0] += self.image_offset[0]

        # Hanging
        if self.actions['hang']:
            pos[0] += 4 * self.direction
            pos[1] += 3

        if self.actions['pull up']:
            pos[1] -= 48

        return pos[0] - self.level.scroll[0], pos[1] - self.level.scroll[1]

    def run_and_walk(self):
        # Reset
        self.velocity[0] = 0
        self.actions['run'] = False
        self.actions['walk'] = False

        if self.zero_health():
            return

        # Key press
        left = pygame.K_a in self.game.held_key_presses
        right = pygame.K_d in self.game.held_key_presses

        # Move left
        if left and not right:
            self.velocity[0] = -self.speed
            self.actions['run'] = True
            self.direction = -1
            self.flip = True

        # Move right
        if right and not left:
            self.velocity[0] = self.speed
            self.actions['run'] = True
            self.direction = 1
            self.flip = False

        # If character is walking reduce the speed
        if self.actions['walk']:
            self.velocity[0] /= 3

    def jump(self):
        if self.zero_health():
            return

        if pygame.K_SPACE in self.game.key_presses:
            if self.jump_count == 0 and self.is_on_floor:
                self.actions['jump'] = True
                self.jump_count = 1
                self.velocity[1] = -3.5
            elif self.jump_count == 1:
                self.actions['double jump'] = True
                self.jump_count = 2
                self.velocity[1] = -3.5

        if self.jump_count == 1:
            self.actions['jump'] = True
        else:
            self.actions['jump'] = False

        if self.animations['double jump'].finished:
            self.actions['double jump'] = False
            # self.jump_count = 1

    def crouch(self):
        self.actions['crouch'] = False

        if self.zero_health():
            return

        if pygame.K_c in self.game.held_key_presses:
            self.actions['crouch'] = True

    def hang_and_pull_up(self, tiles):
        self.actions['hang'] = False
        if self.flip:
            self.hang_rect = pygame.Rect(self.rect.left - 2, self.pos[1] - 1, 2, 1)
            self.side_rect = pygame.Rect(self.rect.left - 2, self.rect.top, 2, 2)
        else:
            self.hang_rect = pygame.Rect(self.rect.right, self.pos[1] - 1, 2, 1)
            self.side_rect = pygame.Rect(self.rect.right, self.rect.top, 2, 2)

        # Condition to be hanging
        if self.velocity[1] >= 0 and not self.actions['fall']:
            if self.side_rect.collidelist(tiles) > -1 and self.hang_rect.collidelist(tiles) == -1:
                self.velocity[1] = 0
                self.jump_count = 3
                self.actions['hang'] = True
                self.actions['double jump'] = False
                self.actions['jump'] = False

        # When hanging, you can either pull up or fall down
        if self.actions['hang']:
            if pygame.K_w in self.game.key_presses or pygame.K_SPACE in self.game.key_presses:
                self.actions['pull up'] = True
            if pygame.K_s in self.game.key_presses:
                self.actions['fall'] = True

        # When pulling up
        if self.actions['pull up']:
            if self.animations['pull up'].finished:
                self.actions['pull up'] = False
                self.actions['hang'] = False
                self.rect.bottom = self.hang_rect.bottom
                self.pos[1] = self.rect.y
                self.pos[0] += 6 * self.direction
                self.jump_count = 0

        # Cancel when character is on the floor
        if self.is_on_floor:
            self.actions['hang'] = False
            self.actions['fall'] = False
            self.actions['pull up'] = False

    def emote(self):
        if self.zero_health():
            return

        if self.emoting:
            if self.animations[self.current_action].finished:
                self.actions[self.current_action] = False
                self.emoting = False

        if self.is_on_floor and pygame.K_e in self.game.key_presses:
            self.actions[random.choice(EMOTES)] = True
            self.emoting = True

    def hand_position(self):
        hand_offset = [0, 0]
        if self.current_action in DOUBLE_STATES:
            hand_offset = (self.offsets['hand offsets'][self.hand_type][self.current_action]
            [self.animations[self.state].get_frame()])

        pos = [self.pos[0] + hand_offset[0] * self.direction, self.pos[1] + hand_offset[1]]

        if self.flip:
            pos[0] += (self.rect.w - 32)

        return pos

    def gun_position(self):
        hand_pos = self.hand_position()
        gun_offset = self.offsets['gun offsets'][self.equipped_gun.name][self.hand_index]

        if self.flip:
            hand_pos[0] += 32

        return [hand_pos[0] + gun_offset[0] * self.direction, hand_pos[1] + gun_offset[1]]

    def update_hands_and_gun(self):
        if self.zero_health():
            return

        # Switch guns
        if pygame.K_i in self.game.key_presses:
            self.guns_index = (self.guns_index + 1) % 2
            self.equipped_gun = self.guns[self.guns_index]
            self.hand_type = self.equipped_gun.type

        self.hand_index = 2
        if pygame.K_w in self.game.held_key_presses:
            self.hand_index = 4
            if pygame.K_k in self.game.held_key_presses:
                self.hand_index = 3

        if pygame.K_s in self.game.held_key_presses:
            self.hand_index = 0
            if pygame.K_k in self.game.held_key_presses:
                self.hand_index = 1

        self.equipped_gun.update(self.gun_position(), self.flip, self.direction, self.hand_index)

        # Shooting
        shoot = pygame.K_j in self.game.key_presses
        if self.equipped_gun.automatic:
            shoot = pygame.K_j in self.game.held_key_presses

        if shoot and self.current_action in DOUBLE_STATES:
            self.equipped_gun.shoot(self.direction, self.hand_index, self.level.player_bullets)

    def switch_gun(self):
        if self.zero_health():
            return

        if pygame.K_x in self.game.key_presses or pygame.K_f in self.game.key_presses:
            for gun in self.level.interactivemap.guns:
                if self.rect.colliderect(gun):
                    #
                    temp = self.equipped_gun

                    # Load into load out
                    self.guns[self.guns_index] = gun
                    self.level.interactivemap.guns.remove(gun)

                    # Add to map
                    self.level.interactivemap.guns.append(temp)
                    self.equipped_gun = self.guns[self.guns_index]
                    self.hand_type = self.equipped_gun.type

    def checkpoint(self):
        for tile in self.level.interactivemap.get_checkpoints(self.rect):
            if self.rect.colliderect(tile.rect.left - 16, tile.rect.top - 96, 64, 96):
                self.respawn_point = [tile.rect.left - 16, tile.rect.top + (32 - self.rect.h)]

    def health(self):
        for bullet in self.level.enemy_projectiles:
            if bullet.rect.colliderect(self.rect):
                bullet.impacted = True
                self.hp -= bullet.damage
                self.actions['hurt'] = True

        if self.actions['hurt']:
            self.velocity[0] = 0
            if self.animations['hurt'].finished:
                self.actions['hurt'] = False

        if self.zero_health():
            if not self.actions['death']:
                SFX['death 1'].play()
            self.actions['death'] = True
            self.death_timer.activate()
            self.death_timer.update()

            if not self.death_timer:
                if self.lives > 1:
                    self.respawn()
                else:
                    self.dead = True

    def respawn(self):
        self.pos = list(self.respawn_point)
        self.hp = int(self.init_hp)
        self.lives -= 1
        self.actions['death'] = False
        self.actions['hurt'] = False

    def update(self, *args, **kwargs):
        # Get tiles around the character
        tiles = self.level.tilemap.get_collision_tiles(self.rect)
        ramps = self.level.tilemap.get_collision_ramps(self.rect)

        # User controlled movement
        self.run_and_walk()
        self.jump()
        self.crouch()
        self.emote()
        self.health()

        # Other
        self.update_hands_and_gun()
        self.switch_gun()

        # Movement
        self.check_on_floor(tiles, ramps)
        self.apply_gravity()
        self.tile_collisions(tiles)
        self.ramp_collisions(ramps)
        self.boundary_collision()
        self.checkpoint()
        self.hang_and_pull_up(tiles)
        self.update_position()

        # Draw the body
        self.animate()
        self.draw()
