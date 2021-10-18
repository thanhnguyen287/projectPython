import pygame


class Menus:
    def __init__(self, x, y, path):
        self. x = x
        self.y = y
        self.sprite = pygame.image.load(path)

    def display(self, screen):
        screen.blit(self.sprite, (self.x, self.y))