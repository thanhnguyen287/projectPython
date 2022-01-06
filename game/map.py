import copy
import random
import noise
import pygame.mouse
from .utils import *
from settings import *
# from buildings import Farm, TownCenter, House, Building
from player import playerOne, player_list
from units import Villager, Unit, Farm, TownCenter, House, Building


class Map:
    def __init__(self, hud, entities, grid_length_x, grid_length_y, width, height):
        self.hud = hud
        self.entities = entities
        self.grid_length_x = grid_length_x
        self.grid_length_y = grid_length_y
        self.width = width
        self.height = height
        # anything >1 or <-1, otherwise pnoise will return 0
        self.perlin_scale = grid_length_x / 2
        self.grass_tiles = pygame.Surface(
            (grid_length_x * TILE_SIZE * 2, grid_length_y * TILE_SIZE + 2 * TILE_SIZE)).convert_alpha()
        self.tiles = self.load_images()
        # lists of lists
        self.buildings = [[None for x in range(self.grid_length_x)] for y in range(self.grid_length_y)]
        self.units = [[None for x in range(self.grid_length_x)] for y in range(self.grid_length_y)]
        self.map = self.create_map()
        # used in the fonction that places the townhall randomly on the map
        self.townhall_placed = False
        self.place_x = 0
        self.place_y = 0
        # here we place the townhall randomly on the map
        self.place_townhall()
        self.collision_matrix = self.create_collision_matrix()
        # new_villager = Villager((0, 0), playerOne, self.map)
        # self.units[0][0] = new_villager
        # used when selecting a tile to build
        self.temp_tile = None
        # used when examining elements of the map
        self.examined_tile = None
        # starting unit
        start_unit = Villager(self.map[5][5]["grid"], playerOne, self)

        # we add the unit we created to the list of units of the player
        playerOne.unit_list.append(start_unit)
        playerOne.unit_occupied.append(0)

        self.units[5][5] = start_unit
        playerOne.pay_entity_cost_bis(Villager)
        self.collision_matrix[start_unit.pos[1]][start_unit.pos[0]] = 0
        self.map[start_unit.pos[0]][start_unit.pos[1]]["collision"] = True

    def create_map(self):
        map = []
        for grid_x in range(self.grid_length_x):
            map.append([])
            for grid_y in range(self.grid_length_y):
                map_tile = self.grid_to_map(grid_x, grid_y)
                map[grid_x].append(map_tile)
                render_pos = map_tile["render_pos"]
                # self.grass_tiles.getwidth()/2 : offset
                self.grass_tiles.blit(self.tiles["grass"],
                                      (render_pos[0] + self.grass_tiles.get_width() / 2, render_pos[1]))
                scroll = pygame.Vector2(0, 0)
                scroll.x = 0
                scroll.y = 0
        return map

    def update(self, camera, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_action = pygame.mouse.get_pressed()
        self.temp_tile = None

        # the player selects a building in the hud
        if self.hud.selected_tile is not None and self.hud.examined_tile is not None:
            grid_pos = self.mouse_to_grid(mouse_pos[0], mouse_pos[1], camera.scroll)
            # if we can't place the building on the tile, there's no need to do the following

            if self.can_place_tile(grid_pos):
                if self.hud.examined_tile.name == "Villager":
                    self.hud.bottom_left_menu = self.hud.villager_menu
                elif self.hud.examined_tile.name == "Town Center":
                    self.hud.bottom_left_menu = self.hud.town_hall_menu

                image = self.hud.selected_tile["image"].copy()
                name = self.hud.selected_tile["name"]
                # setting transparency to make sure player understands it's not built
                image.set_alpha(100)
                collision = None
                if grid_pos[0] < self.grid_length_x and grid_pos[1] < self.grid_length_y:
                    render_pos = self.map[grid_pos[0]][grid_pos[1]]["render_pos"]
                    iso_poly = self.map[grid_pos[0]][grid_pos[1]]["iso_poly"]
                    collision = self.is_there_collision(grid_pos)

                    self.temp_tile = {
                        "name": name,
                        "image": image,
                        "render_pos": render_pos,
                        "iso_poly": iso_poly,
                        "collision": collision
                    }

                else:
                    pass
                # if we left_click to build : the villager goes to an adjacent tile and the building is created
                if mouse_action[0] and not collision:
                    working_villager = self.hud.examined_tile
                    if self.get_empty_adjacent_tiles(grid_pos):
                        villager_dest = self.get_empty_adjacent_tiles(grid_pos)[0]
                        working_villager.move_to(self.map[villager_dest[0]][villager_dest[1]])
                        working_villager.is_moving_to_build = True
                    # we store the future building information inside building_to_create
                    if self.hud.selected_tile["name"] == "Farm" or self.hud.selected_tile["name"] == "House" or self.hud.selected_tile["name"] == "TownCenter":
                        working_villager.building_to_create = {"name": self.hud.selected_tile["name"], "pos": grid_pos}
                    self.hud.selected_tile = None

        # the player hasn't selected something to build, he will interact with what's on the map
        else:
            grid_pos = self.mouse_to_grid(mouse_pos[0], mouse_pos[1], camera.scroll)
            if grid_pos[0] < self.grid_length_x - 1 and grid_pos[1] < self.grid_length_y - 1:
                # we deselect the object examined when left-clicking if not on hud
                town_center_check_condition = (self.buildings[grid_pos[0]][grid_pos[1] + 1] and type(self.buildings[grid_pos[0]][grid_pos[1] + 1]) == TownCenter ) \
                    or (self.buildings[grid_pos[0] - 1][grid_pos[1] + 1] and type(
                            self.buildings[grid_pos[0] - 1][grid_pos[1] + 1]) == TownCenter) or (self.buildings[grid_pos[0] - 1][grid_pos[1]] and type(
                            self.buildings[grid_pos[0] - 1][grid_pos[1]]) == TownCenter)

                if mouse_action[0] and not self.is_there_collision(
                        grid_pos) and not self.hud.bottom_hud_rect.collidepoint(mouse_pos) and not town_center_check_condition:


                    self.examined_tile = None
                    self.hud.examined_tile = None
                    self.hud.bottom_left_menu = None
            # if on the map and left click and the tile isn't empty, we display the bottom hud menu (different depending of the unit/building)
            if self.can_place_tile(grid_pos):
                if grid_pos[0] < self.grid_length_x and grid_pos[1] < self.grid_length_y:
                    building = self.buildings[grid_pos[0]][grid_pos[1]]
                    unit = self.units[grid_pos[0]][grid_pos[1]]
                    if mouse_action[0]:
                        self.examined_tile = grid_pos
                        if building is not None:
                            self.hud.examined_tile = building
                            if type(building) == TownCenter:
                                self.hud.bottom_left_menu = self.hud.town_hall_menu
                            else:
                                self.hud.bottom_left_menu = None

                        elif unit is not None:
                            self.hud.examined_tile = unit
                            if type(unit) == Villager:
                                self.hud.bottom_left_menu = self.hud.villager_menu
                            else:
                                self.hud.bottom_left_menu = None

                        else:
                            if grid_pos[1] + 1 < self.grid_length_y:
                                building = self.buildings[grid_pos[0]][grid_pos[1] + 1]
                            if building and type(building) == TownCenter:
                                self.hud.examined_tile = building
                                self.examined_tile = (grid_pos[0], grid_pos[1] + 1)
                                self.hud.bottom_left_menu = self.hud.town_hall_menu
                            elif self.buildings[grid_pos[0] - 1][grid_pos[1] + 1] and type(self.buildings[grid_pos[0] - 1][grid_pos[1] + 1]) == TownCenter:
                                self.hud.examined_tile = self.buildings[grid_pos[0] - 1][grid_pos[1] + 1]
                                self.examined_tile = (grid_pos[0] - 1, grid_pos[1] + 1)
                                self.hud.bottom_left_menu = self.hud.town_hall_menu
                            elif self.buildings[grid_pos[0] - 1][grid_pos[1]] and type(self.buildings[grid_pos[0] - 1][grid_pos[1]]) == TownCenter:
                                self.hud.examined_tile = self.buildings[grid_pos[0] - 1][grid_pos[1]]
                                self.examined_tile = (grid_pos[0] - 1, grid_pos[1])
                                self.hud.bottom_left_menu = self.hud.town_hall_menu

                else:
                    pass

        # right click, gathering and moving units (fighting in future)
        if mouse_action[2] and 0 <= grid_pos[0] <= 50 and 0 <= grid_pos[1] <= 50:

            # There is a bug with collecting ressources on the side of the map !!!

            if self.hud.examined_tile is not None and self.hud.examined_tile.name == "Villager":
                villager_pos = self.hud.examined_tile.pos
                this_villager = self.units[villager_pos[0]][villager_pos[1]]
                pos_mouse = self.mouse_to_grid(mouse_pos[0], mouse_pos[1], camera.scroll)
                pos_x = pos_mouse[0]
                pos_y = pos_mouse[1]
                # ATTACK
                if self.units[pos_x][pos_y] is not None or self.buildings[pos_x][pos_y] is not None:
                    #si les deux unites sont adjacentes:
                    target_to_attack = self.units[pos_x][pos_y] if self.units[pos_x][pos_y] is not None else self.buildings[pos_x][pos_y]
                    this_villager.target = target_to_attack

                    if this_villager.is_adjacent_to(target_to_attack):
                        this_villager.is_fighting = True
                    else:
                        this_villager_dest = self.get_empty_adjacent_tiles((pos_x, pos_y))[0]
                        this_villager.move_to(self.map[this_villager_dest[0]][this_villager_dest[1]])
                        this_villager.is_moving_to_attack = True

                # ONLY MOVEMENT
                if not self.map[grid_pos[0]][grid_pos[1]]["collision"] and \
                        not this_villager.is_gathering and this_villager.target is None:
                    this_villager.move_to(self.map[grid_pos[0]][grid_pos[1]])

                # we check if the tile we right click on is a ressource and if its on an adjacent tile of the villager pos, and if the villager isnt moving
                # if the tile next to him is a ressource and we right click on it and he is not moving, he will gather it
                if not this_villager.searching_for_path \
                        and (self.map[pos_x][pos_y]["tile"] in ["tree", "rock", "gold", "berrybush"]):

                    this_villager.go_to_ressource((pos_x, pos_y))
                    print("go to")

    def draw(self, screen, camera):
        # Rendering "block", as Surface grass_tiles is in the same dimension of screen so just add (0,0)
        screen.blit(self.grass_tiles, (camera.scroll.x, camera.scroll.y))
        # display grid
        #self.show_grid(camera.scroll, screen)
        # FOR THE MAP


        for x in range(self.grid_length_x):
            for y in range(self.grid_length_y):
                render_pos = self.map[x][y]["render_pos"]

                # HERE WE DRAW THE MAP TILES
                # Rendering what's on the map, if it is not a tree or rock then render nothing as we already had block with green grass
                tile = self.map[x][y]["tile"]



                # if the tile isnt empty and inst destroyed, we display it. All resources have slightly different models to add variety
                if tile != "" and tile != "building":
                    screen.blit(self.hud.resources_sprites[tile][str(self.map[x][y]["variation"])], (
                        render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                        render_pos[1] - (self.tiles[tile].get_height() - TILE_SIZE) + camera.scroll.y)
                                )

                    # here we display the health bar of the ressources
                    if (self.examined_tile is not None and x == self.examined_tile[0] and y == self.examined_tile[1]) \
                            or self.map[x][y]["health"] != self.map[x][y]["max_health"]:
                        self.hud.display_life_bar(screen, self.map[x][y], self, camera=camera, for_hud=False, for_resource=True)

                # HERE WE DRAW THE UNITS ON THE MAP
                # we extract from the units list the unit we want to display
                unit = self.units[x][y]
                if unit is not None and unit.current_health <= 0:
                    self.remove_entity(unit)
                if unit is not None:
                    # have we selected this unit ? if yes we will highlight its tile
                    if self.examined_tile is not None:
                        if (x == self.examined_tile[0]) and (y == self.examined_tile[1]):
                            self.highlight_tile(self.examined_tile[0], self.examined_tile[1], screen, "WHITE",
                                                camera.scroll)
                    if unit.target is not None:
                        target = unit.map.map[unit.target[0]][unit.target[1]]
                    if unit.is_fighting or unit.is_moving_to_fight:
                        # target highlighted in dark red
                        self.highlight_tile(target.pos[0], target.pos[1], screen, "DARK_RED", camera.scroll)
                    elif unit.is_gathering or unit.is_moving_to_gather:
                        self.highlight_tile(target["grid"][0], target["grid"][1], screen, "GREEN", camera.scroll)

                    if type(unit) == Villager:
                        # draw future buildings
                        if unit.building_to_create is not None:
                            future_building = unit.building_to_create
                            future_building_render_pos = self.grid_to_renderpos(future_building["pos"][0],
                                                                                future_building["pos"][1])
                            self.hud.display_building(screen, future_building, camera.scroll, future_building_render_pos,
                                                      is_hypothetical_building=True, is_build_possibility_display=True)
                            #future_building_sprite = self.hud.display_building(screen, future_building, camera.scroll, render_pos, is_hypothetical_building=True, is_build_possibility_display=True)

                            #future_building_sprite.set_alpha(100)
                           # screen.blit(future_building_sprite, (
                            #    future_building_render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                            #    future_building_render_pos[1] - (
                            #            future_building_sprite.get_height() - TILE_SIZE) + camera.scroll.y)
                             #           )

                    screen.blit(unit.sprite, (
                        render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                        render_pos[1] - (unit.sprite.get_height() - TILE_SIZE) + camera.scroll.y)
                                )
                    if unit.searching_for_path:
                        # creates a flag to display where the unit is going
                        screen.blit(destination_flag, (
                            unit.dest["render_pos"][0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                            unit.dest["render_pos"][1] - (destination_flag.get_height() - TILE_SIZE) + camera.scroll.y)
                                    )

        # temp tile is a dictionary containing name + image + render pos + iso_poly + collision
        if self.temp_tile is not None:
            render_pos = self.temp_tile["render_pos"]
            grid = self.renderpos_to_grid(render_pos[0], render_pos[1])

            # if we cannot place our building on the tile because there's already smth, we display the tile in red, else, in green
            # For towncenter, we have to display a 2x2 green/Red case, else we only need to highlight a 1x1 case
            if self.temp_tile["name"] == "TownCenter":
                # collision matrix : 0 if collision, else 1, we check the 4 cases of the town center
                if self.temp_tile["collision"] or self.collision_matrix[grid[1]][grid[0] + 1] == 0 or \
                        self.collision_matrix[grid[1] - 1][grid[0] + 1] == 0 or self.collision_matrix[grid[1] - 1][
                    grid[0]] == 0:
                    self.highlight_tile(grid[0], grid[1] - 1, screen, "RED", camera.scroll, multiple_tiles_tiles_flag=True)
                else:
                    self.highlight_tile(grid[0], grid[1] - 1, screen, "GREEN", camera.scroll, multiple_tiles_tiles_flag=True)

            # for normal buildings (1x1)
            else:
                if self.temp_tile["collision"]:
                    self.highlight_tile(grid[0], grid[1], screen, "RED", camera.scroll)
                else:
                    self.highlight_tile(grid[0], grid[1], screen, "GREEN", camera.scroll)

            # display the buildable building on the tile
            self.hud.display_building(screen, self.temp_tile, camera.scroll, render_pos, is_hypothetical_building=True)

        #building display
        for player in player_list:
            for building in player.building_list:
                if building.current_health <= 0:
                    self.remove_entity(building)

                 #have we clicked on this tile ? if yes we will highlight the building
                if self.examined_tile is not None:
                    if not building.is_being_built:
                        if (building.pos[0] == self.examined_tile[0]) and (building.pos[1] == self.examined_tile[1]):
                            if type(building) != TownCenter:
                                self.highlight_tile(building.pos[0], building.pos[1], screen, "WHITE",
                                    camera.scroll)
                            else:
                                self.highlight_tile(building.pos[0], building.pos[1] - 1, screen, "WHITE",
                                    camera.scroll, multiple_tiles_tiles_flag=True)
                self.hud.display_building(screen, building, camera.scroll,
                                          self.grid_to_renderpos(building.pos[0], building.pos[1]))
                if building.current_health != building.max_health:
                    self.hud.display_life_bar(screen, building, self, for_hud=False, camera=camera)

    def load_images(self):
        block = pygame.image.load(os.path.join(assets_path, "block.png")).convert_alpha()
        tree = pygame.image.load("Resources/assets/Models/Map/Trees/1.png").convert_alpha()
        rock = pygame.image.load(os.path.join("Resources/assets/Models/Map/Stones/7.png")).convert_alpha()
        grass_tile = scale_image(pygame.image.load("Resources/assets/Models/Map/grass_01.png").convert_alpha(), w=132)
        grass_hd = pygame.image.load(os.path.join(assets_path, "12.png")).convert_alpha()
        gold = pygame.image.load(os.path.join("Resources/assets/Models/Map/Gold/4.png")).convert_alpha()
        berrybush = pygame.image.load(os.path.join("Resources/assets/Models/Map/Berrybush/1.png")).convert_alpha()

        town_center = pygame.image.load("Resources/assets/Models/Buildings/Town_Center/town_center_x1.png").convert_alpha()
        house = pygame.image.load("Resources/assets/Models/Buildings/House/house_1.png").convert_alpha()
        farm = pygame.image.load("Resources/assets/Models/Buildings/Farm/farm.png").convert_alpha()
        villager = pygame.image.load("resources/assets/Villager.bmp").convert_alpha()

        images = {
            "TownCenter": town_center,
            "House": house,
            "Farm": farm,
            "tree": tree,
            "rock": rock,
            "block": block,
            "grass": grass_tile,
            "grass_hd": grass_hd,
            "gold": gold,
            "berrybush": berrybush,
            "Villager": villager
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
        # polygon
        iso_poly = [decarte_to_iso(x, y) for x, y in rect]
        iso_poly_minimap = copy.deepcopy(iso_poly)
        minx = min([x for x, y in iso_poly])
        miny = min([y for x, y in iso_poly])
        r = random.randint(1, 100)
        perlin = 100 * noise.pnoise2(grid_x / self.perlin_scale, grid_y / self.perlin_scale)
        # variation is to have different models of the same resources, to add variety
        variation = 0
        if (perlin >= 15) or (perlin <= -35):
            tile = "tree"
            variation = random.randint(1, 4)
        else:
            if r <= 1:
                tile = "rock"
                variation = random.randint(1, 7)
            elif r <= 2:
                tile = "tree"
                variation = random.randint(1, 4)
            elif r <= 3:
                tile = "gold"
                variation = random.randint(1, 7)
            elif r == 4:
                tile = "berrybush"
                variation = random.randint(1, 3)

            else:
                tile = ""

        # perlin = noise.
        out = {
            "grid": [grid_x, grid_y],
            "drect": rect,
            "iso_poly": iso_poly,
            "render_pos": [minx, miny],
            "tile": tile,
            "collision": False if tile == "" else True,
            "max_health": 10,
            "health": 10,
            "variation": variation if tile != "" else 0,
            "iso_poly_minimap": iso_poly_minimap
        }
        return out

    # From the mouse coordinates, we find the corresponding tile of our map (=grid position).
    # Almost does the "opposite" work of grid_to_map
    # x and y : position of mouse
    def mouse_to_grid(self, mouse_x, mouse_y, scroll):
        # 1 : we remove the camera scroll and the offset (for x) to get the corresponding map position
        iso_x = mouse_x - scroll.x - self.grass_tiles.get_width() / 2
        iso_y = mouse_y - scroll.y
        # 2 : we remove the isometric transformation to find cartesian coordinates
        cart_x, cart_y = iso_to_decarte(iso_x, iso_y)
        # 3 : find the grid coordinates (we must get integers to make sense)
        grid_x = int(cart_x // TILE_SIZE)
        grid_y = int(cart_y // TILE_SIZE)
        return grid_x, grid_y

    def renderpos_to_grid(self, x, y):
        # 2 : we remove the isometric transformation to find cartesian coordinates
        cart_x, cart_y = iso_to_decarte(x, y)
        # 3 : find the grid coordinates (we must get integers to make sense)
        grid_x = int(cart_x // TILE_SIZE)
        grid_y = int(cart_y // TILE_SIZE)
        return grid_x + 1, grid_y

    def grid_to_renderpos(self, grid_x, grid_y):
        rect = [
            (grid_x * TILE_SIZE, grid_y * TILE_SIZE),
            (grid_x * TILE_SIZE + TILE_SIZE, grid_y * TILE_SIZE),
            (grid_x * TILE_SIZE + TILE_SIZE, grid_y * TILE_SIZE + TILE_SIZE),
            (grid_x * TILE_SIZE, grid_y * TILE_SIZE + TILE_SIZE)
        ]
        # polygon
        iso_poly = [decarte_to_iso(x, y) for x, y in rect]
        minx = min([x for x, y in iso_poly])
        miny = min([y for x, y in iso_poly])
        render_pos = [minx, miny]
        return render_pos

    def grid_to_iso_poly(self, grid_x, grid_y):
        rect = [
            (grid_x * TILE_SIZE, grid_y * TILE_SIZE),
            (grid_x * TILE_SIZE + TILE_SIZE, grid_y * TILE_SIZE),
            (grid_x * TILE_SIZE + TILE_SIZE, grid_y * TILE_SIZE + TILE_SIZE),
            (grid_x * TILE_SIZE, grid_y * TILE_SIZE + TILE_SIZE)
        ]
        # polygon
        iso_poly = [decarte_to_iso(x, y) for x, y in rect]
        return iso_poly

    # takes tile "matrice" coordinates, returns center of tile
    def get_tile_center(self, tile_x, tile_y, scroll):
        top_left_corner = (tile_x * TILE_SIZE, tile_y * TILE_SIZE)
        bottom_left_corner = (tile_x * TILE_SIZE + TILE_SIZE, tile_y * TILE_SIZE)
        top_right_corner = (tile_x * TILE_SIZE, tile_y * TILE_SIZE + TILE_SIZE)
        bottom_right_corner = (tile_x * TILE_SIZE + TILE_SIZE, tile_y * TILE_SIZE + TILE_SIZE)
        tile_center_x = tile_x + (TILE_SIZE / 2)
        tile_center_y = tile_y + (TILE_SIZE / 2)
        tile_center_x, tile_center_y = decarte_to_iso(tile_center_x, tile_center_y)
        tile_center_x = tile_center_x + scroll.x + (self.grass_tiles.get_width() * 2)
        # tile_center_x = tile_center_x + scroll.x
        tile_center_y = tile_center_y + scroll.y
        return tile_center_x, tile_center_y

    def get_2x2_iso_poly(self, bottom_left_tile_x, bottom_left_tile_y, scroll):

        top_left_corner = (bottom_left_tile_x * TILE_SIZE, bottom_left_tile_y * TILE_SIZE)
        bottom_left_corner = (bottom_left_tile_x * TILE_SIZE + TILE_SIZE * 2, bottom_left_tile_y * TILE_SIZE)
        bottom_right_corner = (
            bottom_left_tile_x * TILE_SIZE + TILE_SIZE * 2, bottom_left_tile_y * TILE_SIZE + TILE_SIZE * 2)
        top_right_corner = (bottom_left_tile_x * TILE_SIZE, bottom_left_tile_y * TILE_SIZE + TILE_SIZE * 2)

        rect = [top_left_corner, bottom_left_corner, bottom_right_corner, top_right_corner]

        # polygon
        iso_poly = [decarte_to_iso(x, y) for x, y in rect]
        iso_poly = [(x + self.grass_tiles.get_width() / 2 + scroll.x, y + scroll.y) for x, y in
                    iso_poly]

        return iso_poly

    # to check if we are able to place an object (collision)
    def can_place_tile(self, grid_pos):
        mouse_on_panel = False
        # we check if it is on the hud
        if self.hud.bottom_hud_rect.collidepoint(pygame.mouse.get_pos()):
            mouse_on_panel = True
        # we check it is not outside the map
        map_bounds = (0 <= grid_pos[0] <= self.grid_length_x) and (0 <= grid_pos[1] <= self.grid_length_y)
        # if we are in the map and not on a hud, we can place it
        if map_bounds and not mouse_on_panel:
            return True
        else:
            return False

    # matrix of 1 and 0, will be used for pathfinding
    # 1 : possible tile
    # 0 : there's already something : collision
    # because of the implementation of the pathfinding package, this matrix can't mirror the map grid and needs to be inverted
    def create_collision_matrix(self):
        # at first, we initialise our matrix with 1 : this means you can go everywhere
        collision_matrix = [[1 for x in range(self.grid_length_x)] for y in range(self.grid_length_y)]
        for x in range(self.grid_length_x):
            for y in range(self.grid_length_y):
                # we iterate through our tiles, if there's something, we put a 0 in our collision matrix
                if self.map[x][y]["collision"]:
                    collision_matrix[y][x] = 0
        return collision_matrix


    # here is the fonction that places the townhall randomly on the map
    def place_townhall(self):
        while not self.townhall_placed:
            place_x = random.randint(0, self.grid_length_x - 2)
            place_y = random.randint(1, self.grid_length_y - 1)

            self.place_x = place_x
            self.place_y = place_y

            new_building = TownCenter((place_x, place_y), self, playerOne)
            new_building.is_being_built = False
            new_building.construction_progress = 100
            new_building.current_health = new_building.max_health
            self.entities.append(new_building)
            self.buildings[place_x][place_y] = new_building

            self.townhall_placed = True

            playerOne.towncenter_pos = (place_x, place_y)

            self.map[place_x][place_y]["tile"] = "building"
            self.map[place_x][place_y]["collision"] = True
            self.map[place_x + 1][place_y]["tile"] = "building"
            self.map[place_x + 1][place_y]["collision"] = True
            self.map[place_x][place_y - 1]["tile"] = "building"
            self.map[place_x][place_y - 1]["collision"] = True
            self.map[place_x + 1][place_y - 1]["tile"] = "building"
            self.map[place_x + 1][place_y - 1]["collision"] = True

    def remove_entity(self, entity):
        if issubclass(type(entity), Building):
            if type(entity) != TownCenter:
                self.buildings[entity.pos[0]][entity.pos[1]] = None
                self.buildings[entity.pos[0] + 1][entity.pos[1]] = None
                self.buildings[entity.pos[0]][entity.pos[1] - 1] = None
                self.buildings[entity.pos[0] + 1][entity.pos[1] - 1] = None
                self.collision_matrix[entity.pos[1]][entity.pos[0]] = 1
                self.collision_matrix[entity.pos[1]][entity.pos[0] + 1] = 1
                self.collision_matrix[entity.pos[1] - 1][entity.pos[0] + 1] = 1
                self.collision_matrix[entity.pos[1] - 1][entity.pos[0]] = 1
            else:
                self.buildings[entity.pos[0]][entity.pos[1]] = None
                self.collision_matrix[entity.pos[1]][entity.pos[0]] = 1
        elif issubclass(type(entity), Unit):
            self.units[entity.pos[0]][entity.pos[1]] = None
            self.collision_matrix[entity.pos[1]][entity.pos[0]] = 1
        self.examined_tile = None
        self.hud.examined_tile = None

    # returns true if there is collision, else False
    def is_there_collision(self, grid_pos: [int, int]):
        return True if self.collision_matrix[grid_pos[1]][grid_pos[0]] == 0 else False

    # return a list of empty tiles around origin
    def get_empty_adjacent_tiles(self, origin_pos: [int, int], origin_size=1):
        empty_adj_tiles = []
        checked_tile = ()
        if origin_size == 1:
            # we check the tiles around the origin tile (rectangular shape)
            for x in range(origin_pos[0] - 1, origin_pos[0] + 2):
                for y in range(origin_pos[1] - 1, origin_pos[1] + 2):
                    checked_tile = (x, y)
                    if self.can_place_tile(checked_tile) and not self.is_there_collision(checked_tile):
                        empty_adj_tiles.append(checked_tile)

        elif origin_size == 2:
            ...
        else:
            ...
        return empty_adj_tiles

    #Outline in white the image. Can be used to show an entity is selected...
    def highlight_image(self, image, screen, render_pos, scroll, color="WHITE"):
        #transform color name to color code
        color = get_color_code(color)
        # outline in white the object selected with mask feature
        mask = pygame.mask.from_surface(image).outline()
        mask = [(x + render_pos[0] + self.grass_tiles.get_width() / 2 + scroll.x,
                 y + render_pos[1] - (
                         image.get_height() - TILE_SIZE) + scroll.y)
                for x, y in mask]
        pygame.draw.polygon(screen, color, mask, 3)

    def highlight_tile(self, grid_x, grid_y, screen, color, scroll, multiple_tiles_tiles_flag=False):
        #we have to highlight 1 tile
        if not multiple_tiles_tiles_flag:
            iso_poly = self.grid_to_iso_poly(grid_x, grid_y)
            iso_poly = [
                (x + self.grass_tiles.get_width() / 2 + scroll.x, y + scroll.y)
                for x, y in iso_poly]
        # for more than 1 tile. For now, only 2x2 highlight is supported.
        else:
            iso_poly = self.get_2x2_iso_poly(grid_x, grid_y, scroll)

        pygame.draw.polygon(screen, get_color_code(color), iso_poly, 3)

    #LAG A LOT DON'T TELL ME I HAVENT WARNED YOU
    def show_grid(self, scroll, screen):
        for x in range(self.grid_length_x):
            for y in range(self.grid_length_y):
                # HERE WE DRAW THE MAP TILES
                # Rendering what's on the map, if it is not a tree or rock then render nothing as we already had block with green grass

                self.highlight_tile(x, y, screen, "BLACK", scroll)

    def draw_minimap(self, screen, camera):
        '''Draw a minimap so you dont get lost. Moving it to HUD or
        Camera is highly recommended, draw the polygon once so increase
        FPS. '''
        minimap_scaling = 16
        for x in range(self.grid_length_x):
            for y in range(self.grid_length_y):
                # Draw polygon
                mini = self.map[x][y]["iso_poly_minimap"]
                mini = [((x + self.width / 2) / minimap_scaling + 1640,
                         (y + self.height / 4) / minimap_scaling + 820) for x, y in mini]  # position x + ...., y  + ...
                pygame.draw.polygon(screen, "WHITE", mini, 1)

                # Draw small dot representing entities
                render_pos = self.map[x][y]["render_pos"]
                tile = self.map[x][y]["tile"]

                if tile == "tree":
                    # pygame.draw.circle(screen, "GREEN", (render_pos[0]/minimap_scaling + 1640, render_pos[1]/minimap_scaling+820), 1)
                    pygame.draw.circle(screen, "GREEN", (mini[1][0], mini[1][1]), 1)
                elif tile == "rock":
                    pygame.draw.circle(screen, "BlACK", (mini[1][0], mini[1][1]), 1)
                elif tile == "gold":
                    pygame.draw.circle(screen, "YELLOW", (mini[1][0], mini[1][1]), 1)
                elif tile == "berrybush":
                    pygame.draw.circle(screen, "RED", (mini[1][0], mini[1][1]), 1)



