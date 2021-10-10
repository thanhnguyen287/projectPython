from Buildings import *
from villager import *

class Townhall(Building):
    def __init__(self, x, y):
        super().__init__(x, y)

        #Display modified
        self.sprite = pygame.image.load("resources/assets/town_center.png")
        self.image_select = pygame.image.load("resources/assets/image_select_medium.png")

    def display_life(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.get_position()[0] + 60, self.get_position()[1] - 15, self.current_health * 1, 10))
        pygame.draw.rect(screen, (25, 25, 25),(self.get_position()[0] + 60, self.get_position()[1] - 15, self.max_health * 1, 10), 4)

    #modified methods for the 2*2 tiles building (the townhall)
    def get_position(self):
        return 854 + (self.x - self.y) * 64, 170 + (self.y + self.x) * 32

    def get_position_select(self):
        return 830+(self.x-self.y)*64, 202+(self.y+self.x)*32

    def select(self):
        if self.x <= self.pos_mouse()[0] <= self.x+1 and self.y <= self.pos_mouse()[1] <= self.y+1:
            self.selected = not self.selected

    def create_villager(self):
        #TODO : change the condition to take in consideration the amount of food and the max pop the player has
        if(1):
            return Villager(928+(self.x-self.y)*64, 154+(self.y+self.x+4)*32, playerOne)




town1 = Townhall(5, 5)