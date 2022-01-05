from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.a_star import DiagonalMovement

from player import *
from math import ceil


class Building:
    population_produced = 0
    is_being_built = True
    construction_progress = 0

    def __init__(self, pos, map, player_owner_of_unit, ):
        self.owner = player_owner_of_unit
        self.rect = self.sprite.get_rect(topleft=pos)
        # pos is the tile position, for ex : (4,4)
        self.pos = pos
        self.map = map

        # will be used in the timer to increase resources of the player
        self.resource_manager_cooldown = pygame.time.get_ticks()

        self.current_health = 1
        self.is_alive = True

        self.image_select = pygame.image.load(os.path.join(assets_path, "image_select.png"))
        self.selected = False

        self.resource_manager_cooldown = pygame.time.get_ticks()
        #self.owner.pay_entity_cost(self)
        self.now = 0

    def update(self):
        pass


class Farm(Building):
    description = " Provides 50 food every 5 seconds."
    construction_tooltip = " Build a Farm"
    construction_cost = [100, 0, 0, 0]
    construction_time = 4
    armor = 0

    sprite = pygame.image.load("Resources/assets/Models/Buildings/Farm/farm.png")

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
    armor = 3
    sprite = pygame.image.load("Resources/assets/Models/Buildings/Town_Center/town_center_x1.png")


    def __init__(self, pos, map, player_owner_of_unit):

        self.name = "Town center"

        self.construction_cost = [0, 0, 0, 0]

        self.max_health = 100
        #becomes true when you create villagers
        self.is_working = False
        #class of unit being trained
        self.unit_type_currently_trained = None
        player_owner_of_unit.max_population += 5
        #used when you order the creation of multiples units
        self.queue = 0
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
    def check_collision_and_spawn_villager_where_possible(self):
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


class House(Building):
    description = " Each House increases the maximum population by 5."
    construction_tooltip = " Build a House"
    construction_cost = [600, 0, 0, 0]
    construction_time = 4
    armor = -2
    sprite = pygame.image.load("Resources/assets/Models/Buildings/House/house_1.png")

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

    def __init__(self, pos, player_owner_of_unit, map):
        self.owner = player_owner_of_unit
        self.map = map
        self.map.entities.append(self)
        # pos is the tile position, for ex : (4,4)
        self.pos = pos
        self.current_health = self.max_health
        self.is_alive = True
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
            finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
            # how far along the path are we
            self.path_index = 0
            self.path, runs = finder.find_path(self.start, self.end, self.grid)

    # returns True if entity is adjacent to unit/building calling it, else False
    def is_adjacent_to(self, entity):
        if (abs(self.pos[0] - entity.pos[0]) == 1 and abs(self.pos[1] - entity.pos[1]) == 0 ) or (abs(self.pos[0] - entity.pos[0]) == 0 and abs(self.pos[1] - entity.pos[1]) == 1 ):
            return True
        else:
            return False

    def change_tile(self, new_tile):
        # remove the unit from its current position on the map

        self.map.units[self.pos[0]][self.pos[1]] = None
        #remove collision from old position
        self.map.collision_matrix[self.pos[1]][self.pos[0]] = 1
        # update the map
        self.map.units[new_tile[0]][new_tile[1]] = self
        self.pos = self.map.map[new_tile[0]][new_tile[1]]["grid"]
        #update collision for new tile
        self.map.collision_matrix[self.pos[1]][self.pos[0]] = 0

    def update(self):
        self.now = pygame.time.get_ticks()
        if self.searching_for_path and self.now - self.move_timer > 1000:
            new_pos = self.path[self.path_index]
            #update position in the world

            self.change_tile(new_pos)
            self.path_index += 1
            self.move_timer = self.now
            if self.path_index == len(self.path):
                self.searching_for_path = False

