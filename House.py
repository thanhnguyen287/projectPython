from Buildings import *

class House(Building):
    def __init__(self, x, y):
        super().__init__(x, y)

        #Display
        self.sprite = pygame.image.load("resources/assets/House.png")


