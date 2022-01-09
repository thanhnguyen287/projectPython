from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.a_star import DiagonalMovement
from time import sleep
from tech import Age_II, Age_III, Age_IV
#from player import *
import os
import pygame
from math import ceil
from game.utils import tile_founding


class Building:
    population_produced = 0
    is_being_built = True
    construction_progress = 0

    def __init__(self, pos, map, player_owner_of_unit, ):
        self.owner = player_owner_of_unit
        self.owner.building_list.append(self)
        # pos is the tile position, for ex : (4,4)
        self.pos = pos
        self.map = map
        # updating map with the new unit, collision, etc...
        self.map.buildings[self.pos[0]][self.pos[1]] = self
        self.map.entities.append(self)
        self.map.map[self.pos[0]][self.pos[1]]["tile"] = "building"
        # 0 means collision = True
        self.map.collision_matrix[self.pos[0]][self.pos[1]] = 0

        # will be used in the timer to increase resources of the player
        self.resource_manager_cooldown = pygame.time.get_ticks()

        self.current_health = 1
        self.is_alive = True

        #self.image_select = pygame.image.load(os.path.join(assets_path, "image_select.png"))
        self.selected = False

        self.resource_manager_cooldown = pygame.time.get_ticks()
        self.now = 0

    def update(self):
        pass


