import pygame

from scripts.globals import GUN_NAMES


GUN_SHOT_SFX = {
    name: pygame.mixer.Sound(f'assets/audio/sfx/guns/{name}.wav') for name in GUN_NAMES
}

ATTACK_SFX = {
    'punch 1': pygame.mixer.Sound(f'assets/audio/sfx/attack/punch_1.wav'),
    'punch 2': pygame.mixer.Sound(f'assets/audio/sfx/attack/punch_2.wav'),
    'punch 3': pygame.mixer.Sound(f'assets/audio/sfx/attack/punch_3.wav'),
    'metal hit 1': pygame.mixer.Sound(f'assets/audio/sfx/attack/metal_hit_1.wav'),
    'metal hit 2': pygame.mixer.Sound(f'assets/audio/sfx/attack/metal_hit_2.wav'),
    'metal hit 3': pygame.mixer.Sound(f'assets/audio/sfx/attack/metal_hit_3.wav'),
    'metal hit 4': pygame.mixer.Sound(f'assets/audio/sfx/attack/metal_hit_4.wav'),
    'metal whoosh 1': pygame.mixer.Sound(f'assets/audio/sfx/attack/metal_whoosh_1.wav'),
    'metal whoosh 2': pygame.mixer.Sound(f'assets/audio/sfx/attack/metal_whoosh_2.wav'),
    'bite': pygame.mixer.Sound(f'assets/audio/sfx/attack/bite.wav'),
    'thrust up': pygame.mixer.Sound(f'assets/audio/sfx/attack/thrust_up.wav'),
    'smash down': pygame.mixer.Sound(f'assets/audio/sfx/attack/smash_down.wav'),
    'swoosh': pygame.mixer.Sound(f'assets/audio/sfx/attack/swoosh.wav'),
    'gun shot': pygame.mixer.Sound(f'assets/audio/sfx/attack/gun_shot.wav'),
    'laser shot': pygame.mixer.Sound(f'assets/audio/sfx/attack/laser_shot.wav'),
    'laser shot 2': pygame.mixer.Sound(f'assets/audio/sfx/attack/laser_shot_2.wav'),
    'warning beep': pygame.mixer.Sound(f'assets/audio/sfx/attack/warning_beep.wav'),
    'flapping wings': pygame.mixer.Sound(f'assets/audio/sfx/attack/flapping_wings.wav'),
}

DEATH_SFX = {
    'human 1': pygame.mixer.Sound('assets/audio/sfx/death/human_death_1.wav'),
    'human 2': pygame.mixer.Sound('assets/audio/sfx/death/human_death_2.wav'),
    'human 3': pygame.mixer.Sound('assets/audio/sfx/death/human_death_3.wav'),
    'human 4': pygame.mixer.Sound('assets/audio/sfx/death/human_death_4.wav'),
    'human 5': pygame.mixer.Sound('assets/audio/sfx/death/human_death_5.wav'),
    'demoness 1': pygame.mixer.Sound('assets/audio/sfx/death/demoness_1.wav'),
    'demoness 2': pygame.mixer.Sound('assets/audio/sfx/death/demoness_2.wav'),
    'player death': pygame.mixer.Sound('assets/audio/sfx/death/player_death.wav'),
    'robot 1': pygame.mixer.Sound('assets/audio/sfx/death/robot_death_1.wav'),
    'robot 2': pygame.mixer.Sound('assets/audio/sfx/death/robot_death_2.wav'),
    'robot 3': pygame.mixer.Sound('assets/audio/sfx/death/robot_death_3.wav'),
    'robot 4': pygame.mixer.Sound('assets/audio/sfx/death/robot_death_4.wav'),
    'robot 5': pygame.mixer.Sound('assets/audio/sfx/death/robot_death_5.wav'),
    'unique': pygame.mixer.Sound('assets/audio/sfx/death/unique.wav'),
    'zombie 1': pygame.mixer.Sound('assets/audio/sfx/death/zombie_1.wav'),
    'zombie 2': pygame.mixer.Sound('assets/audio/sfx/death/zombie_2.wav'),
}

MISC_SFX = {
    'clip empty': pygame.mixer.Sound(f'assets/audio/sfx/guns/empty_gun_shot.wav'),
    'electroshock': pygame.mixer.Sound('assets/audio/sfx/other/electroshock.wav'),
    'electric shock': pygame.mixer.Sound('assets/audio/sfx/other/electric_shock.wav'),
    'electric': pygame.mixer.Sound('assets/audio/sfx/other/electric.wav'),
    'explosion 1': pygame.mixer.Sound('assets/audio/sfx/other/explosion1.wav'),
    'dash 1': pygame.mixer.Sound('assets/audio/sfx/other/dash_1.wav'),
    'dash 2': pygame.mixer.Sound('assets/audio/sfx/other/dash_2.wav'),
}

MUSIC = {
    'ambience': f'assets/audio/music/ambience.ogg',
    'music 1': f'assets/audio/music/music 1.ogg',
    'music 2': f'assets/audio/music/music 2.ogg',
    'music 3': f'assets/audio/music/music 3.ogg',
    'music 4': f'assets/audio/music/music 4.ogg',
    'music 5': f'assets/audio/music/music 5.ogg',
    'level complete': f'assets/audio/other/level complete.wav',
    'game over': f'assets/audio/other/game over.wav',
}

