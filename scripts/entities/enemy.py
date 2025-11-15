import random

import pygame

from scripts.audio import SFX
from scripts.entities.body import Body
from scripts.utils import Animation, Timer


class Enemy(Body):
    def __init__(self, game, level, size, pos, speed, hp, name, image_offset, group=()):
        super().__init__(game, level, size, pos, speed, hp, image_offset, group)

        self.actions = {'hurt': False, 'death': False, 'attack': False, 'walk': False, 'idle': True}
        self.animations = {
            'idle': Animation(f'assets/sprites/enemies/{name}/idle.png', 4, True, (48, 48)),
            'walk': Animation(f'assets/sprites/enemies/{name}/walk.png', 8, True, (48, 48)),
            'hurt': Animation(f'assets/sprites/enemies/{name}/hurt.png', 3, False, (48, 48)),
            'death': Animation(f'assets/sprites/enemies/{name}/death.png', 6, False, (48, 48)),
            'attack': Animation(f'assets/sprites/enemies/{name}/attack.png', 8, False, (48, 48)),
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
        self.edge_rect = pygame.Rect(self.rect.right, self.rect.bottom, 2, 2)
        self.wall_rect = pygame.Rect(self.rect.right, self.rect.top - 4, 2, 8)
        self.is_on_edge = False
        self.is_by_wall = False

        # Attacking
        self.attack_rect = pygame.Rect(self.pos, (20, 20))
        self.hit_player = False

        # Health
        self.death_timer = Timer(5000)
        self.hit_player_sound = 'grunt 1'
        self.take_damage_sound = 'grunt 2'
        self.death_sound = 'death 1'

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

    def check_on_edge(self, tiles):
        if self.flip:
            self.edge_rect = pygame.Rect(self.rect.left - 2 - 10, self.rect.bottom, 2, 2)
            self.wall_rect = pygame.Rect(self.rect.left - 2 - 10, self.rect.top - 4, 2, 8)
        else:
            self.edge_rect = pygame.Rect(self.rect.right + 10, self.rect.bottom, 2, 2)
            self.wall_rect = pygame.Rect(self.rect.right + 10, self.rect.top - 4, 2, 8)

        self.is_on_edge = False
        self.is_by_wall = False

        if self.edge_rect.collidelist(tiles) == -1:
            self.is_on_edge = True

        if self.wall_rect.collidelist(tiles) > -1:
            self.is_by_wall = True

    def roam(self):
        # Reset velocity to 0
        self.velocity[0] = 0
        self.actions['walk'] = False

        # Ignore roaming when player is spotted or dead
        if self.sees_player or self.zero_health():
            return

        # Continue walking if distance has not been covered
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

    def spot_player(self):
        if self.zero_health():
            return

        # Ignore player when he's dead
        if self.level.player.zero_health():
            self.sees_player = False
            return

        # Ignore player when there's a wall between them or enemy is about to fall of
        if self.is_by_wall or self.is_on_edge:
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
                self.hp -= bullet.damage
                bullet.impacted = True
                self.sees_player = True
                if not self.actions['hurt']:
                    SFX[self.take_damage_sound].play()
                self.actions['hurt'] = True

        if self.actions['hurt']:
            self.velocity[0] = 0
            if self.animations['hurt'].finished:
                self.actions['hurt'] = False

        if self.zero_health():
            SFX[self.take_damage_sound].stop()
            if not self.actions['death']:
                self.level.score += 100
                SFX[self.death_sound].play()
            self.actions['death'] = True
            self.death_timer.activate()
            self.death_timer.update()
            if not self.death_timer:
                self.kill()

    def update(self, *args, **kwargs):
        # Get tiles around the character
        tiles = self.level.tilemap.get_collision_tiles(self.rect)
        ramps = self.level.tilemap.get_collision_ramps(self.rect)

        self.check_on_edge(tiles)
        self.roam()
        self.spot_player()
        self.attack()
        self.health()

        self.check_on_floor(tiles, ramps)
        self.apply_gravity()
        self.tile_collisions(tiles)
        self.ramp_collisions(ramps)
        self.update_position()

        self.animate()
        self.draw()