class Farm(Building):
    description = " Provides 50 food every 5 seconds."
    construction_tooltip = " Build a Farm"
    construction_cost = [100, 0, 0, 0]
    construction_time = 4
    armor = 0
    armor_age_bonus = 0

    def __init__(self, pos, map, player_owner_of_unit):
        self.name = " Farm"

        self.construction_cost = [100, 0, 0, 0]

        self.max_health = 10
        self.max_population_bonus = 0

        super().__init__(pos, map, player_owner_of_unit)

    def update(self):
        self.now = pygame.time.get_ticks()
        # BUILDING CONSTRUCTION - we change the display of the building depending on its construction progression
        if self.is_being_built:
            progress_time = ((self.now - self.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / self.construction_time
            if ceil(progress_time_pourcent * self.max_health * 0.01) != 0:
                self.current_health = ceil(progress_time_pourcent * self.max_health * 0.01)

            # if fully built we set is_being_built to 0, else change the progression attribute accordingly
            if self.now - self.resource_manager_cooldown > Farm.construction_time * 1000:
                self.resource_manager_cooldown = self.now
                self.construction_progress = 100
                self.current_health -= 1
                self.is_being_built = False
            elif self.now - self.resource_manager_cooldown > Farm.construction_time * 750:
                self.construction_progress = 75
            elif self.now - self.resource_manager_cooldown > Farm.construction_time * 500:
                self.construction_progress = 50
            elif self.now - self.resource_manager_cooldown > Farm.construction_time * 250:
                self.construction_progress = 25


class TownCenter(Building):
    description = " Used to create villagers."
    construction_tooltip = " Build a Town Center"
    construction_cost = [1000, 0, 0, 100]
    construction_time = 8
    armor = 2
    armor_age_bonus = 1

    def __init__(self, pos, map, player_owner_of_unit):

        self.name = "Town center"
        # additional collision bc 2x1 building

        map.map[pos[0] + 1][pos[1]]["tile"] = "building"
        map.collision_matrix[pos[1]][pos[0] + 1] = 0

        map.map[pos[0]][pos[1] - 1]["tile"] = "building"
        map.collision_matrix[pos[1] - 1][pos[0]] = 0

        map.map[pos[0] + 1][pos[1] - 1]["tile"] = "building"
        map.collision_matrix[pos[0] + 1][pos[1] - 1] = 0

        self.construction_cost = [0, 0, 0, 0]

        self.max_health = 100
        #becomes true when you create villagers
        self.is_working = False
        #class of unit being trained
        self.unit_type_currently_trained = None
        player_owner_of_unit.max_population += 5
        #used when you order the creation of multiples units
        self.queue = 0
        armor = 3
        self.resource_manager_cooldown = 0

        super().__init__(pos, map, player_owner_of_unit)

    # to create villagers, research techs and upgrade to second age
    def update(self):
        self.now = pygame.time.get_ticks()
        # add a button to stop the current action if the town center is working
        if self.is_working and not self.is_being_built:
            # if a villager is being created since 5 secs :
            if self.now - self.resource_manager_cooldown > 5000:
                self.resource_manager_cooldown = self.now
                # we determine the nearest free tile and spawn a villager on it
                self.check_collision_and_spawn_villager_where_possible()
                # decrease the queue
                self.queue -= 1
                # if there are no more villagers to train, we can stop there
                if self.queue <= 0:
                    self.is_working = False

        # BUILDING CONSTRUCTION - we change the display of the building depending on its construction progression
        if self.is_being_built:
            # the current life increases with the construction progress
            progress_time = ((self.now - self.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / self.construction_time
            if ceil(progress_time_pourcent * self.max_health*0.01) != 0:
                self.current_health = ceil(progress_time_pourcent * self.max_health*0.01)

            # if fully built we set is_being_built to 0, else change the progression attribute accordingly
            if self.now - self.resource_manager_cooldown > TownCenter.construction_time * 1000:
                self.resource_manager_cooldown = self.now
                self.construction_progress = 100
                # to fix a little bug
                self.current_health -= 1
                self.is_being_built = False
            elif self.now - self.resource_manager_cooldown > TownCenter.construction_time * 750:
                self.construction_progress = 75
            elif self.now - self.resource_manager_cooldown > TownCenter.construction_time * 500:
                self.construction_progress = 50
            elif self.now - self.resource_manager_cooldown > TownCenter.construction_time * 250:
                self.construction_progress = 25

    # we determine the nearest free tile, collision matrix has a 1 if the tile is free
    # we try the 4 tiles under the town center, then the ones on the sides, then the ones above
    # we also check if we stay in the map boundaries
    def check_collision_and_spawn_villager_where_possible_old(self):
        # UNDER
        #check if the tile is in the map boundaries and if tile is empty
        if 0 <= self.pos[0] < self.map.grid_length_x and 0 < self.pos[1] + 1 < self.map.grid_length_y and self.map.collision_matrix[self.pos[1] + 1][self.pos[0]] == 1:
            # new villager
            self.map.units[self.pos[0]][self.pos[1] + 1] = Villager((self.pos[0], self.pos[1] + 1), self.owner,
                                                                    self.map)

            #we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0]][self.pos[1] + 1])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1] + 1][self.pos[0]] = 0

        elif 0 <= self.pos[0] + 1 < self.map.grid_length_x and 0 < self.pos[1] + 1 < self.map.grid_length_y and self.map.collision_matrix[self.pos[1] + 1][
            self.pos[0] + 1] == 1:
            # new villager
            self.map.units[self.pos[0] + 1][self.pos[1] + 1] = Villager((self.pos[0] + 1, self.pos[1] + 1),
                                                                        self.owner, self.map)

            # we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0] + 1][self.pos[1] + 1])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1] + 1][self.pos[0] + 1] = 0

        elif 0 <= self.pos[0] - 1 < self.map.grid_length_x and 0 < self.pos[1] + 1 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] + 1][self.pos[0] - 1] == 1:
            # new villager
            self.map.units[self.pos[0] - 1][self.pos[1] + 1] = Villager((self.pos[0] - 1, self.pos[1] + 1),
                                                                        self.owner, self.map)

            # we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0] - 1][self.pos[1] + 1])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1] + 1][self.pos[0] - 1] = 0

        elif 0 <= self.pos[0] + 2 < self.map.grid_length_x and 0 < self.pos[1] + 1 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] + 1][self.pos[0] + 2] == 1:
            # new villager
            self.map.units[self.pos[0] + 2][self.pos[1] + 1] = Villager((self.pos[0] + 2, self.pos[1] + 1),
                                                                        self.owner, self.map)

            # we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0] + 2][self.pos[1] + 1])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1] + 1][self.pos[0] + 2] = 0

        # SIDES
        elif 0 <= self.pos[0] - 1 < self.map.grid_length_x and 0 < self.pos[1] < self.map.grid_length_y and self.map.collision_matrix[self.pos[1]][
            self.pos[0] - 1] == 1:
            # new villager
            self.map.units[self.pos[0] - 1][self.pos[1]] = Villager((self.pos[0] - 1, self.pos[1]),
                                                                    self.owner, self.map)

            # we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0] - 1][self.pos[1]])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1]][self.pos[0] - 1] = 0

        elif 0 <= self.pos[0] + 2 < self.map.grid_length_x and 0 < self.pos[1] < self.map.grid_length_y and self.map.collision_matrix[self.pos[1]][
            self.pos[0] + 2] == 1:
            # new villager
            self.map.units[self.pos[0] + 2][self.pos[1]] = Villager((self.pos[0] + 2, self.pos[1]),
                                                                    self.owner, self.map)

            # we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0] + 2][self.pos[1]])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1]][self.pos[0] + 2] = 0

        elif 0 <= self.pos[0] - 1 < self.map.grid_length_x and 0 < self.pos[1] - 1 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] - 1][self.pos[0] - 1] == 1:
            # new villager
            self.map.units[self.pos[0] - 1][self.pos[1] - 1] = Villager((self.pos[0] - 1, self.pos[1] - 1),
                                                                        self.owner, self.map)

            # we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0] - 1][self.pos[1] - 1])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 1][self.pos[0] - 1] = 0

        elif 0 <= self.pos[0] + 2 < self.map.grid_length_x and 0 < self.pos[1] - 1 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] - 1][self.pos[0] + 2] == 1:
            # new villager
            self.map.units[self.pos[0] + 2][self.pos[1] - 1] = Villager((self.pos[0] + 2, self.pos[1] - 1),
                                                                        self.owner, self.map)

            # we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0] + 2][self.pos[1] - 1])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 1][self.pos[0] + 2] = 0


        # ABOVE
        elif 0 <= self.pos[0] - 1 < self.map.grid_length_x and 0 < self.pos[1] - 2 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] - 2][self.pos[0] - 1] == 1:
            # new villager
            self.map.units[self.pos[0] - 1][self.pos[1] - 2] = Villager((self.pos[0] - 1, self.pos[1] - 2),
                                                                        self.owner, self.map)

            # we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0] - 1][self.pos[1] - 2])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 2][self.pos[0] - 1] = 0

        elif 0 <= self.pos[0] < self.map.grid_length_x and 0 < self.pos[1] - 2 < self.map.grid_length_y and self.map.collision_matrix[self.pos[1] - 2][
            self.pos[0]] == 1:
            # new villager
            self.map.units[self.pos[0]][self.pos[1] - 2] = Villager((self.pos[0], self.pos[1] - 2),
                                                                    self.owner, self.map)

            # we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0]][self.pos[1] - 2])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 2][self.pos[0]] = 0

        elif 0 <= self.pos[0] + 1 < self.map.grid_length_x and 0 < self.pos[1] - 2 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] - 2][self.pos[0] + 1] == 1:
            # new villager
            self.map.units[self.pos[0] + 1][self.pos[1] - 2] = Villager((self.pos[0] + 1, self.pos[1] - 2),
                                                                        self.owner, self.map)

            # we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0] + 1][self.pos[1] - 2])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 2][self.pos[0] + 1] = 0

        elif 0 <= self.pos[0] + 2 < self.map.grid_length_x and 0 < self.pos[1] - 2 < self.map.grid_length_y and \
                self.map.collision_matrix[self.pos[1] - 2][self.pos[0] + 2] == 1:
            # new villager
            self.map.units[self.pos[0] + 2][self.pos[1] - 2] = Villager((self.pos[0] + 2, self.pos[1] - 2),
                                                                        self.owner, self.map)

            # we add the unit we created to the list of units of the player
            self.owner.unit_list.append(self.map.units[self.pos[0] + 2][self.pos[1] - 2])
            self.owner.unit_occupied.append(0)

            # update collision for new villager
            self.map.collision_matrix[self.pos[1] - 2][self.pos[0] + 2] = 0

    #trying to simplify that shit
    def check_collision_and_spawn_villager_where_possible(self):

        available_tile_for_spawn = tile_founding(1, 1, 2, self.map.map, self.owner, "")
        print(available_tile_for_spawn[0][0])
        self.map.units[available_tile_for_spawn[0][0]][available_tile_for_spawn[0][1]] = Villager((available_tile_for_spawn[0][0], available_tile_for_spawn[0][1]), self.owner,
                                                                    self.map)
        self.map.map[available_tile_for_spawn[0][0]][available_tile_for_spawn[0][1]]["tile"] = "unit"
        self.map.map[available_tile_for_spawn[0][0]][available_tile_for_spawn[0][1]]["collision"] = True
        #we add the unit we created to the list of units of the player
        self.owner.unit_list.append(self.map.units[available_tile_for_spawn[0][0]][available_tile_for_spawn[0][1]])
        self.owner.unit_occupied.append(0)

        # update collision for new villager
        self.map.collision_matrix[available_tile_for_spawn[0][1]][available_tile_for_spawn[0][0]] = 0


    def research_tech(self, tech):
        if tech == "Advance to Feudal Age":
            tech = Age_II
            self.owner.age = 2
        elif tech == "Advance to Castle Age":
            tech = Age_III
            self.owner.age = 3
        elif tech == "Advance to Imperial Age":
            tech = Age_IV
            self.owner.age = 4

        for resource_type in range(0, 3):
            self.owner.resources[resource_type] -= tech.construction_costs[resource_type]


