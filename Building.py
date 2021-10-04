import pygame

class Building:
    def __init__(self, path):
        self.image = pygame.image.load(path)

    def display(self, screen, x, y):
        #affichage de la sprite aux bonnes coordonnées
        screen.blit(self.image, (x, y))

build = Building("resources/assets/rock.png")
