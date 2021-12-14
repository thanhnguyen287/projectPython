import pygame
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from settings import destination_flag, TILE_SIZE


class Unit:
    def __init__(self, pos, player_owner_of_unit, map):
        self.owner = player_owner_of_unit
        self.map = map
        self.map.entities.append(self)

        self.pos = pos

        self.current_health = self.max_health
        self.is_alive = True

        self.owner.pay_entity_cost(self)

        # means current population +1
        self.owner.update_resource(4, 1)

        #pathfinding
        self.move_timer = pygame.time.get_ticks()
        self.searching_for_path = False
        self.dest = None

    def move_to(self, new_tile, screen, camera):
        if not new_tile["collision"]:
            self.searching_for_path = True
            self.dest = new_tile
            self.grid = Grid(matrix=self.map.collision_matrix)
            self.start = self.grid.node(self.pos["grid"][0], self.pos["grid"][1])
            self.end = self.grid.node(new_tile["grid"][0], new_tile["grid"][1])
            finder = AStarFinder()
            # how far along the path are we
            self.path_index = 0
            self.path, runs = finder.find_path(self.start, self.end, self.grid)




    def change_tile(self, new_tile):
        # remove the unit from its current position on the map
        self.map.units[self.pos["grid"][0]][self.pos["grid"][1]] = None
        #remove collision from old position
        self.map.collision_matrix[self.pos["grid"][1]][self.pos["grid"][0]] = 1
        self.map.map[self.pos["grid"][0]][self.pos["grid"][1]]["collision"] = False

        # update the map
        self.map.units[new_tile[0]][new_tile[1]] = self
        self.pos = self.map.map[new_tile[0]][new_tile[1]]
        #update collision for new tile
        self.map.collision_matrix[self.pos["grid"][1]][self.pos["grid"][0]] = 0
        self.map.map[self.pos["grid"][0]][self.pos["grid"][1]]["collision"] = True

    def update(self):

        now = pygame.time.get_ticks()
        if now - self.move_timer > 1000 and self.searching_for_path:
            new_pos = self.path[self.path_index]
            #update positoin in the world
            self.change_tile(new_pos)
            self.path_index += 1
            self.move_timer = now
            if self.path_index == len(self.path):
                self.searching_for_path = False

    def attack(self, targeted_unit):

        targeted_unit.current_health -= self.attack_dmg
        # pour tester
        # print("hp de unit :", targeted_unit.current_health, " / ", targeted_unit.max_health)

        # if target has less than 0 hp after attack, she dies
        if targeted_unit.current_health < 0:
            # print pour tester
            # print(" unit DIED")
            targeted_unit.is_alive = False
            # del units_group[units_group.index(targeted_unit)]


class Villager(Unit):

    def __init__(self, pos, player_owner_of_unit, map):

        self.name = "Villager"

        # DISPLAY
        self.sprite = pygame.image.load("resources/assets/Villager.bmp").convert_alpha()

        # DATA
        self.max_health = 25
        self.attack_dmg = 3
        self.attack_speed = 1.5
        self.movement_speed = 1.1

        # unit type : melee
        self.range = 0

        #Training : 50 FOOD, 20s
        self.construction_cost = [0, 10, 25, 0]
        self.training_time = 20
        self.population_produced = 1

        self.description = "Your best friend. Can work, fight, get resources."
        self.construction_tooltip = " Train a Villager"


        super().__init__(pos, player_owner_of_unit, map)

    def build(self, tile):
        ...

    def repair(self, building):
        if building.current_health != building.max_health:
            ...
        else:
            ...

    """
    def gatherRessources(self, ressource):
        if (ressource.type = BERRY_BUSH):
            ...
        elif (ressource.type = TREE):
            ...
        elif (ressource.type = GOLD_MINE):
            ...
        elif (ressource.type = STONE_MINE):
            ...
        elif (ressource.type = SHORE_FISH):
            ...
        elif (ressource.type = ANIMALS):
            ...
    """


class Bowman(Unit):

    def __init__(self, pos, player_owner_of_unit, map):
        super().__init__(pos, player_owner_of_unit, map)

        #DISPLAY
        self.sprite = None

        # DATA
        self.max_health = 35
        self.current_health = 35
        self.attack = 3
        self.attack_speed = 1.4
        self.movement_speed = 1.2
        # unit type : distance
        self.range = 5

        #Training : 20 WOOD, 40 FOOD, 30s
        self.training_cost = [20, 40, 0, 0]
        self.training_time = 30
        self.population_produced = 1

        self.description = "Basic ranged unit."
        self.construction_tooltip = " Train a Bowman"




class Clubman(Unit):

    def __init__(self, pos, player_owner_of_unit, map):
        super().__init__(pos, player_owner_of_unit, map)

        #DISPLAY
        self.sprite = None

        # DATA
        self.max_health = 40
        self.current_health = 40
        self.attack = 3
        self.attack_speed = 1.5
        self.movement_speed = 1.2

        # unit type : melee
        self.range = 0

        #Training : 50 FOOD, 26s
        self.training_cost = [0, 50, 0, 0]
        self.training_time = 26
        self.population_produced = 1

        self.description = "Basic melee unit."
        self.construction_tooltip = " Train a Clubman"


