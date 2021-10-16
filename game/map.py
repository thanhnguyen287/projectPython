import pygame
import os
import noise
from settings import *
import os
import random




class Map:
    def __init__(self , grid_length_x, grid_length_y, width, height):
        self.grid_length_x = grid_length_x
        self.grid_length_y = grid_length_y
        self.width = width
        self.height = height

        self.perlin_scale = grid_length_x/2  #anything >1 or <-1, otherwise pnoise will return 0

        self.grass_tiles = pygame.Surface((grid_length_x * TILE_SIZE * 2 ,grid_length_y * TILE_SIZE + 2 * TILE_SIZE)).convert_alpha()
        self.tiles = self.load_images()
        self.map = self.create_map() #Set this at the most bottom line of this __init__

    def create_map(self):
        map = []

        for grid_x in range(self.grid_length_x):
            map.append([])
            for grid_y in range(self.grid_length_y):
                map_tile = self.grid_to_map(grid_x,grid_y)
                map[grid_x].append(map_tile)

                render_pos = map_tile["render_pos"]
                self.grass_tiles.blit(self.tiles["block"],  (render_pos[0] + self.grass_tiles.get_width()/2, render_pos[1]))

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

        r = random.randint(1,100)
        perlin = 100 * noise.pnoise2(grid_x / self.perlin_scale, grid_y / self.perlin_scale)

        if (perlin >=15) or (perlin<=-35):
            tile = "tree"
        else:
            if r <= 1 :
                tile = "rock"
            elif r <= 2:
                tile = "tree"
            else:
                tile = ""

        #perlin = noise.

        out = {
            "grid": [grid_x, grid_y],
            "drect": rect,
            "iso_poly": iso_poly,
            "render_pos": [minx, miny],
            "tile": tile
        }

        return out

    def decarte_to_iso(self, x, y):
        iso_x = x - y
        iso_y = (x + y)/2
        return iso_x, iso_y

    def load_images(self):


        block = pygame.image.load(os.path.join(assets_path, "block.png")).convert_alpha()
        tree = pygame.image.load(os.path.join(assets_path,"tree.png")).convert_alpha()
        rock = pygame.image.load(os.path.join(assets_path,"rock.png")).convert_alpha()

        return {"block": block, "tree": tree, "rock": rock}
