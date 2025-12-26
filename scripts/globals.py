
GRAVITY = .155
FPS = 60
SCREEN_SIZE = 576, 320
TERMINAL_VELOCITY = 8

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

GUN_NAMES = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15')
EFFECTS = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10')
GUNS = {
    '01': {'type': 1, 'bullet type': 'FMJ', 'auto': False},
    '02': {'type': 1, 'bullet type': 'normal', 'auto': False},
    '03': {'type': 1, 'bullet type': 'normal', 'auto': False},
    '04': {'type': 2, 'bullet type': 'normal', 'auto': False},
    '05': {'type': 1, 'bullet type': 'explosive', 'auto': False},
    '06': {'type': 1, 'bullet type': 'electric', 'auto': False},
    '07': {'type': 2, 'bullet type': 'normal', 'auto': True},
    '08': {'type': 2, 'bullet type': 'normal', 'auto': True},
    '09': {'type': 2, 'bullet type': 'normal', 'auto': True},
    '10': {'type': 2, 'bullet type': 'explosive', 'auto': False},
    '11': {'type': 2, 'bullet type': 'FMJ', 'auto': True},
    '12': {'type': 2, 'bullet type': 'normal', 'auto': True},
    '13': {'type': 2, 'bullet type': 'normal', 'auto': False},
    '14': {'type': 2, 'bullet type': 'normal', 'auto': True},
    '15': {'type': 2, 'bullet type': 'electric', 'auto': True},
}