class Villager(Unit):

    # Training : 50 FOOD, 20s
    description = " Your best friend. Can work, fight and gather resources."
    construction_tooltip = " Train a Villager"
    name = "Villager"
    construction_cost = [0, 10, 25, 0]
    construction_time = 5
    population_produced = 1

    def __init__(self, pos, player_owner_of_unit, map):

        self.name = "Villager"
        # DISPLAY
        self.sprite = pygame.image.load("resources/assets/Villager.bmp").convert_alpha()
        # DATA
        self.max_health = 25
        self.attack_dmg = 3
        self.attack_speed = 1500
        self.movement_speed = 1.1
        # unit type : melee
        self.range = 0
        # used to gather ressources
        self.is_moving_to_build = False
        self.is_moving_to_fight = False
        self.building_to_create = None
        self.is_moving_to_gather = False
        self.target = None
        self.is_gathering = False
        self.is_fighting = False
        self.gathered_resources_stack = 0
        #Training : 50 FOOD, 2s
        self.construction_cost = [0, 10, 25, 0]
        self.construction_time = 5
        self.population_produced = 1
        self.now = 0

        super().__init__(pos, player_owner_of_unit, map)

    def repair(self, building):
        if building.current_health != building.max_health:
            ...
        else:
            ...

    def attack(self):
        #target has enough health to survive
        if self.is_fighting and (self.now - self.attack_cooldown > self.attack_speed):

            if self.target.current_health > self.attack_dmg:
                self.target.current_health -= self.attack_dmg
                self.attack_cooldown = self.now

            #unit doesnt survive attack
            else:
                self.map.remove_entity(self.target)
                self.target = None
                self.is_fighting = False

    def build(self):
        self.is_moving_to_build = False
        new_building = None
        if self.building_to_create["type"] == Farm:
            new_building = Farm((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                playerOne)

        elif self.building_to_create["type"] == TownCenter:
            new_building = TownCenter((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                      playerOne)
            # additional collision bc town center is 2x2 tile, not 1x1
            self.map.collision_matrix[self.building_to_create["pos"][1]][self.building_to_create["pos"][0] + 1] = 0
            self.map.collision_matrix[self.building_to_create["pos"][1] - 1][self.building_to_create["pos"][0] + 1] = 0
            self.map.collision_matrix[self.building_to_create["pos"][1] - 1][self.building_to_create["pos"][0]] = 0

        elif self.building_to_create["type"] == House:
            new_building = House((self.building_to_create["pos"][0], self.building_to_create["pos"][1]), self.map,
                                 playerOne)

        # to add it to the entities list on our map
        self.map.entities.append(new_building)
        self.map.buildings[self.building_to_create["pos"][0]][
            self.building_to_create["pos"][1]] = new_building
        # we pay the construction cost
        playerOne.pay_entity_cost_bis(self.building_to_create["type"])
        # we actualize collision
        self.map.collision_matrix[self.building_to_create["pos"][1]][
            self.building_to_create["pos"][0]] = 0
        self.building_to_create = None

    def gather_ressources(self):

        if self.is_gathering and (self.now - self.attack_cooldown > self.attack_speed):

            if self.target["health"] > self.attack_dmg:
                self.target["health"] -= self.attack_dmg
                self.attack_cooldown = self.now
                self.gathered_resources_stack += 1
            # no resource is remaining, we destroy it and give resource to the player:
            else:
                if self.target["tile"] == "tree":
                    self.owner.update_resource("WOOD", 10)
                elif self.target["tile"] == "rock":
                    self.owner.update_resource("STONE", 10)
                elif self.target["tile"] == "gold":
                    self.owner.update_resource("GOLD", 10)
                elif self.target["tile"] == "berrybush":
                    self.owner.update_resource("FOOD", 10)

                self.target["tile"] = ""
                self.target["collision"] = False
                self.map.collision_matrix[self.target["grid"][1]][self.target["grid"][0]] = 1
                self.target = None
                self.is_gathering = False

        #if (tar["tile"] == "tree" or tar["tile"] == "rock" or tar["tile"] == "gold" or tar["tile"] == "berrybush") and tar["health"] > 0:

    def update(self):
        self.now = pygame.time.get_ticks()

        if self.now - self.move_timer > 500:
            # movement
            if self.searching_for_path:
                new_pos = self.path[self.path_index]
                #update position in the world
                self.change_tile(new_pos)
                self.path_index += 1
                if self.path_index == len(self.path):
                    self.searching_for_path = False
                    if self.is_moving_to_build:
                        self.build()
                    elif self.is_moving_to_fight:
                        self.is_fighting = True
                        self.is_moving_to_fight = False
                    elif self.is_moving_to_gather:
                        self.is_gathering = True
                        self.is_moving_to_gather = False

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

