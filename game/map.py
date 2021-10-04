import pygame
from settings import *
import os



class Map:
    def __init__(self , grid_length_x, grid_length_y, width, height):
        self.grid_length_x = grid_length_x
        self.grid_length_y = grid_length_y
        self.width = width
        self.height = height
        self.map = self.create_map()
        self.tiles = self.load_images()
    def create_map(self):
        map = []

        for grid_x in range(self.grid_length_x):
            map.append([])
            for grid_y in range(self.grid_length_y):
                map_tile = self.grid_to_map(grid_x,grid_y)
                map[grid_x].append(map_tile)
        return map


    def grid_to_map(self, grid_x, grid_y):
        rect = [
            (grid_x * TILE_SIZE, grid_y * TILE_SIZE),
            (grid_x * TILE_SIZE + TILE_SIZE, grid_y * TILE_SIZE),
            (grid_x * TILE_SIZE + TILE_SIZE, grid_y * TILE_SIZE + TILE_SIZE),
            (grid_x * TILE_SIZE, grid_y * TILE_SIZE + TILE_SIZE)
        ]


#polygon
        iso_poly = [self.decarte_to_iso(x, y) for x, y in rect]

        minx = min([x for x, y in iso_poly])
        miny = min([y for x, y in iso_poly])

        out = {
            "grid": [grid_x, grid_y],
            "drect": rect,
            "iso_poly": iso_poly,
            "render_pos": [minx, miny]
        }

        return out

    def decarte_to_iso(self, x, y):
        iso_x = x - y
        iso_y = (x + y)/2
        return iso_x, iso_y

    def load_images(self):

       #block = pygame.image.load(os.path.join(assets_path, "block.png"))
        block = pygame.image.load("resources/assets/block.png")
        tree = pygame.image.load("resources/assets/block.png")
        rock = pygame.image.load("resources/assets/block.png")

        return {"block": block, "tree": tree, "rock": rock}