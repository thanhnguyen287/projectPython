import pygame

class Building:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.sprite = pygame.image.load("resources/assets/town_center.png")
        self.image_select = pygame.image.load("resources/assets/image_select.png")
        self.selected = False

    def display(self, screen):
        if self.selected:
            screen.blit(self.image_select, self.get_position_select())
        screen.blit(self.sprite, self.get_position())

    #we return the "real" x and y position to display the building on the map
    def get_position(self):
        return 908+(self.x-self.y)*64, 188+(self.y+self.x)*32

    def get_position_select(self):
        return 894+(self.x-self.y)*64, 202+(self.y+self.x)*32

    def select(self):
        if (self.x, self.y) == self.pos_mouse():
            self.selected = not(self.selected)

    def pos_mouse(self):
        mousex = int(((1 / 2) * pygame.mouse.get_pos()[0] + pygame.mouse.get_pos()[1] - 672) // 64)
        mousey = int((pygame.mouse.get_pos()[1] - (1 / 2) * pygame.mouse.get_pos()[0] + 288) // 64)
        return mousex, mousey



build1 = Building(1, 1)

build2 = Building(7, 8)

buildings = [build1, build2]