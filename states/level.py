import math

import pygame
import json
from datetime import timedelta

from scripts.audio import MUSIC, MISC_SFX
from scripts.camera import Camera
from scripts.globals import SCREEN_SIZE, FPS
from scripts.tilemap import TileMap
from scripts.background import Background
from scripts.item_map import ItemMap
from scripts.character import Biker, Punk, Cyborg
from scripts.enemies import Batsman, Pistolerro, GroundDrone, CyberHound, DockWorker, ExplosiveBot, Zapper, Demoness, Zombie
from scripts.bosses import SportsMan, Tank, Mech, Vampire, TheScientist
from scripts.utils import Timer, load_image, InvisibleButton

CHARACTER = {
    1: Biker,
    2: Punk,
    3: Cyborg
}


ENEMIES = {
    1: Batsman,
    2: Pistolerro,
    3: GroundDrone,
    4: CyberHound,
    5: DockWorker,
    6: ExplosiveBot,
    7: Zapper,
    8: Demoness,
    9: Zombie
}


BOSSES = {
    1: SportsMan,
    2: Tank,
    3: Mech,
    4: Vampire,
    5: TheScientist
}


class Level:
    def __init__(self, game, state_manager):
        self.game = game
        self.state_manager = state_manager
        self.screen = pygame.display.get_surface()

        # Level stuff
        self.camera = Camera()
        self.canvases = {i: pygame.Surface(self.screen.get_size()) for i in range(1, 7)}

        # Images
        self.images = {
            'hp bar': load_image('assets/sprites/gui/hp_bar.png'),
            'hp bar dark': load_image('assets/sprites/gui/hp_bar_dark.png'),
            'game over menu': load_image('assets/sprites/menus/game_over.png'),
            'level complete menu': load_image('assets/sprites/menus/level_completed.png'),
        }

        # Buttons
        self.buttons = {
            '32x32': InvisibleButton((32, 32)),
        }

        # Groups
        self.player_bullets = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.boss = pygame.sprite.GroupSingle()

        # Load data from file
        loaded_data = json.loads(open(f'levels/level{self.state_manager.selected_level}.json').read())

        # Text from level data
        self.texts = []
        for pos, text in loaded_data['text']:
            ttt = self.game.fonts[17].render(text, True, '#111111')
            self.texts.append((pos, ttt))

        # Background
        self.background = Background(loaded_data['tileset'], 'day')

        # Tile map
        self.tilemap = TileMap(self, loaded_data)

        # Items
        self.item_map = ItemMap(self, loaded_data)

        # Player
        self.player = CHARACTER[self.game.character](self, (252, 210))

        # Enemies
        for value in loaded_data['data']['enemies'].values():
            ENEMIES[value['index'] + 1](self, value['pos'])

        # Boss
        for value in loaded_data['data']['bosses'].values():
            self.boss = BOSSES[value['index'] + 1](self, value['pos'])

        # Start level timer
        self.level_timer = Timer(1000 * 60 * 8)
        self.level_timer.activate()
        self.level_completed = False

        # When player meets the boss
        self.boss_fight = False
        self.boundaries = [0, 0]

        # Music
        pygame.mixer.music.load(MUSIC[f'music {self.state_manager.selected_level}'])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.counter = 0

    def main(self):
        # Update camera
        if not self.player.off_map:
            self.camera.scroll(self.player, 24)

        # Canvases
        self.canvases = {i: pygame.Surface(self.screen.get_size(), pygame.SRCALPHA) for i in range(1, 7)}

        # Background
        self.background.draw(self.canvases[1], self.camera)

        # Update tilemap
        self.tilemap.draw()

        # Update item map
        self.item_map.draw()

        # Text goes here
        for pos, text in self.texts:
            self.canvases[3].blit(text, (pos[0] - self.camera.x - 6 * 32, pos[1] - self.camera.y))

        # Projectiles
        self.player_bullets.update()
        self.enemy_projectiles.update()

        # Enemies
        self.enemies.update()

        # Bosses
        self.boss.update()

        # Check if boss is on screen
        if self.camera.on_screen(self.boss, 64) and not self.boss_fight:
            self.boundaries = [self.camera.x - 32, self.camera.right + 32]
            self.boss_fight = True
            self.player.lives = 2
            self.camera.bounds['left'] = self.boundaries[0]
            self.camera.bounds['right'] = self.boundaries[1]
            self.player.respawn_point = [self.camera.x + 32, self.player.rect.bottom - self.player.rect.h]

        # The player
        self.player.update()

        # Draw everything
        for layer in self.canvases.values():
            self.screen.blit(layer, (0, 0))

    def hud(self):
        # Health bar
        for i in range(math.ceil(self.player.init_hp / 10)):
            self.screen.blit(self.images['hp bar dark'], (20 + i * 32, 20))

        for i in range(math.ceil(self.player.hp / 10)):
            self.screen.blit(self.images['hp bar'], (20 + i * 32, 20))

        # Lives
        lives = self.game.fonts[17].render(f'Lives left: {self.player.lives}', True, 'white')
        self.screen.blit(lives, (576 - lives.get_width() - 48, 20))

        # Level timer
        time_delta = str(timedelta(milliseconds=self.level_timer.get_time_left()))
        timer_text = self.game.fonts[17].render(time_delta[2:7], True, 'white')
        self.screen.blit(timer_text, (SCREEN_SIZE[0] / 2 - timer_text.get_width() / 2, 20))

        # Guns
        gun1 = self.player.guns[0]
        text1 = self.game.fonts[15].render(f'{gun1.ammo}/{gun1.mag_size}', True, 'white')
        self.screen.blit(gun1.gun_images[1], (22, 48))
        self.screen.blit(text1, (22 + 35, -5 + 48))

        gun2 = self.player.guns[1]
        text2 = self.game.fonts[15].render(f'{gun2.ammo}/{gun2.mag_size}', True, 'white')
        self.screen.blit(gun2.gun_images[1], (22, 48 + 24))
        self.screen.blit(text2, (22 + 35, -5 + 48 + 24))

    def level_complete(self):
        if not self.level_completed:
            pygame.mixer.music.load(MUSIC['level complete'])
            pygame.mixer.music.play()
            if self.state_manager.selected_level == self.game.data['levels completed']:
                self.game.data['levels completed'] += 1
            self.level_completed = True

        self.screen.blit(self.images['level complete menu'], (0, 0))
        click = 1 in self.game.mouse_clicks and not self.game.mouse_button_down

        # Next
        self.buttons['32x32'].set_pos((6 * 32 + 16, 5 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            if self.state_manager.selected_level == 5:
                self.state_manager.change_state('select level')
            else:
                self.state_manager.selected_level += 1
                self.state_manager.set_level()
            self.game.mouse_button_down = True

        # Restart
        self.buttons['32x32'].set_pos((8 * 32 + 16, 5 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.state_manager.set_level()
            self.game.mouse_button_down = True

        # Select level
        self.buttons['32x32'].set_pos((10 * 32 + 16, 5 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            pygame.mixer.music.load(MUSIC['ambience'])
            pygame.mixer.music.play(-1)
            self.state_manager.change_state('select level')
            self.game.mouse_button_down = True

    def game_over(self):
        if not self.level_completed:
            pygame.mixer.music.load(MUSIC['game over'])
            pygame.mixer.music.play()
            self.level_completed = True

        self.screen.blit(self.images['game over menu'], (0, 0))
        click = 1 in self.game.mouse_clicks and not self.game.mouse_button_down

        self.buttons['32x32'].set_pos((7 * 32, 5 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.state_manager.set_level()
            self.game.mouse_button_down = True

        self.buttons['32x32'].set_pos((10 * 32, 5 * 32), False)
        if self.buttons['32x32'].click(self.game.mouse_rect, click):
            self.game.state = 'select level'
            self.game.mouse_button_down = True

    def transition(self):
        if self.state_manager.phase:
            self.state_manager.alpha -= 2 * self.game.delta * FPS
            self.state_manager.blackout_screen.set_alpha(int(self.state_manager.alpha))
            self.screen.blit(self.state_manager.blackout_screen, (0, 0))
            if self.state_manager.alpha <= 0:
                self.state_manager.phase = False
                self.state_manager.alpha = 0

    def update(self):
        # Pause
        if pygame.K_ESCAPE in self.game.key_presses and not (
                self.game.key_down or self.state_manager.phase or self.level_completed or self.player.dead):
            pygame.mixer.music.pause()
            self.state_manager.change_state('pause')
            self.game.key_down = True

        # Main stuff
        self.main()

        # HUD
        self.hud()

        # Level completed by defeating the boss
        if self.boss_fight and self.boss.dead:
            self.level_complete()

        # Player died
        if self.player.dead or not self.level_timer:
            self.game_over()

        # Countdown the time
        self.level_timer.update()
        if not self.level_timer:
            self.player.dead = True

        # Transition
        self.transition()


