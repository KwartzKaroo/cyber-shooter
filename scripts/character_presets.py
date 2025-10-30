import pygame
from scripts.character import Character


class Biker(Character):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (17, 34), pos, 1.9, 125, (-6, -14), '1', ('04', '11'), group)


class Punk(Character):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (15, 34), pos, 2.7, 75, (-7, -14), '2', ('03', '07'), group)


class Cyborg(Character):
    def __init__(self, game, level, pos, group=()):
        super().__init__(game, level, (14, 35), pos, 2.2, 100, (-8, -13), '3', ('06', '09'), group)