class House(Building):
    description = " Each House increases the maximum population by 5."
    construction_tooltip = " Build a House"
    construction_cost = [300, 0, 0, 50]
    construction_time = 4
    armor = -2
    armor_age_bonus = 2

    def __init__(self, pos, map, player_owner_of_unit):
        self.name = "House"

        self.construction_cost = [600, 0, 0, 0]
        self.max_health = 50
        player_owner_of_unit.max_population += 5

        super().__init__(pos, map, player_owner_of_unit)

    def update(self):
        self.now = pygame.time.get_ticks()
        # BUILDING CONSTRUCTION - we change the display of the building depending on its construction progression
        if self.is_being_built:
            progress_time = ((self.now - self.resource_manager_cooldown) / 1000)
            progress_time_pourcent = progress_time * 100 / self.construction_time
            if ceil(progress_time_pourcent * self.max_health*0.01) != 0:
                self.current_health = ceil(progress_time_pourcent * self.max_health*0.01)
            # if fully built we set is_being_built to 0, else change the progression attribute accordingly
            if progress_time_pourcent > 100:
                self.resource_manager_cooldown = self.now
                self.construction_progress = 100
                self.current_health -= 1
                self.is_being_built = False
            elif progress_time_pourcent > 75:
                self.construction_progress = 75
            elif progress_time_pourcent > 50:
                self.construction_progress = 50
            elif progress_time_pourcent > 25:
                self.construction_progress = 25


