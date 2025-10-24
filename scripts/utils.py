import pygame
from os import walk


def load_image(path):
    return pygame.image.load(path).convert_alpha()

def load_all_images(path):
    images = []
    for root, _, files in walk(path):
        for file in files:
            images.append(load_image(root + '/' + file))
    return images

def cut_sprite_sheet(image, cols=1, size=None):
    images = []
    h = image.get_height()
    w = image.get_width() // cols

    if size is not None:
        w, h = size
        cols = image.get_width() // w

    for i in range(cols):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        area = (i * w, 0, w, h)
        surf.blit(image, (0, 0), area)
        images.append(surf)

    return images

def load_enemy_icons(path, cols=4, size=None):
    images = []
    for root, _, files in walk(path):
        for file in files:
            if file.lower() == 'idle.png':
                image = load_image(root + '/' + file)
                image = cut_sprite_sheet(image, cols, size)
                images.append(image[0])
    return images

def load_pickup_icons(path):
    images = []
    for image in load_all_images(path):
        images.append(cut_sprite_sheet(image, size=(24, 24))[0])
    return images

def debug_rect(surface, rect, scroll=(0, 0), colour='green'):
    if isinstance(rect, pygame.Rect):
        rect = [rect.x - scroll[0], rect.y - scroll[1], rect.w, rect.h]
    else:
        rect = [rect[0] - scroll[0], rect[1] - scroll[1], rect[2], rect[3]]
    pygame.draw.rect(surface, colour, rect, 1)

def debug_info(surface, info, pos, center=False, size=20, text_colour='white', bg_colour='orange'):
    font = pygame.font.SysFont('calibri', size)
    text = font.render(str(info), True, text_colour, bg_colour)
    surf = pygame.Surface((text.get_width() + 2, text.get_height() + 2))
    surf.fill(bg_colour)
    surf.blit(text, (1, 1))

    if center:
        pos = pos[0] - surf.get_width() / 2, pos[1] - surf.get_height() / 2

    surface.blit(surf, pos)


class Animation:
    def __init__(self, image, fps, loop=True, number=1, size=None):
        if isinstance(image, str):
            image = load_image(image)
            
        self.images = cut_sprite_sheet(image, number, size)
        self.fps = fps / 100
        self.loop = loop
        self.frame = 0
        self.finished = False
        
    def get_frame(self):
        return int(self.frame)
    
    def get_image(self):
        return self.images[self.get_frame()]
    
    def reset(self):
        self.frame = 0
        self.finished = False
        
    def update(self, delta):
        self.frame += self.fps * delta
        
        if self.get_frame() > len(self.images) - 1:
            if self.loop:
                self.frame = 0
            else:
                self.finished = True
                self.frame = len(self.images) - 1

    def __len__(self):
        return len(self.images)


class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.active = False
        self.start_time = 0

    def activate(self):
        if not self.active:
            self.start_time = pygame.time.get_ticks()
            self.active = True
    
    def deactivate(self):
        self.start_time = 0
        self.active = False
    
    def update(self):
        if self.active:
            if pygame.time.get_ticks() - self.start_time > self.duration:
                self.deactivate()

    def set_duration(self, duration):
        self.duration = duration

    def __bool__(self):
        return self.active


class ImageButton:
    def __init__(self, image):
        if isinstance(image, str):
            image = load_image(image)

        self.image = image
        self.rect = self.image.get_rect()
        self.draw_pos = [0, 0]

    def draw(self, surface, pos, center=True, offset=(0, 0)):
        rect = self.image.get_rect()
        if center:
            self.rect.center = pos[0], pos[1]
        else:
            self.rect.topleft = pos[0], pos[1]

        self.draw_pos = self.rect.x - offset[0], self.rect.y - offset[1]
        surface.blit(self.image, self.draw_pos)

    def click(self, mouse_rect, clicked):
        return self.rect.colliderect(mouse_rect) and clicked

    def copy(self):
        return ImageButton(self.image)


class CustomButton(ImageButton):
    def __init__(self, btn_size, text, font='calibri', font_size=28, text_colour='yellow', bg_colour='white',
                 bd_width=-1, bd_colour='black'):
        image = pygame.Surface(btn_size)
        image.fill(bg_colour)
        pygame.draw.rect(image, bd_colour, ((0, 0), btn_size), bd_width)

        font = pygame.font.SysFont(font, font_size, True)
        text = font.render(text, True, text_colour)

        center = image.get_rect().center
        image.blit(text, (center[0] - text.get_width() / 2,
                               center[1] - text.get_height() / 2))

        super().__init__(image)
