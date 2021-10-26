import random
import noise
import pygame.mouse
from player import players
from settings import *


class Map:
    def __init__(self, hud, grid_length_x, grid_length_y, width, height):
        self.hud = hud
        self.grid_length_x = grid_length_x
        self.grid_length_y = grid_length_y
        self.width = width
        self.height = height

        # anything >1 or <-1, otherwise pnoise will return 0
        self.perlin_scale = grid_length_x/2

        self.grass_tiles = pygame.Surface((grid_length_x * TILE_SIZE * 2, grid_length_y * TILE_SIZE + 2 * TILE_SIZE)).convert_alpha()
        self.tiles = self.load_images()
        # Set this at the most bottom line of this __init__
        self.map = self.create_map()

        #used when selecting a tile to build
        self.temp_tile = None

    def create_map(self):
        map = []

        for grid_x in range(self.grid_length_x):
            map.append([])
            for grid_y in range(self.grid_length_y):
                map_tile = self.grid_to_map(grid_x,grid_y)
                map[grid_x].append(map_tile)

                render_pos = map_tile["render_pos"]

                # self.grass_tiles.getwidth()/2 : offset
                self.grass_tiles.blit(self.tiles["block"],  (render_pos[0] + self.grass_tiles.get_width() / 2, render_pos[1]))

        return map

    def update(self, camera):
        mouse_pos = pygame.mouse.get_pos()
        mouse_action = pygame.mouse.get_pressed()
        self.temp_tile = None

        # meaning : the player selected a building in the hud
        if self.hud.selected_tile is not None:
            grid_pos = self.mouse_to_grid(mouse_pos[0], mouse_pos[1], camera.scroll)

            # if we can't place the building on the tile, there's no need to do the following
            if self.can_place_tile(grid_pos):
                image = self.hud.selected_tile["image"].copy()
                # setting transparency to make sure player understands it's not built
                image.set_alpha(100)

                render_pos = self.map[grid_pos[0]][grid_pos[1]]["render_pos"]
                iso_poly = self.map[grid_pos[0]][grid_pos[1]]["iso_poly"]

                collision = self.map[grid_pos[0]][grid_pos[1]]["collision"]

                self.temp_tile = {
                    "image": image,
                    "render_pos": render_pos,
                    "iso_poly": iso_poly,
                    "collision": collision
                }

                #if we left_click to build : we place the temp tile in the map
                if mouse_action[0] and not collision:
                    self.map[grid_pos[0]][grid_pos[1]]["tile"] = self.hud.selected_tile["name"]
                    self.map[grid_pos[0]][grid_pos[1]]["collision"] = True
                    self.hud.selected_tile = None

    def draw(self, screen, camera):
        # Rendering "block", as Surface grass_tiles is in the same dimension of screen so just add (0,0)
        screen.blit(self.grass_tiles, (camera.scroll.x, camera.scroll.y))

        # FOR THE MAP
        for x in range(self.grid_length_x):
            for y in range(self.grid_length_y):
                render_pos = self.map[x][y]["render_pos"]

                # Rendering what's on the map, if it is not a tree or rock then render nothing as we already had block with green grass
                tile = self.map[x][y]["tile"]
                if tile != "":
                    screen.blit(self.tiles[tile],
                                     (
                                         render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                                         render_pos[1] - (self.tiles[tile].get_height() - TILE_SIZE) + camera.scroll.y
                                     )
                    )

        # display the potential building on the tile
        if self.temp_tile is not None:
            iso_poly = self.temp_tile["iso_poly"]
            iso_poly = [(x + self.grass_tiles.get_width()/2 + camera.scroll.x, y + camera.scroll.y) for x, y in iso_poly]

            # if we cannot place our building on the tile because there's already smth, we display the tile in red, else, in green
            if self.temp_tile["collision"]:
                pygame.draw.polygon(screen, (255, 0, 0), iso_poly, 3)
            else:
                pygame.draw.polygon(screen, (0, 255, 0), iso_poly, 3)

            render_pos = self.temp_tile["render_pos"]
            screen.blit(self.temp_tile["image"],
                (   # we obviously have to reapply the offset + camera scroll
                    render_pos[0] + self.grass_tiles.get_width()/2 + camera.scroll.x,
                    render_pos[1] - (self.temp_tile["image"].get_height() - TILE_SIZE) + camera.scroll.y
                )
            )

        # RESOURCES_BAR DISPLAY
        for a_player in players:
            if a_player.is_human:
                a_player.update_ressources_bar(screen)


        # # units display
        # # for a_unit in units_group:
        # #     if a_unit.is_alive:
        # #         a_unit.display(self.screen)
        # #
        # #         #health bar display
        # #         if ENABLE_HEALTH_BARS:
        # #             a_unit.display_life(self.screen)
        #


    def load_images(self):

        block = pygame.image.load(os.path.join(assets_path, "block.png")).convert_alpha()
        tree = pygame.image.load(os.path.join(assets_path, "tree.png")).convert_alpha()
        rock = pygame.image.load(os.path.join(assets_path, "rock.png")).convert_alpha()
        grass_tile = pygame.image.load(os.path.join(assets_path, "20001_02.png")).convert_alpha()

        building1 = pygame.image.load("Resources/assets/town_center.png").convert_alpha()
        building2 = pygame.image.load("Resources/assets/House_sprite.png").convert_alpha()

        images = {
            "building1": building1,
            "building2": building2,
            "tree" : tree,
            "rock" : rock,
            "block" : block,
            "grass_tile" : grass_tile
        }

        return images

    # this function returns the isometric picture coordinates corresponding to a grid_tile
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
            "tile": tile,
            "collision" : False if tile == "" else True
        }

        return out

    def decarte_to_iso(self, x, y):
        iso_x = x - y
        iso_y = (x + y)/2
        return iso_x, iso_y

    # From the mouse coordinates, we find the corresponding tile of our map (=grid position).
    # Almost does the "opposite" work of grid_to_map
    # x and y : position of mouse
    def mouse_to_grid(self, mouse_x, mouse_y, scroll):

        # 1 : we remove the camera scroll and the offset (for x) to get the corresponding map position
        map_x = mouse_x - scroll.x - self.grass_tiles.get_width() / 2
        map_y = mouse_y - scroll.y

        # 2 : we remove the isometric transformation to find cartesian coordinates
        # opposite of decarte_to_iso function
        cart_y = (2 * map_y - map_x) / 2
        cart_x = cart_y + map_x

        # 3 : find the grid coordinates (we must get integers to make sense)
        grid_x = int(cart_x // TILE_SIZE)
        grid_y = int(cart_y // TILE_SIZE)

        return grid_x, grid_y

    # to check if we are able to place an object (collision)
    def can_place_tile(self, grid_pos):
        mouse_on_panel = False

        #we check if it is on the hud
        for rect in [self.hud.build_rect, self.hud.select_rect]:
            if rect.collidepoint(pygame.mouse.get_pos()):
                mouse_on_panel = True

        # we check it is not outside the map
        map_bounds = (0 <= grid_pos[0] <= self.grid_length_x) and (0 <= grid_pos[1] <= self.grid_length_y)

        # if we are in the map and not on a hud, we can place it
        if map_bounds and not mouse_on_panel:
            return True
        else:
            return False