class Unit:
    armor = 0

    def __init__(self, pos, player_owner_of_unit, map, angle=225):
        self.owner = player_owner_of_unit
        self.map = map
        # pos is the tile position, for ex : (4,4)
        self.pos = pos
        #updating map with the new unit, collision, etc...
        self.map.units[self.pos[0]][self.pos[1]] = self
        self.map.entities.append(self)
        self.map.map[self.pos[0]][self.pos[1]]["tile"] = "unit"
        # 0 means collision = True
        self.map.collision_matrix[self.pos[0]][self.pos[1]] = 0

        # we add the unit we created to the list of units of the player
        self.owner.unit_list.append(self)

        self.current_health = self.max_health
        self.is_alive = True
        self.angle = angle
        self.sprite_index = 0
        #pathfinding
        self.move_timer = pygame.time.get_ticks()
        self.searching_for_path = False
        self.dest = None
        self.attack_cooldown = 0

    def move_to(self, new_tile):
        if not self.map.is_there_collision(new_tile["grid"]):
            self.searching_for_path = True
            self.dest = new_tile
            self.grid = Grid(matrix=self.map.collision_matrix)
            self.start = self.grid.node(self.pos[0], self.pos[1])
            self.end = self.grid.node(new_tile["grid"][0], new_tile["grid"][1])
            #finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
            finder = AStarFinder(diagonal_movement=DiagonalMovement.always)

            # how far along the path are we
            self.path_index = 0
            self.path, runs = finder.find_path(self.start, self.end, self.grid)

    # returns True if entity is adjacent to unit/building calling it, else False
    def is_adjacent_to(self, entity):
        if (abs(self.pos[0] - entity.pos[0]) == 1 and abs(self.pos[1] - entity.pos[1]) == 0) or \
                (abs(self.pos[0] - entity.pos[0]) == 0 and abs(self.pos[1] - entity.pos[1]) == 1):
            return True
        else:
            return False

    def change_tile(self, new_tile):
        # remove the unit from its current position on the map
        if self.pos != new_tile:
            self.angle = self.map.get_angle_between(self.pos, new_tile, self) if self.map.get_angle_between(self.pos,
                                                                                                     new_tile, self) != -1 else ...
        self.map.units[self.pos[0]][self.pos[1]] = None
        self.map.map[self.pos[0]][self.pos[1]]["tile"] == ""
        #remove collision from old position
        self.map.collision_matrix[self.pos[1]][self.pos[0]] = 1
        # update the map
        self.map.units[new_tile[0]][new_tile[1]] = self
        self.pos = tuple(self.map.map[new_tile[0]][new_tile[1]]["grid"])
        #update collision for new tile
        self.map.collision_matrix[self.pos[1]][self.pos[0]] = 0
        self.map.map[self.pos[0]][self.pos[1]]["tile"] == "unit"

    def update(self):
        self.now = pygame.time.get_ticks()
        if self.searching_for_path and self.now - self.move_timer > 1000:
            while self.path[self.path_index] == self.pos:
                self.path_index += 1
            new_pos = self.path[self.path_index]
            #update position in the world
            self.change_tile(new_pos)
            self.path_index += 1
            self.move_timer = self.map.timer
            if self.path_index == len(self.path):
                self.searching_for_path = False


