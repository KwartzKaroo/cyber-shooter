import json
import math

import pygame

from scripts.audio import MUSIC, SFX, LVL_MUS_MAP
from scripts.entities.character_presets import Biker, Punk, Cyborg
from scripts.entities.enemy_presets import EnemyOne, EnemyTwo, EnemyThree, EnemyFour, EnemyFive, EnemySix, EnemySeven, \
    EnemyEight
from scripts.menus.state import State
from scripts.utils import load_all_images, load_image, ImageButton
from scripts.world.background import Background
from scripts.world.interactive_map import InteractiveMap
from scripts.world.tilemap import TileMap

CHARACTER = {
    1: Biker,
    2: Punk,
    3: Cyborg
}

ENEMIES = {
    0: EnemyOne,
    1: EnemyTwo,
    2: EnemyThree,
    3: EnemyFour,
    4: EnemyFive,
    5: EnemySix,
    6: EnemySeven,
    7: EnemyEight
}


class Level(State):
    def __init__(self, game):
        super().__init__(game)
        self.alpha = 256
        self.phase = True

        # Level stuff
        self.scroll = [96, 96]
        self.player_bullets = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()

        # Images
        self.images = {
            'bars': load_all_images('assets/sprites/gui/bars'),
            'game over': load_image('assets/sprites/menus/game_over.png'),
            'level complete': load_image('assets/sprites/menus/level_completed.png'),
        }

        # Buttons
        self.buttons = {
            '32x32': ImageButton(pygame.Surface((32, 32), pygame.SRCALPHA)),
        }

        # Load in the data
        self.data = json.load(open(f'levels/level{self.game.level}.json', 'r'))
        self.tileset = self.data['tileset']

        # Overlay
        self.overlay = load_image(f'assets/sprites/tilesets/{self.tileset}/background/overlay.png')
        self.overlay.set_alpha(18)

        # Background
        self.background = Background(game, self)

        # Tilemap
        self.tilemap = TileMap(game, self)

        # Interactive map
        self.interactivemap = InteractiveMap(game, self)

        # Player
        self.player = CHARACTER[self.game.character](game, self, (128 + 96, 320))

        # Enemies
        self.enemies = pygame.sprite.Group()
        for _, value in self.data['enemies'].items():
            pos = value['pos'][0] * 32, value['pos'][1] * 32
            ENEMIES[value['index']](self.game, self, pos, self.enemies)

        # Bosses
        self.boss = None

        self.level_completed = False
        self.slow_time = False  # Here's a cool idea to implement: slow down time by altering delta time

    def update(self):
        # Pause
        if pygame.K_ESCAPE in self.game.key_presses and not self.game.key_down and not self.phase:
            pygame.mixer.music.pause()
            self.game.state = 'pause'
            self.game.key_down = True

        # Camera
        self.scroll_camera()

        # Projectiles
        self.player_bullets.update()

        # Draw background
        self.background.draw()

        # Draw tilemap
        self.tilemap.draw()

        # Draw interactive map
        self.interactivemap.draw()

        # Enemies
        self.enemies.update()

        # Player
        self.player.update()

        # Overlay
        self.game.layers[4].blit(self.overlay, (0, 0))

        # HUD
        self.ux()

        # Level completed by defeating all enemies
        if not self.enemies:
            if not self.level_completed:
                pygame.mixer.music.load(MUSIC['level complete'])
                pygame.mixer.music.play()
                self.game.data['levels completed'] += 1
                self.level_completed = True
            self.level_complete()

        # Player died
        if self.player.dead:
            if not self.level_completed:
                pygame.mixer.music.load(MUSIC['game over'])
                pygame.mixer.music.play()
                self.level_completed = True
            self.game_over()

        # Transition
        self.transition()

    def scroll_camera(self):
        # Camera
        if not self.player.zero_health():
            self.scroll[0] += (self.player.center()[0] - 576 / 2 - self.scroll[0]) * self.game.delta * 6
            self.scroll[1] += (self.player.rect.bottom - 320 / 2 - (self.player.rect.h + 64) - self.scroll[
                1]) * self.game.delta * 6
        if self.scroll[0] < 96:
            self.scroll[0] = 96

    def ux(self):
        # Health bar
        for i in range(math.ceil(self.player.init_hp / 25)):
            self.game.layers[5].blit(self.images['bars'][1], (20 + i * 32, 20))

        for i in range(math.ceil(self.player.hp / 25)):
            self.game.layers[5].blit(self.images['bars'][0], (20 + i * 32, 20))

        # Lives
        lives = self.game.fonts[17].render(f'Lives: {self.player.lives}', True, 'white')
        self.game.layers[5].blit(lives, (576 - 128, 20))

        # Guns
        gun1 = self.player.guns[0]
        text1 = self.game.fonts[15].render(f'{gun1.ammo}/{gun1.mag_size}', True, 'white')
        self.game.layers[5].blit(gun1.gun_images[1], (22, 48))
        self.game.layers[5].blit(text1, (22 + 35, -5 + 48))

        gun2 = self.player.guns[1]
        text2 = self.game.fonts[15].render(f'{gun2.ammo}/{gun2.mag_size}', True, 'white')
        self.game.layers[5].blit(gun2.gun_images[1], (22, 48 + 24))
        self.game.layers[5].blit(text2, (22 + 35, -5 + 48 + 24))

    def level_complete(self):
        self.game.layers[4].blit(self.images['level complete'], (0, 0))
        click = 1 in self.game.mouse_clicks and not self.game.clicked

        # Next
        self.buttons['32x32'].draw(self.game.layers[4], (6 * 32 + 16, 5 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            pygame.mixer.music.load(MUSIC['ambience 2'])
            pygame.mixer.music.play(-1)
            self.game.state = 'select level'
            self.game.clicked = True

        # Restart
        self.buttons['32x32'].draw(self.game.layers[4], (8 * 32 + 16, 5 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.game.set_level()
            self.game.clicked = True

        # Main menu
        self.buttons['32x32'].draw(self.game.layers[4], (10 * 32 + 16, 5 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            pygame.mixer.music.load(MUSIC['ambience 2'])
            pygame.mixer.music.play(-1)
            self.game.state = 'start'
            self.game.clicked = True

    def game_over(self):
        self.game.layers[4].blit(self.images['game over'], (0, 0))
        click = 1 in self.game.mouse_clicks and not self.game.clicked

        self.buttons['32x32'].draw(self.game.layers[4], (7 * 32, 5 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.game.set_level()
            self.game.clicked = True

        self.buttons['32x32'].draw(self.game.layers[4], (10 * 32, 5 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.game.state = 'select level'
            self.game.clicked = True

    def transition(self):
        if self.phase:
            if self.alpha < 120:
                pygame.mixer.music.load(MUSIC[f'music {LVL_MUS_MAP[self.game.level]}'])
                pygame.mixer.music.play(-1)
            self.alpha -= 2
            self.blackout_screen.set_alpha(self.alpha)
            self.game.layers[5].blit(self.blackout_screen, (0, 0))
            if self.alpha <= 0:
                SFX['start'].play()
                self.phase = False
                self.alpha = 255


class LevelCompleted(State):
    def __init__(self, game):
        super().__init__(game)


class GameOver(State):
    def __init__(self, game):
        super().__init__(game)
