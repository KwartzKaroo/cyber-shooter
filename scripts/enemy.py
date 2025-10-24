import random

import pygame
from scripts.body import Body
from scripts.utils import Animation, Timer, debug_rect


class Enemy(Body):
    def __init__(self, game, level, size, pos, speed, hp, name, image_offset, group=()):
        super().__init__(game, level, size, pos, speed, hp, image_offset, group)

        self.actions = {'death': False, 'hurt': False, 'attack': False, 'walk': False, 'idle': True}
        self.animations = {
            'idle': Animation(f'assets/sprites/enemies/{name}/idle.png', 7, True, 4),
            'walk': Animation(f'assets/sprites/enemies/{name}/walk.png', 11, True, 6),
            'hurt': Animation(f'assets/sprites/enemies/{name}/hurt.png', 8, False, 2),
            'death': Animation(f'assets/sprites/enemies/{name}/death.png', 7, False, size=(48, 48)),
            'attack': Animation(f'assets/sprites/enemies/{name}/attack.png', 11, False, size=(48, 48)),
        }
        self.current_action = 'idle'
        self.prev_action = 'idle'
        self.display_image = None

        # AI
        self.stop_timer = Timer(1000)
        self.stopped = False
        self.sees_player = False
        self.sight = pygame.Rect(self.rect.x, self.rect.y, 120, 20)
        self.distance = random.randint(150, 300)
        self.walk_distance = 0

        # Attacking
        self.attack_rect = pygame.Rect(self.pos, (20, 20))
        self.hit_player = False

        # Health
        self.death_timer = Timer(5000)

    def draw(self):
        # Character image
        self.game.layers[4].blit(self.image, self.image_position())
        # debug_rect(self.game.layers[4], self.rect, self.level.scroll)

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
        self.animations[self.current_action].update(self.game.delta)
        self.image = pygame.transform.flip(self.animations[self.current_action].get_image(), self.flip, False)

    def image_position(self):
        pos = list(self.pos)

        pos[1] += self.image_offset[1]
        if self.flip:
            pos[0] += (self.rect.w - 48 - self.image_offset[0])
        else:
            pos[0] += self.image_offset[0]

        return pos[0] - self.level.scroll[0], pos[1] - self.level.scroll[1]

    def roam(self):
        # Reset velocity to 0
        self.velocity[0] = 0
        self.actions['walk'] = False

        # Ignore roaming when player is spotted or dead
        if self.sees_player or self.zero_health():
            return

        # Continue walking if distance has not been covered
        if self.walk_distance < self.distance:
            self.actions['walk'] = True
            self.velocity[0] = self.speed * self.direction
            self.walk_distance += self.speed * self.game.delta
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

    def spot_player(self):
        if self.zero_health():
            return

        # Ignore player when he's dead
        if self.level.player.zero_health():
            self.sees_player = False
            return

        if self.flip:
            self.sight = pygame.Rect(self.rect.centerx - 180, self.rect.y, 180, 20)
        else:
            self.sight = pygame.Rect(self.rect.centerx, self.rect.y, 180, 20)

        if self.sight.colliderect(self.level.player):
            self.sees_player = True

        if self.sees_player:
            if self.rect.right < self.level.player.rect.left:
                self.actions['walk'] = True
                self.direction = 1
                self.velocity[0] = self.speed
            elif self.rect.left > self.level.player.rect.right:
                self.actions['walk'] = True
                self.direction = -1
                self.velocity[0] = -self.speed

    def attack(self):
        pass

    def health(self):
        for bullet in self.level.player_bullets:
            if bullet.rect.colliderect(self.rect) and not self.zero_health():
                bullet.impacted = True
                self.sees_player = True
                self.hp -= bullet.damage
                self.actions['hurt'] = True

        if self.actions['hurt']:
            self.velocity[0] = 0
            if self.animations['hurt'].finished:
                self.actions['hurt'] = False

        if self.zero_health():
            self.actions['death'] = True
            self.death_timer.activate()
            self.death_timer.update()
            if not self.death_timer:
                self.kill()

    def update(self, *args, **kwargs):
        self.roam()
        self.spot_player()
        self.attack()
        self.health()

        self.check_on_floor()
        self.apply_gravity()
        self.tile_collisions()
        self.ramp_collisions()
        self.update_position()

        self.animate()
        self.draw()

