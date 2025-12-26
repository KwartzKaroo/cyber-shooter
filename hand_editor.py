import pygame
import time
import pickle

from scripts.utils import TextButton, load_images_folder, debug_info, Animation, debug_rect, Timer
from scripts.globals import SPECS, GUN_NAMES


class Editor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((576, 320))
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
            'main': False,
        }

        # Data
        self.loaded = False
        self.save_timer = Timer(1000 * 60)
        self.save_timer.activate()
        self.frame = 0
        self.auto_play = True
        self.character = 'biker'
        self.rect = None
        self.image_offset = [0, 0]
        self.animations = {}
        self.animation_list = []
        self.animation_index = 0
        self.character_image = None
        self.hand_index = 2
        self.hand_images = {}
        self.gun_images = {}
        self.hand_offsets = {}
        self.edit_hands = True
        self.gun_offsets = {}
        self.gun_type = 1
        self.gun_index = 0

        # Buttons
        self.buttons = {
            'biker': TextButton((160, 48), 'Biker', bd_width=4),
            'punk': TextButton((160, 48), 'Punk', bd_width=4),
            'cyborg': TextButton((160, 48), 'Cyborg', bd_width=4),
            'offsets': TextButton((160, 48), 'Offsets', bd_width=4),
            'next': TextButton((40, 40), '>', bd_width=4),
            'prev': TextButton((40, 40), '<', bd_width=4),
            'left': TextButton((40, 40), '←', bd_width=4),
            'right': TextButton((40, 40), '→', bd_width=4),
            'up': TextButton((40, 40), '↑', bd_width=4),
            'down': TextButton((40, 40), '↓', bd_width=4),
            'save': TextButton((160, 48), 'Save', bd_width=4),
            'type1': TextButton((128, 48), 'Type: 1', bd_width=4),
            'type2': TextButton((128, 48), 'Type: 2', bd_width=4),
            'guns': TextButton((128, 48), 'Guns', bd_width=4),
            'hands': TextButton((128, 48), 'Hands', bd_width=4),
            'auto_on': TextButton((128, 48), 'Auto: On', bd_width=4),
            'auto_off': TextButton((128, 48), 'Auto: Off', font_size=26, bd_width=4),
        }

    def start_screen(self):
        if pygame.K_ESCAPE in self.key_presses and not self.key_down:
            self.running = False

        self.buttons['biker'].draw(self.screen, (572 * 1 / 5, 324 * 1 / 2))
        self.buttons['punk'].draw(self.screen, (572 * 1 / 2, 324 * 1 / 2))
        self.buttons['cyborg'].draw(self.screen, (572 * 4 / 5, 324 * 1 / 2))

        click = 1 in self.mouse_clicks and not self.clicked
        start = False
        if self.buttons['biker'].click(self.mouse_rect, click):
            self.clicked = True
            self.character = 'biker'
            self.rect = pygame.Rect(0, 0, 17, 34)
            self.image_offset = [-6, -14]
            start = True

        if self.buttons['punk'].click(self.mouse_rect, click):
            self.clicked = True
            self.character = 'punk'
            self.rect = pygame.Rect(0, 0, 15, 34)
            self.image_offset = [-7, -14]
            start = True

        if self.buttons['cyborg'].click(self.mouse_rect, click):
            self.clicked = True
            self.character = 'cyborg'
            self.rect = pygame.Rect(0, 0, 14, 35)
            self.image_offset = [-8, -13]
            start = True

        if start:
            self.load_images()
            self.load_data()
            self.rect.center = (self.layer.get_width() // 2, self.layer.get_height() // 2)
            self.states['start screen'] = False
            self.loaded = True

    def main(self):
        if pygame.K_ESCAPE in self.key_presses and not self.key_down:
            self.states['start screen'] = True
            self.loaded = False
            self.save()

        self.draw()
        self.edit()
        self.hud()

    def draw(self):
        animation = self.animations[self.gun_type][self.animation_list[self.animation_index]]
        if self.frame >= len(animation):
            self.frame = 0
        if self.frame < 0:
            self.frame = len(animation) - 1

        if self.auto_play:
            animation.update(self.delta)
            self.frame = animation.get_frame()
        else:
            animation.frame = self.frame

        image = animation.get_image()
        hand_image = self.hand_images[self.gun_type][self.hand_index]

        # Gun
        specs = SPECS[self.hand_index]
        gun_image = pygame.transform.rotate(self.gun_images[specs['type']][self.gun_index], specs['angle'])

        pos = self.rect.topleft
        hand_offset = self.hand_offsets[self.gun_type][self.animation_list[self.animation_index]][self.frame]
        hand_pos = (self.rect.x + hand_offset[0], self.rect.y + hand_offset[1])

        gun_offsets = self.gun_offsets[GUN_NAMES[self.gun_index]][self.hand_index]
        gun_pos = hand_pos[0] + gun_offsets[0], hand_pos[1] + gun_offsets[1]
        debug_rect(self.layer, self.rect)

        if self.gun_type == 1:
            self.layer.blit(hand_image, hand_pos)
            self.layer.blit(gun_image, gun_pos)

        self.layer.blit(image, (pos[0] + self.image_offset[0], pos[1] + self.image_offset[1]))

        if self.gun_type == 2:
            self.layer.blit(gun_image, gun_pos)
            self.layer.blit(hand_image, hand_pos)

    def edit(self):
        click = 1 in self.mouse_clicks and not self.clicked

        # Move pad
        if self.edit_hands:
            offset = self.hand_offsets[self.gun_type][self.animation_list[self.animation_index]][self.frame]
        else:
            offset = self.gun_offsets[GUN_NAMES[self.gun_index]][self.hand_index]


        if pygame.K_d in self.key_presses:
            self.hand_index = (self.hand_index + 1) % 5
        if pygame.K_a in self.key_presses:
            self.hand_index = (self.hand_index - 1) % 5

        if pygame.K_e in self.key_presses:
            self.gun_index = (self.gun_index + 1) % len(GUN_NAMES)
        if pygame.K_q in self.key_presses:
            self.gun_index = (self.gun_index - 1) % len(GUN_NAMES)

        debug_info(self.screen, f'Offset: {offset}', (576 / 2, 320 - 48), True, size=32)
        self.buttons['up'].draw(self.screen, (576 - 96, 320 - 48 * 3))
        if self.buttons['up'].click(self.mouse_rect, click):
            offset[1] += -1
        self.buttons['right'].draw(self.screen, (576 - 48, 320 - 48 * 2))
        if self.buttons['right'].click(self.mouse_rect, click):
            offset[0] += 1
        self.buttons['down'].draw(self.screen, (576 - 96, 320 - 48))
        if self.buttons['down'].click(self.mouse_rect, click):
            offset[1] += 1
        self.buttons['left'].draw(self.screen, (576 - 48 * 3, 320 - 48 * 2))
        if self.buttons['left'].click(self.mouse_rect, click):
            offset[0] += -1

        if self.save_timer:
            self.save_timer.update()
            if not self.save_timer:
                self.save()
                self.save_timer.activate()

    def hud(self):
        click = 1 in self.mouse_clicks and not self.clicked
        # Change animations
        if self.edit_hands:
            debug_info(self.screen, self.animation_list[self.animation_index].capitalize(), (150, 48),
                       True, size=32, bg_colour='#43b0f0')
            self.buttons['left'].draw(self.screen, (48, 48))
            if self.buttons['left'].click(self.mouse_rect, click):
                self.animation_index = (self.animation_index - 1) % 5

            self.buttons['right'].draw(self.screen, (250, 48))
            if self.buttons['right'].click(self.mouse_rect, click):
                self.animation_index = (self.animation_index + 1) % 5
        else:
            debug_info(self.screen, GUN_NAMES[self.gun_index], (150, 48),
                       True, size=32, bg_colour='#43b0f0')
            self.buttons['left'].draw(self.screen, (48, 48))
            if self.buttons['left'].click(self.mouse_rect, click):
                self.gun_index = (self.gun_index - 1) % len(GUN_NAMES)

            self.buttons['right'].draw(self.screen, (250, 48))
            if self.buttons['right'].click(self.mouse_rect, click):
                self.gun_index = (self.gun_index + 1) % len(GUN_NAMES)

        # Auto play
        debug_info(self.screen, f'Frame: {self.frame}', (576 / 2 + 150, 48),
                   True, size=32, bg_colour='#43b0f0')
        if self.auto_play:
            self.buttons['auto_on'].draw(self.screen, (30 + 64, 128 * 1.5))
            if self.buttons['auto_on'].click(self.mouse_rect, click):
                self.clicked = True
                self.auto_play = False
        else:
            self.buttons['auto_off'].draw(self.screen, (30 + 64, 128 * 1.5))
            if self.buttons['auto_off'].click(self.mouse_rect, click):
                self.clicked = True
                self.auto_play = True

            # Control frame
            self.buttons['left'].draw(self.screen, (48 + 288, 48))
            if self.buttons['left'].click(self.mouse_rect, click):
                self.frame -= 1
            self.buttons['right'].draw(self.screen, (250 + 288, 48))
            if self.buttons['right'].click(self.mouse_rect, click):
                self.frame += 1

        # Change type
        if self.gun_type == 1:
            self.buttons['type1'].draw(self.screen, (30 + 64, 128))
            if self.buttons['type1'].click(self.mouse_rect, click):
                self.clicked = True
                self.gun_type = 2
        else:
            self.buttons['type2'].draw(self.screen, (30 + 64, 128))
            if self.buttons['type2'].click(self.mouse_rect, click):
                self.clicked = True
                self.gun_type = 1

        # Change guns/hands
        if self.edit_hands:
            self.buttons['hands'].draw(self.screen, (30 + 64, 128 * 2))
            if self.buttons['hands'].click(self.mouse_rect, click):
                self.clicked = True
                self.edit_hands = False
        else:
            self.buttons['guns'].draw(self.screen, (30 + 64, 128 * 2))
            if self.buttons['guns'].click(self.mouse_rect, click):
                self.clicked = True
                self.edit_hands = True

    def load_images(self):
        self.animations = {
            1: {
                'idle': Animation(f'assets/sprites/characters/{self.character}/idle1.png', 4, size=(48, 48)),
                'jump': Animation(f'assets/sprites/characters/{self.character}/jump1.png', 4, size=(48, 48)),
                'crouch': Animation(f'assets/sprites/characters/{self.character}/crouch1.png', 4, size=(48, 48)),
                'run': Animation(f'assets/sprites/characters/{self.character}/run1.png', 4, size=(48, 48)),
                'walk': Animation(f'assets/sprites/characters/{self.character}/walk1.png', 4, size=(48, 48)),
            },
            2: {
                'idle': Animation(f'assets/sprites/characters/{self.character}/idle2.png', 4, size=(48, 48)),
                'jump': Animation(f'assets/sprites/characters/{self.character}/jump2.png', 4, size=(48, 48)),
                'crouch': Animation(f'assets/sprites/characters/{self.character}/crouch2.png', 4, size=(48, 48)),
                'run': Animation(f'assets/sprites/characters/{self.character}/run2.png', 4, size=(48, 48)),
                'walk': Animation(f'assets/sprites/characters/{self.character}/walk2.png', 4, size=(48, 48)),
            },
        }

        self.hand_images = {
            1: load_images_folder(f'assets/sprites/weapons/hands/{self.character}/1'),
            2: load_images_folder(f'assets/sprites/weapons/hands/{self.character}/2'),
        }

        images = load_images_folder('assets/sprites/weapons/guns')
        self.gun_images = {
            1: [image for x, image in enumerate(images) if x % 2 == 0],
            2: [image for x, image in enumerate(images) if x % 2 == 1],
        }

    def load_data(self):
        self.animation_list = ['idle', 'run', 'jump', 'crouch', 'walk']

        try:
            with open(f'data/hand offsets/{self.character}', 'rb') as file:
                data = pickle.loads(file.read())
                self.hand_offsets = data['hand offsets']
                self.gun_offsets = data['gun offsets']

        except (FileNotFoundError, KeyError):
            self.hand_offsets[1] = {}
            self.hand_offsets[2] = {}

            for action in self.animation_list:
                length = len(self.animations[1][action])
                self.hand_offsets[1][action] = [[0, 0] for _ in range(length)]
                self.hand_offsets[2][action] = [[0, 0] for _ in range(length)]

            for name in GUN_NAMES:
                self.gun_offsets[name] = {
                    0: [0, 0],
                    1: [0, 0],
                    2: [0, 0],
                    3: [0, 0],
                    4: [0, 0],
                }

    def save(self):
        with open(f'data/hand offsets/{self.character}', 'wb') as file:
            data = {
                'hand offsets': self.hand_offsets,
                'gun offsets': self.gun_offsets,
            }
            file.write(pickle.dumps(data))
            print('Saved')

    def run(self):
        prev_time = time.time()
        while self.running:
            # Reset
            self.key_presses = set()
            self.mouse_clicks = set()

            # Event listener
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.loaded:
                        self.save()
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

            if self.states['start screen']:
                self.start_screen()
            else:
                self.main()
                self.screen.blit(pygame.transform.scale(self.layer, (576, 320)), (0, 0))


            # Delta time
            current_time = time.time()
            self.delta = current_time - prev_time
            prev_time = current_time

            # Update screen
            pygame.display.update()


if __name__ == '__main__':
    Editor().run()
    pygame.quit()
