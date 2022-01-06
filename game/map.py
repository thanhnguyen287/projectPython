<<<<<<< Updated upstream
import pygame
import os
=======
import copy
import random
import noise
import pygame.mouse
from .utils import decarte_to_iso, iso_to_decarte, get_color_code, str_to_entity_class
>>>>>>> Stashed changes
from settings import *
import os
import random
#import noise


class Map:
    def __init__(self , grid_length_x, grid_length_y, width, height):
        self.grid_length_x = grid_length_x
        self.grid_length_y = grid_length_y
        self.width = width
        self.height = height

        self.perlin_scale = grid_length_x/2

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
<<<<<<< Updated upstream


#polygon
        iso_poly = [self.decarte_to_iso(x, y) for x, y in rect]

=======
        # polygon
        iso_poly = [decarte_to_iso(x, y) for x, y in rect]
        iso_poly_minimap = copy.deepcopy(iso_poly)
>>>>>>> Stashed changes
        minx = min([x for x, y in iso_poly])
        miny = min([y for x, y in iso_poly])

        r = random.randint(1,100)
        if r <= 10 :
            tile = "rock"
        elif r <= 30:
            tile = "tree"
        else:
            tile = ""

        #perlin = noise.

        out = {
            "grid": [grid_x, grid_y],
            "drect": rect,
            "iso_poly": iso_poly,
            "render_pos": [minx, miny],
<<<<<<< Updated upstream
            "tile": tile
=======
            "tile": tile,
            "collision": False if tile == "" else True,
            "max_health": 10,
            "health": 10,
            "iso_poly_minimap": iso_poly_minimap
>>>>>>> Stashed changes
        }

        return out

    def decarte_to_iso(self, x, y):
        iso_x = x - y
        iso_y = (x + y)/2
        return iso_x, iso_y

    def load_images(self):

       #block = pygame.image.load(os.path.join(assets_path, "block.png"))
        block = pygame.image.load(os.path.join(assets_path, "block.png")).convert_alpha()
        tree = pygame.image.load(os.path.join(assets_path,"tree.png")).convert_alpha()
        rock = pygame.image.load(os.path.join(assets_path,"rock.png")).convert_alpha()

<<<<<<< Updated upstream
        return {"block": block, "tree": tree, "rock": rock}
=======
                self.highlight_tile(x, y, screen, "BLACK", scroll)

    def draw_minimap(self, screen, camera):
        '''Draw a minimap so you dont get lost. Moving it to HUD or
        Camera is highly recommended, draw the polygon once so increase
        FPS. '''
        minimap_scaling = 16
        for x in range(self.grid_length_x):
            for y in range(self.grid_length_y):
                #Draw polygon
                mini = self.map[x][y]["iso_poly_minimap"]
                mini = [((x + self.width / 2) / minimap_scaling + 1640,
                         (y + self.height / 4) / minimap_scaling + 820) for x, y in mini]  # position x + ...., y  + ...
                pygame.draw.polygon(screen, "WHITE", mini, 1)

                #Draw small dot representing entities
                render_pos = self.map[x][y]["render_pos"]
                tile = self.map[x][y]["tile"]

                if tile == "tree":
                    # pygame.draw.circle(screen, "GREEN", (render_pos[0]/minimap_scaling + 1640, render_pos[1]/minimap_scaling+820), 1)
                    pygame.draw.circle(screen, "GREEN", (mini[1][0], mini[1][1]),1)
                elif tile == "rock":
                    pygame.draw.circle(screen, "BlACK", (mini[1][0], mini[1][1]), 1)
                elif tile == "gold":
                    pygame.draw.circle(screen, "YELLOW",(mini[1][0], mini[1][1]), 1)

>>>>>>> Stashed changes
