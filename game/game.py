import pygame
import sys
from .map import Map
from settings import *
import os



class Game:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.width, self.height = self.screen.get_size()
        self.map = Map(10,10, self.width, self.height)

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(60)
            self.events()
            self.update()
            self.draw()

    def events(self):
        #quit game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Quit to menu screen instead maybe
                    pygame.quit()
                    sys.exit()

    def update(self):
        # Build later
        pass

    def draw(self):
        self.screen.fill((0,0,0))

        for x in range(self.map.grid_length_x):
            for y in range(self.map.grid_length_y):
                square = self.map.map[x][y]["drect"]
                rect = pygame.Rect(square[0][0], square[0][1], TILE_SIZE,TILE_SIZE)
                pygame.draw.rect(self.screen, (0,255,255),rect,1)
                #pygame.draw.rect(surface, color, rect, width...)

                render_pos = self.map.map[x][y]["render_pos"]
                self.screen.blit(self.map.tiles["block"], (render_pos[0] + self.width/2, render_pos[1]+self.height/4 ))

                p = self.map.map[x][y]["iso_poly"]
                p = [(x+self.width/2, y + self.height/4) for x, y in p]
                pygame.draw.polygon(self.screen, (255,255,255), p, 1)

        pygame.display.flip()


