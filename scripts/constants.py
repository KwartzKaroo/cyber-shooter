# This file contains# Constants
SPECS = {
    # Hand direction
    (0, 1): {'image': 1, 'angle': -90},
    (1, 1): {'image': 2, 'angle': 0},
    (1, 0): {'image': 1, 'angle': 0},
    (1, -1): {'image': 2, 'angle': 90},
    (0, -1): {'image': 1, 'angle': 90},

    # Index
    0: {'type': 1, 'angle': -90},
    1: {'type': 2, 'angle': 0},
    2: {'type': 1, 'angle': 0},
    3: {'type': 2, 'angle': 90},
    4: {'type': 1, 'angle': 90},
}

INDEX_TO_DIRECTION = {
    0: (0, 1),
    1: (1, 1),
    2: (1, 0),
    3: (1, -1),
    4: (0, -1),
}

DIRECTION_TO_INDEX = {
    (0, 1): 0,
    (1, 1): 1,
    (1, 0): 2,
    (1, -1): 3,
    (0, -1): 4
}


GUN_NAMES = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14')


GUNS = {
    '01': {'type': 1, 'dmg': 25, 'speed': 7, 'fire rate': 580, 'mag size': 40, 'bullet type': 1, 'auto': False}, # 59
    '02': {'type': 1, 'dmg': 30, 'speed': 7, 'fire rate': 600, 'mag size': 40, 'bullet type': 1, 'auto': False}, # 75
    '03': {'type': 1, 'dmg': 36, 'speed': 10, 'fire rate': 540, 'mag size': 60, 'bullet type': 1, 'auto': False}, # 78.26
    '04': {'type': 1, 'dmg': 18, 'speed': 7, 'fire rate': 830, 'mag size': 100, 'bullet type': 1, 'auto': False}, # 105.88
    '05': {'type': 2, 'dmg': 125, 'speed': 7, 'fire rate': 400, 'mag size': 10, 'bullet type': 1, 'auto': False}, # 208.33
    '06': {'type': 1, 'dmg': 40, 'speed': 7, 'fire rate': 640, 'mag size': 30, 'bullet type': 1, 'auto': False},  # 111.11
    '07': {'type': 2, 'dmg': 26, 'speed': 7, 'fire rate': 800, 'mag size': 190, 'bullet type': 1, 'auto': True},  # 130.00
    '08': {'type': 2, 'dmg': 15, 'speed': 7, 'fire rate': 900, 'mag size': 150, 'bullet type': 1, 'auto': True},  # 150.00
    '09': {'type': 2, 'dmg': 24, 'speed': 7, 'fire rate': 880, 'mag size': 120, 'bullet type': 1, 'auto': True},  # 200.00
    '10': {'type': 2, 'dmg': 320, 'speed': 7, 'fire rate': 200, 'mag size': 5, 'bullet type': 1, 'auto': False},  # 400.00
    '11': {'type': 2, 'dmg': 28, 'speed': 7, 'fire rate': 830, 'mag size': 210, 'bullet type': 1, 'auto': True},  # 164.71
    '12': {'type': 2, 'dmg': 180, 'speed': 10, 'fire rate': 400, 'mag size': 10, 'bullet type': 1, 'auto': False},  # 300.00
    '13': {'type': 2, 'dmg': 24, 'speed': 7.5, 'fire rate': 940, 'mag size': 100, 'bullet type': 1, 'auto': True}, # 400.00
    '14': {'type': 2, 'dmg': 80, 'speed': 7, 'fire rate': 680, 'mag size': 15, 'bullet type': 1, 'auto': True},  # 250.00
}