class Villager(Unit):

    # Training : 50 FOOD, 20s
    description = " Your best friend. Can work, fight and gather resources."
    construction_tooltip = " Train a Villager"
    name = "Villager"
    attack_speed = 500

    construction_cost = [0, 10, 25, 0]
    construction_time = 5
    population_produced = 1

    def __init__(self, pos, player_owner_of_unit, map, angle=225):

        self.name = "Villager"
        # DISPLAY
        # DATA
        self.max_health = 25
        self.attack_dmg = 3
        self.attack_speed = 1500
        self.movement_speed = 1.1
        # unit type : melee
        self.is_on_tile = True
        self.range = 0
        # used to gather ressources
        # between 0 and 360, 0 being top, 90 right, etc.... Only 0, 45, 90, 135, etc (up to 360 ofc) supported for now
        self.is_moving_to_build = False
        self.is_moving_to_fight = False
        self.display_pos = pos
        self.building_to_create = None
        self.is_moving_to_gather = False
        self.is_building = False
        self.target = None
        self.is_gathering = False
        self.is_fighting = False
        self.gathered_resources_stack = 0
        #Training : 50 FOOD, 2s
        self.construction_cost = [0, 10, 25, 0]
        self.construction_time = 5
        self.population_produced = 1
        self.now = 0

        super().__init__(pos, player_owner_of_unit, map, angle)
        self.owner.unit_occupied.append(0)

    def repair(self, building):
        if building.current_health != building.max_health:
            ...
        else:
            ...

    def attack(self):
        #target has enough health to survive
        if self.is_fighting and (self.now - self.attack_cooldown > self.attack_speed):
            self.angle = self.map.get_angle_between(self.pos, new_tile, self) if self.map.get_angle_between(self.pos,
                                                                                                      new_tile, self) != -1 else ...

            if self.target.current_health > self.attack_dmg:
                self.target.current_health -= self.attack_dmg
                self.attack_cooldown = self.now

            #unit doesnt survive attack
            else:
                self.map.remove_entity(self.target)
                self.target = None
                self.is_fighting = False

    def go_to_build(self, pos, name):
        if self.map.get_empty_adjacent_tiles(pos):
            villager_dest = self.map.get_empty_adjacent_tiles(pos)[0]
            self.move_to(self.map.map[villager_dest[0]][villager_dest[1]])
            self.is_moving_to_build = True

            self.building_to_create = {"name": name, "pos": pos}

    def build(self):
        self.is_moving_to_build = False
        if self.building_to_create is not None:
            self.angle = self.map.get_angle_between(self.pos, self.building_to_create["pos"], self) if self.map.get_angle_between(self.pos, self.building_to_create["pos"], self) != -1 else ...

        new_building = None
        if self.building_to_create["name"] == "Farm":
            new_building = Farm((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                self.owner)

        elif self.building_to_create["name"] == "TownCenter":
            new_building = TownCenter((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                      self.owner)
            # additional collision bc town center is 2x2 tile, not 1x1
            self.map.collision_matrix[self.building_to_create["pos"][1]][self.building_to_create["pos"][0] + 1] = 0
            self.map.collision_matrix[self.building_to_create["pos"][1] - 1][self.building_to_create["pos"][0] + 1] = 0
            self.map.collision_matrix[self.building_to_create["pos"][1] - 1][self.building_to_create["pos"][0]] = 0

        elif self.building_to_create["name"] == "House":
            new_building = House((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                 self.owner)

        # to add it to the entities list on our map
        self.map.entities.append(new_building)
        self.map.buildings[self.building_to_create["pos"][0]][
            self.building_to_create["pos"][1]] = new_building
        # we pay the construction cost
        self.owner.pay_entity_cost_bis(self.building_to_create["name"])
        # we actualize collision
        self.map.collision_matrix[self.building_to_create["pos"][1]][
            self.building_to_create["pos"][0]] = 0

        pos_x = self.building_to_create["pos"][0]
        pos_y = self.building_to_create["pos"][1]
        self.map.map[pos_x][pos_y]["tile"] = "building"
        #self.building_to_create = None
        self.is_building = False

    def go_to_ressource(self, pos):
        # if the ressource is near us, we directly gather it
        if (abs(pos[0] - self.pos[0]) <= 1 and abs(pos[1] - self.pos[1]) == 0) or \
                (abs(pos[0] - self.pos[0]) == 0 and abs(pos[1] - self.pos[1]) <= 1):
            self.target = (pos[0], pos[1])
            self.is_gathering = True

        # else we go to an adjacent tile
        else:
            if 0 <= pos[0] - 1 <= self.map.grid_length_x and self.map.map[pos[0] - 1][pos[1]]["tile"] == "":
                self.move_to(self.map.map[pos[0] - 1][pos[1]])
                self.target = (pos[0], pos[1])
                self.is_moving_to_gather = True

            elif 0 <= pos[0] + 1 <= self.map.grid_length_x and self.map.map[pos[0] + 1][pos[1]]["tile"] == "":
                self.move_to(self.map.map[pos[0] + 1][pos[1]])
                self.target = (pos[0], pos[1])
                self.is_moving_to_gather = True

            elif 0 <= pos[1] - 1 <= self.map.grid_length_y and self.map.map[pos[0]][pos[1] - 1]["tile"] == "":
                self.move_to(self.map.map[pos[0]][pos[1] - 1])
                self.target = (pos[0], pos[1])
                self.is_moving_to_gather = True

            elif 0 <= pos[0] + 1 <= self.map.grid_length_y and self.map.map[pos[0]][pos[1] + 1]["tile"] == "":
                self.move_to(self.map.map[pos[0]][pos[1] + 1])
                self.target = (pos[0], pos[1])
                self.is_moving_to_gather = True

            else:
                self.target = None

    def gather_ressources(self):
        this_target = self.map.map[self.target[0]][self.target[1]]
        self.angle = self.map.get_angle_between(self.pos, self.target, self) if self.map.get_angle_between(self.pos,
                                                                                             self.target, self) != -1 else ...

        if self.is_gathering and (self.now - self.attack_cooldown > self.attack_speed):

            if this_target["health"] > self.attack_dmg:
                this_target["health"] -= self.attack_dmg
                self.attack_cooldown = self.now
                self.gathered_resources_stack += 1
            # no resource is remaining, we destroy it and give resource to the player:
            else:
                if this_target["tile"] == "tree":
                    self.owner.update_resource("WOOD", 10)
                elif this_target["tile"] == "rock":
                    self.owner.update_resource("STONE", 10)
                elif this_target["tile"] == "gold":
                    self.owner.update_resource("GOLD", 10)
                elif this_target["tile"] == "berrybush":
                    self.owner.update_resource("FOOD", 10)

                this_target["tile"] = ""
                this_target["collision"] = False
                self.map.collision_matrix[this_target["grid"][1]][this_target["grid"][0]] = 1
                self.target = None
                self.is_gathering = False
                self.map.hud.villager_attack_animations[str(self.angle)]["animation"].to_be_played = False

    def update(self):
        self.now = pygame.time.get_ticks()
        if self.now - self.move_timer > 400:
            if self.searching_for_path:

                # movement
                # for debug, because the first tile of our path is the pos of unit, not the first tile where we must go
                if self.path_index < len(self.path) and self.path[self.path_index] == self.pos:
                    self.path_index += 1
                print("debug path index, path)", self.path_index, len(self.path))
                new_pos = self.path[self.path_index] if len(self.path) != self.path_index else ...

                #update position in the world
                self.change_tile(new_pos)

                self.path_index += 1
                if self.path_index == len(self.path):
                    self.searching_for_path = False
                    self.is_on_tile = True
                    if self.is_moving_to_build:
                        self.is_building = True
                        self.build()
                        self.is_moving_to_build = False
                    elif self.is_moving_to_fight:
                        self.is_fighting = True
                        self.is_moving_to_fight = False
                    elif self.is_moving_to_gather:
                        self.is_gathering = True
                        self.is_moving_to_gather = False
            else:
                ...



            #always at the end to reset the timer
            self.move_timer = self.now

        if self.is_gathering:
            self.gather_ressources()


            # fighting
        if self.is_fighting:
            self.attack()


class Bowman(Unit):

    def __init__(self, pos, player_owner_of_unit, map):
        super().__init__(pos, player_owner_of_unit, map)

        #DISPLAY
        self.sprite = None
        self.name = "Bowman"

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
        self.name = "Clubman"

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

