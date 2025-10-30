import pygame


class State:
    def __init__(self, game):
        self.game = game
        self.phase = False
        self.alpha = 1000
        self.blackout_screen = pygame.Surface((576, 320), pygame.SRCALPHA)
        self.blackout_screen.fill('black')
        self.blackout_screen.set_alpha(28)

    def update(self):
        pass

    def transition(self):
        pass

