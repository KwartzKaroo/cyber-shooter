import json

import pygame
import time

from scripts.utils import CustomButton, load_all_images, debug_info, SPECS, Timer, INDEX_TO_DIRECTION, Animation


class Editor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((576 + 320, 320))
        pygame.display.set_caption('Cyber Shooter Gun Editor')
        self.layer = pygame.Surface((576 / 3, 320 / 3))

        # Editor variables
        self.running = True
        self.delta = 0
        self.key_presses = self.held_key_presses = set()
        self.mouse_clicks = self.held_mouse_clicks = set()
        self.key_down = self.clicked = False
        self.mouse_rect = pygame.Rect(0, 0, 4, 4)

        # States
        self.states = {
            'start screen': True,
            'select character': False,
            'edit guns': False,
            'edit offsets': False,
        }

        # Images and data
        self.save_timer = Timer(1000 * 60)
        self.gun_names = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14')
        self.gun_data = {}
        self.gun_images = {}
        self.bullet_images = {}
        self.effect_animations = {}
        self.gun_index = 0
        self.effect_index = 0
        self.shoot = True

        # Gun specific
        self.bullet_offsets = {}
        self.effect_offsets = {}
        self.direction_index = 2
        self.bullet_positions = []
        self.fire_rate = Timer(1000)
        self.fire_rate.activate()

        self.buttons = {
            'offsets': CustomButton((144, 48), 'Offsets', bd_width=4),
            'guns': CustomButton((144, 48), 'Guns', bd_width=4),
            'next': CustomButton((40, 40), '>', bd_width=4),
            'prev': CustomButton((40, 40), '<', bd_width=4),
            'plus': CustomButton((32, 32), '+', bd_width=3),
            'minus': CustomButton((32, 32), '-', bd_width=3),
            'save': CustomButton((160, 48), 'Save', bd_width=4),
        }

    def start_screen(self):
        if pygame.K_ESCAPE in self.key_presses and not self.key_down:
            self.running = False

        self.buttons['offsets'].draw(self.screen, (572 * 1 / 2, 324 * 2 / 6))
        self.buttons['guns'].draw(self.screen, (572 * 1 / 2, 324 * 4 / 6))

        click = 1 in self.mouse_clicks and not self.clicked

    def main(self):
        if pygame.K_ESCAPE in self.key_presses and not self.key_down:
            self.running = False
            self.save()

        self.draw()
        self.edit()
        self.side_panel()

    def draw(self):
        specs = SPECS[self.direction_index]

        gun = self.gun_data[self.gun_names[self.gun_index]]
        gun_image = pygame.transform.rotate(self.gun_images[specs['type']][self.gun_index], specs['angle'])
        bullet_image = pygame.transform.rotate(self.bullet_images[specs['type']][self.gun_index], specs['angle'])
        bullet_offset = self.bullet_offsets[self.gun_names[self.gun_index]][self.direction_index]

        pos = (self.layer.get_width() / 2 - gun_image.get_width() / 2,
               self.layer.get_height() / 2 - gun_image.get_height() / 2)

        if self.fire_rate and self.shoot:
            self.fire_rate.update()
            if not self.fire_rate:
                bullet_pos = [pos[0] + bullet_offset[0], pos[1] + bullet_offset[1]]
                self.bullet_positions.append(bullet_pos)
                self.fire_rate.activate()

        self.layer.blit(gun_image, pos)

        if self.shoot:
            for offset in self.bullet_positions:
                direction = pygame.Vector2(INDEX_TO_DIRECTION[self.direction_index]).normalize()
                offset[0] += gun['bullet_speed'] * direction[0]
                offset[1] += gun['bullet_speed'] * direction[1]
                self.layer.blit(bullet_image, offset)
                if abs(offset[0]) > 600 and abs(offset[1]) > 300:
                    self.bullet_positions.remove(offset)
        else:
            offset = pos[0] + bullet_offset[0], pos[1] + bullet_offset[1]
            self.layer.blit(bullet_image, offset)

    def edit(self):
        click = 1 in self.mouse_clicks and not self.clicked


        self.buttons['prev'].draw(self.screen, (60, 320 * 3 / 4))
        self.buttons['next'].draw(self.screen, (576 - 60, 320 * 3 / 4))

        if self.buttons['prev'].click(self.mouse_rect, click):
            self.gun_index = (self.gun_index - 1) % 14
        if self.buttons['next'].click(self.mouse_rect, click):
            self.gun_index = (self.gun_index + 1) % 14

        if pygame.K_a in self.key_presses:
            self.bullet_offsets[self.gun_names[self.gun_index]][self.direction_index][0] += -1
        if pygame.K_d in self.key_presses:
            self.bullet_offsets[self.gun_names[self.gun_index]][self.direction_index][0] += 1
        if pygame.K_w in self.key_presses:
            self.bullet_offsets[self.gun_names[self.gun_index]][self.direction_index][1] += -1
        if pygame.K_s in self.key_presses:
            self.bullet_offsets[self.gun_names[self.gun_index]][self.direction_index][1] += 1

        if pygame.K_q in self.key_presses:
            self.direction_index = (self.direction_index + 1) % 5
        if pygame.K_e in self.key_presses:
            self.direction_index = (self.direction_index - 1) % 5

        if pygame.K_SPACE in self.key_presses:
            self.shoot = not self.shoot

    def side_panel(self):
        click = 1 in self.mouse_clicks and not self.clicked
        gun = self.gun_data[self.gun_names[self.gun_index]]

        overall = gun['damage'] * (1000 / (1000 - gun['fire_rate']))
        debug_info(self.screen, f'DPS: {round(overall, 2)}', (576 / 2, 40), True, 24)

        # Damage
        self.buttons['minus'].draw(self.screen, (576, 32 + 42 * 0), False)
        if self.buttons['minus'].click(self.mouse_rect, click):
            gun['damage'] = max(5, gun['damage'] - 1)

        self.buttons['plus'].draw(self.screen, (576 + 48, 32 + 42 * 0), False)
        if self.buttons['plus'].click(self.mouse_rect, click):
            gun['damage'] = min(gun['damage'] + 1, 400)

        # Fire rate
        self.buttons['minus'].draw(self.screen, (576, 32 + 42 * 1), False)
        if self.buttons['minus'].click(self.mouse_rect, click):
            gun['fire_rate'] = max(100, gun['fire_rate'] - 10)
            self.fire_rate.duration = 1000 - gun['fire_rate']

        self.buttons['plus'].draw(self.screen, (576 + 48, 32 + 42 * 1), False)
        if self.buttons['plus'].click(self.mouse_rect, click):
            gun['fire_rate'] = min(gun['fire_rate'] + 10, 990)
            self.fire_rate.duration = 1000 - gun['fire_rate']

        # Mag size
        self.buttons['minus'].draw(self.screen, (576, 32 + 42 * 2), False)
        if self.buttons['minus'].click(self.mouse_rect, click):
            gun['mag_size'] = max(5, gun['mag_size'] - 1)

        self.buttons['plus'].draw(self.screen, (576 + 48, 32 + 42 * 2), False)
        if self.buttons['plus'].click(self.mouse_rect, click):
            gun['mag_size'] = min(gun['mag_size'] + 1, 400)

        # Speed
        self.buttons['minus'].draw(self.screen, (576, 32 + 42 * 3), False)
        if self.buttons['minus'].click(self.mouse_rect, click):
            gun['bullet_speed'] = max(4, gun['bullet_speed'] - 1)

        self.buttons['plus'].draw(self.screen, (576 + 48, 32 + 42 * 3), False)
        if self.buttons['plus'].click(self.mouse_rect, click):
            gun['bullet_speed'] = min(gun['bullet_speed'] + 1, 20)

        # Effect
        self.buttons['minus'].draw(self.screen, (576, 32 + 42 * 4), False)
        if self.buttons['minus'].click(self.mouse_rect, click):
            gun['effect'] = max(1, gun['effect'] - 1)

        self.buttons['plus'].draw(self.screen, (576 + 48, 32 + 42 * 4), False)
        if self.buttons['plus'].click(self.mouse_rect, click):
            gun['effect'] = min(gun['effect'] + 1, 4)

        debug_info(self.screen, f'Damage: {gun["damage"]}', (576 + 96, 32 + 42 * 0), size=28, bg_colour='#43b0f0')
        debug_info(self.screen, f'Fire rate: {gun["fire_rate"]}', (576 + 96, 32 + 42 * 1), size=28, bg_colour='#43b0f0')
        debug_info(self.screen, f'Mag size: {gun["mag_size"]}', (576 + 96, 32 + 42 * 2), size=28, bg_colour='#43b0f0')
        debug_info(self.screen, f'Speed: {gun["bullet_speed"]}', (576 + 96, 32 + 42 * 3), size=28, bg_colour='#43b0f0')
        debug_info(self.screen, f'Effect: {gun["effect"]}', (576 + 96, 32 + 42 * 5), size=28, bg_colour='#43b0f0')

    def load_images(self):
        self.gun_images = {
            1: load_all_images('assets/sprites/guns/guns/1'),
            2: load_all_images('assets/sprites/guns/guns/2'),
        }

        self.bullet_images = {
            1: load_all_images('assets/sprites/guns/bullets/1'),
            2: load_all_images('assets/sprites/guns/bullets/2'),
        }

        self.effect_animations = {
            0: Animation('assets/sprites/guns/shoot effects/1/01.png', 6, size=(48, 48))
        }

    def load_data(self):
        for name in self.gun_names:
            self.gun_data[name] = {
                'damage': 5,
                'fire_rate': 100,
                'mag_size': 5,
                'bullet_speed': 4,
                'effect': 1
            }

            self.bullet_offsets[name] = {
                0: [0, 0],
                1: [0, 0],
                2: [0, 0],
                3: [0, 0],
                4: [0, 0],
            }

            self.effect_offsets[name] = {
                0: [0, 0],
                1: [0, 0],
                2: [0, 0],
                3: [0, 0],
                4: [0, 0],
            }

        try:
            self.load()
        except FileNotFoundError:
            print('Create new')

    def load(self):
        with open('data/guns/gun_attributes.json', 'r') as file:
            self.gun_data = json.load(file)

        with open('data/guns/offsets.json', 'r') as file:
            data = json.load(file)
            self.bullet_offsets = data['bullet_offsets']
            self.effect_offsets = data['effect_offsets']

        print('loaded')

    def save(self):
        with open('data/guns/gun_attributes.json', 'w') as file:
            json.dump(self.gun_data, file)

        with open('data/guns/offsets.json', 'w') as file:
            data = {
                'bullet_offsets': self.bullet_offsets,
                'effect_offsets': self.effect_offsets
            }
            json.dump(data, file)

        print('Saved')

    def run(self):
        self.load_images()
        self.load_data()
        prev_time = time.time()
        while self.running:
            # Reset
            self.key_presses = set()
            self.mouse_clicks = set()

            # Event listener
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    self.key_presses.add(event.key)
                    self.held_key_presses.add(event.key)

                if event.type == pygame.KEYUP:
                    self.key_down = False
                    if event.key in self.held_key_presses:
                        self.held_key_presses.remove(event.key)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_clicks.add(event.button)
                    self.held_mouse_clicks.add(event.button)

                if event.type == pygame.MOUSEBUTTONUP:
                    self.clicked = False
                    if event.button in self.held_mouse_clicks:
                        self.held_mouse_clicks.remove(event.button)

                if event.type == pygame.MOUSEMOTION:
                    self.mouse_rect.topleft = event.pos


            # Default screen colour
            self.layer = pygame.Surface((576 / 3, 320 / 3), pygame.SRCALPHA)
            self.screen.fill('#43b0f0')

            self.main()

            self.screen.blit(pygame.transform.scale(self.layer, (576, 320)), (0, 0))

            # Delta time
            self.delta = (time.time() - prev_time) * 66

            # Update screen
            pygame.display.update()


if __name__ == '__main__':
    Editor().run()
    pygame.quit()

