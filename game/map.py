import copy
import csv
import random
import noise
import pygame.mouse

# from .game import show_grid_setting
from .utils import *
from settings import *
# from buildings import Farm, TownCenter, House, Building
from player import playerOne, playerTwo, playerThree, player_list, MAIN_PLAYER
from units import Villager, Unit, Farm, TownCenter, House, Building, Barracks, Clubman, Dragon, Tower, Wall, Market


class Map:
    def __init__(self, hud, entities, grid_length_x, grid_length_y, width, height):
        self.hud = hud
        # 4 booleans for corners. each corner becomes true when a player occupies at the beginning of the game
        self.corners = {"TOP_LEFT": False, "TOP_RIGHT": False, "BOTTOM_LEFT": False, "BOTTOM_RIGHT": False}
        self.entities = entities
        self.grid_length_x = grid_length_x
        self.grid_length_y = grid_length_y
        self.width = width
        self.height = height
        # True if you want grid display, else False
        self.display_grid_setting = False
        # anything >1 or <-1, otherwise pnoise will return 0
        self.perlin_scale = grid_length_x / 2
        self.grass_tiles = pygame.Surface(
            (grid_length_x * TILE_SIZE * 2, grid_length_y * TILE_SIZE + 2 * TILE_SIZE)).convert_alpha()
        self.tiles = self.load_images()
        # lists of lists
        self.buildings = [[None for x in range(self.grid_length_x)] for y in range(self.grid_length_y)]
        self.units = [[None for x in range(self.grid_length_x)] for y in range(self.grid_length_y)]
        self.resources_list = []

        # Fog of war
        # self.visible = self.
        # self.fog = False

        self.map = self.create_map()
        self.camera = None
        self.place_x = 0
        self.place_y = 0
        # here we place the townhall randomly on the map
        # self.place_townhall()
        self.collision_matrix = self.create_collision_matrix()
        # used when selecting a tile to build
        self.temp_tile = None
        # used when examining elements of the map
        self.examined_tile = None

        # universal timer
        self.timer = 0

        for p in player_list:
            self.place_starting_units(p)

        self.anchor_points = self.load_anchor_points("Resources/assets/axeman_attack_anchor_90.csv")
        # self.map[10][10] = Dragon((10,20), MAIN_PLAYER, self)
        # to improve animations, not working for now
        # self.anchor_points = self.load_anchor_points("Resources/assets/axeman_attack_anchor_90.csv")

    def create_map(self):
        map = []
        for grid_x in range(self.grid_length_x):
            map.append([])
            for grid_y in range(self.grid_length_y):
                map_tile = self.grid_to_map(grid_x, grid_y)
                # if tile is resource, we add it to resources_list, is used for display
                if map_tile["tile"] != "" and map_tile["tile"] != "building" and map_tile["tile"] != "unit":
                    self.resources_list.append(map_tile)
                map[grid_x].append(map_tile)
                render_pos = map_tile["render_pos"]
                # self.grass_tiles.getwidth()/2 : offset
                if not self.display_grid_setting:
                    self.grass_tiles.blit(self.hud.resources_sprites["grass"][random.randint(0, 10)],
                                          (render_pos[0] + self.grass_tiles.get_width() / 2, render_pos[1]))
                # standard grid display
                else:
                    self.grass_tiles.blit(
                        scale_image(self.hud.resources_sprites["grass"][random.randint(0, 10)], w=125),
                        (render_pos[0] + self.grass_tiles.get_width() / 2, render_pos[1]))
                scroll = pygame.Vector2(0, 0)
                scroll.x = 0
                scroll.y = 0
        return map

    def update(self, camera, screen):
        self.timer = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        mouse_action = pygame.mouse.get_pressed()
        if mouse_action[1] and self.hud.examined_tile is not None and TEST_MODE:
            print(self.hud.examined_tile)
            if isinstance(self.hud.examined_tile, TownCenter): self.hud.examined_tile.owner.towncenter = None
            self.remove_entity(self.hud.examined_tile, camera.scroll)
        self.temp_tile = None

        # the player selects a building in the hud
        if self.hud.selected_tile is not None and self.hud.examined_tile is not None \
                and ((self.hud.examined_tile.owner == MAIN_PLAYER)
                     or TEST_MODE):
            grid_pos = self.mouse_to_grid(mouse_pos[0], mouse_pos[1], camera.scroll)

            # we change action_panel depending on the selected entity
            if self.can_place_tile(grid_pos):
                if self.hud.examined_tile.name == "Villager":
                    self.hud.bottom_left_menu = self.hud.villager_panel
                elif self.hud.examined_tile.name == "Town Center":
                    self.hud.bottom_left_menu = self.hud.town_hall_panel
                elif self.hud.examined_tile.name == "Barracks":
                    self.hud.bottom_left_menu = self.hud.barracks_panel
                elif self.hud.examined_tile.name == "Market":
                    self.hud.bottom_left_menu = self.hud.market_panel
                elif self.hud.examined_tile.name == "Wall":
                    self.hud.bottom_left_menu = self.hud.wall_panel

                else:
                    self.hud.bottom_left_menu = None

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

                    # we store the future building information inside building_to_create
                    if self.hud.selected_tile["name"] == "Farm" or self.hud.selected_tile["name"] == "House" or \
                            self.hud.selected_tile["name"] == "TownCenter" or \
                            self.hud.selected_tile["name"] == "Barracks" or self.hud.selected_tile["name"] == "Tower" or self.hud.selected_tile["name"] == "Wall"or self.hud.selected_tile["name"] == "Market":
                        working_villager.go_to_build(grid_pos, self.hud.selected_tile["name"])
                    self.hud.selected_tile = None

        # the player hasn't selected something to build, we check if he selected a building/unit
        else:
            grid_pos = self.mouse_to_grid(mouse_pos[0], mouse_pos[1], camera.scroll)
            if 0 < grid_pos[0] < self.grid_length_x - 1 and 0 < grid_pos[1] < self.grid_length_y - 1:

                town_center_check_condition = (self.buildings[grid_pos[0]][grid_pos[1] + 1] and type(self.buildings[grid_pos[0]][grid_pos[1] + 1]) == TownCenter) or (self.buildings[grid_pos[0] - 1][grid_pos[1] + 1] and type(self.buildings[grid_pos[0] - 1][grid_pos[1] + 1]) == TownCenter) or (self.buildings[grid_pos[0] - 1][grid_pos[1]] and type(self.buildings[grid_pos[0] - 1][grid_pos[1]]) == TownCenter)

                barrack_check_condition = (self.buildings[grid_pos[0]][grid_pos[1] + 1] and type(self.buildings[grid_pos[0]][grid_pos[1] + 1]) == Barracks) or (self.buildings[grid_pos[0] - 1][grid_pos[1] + 1] and type(self.buildings[grid_pos[0] - 1][grid_pos[1] + 1]) == Barracks) or (self.buildings[grid_pos[0] - 1][grid_pos[1]] and type(self.buildings[grid_pos[0] - 1][grid_pos[1]]) == Barracks)

                #if we left clicked on nothing
                if mouse_action[0] and not self.is_there_collision(grid_pos) and not self.hud.bottom_hud_rect.collidepoint(
                    mouse_pos) and not town_center_check_condition and not barrack_check_condition:
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
                        if building is not None and (building.owner == MAIN_PLAYER or TEST_MODE):
                            self.hud.examined_tile = building

                            if type(building) == TownCenter:
                                self.hud.bottom_left_menu = self.hud.town_hall_panel
                            elif type(building) == Barracks:
                                self.hud.bottom_left_menu = self.hud.barracks_panel
                            elif type(self.hud.examined_tile) == Market:
                                self.hud.bottom_left_menu = self.hud.market_panel
                            elif type(self.hud.examined_tile) == Wall:
                                self.hud.bottom_left_menu = self.hud.wall_panel

                            else:
                                self.hud.bottom_left_menu = None

                        elif unit is not None and (unit.owner == MAIN_PLAYER or TEST_MODE):
                            self.hud.examined_tile = unit
                            if type(unit) == Villager:
                                self.hud.bottom_left_menu = self.hud.villager_panel
                            else:
                                self.hud.bottom_left_menu = None
                        # there is no unit nor building on this tile, but we check if it belongs to a 2x2 building
                        else:
                            self.check_selection_2x2_buildings(grid_pos)
                else:
                    pass

    def draw(self, screen, camera):
        self.camera = camera
        # displaying grass tiles
        screen.blit(self.grass_tiles, (camera.scroll.x, camera.scroll.y))
        for player in player_list:
            #building death display, not working for now
            for building in player.building_list:
                if type(building) == House and building.death_animation.to_be_played:
                    building.death_animation_group.draw(screen)
                    building.death_animation.update()

            #attack villager animation display
            for unit in player.unit_list:
                if type(unit) == Villager and unit.attack_animation.to_be_played:
                    unit.attack_animation_group.draw(screen)
                    unit.attack_animation.update()
                elif type(unit) == Villager and unit.mining_animation.to_be_played:
                    unit.mining_animation_group.draw(screen)
                    unit.mining_animation.update()

            #boom animation
            if self.hud.boom_animation.to_be_played:
                self.hud.boom_animation_group.draw(screen)
                self.hud.boom_animation.update()

        for player in player_list:
            # building display. If building selected, we highlight the tile. If building not full health, we display its health bar
            for building in player.building_list:
                if building.current_health <= 0:
                    self.remove_entity(building, camera.scroll)

                # if building is selected, we highlight its tile
                if self.examined_tile is not None:
                    if not building.is_being_built:
                        if (building.pos[0] == self.examined_tile[0]) and (building.pos[1] == self.examined_tile[1]):
                            if type(building) != TownCenter and type(building) != Barracks and type(building) != Market:
                                self.highlight_tile(building.pos[0], building.pos[1], screen, "WHITE",
                                                    camera.scroll)
                            else:
                                self.highlight_tile(building.pos[0], building.pos[1] - 1, screen, "WHITE",
                                                    camera.scroll,
                                                    multiple_tiles_tiles_flag=True)
                                self.hud.display_life_bar(screen, building, self, for_hud=False, camera=camera)
                self.display_building(screen, building, building.owner.color, camera.scroll,
                                      self.grid_to_renderpos(building.pos[0], building.pos[1]), player)
                if building.current_health < building.max_health:
                    self.hud.display_life_bar(screen, building, self, for_hud=False, camera=camera)

            # units display. If units selected, we highlight the tile. If units not full health, we display its health bar
            for unit in player.unit_list:
                if unit.current_health <= 0:
                    # self.remove_entity(unit, camera.scroll)
                    ...
                elif unit.current_health < unit.max_health:
                    self.hud.display_life_bar(screen, unit, self, for_hud=False, camera=camera)
                # if building is selected, we highlight its tile
                elif self.examined_tile is not None:
                    if (unit.pos[0] == self.examined_tile[0]) and (unit.pos[1] == self.examined_tile[1]):
                        self.highlight_tile(unit.pos[0], unit.pos[1], screen, "WHITE", camera.scroll)

                self.display_unit(unit, screen, camera, self.grid_to_renderpos(unit.pos[0], unit.pos[1]))
                if self.examined_tile is not None:
                    if (unit.pos[0] == self.examined_tile[0]) and (
                            unit.pos[1] == self.examined_tile[1]):
                        self.hud.display_life_bar(screen, unit, self, for_hud=False, camera=camera)

        for resource in self.resources_list:
            self.display_resources_on_tile(resource, screen, camera)

        # temp tile is a dictionary containing name + image + render pos + iso_poly + collision
        # if player is looking for a tile to place a building, we highlight the tested tiles in RED or GREEN if the tile is free or not
        # we display the future building on the tested tile every time
        for p in player_list:
            if self.temp_tile is not None:
                self.display_potential_building(screen, camera, p)

    def load_images(self):
        block = pygame.image.load(os.path.join(assets_path, "block.png")).convert_alpha()
        tree = pygame.image.load("Resources/assets/Models/Map/Trees/1.png").convert_alpha()
        rock = pygame.image.load(os.path.join("Resources/assets/Models/Map/Stones/7.png")).convert_alpha()
        # grass_tile = scale_image(pygame.image.load("Resources/assets/Models/Map/grass_01.png").convert_alpha(), w=128)
        grass_tile = scale_image(
            pygame.image.load("Resources/assets/Models/Map/grass/t_grass_aoe1_x2_001.png").convert_alpha(), w=125)
        gold = pygame.image.load(os.path.join("Resources/assets/Models/Map/Gold/4.png")).convert_alpha()
        berrybush = pygame.image.load(os.path.join("Resources/assets/Models/Map/Berrybush/1.png")).convert_alpha()

        town_center = pygame.image.load(
            "Resources/assets/Models/Buildings/Town_Center/BLUE/town_center_x1.png").convert_alpha()
        house = pygame.image.load("Resources/assets/Models/Buildings/House/BLUE/house_1BLUE.png").convert_alpha()
        farm = pygame.image.load("Resources/assets/Models/Buildings/Farm/farmBLUE.png").convert_alpha()

        barracks = None
        villager = None

        images = {
            "TownCenter": town_center,
            "House": house,
            "Farm": farm,
            "Barrcacks": barracks,
            "tree": tree,
            "rock": rock,
            "block": block,
            "grass": grass_tile,
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
            variation = random.randint(0, 9)

        else:
            if r <= 1:
                tile = "rock"
                variation = random.randint(0, 6)
            elif r <= 2:
                tile = "tree"
                variation = random.randint(0, 9)
            elif r <= 3:
                tile = "gold"
                variation = random.randint(0, 6)
            elif r == 4:
                tile = "berrybush"
                variation = random.randint(0, 2)

            else:
                tile = ""
                variation = random.randint(1, 11)

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

    # here is the OLD fonction that places the townhall randomly on the map
    """def place_townhall(self, the_player=MAIN_PLAYER):
        while not the_player.townhall_placed:
            place_x = random.randint(0, self.grid_length_x - 2)
            place_y = random.randint(1, self.grid_length_y - 1)

            self.place_x = place_x
            self.place_y = place_y

            new_building = TownCenter((place_x, place_y), self, the_player)
            new_building.is_being_built = False
            new_building.construction_progress = 100
            new_building.current_health = new_building.max_health
            self.entities.append(new_building)
            self.buildings[place_x][place_y] = new_building

            the_player.townhall_placed = True

            the_player.towncenter_pos = (place_x, place_y)
            the_player.towncenter = new_building

            self.map[place_x][place_y]["tile"] = "building"
            self.map[place_x][place_y]["collision"] = True
            self.collision_matrix[place_y][place_x] = 0
            self.map[place_x + 1][place_y]["tile"] = "building"
            self.map[place_x + 1][place_y]["collision"] = True
            self.collision_matrix[place_y][place_x+1] = 0
            self.map[place_x][place_y - 1]["tile"] = "building"
            self.map[place_x][place_y - 1]["collision"] = True
            self.collision_matrix[place_y-1][place_x] = 0
            self.map[place_x + 1][place_y - 1]["tile"] = "building"
            self.map[place_x + 1][place_y - 1]["collision"] = True
            self.collision_matrix[place_y-1][place_x+1] = 0"""

    # here is the fonction that randomly places a player's starting units 4 tiles from the corner
    def place_starting_units(self, the_player=MAIN_PLAYER):
        townhall_placed = False

        while not townhall_placed:
            # (x : 0 if left, 1 if right ; y : 1 if bottom, 0 if top)
            place_x = random.randint(0, 1)
            place_y = random.randint(0, 1)

            # TO TEST, should be disabled if we play a real game
            if TEST_MODE or 1:
                if the_player == playerTwo:
                    place_x = 0
                    place_y = 0
                elif the_player == playerOne:
                    place_x = 1
                    place_y = 0
                elif the_player == playerThree:
                    place_x = 0
                    place_y = 1

            # top_left
            if (place_x, place_y) == (0, 0):
                # we remove stuff from the chosen corner
                for x in range(2, 8):
                    for y in range(2, 8):
                        self.clear_tile(x, y)
                # we place towncenter
                new_building = TownCenter((4, 5), self, the_player)
                # starting unit
                start_unit = Villager(self.map[4][6]["grid"], the_player, self)
                # starting unit. For debug reasons, we need a tuple and not a list (pathfinding)
                vill_pos = tuple(self.map[4][6]["grid"])
                the_player.side = "top"

            # top_right
            elif (place_x, place_y) == (1, 0):
                # we remove stuff from the chosen corner
                for x in range(self.grid_length_x - 8, self.grid_length_x - 2):
                    for y in range(2, 8):
                        self.clear_tile(x, y)
                # we place towncenter
                new_building = TownCenter((self.grid_length_x - 6, 5), self, the_player)
                # starting unit
                start_unit = Villager(self.map[self.grid_length_x - 6][6]["grid"], the_player, self)
                # starting unit. For debug reasons, we need a tuple and not a list (pathfinding)
                vill_pos = tuple(self.map[self.grid_length_x - 6][6]["grid"])
                the_player.side = "right"

            # bot_left
            elif (place_x, place_y) == (0, 1):
                # we remove stuff from the chosen corner
                for x in range(2, 8):
                    for y in range(self.grid_length_y - 8, self.grid_length_y - 2):
                        self.clear_tile(x, y)
                # we place towncenter
                new_building = TownCenter((4, self.grid_length_y - 5), self, the_player)
                # starting unit
                start_unit = Villager(self.map[4][self.grid_length_y - 4]["grid"], the_player, self)
                # starting unit. For debug reasons, we need a tuple and not a list (pathfinding)
                vill_pos = tuple(self.map[4][self.grid_length_y - 4]["grid"])
                the_player.side = "left"

            # bot_right
            elif (place_x, place_y) == (1, 1):
                # we remove stuff from the chosen corner
                for x in range(self.grid_length_x - 8, self.grid_length_x - 2):
                    for y in range(self.grid_length_y - 8, self.grid_length_y - 2):
                        self.clear_tile(x, y)
                # we place towncenter
                new_building = TownCenter((self.grid_length_x - 6, self.grid_length_y - 5), self, the_player)
                # starting unit
                start_unit = Villager(self.map[self.grid_length_x - 6][self.grid_length_y - 4]["grid"], the_player,
                                      self)
                # starting unit. For debug reasons, we need a tuple and not a list (pathfinding)
                vill_pos = tuple(self.map[self.grid_length_x - 6][self.grid_length_y - 4]["grid"])
                the_player.side = "bot"

            # for towncenter
            new_building.is_being_built = False
            new_building.construction_progress = 100
            new_building.current_health = new_building.max_health

            townhall_placed = True
            the_player.towncenter_pos = new_building.pos
            the_player.towncenter = new_building

            # for starting villagers
            the_player.pay_entity_cost_bis(Villager)

    def remove_entity(self, entity, scroll):
        self.entities.remove(entity)
        if issubclass(type(entity), Building):
            if not issubclass(type(entity), Farm):

                death_pos = (self.grid_to_renderpos(entity.pos[0], entity.pos[1]))
                death_pos = (
                    death_pos[0] + self.grass_tiles.get_width() / 2 + scroll.x,
                    death_pos[1] - (self.hud.first_age_building_sprites[
                                        entity.__class__.__name__]["RED"][
                                        entity.owner.age - 1].get_height() - TILE_SIZE) + scroll.y)
            else:
                death_pos = (self.grid_to_renderpos(entity.pos[0], entity.pos[1]))
                death_pos = (
                    death_pos[0] + self.grass_tiles.get_width() / 2 + scroll.x,
                    death_pos[1] - (self.hud.first_age_building_sprites[
                                        entity.__class__.__name__]["RED"].get_height() - TILE_SIZE) + scroll.y)
            entity.owner.building_list.remove(entity)
            if type(entity) == TownCenter:
                self.buildings[entity.pos[0]][entity.pos[1]] = None
                self.buildings[entity.pos[0] + 1][entity.pos[1]] = None
                self.buildings[entity.pos[0]][entity.pos[1] - 1] = None
                self.buildings[entity.pos[0] + 1][entity.pos[1] - 1] = None
                self.collision_matrix[entity.pos[1]][entity.pos[0]] = 1
                self.collision_matrix[entity.pos[1]][entity.pos[0] + 1] = 1
                self.collision_matrix[entity.pos[1] - 1][entity.pos[0] + 1] = 1
                self.collision_matrix[entity.pos[1] - 1][entity.pos[0]] = 1
                self.map[entity.pos[0] + 1][entity.pos[1]]["tile"] = ""
                self.map[entity.pos[0]][entity.pos[1] - 1]["tile"] = ""
                self.map[entity.pos[0] + 1][entity.pos[1] - 1]["tile"] = ""
            else:
                self.buildings[entity.pos[0]][entity.pos[1]] = None
                self.collision_matrix[entity.pos[1]][entity.pos[0]] = 1

        elif issubclass(type(entity), Unit):
            self.units[entity.pos[0]][entity.pos[1]] = None
            self.collision_matrix[entity.pos[1]][entity.pos[0]] = 1

            death_pos = (self.grid_to_renderpos(entity.pos[0], entity.pos[1]))
            death_pos = (
                death_pos[0] + self.grass_tiles.get_width() / 2 + scroll.x,
                death_pos[1] - (self.hud.villager_sprites["RED"][0].get_height() - TILE_SIZE) + scroll.y)
            entity.owner.unit_list.remove(entity)
            if isinstance(entity, Villager):
                entity.owner.unit_occupied.append(0)

        self.examined_tile = None
        self.hud.examined_tile = None
        self.map[entity.pos[0]][entity.pos[1]]["tile"] = ""
        # calculating where to display death animation

        if type(entity) == House:
            entity.owner.max_population -= 5
            self.hud.death_animations[entity.__class__.__name__]["animation"].play(death_pos, age=entity.owner.age,
                                                                                   color=entity.owner.color)
        elif type(entity) == TownCenter:

            entity.owner.max_population -= 10
            self.hud.death_animations["Town Center"]["animation"].play(death_pos, color=entity.owner.color,
                                                                       age=entity.owner.age)
        elif type(entity) == Barracks:

            self.hud.death_animations["Barracks"]["animation"].play(death_pos, color=entity.owner.color,
                                                                       age=entity.owner.age)

        elif type(entity) == Villager:
            entity.owner.current_population -= 1
            self.hud.death_animations["Villager"]["animation"].play(death_pos, color=entity.owner.color,
                                                                    angle=entity.angle)
        elif type(entity) == Dragon:
            entity.owner.current_population -= 1


    # remove resources from tile to get an empty tile
    def clear_tile(self, grid_x, grid_y):
        self.map[grid_x][grid_y]["tile"] = ""
        self.map[grid_x][grid_y]["variation"] = 0
        self.collision_matrix[grid_y][grid_x] = 1
        self.map[grid_x][grid_y]["collision"] = False

    # returns true if there is collision, else False
    def is_there_collision(self, grid_pos: [int, int]):
        if 0 <= grid_pos[0] < self.grid_length_x - 1 and 0 < grid_pos[1] < self.grid_length_y - 1:
            return True if (self.collision_matrix[grid_pos[1]][grid_pos[0]] == 0 or self.map[grid_pos[0]][grid_pos[1]][
                "collision"]) else False
        else:
            return False

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

    # Outline in white the image. Can be used to show an entity is selected...
    def highlight_image(self, image, screen, render_pos, scroll, color="WHITE"):
        # transform color name to color code
        color = get_color_code(color)
        # outline in white the object selected with mask feature
        mask = pygame.mask.from_surface(image).outline()
        mask = [(x + render_pos[0] + self.grass_tiles.get_width() / 2 + scroll.x,
                 y + render_pos[1] - (
                         image.get_height() - TILE_SIZE) + scroll.y)
                for x, y in mask]
        pygame.draw.polygon(screen, color, mask, 3)

    def highlight_tile(self, grid_x, grid_y, screen, color, scroll, multiple_tiles_tiles_flag=False):
        # we have to highlight 1 tile
        if not multiple_tiles_tiles_flag:
            iso_poly = self.grid_to_iso_poly(grid_x, grid_y)
            iso_poly = [
                (x + self.grass_tiles.get_width() / 2 + scroll.x, y + scroll.y)
                for x, y in iso_poly]
        # for more than 1 tile. For now, only 2x2 highlight is supported.
        else:
            iso_poly = self.get_2x2_iso_poly(grid_x, grid_y, scroll)

        pygame.draw.polygon(screen, get_color_code(color), iso_poly, 3)

    # enable/disable show_grid setting. If previously true, becomes False, if previously False, becomes True. False by default
    # actual display is in "create_map" in map.py file
    def show_grid(self):
        self.display_grid_setting = True if not self.display_grid_setting else False

    def draw_minimap(self, screen, camera):
        '''Draw a minimap so you dont get lost. Moving it to HUD or
        Camera is highly recommended, draw the polygon once so increase
        FPS. '''
        minimap_scaling = 16
        ### Draw the camera on the map
        ### 420 and 200 is the size of minimap panel
        self.cam_width = self.width/minimap_scaling
        self.cam_height = self.height/minimap_scaling

        # iso_pos_cam = self.grid_to_iso_poly(camera.scroll.x , camera.scroll.y)
        iso_pos_cam = [(-camera.scroll.x / minimap_scaling + self.width  - 420 ,
                         -camera.scroll.y/ minimap_scaling + self.height - 200)]
        #For debugging purpose

        # for xh in iso_pos_cam:
        #     print(xh)
        #     print("**********")
        rect_cam = pygame.Rect((iso_pos_cam[0][0],iso_pos_cam[0][1]), (self.cam_width, self.cam_height))
        pygame.draw.rect(screen, "WHITE", rect_cam, 2 )

        for x in range(self.grid_length_x):
            for y in range(self.grid_length_y):
                # Draw polygon
                mini = self.map[x][y]["iso_poly"]
                # mini = [((x + self.width / 2) / minimap_scaling + 1640,
                #        (y + self.height / 4) / minimap_scaling + 820) for x, y in mini]  # position x + ...., y  + ...
                mini = [((x) / minimap_scaling + self.width - 420 / 2,
                         (y) / minimap_scaling + self.height - 200) for x, y in mini]
                # pygame.draw.polygon(screen, "WHITE", mini, 1)

                # Draw small dot representing entities

                tile = self.map[x][y]["tile"]

                if tile == "tree":
                    # pygame.draw.circle(screen, "GREEN", (render_pos[0]/minimap_scaling + 1640, render_pos[1]/minimap_scaling+820), 1)
                    pygame.draw.circle(screen, "GREEN", (mini[1][0], mini[1][1]), 1)
                elif tile == "rock":
                    pygame.draw.circle(screen, "WHITE", (mini[1][0], mini[1][1]), 1)
                elif tile == "gold":
                    pygame.draw.circle(screen, "YELLOW", (mini[1][0], mini[1][1]), 1)
                elif tile == "berrybush":
                    pygame.draw.circle(screen, "PINK", (mini[1][0], mini[1][1]), 1)
        for player in player_list:
            for building in player.building_list:
                iso_pos = self.grid_to_iso_poly(building.pos[0], building.pos[1])
                iso_pos = [((x) / minimap_scaling + self.width - 420 / 2,
                         (y) / minimap_scaling + self.height - 200) for x, y in iso_pos]
                pygame.draw.circle(screen, building.owner.color, (iso_pos[1][0], iso_pos[1][1]), 2)
                # print(building.owner.color, iso_pos) Debug purpose
            for unit in player.unit_list:
                unit_pos = self.grid_to_iso_poly(unit.pos[0], unit.pos[1])
                unit_pos = [((x) / minimap_scaling + self.width - 420 / 2,
                            (y) / minimap_scaling + self.height - 200) for x, y in unit_pos]
                pygame.draw.circle(screen, building.owner.color, (unit_pos[1][0], unit_pos[1][1]), 3)

    # display resources on map. Most resources have different variations. If resource is selected or has less than max health, we display its health bar
    def display_resources_on_tile(self, resource_tile, screen, camera):
        tile_type = resource_tile["tile"]
        render_pos = resource_tile["render_pos"]

        # if the tile isnt empty and inst destroyed, we display it. All resources have slightly different models to add variety
        if tile_type != "" and tile_type != "building" and tile_type != "unit":
            variation = self.map[resource_tile["grid"][0]][resource_tile["grid"][1]]["variation"]
            #offset is only used for trees
            offset = self.hud.resources_sprites_offsets[variation]
            if tile_type != "tree":
                offset = (0,0)
            screen.blit(self.hud.resources_sprites[tile_type][variation], (
                            render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + offset[0],
                            render_pos[1] - (self.tiles[tile_type].get_height() - TILE_SIZE) + camera.scroll.y + offset[1])
                        )

            # here we display the health bar of the ressources
            if (self.examined_tile is not None and resource_tile["grid"][0] == self.examined_tile[0] and
                resource_tile["grid"][1] == self.examined_tile[1]) \
                    or resource_tile["health"] != resource_tile["max_health"]:
                self.hud.display_life_bar(screen, resource_tile, self, camera=camera, for_hud=False, for_resource=True)
        # elif tile_type == "":
        #   screen.blit(self.hud.resources_sprites["grass"][
        #                    self.map[resource_tile["grid"][0]][resource_tile["grid"][1]]["variation"]], (
        #                   render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
        #                   render_pos[1] - (self.hud.resources_sprites["grass"][
        #                   self.map[resource_tile["grid"][0]][resource_tile["grid"][1]]["variation"]].get_height() - TILE_SIZE) + camera.scroll.y)
        #               )

    def display_unit(self, unit, screen, camera, render_pos):
        # HERE WE DRAW THE UNITS ON THE MAP
        # we extract from the units list the unit we want to display
        if unit is not None:
            if unit.current_health <= 0:
                self.remove_entity(unit, camera.scroll)
            else:
                # have we selected this unit ? if yes we will highlight its tile
                if self.examined_tile is not None:
                    if (unit.pos[0] == self.examined_tile[0]) and (unit.pos[1] == self.examined_tile[1]):
                        self.highlight_tile(self.examined_tile[0], self.examined_tile[1], screen, "WHITE",
                                            camera.scroll)
                        self.hud.display_life_bar(screen, unit, self, for_hud=False, camera=camera, for_resource=False)

                # we initialize target to None just in case
                target = None

                # if we select the unit, she wont attack herself
                if type(unit.target) in UNIT_TYPES and unit.target.pos == unit.pos:
                    unit.target = None

                # if we select a building or a unit, the unit go attack it
                if (type(unit.target) in UNIT_TYPES and unit.target.pos != unit.pos) or type(unit.target) in BUILDING_TYPES:
                    target = unit.target

                # if we attack a ressource, we go gather it
                if type(unit) == Villager and unit.targeted_ressource is not None:
                    target = unit.map.map[unit.targeted_ressource[0]][unit.targeted_ressource[1]]

                # if the unit is attacking, we highlight the tile she is attacking in DARK RED
                if target is not None and (unit.is_attacking or unit.is_moving_to_attack):
                    # target highlighted in dark red
                    self.highlight_tile(target.pos[0], target.pos[1], screen, "DARK_RED", camera.scroll)

                # if the unit is going to gather we highlight the tile she is going to gather in GREEN
                elif target is not None and ((type(unit) == Villager and unit.is_gathering) or unit.is_moving_to_gather):
                    ...
                    self.highlight_tile(target["grid"][0], target["grid"][1], screen, "GREEN", camera.scroll)

                if unit.searching_for_path and not (type(unit) == Villager and unit.is_moving_to_gather and not unit.is_moving_to_build):
                    screen.blit(scale_image(move_icon, w=40), (
                        render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + 35,
                        render_pos[1] - (
                                self.hud.villager_sprites["RED"][0].get_height() - TILE_SIZE) + camera.scroll.y - 80)
                                )
                elif unit.is_attacking or (type(unit) == Villager and (unit.is_gathering or unit.is_moving_to_gather)):
                    screen.blit(scale_image(attack_icon, w=40), (
                        render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + 35,
                        render_pos[1] - (
                                self.hud.villager_sprites["RED"][0].get_height() - TILE_SIZE) + camera.scroll.y - 80)
                                )

                elif type(unit) == Villager and (unit.is_building or unit.is_moving_to_build):
                    screen.blit(scale_image(build_icon, w=40), (
                        render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + 35,
                        render_pos[1] - (
                                self.hud.villager_sprites["RED"][0].get_height() - TILE_SIZE) + camera.scroll.y + -80)
                                )

                if type(unit) == Villager:
                    # draw future buildings
                    if unit.building_to_create is not None and not unit.building_to_create["has_construction_started"]:
                        future_building = unit.building_to_create
                        future_building_render_pos = self.grid_to_renderpos(future_building["pos"][0],
                                                                            future_building["pos"][1])
                        for p in player_list:
                            self.display_building(screen, future_building, unit.owner.color, camera.scroll,
                                                  future_building_render_pos, p,
                                                  is_hypothetical_building=True, is_build_possibility_display=True)
                # display unit model
                if type(unit) == Villager:
                    self.display_villager(unit, screen, camera, render_pos)
                elif type(unit) == Clubman:
                    self.display_clubman(unit, screen, camera, render_pos)
                elif type(unit) == Dragon:
                    self.display_dragon(unit, screen, camera, render_pos)
                else:
                    screen.blit(unit.sprite, (
                        render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x,
                        render_pos[1] - (unit.sprite.get_height() - TILE_SIZE) + camera.scroll.y)
                                )

                if unit.searching_for_path:
                    # creates a flag to display where the unit is going
                    offset = (20, -25)
                    screen.blit(self.hud.destination_flags_sprites[unit.owner.color][0], (
                        unit.dest["render_pos"][0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + offset[0],
                        unit.dest["render_pos"][1] - (self.hud.destination_flags_sprites[unit.owner.color][0].get_height() - TILE_SIZE) + camera.scroll.y + offset[1])
                                )

    # temp tile is a dictionary containing name + image + render pos + iso_poly + collision
    # if player is looking for a tile to place a building, we highlight the tested tiles in RED or GREEN if the tile is free or not
    # we display the future building on the tested tile every time
    def display_potential_building(self, screen, camera, the_player=MAIN_PLAYER):
        render_pos = self.temp_tile["render_pos"]
        grid = self.renderpos_to_grid(render_pos[0], render_pos[1])

        # if we cannot place our building on the tile because there's already smth, we display the tile in red, else, in green
        # For towncenter, we have to display a 2x2 green/Red case, else we only need to highlight a 1x1 case
        if self.temp_tile["name"] == "TownCenter" or self.temp_tile["name"] == "Barracks" or self.temp_tile["name"] == "Market":
            # collision matrix : 0 if collision, else 1, we check the 4 cases of the town center
            if 0 <= grid[0] < self.grid_length_x - 1 and 0 < grid[0] < self.grid_length_y:
                if self.temp_tile["collision"] or self.collision_matrix[grid[1]][grid[0] + 1] == 0 or \
                        self.collision_matrix[grid[1] - 1][grid[0] + 1] == 0 or \
                        self.collision_matrix[grid[1] - 1][grid[0]] == 0:
                    self.highlight_tile(grid[0], grid[1] - 1, screen, "RED", camera.scroll, multiple_tiles_tiles_flag=True)
                else:
                    self.highlight_tile(grid[0], grid[1] - 1, screen, "GREEN", camera.scroll,
                                        multiple_tiles_tiles_flag=True)

        # for normal buildings (1x1)
        else:
            if self.temp_tile["collision"]:
                self.highlight_tile(grid[0], grid[1], screen, "RED", camera.scroll)
            else:
                self.highlight_tile(grid[0], grid[1], screen, "GREEN", camera.scroll)

        # display the buildable building on the tile
        self.display_building(screen, self.temp_tile, the_player.color, camera.scroll, render_pos, the_player,
                              is_hypothetical_building=True)

    def display_building(self, screen, building, color: str, scroll, render_pos, the_player=MAIN_PLAYER,
                         is_hypothetical_building=False,
                         is_build_possibility_display=False):
        # we either display the building fully constructed or being built ( 4 possible states )
        if not is_hypothetical_building:
            offset = (0, 0)
            # normal display
            if not building.is_being_built:
                if building.__class__.__name__ != "Farm":
                    sprite_to_display = \
                        self.hud.first_age_building_sprites[building.__class__.__name__][building.owner.color][
                            building.owner.age - 1]
                # farm has the same model the 4 ages, hence we directly have the image and not a list of 4 images, 1 for every age
                else:
                    sprite_to_display = self.hud.first_age_building_sprites[building.__class__.__name__][building.owner.color]

                #change the offset to optimise the pos display for every entity
                if isinstance(building, TownCenter):
                    offset = (10, 13)
                elif isinstance(building, Barracks):
                    offset = (8, 24)
                elif isinstance(building, Tower):
                    offset = (-60, 0)
                elif isinstance(building, Market):
                    offset = (20, 20)


                #general display
                screen.blit(sprite_to_display, (
                    render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x + offset[0],
                    render_pos[1] - (sprite_to_display.get_height() - TILE_SIZE) + scroll.y + offset[1])
                            )

            #building construction progress
            else:
                #need to add a little offset for 2x2 constructoin buildings to display it at the right place
                offset = (0,30)
                if building.construction_progress == 0:
                    if type(building) == TownCenter or type(building) == Barracks or type(building) == Market:
                        screen.blit(building_construction_1_2x2, (
                            render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x + offset[0],
                            render_pos[1] - (building_construction_1_2x2.get_height() - TILE_SIZE) + scroll.y + offset[1])
                                    )
                    else:
                        screen.blit(building_construction_1, (
                            render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                            render_pos[1] - (building_construction_1.get_height() - TILE_SIZE) + scroll.y)
                                    )

                elif building.construction_progress == 25:
                    if type(building) == TownCenter or type(building) == Barracks or type(building) == Market:
                        screen.blit(building_construction_2_2x2, (
                            render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x + offset[0],
                            render_pos[1] - (building_construction_2_2x2.get_height() - TILE_SIZE) + scroll.y + offset[1])
                                    )
                    else:
                        screen.blit(building_construction_2, (
                            render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                            render_pos[1] - (building_construction_2.get_height() - TILE_SIZE) + scroll.y)
                                    )
                elif building.construction_progress == 50:
                    if type(building) == TownCenter or type(building) == Barracks or type(building) == Market:
                        screen.blit(building_construction_3_2x2, (
                            render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x + offset[0],
                            render_pos[1] - (building_construction_3_2x2.get_height() - TILE_SIZE) + scroll.y + offset[1])
                                    )
                    else:
                        screen.blit(building_construction_3, (
                            render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                            render_pos[1] - (building_construction_3.get_height() - TILE_SIZE) + scroll.y)
                                    )
                elif building.construction_progress == 75:
                    if type(building) == TownCenter or type(building) == Barracks or type(building) == Market:
                        screen.blit(building_construction_4_2x2, (
                            render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x + offset[0],
                            render_pos[1] - (building_construction_4_2x2.get_height() - TILE_SIZE) + scroll.y + offset[1])
                                    )
                    else:
                        screen.blit(building_construction_4, (
                            render_pos[0] + building.map.grass_tiles.get_width() / 2 + scroll.x,
                            render_pos[1] - (building_construction_4.get_height() - TILE_SIZE) + scroll.y)
                                    )

        # we have to display hypothetical building sprite to show the villager wants to build there
        else:
            if 1:
                # add a condition with your building and the new offset to display the building at the correct area
                offset = (0, 0)
                if building["name"] == "Tower":
                    offset = (-60, 0)
                elif building["name"] == "Barracks":
                    offset = (0, 20)
                elif building["name"] == "Market":
                    offset = (20, 20)

            #if not building["has_construction_started"]:
                if building["name"] != "Farm":
                    sprite_to_display = self.hud.first_age_building_sprites[building["name"]][color][the_player.age - 1]
                else:
                    sprite_to_display = self.hud.first_age_building_sprites[building["name"]][color]

                if is_build_possibility_display:
                    sprite_to_display = sprite_to_display.copy()
                    sprite_to_display.set_alpha(100)

                screen.blit(sprite_to_display,
                            (  # we obviously have to reapply the offset + camera scroll
                                render_pos[0] + 6400 / 2 + scroll.x + offset[0],
                                render_pos[1] - (sprite_to_display.get_height() - TILE_SIZE) + scroll.y + offset[1]
                            )
                            )

    # first try with not 1 image but animation (not only 1 image)
    # self.hud.villager_sprites[0] : corresponding to angle 135,+ 90 every time you add 1 to index
    def display_villager(self, unit, screen, camera, render_pos):
        """
        We have to calculate the angle between the villager's target and him
        """
        if unit.angle == 45:
            unit.sprite_index = 1
        elif unit.angle == 135:
            unit.sprite_index = 3
        elif unit.angle == 225:
            unit.sprite_index = 5
        elif unit.angle == 180:
            unit.sprite_index = 4
        elif unit.angle == 90:
            unit.sprite_index = 2
        elif unit.angle == 270:
            unit.sprite_index = 6
        elif unit.angle == 0:
            unit.sprite_index = 0
        elif unit.angle == 315:
            unit.sprite_index = 7

        if unit.is_attacking:
            animation_pos = (self.grid_to_renderpos(unit.pos[0], unit.pos[1]))
            animation_pos = (
                animation_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + 25,
                animation_pos[1] - (
                        self.hud.villager_sprites["RED"][0].get_height() - TILE_SIZE) + camera.scroll.y - 25)
            unit.attack_animation.play(animation_pos)

        elif unit.is_gathering:
            tile_type = self.map[unit.targeted_ressource[0]][unit.targeted_ressource[1]]["tile"]
            #mining
            # mining villager
            if tile_type == "gold" or tile_type == "rock":
                animation_pos = (self.grid_to_renderpos(unit.pos[0], unit.pos[1]))
                animation_pos = (
                    animation_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + 25,
                    animation_pos[1] - (
                            self.hud.mining_sprites_villager["RED"]["0"][0].get_height() - TILE_SIZE) + camera.scroll.y - 25)
                unit.mining_animation.play(animation_pos)

            #cutting wood or berrybush
            elif tile_type == "tree" or tile_type == "berrybush":
                animation_pos = (self.grid_to_renderpos(unit.pos[0], unit.pos[1]))
                animation_pos = (
                    animation_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + 25,
                    animation_pos[1] - (
                            self.hud.villager_sprites["RED"][0].get_height() - TILE_SIZE) + camera.scroll.y - 25)
                unit.attack_animation.play(animation_pos)

        #normal villager
        else:
            # fixed sprite
            # + 20 because of sprite offset
            screen.blit(self.hud.villager_sprites[unit.owner.color][unit.sprite_index], (
                render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + 32,
                render_pos[1] - (self.hud.villager_sprites[unit.owner.color][
                                     unit.sprite_index].get_height() - TILE_SIZE) + camera.scroll.y - 25)
                        )

    def display_clubman(self, unit, screen, camera, render_pos):
        """
        We have to calculate the angle between the villager's target and him
        """
        if unit.angle == 45:
            unit.sprite_index = 1
        elif unit.angle == 135:
            unit.sprite_index = 3
        elif unit.angle == 225:
            unit.sprite_index = 5
        elif unit.angle == 180:
            unit.sprite_index = 4
        elif unit.angle == 90:
            unit.sprite_index = 2
        elif unit.angle == 270:
            unit.sprite_index = 6
        elif unit.angle == 0:
            unit.sprite_index = 0
        elif unit.angle == 315:
            unit.sprite_index = 7

        if unit.is_attacking:
            animation_pos = (self.grid_to_renderpos(unit.pos[0], unit.pos[1]))
            animation_pos = (
                animation_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + 25,
                animation_pos[1] - (
                        self.hud.clubman_sprites["RED"][0].get_height() - TILE_SIZE) + camera.scroll.y - 25)
            unit.attack_animation.play(animation_pos)

        #normal clubman
        else:
            # fixed sprite
            # + 20 because of sprite offset
            screen.blit(self.hud.clubman_sprites[unit.owner.color][unit.sprite_index], (
                render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + 32,
                render_pos[1] - (self.hud.clubman_sprites[unit.owner.color][
                                     unit.sprite_index].get_height() - TILE_SIZE) + camera.scroll.y - 25)
                        )

    def display_dragon(self, unit, screen, camera, render_pos):
        """
        We have to calculate the angle between the villager's target and him
        """
        if unit.angle == 180:
            unit.sprite_index = 1
        elif unit.angle == 0:
            unit.sprite_index = 3
        elif unit.angle == 90:
            unit.sprite_index = 5
        elif unit.angle == 270:
            unit.sprite_index = 4

       # if unit.is_attacking:
          #  animation_pos = (self.grid_to_renderpos(unit.pos[0], unit.pos[1]))
          #  animation_pos = (
            #    animation_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + 25,
            #    animation_pos[1] - (
            #            self.hud.clubman_sprites["RED"][0].get_height() - TILE_SIZE) + camera.scroll.y - 25)
         #   unit.attack_animation.play(animation_pos)

        #normal idle animation dragon

        animation_pos = (self.grid_to_renderpos(unit.pos[0], unit.pos[1]))
        animation_pos = (animation_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x - 60,animation_pos[1] - (
            self.hud.dragon_sprites["idle"]["0"][0].get_height() - TILE_SIZE) + camera.scroll.y - 25)
        unit.idle_animation.play(animation_pos)

    # returns the angle between the origin tile and the destination tile. Angle goes from 0 to 360, 0 top, 90 right, etc...
    def get_angle_between(self, origin_tile_pos: [int, int], end_tile_pos: [int, int], unit):
        # first we calculate angle between grid, then we will apply some maths to get the "real" isometric angle
        # if origin == destination, no calcul
        angle = 0

        # linear movement : left right ; y the same, x varies
        if end_tile_pos[1] == origin_tile_pos[1]:
            # from left to right
            if end_tile_pos[0] > origin_tile_pos[0]:
                angle = 90
            # else from right to left
            else:
                angle = 270

        # linear movement : top bottom ; x the same, y varies
        elif end_tile_pos[0] == origin_tile_pos[0]:
            # from top to bottom
            if end_tile_pos[1] > origin_tile_pos[1]:
                angle = 180

            # else from bottom to top
            else:
                angle = 0


        # diagonal movement : top left bottom right ; dx = dy
        elif end_tile_pos[0] - origin_tile_pos[0] == end_tile_pos[1] - origin_tile_pos[1]:
            # if going down
            if end_tile_pos[0] - origin_tile_pos[0] > 0:
                angle = 135

            # else he is going up
            else:
                angle = 315

        # diagonal movement : top right bottom left ; dx = - dy
        elif end_tile_pos[0] - origin_tile_pos[0] == - (end_tile_pos[1] - origin_tile_pos[1]):
            # if going towards top right
            if end_tile_pos[0] - origin_tile_pos[0] > 0:
                angle = 45

            # else he is going bottom left
            else:
                angle = 225

        # transformation to get isometric
        angle = angle + 45

        return angle

    def load_anchor_points(self, path):
        anchor_dic = {}
        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if 360 < reader.line_num <= 390:
                    anchor_dic[reader.line_num] = (int(row[0]), int(row[1]))
        return anchor_dic

    #check nearby tiles of checked_tile to determine if we clicked on the ground or on a 2x2 building
    def check_selection_2x2_buildings(self, checked_tile: (int, int)):
        if checked_tile[1] + 1 < self.grid_length_y:
            building = self.buildings[checked_tile[0]][checked_tile[1] + 1]
        if building and type(building) == TownCenter or type(building) == Barracks or type(building) == Market:
            self.examined_tile = (checked_tile[0], checked_tile[1] + 1)

            # if the owner is the MAIN_PLAYER (us)
            if building.owner == MAIN_PLAYER or TEST_MODE:
                self.hud.examined_tile = building
                if type(self.hud.examined_tile) == TownCenter:
                    self.hud.bottom_left_menu = self.hud.town_hall_panel
                elif type(self.hud.examined_tile) == Barracks:
                    self.hud.bottom_left_menu = self.hud.barracks_panel
                elif type(self.hud.examined_tile) == Market:
                    self.hud.bottom_left_menu = self.hud.market_panel

        elif self.buildings[checked_tile[0] - 1][checked_tile[1] + 1] and (type(
                self.buildings[checked_tile[0] - 1][checked_tile[1] + 1]) == TownCenter
                                                                   or type(
                    self.buildings[checked_tile[0] - 1][checked_tile[1] + 1]) == Barracks) or type(
                    self.buildings[checked_tile[0] - 1][checked_tile[1] + 1]) == Market:
            self.examined_tile = (checked_tile[0] - 1, checked_tile[1] + 1)

            # if the owner is the MAIN_PLAYER (us)
            if self.buildings[checked_tile[0] - 1][checked_tile[1] + 1].owner == MAIN_PLAYER or TEST_MODE:
                self.hud.examined_tile = self.buildings[checked_tile[0] - 1][checked_tile[1] + 1]
                if type(self.hud.examined_tile) == TownCenter:
                    self.hud.bottom_left_menu = self.hud.town_hall_panel
                elif type(self.hud.examined_tile) == Barracks:
                    self.hud.bottom_left_menu = self.hud.barracks_panel
                elif type(self.hud.examined_tile) == Market:
                    self.hud.bottom_left_menu = self.hud.market_panel

        elif self.buildings[checked_tile[0] - 1][checked_tile[1]] and (type(
                self.buildings[checked_tile[0] - 1][checked_tile[1]]) == TownCenter
                                                               or type(
                    self.buildings[checked_tile[0] - 1][checked_tile[1]]) == Barracks) or type(
                    self.buildings[checked_tile[0] - 1][checked_tile[1]]) == Market:
            self.examined_tile = (checked_tile[0] - 1, checked_tile[1])

            # if the owner is the MAIN_PLAYER (us)
            if self.buildings[checked_tile[0] - 1][checked_tile[1]].owner == MAIN_PLAYER or TEST_MODE:
                self.hud.examined_tile = self.buildings[checked_tile[0] - 1][checked_tile[1]]
                if type(self.hud.examined_tile) == TownCenter:
                    self.hud.bottom_left_menu = self.hud.town_hall_panel
                elif type(self.hud.examined_tile) == Barracks:
                    self.hud.bottom_left_menu = self.hud.barracks_panel
                elif type(self.hud.examined_tile) == Market:
                    self.hud.bottom_left_menu = self.hud.market_panel

    #specify for which player you want the dragon to spawn
    def spawn_dragon(self, player, camera):
        spawn_position = (player.towncenter_pos[0], player.towncenter_pos[1] + 1)
        if self.map[spawn_position[0]][spawn_position[1]]["tile"] == "unit" or \
                self.map[spawn_position[0]][spawn_position[1]]["tile"] == "building":
            self.remove_entity(self.units[spawn_position[0]][spawn_position[1]], camera.scroll)
        self.clear_tile(spawn_position[0], spawn_position[1])
        # render_pos = self.grid_to_renderpos(spawn_position[0], spawn_position[1])
        # render_pos = render_pos[0] + self.grass_tiles.get_width() / 2 + camera.scroll.x + 10, render_pos[
        #    1] - 55 + camera.scroll.y
        # self.hud.boom_animation.play(render_pos)
        #dis_pos = self.grid_to_display_pos(spawn_position[0], spawn_position[1])
        self.units[spawn_position[0]][spawn_position[1]] = Dragon(spawn_position, player, self)

    # use this function to get the (x,y) tuple you need when you when to blit something and you only have its grid position
    # offset is to slightly change the display position, need to find the good offset yourself tho
    def grid_to_display_pos(self, grid_pos: (int, int), offset=(0, 0)):
        render_pos = self.grid_to_renderpos(grid_pos[0], grid_pos[1])
        display_pos = render_pos[0] + self.grass_tiles.get_width() / 2 + self.camera.scroll.x + 10 + offset[
            1], render_pos[1] - 55 + self.camera.scroll.y + offset[1]

        return display_pos
