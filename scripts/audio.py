import pygame

from scripts.constants import GUN_NAMES

pygame.mixer.init()

GUN_SHOTS = {
    name: pygame.mixer.Sound(f'assets/audio/gun shots/{name}.mp3') for name in GUN_NAMES
}

MUSIC = {
    'ambience 1': f'assets/audio/music/ambience 1.mp3',
    'ambience 2': f'assets/audio/music/ambience 2.mp3',
    'music 1': f'assets/audio/music/music 1.mp3',
    'music 2': f'assets/audio/music/music 2.mp3',
    'music 3': f'assets/audio/music/music 3.mp3',
    'music 4': f'assets/audio/music/music 4.mp3',
    'music 5': f'assets/audio/music/music 5.mp3',
    'level complete': f'assets/audio/music/level complete.mp3',
    'game over': f'assets/audio/music/game over.mp3',
}

SFX = {
    'start': pygame.mixer.Sound('assets/audio/sfx/lets start.mp3'),
    'explosion': pygame.mixer.Sound('assets/audio/sfx/explosion.mp3'),
    'punch 1': pygame.mixer.Sound('assets/audio/sfx/punch 1.mp3'),
    'body fall': pygame.mixer.Sound('assets/audio/sfx/body fall.mp3'),
    'bullet hit': pygame.mixer.Sound('assets/audio/sfx/bullet hit.mp3'),
    'grunt 1': pygame.mixer.Sound('assets/audio/sfx/grunt 1.mp3'),
    'grunt 2': pygame.mixer.Sound('assets/audio/sfx/grunt 2.mp3'),
    'death 1': pygame.mixer.Sound('assets/audio/sfx/death 1.mp3'),
    'death 2': pygame.mixer.Sound('assets/audio/sfx/death 2.mp3'),
}

LVL_MUS_MAP = {
    1: 2,
    2: 1,
    3: 5,
    4: 3,
    5: 4,
    6: 5,
    7: 4,
    8: 2,
    9: 1,
    10: 3,
    11: 5,
    12: 2,
    13: 1,
    14: 4,
    15: 3,
}
