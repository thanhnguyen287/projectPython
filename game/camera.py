import pygame

class Camera:
    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.scroll = pygame.Vector2(0,0)
        self.dx = 0
        self.dy = 0
        self.speed = 25

    def update(self):

        mouse_pos = pygame.mouse.get_pos()

        #moving in x axis
        if mouse_pos[0] > self.width * 0.95:
            self.dx = -self.speed
        elif mouse_pos[0] < self.width * 0.05:
            self.dx = self.speed
        else:
            self.dx = 0

        #moving in y axis
        if mouse_pos[1] > self.height * 0.97:
            self.dy = -self.speed
        elif mouse_pos[1] < self.height * 0.03:
            self.dy = self.speed
        else:
            self.dy = 0
        # update scroll
        self.scroll.x += self.dx
        self.scroll.y += self.dy