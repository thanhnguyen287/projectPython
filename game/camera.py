import pygame
from settings import TILE_SIZE
from math import sqrt
class Camera:
    def __init__(self, width, height, map):
    # def __init__(self, width, height):

        self.width = width
        self.height = height
        self.map = map
        self.scroll = pygame.Vector2(0, 0)
        self.dx = 0
        self.dy = 0
        self.speed = 25
        # self.limit = [self.map.grid_length_x, self.map.grid_length_y]
        self.limit = [60*TILE_SIZE/2, 68*TILE_SIZE/4] #this is the polygon's arcgis length

    def update(self):

        mouse_pos = pygame.mouse.get_pos()
## Boundery, If it get too laggy due to many if-condition check, revert to the old one by uncommenting these code

        # # moving in x axis
        # if mouse_pos[0] > self.width * 0.97:
        #     self.dx = -self.speed
        # elif mouse_pos[0] < self.width * 0.03:
        #     self.dx = self.speed
        # else:
        #     self.dx = 0
        #
        # # moving in y axis
        # if mouse_pos[1] > self.height * 0.97:
        #     self.dy = -self.speed
        # elif mouse_pos[1] < self.height * 0.03:
        #     self.dy = self.speed
        # else:
        #     self.dy = 0

        #moving in x axis
        if self.scroll.x + self.width < self.limit[0]:
            if mouse_pos[0] > self.width * 0.97:
                self.dx = -self.speed
                self.scroll.x += self.dx
            elif mouse_pos[0] < self.width * 0.03:
                self.dx = self.speed
                self.scroll.x += self.dx
            # else:
            #     self.dx = 0
        else:
            if mouse_pos[0] > self.width * 0.97:
                self.dx = -self.speed
                self.scroll.x += self.dx
            # else:
            #     self.dx = 0

        #moving in y axis
        if self.scroll.y + self.height < self.limit[1]:
            if mouse_pos[1] > self.height * 0.97:
                self.dy = -self.speed
                self.scroll.y += self.dy
            elif mouse_pos[1] < self.height * 0.03:
                self.dy = self.speed
                self.scroll.y += self.dy
            # else:
            #     self.dy = 0
        else:
            if mouse_pos[1] > self.height * 0.97:
                self.dy = -self.speed
                self.scroll.y += self.dy
            # else:
            #     self.dy = 0
        # update scroll


